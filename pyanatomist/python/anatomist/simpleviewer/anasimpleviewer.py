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

from __future__ import print_function
from __future__ import absolute_import
import anatomist.direct.api as ana
from soma import aims
from soma.aims import colormaphints
import sys
import os
from optparse import OptionParser

# determine wheter we are using Qt4 or Qt5, and hack a little bit accordingly
# the boolean qt4 gloabl variable will tell it for later usage
from soma.qt_gui import qt_backend
from six.moves import zip
qt_backend.set_qt_backend(compatible_qt5=True)
from soma.qt_gui.qt_backend import QtCore, QtGui, Qt
from soma.qt_gui.qt_backend import uic
from soma.qt_gui.qt_backend.uic import loadUi
import six

# the following imports have to be made after the qApp.startingUp() test
# since they do instantiate Anatomist for registry to work.
from anatomist.cpp.simplecontrols import Simple2DControl, Simple3DControl, \
    registerSimpleControls


class LeftSimple3DControl(Simple2DControl):
    '''
    define another control where rotation is with the left mouse button
    (useful for touch devices)
    '''

    def __init__(self, prio=25, name='LeftSimple3DControl'):
        super(LeftSimple3DControl, self).__init__(prio, name)

    def eventAutoSubscription(self, pool):
        key = QtCore.Qt
        NoModifier = key.NoModifier
        ShiftModifier = key.ShiftModifier
        ControlModifier = key.ControlModifier
        super(LeftSimple3DControl, self).eventAutoSubscription(pool)
        self.mouseLongEventUnsubscribe(key.LeftButton, NoModifier)
        self.mouseLongEventSubscribe(
            key.LeftButton, NoModifier,
          pool.action('ContinuousTrackball').beginTrackball,
          pool.action('ContinuousTrackball').moveTrackball,
          pool.action('ContinuousTrackball').endTrackball, True)
        self.keyPressEventSubscribe(
            key.Key_Space, ControlModifier,
            pool.action("ContinuousTrackball").startOrStop)
        self.mousePressButtonEventSubscribe(key.MiddleButton, NoModifier,
                                            pool.action('LinkAction').execLink)


class VolRenderControl(LeftSimple3DControl):
    '''
    define another control where cut slice rotation is with the middle mouse
    button
    '''

    def __init__(self, prio=25, name='VolRenderControl'):
        super(VolRenderControl, self).__init__(prio, name)

    def eventAutoSubscription(self, pool):
        super(VolRenderControl, self).eventAutoSubscription(pool)
        self.mouseLongEventUnsubscribe(Qt.Qt.MiddleButton, Qt.Qt.NoModifier)
        self.mouseLongEventSubscribe(
            Qt.Qt.MiddleButton, Qt.Qt.NoModifier,
          pool.action('TrackCutAction').beginTrackball,
          pool.action('TrackCutAction').moveTrackball,
          pool.action('TrackCutAction').endTrackball, True)


class AnaSimpleViewer(Qt.QObject):
    '''
    AnaSimpleViewer is a "simple viewer" application and widget, which can be
    used using the "anasimpleviewer.py" command, or included in a custom widget
    as a library module.

    It includes an objects list and 4 3D views (anatomist windows). Objects
    loaded are added in all views, and can be hidden or shown using the "add"
    and "remove" buttons.

    The AnaSimpleViewer class holds methods for menu/actions callbacks, and
    utility functions like load/view objects, remove/delete, etc.

    It is a QObject, but not a QWidget. The widget can be accessed as the
    ``awidget`` attribute in the AnaSimpleViewer instance.

    As it is more intended to be used as a complete application, and it is
    simpler to handle in Anatomist, some global Anatomist config variables and
    controls may be set within AnaSimpleViewer. This is done optionally using
    the :meth:`init_global_handlers` method, which is called by the constructor
    if the argument `init_global_handlers` is not set to False when calling it.
    '''

    _global_handlers_initialized = False

    def __init__(self, init_global_handlers=True):
        Qt.QObject.__init__(self)

        if init_global_handlers:
            self.init_global_handlers()

        a = ana.Anatomist('-b')
        uifile = 'anasimpleviewer-qt4.ui'
        # load the anasimpleviewer GUI
        anasimpleviewerdir = os.path.join(
            six.text_type(a.anatomistSharedPath()),
            'anasimpleviewer')
        cwd = os.getcwd()
        # PyQt4 uic doesn' seem to allow specifying the directory when
        # looking for icon files: we have no other choice than globally
        # changing the working directory
        os.chdir(anasimpleviewerdir)
        awin = loadUi(os.path.join(anasimpleviewerdir, uifile))
        os.chdir(cwd)
        self.awidget = awin

        # connect GUI actions callbacks
        findChild = lambda x, y: Qt.QObject.findChild(x, QtCore.QObject, y)

        findChild(awin, 'fileOpenAction').triggered.connect(self.fileOpen)
        findChild(awin, 'fileExitAction').triggered.connect(self.closeAll)
        findChild(awin, 'editAddAction').triggered.connect(self.editAdd)
        findChild(awin, 'editRemoveAction').triggered.connect(self.editRemove)
        findChild(awin, 'editDeleteAction').triggered.connect(self.editDelete)
        findChild(awin, 'viewEnable_Volume_RenderingAction').toggled.connect(
            self.enableVolumeRendering)
        findChild(awin, 'viewOpen_Anatomist_main_window').triggered.connect(
            self.open_anatomist_main_window)
        # manually entered coords
        le = findChild(awin, 'coordXEdit')
        le.setValidator(Qt.QDoubleValidator(le))
        le = findChild(awin, 'coordYEdit')
        le.setValidator(Qt.QDoubleValidator(le))
        le = findChild(awin, 'coordZEdit')
        le.setValidator(Qt.QDoubleValidator(le))
        le = findChild(awin, 'coordTEdit')
        le.setValidator(Qt.QDoubleValidator(le))
        del le
        findChild(awin,
                  'coordXEdit').editingFinished.connect(self.coordsChanged)
        findChild(awin,
                  'coordYEdit').editingFinished.connect(self.coordsChanged)
        findChild(awin,
                  'coordZEdit').editingFinished.connect(self.coordsChanged)
        findChild(awin,
                  'coordTEdit').editingFinished.connect(self.coordsChanged)
        objects_list = findChild(self.awidget, 'objectslist')
        objects_list.setContextMenuPolicy(Qt.Qt.CustomContextMenu)
        objects_list.customContextMenuRequested.connect(self.popup_objects)

        awin.dropEvent = lambda awin, event: self.dropEvent(awin, event)
        awin.dragEnterEvent = lambda awin, event: self.dragEnterEvent(
            awin, event)
        awin.setAcceptDrops(True)

        self._vrenabled = False
        self.meshes2d = {}
        # register the function on the cursor notifier of anatomist. It will be
        # called when the user clicks on a window
        a.onCursorNotifier.add(self.clickHandler)

        # vieww: parent widget for anatomist windows
        vieww = findChild(awin, 'windows')
        self.viewgridlay = Qt.QGridLayout(vieww)
        self.fdialog = None
        self.awindows = []
        self.aobjects = []
        self.fusion2d = []
        self.volrender = None
        self.control_3d_type = 'LeftSimple3DControl'

    def init_global_handlers(self):
        '''
        Set some global controls / settings in Anatomist application object
        '''
        if not AnaSimpleViewer._global_handlers_initialized:

            registerSimpleControls()
            a = ana.Anatomist('-b')
            iconpath = os.path.join(str(a.anatomistSharedPath()), 'icons')
            pix = Qt.QPixmap(os.path.join(iconpath, 'simple3Dcontrol.png'))
            ana.cpp.IconDictionary.instance().addIcon('LeftSimple3DControl', pix)
            del pix, iconpath
            cd = ana.cpp.ControlDictionary.instance()
            cd.addControl('LeftSimple3DControl', LeftSimple3DControl, 25)
            cd.addControl('VolRenderControl', VolRenderControl, 25)

            # tweak: override some user config options
            a.config()['setAutomaticReferential'] = 1
            a.config()['windowSizeFactor'] = 1.
            a.config()['axialConvention'] = 'neuro'
            a.config()['commonScannerBasedReferential'] = 1

            # register controls
            cm = ana.cpp.ControlManager.instance()
            cm.addControl('QAGLWidget3D', '', 'Simple2DControl')
            cm.addControl('QAGLWidget3D', '', 'LeftSimple3DControl')
            cm.addControl('QAGLWidget3D', '', 'VolRenderControl')
            print('controls registered.')

            del cm

            a.setGraphParams(label_attribute='label')

            AnaSimpleViewer._global_handlers_initialized = True

    def clickHandler(self, eventName, params):
        '''Callback for linked cursor. In volume rendering mode, it will sync
        the VR slice to the linked cursor.
        It also updates the volumes values view
        '''
        a = ana.Anatomist('-b')
        pos = params['position']
        win = params['window']
        wref = win.getReferential()
        # display coords in MNI referential (preferably)
        tr = a.getTransformation(wref, a.mniTemplateRef)
        if tr:
            pos2 = tr.transform(pos[:3])
        else:
            pos2 = pos

        findChild = lambda x, y: Qt.QObject.findChild(x, QtCore.QObject, y)

        x = findChild(self.awidget, 'coordXEdit')
        x.setText('%8.3f' % pos2[0])
        y = findChild(self.awidget, 'coordYEdit')
        y.setText('%8.3f' % pos2[1])
        z = findChild(self.awidget, 'coordZEdit')
        z.setText('%8.3f' % pos2[2])
        t = findChild(self.awidget, 'coordTEdit')
        if len(pos) < 4:
            pos = pos[:3] + [0]
        t.setText('%8.3f' % pos[3])
        # display volumes values at the given position
        valbox = findChild(self.awidget, 'volumesBox')
        valbox.clear()
        # (we don't use the same widget type in Qt3 and Qt4)
        valbox.setColumnCount(2)
        valbox.setHorizontalHeaderLabels(['Volume:', 'Value:'])
        if len(self.fusion2d) > 1:
            valbox.setRowCount(len(self.fusion2d) - 1)
            valbox.setVerticalHeaderLabels([''] * (len(self.fusion2d) - 1))
        i = 0
        for obj in self.fusion2d[1:]:
            # retreive volume value in its own coords system
            aimsv = ana.cpp.AObjectConverter.aims(obj)
            oref = obj.getReferential()
            tr = a.getTransformation(wref, oref)
            if tr:
                pos2 = tr.transform(pos[:3])
            else:
                pos2 = pos[:3]
            vs = obj.voxelSize()
            pos2 = [int(round(x / y)) for x, y in zip(pos2, vs)]
            # pos2 in in voxels, in obj coords system
            newItem = Qt.QTableWidgetItem(obj.name)
            valbox.setItem(i, 0, newItem)
            # check bounds
            if pos2[0] >= 0 and pos2[1] >= 0 and pos2[2] >= 0 and pos[3] >= 0 \
                and pos2[0] < aimsv.dimX() and pos2[1] < aimsv.dimY() \
                    and pos2[2] < aimsv.dimZ() and pos[3] < aimsv.dimT():
                txt = str(aimsv.value(*pos2))
            else:
                txt = ''
            newitem = Qt.QTableWidgetItem(txt)
            valbox.setItem(i, 1, newitem)
            i += 1
        valbox.resizeColumnsToContents()

        # update volume rendering when it is enabled
        if self._vrenabled and len(self.volrender) >= 1:
            clip = self.volrender[0]
            t = a.getTransformation(win.getReferential(),
                                    clip.getReferential())
            if t is not None:
                pos = t.transform(pos[:3])
            clip.setOffset(pos[:3])
            clip.notifyObservers()

    def createWindow(self, wintype='Axial'):
        '''Opens a new window in the windows grid layout.
        The new window will be set in MNI referential (except 3D for now
        because of a buf in volume rendering in direct referentials), will be
        assigned the custom control, and have no menu/toolbars.
        '''
        a = ana.Anatomist('-b')
        w = a.createWindow(wintype, no_decoration=True, options={'hidden': 1})
        w.setAcceptDrops(False)
        # insert in grid layout
        x = 0
        y = 0
        if not hasattr(self, '_winlayouts'):
            self._winlayouts = [[0, 0], [0, 0]]
        else:
            freeslot = False
            for y in (0, 1):
                for x in (0, 1):
                    if not self._winlayouts[x][y]:
                        freeslot = True
                        break
                if freeslot:
                    break
        # in Qt4, the widget must not have a parent before calling
        # layout.addWidget
        self.viewgridlay.addWidget(w.getInternalRep(), x, y)
        self._winlayouts[x][y] = 1
        # keep it in anasimpleviewer list of windows
        self.awindows.append(w)
        # set custom control
        if wintype == '3D':
            a.execute('SetControl', windows=[w], control=self.control_3d_type)
        else:
            a.execute('SetControl', windows=[w], control='Simple2DControl')
            a.assignReferential(a.mniTemplateRef, w)
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
        a.execute('WindowConfig', windows=[w],
                  light={'background': [0., 0., 0., 1.]})

    def loadObject(self, fname):
        '''Load an object and display it in all anasimpleviewer windows
        '''
        a = ana.Anatomist('-b')
        obj = a.loadObject(fname)
        self.registerObject(obj)
        # c = ana.cpp.LoadObjectCommand( fname, -1, "", False,
            #{ 'asynchonous' : True } )
        # c.objectLoaded.connect( self.objectLoaded )
        # a.execute( c )

    @QtCore.Slot('anatomist::AObject *', 'const std::string &')
    def objectLoaded(self, obj, filename):
        a = ana.Anatomist('-b')
        if not obj:
            return
        o = a.AObject(a, obj)
        o.releaseAppRef()
        p = a.theProcessor()
        resetProcExec = False
        if not p.execWhileIdle():
            # allow recursive commands execution, otherwise the execute()
            # may not be done right now
            p.allowExecWhileIdle(True)
            resetProcExec = True
        self.registerObject(o)
        if resetProcExec:
            # set back recursive execution to its previous state
            p.allowExecWhileIdle(False)

    def registerObject(self, obj):
        '''Register an object in anasimpleviewer objects list, and display it
        '''
        a = ana.Anatomist('-b')
        Qt.QObject.findChild(self.awidget, QtCore.QObject,
                             'objectslist').addItem(obj.name)
        # keep it in the global list
        self.aobjects.append(obj)
        if obj.objectType == 'VOLUME':
            # volume are checked for possible adequate colormaps
            hints = colormaphints.checkVolume(
                ana.cpp.AObjectConverter.aims(obj))
            obj.attributed()['colormaphints'] = hints
        bb = obj.boundingbox()
        if not bb:
            # not a viewable object
            return
        # create the 4 windows if they don't exist
        if len(self.awindows) == 0:
            self.createWindow('Coronal')
            self.createWindow('Axial')
            self.createWindow('Sagittal')
            self.createWindow('3D')
            # set a cool angle of view for 3D
            a.execute('Camera', windows=[self.awindows[-1]],
                      view_quaternion=[0.404603, 0.143829, 0.316813, 0.845718])
        # view obj in these views
        self.addObject(obj)
        # set the cursot at the center of the object (actually, overcome a bug
        # in anatomist...)
        position = (aims.Point3df(bb[1][:3]) - bb[0][:3]) / 2.
        wrefs = [w.getReferential() for w in self.awindows]
        srefs = set([r.uuid() for r in wrefs])
        if len(srefs) != 1:
            # not all windows in the same ref
            if aims.StandardReferentials.mniTemplateReferentialID() in srefs:
                wref_id = aims.StandardReferentials.mniTemplateReferentialID()
                wref = [r for r in wrefs if r.uuid() == wref_id][0]
            elif aims.StandardReferentials.acPcReferentialID() in srefs:
                wref = a.centralReferential()
            elif aims.StandardReferentials.commonScannerBasedReferentialID() \
                    in srefs:
                wref_id = \
                    aims.StandardReferentials.commonScannerBasedReferentialID()
                wref = [r for r in wrefs if r.uuid() == wref_id][0]
            else:
                wref = wrefs[0]
            for w in self.awindows:
                w.setReferential(wref)
        else:
            wref = wrefs[0]

        t = a.getTransformation(obj.getReferential(), wref)
        if not t and obj.getReferential() != wref:
            # try to find a scanner-based ref and connect it to MNI
            sbref = [r for r in a.getReferentials()
                     if r.uuid() == aims.StandardReferentials.
                          commonScannerBasedReferentialID()]
            if sbref:
                sbref = sbref[0]
                t2 = a.getTransformation(obj.getReferential(), sbref)
                if t2:
                    a.execute(
                        'LoadTransformation', origin=sbref,
                        destination=a.mniTemplateRef,
                        matrix=[0, 0, 0,
                                1, 0, 0,
                                0, 1, 0,
                                0, 0, 1])
                else:
                    # otherwise we will assume the object is in the central
                    # referential.
                    a.execute(
                        'LoadTransformation', origin=obj.getReferential(),
                        destination=a.centralRef,
                        matrix=[0, 0, 0,
                                1, 0, 0,
                                0, 1, 0,
                                0, 0, 1])
                t = a.getTransformation(obj.getReferential(),
                                        self.awindows[0].getReferential())
        if t:
            position = t.transform(position)
        a.execute('LinkedCursor', window=self.awindows[0], position=position)
        for w in self.awindows:
            w.focusView()

    def _displayVolume(self, obj, opts={}):
        '''Display a volume or a Fusion2D in all windows.
        If volume rendering is allowed, 3D views will display a clipped volume
        rendering of the object.
        '''
        a = ana.Anatomist('-b')
        if self._vrenabled:
            wins = [x for x in self.awindows if x.subtype() != 0]
            if len(wins) != 0:
                a.addObjects(obj, wins, **opts)
            wins = [x for x in self.awindows if x.subtype() == 0]
            if len(wins) == 0:
                return
            vr = a.fusionObjects([obj], method='VolumeRenderingFusionMethod')
            clip = a.fusionObjects([vr], method='FusionClipMethod')
            self.volrender = [clip, vr]
            a.addObjects(clip, wins, **opts)
        else:
            a.addObjects(obj, self.awindows, **opts)

    def addVolume(self, obj, opts={}):
        '''Display a volume in all windows.
        If several volumes are displayed, a Fusion2D will be built to wrap all
        of them.
        If volume rendering is allowed, 3D views will display a clipped volume
        rendering of either the single volume (if only one is present), or of
        the 2D fusion.
        '''
        a = ana.Anatomist('-b')
        if obj in self.fusion2d:
            return
        hasvr = False
        if self.volrender:
            # delete the previous volume rendering
            a.deleteObjects(self.volrender)
            hasvr = True
            self.volrender = None
        if len(self.fusion2d) == 0:
            # only one object
            self.fusion2d = [None, obj]
        else:
            # several objects: fusion them
            fusobjs = self.fusion2d[1:] + [obj]
            f2d = a.fusionObjects(fusobjs, method='Fusion2DMethod')
            if self.fusion2d[0] is not None:
                # destroy the previous fusion
                a.deleteObjects(self.fusion2d[0])
            else:
                a.removeObjects(self.fusion2d[1], self.awindows)
            self.fusion2d = [f2d] + fusobjs
            # repalette( fusobjs )
            obj = f2d
        if obj.objectType == 'VOLUME':
            # choose a good colormap for a single volume
            if 'volume_contents_likelihoods' in obj.attributed():
                cmap = colormaphints.chooseColormaps(
                    (obj.attributed()['colormaphints'], ))
                obj.setPalette(cmap[0])
        else:
            # choose good colormaps for the current set of volumes
            hints = [x.attributed()['colormaphints'] for x in obj.children]
            children = [x for x, y in zip(obj.children, hints)
                        if 'volume_contents_likelihoods' in y]
            hints = [x for x in hints if 'volume_contents_likelihoods' in x]
            cmaps = colormaphints.chooseColormaps(hints)
            for x, y in zip(children, cmaps):
                x.setPalette(y)
        # call a lower-level function for display and volume rendering
        self._displayVolume(obj, opts)

    def removeVolume(self, obj, opts={}):
        '''Hides a volume from views (low-level function: use removeObject)
        '''
        a = ana.Anatomist('-b')
        if obj in self.fusion2d:
            hasvr = False
            if self.volrender:
                a.deleteObjects(self.volrender)
                self.volrender = None
                hasvr = True
            fusobjs = [o for o in self.fusion2d[1:] if o != obj]
            if len(fusobjs) >= 2:
                f2d = a.fusionObjects(fusobjs, method='Fusion2DMethod')
            else:
                f2d = None
            if self.fusion2d[0] is not None:
                a.deleteObjects(self.fusion2d[0])
            else:
                a.removeObjects(self.fusion2d[1], self.awindows)
            if len(fusobjs) == 0:
                self.fusion2d = []
            else:
                self.fusion2d = [f2d] + fusobjs
            # repalette( fusobjs )
            if f2d:
                obj = f2d
            elif len(fusobjs) == 1:
                obj = fusobjs[0]
            else:
                return
            self._displayVolume(obj, opts)

    def get_new_mesh2d_color(self):
        colors = [(1., 0.3, 0.3, 1.),
                  (0.3, 1., 0.3, 1.),
                  (0.3, 0.3, 1., 1.),
                  (1., 1., 0., 1.),
                  (0., 1., 1., 1.),
                  (1., 0., 1., 1.),
                  (1., 1., 1., 1.),
                  (1., 0.7, 0., 1.),
                  (1., 0., 0.7, 1.),
                  (1., 0.7, 0.7, 1.),
                  (0.7, 1., 0., 1.),
                  (0., 1., 0.7, 1.),
                  (0.7, 1., 0.7, 1.),
                  (0.7, 0., 1., 1.),
                  (0., 0.7, 1., 1.),
                  (0.7, 0.7, 1., 1.),
                  (1., 1., 0.5, 1.),
                  (0.5, 1., 1., 1.),
                  (1, 0.5, 1., 1.)]
        used_cols = set([col for obj, col in six.itervalues(self.meshes2d)])
        for col in colors:
            if col not in used_cols:
                return col
        return len(self.meshes2d) % len(colors)

    def addMesh(self, obj, opts):
        a = ana.Anatomist('-b')
        mesh2d = a.fusionObjects([obj.getInternalRep()],
                                 method='Fusion2DMeshMethod')
        color = self.get_new_mesh2d_color()
        self.meshes2d[obj.getInternalRep()] = (mesh2d, color)
        mesh2d.setMaterial(diffuse=color)
        mesh2d.releaseAppRef()
        windows_2d = [w for w in self.awindows if w.subtype() in
                      (w.AXIAL_WINDOW, w.CORONAL_WINDOW, w.SAGITTAL_WINDOW)]
        windows_3d = [w for w in self.awindows if w not in windows_2d]
        a.addObjects(mesh2d, windows_2d)
        a.addObjects(obj, windows_3d)

    def removeMesh(self, obj):
        a = ana.Anatomist('-b')
        mesh2d, col = self.meshes2d[obj.getInternalRep()]
        a.removeObjects([obj, mesh2d], self.awindows)
        del self.meshes2d[obj.getInternalRep()]

    def addObject(self, obj):
        '''Display an object in all windows
        '''
        a = ana.Anatomist('-b')
        opts = {}
        if obj.objectType == 'VOLUME':
            # volumes have a specific function since several volumes have to be
            # fusionned, and a volume rendering may occur
            self.addVolume(obj, opts)
            return
        elif obj.objectType == 'SURFACE':
            self.addMesh(obj, opts)
            return
        elif obj.objectType == 'GRAPH':
            opts['add_graph_nodes'] = 1
        a.addObjects(obj, self.awindows, **opts)

    def removeObject(self, obj):
        '''Hides an object from views
        '''
        a = ana.Anatomist('-b')
        if obj.objectType == 'VOLUME':
            self.removeVolume(obj)
        elif obj.objectType == 'SURFACE':
            self.removeMesh(obj)
        else:
            a.removeObjects(obj, self.awindows, remove_children=True)

    def fileOpen(self):
        '''File browser + load object(s)
        '''
        if not self.fdialog:
            self.fdialog = Qt.QFileDialog()
            self.fdialog.setDirectory(os.getcwd())
        else:
            fd2 = self.fdialog
            self.fdialog = Qt.QFileDialog()
            self.fdialog.setDirectory(fd2.directory())
            self.fdialog.setHistory(fd2.history())
        self.fdialog.setFileMode(self.fdialog.ExistingFiles)
        self.fdialog.show()
        res = self.fdialog.exec_()
        if res:
            fnames = self.fdialog.selectedFiles()
            for fname in fnames:
                print(six.text_type(fname))
                self.loadObject(six.text_type(fname))

    def selectedObjects(self):
        '''list of objects selected in the list box on the upper left panel
        '''
        olist = Qt.QObject.findChild(self.awidget, QtCore.QObject,
                                     'objectslist')
        sobjs = []
        for o in olist.selectedItems():
            sobjs.append(six.text_type(o.text()).strip('\0'))
        return [o for o in self.aobjects if o.name in sobjs]

    def editAdd(self):
        '''Display selected objects'''
        objs = self.selectedObjects()
        for o in objs:
            self.addObject(o)

    def editRemove(self):
        '''Hide selected objects'''
        objs = self.selectedObjects()
        for o in objs:
            self.removeObject(o)

    def editDelete(self):
        '''Delete selected objects'''
        objs = self.selectedObjects()
        self.deleteObjects(objs)

    def deleteObjects(self, objs):
        '''Delete the given objects
        '''
        a = ana.Anatomist('-b')
        for o in objs:
            self.removeObject(o)
        olist = Qt.QObject.findChild(self.awidget, QtCore.QObject,
                                     'objectslist')
        for o in objs:
            olist.takeItem(olist.row(olist.findItems(
                o.name, QtCore.Qt.MatchExactly)[0]))
        self.aobjects = [o for o in self.aobjects if o not in objs]
        a.deleteObjects(objs)

    def deleteObjectsFromFiles(self, files):
        '''Delete the given objects given by their file names
        '''
        a = ana.Anatomist('-b')
        objs = [o for o in a.getObjects() if o.filename in files]
        self.deleteObjects(objs)

    def closeAll(self):
        '''Exit'''
        print("Exiting")
        a = ana.Anatomist('-b')
        # remove windows from their parent to prevent them to be brutally
        # deleted by Qt.
        w = None
        for w in self.awindows:
            w.hide()
            self.viewgridlay.removeWidget(w.internalRep._get())
            w.setParent(None)
        del w
        self.awindows = []
        self.viewgridlay = None
        self.volrender = None
        self.fusion2d = []
        self.aobjects = []
        self.awidget.close()
        self.awidget = None
        del self.fdialog
        a = ana.Anatomist()
        a.close()

    def stopVolumeRendering(self):
        '''Disable volume rendering: show a slice instead'''
        a = ana.Anatomist('-b')
        if not self.volrender:
            return
        a.deleteObjects(self.volrender)
        self.volrender = None
        if len(self.fusion2d) != 0:
            if self.fusion2d[0] is not None:
                obj = self.fusion2d[0]
            else:
                obj = self.fusion2d[1]
        wins = [w for w in self.awindows if w.subtype() == 0]
        a.addObjects(obj, wins)
        self.control_3d_type = 'LeftSimple3DControl'
        a.execute('SetControl', windows=wins, control=self.control_3d_type)

    def startVolumeRendering(self):
        '''Enable volume rendering in 3D views'''
        a = ana.Anatomist('-b')
        if len(self.fusion2d) == 0:
            return
        if self.fusion2d[0] is not None:
            obj = self.fusion2d[0]
        else:
            obj = self.fusion2d[1]
        wins = [x for x in self.awindows if x.subtype() == 0]
        if len(wins) == 0:
            return
        vr = a.fusionObjects([obj], method='VolumeRenderingFusionMethod')
        clip = a.fusionObjects([vr], method='FusionClipMethod')
        self.volrender = [clip, vr]
        a.removeObjects(obj, wins)
        a.addObjects(clip, wins)
        self.control_3d_type = 'VolRenderControl'
        a.execute('SetControl', windows=wins, control=self.control_3d_type)

    def enableVolumeRendering(self, on):
        '''Enable/disable volume rendering in 3D views'''
        self._vrenabled = on
        if self._vrenabled:
            self.startVolumeRendering()
        else:
            self.stopVolumeRendering()

    def open_anatomist_main_window(self):
        a = ana.Anatomist()
        cw = a.getControlWindow()
        a.execute('CreateControlWindow')
        if not cw:
            anacontrolmenu = sys.modules.get('anacontrolmenu')
            if anacontrolmenu:
                anacontrolmenu.add_gui_menus()

    def coordsChanged(self):
        '''set the cursor on the position entered in the coords fields
        '''
        a = ana.Anatomist('-b')
        if len(self.awindows) == 0:
            return
        findChild = lambda x, y: Qt.QObject.findChild(x, QtCore.QObject, y)
        pos = [float(findChild(self.awidget, 'coordXEdit').text()),
               float(findChild(self.awidget, 'coordYEdit').text()),
               float(findChild(self.awidget, 'coordZEdit').text()),
               ]
        # take coords transformation into account
        tr = a.getTransformation(
            a.mniTemplateRef, self.awindows[0].getReferential())
        if tr is not None:
            pos = tr.transform(pos)
        t = float(findChild(self.awidget, 'coordTEdit').text())
        a.execute('LinkedCursor', window=self.awindows[0], position=pos[:3] + [t])

    def dragEnterEvent(self, win, event):
        x = ana.cpp.QAObjectDrag.canDecode( event ) \
            or ana.cpp.QAObjectDrag.canDecodeURI(event)
        if x:
            event.accept()
        else:
            event.reject()

    def dropEvent(self, win, event):
        a = ana.Anatomist('-b')
        o = ana.cpp.set_AObjectPtr()
        if ana.cpp.QAObjectDrag.decode(event, o):
            for obj in o:
                ob = a.AObject(o)
                if ob not in self.aobjects:
                    self.registerObject(ob)
                else:
                    self.addObject(ob)
            event.accept()
            return
        else:
            things = ana.cpp.QAObjectDrag.decodeURI(event)
            if things is not None:
                for obj in things[0]:
                    objnames = [x.fileName() for x in self.aobjects]
                    if obj not in objnames:
                        self.loadObject(obj)
                    else:
                        o = [x for x in self.aobjects if x.fileName() == obj][0]
                        self.addObject(o)
                # TODO: things[1]: .ana scripts
                event.accept()
                return
        event.reject()

    def popup_objects(self):
        '''
        Right-click popup on objects list
        '''
        sel = self.selectedObjects()
        if len(sel) == 0:
            return
        t = aims.Tree()
        osel = [o.getInternalRep() for o in sel]
        options = ana.cpp.OptionMatcher.commonOptions(osel, t)
        menu = ana.cpp.OptionMatcher.popupMenu(osel, t)
        prop = menu.addAction('Object properties')
        prop.triggered.connect(self.object_properties)
        menu.exec_(Qt.QCursor.pos())

    def object_properties(self):
        '''
        Display selected objects properties in a browser window
        '''
        a = ana.Anatomist('-b')
        if not hasattr(self, 'browser') or not self.browser \
                or self.browser.isNull() or not self.browser.isVisible():
            self.browser = a.createWindow('Browser')
        else:
            self.browser.removeObjects(self.browser.Objects())
        self.browser.addObjects(self.selectedObjects())




