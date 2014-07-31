#!/usr/bin/env python

import sys
from anatomist.atlas_viewer import AtlasJsonRois
from PyQt4.QtGui import QApplication
from optparse import OptionParser

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def main(args):
  """this method is the main of this script """

  parser = OptionParser('Atlas viewer and ROIs selector')
  parser.add_option('-i', '--input', dest='input', metavar='FILE',
      help='input model/atlas graph (.arg)')
  parser.add_option('-v', '--volume', dest='volume', metavar='FILE',
      help='volume which may be viewed optionally')
  parser.add_option('-s', '--sel', dest='selection', metavar='FILE',
      help='selection file for pre-selected regions/groups')

  options, args = parser.parse_args(args[1:])

  app = QApplication(args)
  #interface = AtlasJsonRois( '/home/ml236783/Documents/Code/Atlas/01_seg_83ROI.arg', '/home/ml236783/Documents/Code/Atlas/01_t1mri_83ROI.img', 'Json/Hammers_R83_v2.roi')
  #interface = AtlasJsonRois( '/home/ml236783/Documents/Code/Sujet/LabelsVolume.arg',\
  #                           '/home/ml236783/brainvisa_database/Insight/0040044BERE/t1mri/default_acquisition/SpmNewSegmentation/0040044BERE_default_acquisition_T1_nobias_PetSpc.nii',\
  #                          '/home/ml236783/Documents/Code/Sujet/roiTest.roi')
  # interface = AtlasJsonRois( '/home/ml236783/Bureau/nmr_new/sujet01/t1mri/default_acquisition/default_analysis/folds/3.1/Lsujet01.arg')

  new_args = args
  if options.input:
      new_args.insert(0, options.input)
  if len(new_args) == 0:
      parser.parse_args(['-h'])
  if options.volume:
      new_args.insert(1, options.volume)
  if options.selection:
      if len(new_args) < 2:
          new_args.append(None)
      new_args.insert(2, options.selection)

  interface = AtlasJsonRois( *new_args )
  interface.show()
  r = app.exec_()
  return r

if __name__ == "__main__":
  main(sys.argv)
