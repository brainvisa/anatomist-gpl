
''' anatomist.headless module implements a headless (off-screen) version of
Anatomist, and some helper functions.

The main entry point is HeadlessAnatomist:

>>> import anatomist.headless as ana
>>> a = ana.HeadlessAnatomist()

Other functions are used by HeadlessAnatomist implementation.

'''

from soma.qt_gui import headless
from soma.qt_gui.headless import setup_headless
from soma.qt_gui import qt_backend
import importlib

hanatomist = None


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

    inst_force_virtualgl = headless.force_virtualgl

    allow_virtualgl = True
    if 'allow_virtualgl' in kwargs:
        allow_virtualgl = kwargs['allow_virtualgl']
        kwargs = dict(kwargs)
        del kwargs['allow_virtualgl']
    if 'force_virtualgl' in kwargs:
        inst_force_virtualgl = kwargs['force_virtualgl']
        kwargs = dict(kwargs)
        del kwargs['force_virtualgl']

    qt_backend.set_headless(True, True)
    result = headless.setup_headless(need_opengl=True,
                                     allow_virtualgl=allow_virtualgl,
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

