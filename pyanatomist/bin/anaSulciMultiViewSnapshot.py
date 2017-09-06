#!/usr/bin/env python2
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
from __future__ import print_function
from soma import aims
import anatomist, sigraph
import os, sys, sip, numpy, time
import soma.qt_gui.qt_backend.QtCore as qt
import soma.qt_gui.qt_backend.QtGui as qtgui

context = anatomist.CommandContext.defaultContext()
a = anatomist.Anatomist()
p = a.theProcessor()
f = anatomist.FusionFactory.factory()


def createWin(block):
	id = context.freeID()
	cmd1 = anatomist.CreateWindowCommand('3D', id, None, [], 1, block, 3)
	p.execute(cmd1)
	win = cmd1.createdWindow()
	return win

def createFirstWin():
	id = context.freeID()
	cmd1 = anatomist.CreateWindowCommand('3D', id, None, [], 1, None, 3)
	p.execute(cmd1)
	block = cmd1.block()
	win = cmd1.createdWindow()
	return win, block

def addObjectToWin(ag, win):
	cmd2 = anatomist.AddObjectCommand([ag], [win])
	p.execute(cmd2)

def addObjectsToWins(ags, wins):
	cmd2 = anatomist.AddObjectCommand(ags, wins)
	p.execute(cmd2)

def setCamera(win, orientation):
	q = aims.Quaternion()
	q2 = aims.Quaternion()
	if orientation == 'top' :
		q.fromAxis([0, 1, 0], 0)
	elif orientation == 'try1' :
		q.fromAxis([0, 1, 0], numpy.pi)
	elif orientation == 'try2' :
		q.fromAxis([0, 1, 0], numpy.pi)
		q.fromAxis([1, 0, 0], numpy.pi)
	elif orientation == 'back' :
		q.fromAxis([1, 0, 0], -numpy.pi / 2)
		q2.fromAxis([0, 1, 0], numpy.pi)
		q = q.compose(q2)
	elif orientation == 'left' :
		q.fromAxis([0, 1, 0], numpy.pi / 2.)
		q2.fromAxis([1, 0, 0], numpy.pi / 2.)
		q = q.compose(q2)
	elif orientation == 'right' :
		q.fromAxis([0, 1, 0], -numpy.pi / 2.)
		q2.fromAxis([1, 0, 0], numpy.pi / 2.)
		q = q.compose(q2)
	elif orientation == 'left2' :
		q.fromAxis([0, 1, 0], numpy.pi / 2.)
	elif orientation == 'right2' :
		q.fromAxis([0, 1, 0], -numpy.pi / 2.)
		q2.fromAxis([1, 0, 0], numpy.pi)
		q = q.compose(q2)
	elif orientation == 'front' :
		q.fromAxis([1, 0, 0], numpy.pi / 2)
	p.execute("Camera", {'windows' : [win],
		'zoom' : 3,
		'observer_position' : [10., 10., 10.],
		'view_quaternion' : q.vector(),
		'force_redraw' : True})



def display(list):
	anatomist.ObjectActions.displayGraphChildrenMenuCallback().doit(list)

def read(graphname):
	# Read graphs
	r = aims.Reader()
	g = r.read(graphname)
	ag = anatomist.AObjectConverter.anatomist(g)
	return ag

def load(filename):
	cmd = anatomist.LoadObjectCommand(filename)
	p.execute(cmd)
	return cmd.loadedObject()

def display_graph_6_views(graphname, meshname, imagename):
	shared_path = os.path.dirname(a.anatomistSharedPath().latin1())
	hiename = os.path.join(shared_path, 'shfj-3.1', 'nomenclature',
			'hierarchy', 'sulcal_root_colors.hie')
	print(graphname, meshname, hiename)
	# Display 2 graphs in 2 separated 3D windows
	ag = read(graphname)
	tri = load(meshname)
	hie = load(hiename)

	# Windows
	win0, block = createFirstWin()
	win1 = createWin(block)
	win2 = createWin(block)
	win3 = createWin(block)
	win4 = createWin(block)
	win5 = createWin(block)
	wins = {'left2' : win0, 'right2' : win1, 'top' : win2, 'front' : win3,
		'back' : win4, 'bottom' : win5}
	for orientation, win in wins.items():
		setCamera(win, orientation)
		# remove cursor (referential)
		win.setHasCursor(0)
		win.Refresh()
	# hide toolbar/menu
	for win in wins.values(): win.showTools(0)
	addObjectsToWins([ag, tri, hie], wins.values())
	display([ag])
	# see sulci colors
	ag.setColorMode(ag.Normal)
	ag.updateColors()
	ag.notifyObservers()
	ag.setChanged()
	topwin = win.parent()
	# fullscreen
	topwin.setWindowState(topwin.windowState() | qt.Qt.WindowFullScreen)
	winid = topwin.winId()
	# screenshot
	os.system('(xset dpms force on && sleep 20 && '
		'import -window %d %s && kill -9 %s)&' % \
			(winid, imagename, os.getpid()))
	return wins

def main():
    if len(sys.argv) != 4:
        g = '/home/Panabase/data/subjects/zeus/graphe/RzeusBase.arg'
        t1 = '/home/Panabase/data/subjects/zeus/tri/zeus_Rhemi.tri'
        t2 = '/home/Panabase/data/subjects/zeus/tri/Rzeus_white.tri'
        img = 'plop.png'
        cmd = os.path.basename(sys.argv[0])
        print("Display one sulci graph + one mesh (grey/white) on"
              "6 standard views.\n")
        print("Usage %s graphname meshname image" % cmd)
        print("  ex : %s %s %s %s" % (cmd, g, t1, img))
        print("       %s %s %s %s" % (cmd, g, t2, img))
        sys.exit(1)
    graphname, meshname, imagename = sys.argv[1:]
    display_graph_6_views(graphname, meshname, imagename)
    qtgui.qApp.exec_()

main()
