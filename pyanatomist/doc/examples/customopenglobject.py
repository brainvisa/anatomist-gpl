
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
import anatomist.direct.api as anatomist
from OpenGL import GL
import types

class WinViewMesh ( anatomist.cpp.ASurface_3 ):
  def __init__( self, mesh, followorientation=True, followposition=False ):
    if mesh is not None:
      if type( mesh ) is types.StringType:
        # mesh is a filename: read it
        anatomist.cpp.ASurface_3.__init__( self, mesh )
        r = aims.Reader()
        m = aims.rc_ptr_AimsTimeSurface_3( r.read( mesh ) )
        self.setSurface( m )
      else:
        # mesh should be an Aims mesh: assign it
        anatomist.cpp.ASurface_3.__init__( self )
        self.setSurface( mesh )
    else:
      # generate a sphere mesh
      anatomist.cpp.ASurface_3.__init__( self )
      m = aims.rc_ptr_AimsTimeSurface_3( aims.SurfaceGenerator.sphere( \
        aims.Point3df( 0, 0, 0), 10, 100 ) )
      self.setSurface( m )
    self._followorientation = followorientation
    self._followposition = followposition

  def glBeforeBodyGLL( self, state, prim ):
    if self._followorientation and self._followposition:
      return
    gll = anatomist.cpp.GLList()
    gll.generate()
    prim.append( gll )
    GL.glNewList( gll.item(), GL.GL_COMPILE )
    if not self._followposition:
      GL.glMatrixMode( GL.GL_PROJECTION )
      GL.glPushMatrix()
      winDim = 70
      GL.glPushAttrib( GL.GL_VIEWPORT_BIT )
      GL.glViewport( 0, 0, winDim, winDim );
      GL.glLoadIdentity();
      orthoMinX = - 1.5;
      orthoMinY = - 1.5;
      orthoMinZ = - 1.5;
      orthoMaxX =   1.5;
      orthoMaxY =   1.5;
      orthoMaxZ =   1.5;
      GL.glOrtho( orthoMinX, orthoMaxX, orthoMinY, orthoMaxY,
                  orthoMinZ, orthoMaxZ )
      #GL.glMatrixMode( GL.GL_MODELVIEW )
      #GL.glPushMatrix()
      #GL.glLoadIdentity()
      #GL.glScalef( 1, 1, -1 )

    if not self._followorientation:
      if self._followposition:
        GL.glMatrixMode( GL.GL_PROJECTION )
        GL.glPushMatrix()
      win = state.window
      if win \
        and isinstance( win, anatomist.cpp.ControlledWindow ):
        view = win.view()
        #orient = view. # needs GLWidget...
      #GL.glLoadIdentity()
      #GL.glScalef( 0.8, 0.8, -0.8 )
      GL.glTranslate( 1, 1, 1 )
      #mat = GL.glGetFloatv( GL.GL_PROJECTION_MATRIX )
      #print mat
      #mat[3][0] = 0
      #mat[3][1] = 0
      #mat[3][2] = 0
      #GL.glLoadMatrixf( mat )
    GL.glEndList()

  def glAfterBodyGLL( self, state, prim ):
    if self._followorientation and self._followposition:
      return
    gll = anatomist.cpp.GLList()
    gll.generate()
    prim.append( gll )
    GL.glNewList( gll.item(), GL.GL_COMPILE )
    if not self._followorientation and self._followposition:
      GL.glPopMatrix()
    if not self._followposition:
      GL.glMatrixMode( GL.GL_PROJECTION )
      GL.glPopMatrix()
      GL.glPopAttrib( GL.GL_VIEWPORT_BIT )
      #GL.glMatrixMode( GL.GL_MODELVIEW )
      #GL.glPopMatrix()
    GL.glEndList()

# ---
if __name__ == '__main__':
  a = anatomist.Anatomist()
  r = aims.Reader()
  mesh = r.read( 'test.mesh' )
  amesh = anatomist.cpp.AObjectConverter.anatomist( mesh )
  cube1 = aims.SurfaceGenerator.cube( aims.Point3df( 0, 0, 0 ), 0.5, False )
  vcube1 = WinViewMesh( cube1 )
  a.registerObject( vcube1 )
  cube2 = aims.SurfaceGenerator.cone( aims.Point3df( 0, 0, -0.5 ),
    aims.Point3df( 0, 0, 0.5 ), 0.5, 50, True, False )
  vcube2 = WinViewMesh( cube2, followorientation = False,
    followposition = True )
  a.registerObject( vcube2 )
  w = a.createWindow( '3D' )
  a.addObjects( [ amesh, vcube1, vcube2 ], [ w ] )
