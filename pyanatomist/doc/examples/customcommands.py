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
Anatomist commands
------------------

Using the commands interpreter in a generic way
'''

from __future__ import print_function

from __future__ import absolute_import
import anatomist.direct.api as anatomist
from soma import aims
from soma.qt_gui.qt_backend import Qt
import sip
import sys

run_loop = Qt.QApplication.instance() is None \
    and 'sphinx_gallery' not in sys.modules

a = anatomist.Anatomist()

cx = anatomist.cpp.CommandContext.defaultContext()

# custom command
i = cx.freeID()
c = a.execute('CreateWindow', type='Coronal', res_pointer=i)

win = c.createdWindow()

# otherwise, we can retreive the new window using the context
# (which will work if the exact command has no python binding)
print(cx.id(win))
print(cx.object(i))
win2 = cx.object(i)

print(win2 is win)

vol = aims.read('irm.ima')
avol = a.toAObject(vol)
avol.releaseAppRef()

# keywords / real objects test
a.execute('AddObject', objects=[avol], windows=[win])

if run_loop:
    Qt.QApplication.instance().exec_

if run_loop or 'sphinx_gallery' not in sys.modules:
    del win, win2, avol, vol, cx, i
