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

''' Module providing a control to set the colormap ranges

Main class: :class:`PaletteContrastAction`
'''

import anatomist.cpp as anatomist
from soma.qt_gui.qt_backend import QtCore, QtGui
from anatomist.cpp import MiniPaletteGraphics


testControl = False


class PaletteContrastAction(anatomist.Action):
    ''' Anatomist Action class for palette contrasts adjustment
    '''

    def name(self):
        return 'PaletteContrastAction'

    def startContrast(self, x, y, globx, globy):
        'action start'

        self._start = (x, y)
        self._palettes = {}
        self._showGraphicsView(self.view())
        self.minipw = None
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
        'action move'

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
        'action stop'

        del self._start
        del self._palettes
        self._removeGraphicsView(self.view())

    def resetPalette(self):
        'reset the palette to standard values'

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
        self.minipw = None
        import gc
        gc.collect()

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

        if self.minipw is None:
            gwidth = 150
            gheight = 60
            self.minipw = MiniPaletteGraphics(gv, obj, 0, gwidth, gheight,
                                              -10000, -70)
        self.minipw.updateDisplay()


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
