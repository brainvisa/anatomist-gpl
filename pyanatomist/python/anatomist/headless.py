
''' anatomist.headless module implements a headless (off-screen) version of
Anatomist, and some helper functions.

The main entry point is HeadlessAnatomist:

>>> import anatomist.headless as ana
>>> a = ana.HeadlessAnatomist()

Other functions are used by HeadlessAnatomist implementation.

'''

from soma import subprocess
import os
from soma.subprocess import Popen, check_output
import time
import distutils.spawn
import ctypes
import sys
from six.moves import range
import importlib
import shutil
import atexit

virtual_display = 'xvfb'
virtual_display_proc = None
original_display = None
display = None
hanatomist = None
force_virtualgl = True


def setup_virtualGL():
    ''' Load VirtualGL libraries and LD_PRELOAD env variable to run the current
    process via VirtualGL.

    .. warning::
        If the current process has already used some libraries (libX11? libGL
        certainly), setting VirtualGL libs afterwards may cause segfaults and
        program crashes. So it is not safe to use it unless you are sure to do
        it straight at the beginning of the program, prior to importing many
        modules.

        Unfortunately, I don't know how to test it.
    '''
    if os.environ.get('VGL_ISACTIVE') == '1':
        return True
    try:
        if 'VGL_DISPLAY' not in os.environ and original_display is not None:
            # set VGL_DISPLAY to be the initial (3D accelerated) display
            os.environ['VGL_DISPLAY'] = original_display
            print('VGL_DISPLAY:', original_display)
        # needed if linGL is not directly linked against the executable
        os.environ['VGL_GLLIB'] = 'libGL.so.1'
        preload = ['libdlfaker']
        # vglrun may use either librrfaker or libvglfaker depending on its
        # version.
        try:
            vglfaker = ctypes.CDLL('librrfaker.so', ctypes.RTLD_GLOBAL)
            preload.append('librrfaker.so')
        except:
            vglfaker = ctypes.CDLL('libvglfaker.so', ctypes.RTLD_GLOBAL)
            preload.append('libvglfaker.so')
        #dlfaker = ctypes.CDLL('libdlfaker.so', ctypes.RTLD_GLOBAL)
        os.environ['LD_PRELOAD'] = ':'.join(preload)
        os.environ['VGL_ISACTIVE'] = '1'
    except Exception:
        return False
    return True


def test_glx(glxinfo_cmd=None, xdpyinfo_cmd=None, timeout=5.):
    ''' Test the presence of the GLX module in the X server, by running
    glxinfo or xdpyinfo command

    Parameters
    ----------
    glxinfo_cmd: str or list
        glxinfo command: may be a string ('glxinfo') or a list, which allows
        running it through a wrapper, ex: ['vglrun', 'glxinfo']
    xdpyinfo_cmd: str or list
        xdpyinfo command: may be a string ('xdpyinfo') or a list, which allows
        running it through a wrapper, ex: ['vglrun', 'xdpyinfo']. xdpyinfo is
        only used if glxinfo is not present, and can produce an inaccurate
        result (some xvfb servers advertise a GLX extension which does not
        work in fact).
    timeout: float (optional)
        try several times to connect the X server while waiting for it to
        startup. If 0, try only once and return.

    Returns
    -------
    2 if GLX is recognized trough glxinfo (trustable), 1 if GLX is recognized
    through xdpyinfo (not always trustable), 0 otherwise.
    '''
    if glxinfo_cmd is None:
        glxinfo_cmd = distutils.spawn.find_executable('glxinfo')
    if glxinfo_cmd not in (None, []):
        glxinfo = u''
        t0 = time.time()
        t1 = 0
        while glxinfo == u'' and t1 <= timeout:
            # universal_newlines = open stdout/stderr in text mode (Unicode)
            process = Popen(glxinfo_cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)
            try:
                glxinfo, glxerr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                glxinfo, glxerr = process.communicate()
                raise subprocess.TimeoutExpired(process.args, 5,
                                                output=glxinfo)
            retcode = process.poll()

            if retcode != 0:
                if u'unable to open display' not in glxerr:
                    # failed for another reason: probably GLX is not working
                    break
                time.sleep(0.01)
                t1 = time.time() - t0
        if glxinfo != u'' or t1 > timeout:
            if u' GLX Visuals' not in glxinfo:
                return 0
            else:
                return 2

    # here glxinfo has not been used or is not working
    if xdpyinfo_cmd is None:
        xdpyinfo_cmd = distutils.spawn.find_executable('xdpyinfo')
    dpyinfo = u''
    t0 = time.time()
    t1 = 0
    while dpyinfo == u'' and t1 <= timeout:
        try:
            # universal_newlines = open stdout/stderr in text mode (Unicode)
            dpyinfo = check_output(xdpyinfo_cmd,
                                   universal_newlines=True)
        except Exception as e:
            time.sleep(0.01)
            t1 = time.time() - t0
    if u'GLX' not in dpyinfo:
        return 0
    else:
        return 1


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
    process leads to segfaults, or even using GLX in PyQt6.
    Moreover if QApplication is instantiated, the display is already connected
    and cannot change in Qt afterwards.
    However if only a QCoreApplication exists, it is possible to instantiate a
    QApplication in addition (without deleting the QCoreApplication). But
    VirtualGL cannot be used.
    '''
    from soma.qt_gui.qt_backend import QtCore
    if QtCore.QCoreApplication.instance() is not None:
        if QtCore.QCoreApplication.instance().__class__.__name__ \
                != 'QCoreApplication':
            return 'QApp'
        from soma.qt_gui import qt_backend
        if qt_backend.qt_backend == 'PyQt6' and 'PyQt6.QtGui' in sys.modules:
            return 'QApp'  # QtGui is loaded: don't use headless
        return 'QtCore'
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
    ldconfig = check_output(['ldconfig', '-p'], text=True)
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


def start_xvfb(displaynum=None):
    if shutil.which('Xvfb') is None:
        return None
    if displaynum is None:
        for tdisplay in range(100):
            if not os.path.exists('/tmp/.X11-unix/X%d' % tdisplay) \
                    and not os.path.exists('/tmp/.X%d-lock' % tdisplay):
                break
        else:
            raise RuntimeError('Too many X servers')
    else:
        tdisplay = str(displaynum)
    xvfb = Popen(['Xvfb', '-screen', '0', '1280x1024x24',
                  '+extension', 'GLX', ':%d' % tdisplay],
                 preexec_fn=on_parent_exit('SIGINT'))
    if xvfb:
        global display
        display = tdisplay

    return xvfb


def start_xpra(displaynum=None):
    if shutil.which('xpra') is None:
        return None
    if displaynum is None:
        for tdisplay in range(100):
            if not os.path.exists('/tmp/.X11-unix/X%d' % tdisplay) \
                    and not os.path.exists('/tmp/.X%d-lock' % tdisplay):
                break
        else:
            raise RuntimeError('Too many X servers')
    else:
        tdisplay = str(displaynum)
    xpra = Popen(['xpra', 'start', ':%d' % tdisplay,],
                 preexec_fn=on_parent_exit('SIGINT'))
    if xpra:
        global display
        display = tdisplay

    return xpra


def start_virtual_display(display=None):
    global virtual_display
    global virtual_display_proc

    if virtual_display == 'xvfb':
        virtual_display_proc = start_xvfb(display)
        if virtual_display_proc is not None:
            return virtual_display_proc
        else:
            virtual_display = 'xpra'
    if virtual_display == 'xpra':
        virtual_display_proc = start_xpra(display)
    return virtual_display_proc


def terminate_virtual_display():
    global virtual_display
    global virtual_display_proc
    global original_display
    global display

    if virtual_display_proc is None:
        return

    virtual_display_proc.terminate()
    virtual_display_proc.wait()
    virtual_display_proc = None

    if original_display:
        os.environ['DISPLAY'] = original_display
    else:
        del os.environ['DISPLAY']

    if virtual_display == 'xpra':
        subprocess.call(['xpra', 'stop', str(display)])


class PrCtlError(Exception):
    pass


def on_parent_exit(signame):
    """
    Return a function to be run in a child process which will trigger SIGNAME
    to be sent when the parent process dies

    found on https://gist.github.com/evansd/2346614
    """
    import signal
    from ctypes import cdll

    # Constant taken from http://linux.die.net/include/linux/prctl.h
    PR_SET_PDEATHSIG = 1

    signum = getattr(signal, signame)

    def set_parent_exit_signal():
        # http://linux.die.net/man/2/prctl
        result = cdll['libc.so.6'].prctl(PR_SET_PDEATHSIG, signum)
        if result != 0:
            raise PrCtlError('prctl failed with error code %s' % result)
    return set_parent_exit_signal


def setup_headless(allow_virtualgl=True, force_virtualgl=force_virtualgl):
    ''' Sets up a headless virtual X server and tunes the current process
    libraries to use it appropriately.

    .. warning::
        calling this function may run a Xvfb or xpra process, and change the
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
    force_virtualgl: bool (optional)
        only meaningful if allow_virtualgl is True. If force_virtualgl True,
        virtualGL will be attempted even if the X server advertises a GLX
        extension. This is useful when GLX is present but does not work when
        OpenGL is used.
    '''

    global virtual_display_proc
    global virtual_display
    global original_display

    class Result(object):
        def __init__(self):
            self.virtual_display_proc = None
            self.original_display = None
            self.display = None
            self.glx = None
            self.virtualgl = None
            self.headless = None
            self.mesa = False
            self.qtapp = None

    result = Result()
    result.virtual_display_proc = virtual_display_proc
    result.original_display = original_display

    if virtual_display_proc:
        # already setup
        return result
    if sys.platform in ('darwin', 'win32'):
        # not a X11 implementation
        result.headless = False
        return result

    qtapp = test_qapp()
    # print('qtapp:', qtapp)
    result.qtapp = qtapp

    if qtapp == 'QApp':
        # QApplication has already opened the current display: we cannot change
        # it afterwards.
        print('QApplication already instantiated, headless Anatomist is not '
              'possible.')
        result.headless = False
        return result

    use_xvfb = True
    glxinfo_cmd = distutils.spawn.find_executable('glxinfo')
    xdpyinfo_cmd = distutils.spawn.find_executable('xdpyinfo')
    # if not xdpyinfo_cmd:
    # not a X client, probably not Linux
    # use_xvfb = False
    xvfb_cmd = distutils.spawn.find_executable('Xvfb')
    if not xvfb_cmd:
        use_xvfb = False

    if use_xvfb:
        virtual_display_proc = start_virtual_display()

    if virtual_display_proc is not None:
        global display

        original_display = os.environ.get('DISPLAY', None)
        print('using DISPLAY=:%s' % display)
        os.environ['DISPLAY'] = ':%s' % display

        result.original_display = original_display
        result.display = display
        result.virtual_display_proc = virtual_display_proc
        result.headless = True

        glx = test_glx(glxinfo_cmd=glxinfo_cmd, xdpyinfo_cmd=xdpyinfo_cmd)
        result.glx = glx

        gl_libs = set()
        if not glx:
            gl_libs = test_opengl(verbose=True)
            if len(gl_libs) != 0:
                print('OpenGL lib already loaded. Using Xvfb or xpra will not '
                      'be possible.')
                result.virtual_display_proc = None

        # WARNING: the test was initially glx < 2, but then it would not
        # enable virtualGL if glx is detected through glxinfo. I don't remember
        # why this was done this way, we perhaps experienced some crashes.

        if (glx < 2 or force_virtualgl) and not gl_libs and allow_virtualgl \
                and qtapp is None:
            # try VirtualGL
            vgl = distutils.spawn.find_executable('vglrun')
            if vgl:
                print('VirtualGL found.')
                vglglxinfo_cmd = None
                vglxdpyinfo_cmd = None
                if glxinfo_cmd:
                    vglglxinfo_cmd = [vgl, '-d', original_display, glxinfo_cmd]
                if xdpyinfo_cmd:
                    vglxdpyinfo_cmd = [vgl, '-d', original_display,
                                       xdpyinfo_cmd]
                if test_glx(glxinfo_cmd=vglglxinfo_cmd,
                            xdpyinfo_cmd=vglxdpyinfo_cmd, timeout=0):
                    print('VirtualGL should work.')

                    glx = setup_virtualGL()
                    result.virtualgl = glx

                    if glx:
                        print('Running through VirtualGL + %s: '
                              'this is optimal.' % virtual_display)
                    else:
                        print('But VirtualGL could not be loaded...')

                    # test_opengl(verbose=True)
        else:
            print('Too dangerous to use VirtualGL: QCoreApplication is '
                  'instantiated, or GLX is not completely OK, or OpenGL libs '
                  'are loaded.')

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
                virtual_display_proc.terminate()
                virtual_display_proc.wait()
                virtual_display_proc = start_virtual_display(display=display)
                result.virtual_display_proc = virtual_display_proc
                #self.mesa_lib = mesa_lib
                glx = test_glx(glxinfo_cmd, xdpyinfo_cmd)
                result.glx = glx
                result.mesa = True
                if glx:
                    print('Running using Mesa software OpenGL: performance '
                          'will be slow. To get faster results, and if X '
                          'server connection can be obtained, consider '
                          'installing VirtualGL (http://virtualgl.org) '
                          'and running again before loading QtGui.')
            else:
                print('Mesa not found.')

        if not glx:
            print('The current virtual display does not have a GLX extension. '
                  'Aborting it.')
            virtual_display_proc.terminate()
            virtual_display_proc.wait()
            virtual_display_proc = None
            result.virtual_display_proc = None
            if original_display is not None:
                os.environ['DISPLAY'] = original_display
                result.display = original_display
            else:
                del os.environ['DISPLAY']
                result.display = None
            use_xvfb = False
            #raise RuntimeError('GLX extension missing')

    if not use_xvfb:
        if xdpyinfo_cmd:
            glx = test_glx(glxinfo_cmd, xdpyinfo_cmd, 0)
            result.glx = glx
            if not glx:
                raise RuntimeError('GLX extension missing')
        print('Headless Anatomist running in normal (non-headless) mode')
        result.headless = False

    # this is not needed any longer for Xvfb, since on_parent_exit() is passed
    # to Popen, but xpra needs to stop the corresponding server
    if virtual_display_proc is not None:
        atexit.register(terminate_virtual_display)

    return result


def HeadlessAnatomist(*args, **kwargs):
    ''' Implements an off-screen headless Anatomist.

    .. warning:: Only usable with X11.
        Needs either Xvfb or xpra, and xdpyinfo commands to be available,
        and possibly VirtualGL or Mesa.

    All X rendering is deported to a virtual X server (Xvfb or xpra) which
    doesn't actually display things.

    Depending on the OpenGL implementation / driver, Xvfb will not
    necessarily support the GLX extension. This especially happens with
    NVidia OpenGL on Linux.

    To overcome this, HeadlessAnatomist will automatically attempt to use
    VirtualGL (http://www.virtualgl.org), but:

    * all application OpenGL rendering will be redirected through
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
    (keyword) arguments:

    implementation: str (default: 'direct')
        Anatomist API implementation. May be a shortcut ('direct', 'threaded',
        'nbanatomist') or a module + class name
        ('anatomist.direct.api.Anatomist')
    allow_virtualgl: bool (optional, default: True)
        If False, VirtualGL will not be attempted. Default is True.
        Use it if you experience crashes in your programs: it probably means
        that some incompatible libraries have alrealy been loaded.
    force_virtualgl: bool (optional, default: False)
        only meaningful if allow_virtualgl is True. If force_virtualgl True,
        virtualGL will be attempted even if the X server advertises a GLX
        extension through the xdpyinfo command (if glxinfo is OK, then this
        command is trusted). This is useful when GLX is present but does not
        work when OpenGL is used.
    '''

    global hanatomist
    if hanatomist:
        return hanatomist

    global force_virtualgl
    inst_force_virtualgl = force_virtualgl

    allow_virtualgl = True
    if 'allow_virtualgl' in kwargs:
        allow_virtualgl = kwargs['allow_virtualgl']
        kwargs = dict(kwargs)
        del kwargs['allow_virtualgl']
    if 'force_virtualgl' in kwargs:
        inst_force_virtualgl = kwargs['force_virtualgl']
        kwargs = dict(kwargs)
        del kwargs['force_virtualgl']

    result = setup_headless(allow_virtualgl=allow_virtualgl,
                            force_virtualgl=inst_force_virtualgl)

    implementation = kwargs.get('implementation', 'direct')
    if '.' in implementation:
        mod, aclass = implementation.rsplit('.', 1)
    else:
        mod = 'anatomist.%s' % implementation
        aclass = 'Anatomist'

    module = importlib.import_module(mod)
    try:
        Anatomist = getattr(module, aclass)
    except AttributeError:
        mod = '%s.api' % mod
        module = importlib.import_module(mod)
        Anatomist = getattr(module, aclass)

    # def __del__ana(self):
    #atexit._exithandlers.remove((terminate_virtual_display, (), {}))
    # terminate_virtual_display()

    # def createWindow_ana(self, wintype, **kwargs):
    #options = kwargs.get('options', {})
    # if 'hidden' not in options:
    #options['hidden'] = True
    #kwargs = dict(kwargs)
    #kwargs['options'] = options
    # return self._old_createWindow(wintype, **kwargs)

    hanatomist = Anatomist()
    hanatomist.headless_info = result
    #Anatomist.__del__ = __del__ana
    #Anatomist._old_createWindow = Anatomist.createWindow
    #Anatomist.createWindow = createWindow_ana

    return hanatomist

# shortcut for implementations
Anatomist = HeadlessAnatomist

