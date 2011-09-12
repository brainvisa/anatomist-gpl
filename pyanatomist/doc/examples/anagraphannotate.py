#!/usr/bin/env python
# -*- coding: utf-8 -*-

import anatomist.direct.api as ana
from soma import aims
import os, numpy, sys
from PyQt4 import QtGui

byvertex = False
usespheres = True
colorlabels = True

runloop = False
if QtGui.QApplication.startingUp():
  qapp = QtGui.QApplication( sys.argv )
  runloop = True

a = ana.Anatomist()
share = aims.carto.Paths.globalShared()
nomenclname = os.path.join( aims.carto.Paths.shfjShared(), 'nomenclature',
  'hierarchy', 'sulcal_root_colors.hie' )
graphname = os.path.join( share, 'doc', 'pyanatomist-' + '.'.join( [ str(x) for x in aims.version() ] ), 'examples', 'Rbase.arg' )
#graphname = '/neurospin/lnao/Panabase/database_learnclean/nmr/sujet01/t1mri/t1/default_analysis/folds/3.1/base2011_manual/Lsujet01_base2011_manual.arg'
labelatt = 'name'

nomenclature = a.loadObject( nomenclname )
graph = aims.read( graphname )
if graph.has_key( 'label_property' ):
  labelatt = graph[ 'label_property' ]
agraph = a.toAObject( graph )
w = a.createWindow( '3D' )
w.addObjects( agraph , add_graph_nodes=True )

bbox = agraph.boundingbox()
center = ( bbox[0] + bbox[1] ) / 2
size = ( bbox[1] - bbox[0] ).norm() * 0.2
vs = graph[ 'voxel_size' ][:3]
objects = []
lines = aims.TimeSurface( 2 )
lvert = []
lpoly = []

class TObj ( ana.cpp.TextObject ):
  def __init__( self, message='', pos=[0,0,0] ):
    ana.cpp.TextObject.__init__( self, message, pos )

def makelabel( label, gc, pos, color ):
  global objects, lvert, lpoly, usespheres, colorlabels, center
  to = TObj( label )
  to.setScale( 0.1 )
  to.setName( 'label: ' + label )
  if colors.has_key( label ):
    color = colors[ label ]
    if usespheres:
      sph = aims.SurfaceGenerator.icosphere( gc, 2, 50 )
      asph = a.toAObject( sph )
      asph.setMaterial( diffuse=color )
      asph.setName( 'gc: ' + label )
      a.registerObject( asph )
      objects.append( asph )
    if colorlabels:
      to.GetMaterial().set( { 'diffuse': color } )
  texto = ana.cpp.TransformedObject( [ to ], False, True, pos )
  texto.setDynamicOffsetFromPoint( center )
  texto.setName( 'annot: ' + label )
  objects.append( texto )
  lpoly.append( aims.AimsVector_U32_2( ( len( lvert ), len( lvert ) + 1 ) ) )
  lvert += [ gc, pos ]
  a.registerObject( texto )

elements = {}
colors = {}

for v in graph.vertices():
  if v.has_key( 'gravity_center' ) and v.has_key( labelatt ):
    gc = aims.Point3df( numpy.array( v['gravity_center' ] ) * vs )
    label = v[ labelatt ]
    if label != 'unknown':
      if not elements.has_key( label ):
        elem = [ aims.Point3df( 0, 0, 0 ), 0. ]
        elements[ label ] = elem
      else:
        elem = elements[ label ]
      sz = v[ 'size' ]
      elem[0] += gc * sz
      elem[1] += sz
      color = [ 0, 0, 0, 1 ]
      if v.has_key( 'ana_object' ):
        av = v[ 'ana_object' ]
        color = av.GetMaterial().genericDescription()[ 'diffuse' ]
        colors[ label ] = color
      if byvertex:
        pos = gc + ( gc - center ).normalize() * size
        makelabel( label, gc, pos, color )


if not byvertex:
  for label, elem in elements.iteritems():
    gc = elem[0] / elem[1]
    pos = gc + ( gc - center ).normalize() * size
    if colors.has_key( label ):
      color = colors[ label ]
    else:
      color = [ 0, 0, 0, 1 ]
    makelabel( label, gc, pos, color )

lines.vertex().assign( lvert )
lines.polygon().assign( lpoly )
alines = a.toAObject( lines )
alines.setMaterial( diffuse=[ 0, 0, 0, 1 ] )
w.addObjects( alines )
w.addObjects( objects )

if runloop:
  qapp.exec_()

