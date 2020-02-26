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
Custom fusion example
=====================

Creating a new custom fusion type in Anatomist
'''

from __future__ import print_function

from __future__ import absolute_import
from soma import aims
import os
import anatomist.direct.api as anatomist

a = anatomist.Anatomist()


class MyAObjectKrakboumCallback(anatomist.cpp.ObjectMenuCallback):

    def __init__(self):
        anatomist.cpp.ObjectMenuCallback.__init__(self)

    def doit(self, objects):
        print('MyAObjectKrakboumCallback:', objects)


class MyAObject(anatomist.cpp.AObject):
    _type = anatomist.cpp.AObject.registerObjectType('MyAObject')
    _menus = None
    icon = os.path.join(str(a.anatomistSharedPath()),
                        'icons', 'list_cutmesh.xpm')
    ot = anatomist.cpp.QObjectTree
    ot.setObjectTypeName(_type, 'Example of a custom AObject')
    ot.setObjectTypeIcon(_type, icon)

    def __init__(self, filename=''):
        anatomist.cpp.AObject.__init__(self, filename)
        self.setType(MyAObject._type)
        self.setReferential(a.centralReferential())

    def optionTree(self):
        # set new option menus on this new object type
        if MyAObject._menus is None:
            m = anatomist.cpp.ObjectMenu()
            krak = MyAObjectKrakboumCallback()
            m.insertItem(['File'], 'Reload',
                         anatomist.cpp.ObjectActions.fileReloadMenuCallback())
            m.insertItem(['Color'], 'Material',
                         anatomist.cpp.ObjectActions.colorMaterialMenuCallback())
            m.insertItem(['Rototo', 'pouet'], 'krakboum', krak)
            MyAObject._menus = m.releaseTree()
            # avoid deleting the python part of the callback
            MyAObject._nodelete = [krak]
        return MyAObject._menus


class MyFusion(anatomist.cpp.FusionMethod):

    def __init__(self):
        anatomist.cpp.FusionMethod.__init__(self)
        print("init myfusion")

    def canFusion(self, objects):
        print("MyFusion : canFusion")
        return 120

    def fusion(self, objects):
        print("MyFusion : fusion")
        return MyAObject()

    def ID(self):
        return 'myFusion'

    def orderingMatters(self):
        return False

# Register MyFusion
anatomist.cpp.FusionFactory.registerMethod(MyFusion())

# Load an object
obj = a.loadObject('test.mesh')

# if __name__ == '__main__' :
    # import qt
    # if qt.QApplication.startingUp():
        # qt.qApp.exec_loop()
