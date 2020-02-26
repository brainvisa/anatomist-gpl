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
Using OpenGL in PyAnatomist
---------------------------

Customizing OpenGL parameters for objects
'''

from __future__ import absolute_import
from soma import aims
import anatomist.direct.api as anatomist
from soma.qt_gui.qt_backend import Qt
from OpenGL import GL
import six


class VolRender(anatomist.cpp.ObjectVector, anatomist.cpp.GLComponent):

    def __init__(self, objects):
        self._objects = objects
        for o in objects:
            self.insert(o)

    def renderingIsObserverDependent(self):
        return True


class WinViewMesh (anatomist.cpp.ASurface_3):

    def __init__(self, mesh, followorientation=True, followposition=False):
        if mesh is not None:
            if type(mesh) is six.string_types:
                # mesh is a filename: read it
                anatomist.cpp.ASurface_3.__init__(self, mesh)
                r = aims.Reader()
                m = aims.rc_ptr_AimsTimeSurface_3(r.read(mesh))
                self.setSurface(m)
            else:
                # mesh should be an Aims mesh: assign it
                anatomist.cpp.ASurface_3.__init__(self)
                self.setSurface(mesh)
        else:
            # generate a sphere mesh
            anatomist.cpp.ASurface_3.__init__(self)
            m = aims.rc_ptr_AimsTimeSurface_3(aims.SurfaceGenerator.sphere(
                                              aims.Point3df(0, 0, 0), 10, 100))
            self.setSurface(m)
        self._followorientation = followorientation
        self._followposition = followposition

    def renderingIsObserverDependent(self):
        return True

    def glMainGLL(self, state):
        self.glSetChanged(anatomist.cpp.GLComponent.glGENERAL)
        return anatomist.cpp.GLComponent.glMainGLL(self, state)

    def glBeforeBodyGLL(self, state, prim):
        if self._followorientation and self._followposition:
            return
        gll = anatomist.cpp.GLList()
        gll.generate()
        prim.append(gll)
        GL.glNewList(gll.item(), GL.GL_COMPILE)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        if not self._followposition:
            winDim = 70
            GL.glPushAttrib(GL.GL_VIEWPORT_BIT)
            GL.glViewport(0, 0, winDim, winDim)
            GL.glLoadIdentity()
            orthoMinX = - 1.5
            orthoMinY = - 1.5
            orthoMinZ = - 1.5
            orthoMaxX = 1.5
            orthoMaxY = 1.5
            orthoMaxZ = 1.5
            GL.glOrtho(orthoMinX, orthoMaxX, orthoMinY, orthoMaxY,
                       orthoMinZ, orthoMaxZ)

        win = state.window
        if win \
                and isinstance(win, anatomist.cpp.ControlledWindow):
            view = win.view()

        if not self._followorientation:
            GL.glTranslate(1, 1, 0)
            # mat = GL.glGetFloatv( GL.GL_MODELVIEW_MATRIX )
            # scale = aims.Point3df( mat[0][0], mat[1][0], mat[2][0] ).norm()
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            # keep the translation part of the view orientation
            # (mut apply the inverse rotation to it)
            trans = view.rotationCenter()
            r = aims.AffineTransformation3d(view.quaternion()).inverse()
            r = r * aims.AffineTransformation3d([1, 0, 0, trans[0],
                                                 0, 1, 0, trans[1],  0, 0, 1, -trans[2],  0, 0, 0, 1])
            GL.glTranslate(-r.translation()[0], -r.translation()[1],
                           -r.translation()[2])
            GL.glScalef(1., 1., -1.)
            GL.glMatrixMode(GL.GL_PROJECTION)
        else:
            GL.glMatrixMode(GL.GL_MODELVIEW)
            # keep the rotation part of the view orientation, removing the
            # translation part
            trans = view.rotationCenter()
            r = aims.AffineTransformation3d(view.quaternion()).inverse()
            r = aims.AffineTransformation3d([1, 0, 0, trans[0],
                                             0, 1, 0, trans[1],  0, 0, 1, trans[2],  0, 0, 0, 1])
            GL.glTranslate(r.translation()[0], r.translation()[1],
                           r.translation()[2])
            GL.glMatrixMode(GL.GL_PROJECTION)

        GL.glEndList()

    def glAfterBodyGLL(self, state, prim):
        if self._followorientation and self._followposition:
            return
        gll = anatomist.cpp.GLList()
        gll.generate()
        prim.append(gll)
        GL.glNewList(gll.item(), GL.GL_COMPILE)
        GL.glMatrixMode(GL.GL_PROJECTION)
        if not self._followposition:
            GL.glPopAttrib(GL.GL_VIEWPORT_BIT)
        GL.glPopMatrix()
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPopMatrix()
        GL.glEndList()

# ---
if __name__ == '__main__':
    runloop = False
    if Qt.QApplication.instance() is None:
        runloop = True
    a = anatomist.Anatomist()
    mesh = aims.SurfaceGenerator.sphere((0, 0, 0), 1., 200)
    amesh = anatomist.cpp.AObjectConverter.anatomist(mesh)
    cube1 = aims.SurfaceGenerator.cube((0, 0, 0), 0.5, False)
    vcube1 = WinViewMesh(cube1)
    a.registerObject(vcube1)
    cube2 = aims.SurfaceGenerator.cone((0, -0.5, 0), (0, 0.5, 0), 0.5, 50,
                                       True, False)
    vcube2 = WinViewMesh(cube2, followorientation=False,
                         followposition=True)
    a.registerObject(vcube2)
    w = a.createWindow('3D')
    a.addObjects([amesh, vcube1, vcube2], [w])

    import sys
    if 'sphinx_gallery' in sys.modules:
        # display in matplotlib for sphinx_gallery
        import matplotlib
        w.camera(view_quaternion=[0.535079479217529,
                                  0.797160744667053,
                                  0.268512755632401,
                                  0.0782672688364983],
                 zoom=0.45)
        matplotlib.use('agg', force=True)  # force agg
        w.imshow(show=True)
        runloop = False

    if runloop:
        Qt.QApplication.instance().exec_()
    if runloop or 'sphinx_gallery' in sys.modules:
        del w, amesh, vcube1, vcube2, cube1, cube2, mesh