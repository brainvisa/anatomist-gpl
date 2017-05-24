
''' anatomist.headless module implements a headless (off-screen) version of
Anatomist, and some helper functions.

The main entry point is HeadlessAnatomist:

>>> import anatomist.headless as ana
>>> a = ana.HeadlessAnatomist()

Other functions are used by HeadlessAnatomist implementation.

'''

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
hanatomist = None


def setup_virtualGL():
    ''' Load VirtualGL libraries and LD_PRELOAD env variable to run the current
    process via VirtualGL.

    .. warning::
        If the current process has already used some libraries (libX11? libGL
        certainly), setting VirtualGL libs afterwards may cause segfaults and
        program crashes. So it is not safe to use it unless you are sure to to
        it straight at the beginning of the program, prior to importing many
        modules.

        Unfortunately, I don't know how to test it.
    '''
    try:
        preload = ['libdlfaker']
        # vglrun may use either librrfaker or libvglfaker depending on its
        # version.
        try:
            vglfaker = ctypes.CDLL('librrfaker.so', ctypes.RTLD_GLOBAL)
            preload.append('librrfaker.so')
        except:
            vglfaker = ctypes.CDLL('libvglfaker.so', ctypes.RTLD_GLOBAL)
            preload.append('libvglfaker.so')
        dlfaker = ctypes.CDLL('libdlfaker.so', ctypes.RTLD_GLOBAL)
        os.environ['LD_PRELOAD'] = ':'.join(preload)
        os.environ['VGL_ISACTIVE'] = '1'
    except:
        return False
    return True


def test_glx(xdpyinfo_cmd, timeout=5.):
    ''' Test the presence of the GLX module in the X server, by running
    xdpyinfo command

    Parameters
    ----------
    xdpyinfo_cmd: str or list
        xdpyinfo command: may be a string ('xdpyinfo') or a list, which allows
        running it through a wrapper, ex: ['vglrun', 'xdpyinfo']
    timeout: float (optional)
        try several times to connect the X server while waiting for it to
        startup. If 0, try only once and return.

    Returns
    -------
    True if GLX is found, False otherwise.
    '''
    dpyinfo = ''
    t0 = time.time()
    t1 = 0
    while dpyinfo == '' and t1 <= timeout:
        try:
            dpyinfo = check_output(xdpyinfo_cmd)
        except Exception as e:
            time.sleep(0.01)
            t1 = time.time() - t0
    if 'GLX' not in dpyinfo:
        return False
    else:
        return True


def test_opengl(pid=None, verbose=False):
    ''' Test the presence of OpenGL libraries (and which ones) in the specified
    Unix process. Works only on Linux (or maybe ELF Unixes).

    Parameters
    ----------
    pid: int (optional)
        process id to look OpenbGL libs in. Default: current process
    verbose: bool (optional)
        if True, print found libs

    Returns
    -------
    set of loaded libGL libraries
    '''
    if pid is None:
        pid = os.getpid()
    gl_libs = set()
    for line in open('/proc/%d/maps' % pid).readlines():
        lib = line.split()[-1]
        if lib not in gl_libs and lib.find('libGL.so.') != -1:
            gl_libs.add(lib)
            if verbose:
                print(lib)
    return gl_libs


def test_qapp():
    ''' If QtGui is already loaded, switching to VirtualGL in the running
    process leads to segfaults.
    Moreover if QApplication is instantiated, the display is already connected
    and cannot change in Qt afterwards.
    '''
    mods = ('PyQt4.QtGui', 'PyQt5.QtGui', 'PySide.QtGui')
    for mod in mods:
        if mod in sys.modules:
            from soma.qt_gui.qt_backend import QtGui
            if QtGui.QApplication.instance() is not None:
                return 'QApp'
            return 'QtGui'
    return None


def find_mesa():
    ''' Try to find a software Mesa library in the libraries search path.
    Parses the LD_LIBRARY_PATH env variable and libs listed by the command
    "ldconfig -p", looks for a mesa/ subdir containing a libGL.so.1 file.

    Returns
    -------
    Mesa library file with full path, or None if not found
    '''
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


def terminate_xvfb():
    global xvfb
    global original_display
    if xvfb:
        xvfb.terminate()
        xvfb.wait()
        xvfb = None
        if original_display:
            os.environ['DISPLAY'] = original_display
        else:
            del os.environ['DISPLAY']


def setup_headless(allow_virtualgl=True):
    ''' Sets up a headless virtual X server and tunes the current process
    libraries to use it appropriately.

    .. warning::
        calling this function may run a Xvfb process, and change the
        current process libraries to use VirtualGL or Mesa GL.

    If OpenGL library or Qt QtGui module is loaded, then VirtualGL will not be
    allowed to prevent crashes.

    If Qt QApplication is instantiated, headless mode is disabled because Qt
    is already connected to a display that cannot change afterwards.

    If no configuration proves to work, raise an exception.

    Parameters
    ----------
    allow_virtualgl: bool (optional)
        If False, VirtualGL will not be attempted. Default is True.
        Use it if you experience crashes in your programs: it probably means
        that some incompatible libraries have alrealy been loaded.
    '''
    global xvfb
    global original_display

    if xvfb:
        # already setup
        return
    if sys.platform in ('darwin', 'win32'):
        # not a X11 implementation
        return
    qtapp = test_qapp()
    if qtapp == 'QApp':
        # QApplication has already opened the current display: we cannot change
        # it afterwards.
        print('QApplication already instantiated, headless Anatomist is not '
              'possible.')
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

        original_display = os.environ.get('DISPLAY', None)
        os.environ['DISPLAY'] = ':%d' % display

        glx = test_glx(xdpyinfo_cmd)
        gl_libs = set()
        if not glx:
            gl_libs = test_opengl(verbose=True)
            if len(gl_libs) != 0:
                print('OpenGL lib already loaded. Using Xvfb will not be '
                      'possible.')

        if not glx and not gl_libs and allow_virtualgl and qtapp is None:
            # try VirtualGL
            vgl = distutils.spawn.find_executable('vglrun')
            if vgl:
                print('VirtualGL found.')
                if test_glx([vgl, xdpyinfo_cmd], 0):
                    print('VirtualGL should work.')

                    glx = setup_virtualGL()

                    if glx:
                        print('Running through VirtualGL + Xvfb: '
                              'this is optimal.')
                    else:
                        print('But VirtualGL could not be loaded...')

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
                          'installing VirtualGL (http://virtualgl.org) '
                          'and running again before loading QtGui.')
            else:
                print('Mesa not found.')

        if not glx:
            print('The current Xvfb does not have a GLX extension. '
                  'Aborting it.')
            xvfb.terminate()
            xvfb.wait()
            xvfb = None
            if original_display is not None:
                os.environ['DISPLAY'] = original_display
            else:
                del os.environ['DISPLAY']
            use_xvfb = False
            #raise RuntimeError('GLX extension missing')

    if not use_xvfb:
        if xdpyinfo_cmd:
            glx = test_glx(xdpyinfo_cmd, 0)
            if not glx:
                raise RuntimeError('GLX extension missing')
        print('Headless Anatomist running in normal (non-headless) mode')

    if xvfb is not None:
        atexit.register(terminate_xvfb)


def HeadlessAnatomist(*args, **kwargs):
    ''' Implements an off-screen headless Anatomist.

    .. warning:: Only usable with X11.
        Needs Xvfb and xdpyinfo commands to be available, and possibly
        VirtualGL or Mesa.

    All X rendering is deported to a virtual X server (Xvfb) which doesn't
    actually display things.

    Depending on the OpenGL implementation / driver, Xvfb will not
    necessarily support the GLX extension. This especially happens with
    NVidia OpenGL on Linux.

    To overcome this, HeadlessAnatomist will automatically attempt to use
    VirtualGL (http://www.virtualgl.org), but:

    * whole application OpenGL rendering will be redirected through
      VirtualGL, OpenGL calls will be modified.

    * VirtualGL deports the rendering to a working X server, thus this one
      has to exist (other than Xvfb), to be running, and to have working
      OpenGL.

    If VirtualGL is not available, or not working (no X server), then
    HeadlessAnatomist will attempt to find a software Mesa library and
    use it. This has other side effects, since all openGL calls will be
    software.

    .. note::
        This implementation connects to a virtual X server, then runs a
        regular Anatomist. This has several limiations:

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

    Otherwise, returns the unique instance of the configured Anatomist class
    anatomist.api.Anatomist, as configured via
    anatomist.setDefaultImplementation(), to it can use
    any of the different implementations of the Anatomist API.

    If OpenGL has already been loaded, or Xvfb cannot be made to work, and
    if a regular X server conection is working, then a regular, on-screen
    Anatomist will be used.

    Parameters are passed to Anatomist constructor, except the following
    keyword arguments:

    allow_virtualgl: bool (optional)
        If False, VirtualGL will not be attempted. Default is True.
        Use it if you experience crashes in your programs: it probably means
        that some incompatible libraries have alrealy been loaded.
    '''

    global hanatomist
    if hanatomist:
        return hanatomist

    allow_virtualgl = True
    if 'allow_virtualgl' in kwargs:
        allow_virtualgl = kwargs['allow_virtualgl']
        kwargs = dict(kwargs)
        del kwargs['allow_virtualgl']
    setup_headless(allow_virtualgl=allow_virtualgl)

    from anatomist.api import Anatomist

    #def __del__ana(self):
        #atexit._exithandlers.remove((terminate_xvfb, (), {}))
        #terminate_xvfb()

    #def createWindow_ana(self, wintype, **kwargs):
        #options = kwargs.get('options', {})
        #if 'hidden' not in options:
            #options['hidden'] = True
            #kwargs = dict(kwargs)
            #kwargs['options'] = options
        #return self._old_createWindow(wintype, **kwargs)

    hanatomist = Anatomist()
    #Anatomist.__del__ = __del__ana
    #Anatomist._old_createWindow = Anatomist.createWindow
    #Anatomist.createWindow = createWindow_ana

    return hanatomist

