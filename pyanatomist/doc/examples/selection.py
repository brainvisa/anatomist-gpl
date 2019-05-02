# -*- coding: utf-8 -*-

'''
Selection handling
------------------

Getting selected objects
'''

from __future__ import print_function

import anatomist.direct.api as ana
from soma import aims
from soma.aims import colormaphints
import sys
import os

# determine wheter we are using Qt4 or Qt5, and hack a little bit accordingly
from soma.qt_gui import qt_backend
from soma.qt_gui.qt_backend import QtCore, QtGui

# do we have to run QApplication ?
if not QtGui.QApplication.instance() and 'sphinx_gallery' not in sys.modules:
    runqt = True
else:
    runqt = False

# start the Anatomist engine, in batch mode (no main window)
a = ana.Anatomist('-b')

# create a sphere mesh
m = aims.SurfaceGenerator.sphere(aims.Point3df(0), 100, 100)
mesh = a.toAObject(m)

# Create a new 3D window in Anatomist
aw = a.createWindow('3D')

# Put the mesh in the created window
a.addObjects(mesh, aw)

g = a.getDefaultWindowsGroup()
print('mesh isSelected:', g.isSelected(mesh))
print('selecting it')
g.setSelection(mesh)
print("selection in default group", a.getSelection())
print("selection of", g, g.getSelection())
sel = g.getSelection()
# print(mesh, sel, mesh == sel[0], mesh is sel[0])
# print('mesh isSelected:', g.isSelected( mesh ))

# run Qt
if runqt:
    qapp.exec_()
elif 'sphinx_gallery' in sys.modules:
    aw.sphinx_gallery_snapshot()
del aw, mesh, m, g, sel

