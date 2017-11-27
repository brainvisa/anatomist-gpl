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
This module makes anatomist module given implementation thread safe.

The ThreadSafeMetaclass is used to build thread-safe versions of classes
(Anatomist, AItem and other inherited classes).

The function :func:`getThreadSafeClass` enables to create a thread safe class based on a given Anatomist implementation class. It replaces all methods by a call in main thread of the same method.
The ThreadSafeMetaclass metaclass ensures that inherited classes will also be thread safe.
"""

import sys, types
from soma.qt_gui.qtThread import QtThreadCall, MainThreadLife
from soma.singleton import Singleton
import six
from soma.qt_gui.qt_backend import QtCore
import inspect


def threadedModule(anatomistModule, mainThread=None): 
  """
  Adds to current module a thread safe version of given anatomist module,
  replacing Anatomist class by thread safe Anatomist class.
  
  Parameters
  ----------
  anatomistModule: module
      a module containing an implementation of Anatomist class
  mainThread: MainThreadActions (optional)
      an object that enables to send tasks to the mainThread. If it is not
      given in parameters, an instance will be created in this function. So it
      must be called by the mainThread.
  """
  moduleName = anatomistModule.__name__+"_threaded"
  anatomistThreadedModule = sys.modules.get(moduleName)
  if anatomistThreadedModule is None:
    if mainThread is None:
      mainThread = QtThreadCall()
    ThreadedAnatomist = getThreadSafeClass(
        classObj=anatomistModule.Anatomist, mainThread=mainThread)
    anatomistThreadedModule = types.ModuleType(moduleName)
    anatomistThreadedModule.__dict__['Anatomist'] = ThreadedAnatomist
    sys.modules[moduleName] = anatomistThreadedModule
  return anatomistThreadedModule


class ThreadSafeMetaclass(type(QtCore.QObject)):
    '''The ThreadSafeMetaclass replaces all methods of the classes it builds
    with thread-safe wrappers. All function calls are actually deported to the
    main thread. Subclasses are also handled.
    Anatomist.AItem is also made to inherit soma.qt_gui.qtThread.MainThreadLife
    and makes a hook to force deletion to happen in the main thread when
    reference count reaches zero from any thread.

    This meta-class inherits from the meta-class used by PyQt classes.
    '''

    def __init__(cls, name, bases, attdict):
        super(ThreadSafeMetaclass, cls).__init__(name, bases, attdict)
        mainThread = QtThreadCall()
        mro = cls.__mro__
        new_dict = {}
        # get class attributes using dir(), not __dict__ which only contains the
        # terminal class specific attributes, not its parents ones.
        old_dict = dict([(attName, getattr(cls, attName))
                         for attName in dir(cls)])
        new_dict.update(get_thead_safe_dict(old_dict, True))
        for attName, att in six.iteritems(new_dict):
            setattr(cls, attName, att)


def get_thead_safe_dict(dictatt, filtered=False):
    ''' Builds thread-safe wrappers around dict elements which are methods or
    functions, replace classes by thread-safe subclasses
    '''
    new_dict = {}
    mainThread = QtThreadCall()
    for attName, att in six.iteritems(dictatt):
        if attName[0:2] != "__" or attName == "__singleton_init__":
          # builtin methods begin with __
          # but __singleton_init__ must be called from the main thread
          orig_att = att
          att = getattr(att, 'im_func', att) # in case it's a method
          if inspect.isfunction(att) or inspect.isbuiltin(att):
              # replace this method by a thread safe call to this method
              # Note:
              # using getattr(classObj, attName) the attribute object types are
              # different in python2 and python3, and in python3 we cannot
              # distinguish between regular and static methods (both are
              # functions,
              # whereas class methods are methods). classObj.__dict__[attName]
              # does not return the same thing however, and allows to determine
              # the method type, in a python2/3 transparent way: regular methods
              # are functions, static methods are staticmethod instances,
              # class methods are classmethod instances.
              if not hasattr(att, '__code__') \
                      or att.__code__.co_filename != __file__:
                  # avoid doing this several times
                  newAtt = threadSafeCall(mainThread, att)
                  if inspect.isfunction(orig_att) \
                          and not inspect.ismethod(orig_att):
                      newAtt = staticmethod(newAtt)
                  elif inspect.ismethod(orig_att) \
                          and (sys.version_info[0] >= 3 or
                              isinstance(orig_att.__self__, type)):
                      newAtt = classmethod(newAtt)
                  new_dict[attName] = newAtt
          elif type(att) == type: # innner class derived from object
              # replace this class with a thread safe class
              if not issubclass(att, MainThreadLife):
                  newAtt = getThreadSafeClass(att, mainThread)
                  new_dict[attName] = newAtt
          elif not filtered:
              new_dict[attName] = att
    return new_dict


def getThreadSafeClass(classObj, mainThread):
  """
  Generates a thread safe class which inherits from the class given in
  parameters.
  Methods are executed in the main thread to be thread safe. 

  Parameters
  ----------
  classObj: Class
      the class which needs to be thread safe
  mainThread: QtThreadCall
      an object that enables to send tasks to the main thread.

  Returns
  -------
  new_class: Class
      The generated thread safe class
  """
  # create a new class that inherits from classObj
  from anatomist import base
  is_aitem = False
  if classObj.__name__ == 'AItem' \
          or issubclass(classObj, base.Anatomist.AItem):
      bases = (classObj, MainThreadLife)
      is_aitem = True
  else:
      bases = (classObj,)
  threadSafeClass = ThreadSafeMetaclass(classObj.__name__, bases, {})

  if is_aitem:
      def aitem_init(self, *args, **kwargs):
          super(threadSafeClass, self).__init__(*args, **kwargs)
          self._obj_life = self.internalRep
      threadSafeClass.__init__ = aitem_init
      def aitem_del(self):
          super(threadSafeClass, self).__del__()
          MainThreadLife.__del__(self)
      threadSafeClass.__del__ = aitem_del

  return threadSafeClass


def threadSafeCall(mainThread, func):
  """Utility function wrapper for main thread calls

  Returns
  -------
  func: function
      a function that sends the given function's call to the main thread
  """
  import threading
  return lambda *args, **kwargs: mainThread.call(func, *args, **kwargs)
