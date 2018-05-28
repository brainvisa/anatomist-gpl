How to
======

Use / change Anatomist settings
-------------------------------

>>> import anatomist.direct.api as ana
>>> a = ana.Anatomist()
>>> print a.config()['windowSizeFactor']
2.0
>>> a.config()['windowSizeFactor'] = 1.
>>> print a.config()['windowSizeFactor']
1.0

Configuration options are those recognized in the configuration file.
It is documented :anausr:`here <config_file.html>`.


.. _apply_transformations:

Apply transformations to objects
--------------------------------

When transformations information is present in the object header (such as NIFTI volume)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This is a way of scripting the problem of objects appearing misaligned as described in :anausr:`this FAQ topic <faq.html#two-volumes-are-registered-in-spm-but-do-not-appear-matched-in-anatomist>`

To do the same as the GUI option "referential / load information from file header":

>>> import anatomist.api as ana
>>> a = ana.Anatomist()
>>> vol1 = a.loadObject('volume1.nii')
>>> vol2 = a.loadObject('volume2.nii')
>>> a.execute('LoadReferentialFromHeader', objects=[vol1, vol2])

see :anadev:`The LoadReferentialFromHeader command doc <commands.html#loadreferentialfromheader>`. Note that ``vol1`` and ``vol2`` do not need to live in the same coordinates system.

To get referentials linked to both volumes and set a, identity transformation between them, we need the **direct** mode API. The most difficult part of the job is to retreive the correct end-point referential from the correct transformation:

>>> all_trans = a.getTransformations()
>>> trans_from_vols = []
>>> for vol in (vol1, vol2):
>>>     trans_from_vol = [t for t in all_trans
>>>                       if t.source() == vol.referential
>>>                         and not t.isGenerated()]
>>>     # hope trans_from_vol1 contains just one transform
>>>     # but if there are several, try to select the one going to
>>>     # scanner-based
>>>     if len(trans_from_vol) > 1:
>>>         trans_from_vol_filt = [
>>>             t for t in trans_from_vol
>>>                 if t.destination().header()['name'].startswith(
>>>                     'Scanner-based anatomical coordinates')]
>>>         if len(trans_from_vol_filt) == 1:
>>>             trans_from_vol = trans_from_vol_filt
>>>     if len(trans_from_vol) != 1
>>>         raise RuntimeError('could not find a non-ambiguous transform')
>>>     trans_from_vols.append(trans_from_vol)
>>> # now we have the transforms.
>>> # load identity between them
>>> trans_from_vol1, trans_from_vol2 = trans_from_vols
>>> a.execute('LoadTransformation', origin=trans_from_vol1.destintation(),
>>>           destination=trans_from_vol2.destination(),
>>>           matrix=[0, 0, 0, 1, 0, 0,  0, 1, 0,  0, 0, 1])

see :anadev:`The LoadTransformation command doc <commands.html#loadtransformation>`.

To assign other objects (meshes...) the same referential as the above volumes:

>>> mesh = a.loadObject('mesh.gii')
>>> mesh.assignRefetential(vol1.referential)


When transformations are external, in ``.trm`` files
++++++++++++++++++++++++++++++++++++++++++++++++++++

>>> import anatomist.api as ana
>>> a = ana.Anatomist()
>>> vol1 = a.loadObject('volume1.nii')
>>> vol2 = a.loadObject('volume2.nii')
>>> ref1 = a.createReferential()
>>> ref2 = a.createReferential()
>>> vol1.assignReferential(ref1)
>>> vol2.assignReferential(ref2)
>>> tr = a.loadTransformation(ref1, ref2, 'transform.trm')


Use Anatomist to perform off-screen rendering and snapshots
-----------------------------------------------------------

This mode needs Framebuffer rendering support in the OpenGL implementation, and on Linux a X server connection is still required. You may use a virtual X server, like **Xvfb**, or use the HeadlessAnatomist class (see below).

With access to a X server
+++++++++++++++++++++++++

>>> import anatomist.api as ana
>>> a = ana.Anatomist('-b')
>>> mesh = a.loadObject('subject01_Lhemi.mesh')
>>> w = a.createWindow('3D', options={'hidden': True})
>>> w.addObjects(mesh)
>>> w.snapshot('snapshot.jpg', width=3000, height=2500)


Headless Anatomist mode
+++++++++++++++++++++++

HeadlessAnatomist is using Xvfb under the hood, so it should be installed and working. It should also support the GLX protocol, which, with some 3D drivers/OpenGL (nvidia linux driver for instance) will need `VirtualGL <http://www.virtualgl.org>`_ in addition.

>>> import anatomist.headless as hana
>>> a = hana.HeadlessAnatomist()
>>> mesh = a.loadObject('subject01_Lhemi.mesh')
>>> w = a.createWindow('3D')
>>> w.addObjects(mesh)
>>> w.snapshot('snapshot.jpg', width=3000, height=2500)

To use VirtualGL, the *anatomist* process must be run through ``vglrun``:

.. code-block:: bash

    vglrun anatomist_script.py

or:

.. code-block:: bash

    vglrun ipython

then use HeadlessAnatomist in the anatomist script.

