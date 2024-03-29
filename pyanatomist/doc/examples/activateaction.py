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
Action activation triggering API demo
=====================================

Activate actions in the current control of a window.

Action activation works both in direct and socket APIs
but querying the lists of available action methods is only available in
direct mode.
'''

import anatomist.direct.api as anatomist
from soma.qt_gui.qt_backend import Qt
import sys

runloop = False
if Qt.QApplication.instance() is None:
    runloop = True

a = anatomist.Anatomist()

vol = a.loadObject('irm.ima')
w = a.createWindow('Axial')
w.addObjects(vol)

w.activateAction(action_type='key_press', method='movie_start_stop')
# set backward movie mode
w.activateAction(action_type='key_press', method='movie_next_mode')
# loop forward
w.activateAction(action_type='key_press', method='movie_next_mode')
# loop backward
w.activateAction(action_type='key_press', method='movie_next_mode')
# loop both ways
w.activateAction(action_type='key_press', method='movie_next_mode')

# query available actions methods
c = w.view().controlSwitch().activeControlInstance()
print('in control:', c.name())
kpmethods = c.keyPressActionLinkNames()
print('* keyPress methods:', kpmethods)
mpmethods = c.mousePressActionLinkNames()
print('* mousePress methods:', mpmethods)

w.setControl('SelectionControl')
c = w.view().controlSwitch().activeControlInstance()
print('in control:', c.name())
kpmethods = c.keyPressActionLinkNames()
print('* keyPress methods:', kpmethods)
mpmethods = c.mousePressActionLinkNames()
print('* mousePress methods:', mpmethods)

if runloop:  # and 'sphinx_gallery' not in sys.modules:
    Qt.QApplication.instance().exec_()
if runloop or 'sphinx_gallery' in sys.modules:
    del c, w, vol, kpmethods, mpmethods
