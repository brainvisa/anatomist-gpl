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

- organization: `NeuroSpin <http://www.neurospin.org>`_ and `IFR 49 <http://www.ifr49.org>`_

- license: `CeCILL-v2 <http://www.cecill.info/licences/Licence_CeCILL_V2-en.html>`_ (GPL-compatible)

The main entry point is one of the :py:class:`anatomist.base.Anatomist`-inhertied classes which must be instantiated before any operation can be performed.
It represents Anatomist application. This class contains a number of nested classes: :py:class:`anatomist.base.Anatomist.AObject`, :py:class:`anatomist.base.Anatomist.AWindow`... that represents handling elements of Anatomist application.

The entry point of this API is the module api, you can import it as below :

  >>> import anatomist.api as anatomist

And then create an instance of Anatomist :

  >>> a=anatomist.Anatomist()

So you can send commands to Anatomist application, for example creating a window :

  >>> window=a.createWindow('3D')


Implementation
==============

Several means of driving Anatomist in python scripts exist : Python bindings for the C++ library (SIP bindings), or sending commands via a network socket. Behind a general interface, this api provides 2 implementations, one for each method.

**Modules organization**

  - :py:mod:`anatomist.base` module contains the general interface : classes and methods that exist in all implementations. This module also provides the general API documentation.
  - :py:mod:`anatomist.socket.api` module contains an implementation using socket communication with an Anatomist application run in another process in server mode.
  - :py:mod:`anatomist.direct.api` module contains an implementation using sip bindings of Anatomist C++ api.
  - :py:mod:`anatomist.threaded.api` module is a thread safe layer for the direct module. Useful if you have to use anatomist api in a multi-threaded environment.
  - :py:mod:`anatomist.cpp` module contains sip bindings of Anatomist C++ api. It is a low level module, only for advanced user.
  - :py:mod:`anatomist.wip` work in progress module

The direct implementation provides more features as it handles  C++ binding objects : all bound features are available. Socket implementation provides features that can be expressed with Anatomist commands system, so a limited set of features. But it runs Anatomist application in a separate process so potential errors in Anatomist don't crash the application that uses the API.

By default, the implementation used when you import anatomist.api is the direct implementation.
If you want to switch to another implementation, use setDefaultImplementation of this module. For example to use the socket implementation :

  >>> import anatomist
  >>> anatomist.setDefaultImplementation(anatomist.SOCKET)
  >>> import anatomist.api as anatomist

Another specific implementation for Brainvisa also exists : brainvisa.anatomist module in brainvisa.
It enables to use brainvisa database informations on loaded objects to automatically load associated referentials and transformations.
It uses the same api, so it is possible to switch from one implementation to the other.

By default, brainvisa module uses socket implementation. This way, Brainvisa and Anatomist applications run in separated processes. and potential errors in Anatomist do not crash Brainvisa.


.. data:: anatomist.SOCKET

  type: string

  Use this constant to load anatomist api socket implementation. See :py:mod:`anatomist.socket.api` module.

.. data:: DIRECT

  type : string

  Use this constant to load anatomist api direct implementation (sip bindings). See :py:mod:`anatomist.direct.api` module.

.. data:: THREADED

  type: string

  Use this constant to load anatomist api threaded direct implementation. See :py:mod:`anatomist.threaded.api` module.
"""

SOCKET='socket'
DIRECT='direct'
THREADED='threaded'

#import os
#__path__ = [ os.path.join( os.path.dirname( __file__ ), 'direct' ),
  #os.path.dirname( __file__ ) ]

_implementation = DIRECT

def setDefaultImplementation( impl=DIRECT ):
  """
  Changes the default implementation of this api. The selected implementation will be loaded on importation of anatomist.api.
  @type impl: string
  @param impl: implementation to set as default. Possible values are anatomist.SOCKET, anatomist.DIRECT, anatomist.THREADED. Default is direct implementation.
  """
  #global __path__
  #__path__ = [ os.path.join( os.path.dirname( __file__ ), impl ),
    #os.path.dirname( __file__ ) ]
  global _implementation
  _implementation = impl

def getDefaultImplementationModuleName():
  global _implementation
  return 'anatomist.' + _implementation + '.api'
