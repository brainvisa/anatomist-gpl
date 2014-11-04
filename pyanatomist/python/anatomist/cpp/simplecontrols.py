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

import anatomist.cpp as anatomist
from PyQt4 import QtCore, QtGui
import os

'''Simplified controls useful to avoid complex interactions.
When you need them in a custom application, you need to register them first in the ControlManager. They are already registered in the action/control dictionaries.
'''

class ResetFOVAction( anatomist.Action ):
  def name( self ):
    return 'ResetFOVAction'

  def resetFOV( self ):
    self.view().aWindow().focusView()


class Simple2DControl( anatomist.Control ):
  '''Simplified control for 2D views'''

  def __init__( self, prio = 25, name='Simple2DControl' ):
    anatomist.Control.__init__( self, prio, name )

  def eventAutoSubscription( self, pool ):
    key = QtCore.Qt
    NoModifier = key.NoModifier
    ShiftModifier = key.ShiftModifier
    ControlModifier = key.ControlModifier
    AltModifier = key.AltModifier
    self.mouseLongEventSubscribe( key.LeftButton, NoModifier,
      pool.action( 'LinkAction' ).execLink,
      pool.action( 'LinkAction' ).execLink,
      pool.action( 'LinkAction' ).endLink, True )
    self.mouseLongEventSubscribe( key.MidButton, ShiftModifier,
      pool.action( "Zoom3DAction" ).beginZoom,
      pool.action( "Zoom3DAction" ).moveZoom,
      pool.action( "Zoom3DAction" ).endZoom, True )
    self.wheelEventSubscribe( pool.action( "Zoom3DAction" ).zoomWheel )
    self.keyPressEventSubscribe( key.Key_C, ControlModifier,
      pool.action( "Trackball" ).setCenter )
    self.keyPressEventSubscribe( key.Key_C, AltModifier,
      pool.action( "Trackball" ).showRotationCenter )
    self.mouseLongEventSubscribe( key.MidButton, ControlModifier,
      pool.action( "Translate3DAction" ).beginTranslate,
      pool.action( "Translate3DAction" ).moveTranslate,
      pool.action( "Translate3DAction" ).endTranslate, True )
    self.keyPressEventSubscribe( key.Key_PageUp, NoModifier,
      pool.action( "SliceAction" ).previousSlice )
    self.keyPressEventSubscribe( key.Key_PageDown, NoModifier,
      pool.action( "SliceAction" ).nextSlice )
    self.keyPressEventSubscribe( key.Key_PageUp, ShiftModifier,
      pool.action( "SliceAction" ).previousTime )
    self.keyPressEventSubscribe( key.Key_PageDown, ShiftModifier,
      pool.action( "SliceAction" ).nextTime )
    self.keyPressEventSubscribe( key.Key_L, ControlModifier,
      pool.action( "SliceAction" ).toggleLinkedOnSlider )
    self.keyPressEventSubscribe( key.Key_Space, NoModifier,
      pool.action( "MovieAction" ).startOrStop )
    self.keyPressEventSubscribe( key.Key_S, ControlModifier,
      pool.action( "MovieAction" ).sliceOn )
    self.keyPressEventSubscribe( key.Key_T, ControlModifier,
      pool.action( "MovieAction" ).timeOn )
    self.keyPressEventSubscribe( key.Key_M, ControlModifier,
      pool.action( "MovieAction" ).nextMode )
    self.keyPressEventSubscribe( key.Key_Plus, NoModifier,
      pool.action( "MovieAction" ).increaseSpeed )
    self.keyPressEventSubscribe( key.Key_Plus, ShiftModifier,
      pool.action( "MovieAction" ).increaseSpeed )
    self.keyPressEventSubscribe( key.Key_Minus, NoModifier,
      pool.action( "MovieAction" ).decreaseSpeed )
    self.myActions = { "MovieAction" : pool.action( "MovieAction" ),
      "ContinuousTrackball" : pool.action( "ContinuousTrackball" ) }
    self.mouseLongEventSubscribe( key.RightButton, NoModifier,
      pool.action( 'PaletteContrastAction' ).startContrast,
      pool.action( 'PaletteContrastAction' ).moveContrast,
      pool.action( 'PaletteContrastAction' ).stopContrast, True )
    self.keyPressEventSubscribe( key.Key_C, NoModifier,
      pool.action( "PaletteContrastAction" ).resetPalette )
    self.keyPressEventSubscribe( key.Key_Home, NoModifier,
      pool.action( "ResetFOVAction" ).resetFOV )

  def doAlsoOnDeselect( self, pool ):
    a = anatomist.Anatomist('-b')
    for k,ac in self.myActions.iteritems():
      if isinstance( a, anatomist.MovieAction ) and a.isRunning():
        a.startOrStop()
      if isinstance( a, anatomist.ContinuousTrackball ):
        a.stop()

class Simple3DControl( Simple2DControl ):
  '''Simplified control for 3D views: still allow rotation using mouse mid button
  '''

  def __init__( self, prio = 26, name='Simple3DControl' ):
    Simple2DControl.__init__( self, prio, name )

  def eventAutoSubscription( self, pool ):
    key = QtCore.Qt
    NoModifier = key.NoModifier
    ShiftModifier = key.ShiftModifier
    ControlModifier = key.ControlModifier
    Simple2DControl.eventAutoSubscription( self, pool )
    self.mouseLongEventSubscribe ( \
      key.MidButton, NoModifier,
      pool.action( 'ContinuousTrackball' ).beginTrackball,
      pool.action( 'ContinuousTrackball' ).moveTrackball,
      pool.action( 'ContinuousTrackball' ).endTrackball, True )
    self.keyPressEventSubscribe( key.Key_Space, ControlModifier,
      pool.action( "ContinuousTrackball" ).startOrStop )

# register actions and controls
a = anatomist.Anatomist( '-b' )
iconpath = os.path.join( str( a.anatomistSharedPath() ), 'icons' )
pix = QtGui.QPixmap( os.path.join( iconpath, 'simple2Dcontrol.png' ) )
anatomist.IconDictionary.instance().addIcon( 'Simple2DControl', pix )
pix = QtGui.QPixmap( os.path.join( iconpath, 'simple3Dcontrol.png' ) )
anatomist.IconDictionary.instance().addIcon( 'Simple3DControl', pix )

del pix, iconpath, a, os, QtGui

ad = anatomist.ActionDictionary.instance()
ad.addAction( 'ResetFOVAction', ResetFOVAction )
cd = anatomist.ControlDictionary.instance()
cd.addControl( 'Simple2DControl', Simple2DControl, 25 )
cd.addControl( 'Simple3DControl', Simple3DControl, 26 )
#cm = anatomist.ControlManager.instance()
#cm.addControl( 'QAGLWidget3D', '', 'Simple2DControl' )
#cm.addControl( 'QAGLWidget3D', '', 'Simple3DControl' )

del cd, ad

