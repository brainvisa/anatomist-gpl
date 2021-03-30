#!/usr/bin/env python

'''
Install a ROI navigation control in Anatomist with the following features:

* Linked cursor between windows with non-linear deformation fields: non-linear transformations can be loaded between referentials which are not linked via regulart affine transformations. Clicks coordinates are transformed and sent to other windows.

* ROI selection: selectionned objects (double-click) are handled by their name/label, then all objects with the same name/label are also selected in all views. Views are focused on the bounding box of the selected objects.

'''

import anatomist.direct.api as ana
from soma.qt_gui.qt_backend import Qt
from soma.singleton import Singleton
from soma import aims, aimsalgo
import sys
import time
import numpy as np
import yaml
import uuid
import os
import collections
import argparse

argv = sys.argv[:]
a = ana.Anatomist()
from simple_controls import Left3DControl


class TransformationChain3d(object):
    '''
    This fakes aims.TransformationChain3d which inherits Transformation3d,
    and is not part of pyaims bindings in aims 5.0.0
    '''
    def __init__(self, chain):
        self.chain = chain

    def transform(self, position):
        for trans in self.chain:
            position = trans.transform(position)
        return position


class VectorFieldTransforms(Singleton):
    '''
    Manage non-linear transformations, which are not part of Anatomist
    transformations graph.
    This class is a singleton (it has a single shared instance)

    We could also use the HBP web service instead of loading the full vector
    fields:

    https://hbp-spatial-backend.apps.hbp.eu/v1/transform-point?source_space=MNI%20152%20ICBM%202009c%20Nonlinear%20Asymmetric&target_space=Big%20Brain%20%28Histology%29&x=1&y=2&z=3

    see also:
    https://hbp-spatial-backend.apps.hbp.eu/swagger-ui#/api_v1/get_v1_transform_point
    '''

    def __singleton_init__(self):
        super(VectorFieldTransforms, self).__init__()
        self._transformations = {}
        self._refs_from_names = {}

    def add_transformation(self, source_ref, dest_ref, transform):
        '''
        Add (or register) the given transformation in the transformations
        graph.

        transform may be a filename, or a Transformation instance. a
        Transformation is supposed to be a non-linear FFD (Free Form
        Deformation), not a linear transformation. If transform is a string, it
        may be:
        - an empty string will be an identity transformation
        - a .trm file will be an affine transformation, and will be passed to
          the builtin Anatomist system
        - another file (.ima) will be a FFD transformation file and will be
          registered as its filename. Loading will happen only when the
          transformation is used, in get_transformation().
        '''
        if hasattr(source_ref, 'getInternalRep'):
            source_ref = source_ref.getInternalRep()
        if hasattr(dest_ref, 'getInternalRep'):
            dest_ref = dest_ref.getInternalRep()
        if isinstance(transform, str) and (transform.endswith('.trm')
                                           or transform == ''):
            # this transformation is affine: use the regular builtin system
            if transform == '':
                # An empty transformation file is identity.
                transform = [0, 0, 0,  1, 0, 0,  0, 1, 0,  0, 0, 1]
            a = ana.Anatomist()
            a.loadTransformation(transform, source_ref, dest_ref)
        else:
            # non-linear: use our new system
            self._transformations.setdefault(source_ref, {})[dest_ref] \
                = transform

    def remove_transformation(self, source_ref, dest_ref):
        '''
        Remove a non-linear transformation from the graph.
        '''
        if hasattr(source_ref, 'getInternalRep'):
            source_ref = source_ref.getInternalRep()
        if hasattr(dest_ref, 'getInternalRep'):
            dest_ref = dest_ref.getInternalRep()
        t1 = self._transformations.get(source_ref)
        if not t1:
            return
        if dest_ref in t1:
            del t1[dest_ref]
            if len(t1) == 0:
                del self._transformations[source_ref]

    def get_transformation(self, source_ref, dest_ref, allow_compose=False):
        '''
        Get the transformation between source_ref and des_ref. If it is not a
        registered transformation, return None.
        If allow_compose is True and the transformation is not found, then a
        transformations chain path is looked for. If a matching one is found,
        it is then registered in the graph to allow fast access later. The
        drawback of this register operation is that it cannot react to changes
        in the transformation chain (if a new transformation is added and could
        make a shorter path, it will not be taken into account).
        '''
        if hasattr(source_ref, 'getInternalRep'):
            source_ref = source_ref.getInternalRep()
        if hasattr(dest_ref, 'getInternalRep'):
            dest_ref = dest_ref.getInternalRep()

        trans = self._transformations.get(source_ref, {}).get(dest_ref)
        if isinstance(trans, str):
            # the transformation is a filename, load it
            # this is a lazy-load mechanism
            trans = self.load_transformation(trans, source_ref, dest_ref)

        if trans is None and allow_compose:
            chain = self.get_transform_chain(source_ref, dest_ref)
            if chain is not None:
                # print('transform chain:', [(t[1].uuid(), t[2].uuid())
                #                            for t in chain])
                chain = [self.load_transformation(t[0], t[1],t[2])
                        if isinstance(t[0], str) else t[0]
                        for t in chain]
                trans = TransformationChain3d(chain)
                if len(chain) != 0:
                    # register the composition in the graph
                    self.add_transformation(source_ref, dest_ref, trans)

        return trans

    def load_transformation(self, filename, source_ref=None, dest_ref=None):
        '''
        Load a non-linear (FFD) transformation from its filename, and registers
        it in the transformations graph. This is an internal method, called by
        get_transformation() when needed, because transformations don't need to
        be pre-loaded, but are loaded in a lazy way when they are used.
        Moreover this method doesn't handle "regular" affine transformations
        (.trm files) that are registered in the core Anatomist application.

        Users may use add_transformation()  or load_transformations_graph()
        instead.

        By now we only use the ".ima" (GIS format) for deformation fields
        because it can contain 3D vectors in each voxel. But we could easily
        extend it to NIFTIs with 5 dimensions.
        '''
        print('loading transformation', filename, '...')
        trans = aims.read(filename, dtype='FfdTransformation')
        if source_ref and dest_ref:
            self.add_transformation(source_ref, dest_ref, trans)
        return trans

    def get_transform_chain(self, from_space, to_space):
        '''
        Get transformations path. From Yann Leprince's code on:

        https://github.com/HumanBrainProject/hbp-spatial-backend/blob/fc79a6adc5d71fe6a02021f0d36698c5fde86b43/hbp_spatial_backend/transform_graph.py#L36
        '''
        all_refs = [r.getInternalRep() for r in a.getReferentials()]

        to_visit = collections.deque([from_space])
        visited = {from_space}
        back_pointers = {from_space: (None, None)}
        # Breadth-first search on the spaces to find the shortest path
        while True:
            try:
                space = to_visit.popleft()
            except IndexError:
                return None

            # TODO detect ambiguities (multiple same-length chains)
            if space == to_space:
                chain = []
                while back_pointers[space][0] is not None:
                    target_space = space
                    space, transform = back_pointers[space]
                    chain.append((transform, space, target_space))
                chain.reverse()
                return chain

            for target_space, transform \
                    in self._transformations.get(space, {}).items():
                if target_space not in visited:
                    visited.add(target_space)
                    to_visit.append(target_space)
                    back_pointers[target_space] = (space, transform)
            # add builtin transformations to the graph
            for target_space in all_refs:
                if target_space not in visited:
                    transform = a.getTransformation(space, target_space)
                    if transform is not None:
                        visited.add(target_space)
                        to_visit.append(target_space)
                        back_pointers[target_space] = (space, transform)

    def referential_from_id(self, ref_id):
        '''
        Internal method.
        '''
        if isinstance(ref_id, ana.cpp.Referential) \
                or (hasattr(ref_id, 'getInternalRep')
                    and isinstance(ref_id.getInternalRep(),
                                   ana.cpp.Referential)):
            return ref_id
        ref = self._refs_from_names.get(ref_id)
        if ref:
            return ref
        a = ana.Anatomist()
        # is ref_id an UUID ?
        try:
            u = uuid.UUID(ref_id)
            ref = ana.cpp.Referential.referentialOfUUID(ref_id)
            if not ref:
                ref = a.createReferential()
                ref.header()['uuid'] = ref_id
            else:
                ref = a.Referential(a, ref)
        except ValueError:
            # no, it's a name: try by name
            refs = [r for r in a.getReferentials()
                    if r.header().get('name ') == ref_id]
            if len(refs) != 0:
                ref = refs[0]
            else:
                ref = a.createReferential()
                ref.header()['name'] = ref_id
        self._refs_from_names[ref_id] = ref
        self._refs_from_names[ref.uuid()] = ref

        return ref

    def load_transformations_graph(self, gname):
        '''
        Load a full transformations graph from a .yaml file.

        The file is organized as a 2-level dictionary::

            {
                source_ref_id: {
                    dest_ref_id1: transformation_filename1,
                    dest_ref_id2: transformation_filename2,
                },
                ...
            }

        A referential ID is a string which may represent an UUID, or a name.

        A transformatioon filename may be an affine (.trm) or non-linear (.ima)
        transformation file, or an empty string to represent an identity
        transformation.
        '''
        print('load_transformations_graph', gname)
        if os.path.exists(gname):
            # gname is a yaml filename
            with open(gname) as f:
                graph = yaml.safe_load(f)
        else:
            # assume a string directly containing yaml
            graph = yaml.safe_load(gname)
        dirname = os.path.dirname(gname)
        # print(graph)
        for source_id, dest_def in graph.items():
            # print(source_id)
            source_ref = self.referential_from_id(source_id)
            for dest_id, trans in dest_def.items():
                dest_ref = self.referential_from_id(dest_id)
                print(dest_id, repr(trans), dest_ref.uuid())
                inv = False
                sr = source_ref
                if trans.startswith('inv:'):
                    inv = True
                    trans = trans[4:]
                    sr = dest_ref
                    dest_ref = source_ref
                if trans:
                    trans = os.path.join(dirname, trans)
                # print('add trans:', sr.refUuid, dest_ref.refUuid, trans)
                if trans.endswith('.trm') or trans == '':
                    # this transformation is affine: use the regular builtin
                    # system
                    if trans == '':
                        # An empty transformation file is identity.
                        trans = [0, 0, 0,  1, 0, 0,  0, 1, 0,  0, 0, 1]
                    a.loadTransformation(trans, sr, dest_ref)
                else:
                    # non-linear: use our new system
                    self.add_transformation(sr, dest_ref, trans)


class LinkROIAction(ana.cpp.ContinuousTrackball):
    '''
    Anatomist Action class, managing non-linear transformations in clicks,
    and selection by ROI names.
    Based on the existing ContinuousTrackball class, which manages 3D rotation
    using the mouse.
    '''

    def name(self):
        return 'LinkROIAction'

    def beginTrackball(self, x, y, gx, gy):
        # we just record initial mouse position and time
        super(LinkROIAction, self).beginTrackball(x, y, gx, gy)
        self.startx = x
        self.starty = y
        self.start_time = time.time()

    def endTrackball(self, x, y, gx, gy):
        super(LinkROIAction, self).endTrackball(x, y, gx, gy)
        if time.time() - self.start_time < 0.5:
            # single click when the mouse button is released less than 0.5s
            # after it is pressed.
            action = self.view().controlSwitch().getAction('LinkAction')
            if action is not None:
                # perform the default linked cursor action first.
                action.execLink(x, y, gx, gy)
            # then check for non-linear transformations
            self.transform_click(x, y)

    def transform_click(self, x, y):
        '''
        Transform the linked cursor position of the current view in other
        windows by non-linear transformations, if any are registered in the
        VectorFieldTransforms instance.
        Then the cursor position in such windows is updated accordingly.
        '''
        a = ana.Anatomist()
        w = self.view().aWindow()
        pos =  w.positionFromCursor(x, y)  # get 3D position
        if pos is None:
            return
        oref = w.getReferential()

        for win in a.getWindows():
            # discard a number of cases:
            # - don't transform in the same view
            # - don't try to transform non non-3D windows (browsers etc)
            # - if both referentials are the same, don't do anything
            # - if a regular transformation exists, don't do anything
            #   (this means that anatomist regular transformations have a
            #   higher priority than non-linear transformations, which
            #   can be discussed or changed)
            if win.getInternalRep() == w:
                continue
            if not isinstance(win.getInternalRep(), ana.cpp.AWindow3D):
                continue
            dref = win.getReferential().getInternalRep()
            if dref is oref:
                continue
            trans = a.getTransformation(oref, dref)
            if trans:
                continue  # already an affine transfo
            print('look for non-linear trans', oref.uuid(), 'to', dref.uuid())
            trans = VectorFieldTransforms().get_transformation(
                oref, dref, allow_compose=True)
            if not trans:
                continue
            # transform the cursor position (non-linearly)
            tpos = trans.transform(pos)
            print('transformed pos:', list(tpos))
            if np.all(np.logical_not(np.isnan(tpos[0]), np.isnan(tpos))):
                # if the transformed position is valid, move the target window
                # cursor to it
                win.setPosition(tpos, dref)

    def selection_changed(self):
        '''
        Callback handling a selection change in the current view. Here we
        handle it in a specific way:
        1. retreive the name/label of the selected objects (to represent a
           region name) - we could handle a label translation using a
           nomenclature, if needed
        2. get all objects with the same label in all windows
        3. select them all
        4. focus each view on its selected objects, with the camera orientation
           of the current view
        This achieves inter-view/subject/atlas correspondance by region.
        '''

        a = ana.Anatomist()
        action = self.view().controlSwitch().getAction('SelectionAction')
        if action is not None:
            # peform the regular selection action first
            action.selectionChanged()

        sf = ana.cpp.SelectFactory.factory()
        my_w = self.view().aWindow()
        group = my_w.Group()
        # get all selected objects in the window group
        sel = sf.selected().get(group, set())
        selected_names = set()
        my_objects = my_w.Objects()
        # get labels for all selected objects
        for obj in sel:
            if obj not in my_objects:
                continue
            name = self.get_roi_name(obj)
            if name:
                selected_names.add(name)

        # select objects with the same label in all windows
        to_select = {}
        for w in a.getWindows():
            ## do we skip the current view ? not really, we can select other
            ## objects with the same label here as well.
            #if w.getInternalRep() == self.view().aWindow():
                #continue
            if not isinstance(w.getInternalRep(), ana.cpp.AWindow3D):
                continue
            sobj = self.check_win_with_obj_names(w, selected_names)
            to_select.setdefault(w.Group(), set()).update(sobj)
            bbox = self.bounding_box(sobj, w.getReferential())
            self.focus_view(w, bbox)

        for g, o in to_select.items():
            sf.select(g, o)

    @staticmethod
    def get_roi_name(obj):
        '''
        Get a ROI name for the given object. If it is a graph vertex, then it
        may have an attribute "label" or "name" in it. Otherwise, the Anatomist
        object name will be used.

        TODO: handle the use of attribute "label" or "name" in graphs as global
        settings
        '''
        if hasattr(obj, 'attributed'):
            att = obj.attributed()
            label_attribute = 'label'
            if hasattr(obj, 'getInternalRep'):
                iobj = obj.getInternalRep()
            else:
                iobj = obj
            parents = iobj.parents()
            for parent in parents:
                pattributed = getattr(parent, 'attributed', None)
                if pattributed:
                    label_attribute = pattributed().get('label_property',
                                                        'label')
                    break
            name = att.get(label_attribute, '')
        else:
            name = obj.name
        return name

    @staticmethod
    def check_win_with_obj_names(w, selected_names):
        '''
        Get objects in the given view which ROI label matches amongst the given
        ones.
        '''
        to_sel = set()
        # getInternalRep() is important here since w.Objects() overrides
        # it and transforms compound objects into lists, which makes many many
        # of them and is very slow.
        todo = list(w.getInternalRep().Objects())
        count = 0
        while todo:
            obj = todo.pop(0)
            if isinstance(obj, list):
                todo += obj
                continue
            count += 1
            name = LinkROIAction.get_roi_name(obj)
            if name and name in selected_names:
                to_sel.add(obj)
        return to_sel

    @staticmethod
    def bounding_box(objects, wref):
        '''
        Merge bounding boxes of the given objects into the given coordinates
        system.
        '''
        a = ana.Anatomist()
        bbox = None
        for obj in objects:
            trans = a.getTransformation(obj.getReferential(), wref)
            o_box = obj.boundingbox()
            if trans:
                # Coordinate must be transformed to go to the target
                # referential
                o_box = trans.transformBoundingBox(*o_box)
            if not bbox:
                bbox = list(o_box)
            else:
                # merge bounding boxes from prevous objects
                bbox = (np.min((bbox[0], o_box[0]), axis=0),
                        np.max((bbox[1], o_box[1]), axis=0))
        return bbox

    def focus_view(self, win, bbox, margin=20):
        '''
        Focus the given window field of view on the given boundig box. It also
        propagates the current view orientation (quaternion) on 3D windows
        (not in 2D mode)
        '''
        if not bbox:
            return
        center = (np.array(bbox[0]) + np.array(bbox[1])) / 2
        kwargs = {}
        if win.type() == win.WINDOW_3D \
                and self.view().aWindow().type() == win.WINDOW_3D:
            # both views are 3D: propagate also camera orientation
            kwargs = {'view_quaternion': self.view().quaternion().vector()}

        win.camera(
            boundingbox_min=[float(x) for x in np.array(bbox[0]) - margin],
            boundingbox_max=[float(x) for x in np.array(bbox[1]) + margin],
            observer_position=[float(x) for x in center], **kwargs)


class LinkROIControl(Left3DControl):
    '''
    Control in Anatomist views which performs non-linear transformations and
    ROI selection.
    We use the existing Left3DControl as a basis to avoid having to plug every
    action again.
    '''

    def __init__(self,
                 name=Qt.QT_TRANSLATE_NOOP(
                 'ControlledWindow', 'LinkROIControl')):
        super(LinkROIControl, self).__init__(name)

    def eventAutoSubscription(self, pool):
        # call parent class method
        super(LinkROIAction, self).eventAutoSubscription(pool)
        # un-register the events we want to oveload: selection
        self.selectionChangedEventUnsubscribe()
        # then register our own action
        self.selectionChangedEventSubscribe(pool.action(
            'LinkROIAction').selection_changed)
        # same for left mouse button events
        self.mouseLongEventUnsubscribe(Qt.Qt.LeftButton, Qt.Qt.NoModifier)
        self.mouseLongEventSubscribe(
            Qt.Qt.LeftButton, Qt.Qt.NoModifier,
            pool.action('LinkROIAction').beginTrackball,
            pool.action('LinkROIAction').moveTrackball,
            pool.action('LinkROIAction').endTrackball, True )


def install_control():
    '''
    Register the new control/action in Anatomist
    '''
    icon = ana.cpp.IconDictionary.instance().getIconInstance('Selection 3D')
    ana.cpp.IconDictionary.instance().addIcon(
        'LinkROIControl', Qt.QPixmap(icon))
    ad = ana.cpp.ActionDictionary.instance()
    ad.addAction('LinkROIAction', LinkROIAction)
    cd = ana.cpp.ControlDictionary.instance()
    cd.addControl('LinkROIControl', LinkROIControl, 185)
    cm = ana.cpp.ControlManager.instance()
    cm.addControl('QAGLWidget3D', '', 'LinkROIControl')
    del icon


def help():
    return \
        '''Run Anatomist with a ROI navigation control with the following features:

* Linked cursor between windows with non-linear deformation fields: non-linear transformations can be loaded between referentials which are not linked via regulart affine transformations. Clicks coordinates are transformed and sent to other windows.

* ROI selection: selectionned objects (double-click) are handled by their name/label, then all objects with the same name/label are also selected in all views. Views are focused on the bounding box of the selected objects.

The specified objects are loaded at launch time, and any .yaml file is interpreted as a transformations graph.

Non-linear transformations (vector fields) between MNI152 2009c asymmetric, Colin27, BigBrain and an infant atlas templates can be downloaded from the Human Brain Project (HBP) knowledge graph:

https://search.kg.ebrains.eu/instances/Dataset/7a9aa738-a5b2-4601-818e-05db2627ba5c

A transformations graph (graph.yaml) is also found in this dataset and may be passed to this program.

The corresponding atlases templates can be downloaded using the links there. However to work correctly the template images have to be marked with the correct referentials IDs. The ICBM152 template is already marked, but others must be added a .minf file (text file):
- for Colin27: create colin27_t1_tal_lin.nii.minf:

    attributes = {
        "referentials": ["MNI Colin 27"],
    }

- for the BigBrain, the referential is "Big Brain (Histology)"
- for the infants template the referential is "Infant atlas"
'''


def main(argv=sys.argv):

    parser = argparse.ArgumentParser(argv[0], description=help())
    parser.add_argument(
        '-s', '--split', action='store_true',
        help='use separate windows (default: use a views block)')
    parser.add_argument('object_file', nargs='*',
                        help='Load objects or transformation graph (.yaml)')

    options = parser.parse_args(argv[1:])

    to_load = options.object_file
    use_block = not options.split

    install_control()

    # maintain a gloabl list of windows, objects and referentials to keep them
    # alive (otherwise reference counting will destroy them)
    windows = []
    objects = []
    refs = []

    # load the sulci nomenclature and colors set
    sulci_nomenclature = a.loadObject(
        aims.carto.Paths.findResourceFile(
            'nomenclature/hierarchy/sulcal_root_colors.hie'))
    objects.append(sulci_nomenclature)

    # Yaml files are supposed to be transform graphs
    trans_graphs = [f for f in to_load
                    if f.endswith('.yaml') or f.endswith('.yml')]
    # the rest is objects to visualize
    to_load = [f for f in to_load if f not in trans_graphs]

    # we instantiate a non-linear vector fields transformations graph
    vt = VectorFieldTransforms()
    for gname in trans_graphs:
        vt.load_transformations_graph(gname)
    # add a transformation link with Anatomist internals
    # in order to identify the internal MNI and the ICBM 2009c referentials
    vt.load_transformations_graph(
        'MNI 152 ICBM 2009c Nonlinear Asymmetric:\n'
        '  803552a6-ac4d-491d-99f5-b938392b674b: ""')

    # load all given objects, and open a new view for each one
    block = None
    for objname in to_load:
        o = a.loadObject(objname)
        if o:
            # extract referential / transformatin information if available
            o.applyBuiltinReferential()
            r = o.getReferential()
            if not r or r.refUuid == a.centralReferential().refUuid:
                # individualize referential for each object
                r = a.createReferential()
                refs.append(r)
                o.assignReferential(r)
            objects.append(o)
            if not block and use_block:
                # the block is a Qt window which will contain all views in a
                # grid layout. If no block is used each view will be a separate
                # window.
                block = a.createWindowsBlock()
            wtype = '3D'
            if isinstance(o.getInternalRep(), ana.cpp.SliceableObject):
                # for volumes or other voxel-based objects we use the view in
                # "slice" mode
                wtype = 'Axial'
            w = a.createWindow(wtype, block=block)
            windows.append(w)
            # put the loaded object in its view
            w.addObjects(o)
            # force the new control in this new view
            w.setControl('LinkROIControl')

    if 'IPython' not in sys.modules:
        Qt.QApplication.instance().exec_()

    return objects, block, windows, refs


if __name__ == '__main__':
    things_to_keep = main(argv)

