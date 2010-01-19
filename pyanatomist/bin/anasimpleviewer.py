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

import anatomist.direct.api as ana
from anatomist.cpp.palettecontrastaction import PaletteContrastAction
from soma import aims
from soma.aims import colormaphints
import sys, os

# determine wheter we are using Qt4 or Qt3, and hack a little bit accordingly
# the boolean qt4 gloabl variable will tell it for later usage
qt4 = False
if sys.modules.has_key( 'PyQt4'):
  qt4 = True
  from PyQt4 import QtCore, QtGui
  qt = QtGui
  from PyQt4.uic import loadUi
  uifile = 'anasimpleviewer-qt4.ui'
  findChild = lambda x, y: QtCore.QObject.findChild( x, QtCore.QObject, y )
else:
  import qt, qtui
  loadUi = qtui.QWidgetFactory.create
  uifile = 'anasimpleviewer.ui'
  findChild = qt.QObject.child

# do we have to run QApplication ?
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

# start the Anatomist engine, in batch mode (no main window)
a = ana.Anatomist( '-b' )

# load the anasimpleviewer GUI
anasimpleviewerdir = os.path.join( \
  unicode( a.anatomistSharedPath() ),
  'anasimpleviewer' )
awin = loadUi( os.path.join( anasimpleviewerdir, uifile ) )

# global variables: lists of windows, objects, a fusion2d with a number of
# volumes in it, and a volume rendering object + clipping
fdialog = qt.QFileDialog()
awindows = []
aobjects = []
fusion2d = []
volrender = None

# vieww: parent widget for anatomist windows
vieww = findChild( awin, 'windows' )
if qt4:
  viewgridlay = qt.QGridLayout( vieww )
else:
  viewgridlay = qt.QGridLayout( vieww, 2, 2 )


# We redefine simplified controls to avoid complex interactions
class SimpleActions( ana.cpp.Action ):
  def name( self ):
    return 'SimpleActions'

  def resetFOV( self ):
    self.view().window().focusView()

class SimpleControl( ana.cpp.Control ):
  def __init__( self, prio = 25, name='SimpleControl' ):
    ana.cpp.Control.__init__( self, prio, name )

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
    self.mouseLongEventSubscribe( key.RightButton, ControlModifier,
      pool.action( 'PaletteContrastAction' ).startContrast,
      pool.action( 'PaletteContrastAction' ).moveContrastMin,
      pool.action( 'PaletteContrastAction' ).stopContrast, True )
    self.keyPressEventSubscribe( key.Key_C, NoModifier,
      pool.action( "PaletteContrastAction" ).resetPalette )
    self.keyPressEventSubscribe( key.Key_Home, NoModifier,
      pool.action( "SimpleActions" ).resetFOV )

  def doAlsoOnDeselect( self, pool ):
    for k,ac in self.myActions.iteritems():
      if isinstance( a, ana.cpp.MovieAction ) and a.isRunning():
        a.startOrStop()
      if isinstance( a, ana.cpp.ContinuousTrackball ):
        a.stop()

# in 3D views we still allow rotation using mouse mid button
class Simple3DControl( SimpleControl ):
  def __init__( self, prio = 26, name='Simple3DControl' ):
    SimpleControl.__init__( self, prio, name )

  def eventAutoSubscription( self, pool ):
    if qt4:
      key = QtCore.Qt
      NoModifier = key.NoModifier
      ShiftModifier = key.ShiftModifier
      ControlModifier = key.ControlModifier
    else:
      key = qt.Qt
      NoModifier = key.NoButton
      ShiftModifier = key.ShiftButton
      ControlModifier = key.ControlButton
    SimpleControl.eventAutoSubscription( self, pool )
    self.mouseLongEventSubscribe ( \
      key.MidButton, NoModifier,
      pool.action( 'ContinuousTrackball' ).beginTrackball,
      pool.action( 'ContinuousTrackball' ).moveTrackball,
      pool.action( 'ContinuousTrackball' ).endTrackball, True )
    self.keyPressEventSubscribe( key.Key_Space, ControlModifier,
      pool.action( "ContinuousTrackball" ).startOrStop )


# This class holds methods for menu/actions callbacks, and utility functions
# like load/view objects, remove/delete, etc.
class AnaSimpleViewer( qt.QObject ):

  def __init__( self ):
    qt.QObject.__init__( self )
    self._vrenabled = False
    # register the function on the cursor notifier of anatomist. It will be
    # called when the user clicks on a window
    a.onCursorNotifier.add( self.clickHandler )

  def clickHandler( self, eventName, params ):
    '''Callback for linked cursor. In volume rendering mode, it will sync the
    VR slice to the linked cursor.
    It also updates the volumes values view
    '''
    pos = params[ 'position' ]
    win = params[ 'window' ]
    wref = win.getReferential()
    # display coords in MNI referential (preferably)
    tr = a.getTransformation( wref, a.mniTemplateRef )
    if tr:
      pos2 = tr.transform( pos[:3] )
    else:
      pos2 = pos
    x = findChild( awin, 'coordXEdit' )
    x.setText( '%8.3f' % pos2[0] )
    y = findChild( awin, 'coordYEdit' )
    y.setText( '%8.3f' % pos2[1] )
    z = findChild( awin, 'coordZEdit' )
    z.setText( '%8.3f' % pos2[2] )
    t = findChild( awin, 'coordTEdit' )
    t.setText( '%8.3f' % pos[3] )
    # display volumes values at the given position
    valbox = findChild( awin, 'volumesBox' )
    valbox.clear()
    if qt4:
      # (we don't use the same widget type in Qt3 and Qt4)
      valbox.setColumnCount( 2 )
      valbox.setHorizontalHeaderLabels( [ 'Volume:', 'Value:' ] )
      if len( fusion2d ) > 1:
        valbox.setRowCount( len(fusion2d)-1 )
        valbox.setVerticalHeaderLabels( [ '' ] * (len(fusion2d)-1) )
    else:
      valbox.setColumnMode( 2 )
      valbox.setRowMode( qt.QListBox.Variable )
      col1 = []
    i = 0
    for obj in fusion2d[1:]:
      # retreive volume value in its own coords system
      aimsv = ana.cpp.AObjectConverter.aims( obj )
      oref = obj.getReferential()
      tr = a.getTransformation( wref, oref )
      if tr:
        pos2 = tr.transform( pos[:3] )
      else:
        pos2 = pos[:3]
      vs = obj.VoxelSize()
      pos2 = [ int(round(x/y)) for x,y in zip(pos2,vs) ]
      # pos2 in in voxels, in obj coords system
      if qt4:
        newItem = qt.QTableWidgetItem( obj.name )
        valbox.setItem( i, 0, newItem )
      else:
        valbox.insertItem( obj.name )
      # check bounds
      if pos2[0]>=0 and pos2[1]>=0 and pos2[2]>=0 and pos[3]>=0 \
        and pos2[0]<aimsv.dimX() and pos2[1]<aimsv.dimY() \
        and pos2[2]<aimsv.dimZ() and pos[3]<aimsv.dimT():
        txt = str( aimsv.value( *pos2 ) )
      else:
        txt = ''
      if qt4:
        newitem = qt.QTableWidgetItem( txt )
        valbox.setItem( i, 1, newitem )
        i += 1
      else:
        col1.append( txt )
    if qt4:
      valbox.resizeColumnsToContents()
    else:
      for x in col1:
        valbox.insertItem( x )

    # update volume rendering when it is enabled
    if self._vrenabled and len( volrender ) >= 1:
      clip = volrender[0]
      t = a.getTransformation( win.getReferential(),
        clip.getReferential() )
      if t is not None:
        pos = t.transform( pos[:3] )
      clip.setOffset( pos[:3] )
      clip.notifyObservers()

  def createWindow( self, wintype = 'Axial' ):
    '''Opens a new window in the windows grid layout.
    The new window will be set in MNI referential (except 3D for now because
    of a buf in volume rendering in direct referentials), will be assigned
    the custom control, and have no menu/toolbars.
    '''
    c = ana.cpp.CreateWindowCommand( wintype, -1, None, [], 1, vieww, 2,
      { '__syntax__' : 'dictionary', 'no_decoration' : 1 } )
    a.execute( c )
    w = a.AWindow( a, c.createdWindow() )
    # insert in grid layout
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
    if qt4:
      # in Qt4, the widget must not have a parent before calling
      # layout.addWidget
      w.setParent( None )
    viewgridlay.addWidget( w.getInternalRep(), x, y )
    self._winlayouts[x][y] = 1
    # make ref-counting work on python side
    w.releaseAppRef()
    # keep it in anasimpleviewer list of windows
    awindows.append( w )
    # set custom control
    if wintype == '3D':
      a.execute( 'SetControl', windows=[w], control='Simple3DControl' )
    else:
      a.execute( 'SetControl', windows=[w], control='SimpleControl' )
      a.assignReferential( a.mniTemplateRef, w )
      # force redrawing in MNI orientation
      # (there should be a better way to do so...)
      if wintype == 'Axial':
        w.muteAxial()
      elif wintype == 'Coronal':
        w.muteCoronal()
      elif wintype == 'Sagittal':
        w.muteSagittal()
      elif wintype == 'Oblique':
        w.muteOblique()
    # set a black background
    a.execute( 'WindowConfig', windows=[w],
      light={ 'background' : [ 0., 0., 0., 1. ] } )

  def loadObject( self, fname ):
    '''Load an object and display it in all anasimpleviewer windows
    '''
    obj = a.loadObject( fname )
    if qt4:
      findChild( awin, 'objectslist' ).addItem( obj.name )
    else:
      findChild( awin, 'objectslist' ).insertItem( obj.name )
    # keep it in the global list
    aobjects.append( obj )
    if obj.objectType == 'VOLUME':
      # volume are checked for possible adequate colormaps
      hints = colormaphints.checkVolume( \
        ana.cpp.AObjectConverter.aims( obj ) )
      obj.attributed()[ 'colormaphints' ] = hints
    bb = obj.boundingbox()
    # create the 4 windows if they don't exist
    if len( awindows ) == 0:
      self.createWindow( 'Coronal' )
      self.createWindow( 'Axial' )
      self.createWindow( 'Sagittal' )
      self.createWindow( '3D' )
      # set a cool angle of view for 3D
      a.execute( 'Camera', windows=[ awindows[-1] ],
        view_quaternion=[ 0.404603, 0.143829, 0.316813, 0.845718 ] )
    # view obj in these views
    self.addObject( obj )
    # set the cursot at the center of the object (actually, overcome a bug
    # in anatomist...)
    position = ( bb[1] - bb[0] ) / 2.
    t = a.getTransformation( obj.getReferential(),
      awindows[0].getReferential() )
    if t:
      position = t.transform( position )
    a.execute( 'LinkedCursor', window=awindows[0], position=position )

  def _displayVolume( self, obj, opts={} ):
    '''Display a volume or a Fusion2D in all windows.
    If volume rendering is allowed, 3D views will display a clipped volume
    rendering of the object.
    '''
    if self._vrenabled:
      wins = [ x for x in awindows if x.subtype() != 0 ]
      if len( wins ) != 0:
        a.addObjects( obj, wins, **opts )
      wins = [ x for x in awindows if x.subtype() == 0 ]
      if len( wins ) == 0:
        return
      vr = a.fusionObjects( [ obj ], method='VolumeRenderingFusionMethod' )
      clip = a.fusionObjects( [ vr ], method = 'FusionClipMethod' )
      global volrender
      volrender = [ clip, vr ]
      a.addObjects( clip, wins, **opts )
    else:
      a.addObjects( obj, awindows, **opts )

  def addVolume( self, obj, opts={} ):
    '''Display a volume in all windows.
    If several volumes are displayed, a Fusion2D will be built to wrap all of
    them.
    If volume rendering is allowed, 3D views will display a clipped volume
    rendering of either the single volume (if only one is present), or of the
    2D fusion.
    '''
    global fusion2d, volrender
    if obj in fusion2d:
      return
    hasvr = False
    if volrender:
      # delete the previous volume rendering
      a.deleteObjects( volrender )
      hasvr = True
      volrender = None
    if len( fusion2d ) == 0:
      # only one object
      fusion2d = [ None, obj ]
    else:
      # several objects: fusion them
      fusobjs = fusion2d[1:] + [ obj ]
      f2d = a.fusionObjects( fusobjs, method='Fusion2DMethod' )
      if fusion2d[0] is not None:
        # destroy the previous fusion
        a.deleteObjects( fusion2d[0] )
      else:
        a.removeObjects( fusion2d[1], awindows )
      fusion2d = [ f2d ] + fusobjs
      # repalette( fusobjs )
      obj = f2d
    if obj.objectType == 'VOLUME':
      # choose a good colormap for a single volume
      if obj.attributed()[ 'colormaphints' ].has_key( \
        'volume_contents_likelihoods' ):
        cmap = colormaphints.chooseColormaps( \
          ( obj.attributed()[ 'colormaphints' ], ) )
        obj.setPalette( cmap[0] )
    else:
      # choose good colormaps for the current set of volumes
      hints = [ x.attributed()[ 'colormaphints' ] for x in obj.children ]
      children = [ x for x,y in zip( obj.children, hints ) \
        if y.has_key( 'volume_contents_likelihoods' ) ]
      hints = [ x for x in hints if x.has_key( 'volume_contents_likelihoods' ) ]
      cmaps = colormaphints.chooseColormaps( hints )
      for x, y in zip( children, cmaps ):
        x.setPalette( y )
    # call a lower-level function for display and volume rendering
    self._displayVolume( obj, opts )

  def removeVolume( self, obj, opts={} ):
    '''Hides a volume from views (low-level function: use removeObject)
    '''
    global fusion2d, volrender
    if obj in fusion2d:
      hasvr = False
      if volrender:
        a.deleteObjects( volrender )
        volrender = None
        hasvr = True
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
        obj = f2d
      elif len( fusobjs ) == 1:
        obj = fusobjs[0]
      else:
        return
      self._displayVolume( obj, opts )

  def addObject( self, obj ):
    '''Display an object in all windows
    '''
    opts = {}
    if obj.objectType == 'VOLUME':
      # volumes have a specific function since several volumes have to be
      # fusionned, and a volume rendering may occur
      self.addVolume( obj, opts )
      return
    elif obj.objectType == 'GRAPH':
      opts[ 'add_graph_nodes' ] = 1
    a.addObjects( obj, awindows, **opts )

  def removeObject( self, obj ):
    '''Hides an object from views
    '''
    if obj.objectType == 'VOLUME':
      self.removeVolume( obj )
    else:
      a.removeObjects( obj, awindows, remove_children=True )

  def fileOpen( self ):
    '''File browser + load object(s)
    '''
    if qt4:
      fdialog.setFileMode( fdialog.ExistingFiles )
      fdialog.show()
      res = fdialog.exec_()
    else:
      fdialog.setMode( fdialog.ExistingFiles )
      fdialog.show()
      res = fdialog.exec_loop()
    if res:
      fnames = fdialog.selectedFiles()
      if qt4:
        for fname in fnames:
          self.loadObject( unicode( fname ) )
      else:
        for fname in fnames:
          self.loadObject( fname.utf8().data() )

  def selectedObjects( self ):
    '''list of objects selected in the list box on the upper left panel
    '''
    olist = findChild( awin, 'objectslist' )
    sobjs = []
    if qt4:
      for o in olist.selectedItems():
        sobjs.append( unicode( o.text() ).strip('\0') )
    else:
      for i in xrange( olist.count() ):
        if olist.isSelected( i ):
          sobjs.append( olist.text( i ).utf8().data().strip('\0') )
    return [ o for o in aobjects if o.name in sobjs ]

  def editAdd( self ):
    '''Display selected objects'''
    objs = self.selectedObjects()
    for o in objs:
      self.addObject( o )

  def editRemove( self ):
    '''Hide selected objects'''
    objs = self.selectedObjects()
    for o in objs:
      self.removeObject( o )

  def editDelete( self ):
    '''Delete selected objects'''
    objs = self.selectedObjects()
    for o in objs:
      self.removeObject( o )
    olist = findChild( awin, 'objectslist' )
    if qt4:
      for o in objs:
        olist.takeItem( olist.row( olist.findItems( o.name,
          QtCore.Qt.MatchExactly )[ 0 ] ) )
    else:
      for o in objs:
        olist.removeItem( olist.index( olist.findItem( o.name ) ) )
    global aobjects
    aobjects = [ o for o in aobjects if o not in objs ]
    a.deleteObjects( objs )

  def closeAll( self ):
    '''Exit'''
    print "Exiting"
    global vieww, viewgridlay, awindows, fusion2d, aobjects, anasimple
    del vieww, viewgridlay
    del anasimple
    del awindows, fusion2d, aobjects
    awin.close()
    a = ana.Anatomist()
    a.close()

  def stopVolumeRendering( self ):
    '''Disable volume rendering: show a slice instead'''
    global volrender
    if not volrender:
      return
    a.deleteObjects( volrender )
    volrender = None
    if len( fusion2d ) != 0:
      if fusion2d[0] is not None:
        obj = fusion2d[0]
      else:
        obj = fusion2d[1]
    wins = [ w for w in awindows if w.subtype() == 0 ]
    a.addObjects( obj, wins )

  def startVolumeRendering( self ):
    '''Enable volume rendering in 3D views'''
    if len( fusion2d ) == 0:
      return
    if fusion2d[0] is not None:
      obj = fusion2d[0]
    else:
      obj = fusion2d[1]
    wins = [ x for x in awindows if x.subtype() == 0 ]
    if len( wins ) == 0:
      return
    vr = a.fusionObjects( [ obj ], method='VolumeRenderingFusionMethod' )
    clip = a.fusionObjects( [ vr ], method='FusionClipMethod' )
    global volrender
    volrender = [ clip, vr ]
    a.removeObjects( obj, wins )
    a.addObjects( clip, wins )


  def enableVolumeRendering( self, on ):
    '''Enable/disable volume rendering in 3D views'''
    self._vrenabled = on
    if self._vrenabled:
      self.startVolumeRendering()
    else:
      self.stopVolumeRendering()

  def coordsChanged( self ):
    '''set the cursor on the position entered in the coords fields
    '''
    if len( awindows ) == 0:
      return
    pos = [ findChild( awin, 'coordXEdit' ).text().toFloat()[0],
      findChild( awin, 'coordYEdit' ).text().toFloat()[0],
      findChild( awin, 'coordZEdit' ).text().toFloat()[0],
    ]
    # take coords transformation into account
    tr = a.getTransformation( a.mniTemplateRef, awindows[0].getReferential() )
    if tr is not None:
      pos = tr.transform( pos )
    t = findChild( awin, 'coordTEdit' ).text().toFloat()[0]
    a.execute( 'LinkedCursor', window=awindows[0], position=pos[:3]+[t] )


# instantiate the machine
anasimple = AnaSimpleViewer()
# connect GUI actions callbacks
awin.connect( findChild( awin, 'fileOpenAction' ), qt.SIGNAL( 'activated()' ),
  anasimple.fileOpen )
awin.connect( findChild( awin, 'fileExitAction' ), qt.SIGNAL( 'activated()' ),
  anasimple.closeAll )
awin.connect( findChild( awin, 'editAddAction' ), qt.SIGNAL( 'activated()' ),
  anasimple.editAdd )
awin.connect( findChild( awin, 'editRemoveAction' ),
  qt.SIGNAL( 'activated()' ), anasimple.editRemove )
awin.connect( findChild( awin, 'editDeleteAction' ),
  qt.SIGNAL( 'activated()' ), anasimple.editDelete )
awin.connect( findChild( awin, 'viewEnable_Volume_RenderingAction' ),
  qt.SIGNAL( 'toggled( bool )' ), anasimple.enableVolumeRendering )
# manually entered coords
le = findChild( awin, 'coordXEdit' )
le.setValidator( qt.QDoubleValidator( le ) )
le = findChild( awin, 'coordYEdit' )
le.setValidator( qt.QDoubleValidator( le ) )
le = findChild( awin, 'coordZEdit' )
le.setValidator( qt.QDoubleValidator( le ) )
le = findChild( awin, 'coordTEdit' )
le.setValidator( qt.QDoubleValidator( le ) )
del le
if qt4:
  awin.connect( findChild( awin, 'coordXEdit' ),
    qt.SIGNAL( 'editingFinished()' ), anasimple.coordsChanged )
  awin.connect( findChild( awin, 'coordYEdit' ),
    qt.SIGNAL( 'editingFinished()' ), anasimple.coordsChanged )
  awin.connect( findChild( awin, 'coordZEdit' ),
    qt.SIGNAL( 'editingFinished()' ), anasimple.coordsChanged )
  awin.connect( findChild( awin, 'coordTEdit' ),
    qt.SIGNAL( 'editingFinished()' ), anasimple.coordsChanged )
else:
  awin.connect( findChild( awin, 'coordXEdit' ),
    qt.SIGNAL( 'returnPressed()' ), anasimple.coordsChanged )
  awin.connect( findChild( awin, 'coordYEdit' ),
    qt.SIGNAL( 'returnPressed()' ), anasimple.coordsChanged )
  awin.connect( findChild( awin, 'coordZEdit' ),
    qt.SIGNAL( 'returnPressed()' ), anasimple.coordsChanged )
  awin.connect( findChild( awin, 'coordTEdit' ),
    qt.SIGNAL( 'returnPressed()' ), anasimple.coordsChanged )

if not qt4:
  qt.qApp.setMainWidget( awin )

# display on the whole screen
awin.showMaximized()
# remove the splash
spl.finish( awin )
del spl

# tweak: override some user config options
a.config()[ 'setAutomaticReferential' ] = 1
a.config()[ 'windowSizeFactor' ] = 1.

# register actions and controls
ad = ana.cpp.ActionDictionary.instance()
ad.addAction( 'SimpleActions', SimpleActions )
cd = ana.cpp.ControlDictionary.instance()
cd.addControl( 'SimpleControl', SimpleControl, 25 )
cd.addControl( 'Simple3DControl', Simple3DControl, 26 )
cm = ana.cpp.ControlManager.instance()
cm.addControl( 'QAGLWidget3D', '', 'SimpleControl' )
cm.addControl( 'QAGLWidget3D', '', 'Simple3DControl' )

del cd, cm

# run Qt
if runqt:
  if qt4:
    qapp.exec_()
  else:
    qapp.exec_loop()
