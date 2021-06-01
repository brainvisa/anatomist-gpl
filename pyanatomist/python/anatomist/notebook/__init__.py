
from anatomist.headless import HeadlessAnatomist
from functools import partial

# this shortcut is used to easily get the Anatomist implementation
Anatomist = partial(
    HeadlessAnatomist,
    implementation='anatomist.notebook.api.NotebookAnatomist')
'''
Anatomist implementation rendering in a Jupyter Notebook. It is the headless wrapping around the :class:`NotebookAnatomist` implementation.
'''


