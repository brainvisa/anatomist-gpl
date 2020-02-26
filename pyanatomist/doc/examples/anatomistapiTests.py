#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
"""
Anatomist api tests
===================

This example uses data of i2bm platform.
"""
from __future__ import print_function
from __future__ import absolute_import
import os
import sys
import soma.config
import numpy as np
import tempfile


data_directory = os.path.join(
    os.environ.get("BRAINVISA_TEST_RUN_DATA_DIR", ""),
    "tmp_tests_brainvisa/data_for_anatomist")


failures = []
mode = 'direct mode'


def testDirectImpl(interactive=True):
    import anatomist.direct.api as pyanatomist
    global mode
    mode = 'direct mode'
    a = pyanatomist.Anatomist()
    return testAnatomist(a, interactive)


def testSocketImpl(interactive=True):
    # test socket impl, not threaded
    import anatomist.socket.api as pyanatomist
    global mode
    mode = 'socket mode'
    a = pyanatomist.Anatomist()
    return testAnatomist(a, interactive)


def test_assert(condition, message):
    try:
        assert(condition)
    except AssertionError:
        global failures
        failures.append('%s: %s' % (mode, message))
        print('** error: %s: %s **' % (mode, message))


def testAnatomist(a, interactive=True):
    print("\n--- CreateWindowsBlock ---")
    block = a.createWindowsBlock(3)  # a block of windows with 3 columns
    # in direct api the block object is really created only when the first
    # window is added to it
    print("block.internalRep = ", block.internalRep, ", block.nbCols = ",
          block.nbCols)
    test_assert(block.internalRep not in (None, 0), "block is invalid")

    print("\n--- CreateWindow ---")
    w1 = a.createWindow(wintype='Axial', block=block)
    print("w1 : Axial window, added to the block. w1 = ", w1,
          ", block.internalRep = ", block.internalRep)
    test_assert(w1 is not None, 'window w1 is None')
    test_assert(w1.block == block, 'block in w1 is wrong')

    w2 = a.createWindow(wintype='Sagittal', geometry=[10, 20, 200, 500],
                        block=block)
    test_assert(w2 is not None, 'window w2 is None')
    print(
        "w2 : Sagittal window, added to the block. The geometry attribute is not taken into account because of the block, the window is resized to fit into the block.")
    w3 = a.createWindow(wintype='Coronal', block=block, no_decoration=True)
    print(
        "w3 : Coronal window, added to the block (3rd column), thanks to the attribute no decoration, the window has no menus, buttons and so on...")
    test_assert(w3 is not None, 'window w3 is None')
    w4 = a.createWindow(wintype='3D', geometry=[10, 20, 200, 500])
    print("w4 : 3D window, not in the block, with geometry attribute.")
    test_assert(w4 is not None, 'window w4 is None')
    w5 = a.createWindow(wintype='3D', no_decoration=True)
    print("w5 : 3D window, not in the block, with no decoration.")
    test_assert(w5 is not None, 'window w5 is None')

    print("\n--- LoadObject ---")
    o = a.loadObject(os.path.join(data_directory,
                                  "subject01/subject01_Lwhite.mesh"), "objetO")
    test_assert(o is not None, 'object o is None')
    print("o : mesh Lhemi.mesh, renamed objecO, internalRep = ", o,
          ", o.__class__ = ", o.__class__)
    o2 = a.loadObject(os.path.join(data_directory,
                                   "subject01/subject01_Lwhite_curv.tex"),
                      "objetO2")
    test_assert(o2 is not None, 'object o2 is None')
    print("o2 : texture Lwhite_curv.tex, renamed objetO2, internalRep = ", o2)
    o4 = a.loadObject(os.path.join(data_directory,
                                   "roi/basal_ganglia.hie"))
    test_assert(o4 is not None, 'object o4 is None')
    print("o4 : nomenclature basal_ganglia.hie, internalRep = ", o4)
    o3 = a.loadObject(os.path.join(data_directory,
                                   "roi/basal_ganglia.arg"))
    test_assert(o3 is not None, 'object o3 is None')
    print("o3 : graph basal_ganglia.arg, internalRep = ", o3)
    # this should fail
    print(
        'o5 : trying to load an object with wrong type (field restrict_object_type doesn\'t match the type of the object): it should fail.')
    o5 = a.loadObject(filename=os.path.join(data_directory,
                                            "subject01/subject01.nii"),
                      restrict_object_types={'Volume': ['FLOAT']})
    # test_assert(o5 is None, 'object o5 is not None')
    print('The error message is normal, o5 = ', o5)
    o6 = a.loadObject(filename=os.path.join(data_directory,
                                            "subject01/subject01.nii"),
                      restrict_object_types={'Volume': ['S16', 'FLOAT']})
    test_assert(o6 is not None, 'object o6 is None')
    print(
        "o6 : volume subject01.ima, restrict_object_type match the object type. internalRep = ", o6)
    o7 = a.loadObject(
        filename=os.path.join(data_directory, "subject01/subject01.nii"))
    test_assert(o7 is not None, 'object o7 is None')
    print("o7 : same object")
    cur = a.loadCursor(os.path.join(data_directory,
                                    "subject01/subject01_Lhemi.mesh"))
    test_assert(cur is not None, 'object cur is None')
    print(
        "cur : load Lhemi.mesh as a cursor. The object is not in the list of objects in Anatomist main window but can be selected as cursor in preferences. ")
    test_assert(cur not in a.getObjects(),
                'object cur is in Anatomist global list')

    print("\n--- FusionObjects ---")
    fus = a.fusionObjects([o, o2], "FusionTexSurfMethod", interactive)
    test_assert(fus is not None, 'fusion fus is None')
    print(
        "fus : fusion of o and o2, method is FusionTexSurfMethod and askOrder is True, so a window opens to let the user choose the order of the objects in the fusion. internalRep = ", fus)

    print("\n--- CreateReferential ---")
    r = a.createReferential(os.path.join(
        soma.config.BRAINVISA_SHARE,
        "registration/Talairach-MNI_template-SPM.referential"))
    test_assert(r is not None, 'referential r is None')
    print(
        "r : Referential loaded from the Talairach-MNI_template-SPM.referential. r.__class__ = ", r.__class__, ", internalRep = ", r, ", r.refUuid = ",
          r.refUuid, ". This should not create a new referential because Talairach-MNI_template-SPM referential is already loaded in Anatomist. ")
    test_assert(r == a.mniTemplateRef,
                'referenrial r is not the MNI referential')
    r2 = a.createReferential()
    test_assert(r2 is not None, 'referential r2 is None')
    print("r2 : new referential. internalRep = ", r2, ", refUuid = ",
          r2.refUuid)
    cr = a.centralRef
    test_assert(cr is not None, 'central ref is None')
    print("cr : central referential, ", cr, ", refUuid = ", cr.refUuid,
          ". This referential is already loaded in Anatomist.")

    print("\n--- LoadTransformation ---")
    t = a.loadTransformation(os.path.join(
        data_directory,
        "subject01/RawT1-subject01_default_acquisition_TO_Talairach-ACPC.trm"),
        r2, cr)
    test_assert(t is not None, 'transformation t is None')
    print(
        "t : loaded from the file chaos_TO_talairach.trm, as a transformation between r2 and cr. t.__class__ = ",
          t.__class__, ", internalRep = ", t)

    print("\n--- CreatePalette ---")
    p = a.createPalette("maPalette")
    test_assert(p is not None, 'palette p is None')
    print(
        "p : new palette named maPalette, added Anatomist list of palettes. p.__class__ = ",
          p.__class__, ", internalRep = ", p)

    print("\n--- GroupObjects ---")
    g = a.groupObjects([o, o2])
    test_assert(g is not None, 'group g is None')
    print("g : new group of objects containing o and o2. g.__class__ = ",
          g.__class__, ", internalRep = ", g)
    test_assert(o in g.children and o2 in g.children,
                'objects o or o2 are not children of group g')

    print("\n--- linkWindows ---")
    wg = a.linkWindows([w1, w2])
    test_assert(wg is not None, 'window group wg is None')
    print("wg : new group of windows containing w1 and w2. wg.__class__ = ",
          wg.__class__, ", internalRep = ", wg)

    print("\n--- GetInfos ---")
    lo = a.getObjects()
    test_assert(lo is not None, 'objects list lo is None')
    print("\nObjects refererenced in current context : ", lo)
    print("Total : ", len(lo))
    nio = 79
    if mode == "direct mode":
        no = 79
        nt = 6
        nr = 3
    else:
        no = 9
        nt = 1
        # in socket mode r has a different ID as mniTemplateRef, but the same
        # UUID, and it points to the same object in Anatomist. But we now
        # see 4 refs from the client.
        nr = 4
    test_assert(len(lo) == no, 'wrong number of objects')
    lio = a.importObjects(False)  # top_level_only = False -> all objects
    test_assert(lio is not None, 'objects list lio is None')
    print(
        "All objects (importing those that were not referenced in current context) : ", lio)
    print("Total : ", len(lio))
    print("-> Should be the same in direct implementation.")
    test_assert(len(lio) == 79, 'wrong total number of objects')

    lw = a.getWindows()
    test_assert(lw is not None, 'windows list lw is None')
    liw = a.importWindows()
    test_assert(liw is not None, 'windows list liw is None')
    print("\nGetWindows : ", len(lw), ", ImportWindows : ", len(liw))
    print(liw)
    test_assert(len(liw) == 5, 'wrong number of windows')

    print("\nPalettes : ", a.getPalettes())
    test_assert(len(a.getPalettes()) > 50, 'too few palettes')

    lr = a.getReferentials()
    test_assert(lr is not None, 'referentials list lr is None')
    lir = a.importReferentials()
    test_assert(lir is not None, 'referentials list lir is None')
    print("\ngetReferentials : ", len(lr), ", importReferentials : ",
          len(lir))
    print(lir)
    test_assert(len(lr) == nr, 'wrong referentials number: %d instead of %d'
                % (len(lr), nr))
    test_assert(len(lir) == nr,
                'wrong imported referentials number: %d instead of %d'
                % (len(lir), nr))

    lt = a.getTransformations()
    test_assert(lt is not None, 'transformations list lt is None')
    lit = a.importTransformations()
    test_assert(lit is not None, 'transformations list lit is None')
    print("\ngetTransformations : ", len(lt), ", importTransformations : ",
          len(lit))
    test_assert(len(lt) == nt,
                'wrong number of transformations: %d instead od %d'
                % (len(lt), nt))
    test_assert(len(lit) == 6,
                'wrong number of imported transformations: %d instead of 6'
                % len(lt))

    sel = a.getSelection()
    test_assert(sel is not None, 'selection sel is None')
    print("\nSelections in default group", sel)
    test_assert(len(sel) == 0, 'some objects are already selected')

    print("\nCursor last pos", a.linkCursorLastClickedPosition())
    print("Cursor last pos dans ref r2", a.linkCursorLastClickedPosition(r2))

    print("\n--- AddObjects ---")
    a.addObjects([fus], [w1, w2, w3])
    print("Object fus added in windows w1, w2, and w3.")
    test_assert(w1.objects == [fus], 'wrong objects in window w1')

    print("\n--- RemoveObjects ---")
    a.removeObjects([fus], [w2, w1])
    print("Object fus removed from window w1 and w2.")
    test_assert(len(w1.objects) == 0,
                'objects still in window w1')

    print("\n--- DeleteObjects ---")
    # delete the list of objects to avoid keeping a reference on object that
    # prevent from deleting it
    del lo
    del lio
    a.deleteObjects([o7])
    print("Delete object o7.")
    test_assert(len(a.getObjects()) == nio - 1,
                'wrong objects number after deletion of o7: %d instead of %d'
                % (len(a.getObjects()), nio - 1))

    print("\n--- AssignReferential ---")
    a.assignReferential(r, [o2, w2])
    print("Referential r assigned to object o2 and window w2.")
    test_assert(w2.getReferential() == r, 'wrong referential in window w2')
    test_assert(o2.referential is not None, 'No referential in object o6')
    test_assert(o2.referential is not None and o2.referential == r,
                'wrong referential in object o2: %s' % repr(o6.referential))
    o6.assignReferential(r)
    print(
        "Referential r assigned to object o6. Should not have worked because o6 already has a transform to the MNI ref.")
    test_assert(o6.referential is None or o6.referential != r,
                'o6 referential has actually changed to r (wrong)')

    print("\n--- camera ---")
    a.camera([w3], zoom=1.5)
    print("Set zoom to 1.5 in window w3.")

    print("\n--- closeWindows ---")
    # delete lists of windows to avoid keeping a reference that prevent from
    # closing the window.
    del lw
    del liw
    a.closeWindows([w4])
    print("Close window w4.")
    test_assert(len(a.getWindows()) == 4,
                'wrong number of windows after deletion of w4: %d'
                % len(a.getWindows()))

    print("\n--- setMaterial ---")
    o.addInWindows([w1])
    mat = a.Material(diffuse=[0.5, 0.1, 0.1, 1], smooth_shading=1)
    a.setMaterial([o], mat)
    print("Add object o to the window w1 and change its material : ",
          o.material)
    test_assert(w1.objects == [o], 'wrong objects in w1')
    test_assert(np.sum((np.array(o.getInfos()['material']['diffuse']) -
                        [0.5, 0.1, 0.1, 1]) ** 2) <= 1e-10,
                'Material on o has not been updated correctly: %s'
                % repr(o.getInfos()['material']['diffuse']))

    print("\n--- setObjectPalette ---")
    pal = a.getPalette("Blue-Red")
    w6 = a.createWindow('Axial')
    o6.addInWindows([w6])
    a.setObjectPalette([o6], pal, minVal=0, maxVal=0.2)
    print(
        "Put object o6 in a new Axial window w6 and change its palette to Blue-Red with min and max values to 0 and 0.2")
    test_assert(o6.getInfos()['palette']['palette'] == 'Blue-Red',
                'Palette on o6 has not been set to "Blue-Red"')

    print("\n--- setGraphParams ---")
    a.setGraphParams(display_mode="mesh")
    print("Set display mode (paint mode of objects in graph nodes) to mesh.")

    print("\n--- AObject Methods---")
    w7 = a.createWindow('3D')
    o3.addInWindows([w7])
    print("Put object o3 in new 3D window (w7). o3 attributes : filename : ",
          o3.filename, ", material : ", o3.material, "objectType : ",
          o3.objectType, ", children : ", o3.children)

    o.addInWindows([w6])
    o.removeFromWindows([w6])
    print("\nAdd and remove object o from window w6.")
    print(
        "Try to delete o2. Should fail because the object is used in a fusion:")
    o2.delete()

    # Some methods are available in Anatomist class and Objects classes
    # Anatomist.assignReferential -> AObject.assignReferential
    # Anatomist.setMaterial -> AObject.setMaterial
    # Anatomist.setObjectPalette -> AObject.setPalette
    o4.assignReferential(r)
    fus.setMaterial(mat)
    o.setPalette(pal)

    tex = fus.extractTexture()
    test_assert(tex is not None, 'extracted texture is None')
    print("\nExtract texture from object fus :", tex)
    tex = fus.generateTexture()
    test_assert(tex is not None, 'generated texture is None')
    print("Generate a texture: tex =", tex)
    fus2 = a.fusionObjects([o, tex], method="FusionTexSurfMethod")
    fus2.addInWindows([w5])
    print("Fusion the generated texture with object o : fus2 = ", fus2)
    tmp_file = tempfile.mkstemp(suffix='.gii')
    os.close(tmp_file[0])
    fus.exportTexture(tmp_file[1])
    a.sync()  # wait for save operation to complete
    test_assert(os.path.getsize(tmp_file[1]) != 0,
                'saved texture file is empty')
    print("fus texture is saved in file %s." % tmp_file[1])
    tex = a.loadObject(tmp_file[1])
    test_assert(tex is not None, 'could not re-read saved texture')
    test_assert(tex.objectType == 'TEXTURE',
                'loaded texture is not a texture...')
    os.unlink(tmp_file[1])
    os.unlink(tmp_file[1] + '.minf')
    tmp_file = tempfile.mkstemp(suffix='.gii')
    os.close(tmp_file[0])
    o.save(tmp_file[1])
    print("The object o is saved in the file %s." % tmp_file[1])
    a.sync()  # wait for save operation to complete
    test_assert(os.path.getsize(tmp_file[1]) != 0, 'saved mesh file is empty')
    mesh = a.loadObject(tmp_file[1])
    test_assert(mesh is not None, 'could not re-read saved mesh')
    test_assert(mesh.objectType == 'SURFACE', 'loaded mesh is not a mesh...')
    os.unlink(tmp_file[1])
    os.unlink(tmp_file[1] + '.minf')

    print("\n--- AWindow Methods---")
    print(
        "Window attributes: w2.windowType = ", w2.windowType, ", w2.group = ",
          w2.group)
    test_assert(w2.windowType == 'Sagittal', 'w2 type is not Sagittal')
    test_assert(w2.group == wg, 'w2 group is not wg')
    # Some methods available in Anatomist class are also available directly in
    # AWindows class.
    w2.addObjects([o])
    w2.removeObjects([o])
    w2.camera(2)
    w2.assignReferential(cr)
    w2.addObjects([fus])
    w2.moveLinkedCursor([150, 100, 60])
    w6.showToolbox()
                   # opens the toolbox window. This toolbox will be empty if
                   # the window is empty. If there is an object on which it is
                   # possible to draw a roi, the roi toolbox will be shown.

    print("\n--- AWindowsGroup Methods---")
    wg.setSelection([fus])
    print("Set fus object as selected in the group of windows wg : ")
    print("-> selection in default group has not changed :", a.getSelection())
    print("-> selection in the group of window wg :", a.getSelection(wg))
    wg.unSelect([fus])
    print("After unselect, selection in wg :", a.getSelection(wg))

    g0 = a.getDefaultWindowsGroup()  # the default group has the id 0
    g0.setSelectionByNomenclature(o4, ['Caude_droit'])
    print("Selection by nomenclature in default group - add 'Caude_droit':",
          g0.getSelection())
    g0.addToSelectionByNomenclature(o4, ['Caude_gauche'])
    print("Selection by nomenclature  default group - add 'Caude_gauche' :",
          g0.getSelection())
    g0.toggleSelectionByNomenclature(o4, ['Caude_gauche'])
    print(
        "Toggle selection by nomenclature in default group - toggle 'Caude_gauche' : ",
          g0.getSelection())

    print("\n--- APalette Methods---")
    # set colors take as parameter a list of RGB components for colors :
    # [r1,g1,b1,r2,g2,b2...]
    p.setColors(colors=[100, 0, 0] * 20 + [0, 100, 0] * 20 + [0, 0, 100] * 20)
    print("The colors of palette 'maPalette' has changed.")

    print("\n--- ATransformation Methods---")
    tmp_file = tempfile.mkstemp(suffix='.trm')
    os.close(tmp_file[0])
    t.save(tmp_file[1])
    a.sync()  # wait for save operation to complete
    print("Save the transformation t in file %s." % tmp_file[1])
    test_assert(os.path.getsize(tmp_file[1]) != 0,
                'saved transformation file is empty')
    os.unlink(tmp_file[1])
    os.unlink(tmp_file[1] + '.minf')

    # return objects and windows to keep a reference on them and avoid their
    # destroying.
    objects = a.getObjects()
    windows = a.getWindows()
    return (objects, windows)


def testBase():
    # base module : simple interface, methods are not implemented
    import anatomist.base as pyanatomist
    a = pyanatomist.Anatomist()
    w = a.createWindow('Axial')
    print(w)


interactive = True
if len(sys.argv) >= 2 and "-b" in sys.argv[1:] or "--batch" in sys.argv[1:] \
        or 'sphinx_gallery' in sys.modules:
    interactive = False

print("\n****  TEST ANATOMIST API DIRECT IMPLEMENTATION ****\n")
res1 = testDirectImpl(interactive)
if not interactive:
    del res1
print("\n****  TEST ANATOMIST API SOCKET IMPLEMENTATION ****\n")
res2 = testSocketImpl(interactive)
if not interactive:
    del res2


if len(failures) != 0:
    print('\n\n** tests have failed: **')
    print('\n'.join(failures))
    print()
    raise RuntimeError('tests have failed:')

else:
    print('\nTests OK.')
