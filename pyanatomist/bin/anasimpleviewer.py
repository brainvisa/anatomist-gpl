#!/usr/bin/env python
# -*- coding: utf-8 -*-

import anatomist.direct.api as ana
from soma import aims
from soma.aims import colormaphints
import sys, os


qt4 = False
if sys.modules.has_key( 'PyQt4'):
  print 'PyQt4 loaded'
  qt4 = True
  from PyQt4 import QtCore, QtGui
  qt = QtGui
  from PyQt4.uic import loadUi
  uifile = 'anasimpleviewer-qt4.ui'
  findChild = lambda x, y: QtCore.QObject.findChild( x, QtCore.QObject, y )
  print 'findChild 1:', findChild
else:
  print 'PyQt4 Not loaded'
  import qt, qtui
  loadUi = qtui.QWidgetFactory.create
  uifile = 'anasimpleviewer.ui'
  findChild = qt.QObject.child
  print 'findChild 2:', findChild

print 'findChild:', findChild

if qt.qApp.startingUp():
  qapp = qt.QApplication( sys.argv )
  runqt = True
else:
  runqt = False

# splash
pix = qt.QPixmap( os.path.expandvars( '$BRAINVISA_SHARE/anatomist-3.2/icons/anatomist.png' ) )
spl = qt.QSplashScreen( pix )
spl.show()
qt.qApp.processEvents()

a = ana.Anatomist( '-b' )


anasimpleviewerdir = os.path.join( \
  unicode( a.anatomistSharedPath() ),
  'anasimpleviewer' )
awin = loadUi( os.path.join( anasimpleviewerdir, uifile ) )

fdialog = qt.QFileDialog()
awindows = []
aobjects = []
fusion2d = []

vieww = findChild( awin, 'windows' )
if qt4:
  viewgridlay = qt.QGridLayout( vieww )
else:
  viewgridlay = qt.QGridLayout( vieww, 2, 2 )
#vl = qt.QHBoxLayout( vieww )
#vl.addWidget( viewgrid )
#viewgrid.show()

class AnaSimpleViewer( qt.QObject ):

  def createWindow( self, wintype = 'Axial' ):
    c = ana.cpp.CreateWindowCommand( wintype, -1, None, [], 1, vieww, 2,
      { '__syntax__' : 'dictionary', 'no_decoration' : 1 } )
    a.execute( c )
    w = a.AWindow( a, c.createdWindow() )
    x = 0
    y = 0
    if not hasattr( self, '_winlayouts' ):
      self._winlayouts = [ [ 0, 0 ], [ 0, 0 ] ]
    else:
      freeslot = False
      for y in ( 0, 1 ):
        for x in ( 0, 1 ):
          if not self._winlayouts[x][y]:
            freeslot = True
            break
        if freeslot:
          break
    print 'add', wintype, 'at', x, y
    viewgridlay.addWidget( w.getInternalRep(), x, y )
    self._winlayouts[x][y] = 1
    w.releaseAppRef()
    awindows.append( w )

  def loadObject( self, fname ):
    obj = a.loadObject( fname )
    findChild( awin, 'objectslist' ).insertItem( obj.name )
    aobjects.append( obj )
    if obj.objectType == 'VOLUME':
      hints = colormaphints.checkVolume( \
        ana.cpp.AObjectConverter.aims( obj ) )
      obj.attributed()[ 'colormaphints' ] = hints
    bb = obj.boundingbox()
    if len( awindows ) == 0:
      self.createWindow( 'Axial' )
      self.createWindow( 'Coronal' )
      self.createWindow( 'Sagittal' )
      self.createWindow( '3D' )
      a.execute( 'Camera', windows=[ awindows[-1] ],
        view_quaternion=[ 0.404603, 0.143829, 0.316813, 0.845718 ] )
    self.addObject( obj )
    position = ( bb[1] - bb[0] ) / 2.
    t = a.getTransformation( obj.getReferential(),
      awindows[0].getReferential() )
    if t:
      position = t.transform( position )
    a.execute( 'LinkedCursor', window=awindows[0], position=position )

  def addObject( self, obj ):
    if obj.objectType == 'VOLUME':
      global fusion2d
      if len( fusion2d ) == 0:
        fusion2d = [ None, obj ]
      elif obj not in fusion2d:
        fusobjs = fusion2d[1:] + [ obj ]
        f2d = a.fusionObjects( fusobjs, method='Fusion2DMethod' )
        if fusion2d[0] is not None:
          a.deleteObjects( fusion2d[0] )
        else:
          a.removeObjects( fusion2d[1], awindows )
        fusion2d = [ f2d ] + fusobjs
        # repalette( fusobjs )
        obj = f2d
      else:
        return
      if obj.objectType == 'VOLUME':
        cmap = colormaphints.chooseColormaps( \
          ( obj.attributed()[ 'colormaphints' ], ) )
        obj.setPalette( cmap[0] )
      else:
        hints = [ x.attributed()[ 'colormaphints' ] for x in obj.children ]
        cmaps = colormaphints.chooseColormaps( hints )
        for x, y in zip( obj.children, cmaps ):
          x.setPalette( y )
    a.addObjects( obj, awindows )

  def removeObject( self, obj ):
    if obj.objectType == 'VOLUME':
      global fusion2d
      if obj in fusion2d:
        fusobjs = [ o for o in fusion2d[1:] if o != obj ]
        if len( fusobjs ) >= 2:
          f2d = a.fusionObjects( fusobjs, method='Fusion2DMethod' )
        else:
          f2d = None
        if fusion2d[0] is not None:
          a.deleteObjects( fusion2d[0] )
        else:
          a.removeObjects( fusion2d[1], awindows )
        if len( fusobjs ) == 0:
          fusion2d = []
        else:
          fusion2d = [ f2d ] + fusobjs
        # repalette( fusobjs )
        if f2d:
          a.addObjects( f2d, awindows )
        elif len( fusobjs ) == 1:
          a.addObjects( fusobjs[0], awindows )
      else:
        return
    a.removeObjects( obj, awindows )


  def fileOpen( self ):
    fdialog.setMode( fdialog.ExistingFiles )
    fdialog.show()
    if fdialog.exec_loop():
      fnames = fdialog.selectedFiles()
      for fname in fnames:
        self.loadObject( fname.utf8().data() )

  def selectedObjects( self ):
    olist = findChild( awin, 'objectslist' )
    sobjs = []
    for i in xrange( olist.count() ):
      if olist.isSelected( i ):
        sobjs.append( olist.text( i ).utf8().data().strip('\0') )
    return [ o for o in aobjects if o.name in sobjs ]

  def editAdd( self ):
    objs = self.selectedObjects()
    for o in objs:
      self.addObject( o )

  def editRemove( self ):
    objs = self.selectedObjects()
    for o in objs:
      self.removeObject( o )

  def editDelete( self ):
    objs = self.selectedObjects()
    for o in objs:
      self.removeObject( o )
    olist = findChild( awin, 'objectslist' )
    for o in objs:
      olist.removeItem( olist.index( olist.findItem( o.name ) ) )
    global aobjects
    aobjects = [ o for o in aobjects if o not in objs ]
    a.deleteObjects( objs )

anasimple = AnaSimpleViewer()
print 'fileOpenAction:', findChild( awin, 'fileOpenAction' )
print awin.fileOpenAction
awin.connect( findChild( awin, 'fileOpenAction' ), qt.SIGNAL( 'activated()' ),
  anasimple.fileOpen )
awin.connect( findChild( awin, 'fileExitAction' ), qt.SIGNAL( 'activated()' ),
  awin.close )
awin.connect( findChild( awin, 'editAddAction' ), qt.SIGNAL( 'activated()' ),
  anasimple.editAdd )
awin.connect( findChild( awin, 'editRemoveAction' ), qt.SIGNAL( 'activated()' ),
  anasimple.editRemove )
awin.connect( findChild( awin, 'editDeleteAction' ),
  qt.SIGNAL( 'activated()' ), anasimple.editDelete )

qt.qApp.setMainWidget( awin )

awin.showMaximized()
spl.finish( awin )

a.config()[ 'setAutomaticReferential' ] = 1

if runqt:
  qapp.exec_loop()
