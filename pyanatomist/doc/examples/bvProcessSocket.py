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
from neuroProcesses import *
import shfjGlobals
import string

name = 'Test anatomist API socket implementation'
userLevel = 0

# by default, socket implementation is loaded in brainvisa
from brainvisa import anatomist as pyanatomist
import anatomist.api

signature = Signature(
  'object_to_load', ReadDiskItem( "3D Volume", shfjGlobals.anatomistVolumeFormats ),
  )

def initialization( self ):
  pass

def execution( self, context ):
  # register a function that will be called when Anatomist application starts
  pyanatomist.Anatomist.addCreateListener(displayCreation)
  # with attribute create is False, the constructor returns the existing instance of anatomist or None if there isn't one.
  a=pyanatomist.Anatomist(create=False)
  print "anatomist instance:", a
  a=pyanatomist.Anatomist(create=True)
  print "anatomist instance:", a
  # register a function to be called when an object is loaded in anatomist
  a.onLoadNotifier.add(display)
  #a.onLoadNotifier.remove(display)
  #a.onCreateWindowNotifier.add(display)
  #a.onDeleteNotifier.add(display)
  #a.onFusionNotifier.add(display)
  #a.onCloseWindowNotifier.add(display)
  #a.onAddObjectNotifier.add(display)
  #a.onRemoveObjectNotifier.add(display)
  #a.onCursorNotifier.add(display)
  obj=a.loadObject(self.object_to_load)
  w=a.createWindow('Axial')
  a.addObjects([obj], [w])
  ref=obj.referential
  context.write( "referential of object :", ref.refUuid)
  return [obj, w, ref]
  
def display(event, params):
  print "** Event ** ",event, params
  
def displayCreation(instance):
  print "** Creation of an anatomist instance", instance
  
