
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
numtypes = ['unsigned char', 'short', 'unsigned short', 'int',
            'unsigned', 'float', 'double']
basetypes = numtypes + ['AimsRGB', 'AimsRGBA']
matrix = []
for z in [[(x, y) for y in basetypes] for x in basetypes]:
    matrix += z

todo = {'rcptr': ['anatomist::EventHandler', 'anatomist::Unserializer',
                  'anatomist::GLItem', 'anatomist::AObject',
                  'anatomist::AWindow', 'anatomist::APalette',
                  'anatomist::ObjectMenu', 'anatomist::ViewState'],
        'asurface': ['3', '2'],
        'control': ['Void'],
        'vector': ['anatomist::AObject *'],
        'list': ['carto::rc_ptr<anatomist::APalette>',
                 'anatomist::RefGLItem', 'anatomist::Transformation *',
                 'anatomist::AObject *'],
        'set': ['anatomist::AObject *', 'anatomist::AWindow *',
                'anatomist::Referential *', 'anatomist::Transformation *'],
        'map': [('unsigned', 'std::set<anatomist::AObject *>'),
                ('unsigned', 'std::set<anatomist::AWindow *>'),
                ('int', 'QPixmap'),
                ('std::string', 'carto::rc_ptr<anatomist::ObjectMenu>')],
        'anatomist': ['Void'],
        'sharedptr': ['anatomist::AObject', 'anatomist::AWindow'],
        'volumeview': basetypes,
        'glwidget': ['Void'],
        }
