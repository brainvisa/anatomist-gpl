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
      elif isinstance( o, anatomist.MObject ):
        objs += [ mo for mo in o if mo not in objs ]

  def moveContrastMin( self, x, y, globx, globy ):
    win = self.view().window()
    objs = list( win.Objects() )
    diff = ( ( x - self._start[0] ) / 500., ( y - self._start[1] ) / 500. )
    a = anatomist.Anatomist()
    for o in objs:
      pal = o.palette()
      if pal:
        if self._palettes.has_key( o ):
          initpal = self._palettes[ o ]
        else:
          initpal = [ pal.min1(), pal.max1() ]
          self._palettes[ o ] = initpal
        a.theProcessor().execute( 'SetObjectPalette', objects=[o],
          min=initpal[0] + diff[1] )
      elif isinstance( o, anatomist.MObject ):
        objs += [ mo for mo in o if mo not in objs ]

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
      elif isinstance( o, anatomist.MObject ):
        objs += [ mo for mo in o if mo not in objs ]


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
