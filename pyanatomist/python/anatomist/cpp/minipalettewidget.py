# -*- coding: utf-8 -*-
#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

''' Mini palette widget

Main class: :class:`MiniPaletteWidget`.

Other classes are part of the infrastructure and may be considered private.
'''

import anatomist.cpp as anatomist
from soma import aims
from soma.qt_gui.qt_backend import Qt
import weakref
import numpy as np


class _MiniPaletteWidgetobserver(anatomist.Observer):
    ''' Observer connecting MiniPaletteWidget and the anatomist object.

    MiniPaletteWidget cannot inherit directly both QWidget and Observer:
    it causes crashes in Observable::notifyObservers, the multiple
    inheritance seems to cause corruption somawhere in sip bindings, so we use
    a separate observer object.

    You should not matter about this, it is a private class.
    '''

    def __init__(self, palwid, object=None):
        super().__init__()
        self.palwid = weakref.ref(palwid)
        self.aobj = None
        if object is not None:
            self.aobj = weakref.ref(object)
        object.addObserver(self)

    def __del__(self):
        if self.aobj is not None and self.aobj() is not None:
            self.aobj().deleteObserver(self)

    def update(self, observer, arg):
        if self.palwid() is not None:
            self.palwid().update(observer, arg)


class ClickableGraphicsView(Qt.QGraphicsView):
    ''' QGraphicsView which emits signal for mouse press, move and release
    events.

    The normal QGraphicsView captures such events and do not expose them, so a
    widget containing the graphics view cannot react to mouse events, even if
    the graphivs view does nothing with them.
    '''

    mouse_pressed = Qt.Signal(Qt.QMouseEvent)
    ''' mouse_pressed = Qt.Signal(Qt.QMouseEvent)

    signal emitted upon mouse press event
    '''
    mouse_moved = Qt.Signal(Qt.QMouseEvent)
    ''' mouse_moved = Qt.Signal(Qt.QMouseEvent)

    signal emitted upon mouse move event
    '''
    mouse_released = Qt.Signal(Qt.QMouseEvent)
    ''' mouse_released = Qt.Signal(Qt.QMouseEvent)

    signal emitted upon mouse release event
    '''

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.mouse_pressed.emit(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.mouse_moved.emit(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.mouse_released.emit(event)


class MiniPaletteWidget(Qt.QWidget):
    ''' MiniPaletteWidget is the main class of the module.

    It provides a small sized palette widget which can be used both to display
    the palette in a GUI, and to edit the palette range (optionally).

    The palette view displayes the palette assigned to an object, and the view
    may be zoomed to a given values range.

    The palatte may be zoomed in/out using the mouse wheel. This action will
    not change the palette settings, but only the view displayed.

    Edition is possible if enabled, either using the allow_edit constructor
    parameter, or using the method :meth:`allow_edit`.

    Edition is triggered in 2 modes:

    - if ``click_to_edit`` is True (the default), a click on the palette will
      open the editor mode.
    - otherwise a mouse hover will open it, and it will be closed when the
      mouse leaves the editor, without the need for a user click.

    The edition mode opens a popup frameless widget, with sliders.
    See :class:`MiniPaletteWidgetTranscient`.
    '''

    range_changed = Qt.Signal(float, float)
    ''' range_changed = Qt.Signal(float, float)

    signal emitted when the zoom range has changed (after a mouse wheel event,
    typically)
    '''
    palette_clicked = Qt.Signal()
    ''' palette_clicked = Qt.Signal()

    signal emitted when the palete view is clicked, and ``click_to_edit`` mode
    is disabled.
    '''

    def __init__(self, object=None, allow_edit=True, edit_parent=0,
                 click_to_edit=True, auto_range=False):
        '''
        Parameters
        ----------
        object: :class:`AObject` or None
            object to display or edit the palette for
        allow_edit: bool
            if True, an editor will popup, either by clicking on the widget, or
            by "hovering" it if ``click_to_edit`` is False.
        edit_parent: :class:`QWidget` or None or 0
            the parent widget passed to the editor widget, if edition is
            allowed. The special value ``0`` means that the parent will be the
            :class:`MiniPaletteWidget`, ``self``.
        click_to_edit: bool
            if False, the edition widget will popup as soon as the mouse cursor
            passes over the palette widget, without clicking.
            If True, only a user click will open the editor window.
        auto_range: bool
            For edition mode, allow the auto-zoom mode when palette range is
            modified.
        '''
        super().__init__()
        self.aobj = None
        self.obs = None
        self.editor = None
        self.edit_parent = edit_parent
        self.min1 = 0.
        self.max1 = 1.
        self.click_to_edit = click_to_edit
        self.auto_range = auto_range
        self._tmpitems = []
        lay = Qt.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.graphicsview = ClickableGraphicsView()
        lay.addWidget(self.graphicsview)
        self.graphicsview.setFocusPolicy(Qt.Qt.NoFocus)
        #self.pixlabel = Qt.QLabel()
        #self.pixlabel.setFixedSize(150, 30)
        #lay.addWidget(self.pixlabel)
        if object is not None:
            self.set_object(object)
        self.allow_edit(allow_edit, edit_parent=edit_parent)
        self.graphicsview.mouse_released.connect(self.gv_released)

    def set_object(self, obj):
        'set or change the observed object'

        if self.obs is not None:
            self.obs = None
        self.aobj = weakref.ref(obj)

        if obj is not None:
            glc = obj.glAPI()
            if glc:
                extr = glc.glTexExtrema(0)
                pal = obj.palette()
                valmin = extr.minquant[0]
                valmax = extr.maxquant[0]
                if pal.zeroCenteredAxis1():
                    valmax = np.max(np.abs((valmin, valmax)))
                    valmin = -valmax
            self.set_range(valmin, valmax)

        self.obs = _MiniPaletteWidgetobserver(self, obj)
        self.update_display()

    def allow_edit(self, allow, edit_parent=0):
        ''' Enalbes or disable the edition capabilities

        Parameters
        ----------
        allow: bool
            if True, an editor will popup, either by clicking on the widget, or
            by "hovering" it if ``click_to_edit`` is False.
        edit_parent: :class:`QWidget` or None or 0
            the parent widget passed to the editor widget, if edition is
            allowed. The special value ``0`` means that the parent will be the
            :class:`MiniPaletteWidget`, ``self``.
        '''

        self.edit_allowed = allow
        self.edit_parent = edit_parent
        if allow:
            self.setFocusPolicy(Qt.Qt.StrongFocus)
        else:
            self.setFocusPolicy(Qt.Qt.NoFocus)

    def set_range(self, min1, max1):
        'set the view range in object values'

        self.min1 = min1
        self.max1 = max1

    def update_display(self):
        'redraws the palette view'

        if self.aobj is None:
            return
        if self.aobj() is None:
            self.obs = None
            self.aobj = None
            return

        self._drawPaletteInGraphicsView()

        #w = self.pixlabel.width()
        #h = self.pixlabel.height()
        #img = self.aobj().palette().toQImage(w, h)
        #pix = Qt.QPixmap.fromImage(img)
        #self.pixlabel.setPixmap(pix)

    def update(self, observable, arg):
        self.update_display()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

    def _drawPaletteInGraphicsView(self):
        gv = self.graphicsview
        obj = self.aobj()
        if obj is None:
            return
        pal = obj.palette()
        gwidth = self.width() - 2
        gheight = self.height() - 2
        w = gwidth - 12
        baseh = int(round((gheight - 10) * 0.33 + 5))
        if baseh > 30:
            baseh = 30
        baseh2 = gheight - baseh + 3
        # print('rel values:', pal.relValue1(obj, self.min1), pal.relValue1(obj, self.max1))
        # print('pal minmax:', pal.min1(), pal.max1())
        img = pal.toQImage(w, baseh2 - baseh - 1,
                           pal.relValue1(obj, self.min1),
                           pal.relValue1(obj, self.max1))
        pix = Qt.QPixmap.fromImage(img)
        scene = gv.scene()
        paintpen = Qt.QPen(Qt.QColor(150, 150, 100))
        if scene is None:
            scene = Qt.QGraphicsScene(gv)
            gv.setScene(scene)
        for item in self._tmpitems:
            scene.removeItem(item)
        scene.setSceneRect(0, 0, gwidth, gheight)
        self._tmpitems = []
        item0 = Qt.QGraphicsRectItem(0, 0, gwidth, gheight)
        item0.setPen(Qt.QPen(Qt.QColor(80, 80, 30)))
        scene.addItem(item0)
        self._tmpitems.append(item0)
        item = Qt.QGraphicsRectItem(5, baseh, gwidth - 10, baseh2 - baseh,
                                    item0)
        item.setPen(paintpen)
        item = Qt.QGraphicsLineItem(5, baseh, 5, 5, item0)
        item.setPen(paintpen)
        item = Qt.QGraphicsLineItem(gwidth - 5, baseh, gwidth - 5, 5, item0)
        item.setPen(paintpen)
        pixitem = Qt.QGraphicsPixmapItem(pix, item0)
        tr = pixitem.transform()
        tr.translate(6, baseh + 1)
        pixitem.setTransform(tr)
        palmin = pal.absMin1(obj)
        palmax = pal.absMax1(obj)
        valmin = self.min1
        valmax = self.max1

        xmin = 6 + w * (palmin - valmin) / (valmax - valmin)
        xmax = 6 + w * (palmax - valmin) / (valmax - valmin)
        pmin = pal.min1()
        #pmax = pal.max1()
        #if pal.zeroCenteredAxis1():
            #pmin = 0.5 + pmin / 2
            #pmax = 0.5 + pmax / 2
        #xmin = 6 + w * pmin
        #xmax = 6 + w * pmax
        # print('xmin, xmax:', xmin, xmax)
        if xmin >= 0 and xmin < w:
            line = Qt.QGraphicsLineItem(
                xmin, baseh2, xmin, gheight-5, item0)
            line.setPen(paintpen)
        if xmax >= 0 and xmax < w:
            line = Qt.QGraphicsLineItem(
                xmax, baseh2, xmax, gheight-5, item0)
            line.setPen(paintpen)

        # print('valmin, valmax:', valmin, valmax)
        # print('palmin, palmax:', palmin, palmax)
        textpen = Qt.QPen(Qt.QColor(160, 100, 40))
        text = self._textGraphicsItem(self._format(palmin), xmin, baseh2 + 3,
                                      xmax, gwidth - 5, parentitem=item0)
        text.setPen(textpen)
        text = self._textGraphicsItem(self._format(palmax), xmax, baseh2 + 3,
                                      xmin, gwidth - 5, parentitem=item0)
        text.setPen(textpen)
        textpen = Qt.QPen(Qt.QColor(120, 120, 40))
        text = self._textGraphicsItem(self._format(valmin), 8, 5,
                                      gwidth - 5, gwidth - 5, parentitem=item0)
        text.setPen(textpen)
        text = self._textGraphicsItem(self._format(valmax), gwidth - 10, 5,
                                      gwidth - 5, gwidth - 5, parentitem=item0)
        text.setPen(textpen)
        tr = item0.transform()
        tr.translate((gv.width() - gwidth) / 2, gv.height() - gheight - 5)
        item0.setTransform(tr)

    @staticmethod
    def _format(num):
        x = abs(num)
        if x < 0.1 or x > 100000:
            if x == 0.:
                return '0'
            return '%.3e' % num
        if x < 1:
            return '%.4f' % num
        if x < 10:
            return '%.3f' % num
        elif x < 100:
            return '%.2f' % num
        elif x < 1000:
            return '%.1f' % num
        else:
            return '%.0f' % num

    def _textGraphicsItem(self, text, xpos, ypos, xmax, hardmax=None,
                          parentitem=None):
        text = Qt.QGraphicsSimpleTextItem(text, parentitem)
        font = text.font()
        font.setPointSize(6)
        text.setFont(font)
        tr = text.transform()
        x = xpos + 3
        w = text.boundingRect().right()
        # avoid intersecting xmax
        # print('text:', x, w, xmax, hardmax, ':', text.text())
        if xpos < xmax and x + w >= xmax - 3:
            x = xmax - 3 - w
            # avoid intersecting its own line marker
            if x <= xpos and x + w >= xpos and xpos >= w + 3:
                x = xpos - w - 3
        if x < 4:
            x = 4
        # avoid hardmax (right end of the view)
        if hardmax is not None and x + w >= hardmax:
            x = hardmax - w - 3
        tr.translate(x, ypos)
        text.setTransform(tr)
        return text

    def show_editor(self):
        'pops up the editor, if the edition is allowed'

        if not self.edit_allowed:
            return
        # print('show_editor')

        if self.editor is None:
            parent = self.edit_parent
            if parent == 0:
                # artifical way of saying we are the parent
                parent = self
            self.editor = MiniPaletteWidgetTranscient(
                self.aobj(), self, parent=parent,
                opened_by_click=self.click_to_edit, auto_range=self.auto_range)
            self.editor.editor_closed.connect(self.editor_closed)
        else:
            self.editor.reposition()
        self.editor.show()

    def hide_editor(self):
        if self.editor is not None:
            self.editor.hide()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if not self.click_to_edit:
            self.show_editor()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)

    def enterEvent(self, event):
        super().enterEvent(event)
        if not self.click_to_edit:
            self.show_editor()

    def leaveEvent(self, event):
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.click_to_edit:
            event.accept()
            self.show_editor()

    def gv_released(self, event):
        if self.click_to_edit:
            event.accept()
            self.show_editor()
        else:
            self.palette_clicked.emit()

    def wheelEvent(self, event):
        # super().wheelEvent(event)
        event.accept()
        if event.angleDelta().y() > 0:
            scale = 0.5
        else:
            scale = 2.
        obj = self.aobj()
        if obj is None:
            return
        pal = obj.palette()
        if pal.zeroCenteredAxis1():
            c = (self.max1 + self.min1) / 2.
        else:
            c = (pal.absMax1(obj) + pal.absMin1(obj)) / 2
        nmin = c - (self.max1 - self.min1) / 2 * scale
        nmax = c + (self.max1 - self.min1) / 2 * scale
        self.set_range(nmin, nmax)
        self.update_display()
        self.range_changed.emit(nmin, nmax)

    def editor_closed(self):
        self.set_range(self.editor.minipw.minipw.min1,
                       self.editor.minipw.minipw.max1)
        self.update_display()


class _MiniPWSlider(Qt.QSlider):
    ''' Specialized slider class for palette editor
    :class:`MiniPaletteWidgetEdit`.

    Internal class, please consider it private.

    It features float min/max values matching an AObject texture values,
    magnets which mark some given significant values, and emits signals when
    the slider is moved.

    The values range can be changed afterwards.
    '''

    abs_value_changed = Qt.Signal(float)
    ''' abs_value_changed = Qt.Signal(float)

    signal emitted when the value changes, in object texture value scale
    '''
    slider_pressed = Qt.Signal(str)
    ''' slider_pressed = Qt.Signal(str)

    signal emitted when the slider is pressed
    '''
    slider_moved = Qt.Signal(str)
    ''' slider_moved = Qt.Signal(str)

    signal emitted when the slider is moved
    '''
    slider_released = Qt.Signal(str)
    ''' slider_released = Qt.Signal(str)

    signal emitted when the slider is released
    '''

    def __init__(self, orientation=None, parent=None):
        if orientation is not None:
            super().__init__(orientation, parent)
        else:
            super().__init__(parent)
        self.setMinimum(0)
        self.setMaximum(1000)
        self.setValue(500)
        self.presspos = None
        self.magnets = []
        self.pressval = None
        self.mag_size = 20.
        self.set_range(0, 1000)

    def set_magnets(self, magnets):
        ''' Magnets are "attractive" values, where the mouse must be moved
        further to pass them when moving the slider.
        '''
        self.magnets = magnets
        # print('magnets:', self.magnets)

    def set_range(self, min1, max1):
        # print('set range:', min1, max1)
        self.min1 = min1
        self.max1 = max1

    def set_value(self, value):
        self.current_val = value
        d = self.max1 - self.min1
        if d == 0:
            d = 1.
        # print('set value:', value, int((value - self.min1) * 1000 / d), ', range:', self.min1, self.max1)
        self.setValue(int((value - self.min1) * 1000 / d))

    def abs_value(self):
        return self.current_val

    def mousePressEvent(self, event):
        self.presspos = event.pos()
        self.pressval = self.current_val
        super().mousePressEvent(event)
        self.slider_pressed.emit(self.objectName())

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.presspos is not None:
            xdiff = event.pos().x() - self.presspos.x()
            # print('move:', xdiff)
            nval_i = xdiff / self.width()
            nval = self.pressval + nval_i * (self.max1 - self.min1)
            # print('nval:', nval)
            vrange = [min((self.pressval, nval)), max((self.pressval, nval))]
            # print('vrange:', vrange)
            nval_set = False
            if xdiff < 0:
                mrange = reversed(self.magnets)
            else:
                mrange = self.magnets
            for m in mrange:
                if m > vrange[0] and m < vrange[1]:
                    if xdiff > 0:
                        xdiff -= self.mag_size
                        nval_i = xdiff / self.width()
                        old_nval = nval
                        nval = self.pressval + nval_i * (self.max1 - self.min1)
                        # print('x:', xdiff, ', nv:', nval)
                        if old_nval >= m and nval <= m:
                            nval = m
                            nval_set = True
                            break
                    else:
                        xdiff += self.mag_size
                        nval_i = xdiff / self.width()
                        old_nval = nval
                        nval = self.pressval + nval_i * (self.max1 - self.min1)
                        # print('x:', xdiff, ', nv:', nval)
                        if old_nval <= m and nval >= m:
                            nval = m
                            nval_set = True
                            break
                    vrange = [min((self.pressval, nval)),
                              max((self.pressval, nval))]
            if not nval_set:
                # print('new xdiff:', xdiff)
                nval_i = xdiff / self.width()
                nval = self.pressval + nval_i * (self.max1 - self.min1)
            # print('new nval:', nval)
            self.set_value(nval)
            self.abs_value_changed.emit(nval)
        self.slider_moved.emit(self.objectName())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        absval = self.abs_value()
        #self.current_val = absval
        self.abs_value_changed.emit(absval)
        self.slider_released.emit(self.objectName())


class MiniPaletteWidgetEdit(Qt.QWidget):
    ''' Mini palette editor widget.

    :class:`MiniPaletteWidgetEdit` is part of the :class:`MiniPaletteWidget`
    infrastructure and in most cases will not be used directly.

    However a GUI may incorporate the editor widget.

    It is normally used within :class:`MiniPaletteWidgetTranscient`, itself
    used in the edition mode of :class:`MiniPaletteWidget`. In turn,
    :class:`MiniPaletteWidgetEdit` contains a non-editable
    :class:`MiniPaletteWidget` object.

    The editor thus presents a palette view, plus 2 sliders to set the min and
    max range of the palette. The view may be zoomed using the mouse wheel (see
    :class:`MiniPaletteWidget`), and it can also use an automatic zoom mode, if
    ``auto_range=True`` is passed to the constructor, or :meth:`set_auto_range`
    is called. In auto range mode, the zoom range is adapted after each user
    interaction on sliders (after the mouse is released).
    '''

    def __init__(self, object=None, auto_range=False):
        super().__init__()
        layout = Qt.QVBoxLayout()
        self.setLayout(layout)
        self.minslider = _MiniPWSlider(Qt.Qt.Horizontal)
        self.minslider.setObjectName('min_slider')
        self.minipw = MiniPaletteWidget(allow_edit=False, click_to_edit=False)
        self.maxslider = _MiniPWSlider(Qt.Qt.Horizontal)
        self.maxslider.setObjectName('max_slider')
        self.auto_range = False
        self.auto_btn = None
        self.auto_btn_timer = None
        layout.addWidget(self.minslider)
        layout.addWidget(self.minipw)
        layout.addWidget(self.maxslider)
        self.set_object(object)
        self.minipw.graphicsview.setMouseTracking(True)
        self.minipw.graphicsview.mouse_moved.connect(self.gv_moved)
        self.minslider.abs_value_changed.connect(self.min_changed)
        self.maxslider.abs_value_changed.connect(self.max_changed)
        self.set_auto_range(auto_range)
        self.minipw.range_changed.connect(self.set_range)
        self.minipw.palette_clicked.connect(self.select_palette)

    def set_object(self, obj):
        'set or change the observed object'

        self.minipw.set_object(obj)
        if obj.glAPI() is None or obj.glAPI().glTexExtrema() is None:
            return
        self.minipw.obs = _MiniPaletteWidgetobserver(self, obj)
        self.adjust_range()

    def set_auto_range(self, auto_range):
        'allows or disables the auto-zoom mode'

        if auto_range == self.auto_range:
            return
        self.auto_range = auto_range
        if auto_range:
            self.minslider.slider_released.connect(self.adjust_range)
            self.maxslider.slider_released.connect(self.adjust_range)
        else:
            self.minslider.slider_released.disconnect(self.adjust_range)
            self.maxslider.slider_released.disconnect(self.adjust_range)

    def adjust_range(self):
        'auto-range function'

        obj = self.minipw.aobj()
        if obj is not None:
            pal = obj.palette()
            te = obj.glAPI().glTexExtrema()
            tmin = te.minquant[0]
            tmax = te.maxquant[0]
            min1 = pal.min1()
            max1 = pal.max1()
            absmin1 = pal.absMin1(obj)
            absmax1 = pal.absMax1(obj)
            obj.adjustPalette()
            pal = obj.palette()
            self.defmin = pal.absMin1(obj)
            self.defmax = pal.absMax1(obj)
            pal.setMin1(min1)
            pal.setMax1(max1)
            rmax = max((abs(tmax), abs(tmin), absmax1, absmin1))
            if pal.zeroCenteredAxis1():
                if rmax > max((abs(absmin1), abs(absmax1))) * 2:
                    rmax = max((abs(absmin1), abs(absmax1))) * 2
                # rmin = min((absmin1, absmax1, 0))
                rmin = -rmax
            else:
                rmin = min((absmin1, absmax1, tmin, tmax))
                if abs(absmax1 - absmin1) < abs(rmax - rmin) / 2:
                    s = abs(absmax1 - absmin1)
                    c = (absmin1 + absmax1) / 2
                    rmin2 = c - s
                    rmax2 = c + s
                    if rmin < rmin2:
                        rmin = rmin2
                    else:
                        c = (rmin + max((absmin1, absmax1))) / 2
                        s = max((absmin1, absmax1)) - rmin
                        rmax2 = c + s
                    if rmax > rmax2:
                        rmax = rmax2
            # print('set range:', rmin, rmax)
            self.minslider.set_range(rmin, rmax)
            self.maxslider.set_range(rmin, rmax)
            self.minslider.set_value(absmin1)
            self.maxslider.set_value(absmax1)
            self.minipw.set_range(rmin, rmax)
            self.minipw.update_display()

    def update_display(self):
        'redraws the palette and sliders values'

        self.minipw.update_display()
        obj = self.minipw.aobj()
        if obj is not None:
            te = obj.glAPI().glTexExtrema()
            pal = obj.palette()
            mag = set([te.minquant[0], te.maxquant[0],
                       self.defmin, self.defmax])
            if pal.zeroCenteredAxis1():
                mag.add(0)
                mag.add(max((abs(te.minquant[0]), abs(te.maxquant[0]))))
            mag = sorted(mag)
            self.minslider.set_magnets(mag)
            self.minslider.set_value(pal.absMin1(obj))
            self.maxslider.set_magnets(mag)
            self.maxslider.set_value(pal.absMax1(obj))

    def update(self, observable, arg):
        self.update_display()

    def min_changed(self, value):
        obj = self.minipw.aobj()
        if obj is not None:
            pal = obj.palette()
            if pal.absMin1(obj) != value:
                pal.setAbsMin1(obj, value)
                obj.glSetTexImageChanged()
                obj.notifyObservers()

    def max_changed(self, value):
        # print('max_changed:', value)
        obj = self.minipw.aobj()
        if obj is not None:
            pal = obj.palette()
            if pal.absMax1(obj) != value:
                pal.setAbsMax1(obj, value)
                obj.glSetTexImageChanged()
                obj.notifyObservers()

    def set_range(self, rmin, rmax):
        self.minslider.set_range(rmin, rmax)
        self.maxslider.set_range(rmin, rmax)
        obj = self.minipw.aobj()
        if obj is not None:
            pal = obj.palette()
            absmin1 = pal.absMin1(obj)
            absmax1 = pal.absMax1(obj)
            self.minslider.set_value(absmin1)
            self.maxslider.set_value(absmax1)

    def select_palette(self):
        dial = Qt.QDialog(self, Qt.Qt.Popup | Qt.Qt.FramelessWindowHint)
        lay = Qt.QVBoxLayout()
        dial.setLayout(lay)
        palsel = anatomist.PaletteSelectWidget(self)
        lay.addWidget(palsel)
        butl = Qt.QHBoxLayout()
        lay.addLayout(butl)
        but = Qt.QPushButton('Done')
        but.setSizePolicy(Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Fixed)
        butl.addWidget(but)
        but.setDefault(True)
        but.clicked.connect(dial.accept)
        palsel.paletteSelected.connect(self.set_palette)
        dial.resize(500, 800)
        dial.exec()

    def set_palette(self, palname):
        obj = self.minipw.aobj()
        if obj is not None:
            pal = obj.palette()
            ana = anatomist.Anatomist()
            apal = ana.palettes().find(palname)
            pal.setRefPalette(apal)
            obj.glSetTexImageChanged()
            obj.notifyObservers()

    def gv_moved(self, event):
        pos = event.pos()
        if pos.x() >= self.minipw.graphicsview.width() - 40 \
                and pos.y() <= self.minipw.graphicsview.height() * 0.3:
            if self.auto_btn is None:
                self.auto_btn = Qt.QToolButton(self.minipw)
                icon_path = aims.carto.Paths.findResourceFile('icons/auto.png',
                                                              'anatomist')
                icon = Qt.QIcon(icon_path)
                self.auto_btn.setIcon(icon)
                self.auto_btn.setFixedSize(32, 32)
                self.auto_btn.setCheckable(True)
                self.auto_btn.setChecked(self.auto_range)
                self.auto_btn.setToolTip('auto-scale mode')
                self.auto_btn.toggled.connect(self.set_auto_range)
            self.auto_btn.move(self.minipw.graphicsview.width() - 40, 30)
            self.auto_btn.show()
            if self.auto_btn_timer is None:
                self.auto_btn_timer = Qt.QTimer(self)
                self.auto_btn_timer.setSingleShot(True)
                self.auto_btn_timer.setInterval(2000)
                self.auto_btn_timer.timeout.connect(self.clear_auto_btn)
            self.auto_btn_timer.start()

    def clear_auto_btn(self):
        self.auto_btn.hide()


class MiniPaletteWidgetTranscient(Qt.QWidget):
    ''' The transcient palette editor widget features a
    :class:`MiniPaletteWidgetEdit` which shows up upon given conditions (see
    :class:`MiniPaletteWidget`) and closes when the editor widget loses focus.

    More precisely, if opened by a click, a complete focus loss is needed to
    close the window (which is generally triggered by another user action like
    a click at some other place or a keyboard focus change, using <tab> for
    instance).

    If not opened by a click, the widget will close as soon as the mouse
    pointer leaves the widget surface, or when the focus is lost, thus not
    requiring a click or keyboard user action.
    '''

    editor_closed = Qt.Signal()
    ''' editor_closed = Qt.Signal()

    signal emitted when the editor widget closes
    '''

    def __init__(self, object=None, pw=None, parent=None,
                 opened_by_click=False, auto_range=False):
        super().__init__(parent, Qt.Qt.Popup | Qt.Qt.FramelessWindowHint)
        self.setObjectName('frameless_minipalette')
        #self.setAutoFillBackground(False)
        #self.setStyleSheet(
          #'QWidget#frameless_minipalette{margin: 20px; padding: 20px; background-color: transparent; color: red;};'
          #'QSlider{background-color: transparent;}')
        layout = Qt.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.pw = pw
        self._out_focus = False
        self._released = True
        self.opened_by_click = opened_by_click
        self.minipw = MiniPaletteWidgetEdit(object, auto_range=auto_range)
        layout.addWidget(self.minipw)
        self.reposition()
        self.minipw.minslider.slider_pressed.connect(self.slider_pressed)
        self.minipw.maxslider.slider_pressed.connect(self.slider_pressed)
        self.minipw.minslider.slider_released.connect(self.slider_released)
        self.minipw.maxslider.slider_released.connect(self.slider_released)

    def reposition(self):
        ''' Repositions / resizes the widget to superpose on its
        :class:`MiniPaletteWidget`
        '''
        pw = self.pw
        if pw is not None:
            pw.ensurePolished()
            rect = pw.geometry()
            # print('rect:', rect)
            pos = pw.mapToGlobal(Qt.QPoint(0, 0))
            # print('global:', pos)
            #  parent = self.parentWidget()
            # print('width:', pw.width())
            # print('parent:', parent)
            #if parent is not None:
                #pos = parent.mapFromGlobal(pos)
                #print('to parent:', pos)
            rect.setTop(max((pos.y() - 30, 0)))
            rect.setLeft(max((pos.x() - 9, 0)))
            rect.setWidth(pw.width() + 9)
            rect.setHeight(pw.height() + 30)
            self.setGeometry(rect)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        # if opened by a click (an explicit active action),
        # don't close when leaving the window: the user will do another
        # explicit action (click outside) to close the editor.
        if not self.opened_by_click:
            self._out_focus = True
            self.close_if_finished()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._out_focus = True
        self.close_if_finished()

    def enterEvent(self, event):
        super().enterEvent(event)
        self._out_focus = False

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._out_focus = False

    def close_if_finished(self):
        if self._out_focus and self._released:
            self.close()

    def slider_pressed(self):
        self._released = False

    def slider_released(self):
        self._released = True
        self.close_if_finished()

    def closeEvent(self, event):
        super().closeEvent(event)
        if event.isAccepted():
            self.editor_closed.emit()
