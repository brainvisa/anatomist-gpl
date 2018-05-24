#! /bin/env python

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
import sys
import os
import weakref
import gc
import operator
import anatomist.direct.api as anatomist
from soma.qt_gui.qt_backend.QtCore import Qt, QPoint
from soma.qt_gui.qt_backend.QtGui import QSplitter, QListWidget, QTextEdit, \
    QApplication
from soma import aims

from soma.qt_gui import qt_backend
qt_backend.init_matplotlib_backend()
import matplotlib
import numpy
import pylab

FigureCanvas = qt_backend.FigureCanvas
from matplotlib.figure import Figure


class MeasuresWindow(QSplitter):

    def __init__(self, fileName, roiIterator=None, parent=None,
                 anatomistInstance=None):
        QSplitter.__init__(self, Qt.Horizontal, parent)
        if anatomistInstance is None:
            # initialize Anatomist
            self.anatomist = anatomist.Anatomist()
        else:
            self.anatomist = anatomistInstance

        # open an axial window
        self.aWindow = self.anatomist.createWindow(
            'Axial', no_decoration=True)
        self.aWindow.setParent(self)

        if roiIterator is not None:
            self.roiList = QListWidget(self)
            self.maskIterators = []
            # Iterate on each region
            while roiIterator.isValid():
                self.roiList.addItem(roiIterator.regionName())
                maskIterator = roiIterator.maskIterator().get()
                maskIterator.bucket = None
                self.maskIterators.append(maskIterator)
                roiIterator.next()
            self.selectedBucket = None
            self.roiList.currentRowChanged.connect(self.regionSelected)
        else:
            self.roiList = None

        self.infoSplitter = QSplitter(Qt.Vertical, self)
        self.info = QTextEdit(self.infoSplitter)
        self.info.setReadOnly(True)

        self.matplotFigure = Figure()
        self.matplotAxes = self.matplotFigure.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.matplotAxes.hold(False)

        self.matplotCanvas = FigureCanvas(self.matplotFigure)
        self.matplotCanvas.setParent(self.infoSplitter)
        self.matplotCanvas.updateGeometry()

        self.anatomist.onCursorNotifier.add(self.clicked2)

        self.resize(800, 600)

        # Read the image
        dir, base = os.path.split(fileName)
        if dir:
            self.setWindowTitle(base + ' (' + dir + ')')
        else:
            self.setWindowTitle(base)
        # load any volume as a aims.Volume_* object
        r = aims.Reader({'Volume': 'AimsData'})
        self.volume = r.read(fileName)
        self.interpolator = aims.aims.getLinearInterpolator(self.volume).get()

        # convert the AimsData volume to Anatomist API
        avol = self.anatomist.toAObject(self.volume)
        # put volume in window
        self.aWindow.addObjects(avol)

        self._ignoreClicked = False
        voxelSize = self.volume.header()['voxel_size']
        tmp = self.volume.header()['volume_dimension']
        volumeSize = [int(i) for i in tmp]
        volumeCenter = [v * s / 2 for v, s in zip(volumeSize, voxelSize)]
        self.clicked(volumeCenter)

        infoHeight = self.info.sizeHint().height()
        self.infoSplitter.setSizes([infoHeight, self.height() - infoHeight])

    def clicked2(self, eventName, eventParameters):
        self.clicked(eventParameters['position'], eventParameters['window'])

    def clicked(self, posMM, aWindow=None):
        posMM = [float(i) for i in posMM]
        if self._ignoreClicked:
            return
        text = '<html><body>\n'
        text += '<b>Coordinate millimeters:</b> %.2f, %.2f, %.2f, %.2f' % tuple(
            posMM) + '<br/>\n'
        voxelSize = self.volume.header()['voxel_size']
        posVoxel = [int(round(i / j)) for i, j in zip(posMM, voxelSize)]
        text += '<b>Coordinate voxels:</b> %d, %d, %d, %d' % tuple(
            posVoxel) + '<br/>\n'
        tmp = self.volume.header()['volume_dimension']
        volumeSize = [int(i) for i in tmp]
        if not [None for i in posVoxel if i < 0] and  \
           not [None for i, j in zip(posVoxel, volumeSize) if i >= j]:
            text += '<b>Voxel value</b>: ' + \
                str(self.volume.value(*posVoxel)) + '<br/>\n'
            if volumeSize[3] > 1:
                indices = numpy.arange(volumeSize[3])
                # Extract values as numarray structure
                values = self.interpolator.values(posVoxel[0] * voxelSize[0],
                                                  posVoxel[1] * voxelSize[1],
                                                  posVoxel[2] * voxelSize[2])
                self.matplotAxes.plot(indices, numpy.array(values))
                self.matplotCanvas.draw()
        text += '</body></html>'
        self.info.setText(text)

    def regionSelected(self):
        index = self.roiList.currentRow()
        if index >= 0:
            text = '<html><body>\n'
            text += '<h2>' + \
                unicode(self.roiList.item(index).text()) + '</h2>\n'

            maskIterator = self.maskIterators[index]
            if maskIterator.bucket is None:
                roiCenter = aims.Point3df(0, 0, 0)
                bucket = aims.BucketMap_VOID()
                bucket.setSizeXYZT(*maskIterator.voxelSize().items() + (1,))
                maskIterator.restart()
                valid = 0
                invalid = 0
                sum = None
                # Iterate on each point of a region
                while maskIterator.isValid():
                    bucket[0][maskIterator.value()] = 1
                    p = maskIterator.valueMillimeters()
                    roiCenter += p
                    # Check if the point is in the image limit
                    if self.interpolator.isValid(p):
                        values = self.interpolator.values(p)
                        if sum is None:
                            sum = values
                        else:
                            sum = [s + v for s, v in zip(sum, values)]
                        valid += 1
                    else:
                        invalid += 1
                    maskIterator.next()
                text += '<b>valid points:</b> ' + str(valid) + '<br/>\n'
                text += '<b>invalid points:</b> ' + str(invalid) + '<br/>\n'
                if valid:
                    means = [s / float(valid) for s in sum]
                    mean = reduce(operator.add, means) / len(means)
                else:
                    means = []
                    mean = 'N/A'
                text += '<b>mean:</b> ' + str(mean) + '<br/>\n'
                text += '</body></html>'
                maskIterator.text = text
                # convert the BucketMap to Anatomist API
                maskIterator.bucket = self.anatomist.toAObject(bucket)
                maskIterator.bucket.setName(
                    str(self.roiList.item(index).text()))
                maskIterator.bucket.setChanged()
                count = valid + invalid
                if count:
                    maskIterator.roiCenter = [
                        c / count for c in roiCenter.items()]
                else:
                    maskIterator.roiCenter = None
                maskIterator.means = means

            # put bucket in window
            self.info.setText(maskIterator.text)
            self.aWindow.addObjects([maskIterator.bucket])
            # Set selected color to bucket
            maskIterator.bucket.setMaterial(self.anatomist.Material(
                diffuse=[1, 0, 0, 0.5],
                                    lighting=0,
                                    face_culling=1,
            ))
            # Set unselected color to previously selected bucket
            if self.selectedBucket is not None:
                self.selectedBucket.setMaterial(
                    self.anatomist.Material(diffuse=[0, 0.8, 0.8, 0.8]))
            self.selectedBucket = maskIterator.bucket
            if maskIterator.roiCenter is not None:
                self._ignoreClicked = True
                self.aWindow.moveLinkedCursor(maskIterator.roiCenter)
                self._ignoreClicked = False
            if len(maskIterator.means) > 1:
                indices = numpy.arange(len(maskIterator.means))
                self.matplotAxes.plot(
                    indices, numpy.array(maskIterator.means))
                self.matplotCanvas.draw()

if __name__ == '__main__':
    qApp = QApplication(sys.argv)

    if len(sys.argv) == 3:
        roiIterator = aims.aims.getRoiIterator(sys.argv[2]).get()
        w = MeasuresWindow(sys.argv[1], roiIterator=roiIterator)
    else:
        w = MeasuresWindow(sys.argv[1])
    w.show()

    anatomist.Anatomist().getControlWindow().hide()
    qApp.exec_()
    del w
