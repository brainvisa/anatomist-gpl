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

'''
Graph building
--------------

Creating a complete graph and nomenclature in Python
'''

from __future__ import print_function

from __future__ import absolute_import
import anatomist.direct.api as ana
from soma import aims
from soma.qt_gui.qt_backend import Qt
import sys

# create graph structure
graph = aims.Graph('RoiArg')
# these are needed for internal conversions
graph['type.global.tri'] = 'roi.global.tri'
graph['roi.global.tri'] = 'roi roi_global.gii aims_mesh'

# create 2 nodes
v = graph.addVertex('roi')
mesh = aims.SurfaceGenerator.sphere([0, 0, 0], 10, 100)
aims.GraphManip.storeAims(graph, v, 'aims_mesh', mesh)
v['name'] = 'sphere1'
v = graph.addVertex('roi')
mesh = aims.SurfaceGenerator.sphere([0, 0, 100], 10, 100)
aims.GraphManip.storeAims(graph, v, 'aims_mesh', mesh)
v['name'] = 'sphere2'

# create a corresponding nomenclature
hie = aims.Hierarchy()
hie.setSyntax('hierarchy')
hie['graph_syntax'] = 'RoiArg'
n = aims.Tree(True, 'fold_name')
n['name'] = 'sphere1'
n['color'] = aims.vector_S32([255, 255, 0])
hie.insert(n)
n = aims.Tree(True, 'fold_name')
n['name'] = 'sphere2'
n['color'] = aims.vector_S32([0, 255, 0])
hie.insert(n)

runloop = Qt.QApplication.instance() is not None

# create anatomist objects
a = ana.Anatomist()
ahie = a.toAObject(hie)
ahie.releaseAppRef()
agraph = a.toAObject(graph)
agraph.releaseAppRef()

# display graph
w = a.createWindow('3D')
w.addObjects(agraph, add_children=True)
br = a.createWindow('Browser')
br.addObjects(ahie)

w.sphinx_gallery_snapshot()

if runloop and 'sphinx_gallery' not in sys.modules:
    Qt.QApplication.instance().exec_()
if runloop or 'sphinx_gallery' in sys.modules:
    del w, br, agraph, ahie, v, graph, hie, n
