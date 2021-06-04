
"""
Embed an Anatomist 3D view in a jupyter notebook widget

To work this notebook widget needs:

* to install ipycanvas, ipyevents, ipywidgets, numpy, anatomist, jupyter notebook
* to register jupyter notebook extensions (may require sudo permissions if
  jupyter is installed system-wide)::

    jupyter nbextension enable --py widgetsnbextension
    jupyter nbextension enable --py ipyevents
    jupyter nbextension enable --py ipycanvas

There are two ways to use it, in a notebook cell. The first is an "integrated"
variant of the Anatomist application which redirects all its views to notebook
canvases, the second is a "by window" method.

Integrated Anatomist::

    import anatomist.notebook as ana

    a = ana.Anatomist()
    w = a.createWindow('3D')
    mesh = a.loadObject('/home/dr144257/data/ra_head.mesh')
    w.addObjects(mesh)

By window::

    import anatomist.headless as ana
    # need to be instantiated before Qt implementations are loaded
    a = ana.HeadlessAnatomist()

    from anatomist.notebook.api import AnatomistInteractiveWidget

    w = a.createWindow('3D')
    mesh = a.loadObject('/home/riviere/data/ra_head.mesh')
    w.addObjects(mesh)

    canvas = AnatomistInteractiveWidget(w)
    display(canvas)

Note that the integrated anatomist.notebook implementation is a headless implementation, and wraps Anatomist windows widget as a single canvas. It is able to render Qt interfaces in a web browser, but cannot open pop-ups, menus, tooltips, or parameters dialogs. Qt widgets renderings are not synchronized because we lack a callback slot when this is done.

"""

from ipycanvas import Canvas
import anatomist.headless as ana
from soma.qt_gui import qt_backend
#import PIL

import time
import logging
import weakref
#from io import BytesIO
#import PIL.Image

from ipycanvas import Canvas
from ipyevents import Event
import numpy as np
from ipywidgets import Image
from functools import partial
import anatomist.direct.api as anatomist
from soma.qt_gui.qt_backend import Qt

from . import Anatomist


INTERACTION_THROTTLE = 100

log = logging.getLogger(__name__)
log.setLevel("CRITICAL")
#log.setLevel("DEBUG")
log.addHandler(logging.StreamHandler())
debug = True

if debug:
    from ipywidgets import HTML
    h = HTML('Event info')


class AnatomistInteractiveWidget(Canvas):
    """Taken and modified from:
    https://github.com/Kitware/ipyvtklink/blob/master/ipyvtklink/viewer.py

    Remote controller for Anatomist render windows.
    In Anatomist 5.1, Anatomist 3D views are sync'ed to the canvas
    automatically at each 3D rendering (via a Qt signal). In earlier Anatomist
    (5.0) this sync is not automatic and is only forced when input events are
    caught, which means that renderings done on Anatomist side for other
    reasons (such as animations) will not be rendered.

    Other Qt widgets (browsers...) are not sync'ed either because we have no
    obvious means to capture paint events from arbitrary Qt widgets.

    Parameters
    ----------
    allow_wheel : bool, optional
        Capture wheel events and allow zooming using the mouse wheel.
    quality : float, optional
        Full rendering image quality.  100 for best quality, 0 for min
        quality.  Default 85.
    quick_quality : float, optional
        Quick rendering image quality during mouse dragging.  100 for
        best quality, 0 for min quality.  Default 50.  Keep this
        number low to allow rapid rendering on limited bandwidth.
    on_close : callable
        A callable function with no arguments to be triggered when the widget
        is destroyed. This is useful to have a callback to close/clean up the
        render window.
    """

    def __init__(self, awindow, log_events=False,
                 transparent_background=False, allow_wheel=True, quality=85,
                 quick_quality=50, on_close=None, only_3d=False, **kwargs):

        super().__init__(**kwargs)
        if quality < 0 or quality > 100:
            raise ValueError('`quality` parameter must be between 0 and 100')
        self._quality = quality
        self._render_window = weakref.ref(awindow)
        self.transparent_background = transparent_background

        self._full_quality = quality
        self._quick_quality = quick_quality

        # Frame rate (1/renderDelay)
        self.last_render_time = 0
        self.quick_render_delay_sec = 0.01
        self.quick_render_delay_sec_range = [0.02, 2.0]
        self.adaptive_render_delay = True
        self.last_mouse_move_event = None
        self._only_3d = only_3d

        self.qtimer = Qt.QTimer()

        # refresh if mouse is just moving (not dragging)
        self.track_mouse_move = False
        #self.track_mouse_move = True
        #if self.is_window3d():
            #self.track_mouse_move = True

        self.message_timestamp_offset = None

        # Set Canvas size from window size
        self.width, self.height \
            = self.render_window.width(), self.render_window.height()

        #self.layout.width = '%dpx' % awindow.getInternalRep().width()
        #self.layout.height = '%dpx' % awindow.getInternalRep().height()
        self.layout.width = 'auto'
        self.layout.height = 'auto'

        self.render_connected = False
        if hasattr(awindow.getInternalRep().view(), 'viewRendered'):
            awindow.getInternalRep().view().viewRendered.connect(
                self.render_callback)
            self.render_connected = True

        # record first render time
        tstart = time.time()
        self.update_canvas()
        self._first_render_time = time.time() - tstart
        log.debug('First image in %.5f seconds', self._first_render_time)

        # this is the minimum time to render anyway
        self.set_quick_render_delay(self._first_render_time)

        self.dragging = False

        self.interaction_events = Event()
        # Set the throttle or debounce time in millseconds (must be an non-negative integer)
        # See https://github.com/mwcraig/ipyevents/pull/55
        self.interaction_events.throttle_or_debounce = "throttle"
        self.interaction_events.wait = INTERACTION_THROTTLE
        self.interaction_events.source = self

        allowed_events = [
            "dragstart",
            "mouseenter",
            "mouseleave",
            "mousedown",
            "mouseup",
            "mousemove",
            "keyup",
            "keydown",
            "dblclick",
            "contextmenu",  # prevent context menu from appearing on right-click
        ]

        # May be disabled out so that user can scroll through the
        # notebook using mousewheel
        if allow_wheel:
            allowed_events.append("wheel")

        self.interaction_events.watched_events = allowed_events

        self.interaction_events.msg_throttle = 1  # does not seem to have effect
        self.interaction_events.prevent_default_action = True
        self.interaction_events.on_dom_event(self.handle_interaction_event)

        # Errors are not displayed when a widget is displayed,
        # this variable can be used to retrieve error messages
        self.error = None

        # Enable logging of UI events
        self.log_events = log_events
        self.logged_events = []
        self.elapsed_times = []
        self.age_of_processed_messages = []

        if hasattr(on_close, '__call__'):
            self._on_close = on_close
        else:
            self._on_close = lambda: None

    @property
    def render_window(self):
        """reference the weak reference"""
        ren_win = self._render_window()
        if ren_win is None:
            raise RuntimeError('render window has closed')
        return ren_win

    @property
    def ana_view(self):
        if self.is_window3d():
            return self.render_window.view()
        w = self.render_window
        if hasattr(w, 'getInternalRep'):
            return w.getInternalRep()

    def set_quick_render_delay(self, delay_sec):
        if delay_sec < self.quick_render_delay_sec_range[0]:
            delay_sec = self.quick_render_delay_sec_range[0]
        elif delay_sec > self.quick_render_delay_sec_range[1]:
            delay_sec = self.quick_render_delay_sec_range[1]
        self.quick_render_delay_sec = delay_sec

    def update_canvas(self, force_render=True, quality=75):
        """Updates the canvas with the current render"""

        raw_img = self.get_image(force_render=force_render)
        # save using Qt to avoid a copy
        buffer = Qt.QByteArray()
        fbuf = Qt.QBuffer(buffer)
        fbuf.open(fbuf.WriteOnly)
        raw_img.save(fbuf, 'JPEG', quality)
        image = Image(
            value=bytes(fbuf.buffer()), width=raw_img.width(),
            height=raw_img.height())
        if self.width != raw_img.width():
            self.width = raw_img.width()
            self.layout.width = 'auto'
        if self.height != raw_img.width():
            self.height = raw_img.height()
            self.layout.height = 'auto'

        # this one was using a np array and PIL

        #f = BytesIO()
        #PIL.Image.fromarray(raw_img).save(f, 'JPEG', quality=quality)
        #image = Image(
            #value=f.getvalue(), width=raw_img.shape[1],
            #height=raw_img.shape[0])
        #if self.width != raw_img.shape[1]:
            #self.width = raw_img.shape[1]
            #self.layout.width = 'auto'
        #if self.height != raw_img.shape[0]:
            #self.height = raw_img.shape[0]
            #self.layout.height = 'auto'
        self.draw_image(image)

    def get_image(self, force_render=True):
        if force_render and self.is_window3d():
            self.render_window.view().blockSignals(True)
            self.render_window.camera(force_redraw=1)
            self.render_window.view().blockSignals(False)
        return self._fast_image

    @property
    def _fast_image(self):
        if self.is_window3d():
            self.render_window.view().blockSignals(True)
            qdata3 = self.render_window.snapshotImage()
            self.render_window.view().blockSignals(False)
            if self._only_3d:
                qdata = qdata3
            else:
                qdata = self.render_window.grab()
                if qdata.isNull():
                    qdata = qdata3
                else:
                    rpos = self.render_window.view().mapTo(
                        self.render_window.getInternalRep(), Qt.QPoint(0, 0))
                    painter = Qt.QPainter(qdata)
                    painter.drawImage(rpos.x(), rpos.y(), qdata3)
                    del painter
        else:
            qdata = self.render_window.grab()

        return qdata  # return a QImage

        #data = qt_backend.qimage_to_np(qdata)

        #if self.transparent_background:
            #return data
        #else:  # ignore alpha channel
            #return data[:, :, :-1]

    def render_callback(self):
        if self._render_window() is None:
            # the anatromist window has been closed
            self.close()
            return
        self.update_canvas(force_render=False, quality=self._quick_quality)
        # trigger a better quality image
        self.qtimer.singleShot(
            float(INTERACTION_THROTTLE) / 1000,
            partial(self.update_canvas, force_render=False,
                    quality=self._full_quality))

    #@throttle(0.1)
    def full_render(self):
        try:
            import time
            tstart = time.time()
            self.update_canvas(True, self._full_quality)
            self.last_render_time = time.time()
            log.debug('full render in %.5f seconds', time.time() - tstart)
        except Exception as e:
            self.error = str(e)

    #@throttle(0.01)
    def quick_render(self):
        if self.render_connected:
            return  # leave this job to the callback
        try:
            self.update_canvas(quality=self._quick_quality)
            if self.log_events:
                self.elapsed_times.append(time.time() - self.last_render_time)
            self.last_render_time = time.time()
        except Exception as e:
            self.error = str(e)

    def handle_interaction_event(self, event):

        def get_key_modifiers(event):
            qevent_mod = Qt.Qt.NoModifier
            if event['ctrlKey']:
                qevent_mod |= Qt.Qt.ControlModifier
            if event['shiftKey']:
                qevent_mod |= Qt.Qt.ShiftModifier
            if event['metaKey']:
                qevent_mod |= Qt.Qt.MetaModifier
            if event['altKey']:
                qevent_mod |= Qt.Qt.AltModifier
            return qevent_mod

        def get_mouse_event_buttons(event):
            qevent_btn = Qt.Qt.NoButton
            if event["button"] == 0:
                qevent_btn = Qt.Qt.LeftButton
            if event["button"] == 2:
                qevent_btn = Qt.Qt.RightButton
            elif event["button"] == 1:
                qevent_btn = Qt.Qt.MiddleButton

            qevent_btns = Qt.Qt.NoButton
            if event["buttons"] & 1:
                qevent_btns |= Qt.Qt.LeftButton
            if event["buttons"] & 2:
                qevent_btns |= Qt.Qt.RightButton
            elif event["buttons"] & 4:
                qevent_btns |= Qt.Qt.MiddleButton

            qevent_mod = get_key_modifiers(event)

            return qevent_btn, qevent_btns, qevent_mod

        def get_mouse_qevent(event):
            event_name = event["event"]
            if event_name == 'mousemove':
                qevent_type = Qt.QEvent.MouseMove
            elif event_name == 'mousedown':
                qevent_type = Qt.QEvent.MouseButtonPress
            elif event_name == 'mouseup':
                qevent_type = Qt.QEvent.MouseButtonRelease
            elif event_name == 'dblclick':
                qevent_type = Qt.QEvent.MouseButtonDblClick

            qevent_btn, qevent_btns, qevent_mod = get_mouse_event_buttons(
                event)
            qevent = Qt.QMouseEvent(
                qevent_type,
                Qt.QPointF(event["relativeX"], event['relativeY']),
                qevent_btn, qevent_btn, qevent_mod)

            return qevent

        def get_key_qevent(event):
            qevent_type = Qt.QEvent.KeyPress
            if event['event'] == 'keyup':
                qevent_type = Qt.QEvent.KeyRelease
            qevent_mod = get_key_modifiers(event)
            code = event['code']
            if not code.startswith('Key'):
                code = 'Key_%s' % code
            else:
                code = 'Key_%s' % code[3:]
            qevent_key = getattr(Qt.Qt, code)
            qevent_mod = get_key_modifiers(event)

            qevent = Qt.QKeyEvent(qevent_type, qevent_key, qevent_mod,
                                  event['key'], event['repeat'])
            return qevent

        event_name = event["event"]

        if debug:
            lines = ['{}: {}'.format(k, v) for k, v in event.items()]
            h.value = 'new event: %s' % event_name
            display(h)

        #if 'offsetX' in event:
            #event['offsetX'] = round(event["clientX"]-event["boundingRectLeft"]) #re-calculate coordinates
            #scale_x = self.width/event['boundingRectWidth']
            #event['offsetX'] = round(event['offsetX']*scale_x)
            #event['offsetY'] = round(event["clientY"]-event["boundingRectTop"]) #re-calculate coordinates
            #scale_y = self.height/event['boundingRectHeight']
            #event['offsetY'] = round(event['offsetY']*scale_y)


        try:
            if self.log_events:
                self.logged_events.append(event)
            if event_name == "mousemove":

                if self.message_timestamp_offset is None:
                    self.message_timestamp_offset = (
                        time.time() - event["timeStamp"] * 0.001
                    )

                self.last_mouse_move_event = event
                if not self.dragging and not self.track_mouse_move:
                    if debug:
                        content = '<br>'.join(lines)
                        h.value += '<br>' + content
                    return
                if self.adaptive_render_delay:
                    ageOfProcessedMessage = time.time() - (
                        event["timeStamp"] * 0.001 + self.message_timestamp_offset
                    )
                    if ageOfProcessedMessage > 1.5 * self.quick_render_delay_sec:
                        # we are falling behind, try to render less frequently
                        self.set_quick_render_delay(self.quick_render_delay_sec * 1.05)
                    elif ageOfProcessedMessage < 0.5 * self.quick_render_delay_sec:
                        # we can keep up with events, try to render more frequently
                        self.set_quick_render_delay(self.quick_render_delay_sec / 1.05)
                    if self.log_events:
                        self.age_of_processed_messages.append(
                            [ageOfProcessedMessage, self.quick_render_delay_sec]
                        )

                qevent = get_mouse_qevent(event)
                self.post_qevent(qevent)

            elif event_name == "mouseenter":
                self.last_mouse_move_event = None
                self.dragging = False

                qevent = Qt.QFocusEvent(Qt.QEvent.FocusIn,
                                        Qt.Qt.MouseFocusReason)
                self.post_qevent(qevent)

            elif event_name == "mouseleave":
                self.last_mouse_move_event = None
                if self.dragging:  # have to trigger a leave event and release event
                    self.dragging = False
                    qevent_btn, qevent_btns, qevent_mod \
                        = get_mouse_event_buttons(event)
                    qevent = Qt.QMouseEvent(
                        Qt.QEvent.MouseButtonRelease,
                        Qt.QPointF(event["relativeX"], event['relativeY']),
                        qevent_btn, qevent_btn, qevent_mod)
                    self.post_qevent(qevent)

                qevent = Qt.QFocusEvent(Qt.QEvent.FocusOut,
                                        Qt.Qt.MouseFocusReason)
                self.post_qevent(qevent)

            elif event_name == "mousedown":
                self.dragging = True
                qevent = get_mouse_qevent(event)
                self.post_qevent(qevent)

            elif event_name == "mouseup":
                self.dragging = False
                qevent = get_mouse_qevent(event)
                self.post_qevent(qevent)

            elif event_name == "dblclick":
                qevent = get_mouse_qevent(event)
                self.post_qevent(qevent)

            elif event_name == "keydown":
                if (
                    event["key"] != "Shift"
                    and event["key"] != "Control"
                    and event["key"] != "Alt"
                ):
                    qevent = get_key_qevent(event)
                    self.post_qevent(qevent)

            elif event_name == "keyup":
                if (
                    event["key"] != "Shift"
                    and event["key"] != "Control"
                    and event["key"] != "Alt"
                ):
                    qevent = get_key_qevent(event)
                    self.post_qevent(qevent)

            elif event_name == 'wheel':
                if 'wheel' in self.interaction_events.watched_events:
                    qevent_btn, qevent_btns, qevent_mod \
                        = get_mouse_event_buttons(event)
                    qevent = Qt.QWheelEvent(
                        Qt.QPointF(event['relativeX'], event['relativeY']),
                        Qt.QPointF(event['screenX'], event['screenY']),
                        Qt.QPoint(event['deltaX'], event['deltaY']),
                        Qt.QPoint(0, 0), -event['deltaY'] * 2, Qt.Qt.Vertical,
                        qevent_btns, qevent_mod)
                    self.post_qevent(qevent)

            #elif event_name == 'contextmenu':
                #qevent = Qt.QContextMenuEvent(
                    #Qt.QContextMenuEvent.Mouse,
                    #Qt.QPoint(event['relativeX'], event['relativeY']))

        except Exception as e:
            self.error = str(e)
            if debug:
                lines.append(str(e))

        if debug:
            content = ', '.join(lines)
            h.value += '<br>' + content

    def is_window3d(self):
        return hasattr(self.render_window, 'getInternalRep') \
            and hasattr(self.render_window.getInternalRep(), 'view') \
            and isinstance(self.render_window.view(),
                           anatomist.cpp.GLWidgetManager)

    def post_qevent(self, qevent):

        if self._only_3d:
            widget = self.ana_view
        else:
            widget = self.render_window.getInternalRep()
            if hasattr(qevent, 'pos'):
                w2 = widget.childAt(qevent.pos())
                if w2:
                    if hasattr(self, '_last_widget_event') \
                            and qevent.type() in (
                                Qt.QEvent.MouseButtonRelease,
                                Qt.QEvent.MouseMove, Qt.QEvent.FocusOut):
                        # these must happen in the same widget as they were
                        # started
                        w2 = self._last_widget_event
                    pos = w2.mapFromGlobal(widget.mapToGlobal(qevent.pos()))
                    widget = w2
                    if isinstance(qevent, Qt.QMouseEvent):
                        qevent = Qt.QMouseEvent(
                            qevent.type(), pos, qevent.button(),
                            qevent.buttons(), qevent.modifiers())
        self._last_widget_event = widget
        Qt.qApp.postEvent(widget, qevent)

        if not self.is_window3d():
            self.qtimer.singleShot(
                float(INTERACTION_THROTTLE) / 1000,
                partial(self.update_canvas, force_render=False,
                        quality=self._full_quality))

    def close(self):
        super().close()
        self._on_close()

    def __del__(self):
        super().__del__()
        self.close()


class NotebookAnatomist(anatomist.Anatomist):
    '''
    A derived Anatomist class which automatically redirects its views to
    Jupyter notebook canvases. It only overloads the createWindow() method
    which creates an AnatomistInteractiveWidget canvas together with each
    window. It is normally used with the "headless" variant of Anatomist.

    Usage, in a notebook::

        import anatomist.headless as ana

        a = ana.HeadlessAnatomist(
            implementation='anatomist.notebook.api.NotebookAnatomist')
        w = a.createWindow('3D')
        mesh = a.loadObject('/home/dr144257/data/ra_head.mesh')
        w.addObjects(mesh)

    This is also implemented as a variant of Anatomist implementation::

        import anatomist
        anatomist.setDefaultImplementation('notebook')
        import anatomist.api as ana

        a = ana.Anatomist()

    Or, simply::

        import anatomist.notebook as ana

        a = ana.Anatomist()

    ..note::

        In this example we load ``anatomist.notebook`̀̀` without the ``api``
        submodule, because the latter loads Qt and thus prevents the optimized
        headless implementation to load and use VirtualGL.

    The :meth:`createWindow` method overload adds an additonal keyword
    argument, ``only_3D`` which enables to display only the 3D rendering view,
    or the full window with buttons and sliders.
    '''

    def __singleton_init__(self, *args, **kwargs):

        super(NotebookAnatomist, self).__singleton_init__(*args, **kwargs)

    def createWindow(self, wintype, geometry=[], block=None,
                     no_decoration=None, options=None, only_3d=False):
        '''
        Overload for :meth:`anatomist.direct.api.Anatomist.createWindow` which embeds the window in a Jupyter notebook canvas. It has an additional optional keyword argument:

        Parameters
        ----------
        only_3d: bool
            if False, the full window is rendered in the notebook canvas
            (except that menubars are hidden since popups are not working).
            If True, only the 3D view part is rendered in the canvas (which
            should also be more efficient because it avoids a buffer copy).
        '''
        if only_3d:
            no_decoration = True
        win = super(NotebookAnatomist, self).createWindow(
            wintype, geometry=geometry, block=None,
            no_decoration=no_decoration, options=None)
        if not no_decoration:
            # hide menubars
            win.menuBar().hide()
        canvas = AnatomistInteractiveWidget(win, only_3d=only_3d)
        display(canvas)
        win.canvas = canvas
        return win

