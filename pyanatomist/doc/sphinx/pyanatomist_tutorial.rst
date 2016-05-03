
PyAnatomist tutorial
====================

.. default-domain:: py

.. currentmodule:: anatomist.base

Programming with Anatomist in Python language
---------------------------------------------

Anatomist is written in C++ language but has also a python API: **PyAnatomist**. This python API enables to drive Anatomist application through python scripts : using Anatomist, loading volumes, meshes, graphs, viewing them in windows, merging objects, changing color palettes, etc... It can be useful in order to automate a repetitive visualization task or to add features to Anatomist application by developping a python plugin, which is much more easier than developping directly in Anatomist C++ library. Actually, several features in Anatomist have been added via a python plugin like the gradient palette for example. The python API is also used by several viewers in BrainVISA.

Depending how the C++/Python bindings are compiled, the tutorial may work using python2 or python3, or both.


Description of the API
----------------------

The main entry point is the :class:`Anatomist` class which must be instantiated before any operation can be performed. It represents Anatomist application. This class contains a number of nested classes: :class:`~Anatomist.AObject`, :class:`~Anatomist.AWindow`... that represent the elements of Anatomist application.

The entry point of this API is the module **anatomist.api**, you can import it as below:

::

    import anatomist.api as anatomist

And then create an instance of Anatomist:

::

    a = anatomist.Anatomist()

So you can send commands to Anatomist application, for example creating a window:

::

    window = a.createWindow('3D')


Implementation
--------------

Several means of driving Anatomist in python scripts exist :

* **Python bindings for the C++ library** (SIP bindings). In this mode, all bound features are available. You handle directly the Anatomist objects. But Anatomist is loaded directly in your python program, it is not an independent program in this mode. So the errors that occur in Anatomist are reported in the python script.
* **Sending commands via a network socket**. Anatomist is run in server mode and listen for commands on the socket connection. In this mode, the available features are limited to what can be expressed with Anatomist commands system, so a limited set of features. A list of these commands can be found :anatomist:`here (main page in french, sorry) <html/fr/programmation/commands.html>`. You cannot handle directly the Anatomist objects, they are represented by a key. But Anatomist application runs in a separate process so potential errors in Anatomist don't crash the application that uses the API.

Behind a general interface, this api provides 2 implementations, one for each method of communication with Anatomist.

The implementation that uses the python bindings is called *direct* implementation and is in the module :doc:`anatomist.direct.api <pyanatomist_direct>`. The implementation that uses socket communication is called *socket* implementation and is in the module :doc:`anatomist.socket.api <pyanatomist_socket>`. By default, the implementation used when you import `anatomist.api` is the *direct* implementation.

A third implementation is a thread-safe variant of the direct module: :doc:`anatomist.threaded.api <pyanatomist_threaded>` module. It redirects every call to the API to be actually called from the main thread. It is obviously slower.

Another specific implementation for Brainvisa also exists: *brainvisa.anatomist* module. It enables to use brainvisa database information on loaded objects to automatically load associated referentials and transformations. It uses the same api, so it is possible to switch from one implementation to the other.

By default, the brainvisa module uses the threaded implementation. But it is possible to switch to the socket implementation in the configuration options.


Using the API
-------------

In this part, we will use the same story as in the :anatomist:`anatomist tutorial <ana_training/en/html/index.html>` and see how to do the same with a python script. The data for the examples in this section are the same: ftp://ftp.cea.fr/pub/dsv/anatomist/data/demo_data.zip.

The following examples use the general API functions that are available in both direct and socket implementations.
To run the following examples, we will use an interactive python shell `IPython <http://ipython.org>`_. It is much more practical than the classic python shell because it offers useful features like automatic completion. This program is available in the BrainVISA package with all other executable programs in the *bin* directory of the BrainVISA package directory. *IPython* should be run with the option *--gui=qt*, which runs a Qt event loop, needed for the graphical interface.

.. code-block:: bash

    <brainvisa_installation_directory>/bin/ipython --gui=qt


Run Anatomist
+++++++++++++

First of all, we need to import anatomist API module. Here, in a Python shell, the default implementation is the direct one (Python bindings).

Then we can create an instance of Anatomist class.

::

    import anatomist.api as ana

    a = ana.Anatomist()

Load an object
++++++++++++++

In this example, we will put the path to the *data_for_anatomist* directory in a variable named src. We will use this variable in all the next examples. We will also load a python module named *os* which has useful functions to handle files and paths.

::

    import os
    src = "<path to data_for_anatomist directory>"
    # Load an object
    t1mri = a.loadObject(os.path.join(src, "data_for_anatomist", "subject01", "subject01.nii"))

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch03s02.html>`.

View an object
++++++++++++++

We open an axial window and add the volume loaded in the previous example in this window.

::

    # view an object
    axial = a.createWindow("Axial")
    axial.addObjects(t1mri)

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch03s03.html>`.

When opening a new window, it is possible to change its initial position and size with the *geometry* parameter. This parameter is a list of 4 values (in pixels) : [x, y, width, height].

::

    # customizing the position and size of a new window : the windows will be displayed at position (100, 150) with a size of (300, 300)
    w = a.createWindow("Axial", geometry=[100, 150, 300, 300])

Windows block
+++++++++++++

We create 4 views in the same windows block and add the image in each views.

::

    # view an object in a 4 views block
    block = a.createWindowsBlock(2) # 2 columns
    w1 = a.createWindow("Axial", block=block)
    w2 = a.createWindow("Sagittal", block=block)
    w3 = a.createWindow("Coronal", block=block)
    w4 = a.createWindow("3D", block=block)
    t1mri.addInWindows([w1, w2, w3, w4])

Move the cursor
+++++++++++++++

::

    # show the cursor position
    print("\nCursor at : ", a.linkCursorLastClickedPosition())
    # move the linked cursor 
    w1.moveLinkedCursor([150, 100, 60])
    print("\nCursor at : ", a.linkCursorLastClickedPosition())

Camera
++++++

This method enables to change the :meth:`~Anatomist.AWindow.camera` parameters of a window. In this example, we change the zoom.

::

    axial.camera(zoom=2)

You can also change the rotation of the view by changing the *view_quaternion* parameters. The rotation is represented by a quaternion which is a vector with 4 parameters.

As the interpretation of quaternions is not easy at first time, it is useful to look at the current value of the parameter in a window with the method :meth:`~Anatomist.AItem.getInfos`.

::

    axial.getInfos()
    axial.camera(view_quaternion=[0.9, -0.2, -0.2, 0.3])

It is possible to change the orientation of the slice plane with the parameter *slice_quaternion*.

::

    axial.camera(slice_quaternion=[0.3, 0.3, 0, 0.9])

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch03s04.html>`.


View header information
+++++++++++++++++++++++

::

    # view header
    browser = a.createWindow("Browser")
    browser.addObjects(t1mri)

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch03s05.html>`.

Change the color palette
++++++++++++++++++++++++

::

    # color palette
    palette = a.getPalette("Blue-Green-Red-Yellow")
    t1mri.setPalette(palette)

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch03s06.html>`.

Custom palette
::::::::::::::

You can create a new palette by giving the list of RGB parameters of the palette colors.

::

    # custom palette
    customPalette = a.createPalette("customPalette")
    colors = []
    for x in range(255):
        colors.extend([0, 0, x])

    customPalette.setColors(colors=colors)
    t1mri.setPalette(customPalette)

View meshes
+++++++++++

::

    # view meshes
    lwhite = a.loadObject(os.path.join(src, "data_for_anatomist", "subject01", "subject01_Lwhite.mesh"))
    rwhite = a.loadObject(os.path.join(src, "data_for_anatomist", "subject01", "subject01_Rwhite.mesh"))
    w3d = a.createWindow("3D")
    w3d.addObjects([lwhite, rwhite])

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch03s07.html>`.

Superimposing
+++++++++++++

::

    # superimposing
    a.addObjects(t1mri, w3d)

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch03s08.html>`.

Change mesh material
++++++++++++++++++++

::

    # mesh material
    head = a.loadObject(os.path.join(src, "data_for_anatomist", "subject01", "subject01_head.mesh"))
    head.addInWindows(w3d)
    material = a.Material(diffuse=[0.8, 0.6, 0.6, 0.5])
    head.setMaterial(material)

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch03s09.html>`.

Fusion between two volumes
++++++++++++++++++++++++++

::

    brain_mask = a.loadObject(os.path.join(src, "data_for_anatomist", "subject01", "brain_subject01.nii"))
    brain_mask.setPalette("GREEN-ufusion")
    t1mri.setPalette("B-W LINEAR")
    # fusion 2D
    fusion2d = a.fusionObjects([brain_mask, t1mri], "Fusion2DMethod")
    axial = a.createWindow("Axial")
    axial.addObjects(fusion2d)
    # params of the fusion : linear on non null
    a.execute("Fusion2DParams", object=fusion2d, mode="linear_on_defined", rate=0.4)

It is possible to do different types of fusions using the same method :meth:`Anatomist.fusionObjects` and changing the list of objects and the type of fusion.

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch03s10.html>`.

Load a transformation
+++++++++++++++++++++

::

    t1mri_s2 = a.loadObject(os.path.join(src, "data_for_anatomist", "subject02", "sujet02.ima"))
    t1mri_s2.setPalette("Blue-White")
    fusion2d = a.fusionObjects([t1mri, t1mri_s2], "Fusion2DMethod")
    r1 = a.createReferential()
    r2 = a.createReferential()
    cr = a.centralRef
    t1mri.assignReferential(r1)
    t1mri_s2.assignReferential(r2)
    # load a transformation
    a.loadTransformation(os.path.join(src, "data_for_anatomist", "subject01", "RawT1-subject01_default_acquisition_TO_Talairach-ACPC.trm"), r1, cr)
    a.loadTransformation(os.path.join(src, "data_for_anatomist", "subject02", "RawT1-sujet02_200810_TO_Talairach-ACPC.trm"), r2, cr)
    axial = a.createWindow("Axial")
    axial.addObjects(fusion2d)

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch04.html#ana_training%25load_transformation>`.

Load an existing referential
++++++++++++++++++++++++++++

::

    lwhite.assignReferential(r1)
    axial.addObjects(lwhite)

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch04s02.html>`.

Load referential information from file header
+++++++++++++++++++++++++++++++++++++++++++++

::

    map = a.loadObject(os.path.join(src, "data_for_anatomist", "subject01", "Audio-Video_T_map.nii"))
    map.setPalette("tvalues100-200-100")
    t1mri.loadReferentialFromHeader()
    map.loadReferentialFromHeader()
    fusion_map = a.fusionObjects([t1mri, map], "Fusion2DMethod")
    axial = a.createWindow("Axial")
    axial.addObjects(fusion_map)
    a.execute("Fusion2DParams", object=fusion_map, mode="linear_on_defined", rate=0.5)

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch04s03.html>`.

Display a ROI graph
+++++++++++++++++++

::

    graph = a.loadObject(os.path.join(src, "data_for_anatomist", "roi", "basal_ganglia.arg"))
    w = a.createWindow('3D')
    w.addObjects(graph, add_graph_nodes=True)

See :anatomist:`the corresponding actions in the graphical interface <ana_training/en/html/ch05s02.html>`.

Sending a command to Anatomist
++++++++++++++++++++++++++++++

A lot of commands that can be processed by Anatomist are encapsulted in Anatomist class methods. But some commands, less commonly used are not available through specific methods. Nevertheless, they can be called through a generic method :meth:`Anatomist.execute`.

The list of available commands is listed in the following page: :anatomist:`html/fr/programmation/commands.html`.

In the previous examples, we use this method to call the :anatomist:`Fusion2DParams command <html/fr/programmation/commands.html#Fusion2DParams>` which is not encapsulated in a specific method.

::

    a.execute("Fusion2DParams", object=fusion_map, mode="linear_on_defined", rate=0.5)


Using the direct implementation
-------------------------------

When you use the direct implementation of Anatomist Python API, more features are available. Indeed, each C++ class and function that are declared in the SIP bindings are available in Python. Moreover, the Python script and Anatomist objects share memory, so lower level manipulations are possible.

See the :anatomist:`Anatomist doxygen documentation <doxygen/index.html>` about the C++ API to have more information about the classes and functions that may be available in Python (if the bindings are done).

In this mode, it is also possible to interact on objects directly and interactively with Python Aims API. See more details about that in :doc:`pyanatomist_pyaims_tutorial`.

Amongst the noticeable benefits of the direct implementation is the possibility to use Anatomist views as Qt widgets to build custom interfaces. This is what has been used to program the :anatomist:`AnaSimpleViewer <ana_training/en/html/ch08.html>` application. See the :ref:`simple_viewer` example.

