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

Main classes: :class:`MiniPaletteWidget`, :class:`MiniPaletteGraphics`.

The former is a QWidget, the latter is an object which draws in a
QGraphicsView. MiniPaletteWidget is using MiniPaletteGraphics under the hood,
but the latter can be used independently to display a palette view in an
existing QGrpahicsView.

Other classes are part of the infrastructure and may be considered private.
'''

import anatomist.cpp as anatomist
from soma import aims
from soma.qt_gui.qt_backend import Qt
import weakref
import numpy as np
import time


class _MiniPaletteWidgetobserver(anatomist.Observer):
    ''' Observer connecting MiniPaletteWidget and the anatomist object.

    MiniPaletteWidget cannot inherit directly both QWidget and Observer:
    it causes crashes in Observable::notifyObservers, the multiple
    inheritance seems to cause corruption somewhere in sip bindings, so we use
    a separate observer object.

    You should not matter about this, it is a private class.
    '''

    def __init__(self, palwid, object=None):
        super().__init__()
        self.palwid = weakref.ref(palwid)
        self.aobj = None
        if object is not None:
            self.aobj = anatomist.weak_shared_ptr_AObject(object)
        object.addObserver(self)

    def __del__(self):
        if self.aobj is not None and not self.aobj.isNull():
            self.aobj.deleteObserver(self)

    def update(self, observable, arg):
        if self.palwid() is not None:
            self.palwid().update(observable, arg)


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
        # print('create', self)
        super().__init__()
        self.editor = None
        self.edit_parent = edit_parent
        self.click_to_edit = click_to_edit
        self.auto_range = auto_range
        lay = Qt.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.graphicsview = anatomist.QClickGraphicsView()
        lay.addWidget(self.graphicsview)
        self.graphicsview.setFocusPolicy(Qt.Qt.FocusPolicy.NoFocus)
        self.minipg = anatomist.MiniPaletteGraphics(self.graphicsview, object)
        if object is not None:
            self.set_object(object)
        self.allow_edit(allow_edit, edit_parent=edit_parent)
        self.graphicsview.mouseReleased.connect(self.gv_released)

    def __del__(self):
        self.clear()

    def get_object(self):
        return self.minipg.getObject()

    def set_object(self, obj):
        'set or change the observed object'

        self.minipg.setObject(obj)
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
            self.setFocusPolicy(Qt.Qt.FocusPolicy.StrongFocus)
        else:
            self.setFocusPolicy(Qt.Qt.FocusPolicy.NoFocus)

    def set_range(self, min1, max1):
        'set the view range in object values'

        self.minipg.setRange(min1, max1)

    def update_display(self):
        'redraws the palette view'

        self.minipg.updateDisplay()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

    def clear(self):
        self.minipg.clear()

    def show_editor(self):
        'pops up the editor, if the edition is allowed'

        obj = self.get_object()
        if not self.edit_allowed or obj is None:
            return
        # print('show_editor')

        if self.editor is None:
            parent = self.edit_parent
            if parent == 0:
                # artifical way of saying we are the parent
                parent = self
            self.editor = MiniPaletteWidgetTranscient(
                obj, self, parent=parent,
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
        obj = self.get_object()
        if obj is None:
            return
        pal = obj.palette()
        if pal.zeroCenteredAxis1():
            c = (self.minipg.max1() + self.minipg.min1) / 2.
        else:
            c = (pal.absMax1(obj) + pal.absMin1(obj)) / 2
        nmin = c - (self.minipg.max1() - self.minipg.min1()) / 2 * scale
        nmax = c + (self.minipg.max1() - self.minipg.min1()) / 2 * scale

        te = obj.glAPI().glTexExtrema()
        tmin = te.minquant[0]
        tmax = te.maxquant[0]
        absmin1 = pal.absMin1(obj)
        absmax1 = pal.absMax1(obj)
        rmax = max((abs(tmax), abs(tmin), absmax1, absmin1))
        if pal.zeroCenteredAxis1():
            if nmax < rmax:
                rmax = nmax
            rmin = -rmax
        else:
            rmin = min((absmin1, absmax1, tmin, tmax))
            if rmin < nmin:
                rmin = nmin
            if rmax > nmax:
                rmax = nmax

        self.set_range(rmin, rmax)
        self.update_display()
        self.range_changed.emit(rmin, rmax)

    def editor_closed(self):
        self.set_range(self.editor.minipw.minipw.minipg.min1(),
                       self.editor.minipw.minipw.minipg.max1())
        self.update_display()


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
        self.minslider = anatomist.QMagnetSlider(Qt.Qt.Horizontal)
        self.minslider.setObjectName('min_slider')
        self.minipw = MiniPaletteWidget(allow_edit=False, click_to_edit=False)
        self.maxslider = anatomist.QMagnetSlider(Qt.Qt.Horizontal)
        self.maxslider.setObjectName('max_slider')
        self.auto_range = False
        self.auto_btn = None
        self.auto_btn_timer = None
        layout.addWidget(self.minslider)
        layout.addWidget(self.minipw)
        layout.addWidget(self.maxslider)
        self.set_object(object)
        self.minipw.graphicsview.setMouseTracking(True)
        self.minipw.graphicsview.mouseMoved.connect(self.gv_moved)
        self.minslider.absValueChanged.connect(self.min_changed)
        self.maxslider.absValueChanged.connect(self.max_changed)
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
            self.minslider.sliderReleased.connect(self.adjust_range)
            self.maxslider.sliderReleased.connect(self.adjust_range)
        else:
            self.minslider.sliderReleased.disconnect(self.adjust_range)
            self.maxslider.sliderReleased.disconnect(self.adjust_range)

    def adjust_range(self):
        'auto-range function'

        obj = self.minipw.get_object()
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
            self.minslider.setRange(rmin, rmax)
            self.maxslider.setRange(rmin, rmax)
            self.minslider.setValue(absmin1)
            self.maxslider.setValue(absmax1)
            self.minipw.set_range(rmin, rmax)
            self.minipw.update_display()

    def update_display(self):
        'redraws the palette and sliders values'

        self.minipw.update_display()
        obj = self.minipw.get_object()
        if obj is not None:
            te = obj.glAPI().glTexExtrema()
            pal = obj.palette()
            mag = set([te.minquant[0], te.maxquant[0],
                       self.defmin, self.defmax])
            if pal.zeroCenteredAxis1():
                mag.add(0)
                mag.add(max((abs(te.minquant[0]), abs(te.maxquant[0]))))
            mag = sorted(mag)
            self.minslider.setMagnets(mag)
            self.minslider.setDefault(self.defmin)
            self.minslider.setValue(pal.absMin1(obj))
            self.maxslider.setMagnets(mag)
            self.maxslider.setDefault(self.defmax)
            self.maxslider.setValue(pal.absMax1(obj))

    def update(self, observable, arg):
        self.update_display()

    def min_changed(self, value):
        obj = self.minipw.get_object()
        if obj is not None:
            pal = obj.palette()
            if pal.absMin1(obj) != value:
                pal.setAbsMin1(obj, value)
                obj.glSetTexImageChanged()
                obj.notifyObservers()

    def max_changed(self, value):
        # print('max_changed:', value)
        obj = self.minipw.get_object()
        if obj is not None:
            pal = obj.palette()
            if pal.absMax1(obj) != value:
                pal.setAbsMax1(obj, value)
                obj.glSetTexImageChanged()
                obj.notifyObservers()

    def set_range(self, rmin, rmax):
        self.minslider.setRange(rmin, rmax)
        self.maxslider.setRange(rmin, rmax)
        obj = self.minipw.get_object()
        if obj is not None:
            pal = obj.palette()
            absmin1 = pal.absMin1(obj)
            absmax1 = pal.absMax1(obj)
            self.minslider.setValue(absmin1)
            self.maxslider.setValue(absmax1)

    def select_palette(self):
        dial = Qt.QDialog(self,
                          Qt.Qt.WindowType.Popup | Qt.Qt.FramelessWindowHint)
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
        palsel.itemDoubleClicked.connect(dial.accept)
        dial.resize(500, 800)
        dial.exec()

    def set_palette(self, palname):
        obj = self.minipw.get_object()
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
                and pos.y() <= 80:
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
        super().__init__(parent,
                         Qt.Qt.WindowType.Popup | Qt.Qt.FramelessWindowHint)
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
        self.minipw.minslider.sliderPressed.connect(self.slider_pressed)
        self.minipw.maxslider.sliderPressed.connect(self.slider_pressed)
        self.minipw.minslider.sliderPressed.connect(self.slider_released)
        self.minipw.maxslider.sliderPressed.connect(self.slider_released)

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Qt.Key_Escape:
            event.accept()
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)
        if event.isAccepted():
            self.editor_closed.emit()
