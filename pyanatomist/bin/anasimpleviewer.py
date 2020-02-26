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
from soma.qt_gui.qt_backend import QtCore, QtGui
if not hasattr(QtCore, 'Slot'):
    QtCore.Slot = QtCore.pyqtSlot  # compatibility with PySide
qt = QtGui
from soma.qt_gui.qt_backend import uic
from soma.qt_gui.qt_backend.uic import loadUi
import six

if sys.version_info[0] >= 3:
    six.text_type = str


uifile = 'anasimpleviewer-qt4.ui'
findChild = lambda x, y: QtCore.QObject.findChild(x, QtCore.QObject, y)

parser = OptionParser(
    description='A simplified version of Anatomist for quick viewing')
parser.add_option('-i', '--input', dest='input', metavar='FILE',
                  action='append', default=[],
                  help='load given objects from files')
parser.add_option('-l', '--left', dest='left_mode', action='store_true',
                  help='Use left button for rotation in 3D view')

(options, args) = parser.parse_args()

# do we have to run QApplication ?
if qt.qApp.startingUp():
    qapp = qt.QApplication(args)
    runqt = True
else:
    runqt = False

# the following imports have to be made after the qApp.startingUp() test
# since they do instantiate Anatomist for registry to work.
from anatomist.cpp.simplecontrols import Simple2DControl, Simple3DControl, \
    registerSimpleControls
from anatomist.cpp.palettecontrastaction import PaletteContrastAction

# splash
pix = qt.QPixmap(os.path.expandvars(os.path.join(
                                    aims.carto.Paths.globalShared(),
                                    'anatomist-%s/icons/anatomist.png'
                                    % '.'.join(
                                    [str(x) for x in aims.version()]))))
spl = qt.QSplashScreen(pix)
spl.show()
qt.qApp.processEvents()

# start the Anatomist engine, in batch mode (no main window)
a = ana.Anatomist('-b')

# define another control where rotation is with the left mouse button
# (useful for touch devices)


class LeftSimple3DControl(Simple2DControl):

    def __init__(self, prio=25, name='Simple3DControl'):
        Simple2DControl.__init__(self, prio, name)

    def eventAutoSubscription(self, pool):
        key = QtCore.Qt
        NoModifier = key.NoModifier
        ShiftModifier = key.ShiftModifier
        ControlModifier = key.ControlModifier
        Simple2DControl.eventAutoSubscription(self, pool)
        self.mouseLongEventUnsubscribe(key.LeftButton, NoModifier)
        self.mouseLongEventSubscribe(
            key.LeftButton, NoModifier,
          pool.action('ContinuousTrackball').beginTrackball,
          pool.action('ContinuousTrackball').moveTrackball,
          pool.action('ContinuousTrackball').endTrackball, True)
        self.keyPressEventSubscribe(key.Key_Space, ControlModifier,
                                    pool.action("ContinuousTrackball").startOrStop)
        self.mousePressButtonEventSubscribe(key.MiddleButton, NoModifier,
                                            pool.action('LinkAction').execLink)

registerSimpleControls()
iconpath = os.path.join(str(a.anatomistSharedPath()), 'icons')
pix = QtGui.QPixmap(os.path.join(iconpath, 'simple3Dcontrol.png'))
ana.cpp.IconDictionary.instance().addIcon('LeftSimple3DControl', pix)
del pix, iconpath
cd = ana.cpp.ControlDictionary.instance()
cd.addControl('LeftSimple3DControl', LeftSimple3DControl, 25)

control_3d_type = 'Simple3DControl'
if options.left_mode:
    control_3d_type = 'LeftSimple3DControl'

# load the anasimpleviewer GUI
anasimpleviewerdir = os.path.join(
    six.text_type(a.anatomistSharedPath()),
  'anasimpleviewer')
cwd = os.getcwd()
# PyQt4 uic doesn' seem to allow specifying the directory when looking for
# icon files: we have no other choice than globally changing the working
# directory
os.chdir(anasimpleviewerdir)
awin = loadUi(os.path.join(anasimpleviewerdir, uifile))
os.chdir(cwd)

# global variables: lists of windows, objects, a fusion2d with a number of
# volumes in it, and a volume rendering object + clipping
fdialog = qt.QFileDialog()
fdialog.setDirectory(os.getcwd())
awindows = []
aobjects = []
fusion2d = []
volrender = None

# vieww: parent widget for anatomist windows
vieww = findChild(awin, 'windows')
viewgridlay = qt.QGridLayout(vieww)


# This class holds methods for menu/actions callbacks, and utility functions
# like load/view objects, remove/delete, etc.
class AnaSimpleViewer(qt.QObject):

    def __init__(self):
        qt.QObject.__init__(self)
        self._vrenabled = False
        self.meshes2d = {}
        # register the function on the cursor notifier of anatomist. It will be
        # called when the user clicks on a window
        a.onCursorNotifier.add(self.clickHandler)

    def clickHandler(self, eventName, params):
        '''Callback for linked cursor. In volume rendering mode, it will sync the
        VR slice to the linked cursor.
        It also updates the volumes values view
        '''
        pos = params['position']
        win = params['window']
        wref = win.getReferential()
        # display coords in MNI referential (preferably)
        tr = a.getTransformation(wref, a.mniTemplateRef)
        if tr:
            pos2 = tr.transform(pos[:3])
        else:
            pos2 = pos
        x = findChild(awin, 'coordXEdit')
        x.setText('%8.3f' % pos2[0])
        y = findChild(awin, 'coordYEdit')
        y.setText('%8.3f' % pos2[1])
        z = findChild(awin, 'coordZEdit')
        z.setText('%8.3f' % pos2[2])
        t = findChild(awin, 'coordTEdit')
        if len(pos) < 4:
            pos = pos[:3] + [0]
        t.setText('%8.3f' % pos[3])
        # display volumes values at the given position
        valbox = findChild(awin, 'volumesBox')
        valbox.clear()
        # (we don't use the same widget type in Qt3 and Qt4)
        valbox.setColumnCount(2)
        valbox.setHorizontalHeaderLabels(['Volume:', 'Value:'])
        if len(fusion2d) > 1:
            valbox.setRowCount(len(fusion2d) - 1)
            valbox.setVerticalHeaderLabels([''] * (len(fusion2d) - 1))
        i = 0
        for obj in fusion2d[1:]:
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
            newItem = qt.QTableWidgetItem(obj.name)
            valbox.setItem(i, 0, newItem)
            # check bounds
            if pos2[0] >= 0 and pos2[1] >= 0 and pos2[2] >= 0 and pos[3] >= 0 \
                and pos2[0] < aimsv.dimX() and pos2[1] < aimsv.dimY() \
                    and pos2[2] < aimsv.dimZ() and pos[3] < aimsv.dimT():
                txt = str(aimsv.value(*pos2))
            else:
                txt = ''
            newitem = qt.QTableWidgetItem(txt)
            valbox.setItem(i, 1, newitem)
            i += 1
        valbox.resizeColumnsToContents()

        # update volume rendering when it is enabled
        if self._vrenabled and len(volrender) >= 1:
            clip = volrender[0]
            t = a.getTransformation(win.getReferential(),
                                    clip.getReferential())
            if t is not None:
                pos = t.transform(pos[:3])
            clip.setOffset(pos[:3])
            clip.notifyObservers()

    def createWindow(self, wintype='Axial'):
        '''Opens a new window in the windows grid layout.
        The new window will be set in MNI referential (except 3D for now because
        of a buf in volume rendering in direct referentials), will be assigned
        the custom control, and have no menu/toolbars.
        '''
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
        viewgridlay.addWidget(w.getInternalRep(), x, y)
        self._winlayouts[x][y] = 1
        # keep it in anasimpleviewer list of windows
        awindows.append(w)
        # set custom control
        if wintype == '3D':
            a.execute('SetControl', windows=[w], control=control_3d_type)
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
        obj = a.loadObject(fname)
        self.registerObject(obj)
        # c = ana.cpp.LoadObjectCommand( fname, -1, "", False,
            #{ 'asynchonous' : True } )
        # c.objectLoaded.connect( self.objectLoaded )
        # a.execute( c )

    @QtCore.Slot('anatomist::AObject *', 'const std::string &')
    def objectLoaded(self, obj, filename):
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
        findChild(awin, 'objectslist').addItem(obj.name)
        # keep it in the global list
        aobjects.append(obj)
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
        if len(awindows) == 0:
            self.createWindow('Coronal')
            self.createWindow('Axial')
            self.createWindow('Sagittal')
            self.createWindow('3D')
            # set a cool angle of view for 3D
            a.execute('Camera', windows=[awindows[-1]],
                      view_quaternion=[0.404603, 0.143829, 0.316813, 0.845718])
        # view obj in these views
        self.addObject(obj)
        # set the cursot at the center of the object (actually, overcome a bug
        # in anatomist...)
        position = (aims.Point3df(bb[1][:3]) - bb[0][:3]) / 2.
        t = a.getTransformation(obj.getReferential(),
                                awindows[0].getReferential())
        if t:
            position = t.transform(position)
        a.execute('LinkedCursor', window=awindows[0], position=position)

    def _displayVolume(self, obj, opts={}):
        '''Display a volume or a Fusion2D in all windows.
        If volume rendering is allowed, 3D views will display a clipped volume
        rendering of the object.
        '''
        if self._vrenabled:
            wins = [x for x in awindows if x.subtype() != 0]
            if len(wins) != 0:
                a.addObjects(obj, wins, **opts)
            wins = [x for x in awindows if x.subtype() == 0]
            if len(wins) == 0:
                return
            vr = a.fusionObjects([obj], method='VolumeRenderingFusionMethod')
            clip = a.fusionObjects([vr], method='FusionClipMethod')
            global volrender
            volrender = [clip, vr]
            a.addObjects(clip, wins, **opts)
        else:
            a.addObjects(obj, awindows, **opts)

    def addVolume(self, obj, opts={}):
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
            a.deleteObjects(volrender)
            hasvr = True
            volrender = None
        if len(fusion2d) == 0:
            # only one object
            fusion2d = [None, obj]
        else:
            # several objects: fusion them
            fusobjs = fusion2d[1:] + [obj]
            f2d = a.fusionObjects(fusobjs, method='Fusion2DMethod')
            if fusion2d[0] is not None:
                # destroy the previous fusion
                a.deleteObjects(fusion2d[0])
            else:
                a.removeObjects(fusion2d[1], awindows)
            fusion2d = [f2d] + fusobjs
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
        global fusion2d, volrender
        if obj in fusion2d:
            hasvr = False
            if volrender:
                a.deleteObjects(volrender)
                volrender = None
                hasvr = True
            fusobjs = [o for o in fusion2d[1:] if o != obj]
            if len(fusobjs) >= 2:
                f2d = a.fusionObjects(fusobjs, method='Fusion2DMethod')
            else:
                f2d = None
            if fusion2d[0] is not None:
                a.deleteObjects(fusion2d[0])
            else:
                a.removeObjects(fusion2d[1], awindows)
            if len(fusobjs) == 0:
                fusion2d = []
            else:
                fusion2d = [f2d] + fusobjs
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
        mesh2d = a.fusionObjects([obj.getInternalRep()],
                                 method='Fusion2DMeshMethod')
        color = self.get_new_mesh2d_color()
        self.meshes2d[obj.getInternalRep()] = (mesh2d, color)
        mesh2d.setMaterial(diffuse=color)
        mesh2d.releaseAppRef()
        windows_2d = [w for w in awindows if w.subtype() in
                      (w.AXIAL_WINDOW, w.CORONAL_WINDOW, w.SAGITTAL_WINDOW)]
        windows_3d = [w for w in awindows if w not in windows_2d]
        a.addObjects(mesh2d, windows_2d)
        a.addObjects(obj, windows_3d)

    def removeMesh(self, obj):
        mesh2d, col = self.meshes2d[obj.getInternalRep()]
        a.removeObjects([obj, mesh2d], awindows)
        del self.meshes2d[obj.getInternalRep()]

    def addObject(self, obj):
        '''Display an object in all windows
        '''
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
        a.addObjects(obj, awindows, **opts)

    def removeObject(self, obj):
        '''Hides an object from views
        '''
        if obj.objectType == 'VOLUME':
            self.removeVolume(obj)
        elif obj.objectType == 'SURFACE':
            self.removeMesh(obj)
        else:
            a.removeObjects(obj, awindows, remove_children=True)

    def fileOpen(self):
        '''File browser + load object(s)
        '''
        global fdialog
        fd2 = fdialog
        fdialog = qt.QFileDialog()
        fdialog.setFileMode(fdialog.ExistingFiles)
        fdialog.setDirectory(fd2.directory())
        fdialog.setHistory(fd2.history())
        fdialog.show()
        res = fdialog.exec_()
        if res:
            fnames = fdialog.selectedFiles()
            for fname in fnames:
                print(six.text_type(fname))
                self.loadObject(six.text_type(fname))

    def selectedObjects(self):
        '''list of objects selected in the list box on the upper left panel
        '''
        olist = findChild(awin, 'objectslist')
        sobjs = []
        for o in olist.selectedItems():
            sobjs.append(six.text_type(o.text()).strip('\0'))
        return [o for o in aobjects if o.name in sobjs]

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
        for o in objs:
            self.removeObject(o)
        olist = findChild(awin, 'objectslist')
        for o in objs:
            olist.takeItem(olist.row(olist.findItems(o.name,
                                                     QtCore.Qt.MatchExactly)[0]))
        global aobjects
        aobjects = [o for o in aobjects if o not in objs]
        a.deleteObjects(objs)

    def closeAll(self):
        '''Exit'''
        print("Exiting")
        global vieww, viewgridlay, awindows, fusion2d, aobjects, anasimple, volrender, awin, fdialog
        # remove windows from their parent to prevent them to be brutally
        # deleted by Qt.
        for w in awindows:
            w.hide()
            viewgridlay.removeWidget(w.internalRep._get())
            w.setParent(None)
        del w
        del vieww, viewgridlay
        del anasimple
        del awindows, fusion2d, volrender, aobjects
        awin.close()
        del awin
        del fdialog
        a = ana.Anatomist()
        a.close()

    def stopVolumeRendering(self):
        '''Disable volume rendering: show a slice instead'''
        global volrender
        if not volrender:
            return
        a.deleteObjects(volrender)
        volrender = None
        if len(fusion2d) != 0:
            if fusion2d[0] is not None:
                obj = fusion2d[0]
            else:
                obj = fusion2d[1]
        wins = [w for w in awindows if w.subtype() == 0]
        a.addObjects(obj, wins)

    def startVolumeRendering(self):
        '''Enable volume rendering in 3D views'''
        if len(fusion2d) == 0:
            return
        if fusion2d[0] is not None:
            obj = fusion2d[0]
        else:
            obj = fusion2d[1]
        wins = [x for x in awindows if x.subtype() == 0]
        if len(wins) == 0:
            return
        vr = a.fusionObjects([obj], method='VolumeRenderingFusionMethod')
        clip = a.fusionObjects([vr], method='FusionClipMethod')
        global volrender
        volrender = [clip, vr]
        a.removeObjects(obj, wins)
        a.addObjects(clip, wins)

    def enableVolumeRendering(self, on):
        '''Enable/disable volume rendering in 3D views'''
        self._vrenabled = on
        if self._vrenabled:
            self.startVolumeRendering()
        else:
            self.stopVolumeRendering()

    def coordsChanged(self):
        '''set the cursor on the position entered in the coords fields
        '''
        if len(awindows) == 0:
            return
        pos = [findChild(awin, 'coordXEdit').text().toFloat()[0],
               findChild(awin, 'coordYEdit').text().toFloat()[0],
               findChild(awin, 'coordZEdit').text().toFloat()[0],
               ]
        # take coords transformation into account
        tr = a.getTransformation(
            a.mniTemplateRef, awindows[0].getReferential())
        if tr is not None:
            pos = tr.transform(pos)
        t = findChild(awin, 'coordTEdit').text().toFloat()[0]
        a.execute('LinkedCursor', window=awindows[0], position=pos[:3] + [t])

    def dragEnterEvent(self, win, event):
        x = ana.cpp.QAObjectDrag.canDecode( event ) \
            or ana.cpp.QAObjectDrag.canDecodeURI(event)
        if x:
            event.accept()
        else:
            event.reject()

    def dropEvent(self, win, event):
        o = ana.cpp.set_AObjectPtr()
        if ana.cpp.QAObjectDrag.decode(event, o):
            for obj in o:
                ob = a.AObject(o)
                if ob not in aobjects:
                    self.registerObject(ob)
                else:
                    self.addObject(ob)
            event.accept()
            return
        else:
            things = ana.cpp.QAObjectDrag.decodeURI(event)
            if things is not None:
                for obj in things[0]:
                    objnames = [x.fileName() for x in aobjects]
                    if obj not in objnames:
                        self.loadObject(obj)
                    else:
                        o = [x for x in aobjects if x.fileName() == obj][0]
                        self.addObject(o)
                # TODO: things[1]: .ana scripts
                event.accept()
                return
        event.reject()


# instantiate the machine
anasimple = AnaSimpleViewer()
# connect GUI actions callbacks
findChild(awin, 'fileOpenAction').triggered.connect(anasimple.fileOpen)
findChild(awin, 'fileExitAction').triggered.connect(anasimple.closeAll)
findChild(awin, 'editAddAction').triggered.connect(anasimple.editAdd)
findChild(awin, 'editRemoveAction').triggered.connect(anasimple.editRemove)
findChild(awin, 'editDeleteAction').triggered.connect(anasimple.editDelete)
findChild(awin, 'viewEnable_Volume_RenderingAction').toggled.connect(
    anasimple.enableVolumeRendering)
# manually entered coords
le = findChild(awin, 'coordXEdit')
le.setValidator(qt.QDoubleValidator(le))
le = findChild(awin, 'coordYEdit')
le.setValidator(qt.QDoubleValidator(le))
le = findChild(awin, 'coordZEdit')
le.setValidator(qt.QDoubleValidator(le))
le = findChild(awin, 'coordTEdit')
le.setValidator(qt.QDoubleValidator(le))
del le
findChild(awin, 'coordXEdit').editingFinished.connect(anasimple.coordsChanged)
findChild(awin, 'coordYEdit').editingFinished.connect(anasimple.coordsChanged)
findChild(awin, 'coordZEdit').editingFinished.connect(anasimple.coordsChanged)
findChild(awin, 'coordTEdit').editingFinished.connect(anasimple.coordsChanged)

awin.dropEvent = lambda awin, event: anasimple.dropEvent(awin, event)
awin.dragEnterEvent = lambda awin, event: anasimple.dragEnterEvent(
    awin, event)
awin.setAcceptDrops(True)


# display on the whole screen
awin.showMaximized()
# remove the splash
spl.finish(awin)
del spl

# tweak: override some user config options
a.config()['setAutomaticReferential'] = 1
a.config()['windowSizeFactor'] = 1.

# register controls
cm = ana.cpp.ControlManager.instance()
cm.addControl('QAGLWidget3D', '', 'Simple2DControl')
cm.addControl('QAGLWidget3D', '', 'LeftSimple3DControl')
print('controls registered.')

del cm

a.setGraphParams(label_attribute='label')

for i in options.input + args:
    anasimple.loadObject(i)

# run Qt
if runqt:
    qapp.exec_()

# cleanup before exiting
anasimple.closeAll()
