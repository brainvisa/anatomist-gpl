#!/usr/bin/env python
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

from __future__ import print_function
from __future__ import absolute_import
import anatomist.direct.api as ana
from soma import aims
from soma.aims import colormaphints
import sys
import os
from optparse import OptionParser

# determine wheter we are using Qt4 or Qt5, and hack a little bit accordingly
# the boolean qt4 gloabl variable will tell it for later usage
from soma.qt_gui import qt_backend
from six.moves import zip
qt_backend.set_qt_backend(compatible_qt5=True)
from soma.qt_gui.qt_backend import QtCore, QtGui, Qt
from soma.qt_gui.qt_backend import uic
from soma.qt_gui.qt_backend.uic import loadUi
import six

parser = OptionParser(
    description='A simplified version of Anatomist for quick viewing')
parser.add_option('-i', '--input', dest='input', metavar='FILE',
                  action='append', default=[],
                  help='load given objects from files')
parser.add_option('-l', '--left', dest='left_mode', action='store_true',
                  help='Use left button for rotation in 3D view')

(options, args) = parser.parse_args()

# do we have to run QApplication ?
if Qt.qApp.startingUp():
    qapp = Qt.QApplication(args)
    runqt = True
else:
    runqt = False

# the following imports have to be made after the qApp.startingUp() test
# since they do instantiate Anatomist for registry to work.
from anatomist.simpleviewer.anasimpleviewer import AnaSimpleViewer

# splash
pix = Qt.QPixmap(os.path.expandvars(os.path.join(
                                    aims.carto.Paths.globalShared(),
                                    'anatomist-%s/icons/anatomist.png'
                                    % '.'.join(
                                        [str(x) for x in aims.version()]))))
spl = Qt.QSplashScreen(pix)
spl.show()
Qt.qApp.processEvents()


# instantiate the machine
anasimple = AnaSimpleViewer()

if options.left_mode:
    anasimple.control_3d_type = 'LeftSimple3DControl'

# display on the whole screen
anasimple.awidget.showMaximized()
# remove the splash
spl.finish(anasimple.awidget)
del spl


for i in options.input + args:
    anasimple.loadObject(i)

# run Qt
if runqt:
    qapp.exec_()

# cleanup before exiting
anasimple.closeAll()
del anasimple
