#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import anatomist.direct.api as ana
from soma import aims
import os, numpy, sys
from soma.qt_gui.qt_backend import QtGui

byvertex = False

# This intermediate class is only here because I cannot (yet) make SIP
# generate a non-abstract class for TextObject binding. One day, I'll find out!
class TObj ( ana.cpp.TextObject ):
  def __init__( self, message='', pos=[0,0,0] ):
    ana.cpp.TextObject.__init__( self, message, pos )

class Props( object ):
  def __init__( self ):
    self.lvert = []
    self.lpoly = []
    self.usespheres = True
    self.colorlabels = True
    self.center = aims.Point3df()

def makelabel( label, gc, pos, color, props ):
  objects = []
  to = TObj( label )
  to.setScale( 0.1 )
  to.setName( 'label: ' + label )
  if colors.has_key( label ):
    color = colors[ label ]
    if props.usespheres:
      sph = aims.SurfaceGenerator.icosphere( gc, 2, 50 )
      asph = a.toAObject( sph )
      asph.setMaterial( diffuse=color )
      asph.setName( 'gc: ' + label )
      a.registerObject( asph, False )
      objects.append( asph )
    if props.colorlabels:
      to.GetMaterial().set( { 'diffuse': color } )
  texto = ana.cpp.TransformedObject( [ to ], False, True, pos )
  texto.setDynamicOffsetFromPoint( props.center )
  texto.setName( 'annot: ' + label )
  objects.append( texto )
  props.lpoly.append( aims.AimsVector_U32_2( ( len( props.lvert ),
    len( props.lvert ) + 1 ) ) )
  props.lvert += [ gc, pos ]
  a.registerObject( texto, False )
  return objects


runloop = False
if QtGui.QApplication.startingUp():
  qapp = QtGui.QApplication( sys.argv )
  runloop = True

a = ana.Anatomist()
share = aims.carto.Paths.globalShared()
nomenclname = os.path.join( aims.carto.Paths.shfjShared(), 'nomenclature',
  'hierarchy', 'sulcal_root_colors.hie' )
graphname = os.path.join( share, 'doc', 'pyanatomist-' + '.'.join( [ str(x) for x in aims.version() ] ), 'examples', 'Rbase.arg' )
labelatt = 'name'

nomenclature = a.loadObject( nomenclname )
graph = aims.read( graphname )
if graph.has_key( 'label_property' ):
  labelatt = graph[ 'label_property' ]
agraph = a.toAObject( graph )
w = a.createWindow( '3D' )
w.addObjects( agraph , add_graph_nodes=True )
#lgraphaims = aims.Graph( 'labelsGraph' )
#lgraph = a.toAObject( lgraphaims )

bbox = agraph.boundingbox()
props = Props()
props.center = ( bbox[0] + bbox[1] ) / 2

size = ( bbox[1] - bbox[0] ).norm() * 0.2
vs = graph[ 'voxel_size' ][:3]
objects = []
lines = aims.TimeSurface( 2 )


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
        pos = gc + ( gc - props.center ).normalize() * size
        objects += makelabel( label, gc, pos, color, props )


if not byvertex:
  for label, elem in elements.iteritems():
    gc = elem[0] / elem[1]
    pos = gc + ( gc - props.center ).normalize() * size
    if colors.has_key( label ):
      color = colors[ label ]
    else:
      color = [ 0, 0, 0, 1 ]
    objects += makelabel( label, gc, pos, color, props )

lines.vertex().assign( props.lvert )
lines.polygon().assign( props.lpoly )
alines = a.toAObject( lines )
alines.setMaterial( diffuse=[ 0, 0, 0, 1 ] )
objects.append( alines )
labels = a.groupObjects( objects )
w.addObjects( labels, add_children=True )

if runloop:
  qapp.exec_()

