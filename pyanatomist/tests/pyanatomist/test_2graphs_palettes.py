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
import aims, anatomist, sigraph
import sys, qt


def createWin():
	cmd1 = anatomist.CreateWindowCommand('3D')
	p.execute(cmd1)
	return cmd1.createdWindow()

def addObjectToWin(ag, win):
	cmd2 = anatomist.AddObjectCommand([ag], [win])
	p.execute(cmd2)

def display(list):
	# Display sulci and palettes
	anatomist.ObjectActions.displayGraphChildrenMenuCallback().doit(list)
	import paletteViewer
	paletteViewer.ShowHidePaletteCallback().doit(list)

def read(graphname, palettename):
	# Read graphs
	r = aims.Reader()
	g = r.read(graphname)
	ag = anatomist.AObjectConverter.anatomist(g)

	# Set colors modes
	ag.setColorMode(ag.PropertyMap)
	ag.setColorProperty('size')

	# Change palettes
	p.execute('SetObjectPalette',
		{'objects' : [ag], 'palette' : palettename,
		'min' : 0, 'max' : 1})
	return ag

def test1():
	# Display 2 graphs in 2 separated 3D windows
	ag1 = read('/home/Panabase/data/diffusion/chaos/graphe/RchaosBase.arg',
		'zfun-Plasma')
	win1 = createWin()
	addObjectToWin(ag1, win1)
	display([ag1])
	ag2 =read('/home/Panabase/data/diffusion/cronos/graphe/RcronosBase.arg',
		'Yellow-red-fusion')
	win2 = createWin()
	addObjectToWin(ag2, win2)
	display([ag2])

def test2():
	# Display one graph in 2 separated 3D windows
	ag1 = read('/home/Panabase/data/diffusion/chaos/graphe/RchaosBase.arg',
		'zfun-Plasma')
	win1 = createWin()
	win2 = createWin()
	addObjectToWin(ag1, win1)
	addObjectToWin(ag1, win2)
	display([ag1])

def test3():
	# Display 2 graphs in one 3D window
	ag1 = read('/home/Panabase/data/diffusion/chaos/graphe/RchaosBase.arg',
		'zfun-Plasma')
	ag2 =read('/home/Panabase/data/diffusion/cronos/graphe/RcronosBase.arg',
		'Yellow-red-fusion')
	win1 = createWin()
	addObjectToWin(ag1, win1)
	addObjectToWin(ag2, win1)
	display([ag1, ag2])


if len(sys.argv) == 1:
	print("usage : %s N (N in 0..2)" % sys.argv[0])
	sys.exit(1)
tests = [test1, test2, test3]
t = int(sys.argv[1])

a = anatomist.Anatomist()
p = a.theProcessor()
f = anatomist.FusionFactory.factory()


tests[t]()
qt.qApp.exec_loop()

