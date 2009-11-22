#!/usr/bin/env python
# -*- coding: utf-8 -*-

import anatomist.direct.api as ana
from soma import aims
from soma.aims import colormaphints
import qt, qtui
import sys, os


if qt.qApp.startingUp():
  qapp = qt.QApplication( sys.argv )
  runqt = True
else:
  runqt = False

# splash
pix = qt.QPixmap( os.path.expandvars( '$BRAINVISA_SHARE/anatomist-3.2/icons/anatomist.png' ) )
spl = qt.QSplashScreen( pix )
spl.show()

anacustomdir = '.'
if not os.path.basename( sys.argv[0] ).lower().startswith( 'python' ) \
  and not os.path.basename( sys.argv[0] ).lower().startswith( 'ipython' ):
  anacustomdir = os.path.dirname( os.path.realpath( sys.argv[0] ) )
awin = qtui.QWidgetFactory.create( os.path.join(anacustomdir,
  'anacustom.ui' ) )

fdialog = qt.QFileDialog()
awindows = []
aobjects = []
fusion2d = []

vieww = awin.child( 'windows' )
viewgrid = qt.QGrid( 2, qt.QGrid.Horizontal, vieww )
vl = qt.QHBoxLayout( vieww )
vl.addWidget( viewgrid )
viewgrid.show()

def createWindow( wintype = 'Axial' ):
  c = ana.cpp.CreateWindowCommand( wintype, -1, None, [], 1, viewgrid, 2,
    { '__syntax__' : 'dictionary', 'no_decoration' : 1 } )
  a.execute( c )
  w = a.AWindow( a, c.createdWindow() )
  w.releaseAppRef()
  awindows.append( w )

def loadObject( fname ):
  obj = a.loadObject( fname )
  awin.child( 'objectslist' ).insertItem( obj.name )
  aobjects.append( obj )
  if obj.objectType == 'VOLUME':
    hints = colormaphints.checkVolume( \
      ana.cpp.AObjectConverter.aims( obj ) )
    obj.attributed()[ 'colormaphints' ] = hints
  bb = obj.boundingbox()
  if len( awindows ) == 0:
    createWindow( 'Coronal' )
    createWindow( 'Sagittal' )
    createWindow( 'Axial' )
    createWindow( '3D' )
    a.execute( 'Camera', windows=[ awindows[-1] ],
      view_quaternion=[ 0.404603, 0.143829, 0.316813, 0.845718 ] )
  addObject( obj )
  a.execute( 'LinkedCursor', window=awindows[0], position=(bb[1]-bb[0])/2 )

def addObject( obj ):
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

def removeObject( obj ):
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


def fileOpen():
  fdialog.setMode( fdialog.ExistingFiles )
  fdialog.show()
  if fdialog.exec_loop():
    fnames = fdialog.selectedFiles()
    for fname in fnames:
      loadObject( fname.utf8().data() )

def selectedObjects():
  olist = awin.child( 'objectslist' )
  sobjs = []
  for i in xrange( olist.count() ):
    if olist.isSelected( i ):
      sobjs.append( olist.text( i ).utf8().data().strip('\0') )
  return [ o for o in aobjects if o.name in sobjs ]

def editAdd():
  objs = selectedObjects()
  for o in objs:
    addObject( o )

def editRemove():
  objs = selectedObjects()
  for o in objs:
    removeObject( o )

def editDelete():
  objs = selectedObjects()
  for o in objs:
    removeObject( o )
  olist = awin.child( 'objectslist' )
  for o in objs:
    olist.removeItem( olist.index( olist.findItem( o.name ) ) )
  global aobjects
  aobjects = [ o for o in aobjects if o not in objs ]
  a.deleteObjects( objs )

awin.connect( awin.child( 'fileOpenAction' ), qt.SIGNAL( 'activated()' ),
  fileOpen )
awin.connect( awin.child( 'fileExitAction' ), qt.SIGNAL( 'activated()' ),
  awin.close )
awin.connect( awin.child( 'editAddAction' ), qt.SIGNAL( 'activated()' ),
  editAdd )
awin.connect( awin.child( 'editRemoveAction' ), qt.SIGNAL( 'activated()' ),
  editRemove )
awin.connect( awin.child( 'editDeleteAction' ), qt.SIGNAL( 'activated()' ),
  editDelete )

qt.qApp.setMainWidget( awin )

a = ana.Anatomist( '-b' )

awin.showMaximized()
spl.finish( awin )

if runqt:
  qapp.exec_loop()
