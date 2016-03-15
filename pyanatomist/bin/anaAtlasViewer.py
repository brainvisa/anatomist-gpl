#!/usr/bin/env python2

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
                      action='append', default=[],
                      help='input model/atlas graph[s] (.arg). Selveral items allowed.')
    parser.add_option('-v', '--volume', dest='volume', metavar='FILE',
                      help='volume which may be viewed optionally')
    parser.add_option('-s', '--sel', dest='selection', metavar='FILE',
                      help='selection file for pre-selected regions/groups')
    parser.add_option('-n', '--nomenclature', dest='nomenclature',
                      metavar='FILE',
                      help='nomenclature file (.hie) for names and colors')

    options, args = parser.parse_args(args[1:])

    app = QApplication(args)
    # interface = AtlasJsonRois( '/home/ml236783/Documents/Code/Atlas/01_seg_83ROI.arg', '/home/ml236783/Documents/Code/Atlas/01_t1mri_83ROI.img', 'Json/Hammers_R83_v2.roi')
    # interface = AtlasJsonRois( '/home/ml236783/Documents/Code/Sujet/LabelsVolume.arg',\
    #                           '/home/ml236783/brainvisa_database/Insight/0040044BERE/t1mri/default_acquisition/SpmNewSegmentation/0040044BERE_default_acquisition_T1_nobias_PetSpc.nii',\
    #                          '/home/ml236783/Documents/Code/Sujet/roiTest.roi')
    # interface = AtlasJsonRois(
    # '/home/ml236783/Bureau/nmr_new/sujet01/t1mri/default_acquisition/default_analysis/folds/3.1/Lsujet01.arg')

    new_args = args
    roi = options.input
    if not roi:
        if len(args) == 0:
            parser.parse_args(['-h'])
        roi = args.pop(0)
    volume = options.volume
    if not volume and len(args) != 0:
        volume = args.pop(0)
    selection = options.selection
    if not selection and len(args) != 0:
        selection = args.pop(0)
    nomenclature = options.nomenclature
    if not nomenclature and len(args) != 0:
        nomenclature = args.pop(0)

    interface = AtlasJsonRois(arg_roi_path=roi, t1mri_vol_path=volume,
                              json_roi_path=selection,
                              nomenclature_path=nomenclature)
    interface.show()
    r = app.exec_()
    return r

if __name__ == "__main__":
    main(sys.argv)
