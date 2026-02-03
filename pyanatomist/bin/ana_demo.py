#!/usr/bin/env python


import sys
from soma.qt_gui import ipkernel_tools
import anatomist.api as ana
from soma import aims
from soma.aims import demotools
import os
import os.path as osp
import tempfile
import numpy as np

# install demo data (copy/paste from the tutorial notebook)

temp_dirs = []
older_cwd = os.getcwd()
install_dir = os.path.join(aims.carto.Paths.globalShared(), 'brainvisa_demo')
try:
    # download demo data
    demotools.install_demo_data('demo_data.zip', install_dir=install_dir)
except Exception:
    # maybe we don't have write permission in the directory
    # try again in a temp directory
    install_dir = tempfile.mkdtemp(prefix='pyanatomist_tutorial_')
    temp_dirs.append(install_dir)

    # download demo data
    demotools.install_demo_data('demo_data.zip', install_dir=install_dir)

os.chdir(install_dir)
print('we are working in:', install_dir)
os.chdir(install_dir)

# setup ipython kernel

ipkernel_tools.before_start_ipkernel()

a = ana.Anatomist(*sys.argv[1:])
# exits abruptly when closing the control window. Works around the callback
# problem: when the event loop runs through ipython kernel,
# QApplication.aboutToQuit signals are never executed, thus cannot actually
# quit.
a.setExitOnQuit(True)

src = os.path.join(install_dir, "data_for_anatomist", "subject01")

t1mri = a.loadObject(osp.join(src, "subject01.nii"))
head = a.loadObject(osp.join(src, 'subject01_head.mesh'))
lpial = a.loadObject(osp.join(src, 'subject01_Lhemi.mesh'))
rpial = a.loadObject(osp.join(src, 'subject01_Rhemi.mesh'))
rwhite = a.loadObject(osp.join(src, 'subject01_Rwhite.mesh'))
nom = a.loadObject(aims.carto.Paths.findResourceFile(
    'nomenclature/hierarchy/sulcal_root_colors.hie'))
sulci = a.loadObject(osp.join(src, 'sulci/Lsubject01_default_session_auto.arg'))

vr = a.fusionObjects([t1mri], method='VolumeRenderingFusionMethod')
clip1 = a.fusionObjects([vr], method='FusionClipMethod')
clip2 = a.fusionObjects([vr], method='FusionClipMethod')
mid = np.sum([b.np for b in t1mri.boundingbox()], axis=0) / 2
s2 = np.sqrt(2.)
a.execute('SliceParams', objects=[clip2], position=mid,
          quaternion=[0., s2, s2, 0.])
head.setMaterial(diffuse=[0.8, 0.75, 0.66, 0.19])
lpial.setMaterial(diffuse=[0.8, 0.8, 0.5, 1.])
rwhite.setMaterial(diffuse=[0.48, 0.73, 0.4, 1.])
rpial.setMaterial(diffuse=[0.8, 0.8, 0.5, 0.6])
lcut = a.fusionObjects([lpial, t1mri], method='FusionCutMeshMethod')
a.execute('SliceParams', objects=[lcut],
          position=[128.832290649414, 71.6069183349609, 51.6672401428223],
          quaternion=[0.00756764598190784,
                      0.321447312831879,
                      0.89443838596344,
                      0.310796171426773])

win = a.createWindow('3D')
win.addObjects([clip1, clip2, head, lcut, rwhite, rpial, sulci])
win.windowConfig(view_size=[1000, 800], light={'background': [0., 0., 0., 1.]})

ipkernel_tools.start_ipkernel_qt_engine()
