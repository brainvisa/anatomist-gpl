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

from __future__ import absolute_import
import anatomist.cpp as anatomist
#from soma import aims
import sys

from soma.qt_gui.qt_backend import QtCore, QtGui

testControl = False


class PaletteContrastAction(anatomist.Action):
    def name(self):
        return 'PaletteContrastAction'

    def startContrast(self, x, y, globx, globy):
        self._start = (x, y)
        self._palettes = {}
        self._showGraphicsView(self.view())
        self._tmpitems = []
        self._drawPaletteInGraphicsView(self.view())

    def moveContrast(self, x, y, globx, globy):
        win = self.view().aWindow()
        objs = [o for o in win.Objects()
                if not isinstance(o, anatomist.AGraphObject)]
        diff = ((x - self._start[0]) / 500., (y - self._start[1]) / 500.)
        a = anatomist.Anatomist()
        for o in objs:
            if not win.isTemporary(o):
                pal = o.palette()
                if pal:
                    if o in self._palettes:
                        initpal = self._palettes[o]
                    else:
                        initpal = [pal.min1(), pal.max1()]
                        self._palettes[o] = initpal
                    val = initpal[1] + diff[1]
                    minval = initpal[0] + diff[0]
                    threshold = 0.5
                    if val < initpal[0] and initpal[1] > initpal[0]:
                        if diff[1] < -threshold:
                            val = initpal[0] + diff[1] + threshold
                        else:
                            val = initpal[0]
                    a.theProcessor().execute('SetObjectPalette', objects=[o],
                                             min=minval, max=val)
                elif isinstance(o, anatomist.MObject):
                    objs += [mo for mo in o if mo not in objs]
        self._drawPaletteInGraphicsView(self.view())

    def moveContrastMin(self, x, y, globx, globy):
        win = self.view().aWindow()
        objs = list(win.Objects())
        diff = ((x - self._start[0]) / 500., (y - self._start[1]) / 500.)
        a = anatomist.Anatomist()
        for o in objs:
            if not win.isTemporary(o):
                pal = o.palette()
                if pal:
                    if o in self._palettes:
                        initpal = self._palettes[o]
                    else:
                        initpal = [pal.min1(), pal.max1()]
                        self._palettes[o] = initpal
                    a.theProcessor().execute('SetObjectPalette', objects=[o],
                                             min=initpal[0] + diff[1])
                elif isinstance(o, anatomist.MObject):
                    objs += [mo for mo in o if mo not in objs]

    def stopContrast(self, x, y, globx, globy):
        del self._start
        del self._palettes
        self._removeGraphicsView(self.view())

    def resetPalette(self):
        win = self.view().aWindow()
        objs = win.Objects()
        a = anatomist.Anatomist()
        for o in objs:
            pal = o.palette()
            if pal:
                o.adjustPalette()
                a.theProcessor().execute('SetObjectPalette', objects=[o],
                                         min=pal.min1(), max=pal.max1())
            elif isinstance(o, anatomist.MObject):
                objs += [mo for mo in o if mo not in objs]

    def _graphicsViewOnWindow(self, view):
        glw = view.qglWidget()
        parent = glw.parent()
        if isinstance(parent, QtGui.QGraphicsView):
            return parent
        gv = glw.findChild(QtGui.QGraphicsView)
        if gv is not None:
            return gv
        l = QtGui.QVBoxLayout()
        glw.setLayout(l)
        gv = QtGui.QGraphicsView(glw)
        l.addWidget(gv, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
        gv.setFixedSize(150, 50)
        gv.setFrameStyle(QtGui.QFrame.NoFrame)
        return gv

    def _showGraphicsView(self, view):
        gv = self._graphicsViewOnWindow(view)
        gv.show()

    def _removeGraphicsView(self, view):
        gv = self._graphicsViewOnWindow(view)
        scene = gv.scene()
        if scene:
            for item in self._tmpitems:
                scene.removeItem(item)
        self._tmpitems = []
        if view.qglWidget().parent() is not gv:
            gv.hide()

    def _drawPaletteInGraphicsView(self, view):
        gv = self._graphicsViewOnWindow(view)
        win = view.aWindow()
        objs = list(win.Objects())
        obj = None
        for o in objs:
            if not win.isTemporary(o):
                pal = o.palette()
                if pal:
                    obj = o
                    break
                elif isinstance(o, anatomist.MObject):
                    objs += [mo for mo in o if mo not in objs]
        if obj is None:
            return
        gwidth = 150
        gheight = 50
        w = gwidth - 12
        baseh = int(round((gheight - 10) * 0.33 + 5))
        baseh2 = int(round((gheight - 10) * 0.66 + 5))
        img = pal.toQImage(w, baseh2 - baseh - 1)
        pix = QtGui.QPixmap.fromImage(img)
        scene = gv.scene()
        paintpen = QtGui.QPen(QtGui.QColor(150, 150, 100))
        if scene is None:
            scene = QtGui.QGraphicsScene(gv)
            gv.setScene(scene)
        for item in self._tmpitems:
            scene.removeItem(item)
        self._tmpitems = []
        item0 = QtGui.QGraphicsRectItem(0, 0, gwidth, gheight)
        item0.setPen(QtGui.QPen(QtGui.QColor(80, 80, 30)))
        scene.addItem(item0)
        self._tmpitems.append(item0)
        item = QtGui.QGraphicsRectItem(5, baseh, gwidth - 10, baseh2 - baseh,
                                       item0)
        item.setPen(paintpen)
        item = QtGui.QGraphicsLineItem(5, baseh, 5, 5, item0)
        item.setPen(paintpen)
        item = QtGui.QGraphicsLineItem(gwidth - 5, baseh, gwidth - 5, 5, item0)
        item.setPen(paintpen)
        pixitem = QtGui.QGraphicsPixmapItem(pix, item0)
        tr = pixitem.transform()
        tr.translate(6, baseh + 1)
        pixitem.setTransform(tr)
        xmin = 6 + w * pal.min1()
        xmax = 6 + w * pal.max1()
        if xmin >= 0 and xmin < w:
            line = QtGui.QGraphicsLineItem(
                xmin, baseh2, xmin, gheight-5, item0)
            line.setPen(paintpen)
        if xmax >= 0 and xmax < w:
            line = QtGui.QGraphicsLineItem(
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
        textpen = QtGui.QPen(QtGui.QColor(160, 100, 40))
        text = self._textGraphicsItem(self._format(palmin), xmin, baseh2 + 3,
                                      xmax, gwidth - 5, parentitem=item0)
        text.setPen(textpen)
        text = self._textGraphicsItem(self._format(palmax), xmax, baseh2 + 3,
                                      xmin, gwidth - 5, parentitem=item0)
        text.setPen(textpen)
        textpen = QtGui.QPen(QtGui.QColor(120, 120, 40))
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
        text = QtGui.QGraphicsSimpleTextItem(text, parentitem)
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


ad = anatomist.ActionDictionary.instance()
ad.addAction('PaletteContrastAction', PaletteContrastAction)


if testControl:
    class PaletteContrastControl(anatomist.Control):
        def __init__(self, prio=30):
            anatomist.Control.__init__(self, prio, 'PaletteContrastControl')

        def eventAutoSubscription(self, pool):
            key = QtCore.Qt
            NoModifier = key.NoModifier
            ShiftModifier = key.ShiftModifier
            ControlModifier = key.ControlModifier
            AltModifier = key.AltModifier
            self.mouseLongEventSubscribe(key.LeftButton, NoModifier,
                                         pool.action(
                                             'PaletteContrastAction').startContrast,
                                         pool.action(
                                             'PaletteContrastAction').moveContrast,
                                         pool.action('PaletteContrastAction').stopContrast, True)
            self.mouseLongEventSubscribe(key.LeftButton, ControlModifier,
                                         pool.action(
                                             'PaletteContrastAction').startContrast,
                                         pool.action(
                                             'PaletteContrastAction').moveContrastMin,
                                         pool.action('PaletteContrastAction').stopContrast, True)
            self.keyPressEventSubscribe(key.Key_C, NoModifier,
                                        pool.action("PaletteContrastAction").resetPalette)

    cd = anatomist.ControlDictionary.instance()
    cd.addControl('PaletteContrastControl', PaletteContrastControl, 30)
    cm = anatomist.ControlManager.instance()
    cm.addControl('QAGLWidget3D', '', 'PaletteContrastControl')
