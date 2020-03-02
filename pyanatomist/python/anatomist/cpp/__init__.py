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
Low level module containing Sip bindings of Anatomist C++ API.

Introduction
============

This module is mostly bindings to the C++ library of Anatomist. A few classes
have been slightly modified or rewritten, either to hide garbage or to
appear more pythonic.

For typical use, this module will not be called directly but throught general API. But it can be needed for using advanced features.

The main entry point is the :class:`Anatomist` class which must be instantiated before any operation can be performed.

>>> import anatomist.cpp as anatomist
>>> a = anatomist.Anatomist()

Note that instantiating Anatomist also instantiates the
`Qt <http://www.qt.io>`_ QApplication, but does not run the Qt event loop,
so python interactive shells are still accessible after that operation, but
the GUI is frozen until the event loop is executed, using the following PyQt
code:

>>> # from PyQt4 import Qt
>>> # or, to switch to the correct Qt implementation and bindings (Qt4/Qt5)
>>> from soma.qt_gui.qt_backend import Qt
>>> Qt.qApp.exec_loop()

but then the loop does not return until the GUI application is over, so you
should start it at the end of your code.

Another comfortable alternative to the GUI loop problem in interactive
python shells is to use `IPython <http://ipython.scipy.org/>`_ with the
option ``--gui=qt``: IPython is an interactive python shell with many
improvements, and which can run in a different thread than the GUI, so that
the GUI can run without hanging the shell.

Contrarily to the Qt application, Anatomist can be instantiated multiple
times (it is not a singleton, but contains a singleton).

In addition to providing bindings to the Anatomist C++ API, the anatomist
module also loads some python modules in anatomist: every python module
found in the following locations are loaded::

    os.path.join(str(anatomist.Anatomist().anatomistSharedPath()), 'python_plugins')
    os.path.join(str(anatomist.Anatomist().anatomistHomePath()), 'python_plugins')

Main concepts
=============
There are many pieces in Anatomist library, but a few are really needed to
begin with.

* the Anatomist application, the L{Anatomist} class instance, is responsible
  for many global variables, the application state, and the startup
  procedure (including plugins loading). The application is used internally
  in many functions.
* objects: :class:`AObject` class and subclasses
* windows: :class:`AWindow` class and subclasses
* the commands processor: a singleton :class:`Processor` instance obtained via
  the application: :meth:`Anatomist.theProcessor`. The processor is a commands
  interpreter for the rudimentary language of Anatomist. It is also
  responsible of saving every command executed in the history file
  ``$HOME/.anatomist/history.ana`` so most of the session can be replayed.
  Many operations are done via commands and the processor: creating windows,
  loading objects, displaying them, etc. so this element is probably the
  most important part of Anatomist.
* conversions between AIMS object and Anatomist objects:
  :class:`AObjectConverter` is here to perform this task.
'''

from __future__ import print_function

from __future__ import absolute_import
import os
import sys
import string
import glob
import operator
import types
import numpy
import six
import collections
import logging


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


path = os.path.dirname(__file__)
if path not in sys.path:
    sys.path.insert(0, path)
del path

from soma import aims
from soma.importer import ExtendedImporter

# force using sip API v2 for PyQt4
sip_classes = ['QString', 'QVariant', 'QDate', 'QDateTime',
               'QTextStream', 'QTime', 'QUrl']
_sip_api_set = False
import sip
for sip_class in sip_classes:
    try:
        sip.setapi(sip_class, 2)
    except ValueError as e:
        if not _sip_api_set:
            logging.warning(e.message)
    _sip_api_set = True

# cleanup namespaces in Sip-generated code
ExtendedImporter().importInModule('', globals(), locals(), 'anatomistsip')
ExtendedImporter().importInModule('', globals(), locals(), 'anatomistsip',
                                  ['anatomistsip.anatomist'])
del ExtendedImporter

from soma.qt_gui import qt_backend
qt_backend.set_qt_backend(compatible_qt5=True, pyqt_api=2)

from anatomistsip import *

aims.__fixsipclasses__(list(locals().items()))

loaded_modules = []
global _anatomist_modsloaded
_anatomist_modsloaded = 0

# update AObjectConverter class to be more flexible


def aimsFromAnatomist(ao, options={'scale': 1}):
    tn = ao.objectTypeName(ao.type())
    # take into account wrapping case
    if hasattr(ao, 'internalRep'):
        ao = ao.internalRep
    if tn == 'VOLUME':
        try:
            hdr = ao.attributed()
            if hdr:
                dt = hdr['data_type']
                oc = getattr(AObjectConverter, 'aimsData_' + dt)
                aim = oc(ao, options)
                if not aim.isNull():
                    return aim._get()
        except:
            pass
        # all this just in case data_type is not set in header
        aim = AObjectConverter.aimsData_U8(ao, options)
        if not aim.isNull():
            return aim._get()
        aim = AObjectConverter.aimsData_S16(ao, options)
        if not aim.isNull():
            return aim._get()
        aim = AObjectConverter.aimsData_U16(ao, options)
        if not aim.isNull():
            return aim._get()
        aim = AObjectConverter.aimsData_S32(ao, options)
        if not aim.isNull():
            return aim._get()
        aim = AObjectConverter.aimsData_U32(ao, options)
        if not aim.isNull():
            return aim._get()
        aim = AObjectConverter.aimsData_FLOAT(ao, options)
        if not aim.isNull():
            return aim._get()
        aim = AObjectConverter.aimsData_DOUBLE(ao, options)
        if not aim.isNull():
            return aim._get()
        aim = AObjectConverter.aimsData_RGB(ao, options)
        if not aim.isNull():
            return aim._get()
        aim = AObjectConverter.aimsData_RGBA(ao, options)
        if not aim.isNull():
            return aim._get()
    elif tn == 'SURFACE':
        aim = AObjectConverter.aimsSurface3(ao, options)
        if not aim.isNull():
            return aim._get()
        aim = AObjectConverter.aimsSurface4(ao, options)
        if not aim.isNull():
            return aim._get()
        aim = AObjectConverter.aimsSurface2(ao, options)
        if not aim.isNull():
            return aim._get()
    elif tn == 'BUCKET':
        aim = AObjectConverter.aimsBucketMap_VOID(ao, options)
        if not aim.isNull():
            return aim._get()
    elif tn == 'TEXTURE':
        at = ao.attributed()
        if not at:
            dt = 'FLOAT'
        else:
            try:
                dt = at['data_type']
            except:
                dt = 'FLOAT'
        try:
            conv = getattr(AObjectConverter, 'aimsTexture_' + dt)
            aim = conv(ao, options)._get()
            return aim
        except:
            aim = AObjectConverter.aimsTexture_FLOAT(ao, options)
            if not aim.isNull():
                return aim._get()
            aim = AObjectConverter.aimsTexture_POINT2DF(ao, options)
            if not aim.isNull():
                return aim._get()
            aim = AObjectConverter.aimsTexture_S16(ao, options)
            if not aim.isNull():
                return aim._get()
            aim = AObjectConverter.aimsTexture_S32(ao, options)
            if not aim.isNull():
                return aim._get()
            aim = AObjectConverter.aimsTexture_U32(ao, options)
        if aim and not aim.isNull():
            return aim._get()
        return None
    elif tn == 'GRAPH':
        aim = AObjectConverter.aimsGraph(ao, options)
        if not aim.isNull():
            return aim._get()
    elif tn == 'NOMENCLATURE':
        aim = AObjectConverter.aimsTree(ao, options)
        if not aim.isNull():
            return aim._get()
    elif tn == 'SparseMatrix':
        aim = AObjectConverter.aimsSparseMatrix(ao, options)
        if not aim.isNull():
            return aim._get()
    return None

AObjectConverter.aims = staticmethod(aimsFromAnatomist)
del aimsFromAnatomist


def anatomistFromAims(obj):
    ot = type(obj).__name__
    if isinstance(obj, AObject):
        return obj
    t = None
    if isinstance(obj, numpy.ndarray):
        t = None
        if obj.dtype is numpy.dtype(numpy.int8):
            t = aims.Volume_S8
        elif obj.dtype is numpy.dtype(numpy.uint8):
            t = aims.Volume_U8
        elif obj.dtype is numpy.dtype(numpy.int16):
            t = aims.Volume_S16
        elif obj.dtype is numpy.dtype(numpy.uint16):
            t = aims.Volume_U16
        elif obj.dtype is numpy.dtype( numpy.int_ ) \
                or obj.dtype is numpy.dtype(numpy.int32):
            t = aims.Volume_S32
        elif obj.dtype is numpy.dtype(numpy.uint32):
            t = aims.Volume_U32
        elif obj.dtype is numpy.dtype(numpy.float32):
            t = aims.Volume_FLOAT
        elif obj.dtype is numpy.dtype( numpy.float64 ) \
                or obj.dtype is numpy.dtype(numpy.float_):
            t = aims.Volume_DOUBLE
    if t:
        return AObjectConverter.anatomist(t(obj))
    return AObjectConverter._anatomist(obj)
AObjectConverter._anatomist = AObjectConverter.anatomist
AObjectConverter.anatomist = staticmethod(anatomistFromAims)
del anatomistFromAims


# Anatomist class: entry point to anatomist

class Anatomist(AnatomistSip):

    '''
    Anatomist class: entry point to anatomist
    '''

    def __init__(self, *args):
        import anatomistsip
        import os
        import sys
        import glob
        import traceback
        global _anatomist_modsloaded
        modsloaded = _anatomist_modsloaded
        _anatomist_modsloaded = 1
        AnatomistSip.__init__(self, ('anatomist', ) + args)
        if modsloaded:
            return

        pythonmodules = os.path.join(str(self.anatomistSharedPath()),
                                     'python_plugins')
        homemodules = os.path.join(str(self.anatomistHomePath()),
                                   'python_plugins')

        print('global modules:', pythonmodules)
        print('home   modules:', homemodules)

        if sys.path[0] != homemodules:
            sys.path.insert(0, homemodules)
        if sys.path[1] != pythonmodules:
            sys.path.insert(1, pythonmodules)

        mods = glob.glob( os.path.join( pythonmodules, '*' ) ) \
            + glob.glob(os.path.join(homemodules, '*'))
        # print('modules:', mods)

        global loaded_modules

        for x in mods:
            if os.path.basename(x).startswith('_'):
                # don't load files starting with '_' (__init__, __pycache__...)
                continue
            if x[-4:] == '.pyo':
                x = x[:-4]
            elif x[-4:] == '.pyc':
                x = x[:-4]
            elif x[-3:] == '.py':
                x = x[:-3]
            elif not os.path.isdir(x):
                continue
            # print('module:', x)
            x = os.path.basename(x)
            if x in loaded_modules:
                continue
            loaded_modules.append(x)
            print('loading module', x)
            try:
                exec('import ' + x)
            except:
                print()
                print('loading of module', x, 'failed:')
                exceptionInfo = sys.exc_info()
                e, v, t = exceptionInfo
                tb = traceback.extract_tb(t)
                try:
                    name = e.__name__
                except:
                    name = str(e)
                print(name, ':', v)
                print('traceback:')
                for file, line, function, text in tb:
                    if text is None:
                        text = '?'
                    print(file, '(', line, ') in', function, ':')
                    print(text)
                print()
                # must explicitely delete reference to frame objects
                # (traceback) else it creates a reference cycle and the object
                # cannot be deleted
                del e, v, t, tb, exceptionInfo

        print('all python modules loaded')

# Processor.execute


def newexecute(self, *args, **kwargs):
    '''
    Commands execution. It can be used in several different forms:

    * execute(Command)
    * execute(commandname, params=None, context=None)
    * execute(commandname, context=None, **kwargs)

    Parameters
    ----------
    Command: :class:`Command` subclass
        command to be executed
    commandname: str
        name of the command to executed
    params: dict or str
        optional parameters (default: None)
    context: :class:`CommandContext`
        command execution context (default: None)
    kwargs:
        keyword arguments which are passed to Anatomist directly in the command

    Returns
    -------
    command: the executed command (or None)
    '''
    def replace_dict(dic, cc):
        for k, v in dic.items():
            if isinstance( v, AObject ) or isinstance( v, AWindow ) \
                    or isinstance(v, Referential) or isinstance(v, Transformation):
                try:
                    i = cc.id(v)
                except:
                    i = cc.makeID(v)
                dic[k] = i
            elif hasattr(v, 'items'):  # operator.isMappingType( v ):
                replace_dict(v, cc)
            elif not isinstance(v, six.string_types) and isSequenceType(v):
                replace_list(v, cc)

    def replace_list(l, cc):
        k = 0
        for v in l:
            if isinstance( v, AObject ) or isinstance( v, AWindow )\
                    or isinstance(v, Referential) or isinstance(v, Transformation):
                try:
                    i = cc.id(v)
                except:
                    i = cc.makeID(v)
                l[k] = i
            elif hasattr(v, 'items'):  # operator.isMappingType( v ):
                replace_dict(v, cc)
            elif not isinstance(v, six.string_types) and isSequenceType(v):
                replace_list(v, cc)
            k += 1

    if len(args) < 1 or len(args) > 3:
        raise RunTimeError('wrong arguments number')
    if type(args[0]) is not str:
        if len(args) != 1:
            raise RunTimeError('wrong arguments number')
        return self._execute(args[0])

    dic = {}
    cc = None
    if len(kwargs) != 0:
        if len(args) > 2:
            raise RunTimeError('wrong arguments number')
        kw = 0
        if len(args) == 2:
            cc = args[1]
        else:
            cc = kwargs.get('context')
            if cc is not None:
                kw = 1
        dic = kwargs.copy()
        if kw:
            del dic['context']
    elif len(args) >= 2:
        dic = args[1]
        if len(args) == 3:
            cc = args[2]
        elif len(args) > 3:
            raise RunTimeError('wrong arguments number')
    if not cc:
        cc = CommandContext.defaultContext()
    replace_dict(dic, cc)
    return self._execute(args[0], str(dic), cc)

Processor.execute = newexecute
del newexecute

# automatically wrap creator functions in controls system


class PyKeyActionLink(Control.KeyActionLink):

    def __init__(self, method):
        Control.KeyActionLink.__init__(self)
        self._method = method

    def execute(self):
        self._method()

    def clone(self):
        return PyKeyActionLink(self._method)


class PyMouseActionLink(Control.MouseActionLink):

    def __init__(self, method):
        Control.MouseActionLink.__init__(self)
        self._method = method

    def execute(self, x, y, globalX, globalY):
        self._method(x, y, globalX, globalY)

    def clone(self):
        return PyMouseActionLink(self._method)

    def action(self):
        return self._method.__self__


class PyWheelActionLink(Control.WheelActionLink):

    def __init__(self, method):
        Control.WheelActionLink.__init__(self)
        self._method = method

    def execute(self, delta, x, y, globalX, globalY):
        self._method(delta, x, y, globalX, globalY)

    def clone(self):
        return PyWheelActionLink(self._method)


class PySelectionChangedActionLink(Control.SelectionChangedActionLink):

    def __init__(self, method):
        Control.SelectionChangedActionLink.__init__(self)
        self._method = method

    def execute(self):
        self._method()

    def clone(self):
        return PySelectionChangedActionLink(self._method)


class PyActionCreator(ActionDictionary.ActionCreatorBase):

    def __init__(self, function):
        ActionDictionary.ActionCreatorBase.__init__(self)
        self._function = function

    def __call__(self):
        return self._function()


class PyControlCreator(ControlDictionary.ControlCreatorBase):

    def __init__(self, function):
        ControlDictionary.ControlCreatorBase.__init__(self)
        self._function = function

    def __call__(self):
        return self._function()

ControlDictionary.addControl = \
    lambda self, name, creator, prio, allowreplace=False: \
    self._addControl(name, PyControlCreator(creator), prio, allowreplace)
ActionDictionary.addAction = \
    lambda self, name, creator: \
    self._addAction(name, PyActionCreator(creator))

# control subscribe functions


def keyPressSubscribeFunction(self, key, state, func, name=''):
    if name == '':
        if hasattr(func, '__name__'):
            name = func.__name__
        elif hasattr(func, '__func__') and hasattr(func.__func__, '__name__'):
            name = func.__func__.__name__
    self._keyPressEventSubscribe(key, state, PyKeyActionLink(func), name)


def keyReleaseSubscribeFunction(self, key, state, func, name=''):
    if name == '':
        if hasattr(func, '__name__'):
            name = func.__name__
        elif hasattr(func, '__func__') and hasattr(func.__func__, '__name__'):
            name = func.__func__.__name__
    self._keyReleaseEventSubscribe(key, state, PyKeyActionLink(func), name)


def mousePressSubscribeFunction(self, but, state, func, name=''):
    if name == '':
        if hasattr(func, '__name__'):
            name = func.__name__
        elif hasattr(func, '__func__') and hasattr(func.__func__, '__name__'):
            name = func.__func__.__name__
    self._mousePressButtonEventSubscribe(
        but, state, PyMouseActionLink(func), name)


def mouseReleaseSubscribeFunction(self, but, state, func, name=''):
    if name == '':
        if hasattr(func, '__name__'):
            name = func.__name__
        elif hasattr(func, '__func__') and hasattr(func.__func__, '__name__'):
            name = func.__func__.__name__
    self._mouseReleaseButtonEventSubscribe(
        but, state, PyMouseActionLink(func), name)


def mouseDoubleClickSubscribeFunction(self, but, state, func, name=''):
    if name == '':
        if hasattr(func, '__name__'):
            name = func.__name__
        elif hasattr(func, '__func__') and hasattr(func.__func__, '__name__'):
            name = func.__func__.__name__
    self._mouseDoubleClickEventSubscribe(
        but, state, PyMouseActionLink(func), name)


def mouseMoveSubscribeFunction(self, but, state, func, name=''):
    if name == '':
        if hasattr(func, '__name__'):
            name = func.__name__
        elif hasattr(func, '__func__') and hasattr(func.__func__, '__name__'):
            name = func.__func__.__name__
    self._mouseMoveEventSubscribe(but, state, PyMouseActionLink(func), name)

Control.keyPressEventSubscribe = keyPressSubscribeFunction
Control.keyReleaseEventSubscribe = keyReleaseSubscribeFunction
Control.mousePressButtonEventSubscribe = mousePressSubscribeFunction
Control.mouseReleaseButtonEventSubscribe = mouseReleaseSubscribeFunction
Control.mouseMoveEventSubscribe = mouseMoveSubscribeFunction
Control.mouseDoubleClickEventSubscribe = mouseDoubleClickSubscribeFunction
del keyPressSubscribeFunction, keyReleaseSubscribeFunction, \
    mousePressSubscribeFunction, mouseReleaseSubscribeFunction, \
  mouseDoubleClickSubscribeFunction, mouseMoveSubscribeFunction

Control.mouseLongEventSubscribe = lambda self, but, state, startfunc, \
    longfunc, endfunc, exclusive: \
                                  self._mouseLongEventSubscribe(
                                      but, state, PyMouseActionLink(startfunc),
                                      PyMouseActionLink(longfunc), PyMouseActionLink(endfunc), exclusive)
Control.wheelEventSubscribe = lambda self, func: \
    self._wheelEventSubscribe(
        PyWheelActionLink(func))
Control.selectionChangedEventSubscribe = lambda self, func: \
    self._selectionChangedEventSubscribe(
        PySelectionChangedActionLink(func))

aims.convertersObjectToPython.update({
                                     'AObject': AObject.fromObject,
                                     'PN9anatomist7AObjectE': AObject.fromObject,
                                     'N5carto10shared_ptrIN9anatomist7AObjectEEE': AObject.fromObject,
                                     'PN9anatomist7AWindowE': AWindow.fromObject,
                                     })


# Import external python modules
from . import mobject
# delete things from other modules

# apply changes to config properties to Anatomist internal state


def __GlobalConfiguration_setitem__(self, param, value):
    print('config.setitem:', param, ':', value)
    super(GlobalConfiguration, self).__setitem__(param, value)
    self.apply()
anatomist.GlobalConfiguration.__setitem__ = __GlobalConfiguration_setitem__
del __GlobalConfiguration_setitem__

del os, string, glob
del anatomist  # , aims

# -------------
# docs

Command.__doc__ = '''
Commands are the execution units of the :class:`Processor`.

Commands are used as subclasses of :class:`Command`. They can be built either
on the fly by the programmer, or using the commands factory via the
:meth:`Processor.execute` function.

Never call :meth:`Command.execute` or :meth:`Command.doit` directly: only the
processor will do so. Once built, a command must always be executed by the
processor:

>>> a = anatomist.Anatomist()
>>> c = anatomist.CreateWindowCommand('Axial')
>>> a.theProcessor().execute(c)

But in any case there is a more handy shortcut in the higher-level API:
:meth:`anatomist.base.Anatomist.execute`

Comamnds can be subclassed in Python. To be valid, a new command must define
at least the :meth:`name` and :meth:`doit` methods. :meth:`doit` will actually
do the execution and your program may make it do anything. Later, :meth:`read`
and :meth:`write` should also be redefined to allow proper IO for this command
(when the commands IO and factory are exported from C++ to python).

:meth:`Command.doit` receives no parameters (apart from ``self``). All
execution arguments must be set in the command itself upon construction (either
by the constructor or by setting some instance variables).

One important parameter which a command would often use is the
:class:`CommandContext`, which specifies some IO streams for output printing
and communication with external programs, and an identifiers set used to name
and identify objects (in a general meaning: including windows etc.) through
this IO streams.
'''

AObjectConverter.__doc__ = '''
Aims / Anatomist objects converter

Only two static methods are useful in this class:

* :meth:`AObjectConverter.anatomist` converts an AIMS (or possibly other)
  object into an Anatomist object (:class:`AObject` subclass), if possible
* :meth:`AObjectConverter.aims` converts an Anatomist object to an AIMS object,
  if possible

Conversions are generally done by wrapping or embedding, or by extracting a
reference to an internal object, so objects data are genrally shared between
the AIMS and the Anatomist objects layers. This allows internal modification
of Anatomist objects data.

After a modification through the Aims (lower level) layer API, modification
notification must be issued to the Anatomist layer to update the display of
the object in Anatomist. This is generally done via the
:meth:`AObject.setChanged` and :meth:`AObject.notifyObservers` methods.
'''

private = ['private', 'anatomistsip', 'AnatomistSip', 'numpy', 'operator',
           'mobject']
__all__ = []
for x in dir():
    if not x.startswith('_') and x not in private:
        __all__.append(x)
del x, private
