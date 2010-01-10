# -*- coding: utf-8 -*-

import anatomist.cpp as anatomist
#from soma import aims
import sys

qt4 = False
if sys.modules.has_key( 'PyQt4'):
  qt4 = True
  from PyQt4 import QtCore, QtGui
  qt = QtGui
else:
  import qt, qtui

testControl = False

class PaletteContrastAction( anatomist.Action ):
  def name( self ):
    return 'PaletteContrastAction'

  def startContrast( self, x, y, globx, globy ):
    self._start = ( x, y )
    self._palettes = {}

  def moveContrast( self, x, y, globx, globy ):
    win = self.view().window()
    objs = list( win.Objects() )
    diff = ( ( x - self._start[0] ) / 500., ( y - self._start[1] ) / 500. )
    a = anatomist.Anatomist()
    for o in objs:
      if isinstance( o, anatomist.MObject ):
        objs += [ mo for mo in o if mo not in objs ]
      else:
        pal = o.palette()
        if pal:
          if self._palettes.has_key( o ):
            initpal = self._palettes[ o ]
          else:
            initpal = [ pal.min1(), pal.max1() ]
            self._palettes[ o ] = initpal
          val = initpal[1] + diff[1]
          threshold = 0.5
          if val < initpal[0] and initpal[1] > initpal[0]:
            if diff[1] < -threshold:
              val = initpal[0] + diff[1] + threshold
            else:
              val = initpal[0]
          a.theProcessor().execute( 'SetObjectPalette', objects=[o], max=val )

  def moveContrastMin( self, x, y, globx, globy ):
    win = self.view().window()
    objs = list( win.Objects() )
    diff = ( ( x - self._start[0] ) / 500., ( y - self._start[1] ) / 500. )
    a = anatomist.Anatomist()
    for o in objs:
      if isinstance( o, anatomist.MObject ):
        objs += [ mo for mo in o if mo not in objs ]
      else:
        pal = o.palette()
        if pal:
          if self._palettes.has_key( o ):
            initpal = self._palettes[ o ]
          else:
            initpal = [ pal.min1(), pal.max1() ]
            self._palettes[ o ] = initpal
          a.theProcessor().execute( 'SetObjectPalette', objects=[o],
            min=initpal[0] + diff[1] )

  def stopContrast( self, x, y, globx, globy ):
    del self._start
    del self._palettes

  def resetPalette( self ):
    win = self.view().window()
    objs = win.Objects()
    a = anatomist.Anatomist()
    for o in objs:
      pal = o.palette()
      if pal:
        o.adjustPalette()
        a.theProcessor().execute( 'SetObjectPalette', objects=[o],
          min=pal.min1(), max=pal.max1() )


ad = anatomist.ActionDictionary.instance()
ad.addAction( 'PaletteContrastAction', PaletteContrastAction )


if testControl:
  class PaletteContrastControl( anatomist.Control ):
    def __init__( self, prio = 30 ):
      anatomist.Control.__init__( self, prio, 'PaletteContrastControl' )

    def eventAutoSubscription( self, pool ):
      if qt4:
        key = QtCore.Qt
        NoModifier = key.NoModifier
        ShiftModifier = key.ShiftModifier
        ControlModifier = key.ControlModifier
        AltModifier = key.AltModifier
      else:
        key = qt.Qt
        NoModifier = key.NoButton
        ShiftModifier = key.ShiftButton
        ControlModifier = key.ControlButton
        AltModifier = key.AltButton
      self.mouseLongEventSubscribe( key.LeftButton, NoModifier,
        pool.action( 'PaletteContrastAction' ).startContrast,
        pool.action( 'PaletteContrastAction' ).moveContrast,
        pool.action( 'PaletteContrastAction' ).stopContrast, True )
      self.mouseLongEventSubscribe( key.LeftButton, ControlModifier,
        pool.action( 'PaletteContrastAction' ).startContrast,
        pool.action( 'PaletteContrastAction' ).moveContrastMin,
        pool.action( 'PaletteContrastAction' ).stopContrast, True )
      self.keyPressEventSubscribe( key.Key_C, NoModifier,
        pool.action( "PaletteContrastAction" ).resetPalette )

  cd = anatomist.ControlDictionary.instance()
  cd.addControl( 'PaletteContrastControl', PaletteContrastControl, 30 )
  cm = anatomist.ControlManager.instance()
  cm.addControl( 'QAGLWidget3D', '', 'PaletteContrastControl' )

