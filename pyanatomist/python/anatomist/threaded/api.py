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
This module is an implementation of general interface :py:mod:`anatomist.base`.
It is based on direct implementation (bindings of C++ Anatomist api) with adding thread-safe layer. 

This implementation can be used in multi-threaded application. To load it, you can do :

  >>> import anatomist
  >>> anatomist.setDefaultImplementation(anatomist.THREADED)
  >>> import anatomist.api as anatomist

or without changing default implementation : 

  >>> import anatomist.threaded.api as anatomist

This module redefines the Anatomist class from the direct implementation Anatomist class to make all methods execute in the main thread (qt thread). 
It uses methods of :py:mod:`anatomist.threadedimpl`.

Note that this thread-safe implementation is not actually multi-threaded: all calls to the Anatomist API are stacked for execution in the same thread, so it is actually a single-thread execution, but calls can be performed from various threads in a multi-threaded program, avoiding race conditions (provided the calling thread has not locked the main thread in any way).

All classes in the anatomist module are made thread-safe.

Objects returned by calls to the thread-safe API
------------------------------------------------

Generally, objects created (or just returned) by calls to the Anatomist thread-safe API belong to the main thread. This means that they must be used, and importantly, destroyed, within the main thread.

Using objects
+++++++++++++

When returned objects are classes from the Anatomist API, they are subclasses of the thread-safe API, and are already made thread-safe when used.

When objects do not belong to the Anatomist API, like Qt widgets, then caution must be taken to use them from the main GUI thread only. You can use :soma:`soma.qt_gui.qtThread.QtThreadCall <api.html#soma.qt_gui.qtThread.QtThreadCall>` to do so.

Destroying objects
++++++++++++++++++

Destruction of objects in python is somewhat tricky: when a variable is deleted, a reference to it is decremented, and when the last reference is dropped, the object is actually destroyed, indeed from the thread removing this last reference. If several threads hold a reference to a given object, who will actually delete it ? If a sensible (non-thread-safe) object is deleted within the wrong thread, program crashes may occur.

To manage this problem we use wrapper objects which will delegate the destruction of objects they contain to the main thread: :soma:`soma.qt_gui.qtThread.MainThreadLife <api.html#soma.qt_gui.qtThread.MainThreadLife>`.

:py:class:`AItem <anatomist.base.Anatomist.AItem>` subclasses in the threaded implementation (including :py:class:`AObject <anatomist.base.Anatomist.AObject>`, :py:class:`AWindow <anatomist.base.Anatomist.AWindow>` etc) are already subclasses of :soma:`MainThreadLife <api.html#soma.qt_gui.qtThread.MainThreadLife>`.

"""
from anatomist import cpp
import anatomist.threadedimpl
import anatomist.direct.api
import sys
from soma.qt_gui.qtThread import QtThreadCall

mainThread=QtThreadCall()
Anatomist=anatomist.threadedimpl.getThreadSafeClass(\
  classObj=anatomist.direct.api.Anatomist, mainThread=mainThread)

del anatomist, mainThread, QtThreadCall

