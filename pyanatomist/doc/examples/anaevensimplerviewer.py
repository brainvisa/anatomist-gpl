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

'''
Build a custom simplified viewer based on Anatomist
===================================================

An even simplified version of the anasimpleviewer application, which may also be used as a programming example. Its code is in the “bin/”” directory of the binary packages.

.. .. figure:: ../images/anaevensimplerviewer.png
'''

from __future__ import print_function
from __future__ import absolute_import
import anatomist.direct.api as ana
from soma import aims
from soma.aims import colormaphints
import sys
import os
from soma.qt_gui import qt_backend
from soma.qt_gui.qt_backend import Qt, loadUi
import six
from six.moves import zip


def findChild(x, y): return Qt.QObject.findChild(x, Qt.QObject, y)


if Qt.QApplication.instance() is None:
    run_qt = True
else:
    run_qt = False

# start the Anatomist engine, in batch mode (no main window)
a = ana.Anatomist('-b')

# load the anasimpleviewer GUI
uifile = 'anasimpleviewer-qt4.ui'
anasimpleviewerdir = os.path.join(six.text_type(a.anatomistSharedPath()),
                                  'anasimpleviewer')
cwd = os.getcwd()
# PyQt4 uic doesn' seem to allow specifying the directory when looking for
# icon files: we have no other choice than globally changing the working
# directory
os.chdir(anasimpleviewerdir)
awin = loadUi(os.path.join(anasimpleviewerdir, uifile))
os.chdir(cwd)

# global variables: lists of windows, objects, a fusion2d with a number of
# volumes in it
awindows = []
aobjects = []
fusion2d = []

# vieww: parent block widget for anatomist windows
vieww = findChild(awin, 'windows')
viewgridlay = Qt.QGridLayout(vieww)
nviews = 0


# This class holds methods for menu/actions callbacks, and utility functions
# like load/view objects, remove/delete, etc.
class AnaSimpleViewer(Qt.QObject):

    def __init__(self):
        Qt.QObject.__init__(self)
        self.filedialogdir = '.'

    def createWindow(self, wintype='Axial'):
        '''Opens a new window in the windows grid layout.
        The new window will be set in MNI referential, and have no
        menu/toolbars.
        '''
        global vieww, nviews
        x = nviews % 2
        y = nviews // 2
        nviews += 1

        w = a.createWindow(wintype, no_decoration=True, options={'hidden': 1})
        w.setAcceptDrops(False)
        viewgridlay.addWidget(w.getInternalRep(), x, y)

        # keep it in anasimpleviewer list of windows
        awindows.append(w)
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

    def addVolume(self, obj, opts={}):
        '''Display a volume in all windows.
        If several volumes are displayed, a Fusion2D will be built to wrap all of
        them.
        '''
        global fusion2d
        if obj in fusion2d:
            return
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
            if 'volume_contents_likelihoods' in obj.attributed()['colormaphints']:
                cmap = colormaphints.chooseColormaps(
                    (obj.attributed()['colormaphints'], ))
                obj.setPalette(cmap[0])
        else:
            # choose good colormaps for the current set of volumes
            hints = [x.attributed()['colormaphints'] for x in obj.children]
            children = [x for x, y in zip(obj.children, hints)
                        if 'volume_contents_likelihoods' in y]
            hints = [x for x in hints
                     if 'volume_contents_likelihoods' in x]
            cmaps = colormaphints.chooseColormaps(hints)
            for x, y in zip(children, cmaps):
                x.setPalette(y)
        a.addObjects(obj, awindows, **opts)

    def removeVolume(self, obj, opts={}):
        '''Hides a volume from views (low-level function: use removeObject)
        '''
        global fusion2d
        if obj in fusion2d:
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
            a.addObjects(obj, awindows, **opts)

    def addObject(self, obj):
        '''Display an object in all windows
        '''
        opts = {}
        if obj.objectType == 'VOLUME':
            # volumes have a specific function since several volumes have to be
            # fusionned, and a volume rendering may occur
            self.addVolume(obj, opts)
            return
        elif obj.objectType == 'GRAPH':
            opts['add_graph_nodes'] = 1
        a.addObjects(obj, awindows, **opts)

    def removeObject(self, obj):
        '''Hides an object from views
        '''
        if obj.objectType == 'VOLUME':
            self.removeVolume(obj)
        else:
            a.removeObjects(obj, awindows, remove_children=True)

    def fileOpen(self):
        '''File browser + load object(s)
        '''
        fdialog = Qt.QFileDialog()
        fdialog.setDirectory(self.filedialogdir)
        fdialog.setFileMode(fdialog.ExistingFiles)
        res = fdialog.exec_()
        if res:
            fnames = fdialog.selectedFiles()
            self.filedialogdir = fdialog.directory()
            for fname in fnames:
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
                                                     Qt.Qt.MatchExactly)[0]))
        global aobjects
        aobjects = [o for o in aobjects if o not in objs]
        a.deleteObjects(objs)

    def closeAll(self):
        '''Exit'''
        print("Exiting")
        global vieww, awindows, fusion2d, aobjects, anasimple
        global awin, viewgridlay
        # remove windows from their parent to prevent them to be brutally
        # deleted by Qt.
        w = None  # ensure there is a w variable before the "del" later
        for w in awindows:
            w.hide()
            viewgridlay.removeWidget(w.internalRep._get())
            w.setParent(None)
        del w
        del viewgridlay, vieww
        del anasimple
        del awindows, fusion2d, aobjects
        awin.close()
        del awin
        a = ana.Anatomist()
        a.close()


# instantiate the machine
anasimple = AnaSimpleViewer()
# connect GUI actions callbacks
findChild(awin, 'fileOpenAction').triggered.connect(anasimple.fileOpen)
findChild(awin, 'fileExitAction').triggered.connect(anasimple.closeAll)
findChild(awin, 'editAddAction').triggered.connect(anasimple.editAdd)
findChild(awin, 'editRemoveAction').triggered.connect(anasimple.editRemove)
findChild(awin, 'editDeleteAction').triggered.connect(anasimple.editDelete)

# display on the whole screen
awin.showMaximized()

# tweak: override some user config options
a.config()['setAutomaticReferential'] = 1
a.config()['windowSizeFactor'] = 1.

# run Qt
if __name__ == '__main__':
    #run_qt = False
    if not 'sphinx_gallery' in sys.modules and run_qt:
        Qt.QApplication.instance().exec_()
    elif 'sphinx_gallery' in sys.modules:
        # load a data
        awin.showNormal()
        awin.resize(1000, 700)  # control the size of the snapshot
        anasimple.loadObject('irm.ima')
        # these 2 events ensure things are actually drawn
        Qt.QApplication.instance().processEvents()
        Qt.QApplication.instance().processEvents()
        # snapshot the whole widget
        if Qt.QT_VERSION >= 0x050000:
            ws = awin.grab()  # Qt5 only
        else:
            ws = Qt.QPixmap.grabWidget(awin)  # Qt4 only
        # openGl areas are not rendered in the snapshot, we have to make them
        # by hand
        p = Qt.QPainter(ws)
        for w in awindows:
            s = w.snapshotImage()
            # draw the GL rendering into the image (pixmap)
            p.drawImage(w.mapTo(awin, Qt.QPoint(0, 0)), s)
        del w, s, p
        # snapshot to matplotlib
        import matplotlib
        #backend = matplotlib.get_backend()
        matplotlib.use('agg', force=True, warn=False)  # force agg
        from matplotlib import pyplot
        im = qt_backend.qimage_to_np(ws)
        plot = pyplot.imshow(im)
        axes = pyplot.axes()
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)
        pyplot.show(block=False)
        # matplotlib.use(backend, force=True)  # restore backend

    if run_qt or 'sphinx_gallery' in sys.modules:
        anasimple.closeAll()
