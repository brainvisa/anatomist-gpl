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

import anatomist.cpp as anatomist
from soma.qt_gui.qt_backend import Qt
import weakref


class _MiniPaletteWidgetobserver(anatomist.Observer):
    # MiniPaletteWidget cannot inherit directly both QWidget and Observer:
    # it causes crashes in Observable::notifyObservers, the multiple
    # inheritance seems to cause corruption somawhere in sip binidings

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


class MiniPaletteWidget(Qt.QWidget):

    def __init__(self, object=None, allow_edit=True):
        super().__init__()
        self.aobj = None
        self.obs = None
        self.editor = None
        self._tmpitems = []
        lay = Qt.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.graphicsview = Qt.QGraphicsView()
        lay.addWidget(self.graphicsview)
        #self.pixlabel = Qt.QLabel()
        #self.pixlabel.setFixedSize(150, 30)
        #lay.addWidget(self.pixlabel)
        if object is not None:
            self.set_object(object)
        self.allow_edit(allow_edit)

    def set_object(self, obj):
        if self.obs is not None:
            self.obs = None
        self.aobj = weakref.ref(obj)
        self.obs = _MiniPaletteWidgetobserver(self, obj)
        self.update_display()

    def allow_edit(self, allow):
        self.edit_allowed = allow
        if allow:
            self.setFocusPolicy(Qt.Qt.StrongFocus)
        else:
            self.setFocusPolicy(Qt.Qt.NoFocus)

    def update_display(self):
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
        img = pal.toQImage(w, baseh2 - baseh - 1)
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
        xmin = 6 + w * pal.min1()
        xmax = 6 + w * pal.max1()
        if xmin >= 0 and xmin < w:
            line = Qt.QGraphicsLineItem(
                xmin, baseh2, xmin, gheight-5, item0)
            line.setPen(paintpen)
        if xmax >= 0 and xmax < w:
            line = Qt.QGraphicsLineItem(
                xmax, baseh2, xmax, gheight-5, item0)
            line.setPen(paintpen)
        valmin = 0.
        valmax = 1.
        glc = obj.glAPI()
        if glc:
            extr = glc.glTexExtrema(0)
            valmin = extr.minquant[0]
            valmax = extr.maxquant[0]
            del extr, glc
        palmin = valmin + (valmax - valmin) * pal.min1()
        palmax = valmin + (valmax - valmin) * pal.max1()
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
        if x < xmax and x + w >= xmax - 3:
            x = xmax - 3 - w
        if x < 4:
            x = 4
        if hardmax is not None and x + w >= hardmax:
            x = hardmax - w - 3
        tr.translate(x, ypos)
        text.setTransform(tr)
        return text

    def show_editor(self):
        if not self.edit_allowed:
            return

        if self.editor is None:
            self.editor = MiniPaletteWidgetTranscient(self.aobj(), self)
        else:
            self.editor.reposition()
        self.editor.show()

    def hide_editor(self):
        if self.editor is not None:
            self.editor.hide()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.show_editor()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        #self.hide_editor()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.show_editor()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        #self.hide_editor()


class _MiniPWSlider(Qt.QSlider):

    abs_value_changed = Qt.Signal(float)

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

    def set_magnets(self, magnets):
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
        # print('set value:', value, int((value - self.min1) * 1000 / d))
        self.setValue(int(value * 1000 / d))

    def abs_value(self):
        return self.current_val

    def mousePressEvent(self, event):
        self.presspos = event.pos()
        self.pressval = self.current_val
        super().mousePressEvent(event)

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

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        absval = self.abs_value()
        self.current_val = absval
        self.abs_value_changed.emit(absval)


class MiniPaletteWidgetEdit(Qt.QWidget):

    def __init__(self, object=None):
        super().__init__()
        layout = Qt.QVBoxLayout()
        self.setLayout(layout)
        self.minslider = _MiniPWSlider(Qt.Qt.Horizontal)
        self.minipw = MiniPaletteWidget(allow_edit=False)
        self.maxslider = _MiniPWSlider(Qt.Qt.Horizontal)
        layout.addWidget(self.minslider)
        layout.addWidget(self.minipw)
        layout.addWidget(self.maxslider)
        self.set_object(object)
        self.minslider.abs_value_changed.connect(self.min_changed)
        self.maxslider.abs_value_changed.connect(self.max_changed)

    def set_object(self, obj):
        self.minipw.set_object(obj)
        if obj.glAPI() is None or obj.glAPI().glTexExtrema() is None:
            return
        self.minipw.obs = _MiniPaletteWidgetobserver(self, obj)
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
                rmin = min((absmin1, absmax1, 0))
            else:
                rmin = min((absmin1, absmax1, tmin, tmax))
            self.minslider.set_range(rmin, rmax)
            self.maxslider.set_range(rmin, rmax)
            self.minslider.set_value(absmin1)
            self.maxslider.set_value(absmax1)

    def update_display(self):
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
                obj.setChanged()
                obj.notifyObservers()

    def max_changed(self, value):
        obj = self.minipw.aobj()
        if obj is not None:
            pal = obj.palette()
            if pal.absMax1(obj) != value:
                pal.setAbsMax1(obj, value)
                obj.setChanged()
                obj.notifyObservers()


class MiniPaletteWidgetTranscient(Qt.QWidget):

    def __init__(self, object=None, parent=None):
        super().__init__(parent, Qt.Qt.Popup | Qt.Qt.FramelessWindowHint)
        self.setObjectName('frameless_minipalette')
        #self.setAutoFillBackground(False)
        #self.setStyleSheet(
          #'QWidget#frameless_minipalette{margin: 20px; padding: 20px; background-color: transparent; color: red;};'
          #'QSlider{background-color: transparent;}')
        layout = Qt.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.minipw = MiniPaletteWidgetEdit(object)
        layout.addWidget(self.minipw)
        self.reposition()

    def reposition(self):
        parent = self.parentWidget()
        if parent is not None:
            rect = parent.geometry()
            rect.setTop(max((rect.top() - 30, 0)))
            rect.setLeft(max((rect.left() - 9, 0)))
            rect.setWidth(rect.width() + 9)
            rect.setHeight(rect.height() + 30)
            self.setGeometry(rect)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.close()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.close()

