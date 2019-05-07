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

'''
Ellipsoid example
-----------------

Updating the size and shape of an object interactively
'''

from soma import aims
import anatomist.direct.api as anatomist
import time
import numpy
import sys


a = anatomist.Anatomist()


def rotation_3d(a1, a2, a3):
    '''
    Return matrix 4x4 of rotation along 3 canonic axis based on 3 angles.

    - a1, a2, a3 : rotation angles.
    '''
    c1, s1 = numpy.cos(a1), numpy.sin(a1)
    c2, s2 = numpy.cos(a2), numpy.sin(a2)
    c3, s3 = numpy.cos(a3), numpy.sin(a3)
    m1 = numpy.matrix([
        [c1, -s1, 0, 0],
        [s1, c1,  0, 0],
        [0,   0,  1, 0],
        [0,   0,  0, 1]])
    m2 = numpy.matrix([
        [1,  0,   0, 0],
        [0, c2, -s2, 0],
        [0, s2,  c2, 0],
        [0,  0,   0, 1]])
    m3 = numpy.matrix([
        [c3, 0, -s3, 0],
        [0,  1,   0, 0],
        [s3, 0,  c3, 0],
        [0,  0,   0, 1]])
    return m1 * m2 * m3


def apply_transform(mesh, scaling, rot, translate):
    '''
    Transform mesh with scaling, translation and rotation matrix.
    '''
    mesh2 = aims.AimsTimeSurface_3(mesh)
    # create transformation
    scale = numpy.asmatrix(numpy.diag(scaling))
    rot[:, 3] = numpy.asmatrix(translate).T
    cov = rot * scale * rot.I
    # apply transformation
    motion = aims.Motion(numpy.asarray(cov).flatten())
    aims.SurfaceManip.meshTransform(mesh2, motion)
    # update mesh in anatomist object
    asphere.setSurface(mesh2)


def transform(mesh, angles, scaling, translate):
    '''
    Create and apply transformation to mesh.
    '''
    angles[0] += 0.02
    angles[1] += 0.03
    angles[2] += 0.05
    a1, a2, a3 = angles
    scaling = numpy.array([1.1 + numpy.cos(a1 * 3), 1.1 + numpy.cos(a2 * 2),
                           1.1 + numpy.cos(a3), 0]) * 0.5
    scaling[3] = 1.
    rot = rotation_3d(a1, a2, a3)
    apply_transform(mesh, scaling, rot, translate)

mesh = aims.SurfaceGenerator.sphere(aims.Point3df(0, 0, 0), 1, 500)
asphere = a.toAObject(mesh)
asphere.releaseAppRef()
aw = a.createWindow('3D')
aw.setHasCursor(0)
a.addObjects([asphere], [aw])


if __name__ == '__main__':
    from soma.qt_gui import qt_backend
    from soma.qt_gui.qt_backend import QtGui
    angles = numpy.array([0., 0., 0.])
    scaling = numpy.array([1., 1., 1., 0.])
    translate = numpy.array([0, 0, 0, 1])
    if 'sphinx_gallery' in sys.modules:
        for i in range(90):
            transform(mesh, angles, scaling, translate)
        asphere.setChanged()
        asphere.notifyObservers()
        QtGui.qApp.processEvents()
        # display in matplotlib for sphinx_gallery
        import matplotlib
        matplotlib.use('agg', force=True)  # force agg
        aw.imshow(show=True)

    else:
        while a.getControlWindow().isVisible():
            transform(mesh, angles, scaling, translate)
            asphere.setChanged()
            asphere.notifyObservers()
            QtGui.qApp.processEvents()
            time.sleep(0.01)

    del aw, asphere, mesh
