
from __future__ import print_function

import subprocess
import os
from subprocess import Popen, check_output
import atexit
import time
import distutils.spawn
import ctypes
import sys

xvfb = None
original_display = None


def setup_virtualGL():
    try:
        rfaker = ctypes.CDLL('librrfaker.so', ctypes.RTLD_GLOBAL)
        dlfaker = ctypes.CDLL('libdlfaker.so', ctypes.RTLD_GLOBAL)
        os.environ['LD_PREFLOAD'] = 'libdlfaker.so:librrfaker.so'
        os.environ['VGL_ISACTIVE'] = '1'
    except:
        return False
    return True


def test_glx(xdpyinfo_cmd):
    dpyinfo = ''
    t0 = time.time()
    t1 = 0
    timeout = 5
    while dpyinfo == '' and t1 < timeout:
        try:
            dpyinfo = check_output(xdpyinfo_cmd)
        except Exception, e:
            print(e)
            time.sleep(0.01)
            t1 = time.time() - t0
    if 'GLX' not in dpyinfo:
        return False
    else:
        return True


def test_opengl(pid=None, verbose=False):
    if pid is None:
        pid = os.getpid()
    gl_libs = set()
    for line in open('/proc/%d/maps' % pid).readlines():
        lib = line.split()[-1]
        if lib not in gl_libs and lib.find('libGL.so.1') != -1:
            gl_libs.add(lib)
            if verbose:
                print(lib)
    return gl_libs


def find_mesa():
    paths = os.environ.get('LD_LIBRARY_PATH')
    ldconfig = check_output(['ldconfig', '-p'])
    paths2 = [os.path.dirname(p.split()[-1])
              for p in ldconfig.split('\n')[1:-1]]
    if paths:
        paths = paths.split(':')
    else:
        paths = []
    spaths = set(paths)
    for p in paths2:
        if p not in spaths:
            paths.append(p)
            spaths.add(p)
    for path in paths:
        test_gl = os.path.join(path, 'mesa', 'libGL.so.1')
        if os.path.exists(test_gl):
            return test_gl
    return None


def setup_headless():
    global xvfb
    global original_display

    if xvfb:
        # already setup
        return
    use_xvfb = True
    xdpyinfo_cmd = distutils.spawn.find_executable('xdpyinfo')
    if not xdpyinfo_cmd:
        # not a X client, probably not Linux
        use_xvfb = False
    xvfb_cmd = distutils.spawn.find_executable('Xvfb')
    if not xvfb_cmd:
        use_xvfb = False

    if use_xvfb:
        for display in range(100):
            if not os.path.exists('/tmp/.X11-unix/X%d' % display) \
                    and not os.path.exists('/tmp/.X%d-lock' % display):
                break
        else:
            raise RuntimeError('Too many X servers')
        xvfb = Popen(['Xvfb', '-screen', '0', '1280x1024x24',
                      '+extension', 'GLX', ':%d' % display])

        original_display = os.environ['DISPLAY']
        os.environ['DISPLAY']=':%d' % display

        glx = test_glx(xdpyinfo_cmd)
        if not glx:
            gl_libs = test_opengl(verbose=True)
            if len(gl_libs) != 0:
                print('OpenGL lib already loaded. Using Xvfb will not be '
                      'possible.')

        if not glx and not gl_libs:
            # try VirtualGL
            vgl = distutils.spawn.find_executable('vglrun')
            if vgl:
                print('VirtualGL found.')
                if test_glx([vgl, xdpyinfo_cmd]):
                    print('VirtualGL should work.')

                    glx = setup_virtualGL()

                    if glx:
                        print('Running through VirtualGL + Xvfb: '
                              'this is optimal.')

                    #test_opengl(verbose=True)

        if not glx and not gl_libs:
            # try Mesa, if found
            mesa = find_mesa()
            if mesa:
                print('MESA found:', mesa)
                mesa_lib = ctypes.CDLL(mesa, ctypes.RTLD_GLOBAL)
                os.environ['LD_PRELOAD'] = mesa
                os.environ['LD_LIBRARY_PATH'] \
                    = os.path.dirname(mesa) + ':' \
                        + os.getenv('LD_LIBRARY_PATH')
                # re-run Xvfb using new path
                xvfb.terminate()
                xvfb.wait()
                xvfb = Popen(['Xvfb', '-screen', '0', '1280x1024x24',
                              '+extension', 'GLX', ':%d' % display])
                #self.mesa_lib = mesa_lib
                glx = test_glx(xdpyinfo_cmd)
                if glx:
                    print('Running using Mesa software OpenGL: performance '
                          'will be slow. To get faster results, and if X '
                          'server connection can be obtained, consider '
                          'installing VirtualGL (http://virtualgl.org).')
            else:
                print('Mesa not found.')

        if not glx:
            print('The current Xvfb does not have a GLX extension. '
                  'Aborting it.')
            xvfb.terminate()
            xvfb.wait()
            xvfb = None
            os.environ['DISPLAY'] = original_display
            use_xvfb = False
            #raise RuntimeError('GLX extension missing')

    if not use_xvfb:
        if xdpyinfo_cmd:
            glx = test_glx(xdpyinfo_cmd)
            if not glx:
                raise RuntimeError('GLX extension missing')
        print('Headeless Anatomist running in normal (non-headless) mode')


def terminate_xvfb():
    global xvfb
    global original_display
    if xvfb:
        xvfb.terminate()
        xvfb.wait()
        xvfb = None
        if original_display:
            os.environ['DISPLAY'] = original_display


def HeadlessAnatomist():
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

        * HeadlessAnatomist should be instantiated before any OpenGL
          library is loaded to allow tweaking, using either VirtualGL
          (http://virtualgl.org), or a software Mesa OpenGL if one can be
          found and is useable.
          This means any Qt module should *not* be imported yet, including
          anatomist.api.
          If OpenGL is already loaded, just hope its implementation will be
          compatible with Xvfb.

        * HeadlessAnatomist must be instantiated before any Qt widget is
          rendered, because Qt does not allow mixed-X displays. Once a
          widget is created, all others will go to the same display.

    Otherwise, HeadlessAnatomist inherits the configured Anatomist class
    anatomist.api.Anatomist, as configured via
    anatomist.setDefaultImplementation(), to it can use
    any of the different implementations of the Anatomist API.
    '''

    setup_headless()

    from anatomist.api import Anatomist

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

            * HeadlessAnatomist should be instantiated before any OpenGL
              library is loaded to allow tweaking, using either VirtualGL
              (http://virtualgl.org), or a software Mesa OpenGL if one can be
              found and is useable.
              This means any Qt module should *not* be imported yet, including
              anatomist.api.
              If OpenGL is already loaded, just hope its implementation will be
              compatible with Xvfb.

            * HeadlessAnatomist must be instantiated before any Qt widget is
              rendered, because Qt does not allow mixed-X displays. Once a
              widget is created, all others will go to the same display.

        Otherwise, HeadlessAnatomist inherits the configured Anatomist class
        anatomist.api.Anatomist, as configured via
        anatomist.setDefaultImplementation(), to it can use
        any of the different implementations of the Anatomist API.
        '''
        def __singleton_init__(self):
            self.xvfb = xvfb

            super(HeadlessAnatomist, self).__singleton_init__()
            atexit.register(terminate_xvfb)

        def __del__(self):
            atexit._exithandlers.remove((terminate_xvfb, (), {}))
            terminate_xvfb()

    hana = HeadlessAnatomist()
    return hana

