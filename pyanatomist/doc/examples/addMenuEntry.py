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
Adding custom menus in an object options
========================================
'''

from __future__ import print_function

import anatomist.direct.api as anatomist
from soma import aims
import os

a = anatomist.Anatomist()


class MyCallback(anatomist.cpp.ObjectMenuCallback):

    def __init__(self):
        anatomist.cpp.ObjectMenuCallback.__init__(self)

    def doit(self, objects):
        print('plop!!')

# Store python callbacks
callbacks_list = []


# Add plop Menu to an object
def addMenuEntryToOptionTree(object):
    import sip
    m = anatomist.cpp.ObjectMenu(object.optionTree())
    mycallback = MyCallback()
    callbacks_list.append(mycallback)
    m.insertItem([], 'plop!', mycallback)
    m.insertItem(['bloups'], 'plop!', mycallback)
    t = m.releaseTree()
    sip.transferto(t, None)


# Create a dummy AGraph and add plop menu entry
g = aims.Graph('dummy')
ag = a.toAObject(g)
ag.releaseAppRef()
addMenuEntryToOptionTree(ag)


if __name__ == '__main__':
    from soma.qt_gui.qt_backend import Qt
    if Qt.QApplication.startingUp():
        Qt.qApp.exec_()
        del ag, g, callbacks_list
