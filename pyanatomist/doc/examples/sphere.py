
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
import anatomist.direct.api as anatomist
from soma import aims
import types


class ASphere(anatomist.cpp.ASurface_3):

    def __init__(self, mesh=None):
        self._center = aims.Point3df(0, 0, 0)
        self._radius = 100
        if mesh is not None:
            if type(mesh) is types.StringType:
                # mesh is a filename: read it
                anatomist.cpp.ASurface_3.__init__(self, mesh)
                r = aims.Reader()
                m = aims.rc_ptr_AimsTimeSurface_3(r.read(mesh))
                self.setSurface(m)
            else:
                # mesh should be an Aims mesh: assign it
                anatomist.cpp.ASurface_3.__init__(self)
                self.setSurface(mesh)
        else:
            # generate a sphere mesh
            anatomist.cpp.ASurface_3.__init__(self)
            m = aims.rc_ptr_AimsTimeSurface_3(aims.SurfaceGenerator.sphere(
                                              self._center, self._radius, 100))
            self.setSurface(m)

    def radius(self):
        return self._radius

    def center(self):
        return self._center

    def setCenter(self, c):
        if type(c) is not aims.Point3df:
            c = aims.Point3df(*c)
        cdiff = c - self._center
        self._center = c
        # translate all
        v = self.surface().vertex()
        for vi in v:
            vi += cdiff
        self.setChanged()
        self.UpdateMinAndMax()
        self.notifyObservers()

    def setRadius(self, r):
        if r == 0:
            print 'can\'t assign radius 0'
            return
        scl = float(r) / self._radius
        self._radius = float(r)
        # scale all
        v = self.surface().vertex()
        c = self._center
        for vi in v:
            vi.assign((vi - c) * scl + c)
        self.setChanged()
        self.UpdateMinAndMax()
        self.notifyObservers()

# example

if __name__ == '__main__':
    a = anatomist.Anatomist()
    s = ASphere()
    s.setName('sphere')
    a.registerObject(s)

    # import qt
    # qt.qApp.exec_loop()
