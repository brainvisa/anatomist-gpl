
PyAnatomist examples
====================

Most of these examples are expected to be run from an IPython_ shell, run from the directory of the examples (because some of them might load data from the current directory). Start IPython using:

>>> ipython -q4thread

.. _IPython: http://ipython.scipy.org/


Volume manipulation
-------------------

Loading and viewing a Volume with anatomist

Download source: `volumetest.py <../examples/volumetest.py>`_

.. literalinclude:: ../examples/volumetest.py


Aims / Anatomist volume manipulation
------------------------------------

Loading, handling and viewing a Volume with aims and anatomist

Download source: `aimsvolumetest.py <../examples/aimsvolumetest.py>`_

.. literalinclude:: ../examples/aimsvolumetest.py


Mesh manipulation
-----------------

Using a mesh and modifying it while it is displayed

Download source: `meshtest.py <../examples/meshtest.py>`_

.. literalinclude:: ../examples/meshtest.py


Anatomist commands
------------------

Using the commands interpreter in a generic way

Download source: `customcommands.py <../examples/customcommands.py>`_

.. literalinclude:: ../examples/customcommands.py


Fusion 3D
---------

Merging a volume and mesh in a 3D fusion object

Download source: `fusion3D.py <../examples/fusion3D.py>`_

.. literalinclude:: ../examples/fusion3D.py


Graph manipulation
------------------

Loading and displaying a graph

Download source: `graph.py <../examples/graph.py>`_

.. literalinclude:: ../examples/graph.py


Graph building
--------------

Creating a complete graph and nomenclature in Python

Download source: `graph_building.py <../examples/graph_building.py>`_

.. literalinclude:: ../examples/graph_building.py


Events handling
---------------

Catching click events and plugging a callback

Download source: `events.py <../examples/events.py>`_

.. literalinclude:: ../examples/events.py


Selection handling
------------------

Getting selected objects

Download source: `selection.py <../examples/selection.py>`_

.. literalinclude:: ../examples/selection.py


Selection by nomenclature
-------------------------

Selecting graph nodes according a nomenclature

Download source: `nomenclatureselection.py <../examples/nomenclatureselection.py>`_

.. literalinclude:: ../examples/nomenclatureselection.py


Sphere example
--------------

Subclassing Anatomist objects

Download source: `sphere.py <../examples/sphere.py>`_

.. literalinclude:: ../examples/sphere.py


Ellipsoid example
-----------------

Updating the size and shape of an object interactively

Download source: `ellipsoid.py <../examples/ellipsoid.py>`_

.. literalinclude:: ../examples/ellipsoid.py


Custom controls example
-----------------------

Plugging new conrols / actions in Anatomist views

Download source: `control.py <../examples/control.py>`_

.. literalinclude:: ../examples/control.py


Custom menus example
--------------------

Customizing object-specific menus

Download source: `addMenuEntry.py <../examples/addMenuEntry.py>`_

.. literalinclude:: ../examples/addMenuEntry.py


Custom fusion example
--------------------

Registering new fusion types

Download source: `fusion.py <../examples/fusion.py>`_

.. literalinclude:: ../examples/fusion.py


Anatomist API tests
-------------------

Most of anatomist API module features

Download source: `anatomistapiTests.py <../examples/anatomistapiTests.py>`_

.. literalinclude:: ../examples/anatomistapiTests.py


Using OpenGL in PyAnatomist
---------------------------

Customizing OpenGl parameters for objects

Download source: `customopenglobject.py <../examples/customopenglobject.py>`_

.. literalinclude:: ../examples/customopenglobject.py


Texture drawing
---------------

Drawing ROI on a mesh in a texture

Download source: `texturedrawing.py <../examples/texturedrawing.py>`_

.. literalinclude:: ../examples/texturedrawing.py


Measurements on a volume
------------------------

Complete example with a specific graphical interface that embeds an Anatomist window and a matplotlib widget. Shows a 4D volume and a curve of the values in a selected voxel or the mean of values in a selected region.

Download source: `volumeMeasures.py <../examples/volumeMeasures.py>`_

.. literalinclude:: ../examples/volumeMeasures.py


Simple viewer
-------------

An even simplified version of the anasimpleviewer application, which may also be used as a programming example. Its code is in the "bin/"" directory of the binary packages.

Download source: `anaevensimplerviewer.py <../examples/anaevensimplerviewer.py>`_

.. literalinclude:: ../examples/anaevensimplerviewer.py


Using PyAnatomist in BrainVisa
------------------------------

This example shows how to use Anatomist from a BrainVisa process, and get events from Anatomist even when it is run through a socket connection.

Download source: `bvProcessSocket.py <../examples/bvProcessSocket.py>`_

.. literalinclude:: ../examples/bvProcessSocket.py

