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

The function C{getThreadSafeClass} enables to create a thread safe class based on a given Anatomist implementation class. It replaces all methods by a call in main thread of the same method. 
"""

import sys, types
from soma.qt_gui.qtThread import QtThreadCall, MainThreadLife
from soma.singleton import Singleton
import six


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
  threadSafeClass = type(classObj.__name__, bases, {})
  # replace all methods (not builtin) by a thread safe call to the same method
  # and replace all inner class by a thread safe class

  for attName, att in six.iteritems(classObj.__dict__):
      if attName[0:2] != "__" or attName == "__singleton_init__":
        # builtin methods begin with __
        # but __singleton_init__ must be called from the main thread
        if type(att) is types.FunctionType:
          # attribute is a method and not a class or static method
          # replace this method by a thread safe call to this method
          # Note:
          # using getattr(classObj, attName) the attribute object types are
          # different in python2 and python3, and in python3 we cannot
          # distinguish between regular and static methods (both are functions,
          # whereas class methods are methods). classObj.__dict__[attName]
          # does not return the same thing however, and allows to determine
          # the method type, in a python2/3 transparent way: regular methods
          # are functions, static methods are staticmethod instances,
          # class methods are classmethod instances.
          if att.func_code.co_filename != __file__:
              # avoid doing this several times
              newAtt = threadSafeCall(mainThread, att)
              setattr(threadSafeClass, attName, newAtt)
        elif type(att) == type: # innner class derived from object
          # replace this class with a thread safe class
          if not issubclass(att, MainThreadLife):
              newAtt = getThreadSafeClass(att, mainThread)
              setattr(threadSafeClass, attName, newAtt)

  if is_aitem:
      #classObj.AItem.__bases__ = classObj.AItem.__bases__ + (MainThreadLife, )
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
