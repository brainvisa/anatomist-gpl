#!/usr/bin/env python

import sys
from anatomist.atlas_viewer import AtlasJsonRois
from PyQt4.QtGui import QApplication

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def main(args):
  """this method is the main of this script """
  app = QApplication(args)
  #interface = AtlasJsonRois( '/home/ml236783/Documents/Code/Atlas/01_seg_83ROI.arg', '/home/ml236783/Documents/Code/Atlas/01_t1mri_83ROI.img', 'Json/Hammers_R83_v2.roi')
  #interface = AtlasJsonRois( '/home/ml236783/Documents/Code/Sujet/LabelsVolume.arg',\
  #                           '/home/ml236783/brainvisa_database/Insight/0040044BERE/t1mri/default_acquisition/SpmNewSegmentation/0040044BERE_default_acquisition_T1_nobias_PetSpc.nii',\
  #                          '/home/ml236783/Documents/Code/Sujet/roiTest.roi')
  # interface = AtlasJsonRois( '/home/ml236783/Bureau/nmr_new/sujet01/t1mri/default_acquisition/default_analysis/folds/3.1/Lsujet01.arg')
  interface = AtlasJsonRois( *sys.argv[1:] )
  interface.show()
  r = app.exec_()
  return r

if __name__ == "__main__":
  main(sys.argv)
