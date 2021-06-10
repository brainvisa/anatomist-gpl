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
Introduction
============
This API enables to drive *Anatomist* application throught python scripts : running Anatomist, loading volumes, meshes, graphs, viewing them in windows, merging objects, changing colour palette...

* organization: NeuroSpin and IFR 4
* license: `CeCILL-v2 <http://www.cecill.info/licences/Licence_CeCILL_V2-en.html>`_ (GPL-compatible)

From version 4.7.0 and later, PyAnatomist work with both Python 2 (2.7 and later) and Python 3 (3.4 and later) (provided C++/python bindings have been compiled appropriately).

The main entry point is one of the :py:class:`anatomist.base.Anatomist`-inhertied classes which must be instantiated before any operation can be performed.
It represents Anatomist application. This class contains a number of nested classes: :py:class:`anatomist.base.Anatomist.AObject`, :py:class:`anatomist.base.Anatomist.AWindow`... that represents handling elements of Anatomist application.

The entry point of this API is the module api, you can import it as below :

>>> import anatomist.api as anatomist

And then create an instance of Anatomist :

>>> a = anatomist.Anatomist()

So you can send commands to Anatomist application, for example creating a window :

>>> window = a.createWindow('3D')


Implementation
==============

Several means of driving Anatomist in python scripts exist : Python bindings for the C++ library (SIP bindings), or sending commands via a network socket. Behind a general interface, this api provides 2 implementations, one for each method.

**Modules organization**

* :mod:`anatomist.base` module contains the general interface : classes and methods that exist in all implementations. This module also provides the general API documentation.
* :mod:`anatomist.socket.api` module contains an implementation using socket communication with an Anatomist application run in another process in server mode.
* :mod:`anatomist.direct.api` module contains an implementation using sip bindings of Anatomist C++ api.
* :mod:`anatomist.threaded.api` module is a thread safe layer for the direct module. Useful if you have to use anatomist api in a multi-threaded environment.
* :mod:`anatomist.headless` module is an off-screen redirection of Anatomist display.
* :mod:`anatomist.notebook` module is a Jupyter Notebook widget proxy, rendering the contents of an Anatomist view.
* :mod:`anatomist.cpp` module contains sip bindings of Anatomist C++ api. It is a low level module, only for advanced user.
* :doc:`pyanatomist_wip` work in progress module

The direct implementation provides more features as it handles  C++ binding objects: all bound features are available. Socket implementation provides features that can be expressed with Anatomist commands system, so a limited set of features. But it runs Anatomist application in a separate process so potential errors in Anatomist don't crash the application that uses the API.

By default, the implementation used when you import anatomist.api is the direct implementation.
If you want to switch to another implementation, use setDefaultImplementation of this module. For example to use the socket implementation :

>>> import anatomist
>>> anatomist.setDefaultImplementation(anatomist.SOCKET)
>>> import anatomist.api as anatomist

Another specific implementation for Brainvisa also exists: brainvisa.anatomist module in brainvisa.
It enables to use brainvisa database informations on loaded objects to automatically load associated referentials and transformations.
It uses the same api, so it is possible to switch from one implementation to the other.

By default, brainvisa module uses the :doc:`direct <pyanatomist_direct>` implementation.

In addition to the Python APIs, the :meth:`Anatomist.execute <base.Anatomist.execute>` method of Anatomist also grants access to the :anadev:`commands system <commands.html>` which offers many functionalities, some of which have not been wrapped yet int the more "pythonic" API.

Attributes
----------
SOCKET: str
    Use this constant to load anatomist api socket implementation. See :mod:`anatomist.socket.api` module.

DIRECT: str
    Use this constant to load anatomist api direct implementation (sip bindings). See :mod:`anatomist.direct.api` module.

THREADED: str
    Use this constant to load anatomist api threaded direct implementation. See :mod:`anatomist.threaded.api` module.

HEADLESS: str
    Identifier of the anatomist api headless implementation. See :mod:`anatomist.headless` module.

NOTEBOOK: str
    Identifier of the anatomist api notebook implementation (inside a jupyter notebook). See :mod:`anatomist.notebook` module.

IMPLEMENTATIONS: tuple
    List of Anatomist API implementations

Methods
-------
getDefaultImplementationModuleName

"""
from __future__ import absolute_import
__docformat__ = 'restructuredtext en'

from anatomist import info
__version__ = '.'.join((info.version_major, info.version_minor,
                        info.version_micro))

SOCKET = 'socket'
DIRECT = 'direct'
THREADED = 'threaded'
HEADLESS = 'headless'
NOTEBOOK = 'notebook'

IMPLEMENTATIONS = (SOCKET, DIRECT, THREADED, HEADLESS, NOTEBOOK)

# import os
#__path__ = [ os.path.join( os.path.dirname( __file__ ), 'direct' ),
# os.path.dirname( __file__ ) ]

_implementation = DIRECT


def setDefaultImplementation(impl=DIRECT):
    """
    Changes the default implementation of this api. The selected implementation will be loaded on importation of anatomist.api.

    Parameters
    ----------
    impl: str
        implementation to set as default. Possible values are :attr:`SOCKET`, :attr:`DIRECT`, :attr:`THREADED`. Default is direct implementation.
    """
    # global __path__
    #__path__ = [ os.path.join( os.path.dirname( __file__ ), impl ),
    # os.path.dirname( __file__ ) ]
    global _implementation
    _implementation = impl


def getDefaultImplementationModuleName():
    global _implementation
    return 'anatomist.' + _implementation
