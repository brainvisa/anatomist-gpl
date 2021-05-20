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

from __future__ import absolute_import
import anatomist.cpp as anatomist
from soma import aims
import numpy


class ObjectFollowerCube(anatomist.ASurface_2):
    def __init__(self, obj):
        anatomist.ASurface_2.__init__(self)
        self.GetMaterial().set({'ghost': 1})
        self._objects = []
        # print 'ObjectFollowerCube.__init__, objects:', len( obj )
        self.setSurface(aims.AimsTimeSurface_2_VOID())
        self.setObserved(obj)

    def observed(self):
        return self._objects

    def setObserved(self, obj):
        #print 'setObserved', len(obj)
        oldobj = [i for i in self._objects]
        for i in oldobj:
            self.unregisterObservable(i.get())
        del oldobj
        self._objects = [anatomist.weak_ptr_AObject(i) for i in obj]
        for i in obj:
            self.registerObservable(i)
        self.redraw()

    def update(self, obs, param):
        #print 'ObjectFollowerCube.update'
        if obs in self._objects:
            self.redraw()
            self.notifyObservers(obs)

    def unregisterObservable(self, obs):
        #print 'ObjectFollowerCube.unregisterObservable', obs
        obss = anatomist.weak_ptr_AObject(obs)
        if obss in self._objects:
            self._objects = [i for i in self._objects if i != obss]
            self.redraw()

    def boundingbox(self):
        #print 'ObjectFollowerCube.boundingbox', len( self._objects )
        bbox = []
        for obj in self._objects:
            bbox2 = [aims.Point3df(x[:3]) for x in obj.boundingbox()]
            if not bbox2:
                # this object has no bbox
                continue
            a = anatomist.Anatomist()
            tr = a.getTransformation(obj.getReferential(),
                                     self.getReferential())
            if tr is not None:
                bbox2 = tr.transformBoundingBox(bbox2[0], bbox2[1])
            if not bbox:
                bbox = bbox2
            else:
                bbox = [numpy.min([bbox[0], bbox2[0]], axis=0),
                        numpy.max([bbox[1], bbox2[1]], axis=0)]
                #print 'bbox:', bbox
        if not bbox:
            return ()
        return (aims.vector_FLOAT(bbox[0]), aims.vector_FLOAT(bbox[1]))

    def redraw(self):
        if hasattr(self, '_redrawing'):
            return
        self._redrawing = True
        #print 'ObjectFollowerCube.redraw'
        mesh = self.surface()
        if mesh.isNull():
            self.setSurface(aims.AimsTimeSurface_2_VOID())
            mesh = self.surface()
        if len(self._objects) == 0:
            mesh.vertex().assign([])
            mesh.normal().assign([])
            mesh.polygon().assign([])
        else:
            bbox = self.boundingbox()
            if len(bbox) == 2:
                cube = aims.SurfaceGenerator.parallelepiped_wireframe(
                    bbox[0][:3], bbox[1][:3])
                mesh.vertex().assign(cube.vertex())
                mesh.polygon().assign(cube.polygon())
        self.setChanged()
        del self._redrawing
