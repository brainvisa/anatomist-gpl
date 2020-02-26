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
Events handling
---------------

Catching click events and plugging a callback
'''

from __future__ import print_function

from __future__ import absolute_import
import anatomist.direct.api as anatomist
from soma import aims

a = anatomist.Anatomist()

# definig a custom event handler in python:


def clickHandler(eventName, params):
    print('click event: ', eventName)
    print('LinkedCursor event contents:', list(params.keys()))
    pos = params['position']
    print('pos:', pos)
    win = params['window']
    print('window:', win)

# register the function on the cursor notifier of anatomist. It will be
# called when the user click on a window
a.onCursorNotifier.add(clickHandler)


# definig a custom event in python
class TotoEvent (anatomist.cpp.OutputEvent):

    def __init__(self):
    # we can't make a custom Object yet...
        anatomist.cpp.OutputEvent.__init__(self, 'Toto',
                                           {}, 1)
ev = TotoEvent()
ev.send()

# ...
# wen you're done
# you can remove the handler
# a.onCursorNotifier.remove(clickHandler)
