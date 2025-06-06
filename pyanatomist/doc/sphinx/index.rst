
.. image:: anatomist.png
  :align: center

.. _pyanatomist_index:

PyAnatomist programming documentation
-------------------------------------

First, have a look at the :anatomist:`PyAnatomist overview <pyanatomist_overview.pdf>` slides, which were presented at the `Python in Neuroscience 2011 <http://pythonneuro.sciencesconf.org/>`_ conference on 2011/08/30.

.. automodule:: anatomist
  :members:


Sub-modules
-----------

- :doc:`pyanatomist_base`

- :doc:`pyanatomist_direct`

- :doc:`pyanatomist_socket`

- :doc:`pyanatomist_threaded`

- :doc:`pyanatomist_cpp`

- :doc:`pyanatomist_headless`

- :doc:`pyanatomist_notebook`

- The C++ bindings are built on top of :pyaims:`PyAims <index.html>`

- :doc:`pyanatomist_addons`

- :doc:`pyanatomist_wip`

- Description of the :anadev:`commands system <commands.html>`

How to
------

- :doc:`pyanatomist_howto`


PyAnatomist examples
--------------------

.. ifconfig:: 'sphinx_gallery.gen_gallery' not in extensions

    :doc:`pyanatomist_examples`

.. ifconfig:: 'sphinx_gallery.gen_gallery' in extensions

    :doc:`auto_examples/index`


Tutorial
--------

.. ifconfig:: 'nbsphinx' in extensions

    - :doc:`pyanatomist_tutorial_nb`
    - :download:`Downoad the tutorial notebook <pyanatomist_tutorial_nb.ipynb>`
    - :doc:`pyanatomist_pyaims_tutorial`
    - You can also have a look at the :pyaims:`PyAims tutorial <pyaims_tutorial_nb.html>`.
    - :doc:`ana_notebook`
    - :download:`Downoad the notebook demo <ana_notebook.ipynb>`


.. ifconfig:: 'nbsphinx' not in extensions

    - :doc:`pyanatomist_tutorial`
    - :download:`Downoad the tutorial notebook <pyanatomist_tutorial_nb.ipynb>`
    - :doc:`pyanatomist_pyaims_tutorial`
    - You can also have a look at the :pyaims:`PyAims tutorial <pyaims_tutorial.html>`.
    - :download:`Downoad the notebook demo  <ana_notebook.ipynb>`


Table of contents
-----------------

.. ifconfig:: 'nbsphinx' in extensions

    .. toctree::
      :maxdepth: 3

      pyanatomist_base
      pyanatomist_direct
      pyanatomist_socket
      pyanatomist_threaded
      pyanatomist_cpp
      pyanatomist_headless
      pyanatomist_notebook
      pyanatomist_wip
      pyanatomist_tutorial_nb
      pyanatomist_pyaims_tutorial
      pyanatomist_howto
      ana_notebook

.. ifconfig:: 'nbsphinx' not in extensions

    .. toctree::
      :maxdepth: 3

      pyanatomist_base
      pyanatomist_direct
      pyanatomist_socket
      pyanatomist_threaded
      pyanatomist_cpp
      pyanatomist_headless
      pyanatomist_notebook
      pyanatomist_wip
      pyanatomist_tutorial
      pyanatomist_pyaims_tutorial
      pyanatomist_howto

.. ifconfig:: 'sphinx_gallery.gen_gallery' in extensions

    .. toctree::
      :maxdepth: 3

      auto_examples/index

.. ifconfig:: 'sphinx_gallery.gen_gallery' not in extensions

    .. toctree::
      :maxdepth: 3

      pyanatomist_examples

