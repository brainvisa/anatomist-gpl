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
from soma import aims
import time
import os
import anatomist.direct.api as anatomist
import sys
from soma.qt_gui.qt_backend.QtGui import qApp

# create a unit sphere of radius 1 and 500 vertices
m = aims.SurfaceGenerator.sphere(aims.Point3df(0, 0, 0), 1, 500, False)

# Multiply the sphere size by 100
for p in xrange(m.vertex().size()):
    m.vertex()[p] *= 100

# Open Anatomist
a = anatomist.Anatomist()

# Put the mesh in anatomist
am = a.toAObject(m)

# Create a new 3D window in Anatomist
aw = a.createWindow('3D')
# c = anatomist.CreateWindowCommand( '3D' )
# proc.execute( c )
# aw = c.createdWindow()

# Put the mesh in the created window
a.addObjects(am, aw)
# c = anatomist.AddObjectCommand( [ am ], [ aw ] )
# proc.execuFalsete( c )

# keep a copy of original vertices
coords = [aims.Point3df(m.vertex()[i])
          for i in xrange(len(m.vertex()))]
# take one vertex out of 3
points = xrange(0, len(coords), 3)

for i in xrange(10):
    # shrink
    for s in reversed(xrange(100)):
        for p in points:
            m.vertex()[p] = coords[p] * s / 100.
        am.setChanged()
        am.notifyObservers()
        qApp.processEvents()
        time.sleep(0.01)
    # expand
    for s in xrange(100):
        for p in points:
            m.vertex()[p] = coords[p] * s / 100.
        am.setChanged()
        am.notifyObservers()
        qApp.processEvents()
        time.sleep(0.01)
