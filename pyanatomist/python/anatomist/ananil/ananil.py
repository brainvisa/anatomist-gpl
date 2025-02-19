
import anatomist.direct.api as ana
from soma.qt_gui.qt_backend import Qt
from soma import aims
import numpy as np
import os
import os.path as osp
import glob


class ContrastPanel(Qt.QMainWindow):
    '''
    Anatiomist-based application for fMRI results display (would be used after
    nilearn).
    Currently it displays a list of subjects / contrasts with checkboxes, and
    loads/displays data accordingly.
    It has to be run from the study data root directory, or the user can use
    the menu "open study".

    For now it's just a draft which should merely be seen as a basis for
    discussion.

    As always the main difficulties are handling coordinates systems and
    transformations.
    '''

    class SubViews:
        axial_view = 0
        coronal_view = 1
        sagittal_view = 2
        values_view = 4
        info_view = 5
        td_view = 3

    views_per_sub = 6
    sv = SubViews()

    def __init__(self):
        super().__init__()

        self.study_dir = ''
        self.fmriprep_dir = 'fMRIprep'
        self.fmri_anal_dir = 'first_level'
        self.morpho_dir = 'morphologist'
        self.morpho_layout = 'bids'
        self.disp_subjects = {}
        self.sub_data = {}
        self.binarize_multi_z = True
        self.binarize_threshold = 1.96  # Z for p == 0.05

        menu = self.menuBar()
        filem = menu.addMenu('File')
        opendir = filem.addAction('&Open study directory')
        opendir.triggered.connect(self.open_study)
        filem.addSeparator()
        quit = filem.addAction('&Quit')
        a = ana.Anatomist()
        quit.triggered.connect(self.quit)

        cw = Qt.QWidget()
        self.setCentralWidget(cw)
        lay = Qt.QHBoxLayout(cw)
        split = Qt.QSplitter()
        self.splitter = split
        lay.addWidget(split)

        sub_wid = Qt.QWidget()
        sub_lay = Qt.QVBoxLayout(sub_wid)
        split.addWidget(sub_wid)
        sub_lay.addWidget(Qt.QLabel('Subjects:'))
        self.sub_box = Qt.QListWidget()
        sub_lay.addWidget(self.sub_box)
        self.sub_box.itemClicked.connect(self.sub_clicked)

        zmap_wid = Qt.QWidget()
        zmap_lay = Qt.QVBoxLayout(zmap_wid)
        split.addWidget(zmap_wid)
        zmap_lay.addWidget(Qt.QLabel('Zmaps:'))
        self.zmap_box = Qt.QListWidget()
        zmap_lay.addWidget(self.zmap_box)
        self.zmap_box.itemClicked.connect(self.zmap_clicked)

        ctr_wid = Qt.QWidget()
        ctr_lay = Qt.QVBoxLayout(ctr_wid)
        split.addWidget(ctr_wid)
        ctr_lay.addWidget(Qt.QLabel('Contrasts:'))
        self.ctr_box = Qt.QListWidget()
        ctr_lay.addWidget(self.ctr_box)
        self.ctr_box.itemClicked.connect(self.contrast_clicked)

        self.block = a.createWindowsBlock(visible=True, default_block=True)
        split.addWidget(self.block.internalWidget.widget)

        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 0)
        split.setStretchFactor(2, 0)
        split.setStretchFactor(3, 10)

        self.init_study()

    def quit(self):
        a = ana.Anatomist()
        a.quit()

    def open_study(self):
        sdir = Qt.QFileDialog.getExistingDirectory(
            self, 'Open study directory', self.study_dir)
        if sdir is not None:
            self.study_dir = sdir
            self.init_study()

    def init_study(self):
        subjects = self.parse_subjects()
        self.sub_box.clear()
        for s in subjects:
            item = Qt.QListWidgetItem(s)
            item.setCheckState(Qt.Qt. Unchecked)
            self.sub_box.addItem(item)
        self.sub_box.setCurrentRow(0)

        sub = None
        if len(subjects) != 0:
            sub = subjects[0]
        zmaps = self.parse_zmaps(sub)
        self.zmap_box.clear()
        for c in zmaps:
            cn = c.split('.')[0]
            cn = cn.split('_zmap_')[1]
            item = Qt.QListWidgetItem(cn)
            item.setCheckState(Qt.Qt.Unchecked)
            self.zmap_box.addItem(item)

        contrasts = self.parse_contrasts(sub)
        self.ctr_box.clear()
        for c in contrasts:
            cn = c.split('.')[0]
            cn = cn.split('_zmap_')[1]
            item = Qt.QListWidgetItem(cn)
            item.setCheckState(Qt.Qt.Unchecked)
            self.ctr_box.addItem(item)

        sz = [self.sub_box.sizeHintForColumn(0),
              self.zmap_box.sizeHintForColumn(0),
              self.ctr_box.sizeHintForColumn(0)]
        sz.append(self.width() - sum(sz))
        self.splitter.setSizes(sz)

    def parse_subjects(self):
        subjects = glob.glob(osp.join(self.fmriprep_dir, 'sub-*'))
        subjects = sorted([osp.basename(s) for s in subjects if osp.isdir(s)])
        return subjects

    def parse_zmaps(self, sub):
        if not sub:
            return []
        zmaps = glob.glob(osp.join(self.fmri_anal_dir,
                                   f'{sub}/{sub}_zmap_*condition*.nii*'))
        zmaps = sorted([osp.basename(c) for c in zmaps
                        if '_smoothing-' not in c])
        return zmaps

    def parse_contrasts(self, sub):
        if not sub:
            return []
        zmaps = glob.glob(osp.join(self.fmri_anal_dir,
                                   f'{sub}/{sub}_zmap_*_contrast*.nii*'))
        zmaps = sorted([osp.basename(c) for c in zmaps
                        if '_smoothing-' not in c])
        return zmaps

    def selected_subjects(self):
        selected = [self.sub_box.item(i) for i in range(self.sub_box.count())]
        selected = [item.text() for item in selected
                    if item.checkState() == Qt.Qt.Checked]
        return selected

    def selected_zmaps(self):
        selected = [self.zmap_box.item(i)
                    for i in range(self.zmap_box.count())]
        selected = [item.text() for item in selected
                    if item.checkState() == Qt.Qt.Checked]
        return selected

    def selected_contrasts(self):
        selected = [self.ctr_box.item(i) for i in range(self.ctr_box.count())]
        selected = [item.text() for item in selected
                    if item.checkState() == Qt.Qt.Checked]
        return selected

    def sub_clicked(self):
        subjects = self.selected_subjects()
        contrasts = self.selected_contrasts()
        self.display_subjects(subjects, contrasts)

    def zmap_clicked(self):
        self.sub_clicked()

    def contrast_clicked(self):
        self.sub_clicked()

    def display_subjects(self, subjects, contrasts):
        print('subjects:', subjects)
        print('contrasts:', contrasts)
        views = {}
        for sub in list(self.disp_subjects.keys()):
            if sub not in subjects:
                self.close_sub_views(sub)
        for sub in subjects:
            if sub in self.disp_subjects:
                views[sub] = self.disp_subjects[sub]
            else:
                views[sub] = self.open_sub_views(sub)
                self.disp_subjects[sub] = views[sub]
            self.display_sub_data(sub)
        self.block.reorderViews(sum(views.values(), []))
        if len(subjects) == 1:
            self.block.setColumns(int(np.ceil(self.views_per_sub / 2)))
        else:
            self.block.setColumns(self.views_per_sub)

    def open_sub_views(self, sub):
        wins = []
        a = ana.Anatomist()
        wins.append(a.createWindow('Axial', no_decoration=True))
        wins.append(a.createWindow('Coronal', no_decoration=True))
        wins.append(a.createWindow('Sagittal', no_decoration=True))
        wins.append(a.createWindow('3D', no_decoration=True))
        wins.append(a.createWindow('ValuesPlot', no_decoration=True))
        wins.append(a.createWindow('Info', no_decoration=True))
        a.assignReferential(referential=a.mniTemplateRef, elements=wins)
        # force redrawing in MNI orientation
        # (there should be a better way to do so...)
        wins[0].muteAxial()
        wins[1].muteCoronal()
        wins[2].muteSagittal()
        # set a black background
        a.execute('WindowConfig', windows=wins[:4],
                  light={'background': [0., 0., 0., 1.]})
        return wins

    def close_sub_views(self, sub):
        views = self.disp_subjects.get(sub, [])
        if views:
            a = ana.Anatomist()
            a.execute('DeleteElement', elements=views)
            del views
            del self.disp_subjects[sub]
        if sub in self.sub_data:
            del self.sub_data[sub]

    def get_anat(self, sub):
        # look in fmriprep
        ses = 'ses-01'
        space = 'space-MNI152NLin2009cAsym_'
        anat = osp.join(
            self.fmriprep_dir,
            f'{sub}/{ses}/anat/{sub}_{ses}_{space}'
            'desc-preproc_T1w.nii.gz')
        if osp.exists(anat):
            return (anat, None)

        # look in morphologist
        if osp.exists(osp.join(self.morpho_dir, sub)):
            sesdir = glob.glob(osp.join(self.morpho_dir, sub, 'ses-*'))
            if sesdir:
                d = osp.join(sesdir[0], 'anat/t1mri')
                acqdir = None
                for p in os.listdir(d):
                    tacqdir = osp.join(d, p)
                    if os.path.isdir(tacqdir):
                        acqdir = tacqdir
                        break
                if acqdir:
                    anat = osp.join(acqdir, f'{sub[4:]}.nii.gz')
                    if osp.exists(anat):
                        trans = osp.join(
                            acqdir, 'registration',
                            f'RawT1-{sub[4:]}'
                            '_default_acquisition_TO_Talairach-MNI.trm')
                        if not osp.exists(trans):
                            trans = None
                        return (anat, trans)

        return (None, None)

    def get_zmap(self, sub, mapname):
        zmap = osp.join(
            self.fmri_anal_dir, f'{sub}/{sub}_zmap_{mapname}.nii.gz')
        if not osp.exists(zmap):
            return (None, None)
        return (zmap, None)

    def get_contrast(self, sub, contrast):
        cmap = osp.join(
            self.fmri_anal_dir, f'{sub}/{sub}_zmap_{contrast}.nii.gz')
        if not osp.exists(cmap):
            return (None, None)
        return (cmap, None)

    def get_meshes(self, sub):
        ses = 'ses-01'
        meshfilt = osp.join(
            self.fmriprep_dir,
            f'{sub}/{ses}/anat/{sub}_{ses}_hemi-?_midthickness.surf.gii')
        meshesf = sorted(glob.glob(meshfilt))
        if len(meshesf) == 0:
            return (None, None)
        #tr = meshesf[0] + '.trmhdr?index=0'
        tr = None
        # coords in midthickness.gii files are in scanner-based coordinates
        # but this scanner referential is not available in any transform.
        # We can get it either from the raw FS lh.white file header, or by
        # combining the MNI transform in
        # freesurfer/sub-*/mri/transformations/talairach.auto.xfm
        return (meshesf, tr)

    def display_sub_data(self, sub):
        '''
        Display subject data.
        Data are cached in memory so that unchecking / re-checking them does
        not reload everything from disk. As a drawback, there is no memory
        limit yet, and for large datasets the cache may grow too big.
        This could be improved, of course.
        '''
        print('display_sub_data', sub)
        sd = self.sub_data.setdefault(sub, {})
        if 'anat' not in sd:
            anat, trans_file = self.get_anat(sub)
            if anat:
                # print('load anat:', anat)
                oanat = self.load_data(anat, trans_file)
                if oanat:
                    sd['anat'] = oanat
                    # force palete min to 0 in case there are neg. values
                    oanat.setPalette(minVal=0, absoluteMode=True)
        self.display_zmaps(sub)
        self.display_contrasts(sub)
        self.display_wmesh(sub)

    def display_zmaps(self, sub):
        print('display_zmaps', sub)
        zmaps = self.selected_zmaps()
        sd = self.sub_data.setdefault(sub, {})
        cmaps = sd.get('zmaps', {})
        if zmaps and sorted(cmaps.keys()) == sorted(zmaps):
            print('no change in zmaps')
            return

        views = self.disp_subjects[sub]
        anat = sd.get('anat')
        a = ana.Anatomist()
        if 'zmaps_fusion' in sd:
            if views:
                a.removeObjects(objects=sd['zmaps_fusion'], windows=views)
            del sd['zmaps_fusion']
        cmaps = {k: v for k, v in cmaps.items() if k in zmaps}
        sd['zmaps'] = cmaps
        if 'zmap_labels' in sd:
            print('del zmap_labels')
            del sd['zmap_labels']
        ana.cpp.Referential.clearUnusedReferentials()
        for zmap in zmaps:
            if zmap not in cmaps:
                zmapf, trans = self.get_zmap(sub, zmap)
                ozmap = self.load_data(zmapf, trans)
                # print('load zmap:', zmap, ':', ozmap)
                if ozmap:
                    cmaps[zmap] = ozmap
        if len(cmaps) >= 2 and self.binarize_multi_z:
            if 'zmap_labels' not in sd:
                amaps = [a.toAimsObject(m) for m in cmaps.values()]
                labelmap = aims.Volume(amaps[0].getSize(), dtype='S32')
                labelmap.copyHeaderFrom(amaps[0].header())
                labelmap.fill(0)
                for i, m in enumerate(amaps):
                    bmap = m.np
                    labelmap.np[bmap <= -self.binarize_threshold] \
                        += -(3 ** i)
                    labelmap.np[bmap >= self.binarize_threshold] += 3 ** i
                    labelmap.header()['volumeInterpolation'] = 0
                    olabelmap = a.toAObject(labelmap)
                    olabelmap.releaseAppRef()
                    sd['zmap_labels'] = olabelmap
                    minVal = 0
                    maxVal = np.ceil((3 ** len(amaps)) / 2) - 1
                    cmaps = {'labels': olabelmap}
        else:
            minVal = 1.96  # p = 0.05
            maxVal = 7.
        if cmaps and views:
            zmaps = list(cmaps.values())
            a.setObjectPalette(objects=zmaps,
                               palette='sym_blue_yellow_red', minVal=minVal,
                               maxVal=maxVal, zeroCentered1=True,
                               absoluteMode=True)
            obj = []
            if anat is not None:
                obj.append(anat)
            obj += zmaps
            fusion = a.fusionObjects(obj, method='Fusion2DMethod')
            sd['zmaps_fusion'] = fusion
            t = 1
            if anat is not None:
                a.execute('TexturingParams', objects=[fusion], texture_index=1,
                          mode='linear_A_if_B_white', rate=0.)
                t += 1
            for t in range(t, len(zmaps) + t - 1):
                a.execute('TexturingParams', objects=[fusion], texture_index=t,
                          mode='geometric')
            a.addObjects(objects=fusion,
                         windows=[views[self.sv.axial_view],
                                  views[self.sv.coronal_view],
                                  views[self.sv.sagittal_view]])
            #a.addObjects(objects=zmaps,
                         #windows=[views[self.sv.info_view],
                                  #views[self.sv.values_view]])
        elif views and anat is not None:
            # show anat only
            a.addObjects(objects=anat,
                         windows=[views[self.sv.axial_view],
                                  views[self.sv.coronal_view],
                                  views[self.sv.sagittal_view]])

    def display_contrasts(self, sub):
        print('display_contrasts', sub)
        contrasts = self.selected_contrasts()
        sd = self.sub_data.setdefault(sub, {})
        views = self.disp_subjects[sub]
        a = ana.Anatomist()
        cmaps = sd.get('contrasts', {})
        cmaps = {k: v for k, v in cmaps.items() if k in contrasts}
        sd['contrasts'] = cmaps
        for contrast in contrasts:
            if contrast not in cmaps:
                contrastf, trans = self.get_contrast(sub, contrast)
                ocontrast = self.load_data(contrastf, trans)
                # print('load contrast:', contrast, ':', ocontrast)
                if ocontrast:
                    ocontrast.setName(contrast)
                    cmaps[contrast] = ocontrast
        if cmaps and views:
            contrasts = list(cmaps.values())
            a.addObjects(objects=contrasts,
                         windows=[views[self.sv.info_view],
                                  views[self.sv.values_view]])

    def display_wmesh(self, sub):
        '''
        Display white matter mesh, with Zmap (if any) as texture.
        The fusion (Fusion3D) is in "sphere" mode, which involves calculations
        which are not immediate, so this produces latencies.
        '''
        print('display meshes', sub)
        meshesf, trans = self.get_meshes(sub)
        if meshesf is None:
            return
        sd = self.sub_data.setdefault(sub, {})
        views = self.disp_subjects[sub]
        a = ana.Anatomist()
        mshs = sd.setdefault('meshes', {})
        ref_trans = None
        zmaps = sd.get('zmap_labels')
        if zmaps is None:
            zmaps = sd.get('zmaps')
            if zmaps:
                zmaps = zmaps[next(iter(zmaps))]
        zmaps_k = sorted(sd.get('zmaps', {}).keys())

        for meshf in meshesf:
            for side in ('L', 'R'):
                if f'-{side}_' in meshf:
                    if side not in mshs:
                        print('load mesh:', meshf)
                        omesh = self.load_data(meshf, trans)
                        if ref_trans is None:
                            # Freesurfer meshes referentials and
                            # transformations are a bit tricky to determine
                            mtrans = self.load_mesh_tranform(sub, meshf, omesh)
                            if mtrans is not None:
                                trm = list(mtrans.np[:3, 3]) \
                                    + list(mtrans.np[0, :3]) \
                                    + list(mtrans.np[1, :3]) \
                                    + list(mtrans.np[2, :3])
                                ref = a.createReferential()
                                a.execute('LoadTransformation', origin=ref,
                                          destination=a.mniTemplateRef,
                                          matrix=trm)
                                ref_trans = ref
                        if ref_trans is not None:
                            omesh.assignReferential(ref_trans)
                        omesh.setMaterial(front_face='counterclockwise')
                        if omesh:
                            mshs[side] = {'mesh': omesh}
                    if side in mshs:
                        if zmaps:
                            if 'fusion' not in mshs[side] \
                                    or mshs[side]['fusion'][1] != zmaps_k:
                                print('fusion zmaps:', sub, side, mshs)
                                omesh = mshs[side]['mesh']
                                print('build fusion3D')
                                mfusion = a.fusionObjects(
                                    [omesh, zmaps], method='Fusion3DMethod')
                                a.execute('Fusion3DParams', object=mfusion,
                                          method='sphere',
                                          submethod='mean_corrected',
                                          depth=2., step=1.)
                                mshs[side]['fusion'] = (mfusion, zmaps_k)
                            else:
                                print('no change in 3D fusion')
                        elif 'fusion' in mshs[side]:
                            del mshs[side]['fusion']
        print('meshes:', meshesf)
        if mshs and views:
            meshes = list(mshs.values())
            addmeshes = [m.get('fusion')[0] if 'fusion' in m else m['mesh']
                         for m in meshes]
            rmmeshes = [m.get('mesh') for m in meshes if 'fusion' in m]
            if rmmeshes:
                print('rm from view:', rmmeshes)
                a.removeObjects(objects=rmmeshes,
                                windows=[views[self.sv.td_view]])
            print('add in view:', addmeshes)
            a.addObjects(objects=addmeshes, windows=[views[self.sv.td_view]])
            print('add done.')

    def load_data(self, datafile, transfile=None):
        '''
        Load the given data file in Anatomist, and try to determine coordinates
        system and transformations.
        The load function is generic (can load meshes, images etc).
        '''
        a = ana.Anatomist()
        if datafile is None:
            return None
        data = a.loadObject(datafile)
        if data is None:
            return None
        trans = None
        if hasattr(data, 'attributed'):
            hdr = data.attributed()
            refuid = hdr.get('referential')
        else:
            hdr = None
            refuid = None
        if transfile is not None:
            trans = aims.read(transfile)
        elif hdr is not None:
            refs = hdr.get('referentials')
            if refs and aims.StandardReferentials.mniTemplateReferential() \
                    in refs:
                index = refs.index(
                    aims.StandardReferentials.mniTemplateReferential())
                transl = hdr.get('transformations')
                if transl is not None and len(transl) > index:
                    trans = aims.AffineTransformation3d(transl[index])
            if refs and 'Coordinates aligned to another file or to ' \
                    'anatomical truth' in refs:
                print('spm aligned ?')
                index = refs.index(
                    'Coordinates aligned to another file or to anatomical '
                    'truth')
                transl = hdr.get('transformations')
                if transl is not None and len(transl) > index:
                    trans = aims.AffineTransformation3d(transl[index])
        if trans is not None and refuid is None and hdr is None:
            refuid = trans.header().get('source_referential')
        if refuid is not None or trans is not None:
            ref = data.getReferential()
            if ref is None or ref.uuid() == a.centralRef.uuid():
                ref = a.createReferential()
                data.assignReferential(ref)
            if refuid is not None:
                ref.header()['uuid'] = refuid
        if trans is not None \
                and a.getTransformation(ref, a.mniTemplateRef) is None:
            trm = list(trans.np[:3, 3]) + list(trans.np[0, :3]) \
                + list(trans.np[1, :3]) + list(trans.np[2, :3])
            a.execute('LoadTransformation', origin=ref,
                      destination=a.mniTemplateRef,
                      matrix=trm)
        return data

    def load_mesh_tranform(self, sub, meshf, mesh):
        # coords in midthickness.gii files are in scanner-based coordinates
        # but this scanner referential is not available in any transform.
        # We can get it either from the raw FS lh.white file header, or by
        # combining the MNI transform in
        # freesurfer/sub-*/mri/transformations/talairach.auto.xfm
        #wm_to_mni = aims.AffineTransformation3d(
            #mesh.header()['transformations'][0])
        sb_to_mni = None
        xfmf = osp.join(
            self.fmriprep_dir,
            f'sourcedata/freesurfer/{sub}/mri/transforms/talairach.auto.xfm')
        # print('mesh transform:', xfmf, osp.exists(xfmf))
        if osp.exists(xfmf):
            sb_to_mni = aims.read(xfmf)
        return sb_to_mni
