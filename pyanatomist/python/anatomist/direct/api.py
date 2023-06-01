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

"""
This module is an implementation of the general interface :mod:`anatomist.base`.
It uses Sip bindings of C++ Anatomist api to execute and drive Anatomist application.

This is the default implementation. So, to use it you just have to import anatomist.api, it is automatically linked to this module.

>>> import anatomist.api as anatomist
>>> a = anatomist.Anatomist()


Objects created via this module encapsulate sip bindings of C++ Anatomist api objects (Sip binding classes are in module anatomist.cpp).
This implementation provides additional features  to those in the general interface because it gives access to the bound C++ objects, and potentially the whole Anatomist library is available, includind direct manipulation and modification of objects in memory using low-level operations.
But Anatomist program is loaded in current process so if it fails, the current process also fails and possibly crashes, so it is more dangerous.

This implementation needs to run qt application.
In an interactive python shell, this can be done using ``ipython --gui=qt`` for example.
If the Anatomist object is created outside the main thread, you must get a thread safe version (See :py:mod:`anatomist.threaded.api`). So you have to change the default implementation before importing anatomist api :

>>> import anatomist
>>> anatomist.setDefaultImplementation(anatomist.THREADED)
>>> import anatomist.api as anatomist

"""
from __future__ import print_function

from __future__ import absolute_import
from anatomist import cpp
from anatomist import base
import operator
from soma import aims
from soma.qt_gui import qt_backend
import os
import sys
import types
import weakref
import sys
import numpy as np
import six
from anatomist.base import isSequenceType, isMappingType

try:
    from soma.qt_gui.qt_backend.QtCore import QString
    _string_or_qstring = (six.string_types, QString)
except ImportError:
    _string_or_qstring = (six.string_types, )
from soma.qt_gui.qt_backend import QtCore, Qt
Slot = QtCore.pyqtSlot


version = cpp.Anatomist.version()


class Anatomist(base.Anatomist, cpp.Anatomist):

    """
    Interface to communicate with an Anatomist Application using direct bindings to the C++ api.
    It inherits from Anatomist class of :py:mod:`anatomist.cpp` module (Sip bindings module).

    Attributes
    ----------
    centralRef: :class:`Referential`
        Anatomist central referential (talairach acpc ref)
    mniTemplateRef: :class:`Referential`
        Referential of the MNI template (used by spm and other software)

        These two referentials and transformation between them are always loaded in anatomist.

    handlers: dict
        Registered handlers for events. name of the event (string) -> event handler (:class:`Anatomist.AEventHandler`). Handlers must be stored to enable unregistration.
    """

    def __singleton_init__(self, *args, **kwargs):
        # call C++ constructor now with all arguments, otherwise it will be called
        # via Singleton.__init__ without arguments.
        self.context = cpp.CommandContext.defaultContext()
        self.handlers = {}
        self._loadCbks = set()
        global __version__
        cpp.Anatomist.__init__(self, *args, **kwargs)
        super(Anatomist, self).__singleton_init__(*args, **kwargs)
        from soma.qt_gui.qt_backend import QtGui
        import threading
        self.log("Anatomist started.")

    def __del__(self):
        # quit the app and delete it
        # (avoid calling the overload of __getattr__ here)
        s = super()
        quit = s.__getattribute__('quit')
        quit()
        if hasattr(s, '__del__'):
          s.__del__()


    class AEventHandler(cpp.EventHandler):

        """
        Anatomist event handler class. When an event is received, the corresponding notifier triggered and a message is logged.
        """

        def __init__(self, notifier, anatomistinstance):
            """
            Parameters
            ----------
            notifier: :class:`soma.notification.Notifier`
                The notifier to activate when the event occurs.
            anatomistinstance: :class:`Anatomist`
            """

            cpp.EventHandler.__init__(self)
            self.notifier = notifier
            self.anatomistinstance = weakref.proxy(anatomistinstance)

        def doit(self, event):
            """
            This method is called when the event occurs.
            """
            eventName = event.eventType()
            data = event.contents()
            # event content is a GenericObject, it
            # contains values associated with keys as a
            # dictionary. But the values are
            # GenericObject too, no python objects. So it
            # must be converted in python.
            dataDict = {}
            for k in data.keys():  # get all parameters in a dictionary, except private parameters (beginning with _)
                if k[0] != "_":
                    dataDict[k] = data[k]
            params = dataDict
            # then object's or window identifiers will be replaced by
            # corresponding objects but before log the value (objects cannot be
            # logged, identifier can)
            self.anatomistinstance.logEvent(eventName, str(params))
            o = params.get('object')
            if o is not None:  # get the object by identifier and create a AObject representing it
                params['object'] = self.anatomistinstance.typedObject(
                    self.anatomistinstance.context.object(o))
            w = params.get('window')
            if w is not None:
                params['window'] = self.anatomistinstance.AWindow(
                    self.anatomistinstance, self.anatomistinstance.context.object(w))
            ch = params.get('children')  # list of AObject
            if ch is not None:
                chObj = []
                for c in ch:
                    chObj.append(self.anatomistinstance.typedObject(
                        self.anatomistinstance.context.object(c)))
                params['children'] = chObj
            self.notifier.notify(eventName, params)

    def enableListening(self, event, notifier):
        """
        Set listening of this event on. So when the event occurs, the notifier's notify method is called.
        This method is automatically called when the first listener is added to a notifier. That is to say that notifiers are activated only if they have registered listeners.

        Parameters
        ----------
        event: str
            Name of the event to listen
        notifier: :class:`soma.notification.Notifier`
            The notifier whose notify method must be called when this event occurs
        """
        self.context.evfilter.filter(event)
        handler = self.AEventHandler(notifier, self)
        self.handlers[event] = handler
        cpp.EventHandler.registerHandler(event, handler)

    def disableListening(self, event):
        """
        Set listening of this event off.

        Parameters
        ----------
        event: str
            Name of the event to disable.
        """
        self.context.evfilter.unfilter(event)
        cpp.EventHandler.unregisterHandler(event, self.handlers[event])
        del self.handlers[event]

    #
    # Methods inherited from base.Anatomist

    def close(self):
        # in direct implementation cleanup the internal variables
        self.quit()

    # objects creation
    def createWindowsBlock(self, nbCols=2, nbRows=0, widget=None):
        """
        Creates a window containing other windows.

        An id is reserved for that block but the bound object isn't created. It will be created first time a window is added to the block with createWindow method.

        Parameters
        ----------
        nbCols: int
            Number of columns of the windows block
        nbRows: int
            Number of rows of the windows block (exclusive with nbCols)
        widget: QWidget (optional)
            New in Anatomist 4.6.2, only applies to the direct implementation.
            Existing parent widget to be used as a block

        Returns
        -------
        block: :class:`AWindowsBlock`
            A window which can contain several :class:`AWindow`
        """
        if nbRows:
            nbCols = 0
        block = self.AWindowsBlock(self, nbCols=nbCols, nbRows=nbRows)
        if widget is not None:
            block.setWidget(widget)
        return block

    def createWindow(self, wintype, geometry=[], block=None,
                     no_decoration=None, options=None):
        """
        Creates a new window and opens it.

        Parameters
        ----------
        wintype: str
            Type of window to open (``"Axial"``, ``"Sagittal"``, ``"Coronal"``, ``"3D"``, ``"Browser"``, ``"Profile"``, ...)
        geometry: int vector
            Position on screen and size of the new window (x, y, w, h)
        block: :class:`AWindowsBlock` or QWidget
            A parent block in which the new window must be added.
            In Anatomist 4.6.2 and later, the block may be a regular QWidget
            (this is only OK in direct implementation mode)
        no_decoration: bool
            Indicates if decorations (menus, buttons) can be painted around the
            view.
        options: dict
            Internal advanced options.

        Returns
        -------
        window: :class:`AWindow`
            The newly created window
        """
        if geometry is None:
            geometry = []
        # options=None
        if no_decoration:
            if not options:
                options = {'__syntax__': 'dictionary', 'no_decoration': 1}
            else:
                options['__syntax__'] = 'dictionary'
                options['no_decoration'] = 1

        if block is not None:
            # CreateWindowCommand(type, id, context, geometry, blockid, block,
            # block_columns, options)
            bwid = None
            bid = -1
            if isinstance(block, Qt.QWidget):
                block = self.createWindowsBlock(widget=block)
            if block.internalWidget is not None:
                bwid = block.internalWidget.widget
            bid = block.getInternalRep()

            c = cpp.CreateWindowCommand(
                wintype, -1, None, geometry, bid, bwid, block.nbCols,
                block.nbRows, aims.Object(options))
            self.execute(c)
            if block.internalWidget is None:
                block.setWidget(c.block())
        else:
            c = cpp.CreateWindowCommand(
                wintype, -1, None, geometry, 0,  None, 0, 0,
                aims.Object(options))
            self.execute(c)
        # use a WeakShared reference type because AWindows are also QWidgets,
        # which can have parents, and can be destroyed by parent widgets within
        # Qt mechanisms that we cannot prevent.
        w = self.AWindow(self, c.createdWindow(), refType='WeakShared')
        w.releaseAppRef()
        w.block = block
        return w

    def loadObject(self, filename, objectName="", restrict_object_types=None,
                   forceReload=True, duplicate=False, hidden=False,
                   asyncCallback=None):
        """
        Loads an object from a file (volume, mesh, graph, texture...)

        Parameters
        ----------
        filename: str
            The file containing object data
        objectName: str
            Object name
        restrict_object_types: dict
            object -> accpepted types list. Ex: ``{'Volume' : ['S16', 'FLOAT']}``
        forceReload: bool
            If *True*, the object will be loaded even if it is already loaded in Anatomist. Otherwise, the already loaded one is returned.
        duplicate: bool
            If the object already exists, duplicate it. The original and the copy will share the same data but not display parameters as palette. If the object is not loaded yet, load it hidden and duplicate it (unable to keep the original object with default display parameters).
        hidden: bool
            A hidden object does not appear in Anatomist main control window.

        Returns
        -------
        object: :class:`AObject`
            The loaded object
        """
        # LoadObjectCommand(filename, id, objname, ascursor, options, context)
        if not forceReload:  # do not load the object if it is already loaded
            object = self.getObject(filename)
            if object is not None:  # object is already loaded
                files = [filename, filename + '.minf']
                for f in files:
                    if os.path.exists(f):
                        # reload it if the file has been modified since last load
                        if os.stat(f).st_mtime >= object.loadDate:
                            self.reloadObjects([object])
                            break
                if duplicate:
                    return self.duplicateObject(object)
                if not hidden:
                    # must show the object if it was hidden
                    self.showObject(object)
                return object
        # if forceReload or object is not already loaded
        if duplicate:
            hidden = True
        if objectName is None:  # Command constructor doesn't support None value for this parameter
            objectName = ""
        options = None
        if restrict_object_types is not None or hidden or asyncCallback:
            options = {'__syntax__': 'dictionary'}
            if restrict_object_types:
                restrict_object_types['__syntax__'] = 'dictionary'
                options['restrict_object_types'] = restrict_object_types
            if hidden:
                options['hidden'] = 1
            if asyncCallback:
                options['asynchronous'] = True
        c = cpp.LoadObjectCommand(filename, -1, objectName, False,
                                  aims.Object(options))
        if asyncCallback:
            cbk = self._ObjectLoaded(self, duplicate, asyncCallback, filename)
            self._loadCbks.add(cbk)
            c.objectLoaded.connect(cbk.loaded)
        self.execute(c)
        if not asyncCallback:
            objs = c.loadedObjects()
            objects = []
            for obj in objs:
                o = self.typedObject(obj)
                objects.append(o)
                o.releaseAppRef()
                if duplicate:
                    # the original object has been loaded hidden, duplicate it
                    copyObject = self.duplicateObject(o)
                    return copyObject
            if len(objects) == 1:
                return objects[0]
            elif len(objects) == 0:
                return None
            return objects

    class _ObjectLoaded(object):

        '''internal.'''

        def __init__(self, anatomistinstance, duplicate, callback, filename):
            self.anatomistinstance = anatomistinstance
            self.duplicate = duplicate
            self.callback = callback
            self.filename = filename

        def loaded(self, obj, filename):
            self.anatomistinstance._loadCbks.remove(self)
            if obj is None:
                self.callback(None, filename)
            else:
                o = self.anatomistinstance.typeObject(obj)
                o.releaseAppRef()
                if self.duplicate:
                    # the original object has been loaded hidden, duplicate it
                    o = self.anatomistinstance.duplicateObject(o)
                self.callback(o, filename)

    def duplicateObject(self, source, shallowCopy=True):
        """
        Creates a copy of source object.

        Parameters
        ----------
        source: :class:`AObject`
            The object to copy.

        Returns
        -------
        object: :class:`AObject`
            The copy. it has a reference to its source object, so original object will not be deleted as long as the copy exists.
        """
        newObjectId = self.newId()
        if shallowCopy:
            shallowCopy = 1
        else:
            shallowCopy = 0
        self.execute("DuplicateObject", source=source, res_pointer=newObjectId,
                     shallow=shallowCopy)
        cObject = self.context.object(newObjectId)
        if cObject is not None:
            newObject = self.typedObject(cObject)
            newObject.releaseAppRef()
            newObject.source = source
            return newObject
        return source

    def createGraph(self, object, name=None, syntax=None, filename=None):
        """
        Creates a graph associated to an object (volume for example). This object initializes the graph dimensions (voxel size, extrema).

        Parameters
        ----------
        object: :class:`AObject`
            The new graph is based on this object
        name: str
            Graph name. default is ``'RoiArg'``.
        syntax: str
            Graph syntactic attribute. default is ``'RoiArg'``.
        filename: str
            Filename used for saving. Default is *None*.

        Returns
        -------
        graph: :class:`AGraph`
            The new graph object
        """
        newGraphId = self.newId()
        self.execute("CreateGraph", object=object, res_pointer=newGraphId,
                     name=name, syntax=syntax, filename=filename)
        newGraph = self.AGraph(self, self.context.object(newGraphId))
        newGraph.releaseAppRef()
        return newGraph

    def typedObject(self, obj):
        """
        Get :class:`AObject` or a subclass from a sip object when it is possible.

        Returns
        -------
        object: :class:`AObject`
        """
        # print '==== pyanatomist::typedObject, obj:', obj
        if isinstance(obj, base.Anatomist.AObject):
            return obj

        else:
            # print'==== pyanatomist::typedObject, type:', obj.type()
            typename = obj.objectTypeName(obj.type())
            # print '==== pyanatomist::typedObject, typename:', typename
            if typename == 'GRAPH':
                o = self.AGraph(self, obj)

            else:
                o = self.AObject(self, obj)

            return o

    def toAObject(self, object):
        """
        Converts an AIMS object or numpy array to AObject.

        Returns
        -------
        aobject: :class:`AObject`
        """
        bobject = cpp.AObjectConverter.anatomist(object)
        return self.typedObject(bobject)

    def toAimsObject(self, object):
        """
        Converts an :class:`AObject` to an AIMS object.

        Parameters
        ----------
        object: :class:`AObject`
            The object to convert

        Returns
        -------
        aims: various types
            The underlying converted AIMS object
        """
        return cpp.AObjectConverter.aims(object.getInternalRep())

    def loadCursor(self, filename):
        """
        Loads a cursor for 3D windows from a file.

        Parameters
        ----------
        filename: str
            The file containing object data

        Returns
        -------
        cursor: :class:`AObject`
            The loaded object
        """
        c = cpp.LoadObjectCommand(filename, -1, "", True)
        self.execute(c)
        if len(c.loadedObjects()) == 0:
            raise IOError('file %s cannot be read' % filename)
        o = self.typedObject(c.loadedObjects()[0])
        o.releaseAppRef()
        return o

    def fusionObjects(self, objects, method="", ask_order=False):
        """
        Creates a fusionned multi object that contains all given objects.

        Parameters
        ----------
        objects: list of :class:`AObject`
            List of objects that must be fusionned
        method: str
            Method to apply for the fusion (``'Fusion2DMethod'``...)
        ask_order: bool
            If *True*, asks user in which order the fusion must be processed.

        Returns
        -------
        object: :class:`AObject`
            The newly created fusion object.
        """
        if method is None:
            method = ""
        bObjects = self.convertParamsToObjects(objects)
        bObjects = [x for x in bObjects if x is not None]
        c = cpp.FusionObjectsCommand(
            self.makeList(bObjects), method, -1, ask_order)
        # force execution now
        ah = self.theProcessor().execWhileIdle()
        self.theProcessor().allowExecWhileIdle(True)
        self.execute(c)
        self.theProcessor().allowExecWhileIdle(ah)
        o = c.createdObject()
        if o is not None:
            o = self.typedObject(c.createdObject())
            o.releaseAppRef()
        return o

    def getFusionInfo(self, objects=None):
        """
        Gets information about fusion methods. If objects is not specified, the global list of all fusion methods is returned. Otherwise the allowed fusions for those specific objects is returned.

        Returns
        -------
        methods: dict
            Fusion methods
        """
        if objects is None:
            return {'all_methods': list(cpp.FusionFactory.methods())}
        else:
            bObjects = self.convertParamsToObjects(objects)
            return {'allowed_methods':
                    list(cpp.FusionFactory.factory().allowedMethods(bObjects))}

    def createReferential(self, filename=""):
        """
        This command does not exist in Anatomist because the command AssignReferential can create a new referential if needed.
        But the way of creating a new referential depends on the connection with Anatomist,
        so it seems to be better to encapsulate this step on another command. So referentials are treated the same as other objects.
        (LoadObject -> addAobject | createReferential -> assignReferential)

        Parameters
        ----------
        filename: str
            Name of a file (``minf`` file, extension ``.referential``) containing  information about the referential: its name and uuid

        Returns
        -------
        ref: :class:`Referential`
            The newly created referential
        """
        if filename is None:
            filename = ""
        c = cpp.AssignReferentialCommand(None, [], [], -1, None, filename)
        self.execute(c)
        return self.Referential(self, c.ref())

    def loadTransformation(self, filename, origin, destination):
        """
        Loads a transformation from a referential to another. The transformation informations are given in a file.

        Parameters
        ----------
        filename: str
            File containing transformation information
        origin: :class:`Referential`
            Origin of the transformation
        destination: :class:`Referential`
            Referential after applying transformation

        Returns
        -------
        trans: :class:`Transformation`
            Transformation to apply to convert coordinates from one referent
        """
        if hasattr(origin, 'getInternalRep'):
            origin = origin.getInternalRep()
        if hasattr(destination, 'getInternalRep'):
            destination = destination.getInternalRep()
        c = cpp.LoadTransformationCommand(filename, origin, destination)
        self.execute(c)
        return self.Transformation(self, c.trans())

    def createTransformation(self, matrix, origin, destination):
        """
        Creates a transformation from a referential to another. The transformation informations are given in a matrix.

        Parameters
        ----------
        matrix: float vector, size 12
            Transformation matrix (4 lines, 3 colons ; 1st line: translation, others: rotation)
        origin: :class:`Referential`
            Origin of the transformation
        destination: :class:`Referential`
            Referential after applying transformation

        Returns
        -------
        trans: :class:`Transformation`
            New transformation
        """
        if hasattr(origin, 'getInternalRep'):
            origin = origin.getInternalRep()
        if hasattr(destination, 'getInternalRep'):
            destination = destination.getInternalRep()
        c = cpp.LoadTransformationCommand(matrix, origin, destination)
        self.execute(c)
        return self.Transformation(self, c.trans())

    def createPalette(self, name):
        """
        Creates an empty palette and adds it in the palettes list.

        Parameters
        ----------
        name: str
            Name of the new palette

        Returns
        -------
        palette: :class:`APalette`
            The newly created palette
        """
        c = cpp.NewPaletteCommand(name)
        self.execute(c)
        return self.getPalette(name)

    def groupObjects(self, objects):
        """
        Creates a multi object containing objects in parameters.

        Parameters
        ----------
        objects: list of :class:`AObject`
            Objects to put in a group

        Returns
        -------
        group: :class:`AObject`
            The newly created multi object
        """
        bObjects = self.convertParamsToObjects(objects)
        c = cpp.GroupObjectsCommand(self.makeList(bObjects))
        self.execute(c)
        return self.typedObject(c.groupObject())

    #
    # objects access
    def __getattr__(self, name):
        """
        Called when trying to access to name attribute, which is not defined.
        Used to give a value to centralRef attribute first time it is accessed.
        """
        if name == "centralRef":
            self.centralRef = self.Referential(self, self.centralReferential())
            return self.centralRef
        elif name == "mniTemplateRef":
            self.mniTemplateRef = self.Referential(self,
                                                   cpp.Referential.mniTemplateReferential())
            return self.mniTemplateRef
        else:
            raise AttributeError(name)

    def __getattribute__(self, name):
        '''
        __getattribute__ is overloaded in Anatomist.direct.api:
        the aim is to intercept calls to the C++ API and convert return
        values which contain C++ instances to their corresponding wrapper in
        the Anatomist.direct implementation: AObject, AWindow, Referential,
        Transformation instances are converted.
        Drawback: all return values which are lists or dictionaries are copied.
        '''
        att = super(Anatomist, self).__getattribute__(name)
        if callable(att):
            if type(att).__name__ == 'builtin_function_or_method':
                conv = super(Anatomist, self).__getattribute__(
                    'convertParamsToAItems')
                return lambda *args, **kwargs: conv(att(*args, **kwargs))
        return att

    def _getAttributeNames(self):
        '''IPython completion feature...'''
        m = ['centralRef', 'mniTemplateRef']
        l = [self]
        done = set()
        while l:
            c = l.pop()
            done.add(c)
            m += [x for x in list(c.__dict__.keys())
                  if not x.startswith('_') and x not in m]
            cl = getattr(c, '__bases__', None)
            if not cl:
                cl = getattr(c, '__class__', None)
                if cl is None:
                    continue
                else:
                    cl = [cl]
            l += [x for x in cl if x not in done]
        return m

    def getPalette(self, name):
        """
        Returns
        -------
        palette: :class:`APalette`
            The named palette
        """
        pal = self.palettes().find(name)
        if pal.isNull():
            pal = None
        else:
            pal = self.APalette(name, self, pal)
        return pal

    # information that can be obtained with GetInfo command
    def getObjects(self):
        """
        Gets all objects referenced in current context.

        Returns
        -------
        objects: list of :class:`AObject`
            List of existing objects
        """
        boundObjects = cpp.Anatomist.getObjects(self)
        objects = []
        for o in boundObjects:
            objects.append(self.typedObject(o))
        return objects

    def importObjects(self, top_level_only=False):
        """
        Gets objects importing those that are not referenced in the current
        context.

        Parameters
        ----------
        top_level_only: bool
            If *True*, imports only top-level objects (that have no parents), else all objects are imported.

        Returns
        -------
        objects: list of :class:`AObject`
            List of existing objects
        """
        return self.getObjects()

    def getWindows(self):
        """
        Gets all windows referenced in current context.

        Returns
        -------
        windows: list of :class:`AWindow`
            List of opened windows
        """
        boundWindows = cpp.Anatomist.getWindows(self)
        windows = []
        for w in boundWindows:
            windows.append(self.AWindow(self, w))
        return windows

    def importWindows(self):
        """
        Gets all windows importing those that are not referenced in the current
        context.

        Returns
        -------
        windows: list of :class:`AWindow`
            List of opened windows
        """
        return self.getWindows()

    def getReferentials(self):
        """
        Gets all referentials in current context.

        Returns
        -------
        refs: list of :class:`Referential`
            List of referentials
        """
        boundRefs = cpp.Anatomist.getReferentials(self)
        refs = []
        for r in boundRefs:
            refs.append(self.Referential(self, r))
        return refs

    def importReferentials(self):
        """
        Gets all referentials importing those that are not referenced in the
        current context.

        Returns
        -------
        refs: list of :class:`Referential`
            List of referentials
        """
        return self.getReferentials()

    def getTransformations(self):
        """
        Gets all transformations.

        Returns
        -------
        trans: list of :class:`Transformation`
            List of transformations
        """
        boundTrans = cpp.Anatomist.getTransformations(self)
        trans = []
        for t in boundTrans:
            trans.append(self.Transformation(self, t))
        return trans

    def importTransformations(self):
        """
        Gets all transformations importing those that are not referenced in the
        current context.

        Returns
        -------
        trans: list of :class:`Transformation`
            List of transformations
        """
        return self.getTransformations()

    def getPalettes(self):
        """
        Returns
        -------
        palettes: list of :class:`APalette`
            List of palettes.
        """
        paletteList = self.palettes().palettes()
        palettes = []
        for p in paletteList:
            palettes.append(self.APalette(p.name(), self, p))
        return palettes

    def getSelection(self, group=None):
        """
        Parameters
        ----------
        group: :class:`AWindowsGroup`
            Get the selection in this group. If *None*, returns the selection in the default group.

        Returns
        -------
        objects: list of :class:`AObject`
            The list of selected objects in the group of windows
        """
        selections = cpp.SelectFactory.factory().selected()
        if group is None:
            group = 0
        elif isinstance(group, Anatomist.AWindowsGroup):
            group = group.internalRep
        elif type(group) != int:
            raise TypeError('Incorrect parameter type : group')
        objects = selections.get(group)
        l = []
        if objects is not None:
            for o in objects:
                l.append(self.typedObject(o))
        return l

    def linkCursorLastClickedPosition(self, ref=None):
        """
        Gives the last clicked position of the cursor.

        Parameters
        ----------
        ref: :class:`Referential`
            If given, cursor position value will be in this referential. Else, anatomist central referential is used.

        Returns
        -------
        position: float vector, size 3
            Last position of the cursor
        """
        if ref is not None:
            return self.lastPosition(ref.internalRep)
        else:
            return self.lastPosition()

    def getAimsInfo(self):
        """
        Returns
        -------
        info: str
            Information about the AIMS library.
        """
        p = self.theProcessor()
        resetProcExec = False
        if not p.execWhileIdle():
            # allow recursive commands execution, otherwise the execute()
            # may not be done right now
            p.allowExecWhileIdle(True)
            resetProcExec = True
        command = self.execute("GetInfo", aims_info=1)
        result = command.result()
        if resetProcExec:
            # set back recursive execution to its previous state
            p.allowExecWhileIdle(False)
        return result['aims_info']

    def getCommandsList(self):
        """
        Returns
        -------
        commands: dict
            Dict of commands available in Anatomist with their parameters.
            dict command name -> dict parameter name -> dict attribute -> value (needed, type)
        """
        p = self.theProcessor()
        resetProcExec = False
        if not p.execWhileIdle():
            # allow recursive commands execution, otherwise the execute()
            # may not be done right now
            p.allowExecWhileIdle(True)
            resetProcExec = True
        command = self.execute("GetInfo", list_commands=1)
        result = command.result()
        if resetProcExec:
            # set back recursive execution to its previous state
            p.allowExecWhileIdle(False)
        return result['commands']

    def getModulesInfo(self):
        """
        Returns
        -------
        info: dict
            Dict of modules and their description. dict module name -> dict attribute -> value (description)
        """
        p = self.theProcessor()
        resetProcExec = False
        if not p.execWhileIdle():
            # allow recursive commands execution, otherwise the execute()
            # may not be done right now
            p.allowExecWhileIdle(True)
            resetProcExec = True
        command = self.execute("GetInfo", modules_info=1)
        result = command.result()
        if resetProcExec:
            # set back recursive execution to its previous state
            p.allowExecWhileIdle(False)
        return result['modules']

    def getVersion(self):
        """
        Returns
        -------
        version: str
            Anatomist version
        """
        p = self.theProcessor()
        resetProcExec = False
        if not p.execWhileIdle():
            # allow recursive commands execution, otherwise the execute()
            # may not be done right now
            p.allowExecWhileIdle(True)
            resetProcExec = True
        command = self.execute("GetInfo", version=1)
        result = command.result()
        if resetProcExec:
            # set back recursive execution to its previous state
            p.allowExecWhileIdle(False)
        return result['anatomist_version']

    #
    # objects manipulation
    def addObjects(self, objects, windows, add_children=False,
                   add_graph_nodes=True, add_graph_relations=False, temporary=False,
                   position=-1):
        """
        Adds objects in windows.
        The objects and windows must already exist.

        Parameters
        ----------
        objects: list of :class:`AObject`
            List of objects to add
        windows: list of :class:`AWindow`
            List of windows in which the objects must be added
        add_children: bool (optional)
            if children objects should also be added individually after their
            parent
        add_graph_relations: bool (optional)
            if graph relations should be also be added
        temporary: bool (optional)
            temporary object do not affect the view boundaries and camera settings
        position: int (optional)
            insert objects as this order number
        """
        bObjects = self.convertParamsToObjects(objects)
        bWindows = self.convertParamsToObjects(windows)
        c = cpp.AddObjectCommand(
            self.makeList(bObjects), self.makeList(bWindows),
            add_children, add_graph_nodes, add_graph_relations, temporary, position)
        self.execute(c)

    def removeObjects(self, objects, windows, remove_children=False):
        """
        Removes objects from windows.

        Parameters
        ----------
        objects: list of :class:`AObject`
            List of objects to remove
        windows: list of :class:`AWindow`
            List of windows from which the objects must be removed
        """
        bObjects = self.convertParamsToObjects(objects)
        bWindows = self.convertParamsToObjects(windows)
        c = cpp.RemoveObjectCommand(
            self.makeList(bObjects), self.makeList(bWindows),
            int(remove_children))
        self.execute(c)

    def assignReferential(self, referential, elements):
        """
        Assign a referential to objects and/or windows.
        The referential must exist. To create a new Referential, execute createReferential,
        to assign the central referential, first get it with Anatomist.centralRef attribute.

        Parameters
        ----------
        referential: :class:`Referential`
            The referential to assign to objects and/or windows
        elements: list of :class:`AObject` / :class:`AWindow`
            Objects or windows which referential must be changed.
            The corresponding command tree contains an attribute central_ref to indicate if the referential to assign is anatomist central ref,
            because this referential isn't referenced by an id. In the socket implementation, Referential object must have an attribute central_ref,
            in order to create the command message. In direct impl, it is possible to access directly to the central ref object.
        """
        objects = []
        windows = []
        # in anatomist command, objects and windows must be passed in two lists
        for e in self.makeList(elements):
            if isinstance(e, base.Anatomist.AObject):
                objects.append(e.getInternalRep())
            elif isinstance(e, base.Anatomist.AWindow):
                windows.append(e.getInternalRep())
        referential = getattr(referential, 'internalRep', None) or referential
        c = cpp.AssignReferentialCommand(referential, objects, windows)
        self.execute(c)

    #
    def execute(self, command, **kwargs):
        """
        Executes a command in anatomist application. It should be a command that can be processed by Anatomist command processor.
        The list of available commands is in
        :anadev:`the commands system <commands.html>`.
        Parameters are converted before sending the request to anatomist
        application.

        Parameters
        ----------
        command: str
            Name of the command to execute.
        kwargs: dict
            Parameters for the command
        """

        def ununderscore(k):
            # this removes a trailing '_' from params names
            # it allows to used reserved words as params, like raise, by appending
            # an underscore, like in PyQt4:
            # a.execute( 'WindowConfig', windows=[w], raise_=1 )
            if k.endswith('_'):
                return k[:-1]
            return k
        params = dict((ununderscore(k), self.convertParamsToIDs(v)) for k, v
                      in six.iteritems(kwargs) if v is not None)
        self.logCommand(command, **params)
        return self.theProcessor().execute(command, **params)

    def convertSingleObjectParamsToIDs(self, v):
        """
        Converts current api object to corresponding anatomist object
        representation.

        Parameters
        ----------
        v: :class:`AItem` instance
            Element to convert

        Returns
        -------
        *dictionary* or *list*
            Converted elements
        """
        if isinstance(v,  base.Anatomist.AItem):
            v = v.getInternalRep()
        if isinstance(v, cpp.APalette):
            return v.name()
        if isinstance(v, cpp.AObject) or isinstance(v, cpp.AWindow) \
                or isinstance(v, cpp.Transformation) or isinstance(v, cpp.Referential):
            try:
                i = self.context.id(v)
            except:
                i = self.context.makeID(v)
            return i
        elif isinstance(v, (six.string_types, int, float, dict,
                            np.int16, np.int32, np.int64, np.int8,
                            np.uint16, np.uint32, np.uint64, np.uint8,
                            np.float16, np.float32, np.float64,
                            np.float128)):
            return v
        raise TypeError('Expecting an Anatomist object but got one of type %s'
                        % repr(type(v)))

    def convertSingleObjectParamsToObjects(self, v):
        """
        Converts current api object to corresponding anatomist C++ object representation.

        Parameters
        ----------
        v: :class:`AItem`
            Element to convert

        Returns
        -------
        objects: dict or list
            Converted elements
        """
        if isinstance(v,  base.Anatomist.AItem):
            return v.getInternalRep()
        return v

    def convertParamsToObjects(self, params):
        """
        Converts current api objects to corresponding anatomist object representation.
        This method must be called before sending a command to anatomist application on command parameters.

        Parameters
        ----------
        params: dict or list
            Elements to convert

        Returns
        -------
        objects: dict or list
            Converted elements
        """
        if not isinstance(params, six.string_types) \
                and isSequenceType(params):
            return [self.convertSingleObjectParamsToObjects(i) for i in params]
        else:
            return self.convertSingleObjectParamsToObjects(params)

    def getAItem(self, idorcpp, convertIDs=True, allowother=True):
        """
        Converts a C++ API objects or context IDs to a generic API object.

        Parameters
        ----------
        idorcpp: ID or C++ instance to be converted
            If *idorcpp* is already an :class:`AItem`, it is returned as is
        convertIDs: bool
            If *True*, int numbers are treated as item IDs and
            converted accordingly when possible.
        allowother: bool
            If *True*, *idorcpp* is returned unchanged if not recognized

        Returns
        -------
        aitem: :class:`AItem` instance, or *None* (or the unchanged input if allowother is *True*)
            Converted element
        """
        if isinstance(idorcpp, base.Anatomist.AItem):
            return idorcpp
        if convertIDs and type(idorcpp) is int:
            try:
                o = self.context.object(idorcpp)
            except:
                o = None
            if o is None:
                if allowother:
                    return idorcpp
                else:
                    return None
            else:
                idorcpp = o
        if isinstance(idorcpp, cpp.AObject):
            return self.typedObject(idorcpp)
        if isinstance(idorcpp, cpp.AWindow):
            return Anatomist.AWindow(self, idorcpp)
        if isinstance(idorcpp, cpp.Referential):
            return Anatomist.Referential(self, idorcpp)
        if isinstance(idorcpp, cpp.Transformation):
            return Anatomist.Transformation(self, idorcpp)
        if allowother:
            return idorcpp
        else:
            return None

    def convertParamsToAItems(self, params, convertIDs=False, changed=[]):
        """
        Recursively converts C++ API objects or context IDs to generic API objects.

        Parameters
        ----------
        params: dict or list or anything else
        convertIDs: bool
            If *True*, int numbers are treated as item IDs and
            converted accordingly when possible.
        changed: list
            If anything has been changed from the input params, then
            changed will be added a True value. It's actually an output parameter

        Returns
        -------
        elements: list
            converted elements
        """
        def is_untransformed_object(obj):
            if isinstance(obj, _string_or_qstring):
                return True
            name = obj.__class__.__name__
            begins = ('AimsTimeSurface_', 'TimeTexture_', 'AimsRGB', 'AimsHSV')
            for n in begins:
                if name.startswith(n) or name.startswith('rc_ptr_' + n):
                    return True
            return False
        if is_untransformed_object(params):
            return params
        elif isSequenceType(params):
            conv = super(Anatomist, self).__getattribute__(
                'convertParamsToAItems')
            changed2 = []
            l = [conv(i, convertIDs=convertIDs, changed=changed2)
                 for i in params]
            if not changed2:
                return params
            else:
                if not changed:
                    changed.append(True)
                return l
        elif isMappingType(params) and not isinstance(params, aims.Graph):
            r = {}
            conv = super(Anatomist, self).__getattribute__(
                'convertParamsToAItems')
            changed2 = []
            for k, v in six.iteritems(params):
                r[k] = conv(v, convertIDs=convertIDs, changed=changed2)
            if changed2:
                if not changed:
                    changed.append(True)
                return r
            else:
                return params
        else:
            try:
                # TODO FIXME: this list has already been tried: remove it
                conv = super(Anatomist, self).__getattribute__(
                    'convertParamsToAItems')
                changed2 = []
                l = [conv(i, convertIDs=convertIDs, changed=changed2)
                     for i in params]
                if changed2:
                    if not changed:
                        changed.append(True)
                    return l
                else:
                    return params
            except:
                obj = super(Anatomist, self).__getattribute__('getAItem')(
                    params, convertIDs=convertIDs)
                if obj is not params and not changed:
                    changed.append(True)
                return obj

    def newItemRep(self):
        """
        Creates a new item representation.
        """
        return None

    def newId(self):
        """
        In this implementation, anatomist objects are accessibles but some commands need an id associated to the object :
        CreateWindowCommand blockid attribute, linkWindows group attribute...
        This method generates a unique id in current context.

        Returns
        -------
        id: int
            A new unused ID.
        """
        newId = self.context.makeID(None)
        if newId == 0:
            newId = self.context.makeID(None)
        return newId

    def sync(self):
        """
        Wait for anatomist finishing current processing.
        """
        from soma.qt_gui.qt_backend import QtGui
        QtGui.qApp.processEvents()

    #
    class AItem(base.Anatomist.AItem):

        """
        Base class for representing an object in Anatomist application.

        Attributes
        ----------
        anatomistinstance: :class:`Anatomist`
            Reference to Anatomist object which created this object.
            Useful because some methods defined in AItem objects will need to send a command to the Anatomist application.
        internalRep: object
            Representation of this object in anatomist application.
        ref: bool
            Indicates if a reference has been taken on the corresponding anatomist object. If *True*, the reference is released on deleting this item.
        refType: str
            Type of reference taken on the object : ``Weak`` (reference counter not incremented), ``WeakShared`` (reference counter incrementerd but the object can be deleted even if it remains references) or ``Strong`` (reference counter is incremented, the object cannot be deleted since there is references on it). If it is not specified, :py:data:`anatomist.base.Anatomist.defaultRefType` is used.
        """

        def __init__(self, *args, **kwargs):
            super(Anatomist.AItem, self).__init__(*args, **kwargs)

        def getInfo(self):
            """
            Gets information about this object.

            Returns
            -------
            info: dict
                information about the object (property -> value)
            """
            # using ObjectInfoCommand class directly doesn't work, I don't know why...
            # command=cpp.ObjectInfoCommand("", self.anatomistinstance.context,
            # self.anatomistinstance.convertToIds([self]), True, True)
            p = self.anatomistinstance.theProcessor()
            resetProcExec = False
            if not p.execWhileIdle():
                # allow recursive commands execution, otherwise the execute()
                # may not be done right now
                p.allowExecWhileIdle(True)
                resetProcExec = True
            command = self.anatomistinstance.execute(
                "ObjectInfo", objects=[self], name_children=1, name_referentials=1)
            infosObj = command.result()
            if resetProcExec:
                # set back recursive execution to its previous state
                p.allowExecWhileIdle(False)
            infos = eval(str(infosObj))  # aims.Object -> python dictionary
            if infos is not None:
                infos = infos.get(self.anatomistinstance.context.id(
                                  self.getInternalRep()))
            return infos

        def getInternalRep(self):
            # en attendant une conversion automatique dans sip
            if (getattr(self.internalRep, "get", None)):
                return self.internalRep.get()
            return self.internalRep

        def __getattr__(self, name):
            '''
            __getattribute__ is overloaded in Anatomist.direct.api:
            the aim is to intercept calls to the C++ API and convert return
            values which contain C++ instances to their corresponding wrapper in
            the Anatomist.direct implementation: AObject, AWindow, Referential,
            Transformation instances are converted.
            Drawback: all return values which are lists or dictionaries are
            copied.
            '''
            try:
                return super(base.Anatomist.AItem, self).__getattr__(name)
            except:
                # delegate to internalRep
                gattr = super(base.Anatomist.AItem, self).__getattribute__
                att = getattr(gattr('internalRep'), name, None)
                if att is None:
                    raise AttributeError("'" + type(self).__name__ +
                                         '\' object has no attribute \'' + name + "'")
                # get anatomist instance out of its weakproxy
                ainstance = gattr('anatomistinstance').__init__.__self__
                conv = super(type(ainstance), ainstance).__getattribute__(
                    'convertParamsToAItems')
                if callable(att):
                    return lambda *args, **kwargs: conv(att(*args, **kwargs))
                return conv(att)

        def _getAttributeNames(self):
            '''IPython completion feature...'''
            m = []
            l = [self.internalRep, self]
            done = set()
            while l:
                c = l.pop()
                done.add(c)
                m += [x for x in list(c.__dict__.keys())
                      if not x.startswith('_') and x not in m]
                cl = getattr(c, '__bases__', None)
                if not cl:
                    cl = getattr(c, '__class__', None)
                    if cl is None:
                        continue
                    else:
                        cl = [cl]
                l += [x for x in cl if x not in done]
            return m

    #
    class AObject(AItem, base.Anatomist.AObject):

        """
        Represents an object in Anatomist application.

        Following information can be obtained using ObjectInfo command:

        Attributes
        ----------
        objectType: str
            object type. For example : volume, bucket, graph, texture...
        children: list of :class:`Anatomist.AObject`
            List of objects which are children of current object (for example: nodes in a graph). Can be empty.
        filename: str
            Name of the file from which the object has been loaded. May be *None*.
        name: str
            Name of the object presented in Anatomist window.
        copy: bool
            *True* indicates that this object is a copy of another object, otherwise it is the original object.
        material: :class:`anatomist.cpp.Material`
            Object material parameters
        referential: :class:`Anatomist.Referential`
            Referential assigned to this object.
        """

        def __init__(self, *args, **kwargs):
            super(Anatomist.AObject, self).__init__(*args, **kwargs)

        def __getattr__(self, name):
            """
            The first time an attribute of this object is requested, it is asked to anatomist application with ObjectInfo command. It returns a dictionary containing informations about objects :
            ``{objectId -> {attributeName : attributeValue, ...},
            ...
            requestId -> id}``
            """
            if name == "objectType":
                self.objectType = self.internalRep.objectTypeName(
                    self.internalRep.type())
                return self.objectType
            elif name == "children":
                objects = []
                # if internalRep is a multi object, it is iterable and can have
                # children
                if isinstance(self.getInternalRep(), cpp.MObject):
                    for c in self.getInternalRep():
                        objects.append(self.anatomistinstance.typedObject(c))
                return objects
            elif name == "filename":
                self.filename = self.internalRep.fileName()
                return self.filename
            elif name == "name":
                return self.internalRep.name()
            elif name == "copy":
                self.copy = self.internalRep.isCopy()
                return self.copy
            elif name == "loadDate":
                return self.internalRep.loadDate()
            elif name == "material":
                matdesc = self.internalRep.GetMaterial().genericDescription()
                matParams = {}
                for k, v in matdesc.items():
                    matParams[k] = v
                matObj = self.anatomistinstance.Material(**matParams)
                return matObj
            elif name == "referential":
                ref = None
                iref = self.internalRep.getReferential()
                if iref is not None:
                    ref = self.anatomistinstance.Referential(
                        self.anatomistinstance, iref)
                return ref
            else:  # must raise AttributeError if it is not an existing attribute. else, error can occur on printing the object
                # return getattr(self.internalRep, name)
                return Anatomist.AItem.__getattr__(self, name)

        def _getAttributeNames(self):
            return ['objectType', 'children', 'filename', 'name', 'copy',
                    'loadDate', 'material', 'referential'] \
                + Anatomist.AItem._getAttributeNames(self)

        def __eq__(self, other):
            if not hasattr(other, 'getInternalRep'):
                return False
            return self.getInternalRep() == other.getInternalRep()

        def __hash__(self):
            # needs overriding in python3, since:
            # "a class that overrides __eq__() and does not define __hash__()
            #  will have its __hash__() implicitly set to None"
            return base.Anatomist.AItem.__hash__(self)

        def extractTexture(self, time=-1):
            """
            Extract the object texture to create a new texture object.

            Parameters
            ----------
            time: float
                For temporal objects, if this parameter is mentionned the texture will be extracted at this time. if not mentionned,
                All times will be extracted and the texture will be a temporal object.
                In socket implementation, it is necessary to get a new id for the texture object and to pass it to the command.

            Returns
            -------
            texture: AObject
                The newly created texture object
            """
            if time is None:
                time = -1
            c = cpp.ExtractTextureCommand(self.getInternalRep(), -1, time)
            self.anatomistinstance.execute(c)
            return self.anatomistinstance.typedObject(c.createdObject())

        def generateTexture(self, dimension=1):
            """
            Generates an empty texture (value 0 everywhere) for a mesh object.

            Parameters
            ----------
            dimension: int
                Texture dimension (1 or 2)

            Returns
            -------
            texture: AObject
                The newly created texture object
            """
            c = cpp.GenerateTextureCommand(
                self.getInternalRep(), -1, dimension)
            self.anatomistinstance.execute(c)
            return self.anatomistinstance.typedObject(c.createdObject())

        def setChanged(self):
            """
            Mark the current object as changed, so that a view update will take it into account.
            """
            self.internalRep.setChanged()

        def notifyObservers(self):
            """
            Update the observers views on the object (windows, or fusion objects etc will be re-calculated as needed)
            """
            self.internalRep.notifyObservers()

        def toAimsObject(self):
            """
            Converts AObject to aims object.
            """
            return cpp.AObjectConverter.aims(self.getInternalRep())

        def takeRef(self):
            if self.refType is None:
                self.refType = self.anatomistinstance.defaultRefType
            super(Anatomist.AObject, self).takeRef()
            if self.refType == "Weak":
                self.internalRep = cpp.weak_ptr_AObject(self.internalRep)
            elif self.refType == "WeakShared":
                self.internalRep = cpp.weak_shared_ptr_AObject(
                    self.internalRep)
            # print "take ref ", self.refType, self, self.internalRep,
            # self.internalRep.__class__

        def releaseRef(self):
            # print "release ref ", self
            super(Anatomist.AObject, self).releaseRef()
            del self.internalRep

        def releaseAppRef(self):
            # print "release app ref ", self
            self.anatomistinstance.releaseObject(self.getInternalRep())

        def takeAppRef(self):
            # print "release app ref ", self
            self.anatomistinstance.takeObjectRef(self.getInternalRep())

        # def __del__(self):
            # print "del AObject ", self
            # super(Anatomist.AObject, self).__del__()

    #
    class AGraph(AObject, base.Anatomist.AGraph):

        """
        Represents a graph.
        """

        def __init__(self, anatomistinstance, internalRep=None, *args, **kwargs):
            super(Anatomist.AGraph, self).__init__(
                anatomistinstance, internalRep, *args, **kwargs)

        def createNode(self, name=None, syntax=None, with_bucket=None, duplicate=True):
            """
            Creates a new node with optionally an empty bucket inside and adds it in the graph.

            Parameters
            ----------
            name: str
                node name. default is ``RoiArg``.
            syntax: str
                node syntax attribute. default is ``roi``.
            with_bucket: bool
                if *True*, creates an empty bucket in the node and returns it with the node. default is None, so the bucket is created but not returned
            duplicate: bool
                enables duplication of nodes with the same name attribute.

            Returns
            -------
            node_def: (AObject, AObject)
                (the created node, the created bucket) or only the created node if with_bucket is False
            """
            nodeId = self.anatomistinstance.newId()
            bucketId = None
            if with_bucket is not None:
                if with_bucket:
                    with_bucket = 1
                    bucketId = self.anatomistinstance.newId()
                else:
                    with_bucket = 0
            if duplicate:
                no_duplicate = 0
            else:
                no_duplicate = 1
            self.anatomistinstance.execute(
                "AddNode", graph=self, res_pointer=nodeId,
                name=name, with_bucket=with_bucket, res_bucket=bucketId, no_duplicate=no_duplicate)
            node = self.anatomistinstance.typedObject(
                self.anatomistinstance.context.object(nodeId))
            if bucketId is not None:
                bucket = self.anatomistinstance.typedObject(
                    self.anatomistinstance.context.object(bucketId))
                res = (node, bucket)
            else:
                res = node
            return res

    #
    class AWindow(AItem, base.Anatomist.AWindow):

        """
        Represents an anatomist window.

        Attributes
        ----------
        windowType: str
            Windows type (``'axial'``, ``'sagittal'``, ...)
        group: :class:`Anatomist.AWindowsGroup`
            The group which this window belongs to.
        objects: list of :class:`Anatomist.AObject`
            The window contains these objects.
        """

        def __init__(self, *args, **kwargs):
            super(Anatomist.AWindow, self).__init__(*args, **kwargs)
            # needed to allow dynamic request in __getattr__
            if self.block is None:
                del self.block

        def __getattr__(self, name):
            """
            The first time an attribute of this window is requested, it is asked to anatomist application with ObjectInfo command. It returns a dictionary containing informations about objects :
            {objectId -> {attributeName : attributeValue, ...},
            ...
            requestId -> id}
            """
            if name == "windowType":
                t = self.internalRep.subtype()
                if t == 0:
                    t = self.internalRep.type()
                return cpp.AWindowFactory.typeString(t)
            elif name == "group":  # window group can change so it is not saved in an attribute
                return self.anatomistinstance.AWindowsGroup(self.anatomistinstance, self.internalRep.Group())
            elif name == "objects":
                objs = self.internalRep.Objects()
                aobjs = []
                for obj in objs:
                    aobjs.append(self.anatomistinstance.typedObject(obj))
                return aobjs
            elif name == 'block':
                if not self.parent() or not self.parent().parent():
                    return None
                else:
                    block = Anatomist.AWindowsBlock.findBlock(
                        self.parent().parent())
                    if block:
                        return Anatomist.AWindowsBlock(self.anatomistinstance,
                                                       widgetproxy=block)
                return None
            else:  # must raise AttributeError if it is not an existing attribute. else, error can occur on printing the object
                return Anatomist.AItem.__getattr__(self, name)

        def _getAttributeNames(self):
            return ['windowType', 'group', 'objects'] + \
                Anatomist.AItem._getAttributeNames(self)

        def takeRef(self):
            if self.refType is None:
                self.refType = self.anatomistinstance.defaultRefType
            super(Anatomist.AWindow, self).takeRef()
            if self.refType == "Weak":
                self.internalRep = cpp.weak_ptr_AWindow(self.internalRep)
            elif self.refType == "WeakShared":
                self.internalRep = cpp.weak_shared_ptr_AWindow(
                    self.internalRep)
            # print "take ref ", self.refType, self, self.internalRep,
            # self.internalRep.__class__

        def releaseRef(self):
            # print "release ref ", self
            super(Anatomist.AWindow, self).releaseRef()
            del self.internalRep

        def releaseAppRef(self):
            # print "release app ref ", self
            self.anatomistinstance.releaseWindow(self.getInternalRep())

        def takeAppRef(self):
            # print "release app ref ", self
            self.anatomistinstance.takeWindowRef(self.getInternalRep())

        # def __del__(self):
            # print "del AWindow ", self
            # super(Anatomist.AWindow, self).__del__()

        def getReferential(self):
            ref = self.internalRep.getReferential()
            if ref is not None:
                return self.anatomistinstance.Referential(
                    self.anatomistinstance,
                    ref)
            return ref

        def imshow(self, width=0, height=0, figure=None, show=False):
            '''
            Display the 3D view rendering into a Matplotlib figure using
            pylab.imshow(). This is useful to display static figures in a
            widget, or use them to export in a document, or to use the
            sphinx_gallery module for documentation.
            '''
            if not hasattr(self.internalRep, 'snapshotImage'):
                raise TypeError('AWindow.to_imshow called on a non-OpenGL '
                                'window type')
            im = self.internalRep.snapshotImage(0, width, height)
            aim = qt_backend.qimage_to_np(im)
            from matplotlib import pyplot
            plot = pyplot.imshow(aim, figure=figure)
            if figure is not None:
                axes = figure.axes()
            else:
                axes = pyplot.axes()
            axes.get_xaxis().set_visible(False)
            axes.get_yaxis().set_visible(False)
            if show:
                if figure is not None:
                    figure.show()
                else:
                    pyplot.show(block=False)
            return plot

        def sphinx_gallery_snapshot(self, width=0, height=0,
                                    restore_backend=False):
            '''
            Render the view in a matplotlib AGG graph to be used by the
            sphinx_gallery module, when building documentation examples.
            If sphinx_gallery is not already loaded, then nothing is done

            Parameters
            ----------
            width: int
            height: int
            restore_backend: bool
                the rendering needs to set matplotlib backend to "agg"
                temporarily. If restore_backend is True, then the former
                backend is restored. Otherwise (the default) it is left to agg.
                sphinx_gallery generally needs to leave it to agg when building
                docs for multiple Anatomist examples.

            Returns
            -------
            plot:
                result oy pyplot.imshow(), or None if sphinx_gallery is not
                loaded
            '''
            if 'sphinx_gallery' not in sys.modules:
                return None
            # display in matplotlib for sphinx_gallery
            import matplotlib
            backend = matplotlib.get_backend()
            matplotlib.use('agg', warn=False, force=True)  # force agg
            plot = self.imshow(show=True, width=width, height=height)
            if restore_backend:
                # restore backend
                matplotlib.use(backend, warn=False, force=True)
            return plot

    #
    class AWindowsBlock(AItem, base.Anatomist.AWindowsBlock):

        """
        A window containing other windows.

        Attributes
        ----------
        nbCols: int
            Number of columns of the windows block
        """
        _widgets = weakref.WeakKeyDictionary()

        class WidgetProxy(object):

            '''Contains a QWidget. This proxy class is only here to activate
            reference counting on the widget'''

            def __init__(self, anatomistinstance, internalRep, widget):
                self.anatomistinstance = anatomistinstance
                self.widget = widget
                self.internalRep = internalRep

            def __del__(self):
                # print 'delete block', self, ', id:', self.internalRep, ',
                # widget:', self.widget
                self.anatomistinstance.execute('DeleteElement',
                                               elements=[self.internalRep])

            def __eq__(self, y):
                if isinstance(y, Anatomist.AWindowsBlock.WidgetProxy):
                    return self.widget == y.widget
                return self.widget == y

            def __lt__(self, y):
                if isinstance(y, Anatomist.AWindowsBlock.WidgetProxy):
                    return self.widget < y.widget
                return self.widget < y

            def __le__(self, y):
                if isinstance(y, Anatomist.AWindowsBlock.WidgetProxy):
                    return self.widget <= y.widget
                return self.widget <= y

            def __gt__(self, y):
                if isinstance(y, Anatomist.AWindowsBlock.WidgetProxy):
                    return self.widget > y.widget
                return self.widget > y

            def __ge__(self, y):
                if isinstance(y, Anatomist.AWindowsBlock.WidgetProxy):
                    return self.widget >= y.widget
                return self.widget >= y

            def __hash__(self):
                return id(self.widget)

        def __init__(self, anatomistinstance=None, nbCols=2, nbRows=0,
                     widgetproxy=None):
            super(Anatomist.AWindowsBlock, self).__init__(anatomistinstance,
                                                          nbCols=nbCols,
                                                          nbRows=nbRows)
            if widgetproxy is not None:
                self.internalRep = widgetproxy.internalRep
                self.internalWidget = widgetproxy
            else:
                self.internalRep = anatomistinstance.newId()
                self.internalWidget = None

        def __del__(self):
            base.Anatomist.AWindowsBlock.__del__(self)
            Anatomist.AItem.__del__(self)

        def setWidget(self, w):
            if isinstance(w, self.WidgetProxy):
                self.internalWidget = w
            else:
                wp = self.findBlock(w)
                if wp is not None:
                    self.internalWidget = wp
                else:
                    self.internalWidget = self.WidgetProxy(
                        self.anatomistinstance,
                        self.internalRep, w)
                    self._widgets[self.internalWidget] = None

        def widgetProxy(self):
            return self.internalWidget

        @staticmethod
        def findBlock(widget):
            for x in Anatomist.AWindowsBlock._widgets:
                if x.widget == widget:
                    return x
            return None

    #
    class AWindowsGroup(AItem, base.Anatomist.AWindowsGroup):

        """
        A group containing several windows which are linked. Moving cursor in one window moves it in all linked windows.
        """

        def __init__(self, anatomistinstance, groupid=None):
            if groupid is None:
                groupid = anatomistinstance.newId()
            super(Anatomist.AWindowsGroup, self).__init__(
                anatomistinstance, groupid)

    #
    class Referential(AItem, base.Anatomist.Referential):

        """
        Attributes
        ----------
        refUuid: str
            A unique id representing this referential.
            Two referential are equal if they have the same uuid.
        """

        def __init__(self, anatomistinstance, internalRep=None, uuid=None):
            super(Anatomist.Referential, self).__init__(
                anatomistinstance, internalRep, uuid)

        def __getattr__(self, name):
            """
            """
            if name == "refUuid":
                self.refUuid = self.internalRep.uuid()
                return self.refUuid
            else:  # must raise AttributeError if it is not an existing attribute. else, error can occur on printing the object
                return Anatomist.AItem.__getattr__(self, name)

        def _getAttributeNames(self):
            return ['refUuid'] + Anatomist.AItem._getAttributeNames(self)

    #
    class APalette(AItem, base.Anatomist.APalette):

        """
        Attributes
        ----------
        name: str
            Palette name. Must be unique, it is the palette identifier.
        """

        def __init__(self, name, anatomistinstance, internalRep=None, *args, **kwargs):
            super(Anatomist.APalette, self).__init__(
                name, anatomistinstance, internalRep, *args, **kwargs)

    #
    class Transformation(AItem, base.Anatomist.Transformation):

        """
        This objects contains informations to convert coordinates from one referential to another: rotation_matrix, translation
        """

        def __init__(self, anatomistinstance, internalRep=None, *args, **kwargs):
            super(Anatomist.Transformation, self).__init__(
                anatomistinstance, internalRep, *args, **kwargs)
