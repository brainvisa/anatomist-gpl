# -*- coding: iso-8859-1 -*-
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
from soma.qt_gui.qt_backend import QtCore, QtGui
from soma import aims
from soma.qt_gui.rangeSlider import QRangeSlider
from tempfile import mkstemp
import anatomist.api as ana
import os
import sys
import six


class PaletteEditor(QtGui.QGroupBox):

    paletteMinMaxChanged = QtCore.Signal(object)

    def __init__(self, image,
                 default=None, title="", palette_filter=None,
                 real_min=0, real_max=100,
                 parent=None, sliderPrecision=100, zoom=1,
                 all_palettes=False):
        QtGui.QGroupBox.__init__(self, parent)

        self.real_min = real_min
        self.real_max = real_max
        self.sliderPrecision = sliderPrecision

        self.palette_image_temp_path = None

        a = ana.Anatomist('-b')
        self.image = image
        self.setTitle(title)

        vlay = QtGui.QVBoxLayout(self)
        vlay.setContentsMargins(0, 0, 0, 0)

        font = QtGui.QFont()
        font.setPixelSize(12 * zoom)

        if palette_filter is not None or all_palettes:
            hlay = QtGui.QHBoxLayout()
            vlay.addLayout(hlay)
            hlay.addSpacerItem(QtGui.QSpacerItem(
                20, 20, hPolicy=QtGui.QSizePolicy.Expanding))
            self.palettecb = QtGui.QComboBox(self)
            self.palettecb.setFont(font)
            if(zoom > 1.0):
                self.palettecb.setFixedWidth(256 * zoom)
            else:
                self.palettecb.setFixedWidth(256 * zoom * zoom)
            self.palettecb.setToolTip("Change the palette")
            hlay.addWidget(self.palettecb)
            hlay.addSpacerItem(QtGui.QSpacerItem(
                20, 20, hPolicy=QtGui.QSizePolicy.Expanding))
        else:
            self.palettecb = None

        hlay = QtGui.QHBoxLayout()
        hlay.setContentsMargins(0, 0, 0, 0)
        hlay.setSpacing(0)

        vlay.addLayout(hlay)

        if isinstance(self.real_min, float) or isinstance(self.real_max, float):
            self.minsb = QtGui.QDoubleSpinBox(self)
            self.minsb.setFont(font)
            self.minsb.setSingleStep(0.1)
        else:
            self.minsb = QtGui.QSpinBox(self)
        self.minsb.setFixedWidth(62 * zoom)
        self.minsb.setRange(self.real_min, self.real_max)
        self.minsb.setToolTip("Change the palette minimum value")
        self.minsb.setFont(font)
        hlay.addWidget(self.minsb)

        self.rangeslider = QRangeSlider()
        self.rangeslider.show()
        self.rangeslider.setFixedHeight(32 * zoom)
        self.rangeslider.setFixedWidth(256 * zoom * zoom)
        self.rangeslider.setMin(0)
        self.rangeslider.setMax(sliderPrecision)
        self.rangeslider.setRange(0, sliderPrecision)
        hlay.addWidget(self.rangeslider)

        if isinstance(self.real_min, float) or isinstance(self.real_max, float):
            self.maxsb = QtGui.QDoubleSpinBox(self)
            self.maxsb.setSingleStep(0.1)
        else:
            self.maxsb = QtGui.QSpinBox(self)
        self.maxsb.setFixedWidth(62 * zoom)
        self.maxsb.setRange(self.real_min, self.real_max)
        self.maxsb.setToolTip("Change the palette maximum value")
        self.maxsb.setFont(font)
        hlay.addWidget(self.maxsb)

        self.paletteDic = {}

        if all_palettes:
            self.loadAllPaletteList()
        else:
            self.loadPaletteList(palette_filter)

        if(default is None):
          # set palette name using current object palette info
            try:
                default = ((image.palette()).refPalette()).name()
            except:
                default = None

        if palette_filter is not None or all_palettes:
            self.palettecb.currentIndexChanged[str].connect(
                self.paletteNameChanged)

        if palette_filter is not None or all_palettes:
            try:
                self.palettecb.setCurrentIndex(self.paletteDic[default])
            except:
                self.palettecb.setCurrentIndex(0)

        self.minsb.valueChanged.connect(self.minSbChanged)
        self.maxsb.valueChanged.connect(self.maxSbChanged)

        # set palette bound using current object palette info
        paletteStart = image.palette().min1() * (real_max - real_min) + real_min
        paletteStart = int(paletteStart)
        paletteEnd = image.palette().max1() * (real_max - real_min) + real_min
        paletteEnd = int(paletteEnd)
        self.rangeslider.setStart(
            int(image.palette().min1() * (real_max - real_min) + real_min))
        self.rangeslider.setEnd(
            int(image.palette().max1() * (real_max - real_min) + real_min))
#        self.rangeslider.setStart(0)
#        self.rangeslider.setEnd(100)
        self._paletteMinMaxChanged()

        self.rangeslider.startValueChanged.connect(self._paletteMinMaxChanged)
        self.rangeslider.endValueChanged.connect(self._paletteMinMaxChanged)

    def setImage(self, image, realMin=None, realMax=None):
        self.image = image
        pal = self.image.getOrCreatePalette()

        if self.palettecb:
            self.palettecb.blockSignals(True)
            self.palettecb.setCurrentIndex(
                self.paletteDic[pal.refPalette().name()])
            self.palettecb.blockSignals(False)

        if realMin:
            self.real_min = realMin
        if realMax:
            self.real_max = realMax

        min = ((self.real_max - self.real_min)*pal.min1()) + self.real_min
        max = ((self.real_max - self.real_min)*pal.max1()) + self.real_min

        self.minsb.setRange(self.real_min, self.real_max)
        self.maxsb.setRange(self.real_min, self.real_max)
        self.minsb.setValue(self.real_min)
        self.maxsb.setValue(self.real_max)
        self.minsb.setValue(min)
        self.maxsb.setValue(max)

    def loadAllPaletteList(self):
        a = ana.Anatomist('-b')
        for p in a.palettes().palettes():
            self.paletteDic.update({p.name(): self.palettecb.count()})
            self.palettecb.addItem(p.name())

    def loadPaletteList(self, palette_filter):
        if palette_filter == []:
            return

        a = ana.Anatomist('-b')
        for p in a.palettes().palettes():
            name = p.name()
            if palette_filter and not name in palette_filter:
                continue
            if self.palettecb is None:
                continue

            self.paletteDic.update({p.name(): self.palettecb.count()})
            self.palettecb.addItem(p.name())

    def paletteNameChanged(self, name):
        a = ana.Anatomist('-b')
        apal = self.image.getOrCreatePalette()
        self.image.setPalette(name,
                              minVal=apal.min1(),
                              maxVal=apal.max1())
        self._paletteMinMaxChanged()

    def _paletteMinMaxChanged(self):
        a = ana.Anatomist('-b')
        min = self.rangeslider.start()
        max = self.rangeslider.end()
        refpal = self.image.getOrCreatePalette().refPalette()
        self.image.setPalette(refpal.name(),
                              minVal=min*(1.0/self.sliderPrecision),
                              maxVal=max*(1.0/self.sliderPrecision))

        if not self.rangeslider._movingHandle:
            paletteinfo = self.updatePaletteLabel()
            if self.palette_image_temp_path is not None:
                if os.path.exists(self.palette_image_temp_path):
                    os.remove(self.palette_image_temp_path)
                else:
                    raise Exception(
                        'The temporary palette image has not been normally deleted')
            else:
                self.palette_image_temp_path = mkstemp()[1]

            paletteinfo[0].save(self.palette_image_temp_path, "PNG")
            self.rangeslider.setStyleSheet("QRangeSlider * { border: 0px; padding: 0px; } \
                                            QRangeSlider #Head { background: " + paletteinfo[1] + " repeat-x; } \
                                            QRangeSlider #Span { background: url(" + self.palette_image_temp_path + ") repeat-x; } \
                                            QRangeSlider #Tail { background: " + paletteinfo[2] + " repeat-x; } \
                                            QRangeSlider > QSplitter::handle { background: #888888; } \
                                            QRangeSlider > QSplitter::handle:vertical { height: 4px; } \
                                            QRangeSlider > QSplitter::handle:pressed { background: #ACACAC; } ")

        real_min = ((self.real_max - self.real_min) * min /
                    self.sliderPrecision) + self.real_min
        real_max = ((self.real_max - self.real_min) * max /
                    self.sliderPrecision) + self.real_min

        self.minsb.blockSignals(True)
        self.minsb.setValue(real_min)
        self.minsb.blockSignals(False)
        self.maxsb.blockSignals(True)
        self.maxsb.setValue(real_max)
        self.maxsb.blockSignals(False)

        self.paletteMinMaxChanged.emit(self.image)

    def updatePaletteLabel(self):
        apal = self.image.getOrCreatePalette()
        min = apal.min1()
        max = apal.max1()

        refpal = apal.refPalette()
        dimx = refpal.getSizeX()
        dimy = refpal.getSizeY()
        if dimy < 32:
            dimy = 32
        if dimx > 256:
            dimx = 256
        elif dimx == 0:
            dimx = 1
        if dimy > 256:
            dimy = 256
        if abs(max - min) <= sys.float_info.epsilon:
            min = 0
            max = 1

        facx = float(refpal.getSizeX()) / dimx
        facy = float(refpal.getSizeY()) / dimy

        rgb = aims.AimsRGBA
        minx = dimx * min
        maxx = dimx * max

        range = int(maxx-minx)

        imbackground = QtGui.QImage(QtCore.QSize(range, int(dimy)), 4)
        pmbackground = QtGui.QPixmap()

        for x in six.moves.xrange(dimx):
            rgb = refpal.value(int(facx * x), 0)

            for y in six.moves.xrange(dimy):
                xpal = int(x*(maxx-minx)/dimx)
                if xpal >= range:
                    xpal = range-1

                imbackground.setPixel(xpal, y, QtGui.qRgb(
                    rgb.red(), rgb.green(), rgb.blue()))

        if QtCore.QT_VERSION_STR < '4.7':
            pmbackground = QtGui.QPixmap.fromImage(imbackground)
        else:
            pmbackground.convertFromImage(imbackground)

        rgb = refpal.value(0, 0)
        valueinf = '#%02x%02x%02x' % (rgb.red(), rgb.green(), rgb.blue())
        rgb = refpal.value(int(facx * (dimx-1)), int(facy * (dimy-1)))
        valuesup = '#%02x%02x%02x' % (rgb.red(), rgb.green(), rgb.blue())

        return (pmbackground, valueinf, valuesup)

    def minSbChanged(self, value):
        if value >= self.maxsb.value():
            value = self.maxsb.value()-1

        slider_value = self.sliderPrecision * \
            (value - self.real_min) / (self.real_max - self.real_min)

        self.rangeslider.setStart(int(slider_value))

    def maxSbChanged(self, value):
        if value <= self.minsb.value():
            value = self.minsb.value()+1

        slider_value = self.sliderPrecision * \
            (value - self.real_min) / (self.real_max - self.real_min)

        self.rangeslider.setEnd(int(slider_value))

    def setPaletteComBoxEditable(self, boolean_state):
        self.palettecb.setEditable(boolean_state)

    def changeCurrentImage(self, image):
        a = ana.Anatomist('-b')
        min = self.rangeslider.start()
        max = self.rangeslider.end()
        refpal = self.image.getOrCreatePalette().refPalette()
        palette_object = a.getPalette(str(refpal.name()))
        image.setPalette(palette_object,
                         minVal=min*(1.0/self.sliderPrecision),
                         maxVal=max*(1.0/self.sliderPrecision))
        self.image = image

    def closeEvent(self, event):
        if self.palette_image_temp_path is not None:
            if os.path.exists(self.palette_image_temp_path):
                os.remove(self.palette_image_temp_path)
            else:
                raise Exception(
                    'The temporary palette image has not been normally deleted')
        else:
            raise Exception(
                'paletteEditor instance was closed before palette_image_temp_path variate creation')
        event.accept()
