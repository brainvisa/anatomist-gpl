# -*- coding: utf-8 -*-
import anatomist.direct.api as ana
from soma import aims
from soma.aims import colormaphints
import sys, os

# determine wheter we are using Qt4 or Qt3, and hack a little bit accordingly
# the boolean qt4 gloabl variable will tell it for later usage
qt4 = False
if sys.modules.has_key( 'PyQt4'):
  qt4 = True
  from PyQt4 import QtCore, QtGui
  qt = QtGui
  from PyQt4.uic import loadUi
else:
  import qt, qtui
  loadUi = qtui.QWidgetFactory.create

# do we have to run QApplication ?
if qt.qApp.startingUp():
  qapp = qt.QApplication( sys.argv )
  runqt = True
else:
  runqt = False

# splash
pix = qt.QPixmap( os.path.expandvars( '$BRAINVISA_SHARE/anatomist-3.2/icons/anatomist.png' ) )
spl = qt.QSplashScreen( pix )
spl.show()
qt.qApp.processEvents()

# start the Anatomist engine, in batch mode (no main window)
a = ana.Anatomist()

#a = anatomist.Anatomist()

# create a sphere mesh
m = aims.SurfaceGenerator.sphere( aims.Point3df( 0 ), 100, 100 )
mesh = a.toAObject( m )

# Create a new 3D window in Anatomist
aw = a.createWindow( '3D' )

# Put the mesh in the created window
a.addObjects( mesh, aw )

g=a.getDefaultWindowsGroup()
#sel = anatomist.SelectFactory.factory()
print 'mesh isSelected:', g.isSelected( mesh )
print 'selecting it'
g.setSelection( mesh )
print "selection in default group", a.getSelection()
print "selection de", g, g.getSelection()
sel=g.getSelection()
#print mesh, sel, mesh == sel[0], mesh is sel[0]
#print 'mesh isSelected:', g.isSelected( mesh )

# run Qt
if runqt:
  if qt4:
    qapp.exec_()
  else:
    qapp.exec_loop()
