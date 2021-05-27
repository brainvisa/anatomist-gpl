
"""
Embed an Anatomist 3D view in a jupyter notebook widget

To work this notebook widget needs:

* to install ipycanvas, ipyevents, ipywidgets, PIL, numpy, anatomist, jupyter notebook
* to register jupyter notebook extensions (may require sudo permissions if
  jupyter is installed system-wide)::

    jupyter nbextension enable --py widgetsnbextension
    jupyter nbextension enable --py ipyevents
    jupyter nbextension enable --py ipycanvas

Typical use, in a notebook cell::

    import anatomist.headless as ana
    from anatomist.nbanatomist import AnatomistInteractiveWidget

    a = ana.HeadlessAnatomist()
    w = a.createWindow('3D')
    mesh = a.loadObject('/home/riviere/data/ra_head.mesh')
    w.addObjects(mesh)

    canvas = AnatomistInteractiveWidget(w)
    display(canvas)

"""

from ipycanvas import Canvas
import anatomist.headless as ana
from ipywidgets import Image
from io import BytesIO
from soma.qt_gui import qt_backend
import PIL

import time
import logging
import weakref
from io import BytesIO
import PIL.Image

from ipycanvas import Canvas
from ipyevents import Event
import numpy as np
from ipywidgets import Image


### throttler.py:

## the throttler does not seem to work in python 3.6 at least.

#import asyncio

INTERACTION_THROTTLE = 100

#class Timer:
    #def __init__(self, timeout, callback):
        #self._timeout = timeout
        #self._callback = callback
        #self._task = asyncio.ensure_future(self._job())

    #async def _job(self):
        #await asyncio.sleep(self._timeout)
        #self._callback()

    #def cancel(self):
        #self._task.cancel()


#def throttle(wait):
    #""" Decorator that prevents a function from being called
        #more than once every wait period. """

    #def decorator(fn):
        #time_of_last_call = 0
        #scheduled = False
        #new_args, new_kwargs = None, None

        #def throttled(*args, **kwargs):
            #nonlocal new_args, new_kwargs, time_of_last_call, scheduled

            #def call_it():
                #nonlocal new_args, new_kwargs, time_of_last_call, scheduled
                #time_of_last_call = time.time()
                #fn(*new_args, **new_kwargs)
                #scheduled = False

            #time_since_last_call = time.time() - time_of_last_call
            #new_args = args
            #new_kwargs = kwargs
            #if not scheduled:
                #new_wait = max(0, wait - time_since_last_call)
                #Timer(new_wait, call_it)
                #scheduled = True

        #return throttled

    #return decorator


## viewer.py

log = logging.getLogger(__name__)
log.setLevel("CRITICAL")
#log.setLevel("DEBUG")
log.addHandler(logging.StreamHandler())
debug = False

if debug:
    from ipywidgets import HTML
    h = HTML('Event info')

class AnatomistInteractiveWidget(Canvas):
    """Taken and modified from:
    https://github.com/Kitware/ipyvtklink/blob/master/ipyvtklink/viewer.py

    Remote controller for Anatomist render windows.
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
                 quick_quality=50, on_close=None, **kwargs):

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

        # refresh if mouse is just moving (not dragging)
        self.track_mouse_move = False

        self.message_timestamp_offset = None

        self.layout.width = '%dpx' % awindow.getInternalRep().width()
        self.layout.height = '%dpx' % awindow.getInternalRep().height()

        # Set Canvas size from window size
        self.width, self.height \
            = self.render_window.width(), self.render_window.height()

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

    def set_quick_render_delay(self, delay_sec):
        if delay_sec < self.quick_render_delay_sec_range[0]:
            delay_sec = self.quick_render_delay_sec_range[0]
        elif delay_sec > self.quick_render_delay_sec_range[1]:
            delay_sec = self.quick_render_delay_sec_range[1]
        self.quick_render_delay_sec = delay_sec

    def update_canvas(self, force_render=True, quality=75):
        """Updates the canvas with the current render"""
        raw_img = self.get_image(force_render=force_render)
        f = BytesIO()
        PIL.Image.fromarray(raw_img).save(f, 'JPEG', quality=quality)
        image = Image(
            value=f.getvalue(), width=self.width, height=self.height
        )
        self.draw_image(image)

    def get_image(self, force_render=True):
        if force_render:
            self.render_window.camera(force_redraw=1)
        return self._fast_image

    @property
    def _fast_image(self):
        qdata = self.render_window.snapshotImage()
        data = qt_backend.qimage_to_np(qdata)

        if self.transparent_background:
            return data
        else:  # ignore alpha channel
            return data[:, :, :-1]

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

    def send_pending_mouse_move_event(self):
        if self.last_mouse_move_event is not None:
            self.last_mouse_move_event = None

    #@throttle(0.01)
    def quick_render(self):
        try:
            self.send_pending_mouse_move_event()
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

        if 'offsetX' in event:
            event['offsetX'] = round(event["clientX"]-event["boundingRectLeft"]) #re-calculate coordinates
            scale_x = self.width/event['boundingRectWidth']
            event['offsetX'] = round(event['offsetX']*scale_x)
            event['offsetY'] = round(event["clientY"]-event["boundingRectTop"]) #re-calculate coordinates
            scale_y = self.height/event['boundingRectHeight']
            event['offsetY'] = round(event['offsetY']*scale_y)

        from soma.qt_gui.qt_backend import Qt

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
                Qt.qApp.postEvent(self.render_window.getInternalRep().view(),
                                  qevent)

                # We need to render something now it no rendering
                # since self.quick_render_delay_sec
                if time.time() - self.last_render_time > self.quick_render_delay_sec:
                    self.quick_render()
            elif event_name == "mouseenter":
                #self.interactor.EnterEvent()
                self.last_mouse_move_event = None

                qevent = Qt.QFocusEvent(Qt.QEvent.FocusInEvent,
                                        Qt.Qt.MouseFocusReason)
                Qt.qApp.postEvent(self.render_window.getInternalRep().view(),
                                  qevent)
            elif event_name == "mouseleave":
                #self.interactor.LeaveEvent()
                self.last_mouse_move_event = None
                if self.dragging:  # have to trigger a leave event and release event
                    #self.interactor.LeftButtonReleaseEvent()
                    self.dragging = False

                qevent = Qt.QFocusEvent(Qt.QEvent.FocusOutEvent,
                                        Qt.Qt.MouseFocusReason)
                Qt.qApp.postEvent(self.render_window.getInternalRep().view(),
                                  qevent)
                self.full_render()
            elif event_name == "mousedown":
                self.dragging = True
                self.send_pending_mouse_move_event()
                qevent = get_mouse_qevent(event)
                Qt.qApp.postEvent(self.render_window.getInternalRep().view(),
                                  qevent)

                self.full_render()  # does this have to be rendered?
            elif event_name == "mouseup":
                self.send_pending_mouse_move_event()
                qevent = get_mouse_qevent(event)
                Qt.qApp.postEvent(self.render_window.getInternalRep().view(),
                                  qevent)

                self.full_render()
            elif event_name == "dblclick":
                self.send_pending_mouse_move_event()
                qevent = get_mouse_qevent(event)
                Qt.qApp.postEvent(self.render_window.getInternalRep().view(),
                                  qevent)

                self.full_render()
            elif event_name == "keydown":
                self.send_pending_mouse_move_event()
                if (
                    event["key"] != "Shift"
                    and event["key"] != "Control"
                    and event["key"] != "Alt"
                ):
                    qevent = get_key_qevent(event)
                    Qt.qApp.postEvent(
                        self.render_window.getInternalRep().view(), qevent)
                    self.full_render()
            elif event_name == "keyup":
                self.send_pending_mouse_move_event()
                if (
                    event["key"] != "Shift"
                    and event["key"] != "Control"
                    and event["key"] != "Alt"
                ):
                    qevent = get_key_qevent(event)
                    Qt.qApp.postEvent(
                        self.render_window.getInternalRep().view(), qevent)
                    self.full_render()
            elif event_name == 'wheel':
                if 'wheel' in self.interaction_events.watched_events:
                    self.send_pending_mouse_move_event()
                    qevent_btn, qevent_btns, qevent_mod \
                        = get_mouse_event_buttons(event)
                    qevent = Qt.QWheelEvent(
                        Qt.QPointF(event['relativeX'], event['relativeY']),
                        Qt.QPointF(event['screenX'], event['screenY']),
                        Qt.QPoint(event['deltaX'], event['deltaY']),
                        Qt.QPoint(0, 0), -event['deltaY'] * 2, Qt.Qt.Vertical,
                        qevent_btns, qevent_mod)
                    Qt.qApp.postEvent(
                        self.render_window.getInternalRep().view(), qevent)
                    self.full_render()

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

    def close(self):
        super().close()
        self._on_close()

    def __del__(self):
        super().__del__()
        self.close()


if __name__ == '__main__':

    a = ana.HeadlessAnatomist()
    w = a.createWindow('3D')
    mesh = a.loadObject('/home/riviere/data/ra_head.mesh')
    w.addObjects(mesh)

    canvas = AnatomistInteractiveWidget(w)
    display(canvas)
    if debug:
        display(h)


