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

import anatomist

import six
import importlib


'''API version, corresponds to the C++ bindings lib version, if loaded.
Thus the version may be None if using the socket API.
'''
__version__ = None

ana_mod = None
error = False
# here we just import the default implementation
for impl in ('anatomist.%s' % anatomist._implementation,
             'anatomist.%s.api' % anatomist._implementation):
    try:
        # try with the api submodule
        ana_mod = importlib.import_module(impl)
        if hasattr(ana_mod, 'Anatomist'):
            break
    except ImportError:
        error = True

if error:
    raise

del impl, error

if ana_mod:
    Anatomist = ana_mod.Anatomist

    if hasattr(ana_mod, 'version'):
        __version__ = ana_mod.version
    elif hasattr(ana_mod, '__version__'):
        __version__ = ana_mod.version

    for k, v in ana_mod.__dict__.items():
        if not k.startswith('__'):
            globals()[k] = v

    del ana_mod
