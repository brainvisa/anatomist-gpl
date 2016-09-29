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
General interface of pyanatomist API. It describes classes and methods that are shared by all implementations : the set of Anatomist features available throught this API.
Several implementations exist depending on the mean of driving Anatomist (Sip bindings C++/Python or commands via socket).
"""

from __future__ import print_function

from soma.notification import ObservableNotifier
from soma.singleton import Singleton
from soma.functiontools import partial
import operator
import string
import threading
import collections
import sys
import six

if sys.version_info[0] >= 3:
    basestring = str


def isSequenceType(item):
    if isinstance(item, collections.Sequence):
        return True
    if hasattr(item, 'isArray'):
        # aims Object API
        return item.isArray()
    if isMappingType(item):
        return False
    methods = ['__getitem__', '__contains__', '__iter__', '__len__']
    # should also include: count, index but pyaims sequences do not have them
    for m in methods:
        if not hasattr(item, m):
            return False
    return True


def isMappingType(item):
    if isinstance(item, collections.Mapping):
        return True
    if hasattr(item, 'isDictionary'):
        # aims Object API
        return item.isDictionary()
    methods = ['get', 'items', 'keys', 'values', '__getitem__', '__iter__',
               '__contains__', '__len__']
    if sys.version_info[0] < 3:
        methods.append('iteritems')
    for m in methods:
        if not hasattr(item, m):
            return False
    return True


class Anatomist(Singleton):
  """
  Interface to communicate with an Anatomist Application. This class is virtual, some methods are not implemented. It is the base class of Anatomist classes in each implementation.

  This class is a Singleton, so there is only one global instance of this class. The first time the constructor is called, an instance is created. Each next time, the same instance is returned.
  It is also possible to ask for anatomist instance without creating an instance if it does not exit. To do this, use the constructor with create=False as parameter :

  >>> a=anatomist.Anatomist(create=False)

  will return the current instance or None if no instance exists.

  This class can notify anatomist events. To call a function when an event occurs, add a listener to one of Anatomist's notifiers.

  For example:

  >>> anatomist.onLoadNotifier.add(listener)

  listener must be a callback function that accepts two parameters : the event name (string) and a dictionary of parameters describing the event.

  .. data:: onLoadNotifier

    type: ObservableNotifier

    Notifies object loading.

    Event parameters : ``{ 'filename' : string, 'object' : AObject, 'type' : string }``

  .. data:: onDeleteNotifier

    type: ObservableNotifier

    Notifies object deletion.

    Event parameters : ``{'object' : AObject }``

  .. data:: onFusionNotifier

    type: ObservableNotifier

    Notifies objects fusion.

    Event parameters : ``{'children' : list of AObject, 'method' : string, 'object' : AObject, 'type' : string }``

  .. data:: onCreateWindowNotifier

    type: ObservableNotifier

    Notifies window creation.

    Event parameters : ``{'type' : string, 'window' : AWindow }``

  .. data:: onCloseWindowNotifier

    type: ObservableNotifier

    Notifies window closing.

    Event parameters : ``{'window' : AWindow }``

  .. data:: onAddObjectNotifier

    type: ObservableNotifier

    Notifies object adding in window.

    Event parameters : ``{'object' : AObject, 'window' : AWindow }``

  .. data:: onRemoveObjectNotifier

    type: ObservableNotifier

    Notifies object removing from window.

    Event parameters : ``{'object' : AObject, 'window' : AWindow }``

  .. data:: onCursorNotifier

    type: ObservableNotifier

    Notifies cursor position change.

    Event parameters : ``{'position' : float vector size 4, 'window' : AWindow }``

  .. data: onExitNotifier

    type: ObservableNotifier

    Notifies that Anatomist application exits.

  .. data:: centralRef

    type: Referential

    Anatomist's central referential (talairach acpc ref)

  .. data:: mniTemplateRef

    type: Referential

    Template mni referential (used by spm)

  These two referentials and transformation between them are always loaded in anatomist.

  .. data:: defaultRefType

    type: string

    Reference type taken by default on anatomist objects. Strong means that objects or windows cannot be deleted while a reference exist on it.

  .. data:: lock

    type: threading.RLock

    Enable to take a lock on anatomist singleton instance
  """
  defaultRefType="Strong"
  lock = threading.RLock()

  def __new__( cls, *args, **kwargs ):
    '''If the keyword arg create is set to False, then a new instance is
    not created event if the singleton has not been instantiated yet.
    '''
    instance=None
    create = kwargs.get( 'create', True )
    if '_singleton_instance' not in cls.__dict__:
      if create:
        instance = super(Anatomist, cls).__new__( cls, *args,
          **kwargs )
    else:
      instance = cls._singleton_instance
    return instance

  def __singleton_init__(self, *args, **kwargs):
    super(Anatomist, self).__singleton_init__()

    self.onLoadNotifier=ObservableNotifier()
    # enable listening of event  only when the notifier has at least one listener.
    self.onLoadNotifier.onAddFirstListener.add( partial( self.enableListening, "LoadObject", self.onLoadNotifier ) )
    self.onLoadNotifier.onRemoveLastListener.add( partial( self.disableListening, "LoadObject" ) )

    self.onDeleteNotifier=ObservableNotifier()
    self.onDeleteNotifier.onAddFirstListener.add( partial( self.enableListening, "DeleteObject", self.onDeleteNotifier ) )
    self.onDeleteNotifier.onRemoveLastListener.add( partial( self.disableListening, "DeleteObject" ) )

    self.onFusionNotifier=ObservableNotifier()
    self.onFusionNotifier.onAddFirstListener.add( partial( self.enableListening, "FusionObjects", self.onFusionNotifier ) )
    self.onFusionNotifier.onRemoveLastListener.add( partial( self.disableListening, "FusionObjects" ) )

    self.onCreateWindowNotifier=ObservableNotifier()
    self.onCreateWindowNotifier.onAddFirstListener.add( partial( self.enableListening, "CreateWindow", self.onCreateWindowNotifier ) )
    self.onCreateWindowNotifier.onRemoveLastListener.add( partial( self.disableListening, "CreateWindow" ) )

    self.onCloseWindowNotifier=ObservableNotifier()
    self.onCloseWindowNotifier.onAddFirstListener.add( partial( self.enableListening, "CloseWindow", self.onCloseWindowNotifier ) )
    self.onCloseWindowNotifier.onRemoveLastListener.add( partial( self.disableListening, "CloseWindow" ) )

    self.onAddObjectNotifier=ObservableNotifier()
    self.onAddObjectNotifier.onAddFirstListener.add( partial( self.enableListening, "AddObject", self.onAddObjectNotifier ) )
    self.onAddObjectNotifier.onRemoveLastListener.add( partial( self.disableListening, "AddObject" ) )

    self.onRemoveObjectNotifier=ObservableNotifier()
    self.onRemoveObjectNotifier.onAddFirstListener.add( partial( self.enableListening, "RemoveObject", self.onRemoveObjectNotifier ) )
    self.onRemoveObjectNotifier.onRemoveLastListener.add( partial( self.disableListening, "RemoveObject" ) )

    self.onCursorNotifier=ObservableNotifier()
    self.onCursorNotifier.onAddFirstListener.add( partial( self.enableListening, "LinkedCursor", self.onCursorNotifier ) )
    self.onCursorNotifier.onRemoveLastListener.add( partial( self.disableListening, "LinkedCursor" ) )

    self.onExitNotifier=ObservableNotifier()
    self.onExitNotifier.onAddFirstListener.add( partial( self.enableListening, "Exit", self.onExitNotifier ) )
    self.onExitNotifier.onRemoveLastListener.add( partial( self.disableListening,"Exit" ) )

  def enableListening(self, event, notifier):
    """
    Set listening of this event on. So when the event occurs, the notifier's notify method is called.
    This method is automatically called when the first listener is added to a notifier. That is to say that notifiers are activated only if they have registered listeners.

    :param string event:
      Name of the event to listen

    :param notifier:
      The notifier whose notify method must be called when this event occurs
    :type notifier: :py:class:`soma.notification.Notifier`
    """
    pass

  def disableListening(self, event):
    """
    Set listening of this event off.

    :param string  event:
      Name of the event to disable.
    """
    pass

  # objects creation
  def createWindowsBlock(self, nbCols=None, nbRows=None):
    """
    Creates a window containing other windows.

    :param int nbCols:
      Number of columns of the windows block

    :param int nbRows:
      Number of rows of the windows block (exclusive with nbCols)

    :returns:
      A window which can contain several :py:class:`AWindow`
    :rtype: :py:class:`AWindowsBlock`
    """
    pass

  def createWindow(self, wintype, geometry=None, block=None,
    no_decoration=None, options=None):
    """
    Creates a new window and opens it.

    :param string wintype:
      Type of window to open (``"Axial"``, ``"Sagittal"``, ``"Coronal"``, ``"3D"``, ``"Browser"``, ``"Profile"``, ...)

    :param geometry:
      Position on screen and size of the new window (x, y, w, h)
    :type geometry: int vector

    :param block:
      A block in which the new window must be added
    :type block: :py:class:`AWindowsBlock`

    :param bool no_decoration:
      Indicates if decorations (menus, buttons) can be painted around the view.

    :param dictionary options:
      Internal advanced options.

    :returns:
      The newly created window
    :rtype: :py:class:`AWindow`
    """
    pass

  def loadObject(self, filename, objectName=None, restrict_object_types=None, forceReload=True, duplicate=False, hidden=False):
    """
    Loads an object from a file (volume, mesh, graph, texture...)

    :param string filename:
      The file containing object data

    :param string objectName:
      Object name

    :param dictionary restrict_object_types:
      object -> accpepted types list. Ex: ``{'Volume' : ['S16', 'FLOAT']}``

    :param boolean forceReload:
      If *True* the object will be loaded even if it is already loaded in Anatomist. Otherwise, the already loaded one is returned.

    :param boolean duplicate:
      If the object already exists, duplicate it. The original and the copy will share the same data but not display parameters as palette. If the object is not loaded yet, load it hidden and duplicate it (unable to keep the original object with default display parameters).

    :param boolean hidden:
      a hidden object does not appear in Anatomist main control window.

    :returns:
      The loaded object
    :rtype: :py:class:`AObject`
    """
    pass

  def duplicateObject(self, source, shallowCopy=True):
    """
    Creates a copy of source object.

    :param source:
      The object to copy.
    :type source: :py:class:`AObject`

    :returns:
      The copy
    :rtype: :py:class:`AObject`
    """
    pass

  def createGraph(self, object, name=None, syntax=None, filename=None):
    """
    Creates a graph associated to an object (volume for example). This object initializes the graph dimensions (voxel size, extrema).

    :param object:
      The new graph is based on this object
    :type object: :py:class:`AObject`

    :param string name:
      Graph name. default is ``'RoiArg'``.

    :param string syntax:
      Graph syntactic attribute. default is ``'RoiArg'``.

    :param string filename:
      Filename used for saving. Default is None.

    :returns:
      The new graph object
    :rtype: :py:class:`AGraph`
    """
    pass

  def loadCursor(self, filename):
    """
    Loads a cursor for 3D windows from a file.

    :param string filename:
      The file containing object data

    :returns:
      The loaded object
    :rtype: :py:class:`AObject`
    """
    pass

  def fusionObjects(self, objects, method=None, ask_order=False):
    """
    Creates a fusionned multi object that contains all given objects.

    :param objects:
      List of objects that must be fusionned
    :type objects: list of :py:class:`AObject`

    :param string method:
      Method to apply for the fusion (``'Fusion2DMethod'``...)

    :param boolean ask_order:
      If *True*, asks user in what order the fusion must be processed.

    :returns:
      The newly created fusion object.
    :rtype: :py:class:`AObject`
    """
    pass

  def getFusionInfo( self, objects=None ):
    """
    Gets information about fusion methods. If objects is not specified, the global list of all fusion methods is returned. Otherwise the allowed fusions for those specific objects is returned.

    :returns:
      Fusion methods
    :rtype: dictionary
    """
    pass

  def createReferential(self, filename=None):
    """
    This command does not exist in Anatomist because the command AssignReferential can create a new referential if needed.
    But the way of creating a new referential depends on the connection with Anatomist,
    so it seems to be better to encapsulate this step on another command. So referentials are treated the same as other objects.
    (LoadObject -> addAobject | createReferential -> assignReferential)

    :param string filename:
      Name of a file (minf file, extension .referential) containing  informations about the referential : its name and uuid

    :returns:
      The newly created referential
    :rtype: :py:class:`Referential`
    """
    pass

  def loadTransformation(self, filename, origin, destination):
    """
    Loads a transformation from a referential to another. The transformation informations are given in a file.

    :param string filename:
      File containing transformation information

    :param origin:
      Origin of the transformation
    :type origin: :py:class:`Referential`

    :param destination:
      Referential after applying transformation
    :type destination: :py:class:`Referential`

    :returns:
      Transformation to apply to convert coordinates from one referent
    :rtype: :py:class:`Transformation`
    """
    pass

  def createTransformation(self, matrix, origin, destination):
    """
    Creates a transformation from a referential to another. The transformation informations are given in a matrix.

    :param matrix:
      Transformation matrix (4 lines, 3 colons; 1st line: translation, others: rotation)
    :type matrix: float vector, size 12

    :param origin:
      Origin of the transformation
    :type origin: :py:class:`Referential`

    :param destination:
      Referential after applying transformation
    :type destination: :py:class:`Referential`

    :returns:
      New transformation
    :rtype: :py:class:`Transformation`
    """
    pass

  def createPalette(self, name):
    """
    Creates an empty palette and adds it in the palettes list.

    :param string name:
      Name of the new palette

    :returns:
      The newly created palette
    :rtype: :py:class:`APalette`
    """
    pass

  def groupObjects(self, objects):
    """
    Creates a multi object containing objects in parameters.

    :param objects:
      Objects to put in a group
    :type objects: list of :py:class:`AObject`

    :returns:
      The newly created multi object
    :rtype: :py:class:`AObject`
    """
    pass

  def linkWindows(self, windows, group=None):
    """
    Links windows in a group. Moving cursor position in a window moves it in all linked windows.
    By default all windows are in the same group.

    :param windows:
      The windows to link
    :type windows: list of :py:class:`AWindow`

    :param group:
      Put the windows in this group. If it is *None*, a new group is created.
    :type group: :py:class:`AWindowsGroup`

    :rtype: :py:class:`AWindowsGroup`
    """
    if windows != []:
      windows = self.makeList( windows )
      self.execute("LinkWindows", windows = windows, group = group)
      if group is None:
        group=windows[0].group
    return group

  ###############################################################################
  # objects access
  def getPalette(self, name):
    """
    :returns:
      The named palette
    :rtype: :py:class:`APalette`
    """
    pass

  # information that can be obtained with GetInfo command
  def getObjects(self):
    """
    Gets all objects referenced in current context.

    :returns:
      List of existing objects
    :rtype:  list of :py:class:`AObject`
    """
    pass

  def importObjects(self, top_level_only=False):
    """
    Gets objects importing those that are not referenced in current context.

    :param bool top_level_only:
      If *True*, imports only top-level objects (that have no parents), else all objects are imported.

    :returns:
      List of existing objects
    :rtype:  list of :py:class:`AObject`
    """
    pass

  def getObject(self, filename):
    """
    Get the object corresponding to this filename if it is currently loaded.

    :param string filename:
      Filename of the requested object

    :returns:
      The object if it is loaded, else returns *None*.
    :rtype: :py:class:`AObject` or *None*
    """
    objects=self.getObjects()
    loadedObject=None
    for o in objects:
      if o.filename == filename and not o.copy:
        loadedObject=o
        break
    return loadedObject

  def getWindows(self):
    """
    Gets all windows referenced in current context.

    :returns:
      List of opened windows
    :rtype: list of :py:class:`AWindow`
    """
    pass

  def importWindows(self):
    """
    Gets all windows importing those that are not referenced in current context.

    :returns:
      List of opened windows
    :rtype: list of :py:class:`AWindow`
    """
    pass

  def getReferentials(self):
    """
    Gets all referentials in current context.

    :returns:
      List of referentials
    :type: list of :py:class:`Referential`
    """
    pass

  def importReferentials(self):
    """
    Gets all referentials importing those that are not referenced in current context.

    :returns:
      List of referentials
    :rtype: list of :py:class:`Referential`
    """
    pass

  def getTransformations(self):
    """
    Gets all transformations.

    :returns:
      List of transformations
    :rtype: list of :py:class:`Transformation`
    """
    pass

  def importTransformations(self):
    """
    Gets all transformations importing those that are not referenced in current context.

    :returns:
      List of transformations
    :rtype: list of :py:class:`Transformation`
    """
    pass

  def getPalettes(self):
    """
    :returns:
      List of palettes.
    :rtype: list of :py:class:`APalette`
    """
    pass

  def getSelection(self, group=None):
    """
    :param group:
      Get the selection in this group. If *None*, returns the selection in the default group.
    :type group: :py:class:`AWindowsGroup`

    :returns:
      The list of selected objects in the group of windows
    :rtype: list of :py:class:`AObject`
    """
    pass

  def getDefaultWindowsGroup(self):
    '''
    Normally returns 0
    '''
    return self.AWindowsGroup(self, 0)

  def linkCursorLastClickedPosition(self, ref=None):
    """
    Gives the last clicked position of the cursor.

    :param ref:
      If given, cursor position value will be in this referential. Else, anatomist central referential is used.
    :type ref: :py:class:`Referential`

    :returns:
      Last position of the cursor
    :rtype: float vector, size 3
    """
    pass

  def getAimsInfo(self):
    """
    :returns:
      Information about AIMS library.
    :rtype: string
    """
    pass

  def getCommandsList(self):
    """
    :returns:
      List of commands available in Anatomist with their parameters.
      dict command name -> dict parameter name -> dict attribute -> value (needed, type)
    :rtype: dictionary
    """
    pass

  def getModulesInfo(self):
    """
    :returns:
      List of modules and their description. dict module name -> dict attribute -> value (description)
    :rtype: dictionary
    """
    pass

  def getVersion(self):
    """
    :returns:
      Anatomist version
    :rtype: string
    """
    pass

  ###############################################################################
  # objects manipulation
  def showObject(self, object):
    '''Displays the given object in a new window'''
    self.execute("ShowObject", object=object)

  def addObjects(self, objects, windows, add_children=False,
        add_graph_nodes=True, add_graph_relations=False, temporary=False,
        position=-1):
    """
    Adds objects in windows.
    The objects and windows must already exist.

    Parameters
    ----------
    objects: list of :py:class:`AObject`
        List of objects to add
    windows: list of :py:class:`AWindow`
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
    self.execute("AddObject", objects=self.makeList(objects),
      windows=self.makeList(windows), add_children=int(add_children),
      add_graph_nodes=int(add_graph_nodes),
      add_graph_relations=int(add_graph_relations), temporary=int(temporary),
      position=position)

  def removeObjects(self, objects, windows, remove_children=False):
    """
    Removes objects from windows.

    :param objects:
      List of objects to remove
    :type objects: list of :py:class:`AObject`

    :param windows:
      List of windows from which the objects must be removed
    :type windows: list of :py:class:`AWindow`
    """
    self.execute("RemoveObject", objects=self.makeList(objects),
      windows=self.makeList(windows), remove_children=int(remove_children) )

  def deleteObjects(self, objects):
    """
    Deletes objects

    :param objects:
      Objects to delete
    :type objects: list of :py:class:`AObject`
    """
    objects=self.makeList(objects)
    for o in objects:
      o.releaseRef()
    #self.execute("DeleteObject", objects=objects)

  def deleteElements(self, elements):
    """
    Deletes objects, windows, referentials, anything that is referenced in anatomist application.

    :param elements:
      Elements to delete
    :type elements: list of :py:class:`AItem`
    """
    self.execute("DeleteElement", elements=self.makeList(elements))

  def reloadObjects(self, objects):
   """
   Reload objects already in memory reading their files.
   """
   self.execute("ReloadObject", objects=self.makeList(objects))

  def assignReferential(self, referential, elements):
    """
    Assign a referential to objects and/or windows.
    The referential must exist. To create a new Referential, execute createReferential,
    to assign the central referential, first get it with Anatomist.centralRef attribute.

    :param referential:
      The referential to assign to objects and/or windows
    :type referential: :py:class:`Referential`

    :param elements:
      Objects or windows which referential must be changed.
      The corresponding command tree contains an attribute central_ref to indicate if the referential to assign is anatomist central ref,
      because this referential isn't referenced by an id. In the socket implementation, Referential object must have an attribute central_ref,
      in order to create the command message. In direct impl, it is possible to access directly to the central ref object.
    :type elements: list of :py:class:`AItem`
    """
    objects=[]
    windows=[]
    # in anatomist command, objects and windows must be passed in two lists
    for e in self.makeList(elements):
      if issubclass(e.__class__, Anatomist.AObject):
        objects.append(e)
      elif issubclass(e.__class__, Anatomist.AWindow):
        windows.append(e)
    self.execute("AssignReferential", ref_id = referential, objects=objects,
      windows=windows, central_ref=referential.centralRef)

  def loadReferentialFromHeader(self, objects):
    """
    Extracts referentials / transformations from objects headers when they contain such information, and assign them.

    :param objects:
      Objects which referential information must be loaded
    :type objects: list of :py:class:`AObject`
    """
    self.execute("LoadReferentialFromHeader", objects=self.makeList(objects) )

  applyBuiltinReferential = loadReferentialFromHeader

  def camera(self, windows, zoom=None, observer_position=None, view_quaternion=None, slice_quaternion=None, force_redraw=False, cursor_position=None, boundingbox_min=None, boundingbox_max=None, slice_orientation=None):
    """
    Sets the point of view, zoom, cursor position for 3D windows.

    :param windows:
      Windows which options must be changed
    :type windows: list of :py:class:`AWindow`

    :param float zoom:
      Zoom factor, default is 1

    :param observer_position:
      Camera position
    :type observer_position: float vector, size 3

    :param view_quaternion:
      View rotation
    :type view_quaternion: float vector, size 4, normed

    :param slice_quaternion:
      Slice plane rotation
    :type slice_quaternion: float vector, size 4, normed

    :param boolean force_redraw:
      If *True*, refresh printing immediatly, default is *False*

    :param cursor_position:
      Linked cursor position
    :type cursor_position: float vector

    :param boundingbox_min:
      Bounding box min values
    :type boundingbox_min: float vector

    :param boundingbox_max:
      Bounding box max values
    :type boundingbox_max: float vector

    :param slice_orientation:
      Slice plane orientation, normal to the plane
    :type slice_orientation: float vector, size 3
    """
    if force_redraw:
      force_redraw = 1
    else: force_redraw = 0
    self.execute("Camera", windows=self.makeList(windows), zoom = zoom, observer_position = observer_position, view_quaternion = view_quaternion, slice_quaternion = slice_quaternion, force_redraw = force_redraw, cursor_position = cursor_position, boundingbox_min = boundingbox_min, boundingbox_max = boundingbox_max, slice_orientation = slice_orientation )

  def setWindowsControl(self, windows, control):
    """
    Changes the selected button in windows menu.

    :param windows:
      Windows to set control on
    :type windows: list of :py:class:`AWindow`

    :param string control:
      Control to set. Examples of controls : 'PaintControl', 'NodeSelectionControl', 'Default 3D Control', 'Selection 3D', 'Flight Control', 'ObliqueControl', 'TransformationControl', 'CutControl', 'Browser Selection', 'RoiControl'...
    """
    self.execute("SetControl", windows=self.makeList(windows), control=control)

  def closeWindows(self, windows):
    """
    Closes windows.

    :param windows:
      Windows to be closed
    :type windows: list of :py:class:`AWindow`
    """
    windows=self.makeList(windows)
    for w in windows:
      w.releaseRef()
    #self.execute("CloseWindow", windows=windows)

  def setMaterial(self, objects, material=None, refresh=None, ambient=None,
    diffuse=None, emission=None, specular=None, shininess=None, lighting=None,
    smooth_shading=None, polygon_filtering=None, depth_buffer=None,
    face_culling=None, polygon_mode=None, unlit_color=None, line_width=None,
    ghost=None, front_face=None, selectable_mode=None ):
    """
    Changes objects material properties.

    :param material:
      Material characteristics, including render properties.
      The material may be specified as a Material object, or as its various
      properties (ambient, diffuse, etc.). If both a material parameter and
      other properties are specified, the material is used as a base, and
      properties are used to modify it
    :type material: :py:class:`anatomist.base.Anatomist.Material`

    :param bool refresh:
      If *True*, force windows refreshing

    :param ambient:
    :type ambient: RGB[A] vector: float values between 0 and 1.

    :param list diffuse:
      This parameter corresponds to the "standard" notion of color
    :type diffuse: RGB[A] vector: float values between 0 and 1.

    :param emission:
    :type emission: RGB[A] vector: float values between 0 and 1.

    :param specular:
    :type specular: RGB[A] vector: float values between 0 and 1.

    :param float shininess:
      0-124

    :param boolaen lighting:
      enables (1) or disables (0) objects lighting/shading. Setting this value to -1 goes back to the default mode (globally set at the view/scene level).

    :param int smooth_shading:
      (tristate: 0/1/-1) smooth or flat polygons mode

    :param int polygon_filtering:
      (tristate: 0/1/-1) filtering (antialiasing) of lines/polygons

    :param int depth_buffer:
      (tristate: 0/1/-1) enables/disables writing in the Z-buffer. You can disable it if you want to click "through" an object (but it may have strange effects on the rendering)

    :param int face_culling:
      (tristate: 0/1/-1) don't draw polygons seen from the back side. The best is to enable it for transparent objects, and to disable it for "open" (on which both sides may be seen) and opaque meshes. For objects both open and transparent, there is no perfoect setting...

    :param string polygon_mode:
      polygons rendering mode: "normal", "wireframe", "outline" (normal + wireframe), "hiddenface_wireframe" (wireframe with hidden faces), "default" (use the global view settings), "ext_outlined" (thickened external boundaries + normal rendering).

    :param unlit_color:
      color used for lines when lighting is off. For now it only affects polygons boundaries in "outlined" or "ext_outlined" polygon modes.
    :type unlit_color: RGB[A] vector: float values between 0 and 1.

    :param float line_width:
      Lines thickness (meshes, segments, wireframe rendering modes). A null or negative value fallsback to default (1 in principle).

    :param string front_face:
      Specifies if the mesh(es) polygons external face is the clockwise or counterclockwise side. Normally in Aims/Anatomist indirect referentials, polygons are in clockwise orientation. Values are "clockwise", "counterclockwise", or "neutral" (the default).

    :param string selectable_mode:
      New in Anatomist 4.5.
      Replaces the ghost property.
      always_selectable: object is selecatble whatever its opacity.
      ghost: object is not selectable.
      selectable_when_opaque: object is selectable when totally opaque (this is the default in Anatomist).
      selectable_when_not_totally_transparent: object is selectable unless opacity is zero.
    """
    if material is not None:
      if ambient is None:
        ambient = material.ambient
      if diffuse is None:
        diffuse = material.diffuse
      if emission is None:
        emission = material.emission
      if specular is None:
        specular = material.specular
      if shininess is None:
        shininess = material.shininess
      if lighting is None:
        lighting = material.lighting
      if smooth_shading is None:
        smooth_shading = material.smooth_shading
      if polygon_filtering is None:
        polygon_filtering = material.polygon_filtering
      if depth_buffer is None:
        depth_buffer = material.depth_buffer
      if face_culling is None:
        face_culling = material.face_culling
      if polygon_mode is None:
        polygon_mode = material.polygon_mode
      if unlit_color is None:
        unlit_color = material.unlit_color
      if line_width is None:
        line_width = material.line_width
      if front_face is None:
        front_face = material.front_face
      if selectable_mode is None:
        selectable_mode = material.selectable_mode
    self.execute("SetMaterial", objects=self.makeList(objects), ambient=ambient, diffuse=diffuse, emission=emission, specular=specular, shininess=shininess, refresh=refresh, lighting=lighting, smooth_shading=smooth_shading, polygon_filtering=polygon_filtering, depth_buffer=depth_buffer, face_culling=face_culling, polygon_mode=polygon_mode, unlit_color=unlit_color, line_width=line_width, selectable_mode=selectable_mode, front_face=front_face)

  def setObjectPalette(self, objects, palette=None, minVal=None, maxVal=None, palette2=None,  minVal2=None, maxVal2=None, mixMethod=None, linMixFactor=None, palette1Dmapping=None, absoluteMode=False):
    """
    Assign a palette to objects

    :param objects:
      Assign palette parameters to these objects
    :type objects: list of :py:class:`AObject`

    :param palette:
      Principal palette to apply
    :type palette: :py:class:`APalette` or string (name)

    :param minVal:
      Palette value to assign to objects texture min value (proportionally to palette's limits)
    :type minVal: float (0 - 1)

    :param maxVal:
      Palette value to assign to objects texture max value
    :type maxVal: float (0 - 1)

    :param palette2:
      Second palette, for 2D textures
    :type palette2: :py:class:`APalette`

    :param minVal2:
      Second palette value to affect to object texture second component min value
    :type minVal2: float (0 - 1)

    :param maxVal2:
      Second palette value to assign to object texture second component max value
    :type maxVal2: float (0 - 1)

    :param string mixMethod:
      Method to mix two palettes in a 2D palette : linear or geometric

    :param float linMixFactor:
      mix factor for the linear method

    :param string palette1Dmapping:
      way of using 2D palette for 1D texture : FirstLine or Diagonal

    :param boolean absoluteMode:
      if *True*, min/max values are supposed to be absolute values (in regard to objects texture) rather than proportions
    """
    if isinstance(palette, self.APalette):
        palette = palette.name
    self.execute('SetObjectPalette', objects = self.makeList(objects),
                 palette = palette, palette2 = palette2, min=minVal,
                 max=maxVal, min2=minVal2, max2=maxVal2, mixMethod=mixMethod,
                 linMixFactor=linMixFactor, palette1Dmapping=palette1Dmapping,
                 absoluteMode=int(absoluteMode))

  ###############################################################################
  # application control
  def createControlWindow(self):
    """
    Creates anatomist main window. Currently it is done automatically.
    """
    self.execute('CreateControlWindow')

  def close(self):
    """
    Exits Anatomist application.
    if anatomist is closed, the singleton instance is deleted.
    So next time the constructor is called, a new instance will be created.
    """
    try:
      delattr(self.__class__, "_singleton_instance")
      self.execute('Exit')
    except:  # may fail if it is already closed
      pass

  def setGraphParams(self, display_mode=None, label_attribute=None, save_only_modified=None, saving_mode=None, selection_color=None, selection_color_inverse=None, set_base_directory=None, show_tooltips=None, use_nomenclature=None):
    """
    Modifies graphs and selections options.

    :param string display_mode:
      Paint mode of objects in graph nodes : mesh, bucket, all, first

    :param string label_attribute:
      Selects the attribute used as selection filter: label or name

    :param save_only_modified:
      If enabled, graph save saves not all sub objects but only those that have been modified.
    :type save_only_modified: boolean int (0/1)

    :param string saving_mode:
      Graph saving mode : unchanged (keep the reading format), global (1 file for all same category sub-objects), or local (1 file per sub-object)

    :param selection_color:
      Selected objects color : R G B [A [NA]] (A opacity, NA: 0/1 use object's opacity parameter)
    :type selection_color: int vector

    :param selection_color_inverse:
      Selection inverses color instead of using selection_color
    :type selection_color_inverse: boolean int (0/1)

    :param set_base_directory:
      Save subobjects in a directory <graph name>.data
    :type set_base_directory: boolean int (0/1)

    :param show_tooltips:
      Show graph nodes names in tooltips
    :type show_tooltips: boolean int (0/1)

    :param use_nomenclature:
      Enable graph coloring with nomenclature
    :type use_nomenclature: boolean int (0/1)
    """
    self.execute('GraphParams', display_mode=display_mode, label_attribute=label_attribute, save_only_modified=save_only_modified, saving_mode=saving_mode, selection_color=selection_color, selection_color_inverse=selection_color_inverse, set_base_directory=set_base_directory, show_tooltips=show_tooltips, use_nomenclature=use_nomenclature)

  def setPaintParams( self, brush_size=None, brush_type=None,
    follow_linked_cursor=None, line_mode=None, millimeter_mode=None,
    replace_mode=None, region_transparency=None ):
    """
    Setup Paint contol parameters.
    All parameters are optional.

    :param float brush_size: Radius of the paint brush, either in millimeters or in voxels, depending on the millimeter_mode.

    :param string brush_type: "point", "square", "disk", or "sphere". "ball" is an alias for sphere.

    :param boolean follow_linked_cursor: Linked cursor moving with brush

    :param boolean line_mode: line interpolation mode between brush strokes

    :param boolean millimeter_mode: brush size can be either in mm or in voxels. In voxels mode, the brush may be anisotropic.

    :param boolean replace_mode: region replacing mode (when drawing on a different region)

    :param float region_transparency: value of the region transparency
    """
    if follow_linked_cursor is not None:
      follow_linked_cursor = int( follow_linked_cursor )
    if line_mode is not None:
      line_mode = int( line_mode )
    if millimeter_mode is not None:
      millimeter_mode = int( millimeter_mode )
    if replace_mode is not None:
      replace_mode = int( replace_mode )
    self.execute( 'PaintParams', brush_size=brush_size,
      brush_type=brush_type, follow_linked_cursor=follow_linked_cursor,
      line_mode=line_mode, millimeter_mode=millimeter_mode,
      replace_mode=replace_mode, region_transparency=region_transparency )

  ###############################################################################
  # commands sending
  def execute( self, command, **kwargs ):
    """
    Executes a command in anatomist application. It should be a command that can be processed by Anatomist command processor.
    The list of available commands is in http://brainvisa.info/doc/anatomist/html/fr/programmation/commands.html.
    Parameters are converted before sending the request to anatomist application.

    :param string command:
      Name of the command to execute.

    :param dictionary kwargs:
      Parameters for the command
    """
    def ununderscore(k):
      # this removes a trailing '_' from params names
      # it allows to used reserved words as params, like raise, by appending
      # an underscore, like in PyQt4:
      # a.execute( 'WindowConfig', windows=[w], raise_=1 )
      if k.endswith( '_' ):
        return k[:-1]
      return k
    params=dict((ununderscore(k),self.convertParamsToIDs(v))
                for k, v in six.iteritems(kwargs) if v is not None)
    self.logCommand(command, **params )
    self.send(command, **params)

  def logCommand(self, command, **kwargs):
    pass

  def logEvent(self, event, params):
    pass


  def makeList( thing ):
    """
    Transforms the argument into a list: a list with one element if it is
    not a sequence, or return the input sequence if it is already one
    """
    if isSequenceType( thing ):
      try:
        if thing.__module__.startswith( 'anatomist.' ):
          return [ thing ]
      except:
        pass
      return thing
    return [ thing ]
  makeList = staticmethod( makeList )

  def convertSingleObjectParamsToIDs( self, item ):
    """
    Converts current api object to corresponding anatomist object representation.

    :param item:
      Element to convert
    :type item: :py:class:`AItem`

    :rtype: *dictionary* or *list*
    :returns:
      Converted elements
    """
    if isinstance( item, Anatomist.AItem ) :
      return item.getInternalRep()
    elif isinstance( item, ( basestring, int, float, dict ) ):
      return item
    raise TypeError( 'Expecting an Anatomist object but got one of type %s' % repr( type( item ) )  )


  def convertParamsToIDs( self, params ):
    """
    Converts current api objects to corresponding anatomist object representation.
    This method must be called before sending a command to anatomist application on command parameters.

    :param params:
      Elements to convert
    :type params: dictionary or list

    :returns:
      Converted elements
    :rtype: dictionary or list
    """
    if not isinstance( params, basestring ) \
        and isSequenceType( params ):
      return [self.convertSingleObjectParamsToIDs(i) for i in params]
    else:
      return self.convertSingleObjectParamsToIDs( params )

  def send( self, command, **kwargs ):
      """
      Sends a command to anatomist application. Call this method if there's no answer to get.
      This method depends on the mean of communication with anatomist. Must be redefined in implementation api.

      :param string command:
        Name of the command to execute. Any command that can be processed by anatomist command processor.
        The complete commands list is in http://brainvisa.info/doc/anatomist/html/fr/programmation/commands.html

      :param dictionary kwargs:
        Parameters for the command
      """
      pass

  def newItemRep(self):
      """
      Creates a new item representation.
      This method depends on the mean of communication with anatomist. Must be redefined in implementation api.
      """
      pass

  def sync(self):
    """
    Wait for anatomist finishing current processing.
    """
    pass

  def waitEndProcessing(self):
    """
    Deprecated. Use method sync instead.
    """
    self.sync()

  ###############################################################################
  # logs

  def  log( self, message ):
    """
    Use this method to print a log message.
    This method prints on standard output. To be redefined for another type of log.
    """
    print(message)

  ###############################################################################
  class AItem(object):
    """
    Base class for representing an object in Anatomist application.

    :param anatomistinstance:
      Reference to Anatomist object which created this object.
      Useful because some methods defined in AItem objects will need to send a command to the Anatomist application.
    :type anatomistinstance: :py:class:`Anatomist`

    :param object internalRep:
      Representation of this object in anatomist application.

    :param bool ref:
      Indicates if a reference has been taken on the corresponding anatomist object. If *True*, the reference is released on deleting this item.

    :param string refType:
      Type of reference taken on the object : ``Weak`` (reference counter not incremented), ``WeakShared`` (reference counter incremented but the object can be deleted even if it remains references) or ``Strong`` (reference counter is incremented, the object cannot be deleted since there are references on it). If it is not specified, :py:data:`anatomist.base.Anatomist.defaultRefType` is used.

    """
    def __init__( self, anatomistinstance, internalRep=None, refType=None, *args, **kwargs ):
      super(Anatomist.AItem, self).__init__(*args, **kwargs)
      self.anatomistinstance = anatomistinstance
      self.refType=refType
      if internalRep is None:
        internalRep=anatomistinstance.newItemRep()
      if isinstance( internalRep, Anatomist.AItem ):
        # avoid recursion
        self.internalRep = internalRep.internalRep
      else:
        self.internalRep = internalRep
      self.ref=False

    def __repr__(self):
      """
      String representation of the object.
      """
      return str(self.internalRep)

    def __cmp__(self, other):
      """
      Called on comparison operations between self and other.
      Their internalRep is compared.

      :returns:
        -1 if self < other, 0 if self == other, 1 if self > other
      :rtype: int
      """
      if not isinstance(other, Anatomist.AItem):
        return 1
      if self.internalRep == other.internalRep:
        return 0
      elif self.internalRep < other.internalRep:
        return -1
      else:
        return 1

    def __eq__(self, other):
      """
      Equality operator for python3
      """
      if not isinstance(other, Anatomist.AItem):
        return False
      return self.internalRep == other.internalRep

    def __lt__(self, other):
      """
      Comparison operator for python3
      """
      if not isinstance(other, Anatomist.AItem):
        return False
      return self.internalRep < other.internalRep

    def __gt__(self, other):
      """
      Comparison operator for python3
      """
      if not isinstance(other, Anatomist.AItem):
        return False
      return self.internalRep > other.internalRep

    def getInfos(self):
      """
      Gets informations about this object.

      :returns:
        information about the object (property -> value)
      :rtype: dictionary
      """
      pass

    def takeRef(self):
      """
      Take a reference on this object.
      """
      #print "take ref ", self.refType, self, self.__class__
      self.ref=True

    def releaseRef(self):
      """
      Release a reference on this object.
      """
      #print "release ref", self, self.__class__
      self.ref=False

    def releaseAppRef(self):
      """
      Release anatomist application reference on this object : so object life is controled by references on it. If there is no more references on the object, it is deleted.
      Used when an object is created by python api. It is not owned by anatomist application.
      """
      pass

    def takeAppRef(self):
      """
      Take anatomist application reference on this object : so object life is controled the normal way by Anatomist.
      Inverse of releaseAppRef(). The object is now owned by anatomist application.
      """
      pass

    def getRef(self, refType):
      """
      Get a reference of type *refType* on this object.

      :returns:
        A copy of current object with a reference of type refType on anatomist object.
      :rtype: :py:class:`anatomist.base.Anatomist.AItem`
      """
      #print "get ref ", self, self.__class__
      return self.__class__(self.anatomistinstance, self.getInternalRep(), refType)

    def __del__(self):
      """
      Called when current object is deleted (when it is no more referenced). If a reference had been taken on anatomist corresponding object, it is released.
      """
      #print "del ", self, self.__class__
      if self.ref:
        try: # can fail if Anatomist is already closed
          self.releaseRef()
        except:
          pass

    def getInternalRep(self):
      """
      Returns internal representation of the object (implementation dependant).
      """
      return self.internalRep

    def makeList( self, objects ):
      return self.anatomistinstance.makeList( objects )

  #############################################################################
  class AObject(AItem):
    """
    Represents an object in Anatomist application.

    Following information can be obtained using ObjectInfo command :

    :param string objectType:
      object type. For example : volume, bucket, graph, texture...

    :param children:
      List of objects which are children of current object (for example: nodes in a graph). Can be empty.
    :type children: list of :py:class:`anatomist.base.Anatomist.AObject`

    :param string filename:
      Name of the file from which the object has been loaded. May be *None*.

    :param string name:
      Name of the object presented in Anatomist window.

    :param boolean copy:
      *True* indicates that this object is a copy of another object, otherwise it is the original object.

    :param material:
      Object's material parameters
    :type material: :py:class:`anatomist.base.Anatomist.Material`

    :param referential:
      Referential assigned to this object.
    :type referential: :py:class:`anatomist.base.Anatomist.Referential`
    """
    def __init__(self, anatomistinstance, internalRep=None, *args, **kwargs):
      """
      If internal rep is given in parameter, the corresponding anatomist object already exists : take a reference on it (to prevent its deletion).
      """
      super(Anatomist.AObject, self).__init__(anatomistinstance, internalRep, *args, **kwargs)
      if internalRep is not None:
        self.takeRef()

    def getWindows(self):
      """
      Gets windows that contain this object.

      :returns:
        Opened windows that contain this object.
      :rtype: list of :py:class:`anatomist.base.Anatomist.AWindow`
      """
      allWindows=self.anatomistinstance.importWindows()
      windows=[]
      for w in allWindows:
        objs=w.objects
        if self in objs:
          windows.append(w)
      return windows

    # object manipulation
    def addInWindows(self, windows, temporary=False, position=-1):
      """
      Adds the object in windows.
      Windows must already exist.

      Parameters
      ----------
      windows: list of :py:class:`anatomist.base.Anatomist.AWindow`
          List of windows in which the object must be added
      temporary: bool (optional)
          temporary object do not affect the view boundaries and camera
          settings
      position: int (optional)
          insert objects as this order number
      """
      self.anatomistinstance.addObjects([self], windows, temporary=temporary,
                                        position=position)

    def removeFromWindows(self, windows):
      """
      Removes object from windows.

      :param windows:
        List of windows from which the object must be removed
      :type windows: list of :py:class:`anatomist.base.Anatomist.AWindow`
      """
      self.anatomistinstance.removeObjects([self], windows)

    def delete(self):
      """
      Deletes object
      """
      self.anatomistinstance.deleteObjects([self])

    def assignReferential(self, referential):
      """
      Assign a referential to object.
      The referential must exist. To create a new Referential, execute createReferential,
      to assign the central referential, first get it with Anatomist.centralRef attribute.

      :param referential:
        The referential to be assigned to the object
      :type referential: :py:class:`anatomist.base.Anatomist.Referential`
      """
      self.anatomistinstance.assignReferential(referential, [self])

    def loadReferentialFromHeader(self):
      """
      Extract information about referential and transformations from the header of the object and assign the found referential.
      """
      self.anatomistinstance.loadReferentialFromHeader([self])

    applyBuiltinReferential = loadReferentialFromHeader

    def setMaterial(self, material=None, refresh=None, ambient=None,
      diffuse=None, emission=None, specular=None, shininess=None,
      lighting=None, smooth_shading=None, polygon_filtering=None,
      depth_buffer=None, face_culling=None, polygon_mode=None,
      unlit_color=None, line_width=None, ghost=None, front_face=None,
      selectable_mode=None):
      """
      Changes object material properties.

      :param material:
        Material characteristics, including render properties.
        The material may be specified as a Material object, or as its various
        properties (ambient, diffuse, etc.). If both a material parameter and
        other properties are specified, the material is used as a base, and
        properties are used to modify it
      :type material: :py:class:`anatomist.base.Anatomist.Material`

      :param bool refresh:
        If *True*, force windows refreshing

      :param ambient:
      :type ambient: RGB[A] vector: float values between 0 and 1.

      :param list diffuse:
        This parameter corresponds to the "standard" notion of color
      :type diffuse: RGB[A] vector: float values between 0 and 1.

      :param emission:
      :type emission: RGB[A] vector: float values between 0 and 1.

      :param specular:
      :type specular: RGB[A] vector: float values between 0 and 1.

      :param float shininess:
        0-124

      :param boolaen lighting:
        enables (1) or disables (0) objects lighting/shading. Setting this value to -1 goes back to the default mode (globally set at the view/scene level).

      :param int smooth_shading:
        (tristate: 0/1/-1) smooth or flat polygons mode

      :param int polygon_filtering:
        (tristate: 0/1/-1) filtering (antialiasing) of lines/polygons

      :param int depth_buffer:
        (tristate: 0/1/-1) enables/disables writing in the Z-buffer. You can disable it if you want to click "through" an object (but it may have strange effects on the rendering)

      :param int face_culling:
        (tristate: 0/1/-1) don't draw polygons seen from the back side. The best is to enable it for transparent objects, and to disable it for "open" (on which both sides may be seen) and opaque meshes. For objects both open and transparent, there is no perfoect setting...

      :param string polygon_mode:
        polygons rendering mode: "normal", "wireframe", "outline" (normal + wireframe), "hiddenface_wireframe" (wireframe with hidden faces), "default" (use the global view settings), "ext_outlined" (thickened external boundaries + normal rendering).

      :param unlit_color:
        color used for lines when lighting is off. For now it only affects polygons boundaries in "outlined" or "ext_outlined" polygon modes.
      :type unlit_color: RGB[A] vector: float values between 0 and 1.

      :param float line_width:
        Lines thickness (meshes, segments, wireframe rendering modes). A null or negative value fallsback to default (1 in principle).

      :param string front_face:
        Specifies if the mesh(es) polygons external face is the clockwise or counterclockwise side. Normally in Aims/Anatomist indirect referentials, polygons are in clockwise orientation. Values are "clockwise", "counterclockwise", or "neutral" (the default).

      :param string selectable_mode:
        New in Anatomist 4.5.
        Replaces the ghost property.
        always_selectable: object is selecatble whatever its opacity.
        ghost: object is not selectable.
        selectable_when_opaque: object is selectable when totally opaque (this is the default in Anatomist).
        selectable_when_not_totally_transparent: object is selectable unless opacity is zero.

      """
      self.anatomistinstance.setMaterial([self], material, refresh,
      ambient, diffuse, emission, specular, shininess, lighting,
      smooth_shading, polygon_filtering, depth_buffer, face_culling,
      polygon_mode, unlit_color, line_width, ghost=None,
      front_face=front_face, selectable_mode=selectable_mode)

    def setPalette(self, palette=None, minVal=None, maxVal=None, palette2=None,  minVal2=None, maxVal2=None, mixMethod=None, linMixFactor=None, palette1Dmapping=None, absoluteMode=False):
      """
      Assign a palette to object

      :param palette:
        Principal palette to apply
      :type palette: :py:class:`anatomist.base.Anatomist.APalette` or string (name)

      :param minVal:
        Palette value to assign to objects texture min value (proportionally to palette's limits)
      :type minVal: float (0 - 1)

      :param maxVal:
        Palette value to assign to objects texture max value
      :type maxVal: float (0 - 1)

      :param palette2:
        Second palette, for 2D textures
      :type palette2: :py:class:`APalette`

      :param minVal2:
        Second palette value to affect to object texture second component min value
      :type minVal2: float (0 - 1)

      :param maxVal2:
        Second palette value to assign to object texture second component max value
      :type maxVal2: float (0 - 1)

      :param string mixMethod:
        Method to mix two palettes in a 2D palette : linear or geometric

      :param float linMixFactor:
        mix factor for the linear method

      :param string palette1Dmapping:
        way of using 2D palette for 1D texture : FirstLine or Diagonal

      :param boolean absoluteMode:
        if *True*, min/max values are supposed to be absolute values (in regard to objects texture) rather than proportions
      """
      self.anatomistinstance.setObjectPalette([self], palette, minVal, maxVal, palette2,  minVal2, maxVal2, mixMethod, linMixFactor, palette1Dmapping,
      absoluteMode=absoluteMode)

    def extractTexture(self, time=None):
      """
      Extract the object texture to create a new texture object.

      :param float time:
        For temporal objects, if this parameter is mentionned the texture will be extracted at this time. if not mentionned,
        All times will be extracted and the texture will be a temporal object.
        In socket implementation, it is necessary to get a new id for the texture object and to pass it to the command.

      :returns:
        The newly created texture object
      :rtype: :py:class:`anatomist.base.Anatomist.AObject`
      """
      pass

    def generateTexture(self, dimension=1):
      """
      Generates an empty texture (value 0 everywhere) for a mesh object.

      :param int dimension:
        Texture dimension (1 or 2)

      :returns:
        The newly created texture object
      :rtype: :py:class:`anatomist.base.Anatomist.AObject`
      """
      pass

    def exportTexture(self, filename, time=None):
      """
      Saves the texture of an object to a file

      :param string filename:
        File in which the texture must be written

      :param float time:
        For temporal objects, if this parameter is mentionned the texture will be extracted at this time. if not mentionned,
        all times will be extracted and the texture will be a temporal object.
      """
      self.anatomistinstance.execute("ExportTexture", filename=filename, object=self, time=time)

    def save(self, filename=None):
      """
      Saves object in file.

      :param string filename:
        File in which the object will be written. If not mentionned, the object is saved in the file from which it has been loaded.
      """
      self.anatomistinstance.execute("SaveObject", object=self, filename=filename)

    def reload(self):
      """
      Reload this object already in memory reading its file.
      """
      self.anatomistinstance.reloadObjects([self])

  ###############################################################################
  class AGraph(AObject):
    """
    Graph object in Anatomist.
    """
    def __init__(self, anatomistinstance, internalRep=None, *args, **kwargs):
      super(Anatomist.AGraph, self).__init__(anatomistinstance, internalRep, *args, **kwargs)

    def createNode(self, name=None, syntax=None, with_bucket=None, duplicate=True ):
      """
      Creates a new node with optionally an empty bucket inside and adds it in the graph.

      :param string name:
        node name. default is ``RoiArg``.

      :param string syntax:
        node syntax attribute. default is ``roi``.

      :param bool with_bucket:
        if *True*, creates an empty bucket in the node and returns it with the node. default is None, so the bucket is created but not returned

      :param bool duplicate:
        enables duplication of nodes with the same name attribute.

      :returns:
        (the created node, the created bucket) or only the created node if with_bucket is False
      """
      pass

  ###############################################################################
  class AWindow(AItem):
    """
    Represents an anatomist window.

    .. py:attribute:: windowType

      Windows type (``'axial'``, ``'sagittal'``, ...)

    .. py:attribute:: group

      :py:class:`anatomist.base.Anatomist.AWindowsGroup`. The group which this window belongs to.

    .. py:attribute:: objects

      List of :py:class:`anatomist.base.Anatomist.AObject`. The window contains these objects.

    .. py:attribute:: block

      :py:class:`anatomist.base.Anatomist.AWindowsBlock`. The block in which the window is contained, None if it is not in a block.

    """
    def __init__(self, anatomistinstance, internalRep=None, *args, **kwargs):
      """
      If internal rep is given in parameter, the corresponding anatomist window already exists : take a reference on it (to prevent its deletion).
      """
      super(Anatomist.AWindow, self).__init__(anatomistinstance, internalRep, *args, **kwargs)
      if internalRep is not None:
        self.takeRef()
      # We need to keep a reference on the windows block in which the window is to prevent it to be deleted before the window.
      # Indeed, there is no reference count for windows blocks, they are only classical QWidgets.
      self.block=None

    def addObjects(self, objects, add_children=False, add_graph_nodes=True,
      add_graph_relations=False, temporary=False, position=-1):
      """
      Adds objects in window.

      Parameters
      ----------
      objects: list of :py:class:`anatomist.base.Anatomist.AObject`
          List of objects to add
      temporary: bool (optional)
          temporary object do not affect the view boundaries and camera
          settings
      position: int (optional)
          insert objects as this order number
      """
      self.anatomistinstance.addObjects(objects, [self], add_children,
        add_graph_nodes, add_graph_relations, temporary=temporary,
        position=position)

    def removeObjects(self, objects):
      """
      Removes objects from window.

      :param objects:
        List of objects to remove
      :type objects: list of :py:class:`anatomist.base.Anatomist.AObject`
      """
      self.anatomistinstance.removeObjects(objects, [self])

    def camera(self, zoom=None, observer_position=None, view_quaternion=None,
      slice_quaternion=None, force_redraw=None, cursor_position=None,
      boundingbox_min=None, boundingbox_max=None, slice_orientation=None):
      """
      Sets the point of view, zoom, cursor position for a 3D window.

      :param float zoom:
        Zoom factor, default is 1

      :param observer_position:
        Camera position
      :type observer_position: float vector, size 3

      :param view_quaternion:
        View rotation
      :type view_quaternion: float vector, size 4, normed

      :param slice_quaternion:
        Slice plan rotation
      :type slice_quaternion: float vector, size 4, normed

      :param boolean force_redraw:
        If *True*, refresh printing immediatly, default is *False*

      :param cursor_position:
        Linked cursor position
      :type cursor_position: float vector

      :param boundingbox_min:
        Bounding box min values
      :type boundingbox_min: float vector

      :param boundingbox_max:
        Bounding box max values
      :type boundingbox_max: float vector

      :param slice_orientation:
        Slice plane orientation, normal to the plane
      :type slice_orientation: float vector, size 3
      """
      self.anatomistinstance.camera([self], zoom, observer_position,
        view_quaternion, slice_quaternion, force_redraw, cursor_position,
        boundingbox_min, boundingbox_max, slice_orientation=slice_orientation)

    def windowConfig(self, clipping=None, clip_distance=None,
                     cursor_visibility=None, face_culling=None,
                     flat_shading=None, fog=None, geometry=None, iconify=None,
                     light=None, linkedcursor_on_slider_change=None,
                     perspective=None, polygon_filtering=None,
                     polygon_mode=None, polygons_depth_sorting=None,
                     raise_window=None, record_basename=None, record_mode=None,
                     snapshot=None, transparent_depth_buffer=None,
                     view_size=None, fullscreen=None,
                     show_cursor_position=None, show_toolbars=None):
      """Settings for windows (includes various settings)

      Parameters
      ----------
      clipping: int (optional)
          number of clipping planes: 0, 1 or 2
      clip_distance: float (optional)
          distance between the slice plane and the clipping planes
      cursor_visibility: int (optional)
          makes visible (1) or invisible (0) the linked cursor in the chosen
          windows. The value -1 sets back the global setting (of the
          preferences)
      face_culling: int (optional)
          enables (1) or disables (0) the elimination of polygons seen from the
          bottom face
      flat_shading: int (optional)
          enables (1) or disables (0) rendering in "flat shading" mode (without
          color smoothing)
      fog: int (optional)
          enables (1) or disables (0) fog
      geometry: list of int (optional)
          position and size of the window (external size). If sizes are zero or
          not specified, the current window size is not changed
      iconify: int (optional)
          iconifies (or hides) windows
      light: dict (optional)
          Windows lighting settings. This dictionary may include the following
          parameters:
              * ambient: ambiant lighting settings (list of float, 4 elements)
              * diffuse: diffuse lighting settings (list of float, 4 elements)
              * specular: specular lighting settings (list of float, 4
                elements)
              * background: background color (list of float, 4 elements)
              * position: light position (list of float, 4 elements)
              * spot_direction: spot light direction (list of float, 3
                elements)
              * spot_exponent: spot light intensity exponent (float)
              * spot_cutoff: spot light cutoff angle (float)
              * attenuation_offset: light attenuation, offset part (float)
              * attenuation_linear: light attenuation, linear coefficient
                (float)
              * attenuation_quadratic: light attenuation, quadratic coefficient
                (float)
              * model_ambient: don't really know... (list of float, 4 elements)
              * model_local_viewer: don't really know... (float)
              * model_two_side: don't really know (float)
      linkedcursor_on_slider_change: int (optional)
          enables or disables the mode when slice/time sliders act as linked
          cursor actions (with propagation to other views)
      perspective: int (optional)
          enables (1) or disables (0) the perspective rendering mode
      polygon_filtering: int (optional)
          enables (1) or disables (0) polygons and lines smoothing (anti-
          aliasing)
      polygon_mode: string (optional)
          polygons rendering mode: "normal", "wireframe", "outline" (normal +
          wireframe), "hiddenface_wireframe" (wireframe with hidden faces)
      polygons_depth_sorting: int (optional)
          enables (1) or disables (0) polygons sortig along depth on
          transparent objects to allow a better rendering. This mode has a
          large impact on performances, so use it with care.
      raise_window: int (optional)
          unicognifies windows and make them move to the top of the desktop.
          Note that this parameter has a different name as the anatomist
          command interface (is was "raise" there) because "raise" is a
          reserved keyword in Python and cannot be used here.
      record_basename: string (optional):
          base filename of images written using the film recording mode (ex:
          /tmp/toto.jpg). Images will actually have numbers appended before the
          extension
      record_mode: int (optional)
          enables (1) or disables (0) the images recording mode (film) of 3D
          windows. To enable it, record_basename must also be specified
      snapshot: string (optional)
          Saves the image of the view in the specified file. If windows
          contains several values, then several images have to be saved: in
          this case, snapshot is a list of filenames separated by space
          characters: so the file name/path must not contain any space
          character (this restriction doesn't apply if a single window is
          used). Node: escape character ("\ ") are not supported yet.
      transparent_depth_buffer: int (optional)
          enables (1) or disables (0) writing of transparent objects in the
          depth buffer. Useful if you want to click across transparents objects
          (but the rendering can be wrong)
      view_size: list of int (optional)
          size of the rendering zone (3D rendering widget). This parameter has
          a higher priority than sizes given using geometry if both are
          specified
      fullscreen: int (optional)
          enables or disables the fullscreen mode
      show_cursor_position: int (optional)
          shows or hides the status bar at the bottom of the window, showing
          the cursor position and a current object value at this position.
      show_toolbars: int (optional)
          shows or hides everything around the 3D view (menus, buttons bars,
          status bar, referential...)
      """
      self.anatomistinstance.execute(
        "WindowConfig", windows=[self], clipping=clipping,
        clip_distance=clip_distance,
        cursor_visibility=cursor_visibility, face_culling=face_culling,
        flat_shading=flat_shading, fog=fog, geometry=geometry, iconify=iconify,
        light=light,
        linkedcursor_on_slider_change=linkedcursor_on_slider_change,
        perspective=perspective, polygon_filtering=polygon_filtering,
        polygon_mode=polygon_mode,
        polygons_depth_sorting=polygons_depth_sorting,
        raise_=raise_window, record_basename=record_basename,
        record_mode=record_mode, snapshot=snapshot,
        transparent_depth_buffer=transparent_depth_buffer,
        view_size=view_size, fullscreen=fullscreen,
        show_cursor_position=show_cursor_position, show_toolbars=show_toolbars)

    def snapshot(self, filename):
      """Take a snapshot of the window 3D contents and save it into a file

      Equivalent to:

      ::

         window.windowConfig(snapshot=filename)

      Parameters
      ----------
      filename: string
          file name to save the snapshot into
      """
      self.anatomistinstance.execute("WindowConfig", windows=[self],
                                     snapshot=filename)

    def assignReferential(self, referential):
      """
      Assign a referential to window.
      The referential must exist. To create a new Referential, execute
      createReferential,
      to assign the central referential, first get it with Anatomist.centralRef
      attribute.

      :param referential:
        The referential to assign to objects and/or windows
      :type referential: :py:class:`anatomist.base.Anatomist.Referential`
      """
      self.anatomistinstance.assignReferential(referential, [self])

    def getReferential( self ):
      """
      Get the referential attached to the window (the coordinates system used
      for 3D positions in this window)
      """
      pass


    def moveLinkedCursor(self, position):
      """
      Changes cursor position in this window and all linked windows (same group).

      :param position:
        Cursor new position
      :type position: float vector, size 3
      """
      self.anatomistinstance.execute("LinkedCursor", window=self, position=position)

    def showToolbox(self, show=True):
      """
      Shows or hides the toolbox frame of a window.

      :param boolean show:
        If *True*, the window's toolbox frame is shown, else it is hidden.
      """
      if show:
        show=1
      else: show=0
      self.anatomistinstance.execute("ControlsParams", window=self, show=show)

    def setControl(self, control):
      """
      Changes the selected button in windows menu.
      Examples of controls : ``'PaintControl'``, ``'NodeSelectionControl'``, ``'Default 3D Control'``, ``'Selection 3D'``, ``'Flight Control'``, ``'ObliqueControl'``, ``'TransformationControl'``, ``'CutControl'``, ``'Browser Selection'``, ``'RoiControl'``...
      """
      self.anatomistinstance.setWindowsControl(windows=[self], control=control)

    def close(self):
      """
      Closes window.
      """
      self.anatomistinstance.closeWindows([self])

    def activateAction(self, action_type, method, **kwargs):
      """
      Triggers window action activation.

      New in Anatomist 4.5.

      Parameters
      ----------
      action_type:  str (mandatory)
          type of action: "key_press", "key_release", "mouse_press", 
          "mouse_release", "mouse_double_click", "mouse_move". Additional
          parameters depend on the action type:
          * key actions do not use any;
          * mouse actions need x and y keyword parameters
      method:  str (mandatory)
          action method name, as registered in the active control. Deteremines
          what will actually be done.
      x:  int (optional)
          x mouse coord, for mouse actions only.
      y:  int (optional)
          y mouse coord, for mouse actions only.
      """
      self.anatomistinstance.execute('ActivateAction', window=self,
        action_type=action_type, method=method, **kwargs)

  #############################################################################
  class AWindowsBlock(AItem):
    """
    A window containing other windows.

    :param int nbCols:
      Number of columns of the windows block
    """
    def __init__(self, anatomistinstance=None, internalRep=None, nbCols=0,
      nbRows=0, *args, **kwargs):
      super(Anatomist.AWindowsBlock, self).__init__(anatomistinstance, internalRep, *args, **kwargs)
      self.nbCols = nbCols
      self.nbRows = nbRows

    def setColumns( self, nCol ):
      self.nbCols = nCol
      self.rnRows = 0
      self.anatomistinstance.execute( 'WindowBlock', block=self.internalRep,
        block_columns=nCol )

    def setRows( self, nRow ):
      self.nbRows = nRow
      self.nbCols = 0
      self.anatomistinstance.execute( 'WindowBlock', block=self.internalRep,
        block_rows=nRow )

    def arrangeInRect( self, widthHeightRatio=1. ):
      self.anatomistinstance.execute( 'WindowBlock', block=self.internalRep,
        make_rectangle=1, rectangle_ratio=widthHeightRatio )

  ###############################################################################
  class AWindowsGroup(AItem):
    """
    A group containing several windows which are linked. Moving cursor in one window moves it in all linked windows.
    Its internalRep is the group id (int).
    """
    def __init__(self, anatomistinstance, internalRep=None, *args, **kwargs):
      super(Anatomist.AWindowsGroup, self).__init__(anatomistinstance, internalRep, *args, **kwargs)

    def getSelection(self):
      """
      :retutns:
        Objects that are selected in this windows group
      :rtype: list of :py:class:`anatomist.base.Anatomist.AObject`
      """
      return self.anatomistinstance.getSelection(self)

    def isSelected(self, object):
      """
      :param object:
        An object in this windows group
      :type object: :py:class:`anatomist.base.Anatomist.AObject`

      :returns:
        *True* if the object is selected in this windows group
      :rtype: bool
      """
      selectedObjects=self.getSelection()
      return (selectedObjects is not None) and (object in selectedObjects)

    def setSelection(self, objects):
      """
      Initializes selection with given objects for this windows group.

      :param objects:
        Objects to select
      :type objects: list of :py:class:`anatomist.base.Anatomist.AObject`
      """
      self.anatomistinstance.execute("Select", objects=self.makeList(objects), group=self, modifiers="set")

    def addToSelection(self, objects):
      """
      Adds objects to this windows group's current selection.

      :param objects:
        Objects to add to selection
      :type objects: list of :py:class:`anatomist.base.Anatomist.AObject`
      """
      self.anatomistinstance.execute("Select", objects=self.makeList(objects), group=self, modifiers="add")

    def unSelect(self, objects):
      """
      Removes objects from this windows group's selection.

      :param objects:
        Objects to unselect
      :type objects: list of :py:class:`anatomist.base.Anatomist.AObject`
      """
      self.anatomistinstance.execute("Select", unselect_objects=self.makeList(objects), group=self, modifiers="add")

    def toggleSelection(self, objects):
      """
      Inverses selection in this windows group. Selected objects becomes unselected, unselected objects become selected.
      """
      self.anatomistinstance.execute("Select", objects=self.makeList(objects), group=self, modifiers="toggle")

    def setSelectionByNomenclature(self, nomenclature, names):
      """
      Selects objects giving their name in a nomenclature. In anatomist graphical interface, it is done by clicking on items of a nomenclature opened in a browser.

      :param nomenclature:
        tree with names and labels associated to nodes.
      :type nomenclature: :py:class:`anatomist.base.Anatomist.AObject`

      :param names:
        Names of elements to select.
      :type names: list of string
      """
      if names is not None and names != []: # executing the command with names = [] make errors
        snames = ' '.join(names)
        self.anatomistinstance.execute("SelectByNomenclature", nomenclature=nomenclature, names=snames, group=self, modifiers="set")

    def addToSelectionByNomenclature(self, nomenclature, names):
      """
      Adds objects to this windows group's current selection, given their name in a nomenclature.

      :param nomenclature:
        Tree with names and labels associated to nodes.
      :type nomenclature: :py:class:`anatomist.base.Anatomist.AObject`

      :param names:
        Names of elements to add to selection.
      :type names: list of string
      """
      if names is not None and names != []:
        snames = ' '.join(names)
        self.anatomistinstance.execute("SelectByNomenclature", nomenclature=nomenclature, names=snames, group=self, modifiers="add")


    def toggleSelectionByNomenclature(self, nomenclature, names):
      """
      Removes objects from this windows group's selection, given their name in a nomenclature.

      :param nomenclature:
        Tree with names and labels associated to nodes.
      :type nomenclature: :py:class:`anatomist.base.Anatomist.AObject`

      :param names:
        Names of elements to unselect.
      :type names: list of string
      """
      if names is not None and names != []:
        snames = ' '.join(names)
        self.anatomistinstance.execute("SelectByNomenclature", nomenclature=nomenclature, names=snames, group=self, modifiers="toggle")

  ###############################################################################
  class Referential(AItem):
    """
    :param string refUuid:
      A unique id representing this referential
      Two referential are equal if they have the same uuid.
    """

    def __init__(self, anatomistinstance, internalRep=None, uuid=None, *args, **kwargs):
      super(Anatomist.Referential, self).__init__(anatomistinstance, internalRep, *args, **kwargs)
      if uuid is not None:
        self.refUuid=uuid

    def __cmp__(self, other):
      """
      Called on comparison operations between self and other.
      Their uuid is compared.

      :returns:
        -1 if self < other, 0 if self == other, 1 if self > other
      :rtype: int
      """
      if not isinstance(other, Anatomist.Referential):
        return 1
      if self.refUuid == other.refUuid:
        return 0
      elif self.refUuid < other.refUuid:
        return -1
      else:
        return 1

    def __eq__(self, other):
      if not isinstance(other, Anatomist.Referential):
        return False
      return self.refUuid == other.refUuid

    def __lt__(self, other):
      if not isinstance(other, Anatomist.Referential):
        return False
      return self.refUuid < other.refUuid

    def __gt__(self, other):
      if not isinstance(other, Anatomist.Referential):
        return False
      return self.refUuid > other.refUuid

  #############################################################################
  class APalette(AItem):
    """
    :param string name:
      Palette name. Must be unique, it is the palette identifier.
    """
    def __init__(self, name, anatomistinstance, internalRep=None, *args,
                 **kwargs):
      super(Anatomist.APalette, self).__init__(anatomistinstance, internalRep,
                                               *args, **kwargs)
      self.name = name

    def setColors(self, colors, color_mode="RGB"):
      """
      Modifies a palette (colors).

      Parameters
      ----------
      palette: :py:class:`anatomist.base.Anatomist.APalette` object or name
        The palette which colors must be changed

      colors: list of ints
        Color vectors, in line (a list of R, G, B, R, G, B...
        or R, G, B, A, ..), as int 8 bit values

      color_mode: string
        ``'RGB'`` or ``'RGBA'``
      """
      self.anatomistinstance.execute("ChangePalette", name=self.name,
                                     colors=colors, color_mode=color_mode)

  #############################################################################
  class Transformation(AItem):
    """
    This objects contains informations to convert coordinates from one referential to another.
    rotation_matrix
    translation
    """
    def __init__(self, anatomistinstance, internalRep=None, *args, **kwargs):
      super(Anatomist.Transformation, self).__init__(anatomistinstance, internalRep, *args, **kwargs)

    def save(self, filename):
      """
      Saves transformation in file.

      :param string filename:
        File in which the transformation will be written.
      """
      self.anatomistinstance.execute("SaveTransformation", filename=filename, transformation=self)

  ###############################################################################
  class Material(object):
    """
    :param ambient:
    :type ambient: RGB[A] vector: float values between 0 and 1.

    :param list diffuse:
      This parameter corresponds to the "standard" notion of color
    :type diffuse: RGB[A] vector: float values between 0 and 1.

    :param emission:
    :type emission: RGB[A] vector: float values between 0 and 1.

    :param specular:
    :type specular: RGB[A] vector: float values between 0 and 1.

    :param float shininess:
      0-124

    :param boolaen lighting:
      enables (1) or disables (0) objects lighting/shading. Setting this value to -1 goes back to the default mode (globally set at the view/scene level).

    :param int smooth_shading:
      (tristate: 0/1/-1) smooth or flat polygons mode

    :param int polygon_filtering:
      (tristate: 0/1/-1) filtering (antialiasing) of lines/polygons

    :param int depth_buffer:
      (tristate: 0/1/-1) enables/disables writing in the Z-buffer. You can disable it if you want to click "through" an object (but it may have strange effects on the rendering)

    :param int face_culling:
      (tristate: 0/1/-1) don't draw polygons seen from the back side. The best is to enable it for transparent objects, and to disable it for "open" (on which both sides may be seen) and opaque meshes. For objects both open and transparent, there is no perfoect setting...

    :param string polygon_mode:
      polygons rendering mode: "normal", "wireframe", "outline" (normal + wireframe), "hiddenface_wireframe" (wireframe with hidden faces), "default" (use the global view settings), "ext_outlined" (thickened external boundaries + normal rendering).

    :param unlit_color:
      color used for lines when lighting is off. For now it only affects polygons boundaries in "outlined" or "ext_outlined" polygon modes.
    :type unlit_color: RGB[A] vector: float values between 0 and 1.

    :param float line_width:
      Lines thickness (meshes, segments, wireframe rendering modes). A null or negative value fallsback to default (1 in principle).

    :param int ghost:
      obsolete: use selectable_mode instead.
      In ghost mode, objects are not drawn in the depth buffer

    :param string selectable_mode:
      New in Anatomist 4.5.
      Replaces the ghost property.
      always_selectable: object is selecatble whatever its opacity.
      ghost: object is not selectable.
      selectable_when_opaque: object is selectable when totally opaque (this is the default in Anatomist).
      selectable_when_not_totally_transparent: object is selectable unless opacity is zero.

    :param string front_face:
      Specifies if the mesh(es) polygons external face is the clockwise or counterclockwise side. Normally in Aims/Anatomist indirect referentials, polygons are in clockwise orientation. Values are "clockwise", "counterclockwise", or "neutral" (the default).
    """

    def __init__(self, ambient=None, diffuse=None, emission=None, shininess=None, specular=None, lighting=None, smooth_shading=None, polygon_filtering=None, depth_buffer=None, face_culling=None, polygon_mode=None, unlit_color=None, line_width=None, ghost=None, front_face=None, selectable_mode=None):
      self.ambient = ambient
      self.diffuse = diffuse
      self.emission = emission
      self.shininess = shininess
      self.specular = specular
      # render properties
      self.lighting = lighting
      self.smooth_shading = smooth_shading
      self.polygon_filtering = polygon_filtering
      self.depth_buffer = depth_buffer
      self.face_culling = face_culling
      self.polygon_mode = polygon_mode
      self.unlit_color = unlit_color
      self.line_width = line_width
      self.selectable_mode = selectable_mode
      if ghost and self.selectable_mode is None:
        self.selectable_mode = 'ghost'
      self.front_face = front_face

    def __repr__(self):
      return "{ambient :"+ str(self.ambient)+ ", diffuse :"+ str(self.diffuse)+ ", emission :"+ str(self.emission)+ ", shininess :"+ str(self.shininess)+ ", specular :"+ str(self.specular)+ ", lighting :"+str(self.lighting)+", smooth_shading:"+str(self.smooth_shading)+", polygon_filtering :"+str(self.polygon_filtering)+", depth_buffer :"+str(self.depth_buffer)+", face_culling :"+str(self.face_culling)+", polygon_mode :"+str(self.polygon_mode)+", unlit_color :"+str(self.unlit_color)+", line_width :"+str(self.line_width)+", selectable_mode :"+str(self.selectable_mode)+", front_face:"+str(self.front_face)+"}"

