
from __future__ import print_function
from anatomist.api import Anatomist
import os
from subprocess import Popen, check_output
import atexit
import time

class HeadlessAnatomist(Anatomist):
    ''' Implements an off-screen headless Anatomist.

    .. warning:: Only usable with X11.
        Needs Xvfb and xdpyinfo commands to be available.

    All X rendering is deported to a virtual X server (Xvfb) which doesn't
    actually display things.

    Depending on the OpenGL implementation / driver, Xvfb will not necessarily
    support the GLX extension. This especially happens with NVidia OpenGL on
    Linux.

    To overcome this, it is possible to use VirtualGL
    (http://www.virtualgl.org), but:

    * it needs to run the whole application through vglrun:

        .. code-block:: bash

            vglrun app_script.py
            # or:
            vglrun ipython --gui

    * VirtualGL deports the rendering to a working X server, thus this one has
      to exist, to be running, and to have working OpenGL.

    .. note::
        This implementation connects to a virtual X server, then runs a regular
        Anatomist. This has several limiations:

        * All the widgets from the application will be redirected to this
          display: it is not possible to mix on-screen and off-screen
          rendering, or a regular on-screen Qt application with off-screen
          anatomist snapshoting.

        * HeadlessAnatomist must be instantiated before any Qt widget is
          rendered, because Qt does not allow mixed-X displays. Once a widget
          is created, all others will go to the same display.

    Otherwise, HeadlessAnatomist inherits the configured Anatomist class
    anatomist.api.Anatomist, as configured via
    anatomist.setDefaultImplementation(), to it can use
    any of the different implementations of the Anatomist API.
    '''
    def __singleton_init__(self):
        for display in range(100):
            if not os.path.exists('/tmp/.X11-unix/X%d' % display):
                break
        else:
            raise RuntimeError('Too many X servers')
        self.xvfb = Popen(['Xvfb', '-screen', '0', '1280x1024x24', '+extension', 'GLX', ':%d' % display])

        os.environ['DISPLAY']=':%d' % display

        dpyinfo = None
        t0 = time.clock()
        t1 = 0
        timeout = 5
        while dpyinfo is None and t1 < timeout:
            try:
                dpyinfo = check_output('xdpyinfo')
            except:
                time.sleep(0.01)
                t1 = time.clock() - t0
        if 'GLX' not in dpyinfo:
            print('The current Xvfb does not have a GLX extension. Aborting.')
            self.xvfb.terminate()
            raise RuntimeError('GLX extension missing')
        super(HeadlessAnatomist, self).__singleton_init__()
        atexit.register(self.xvfb.terminate)

    def __del__(self):
        atexit._exithandlers.remove((self.xvfb.terminate, (), {}))
        self.xvfb.terminate()

