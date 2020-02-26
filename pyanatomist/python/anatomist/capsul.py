from __future__ import print_function
from __future__ import absolute_import

import os
from capsul.api import InteractiveProcess
from traits.api import File, Enum, Int
import math
from six.moves import range

class AnatomistSceneProcess(InteractiveProcess):
    '''
    Base class for all viewers and snapshot generators. All derived 
    classes must define a create_anatomist_view method that create 
    an anatomist window containing a scene.
    '''
    output = File(output=True)
    output_width = Int(None, output=False)
    output_height = Int(None, output=False)

    def __init__(self, *args, **kwargs):
        super(AnatomistSceneProcess, self).__init__(*args, **kwargs)
        self._anatomist = None

    def set_anatomist(self, anatomist):
        '''
        Define the Anatomist instance that will be used when viewer is
        executed.
        '''
        self._anatomist = anatomist

    @property
    def anatomist(self):
        '''
        Get the anatomist instance for the viewer. Create a new Anatomist
        instance if self.set_anatomist has not already been called.
        '''
        if self._anatomist is None:
            if self.is_interactive:
                from anatomist.api import Anatomist
                self.set_anatomist(Anatomist('-b'))
            else:
                from anatomist.headless import HeadlessAnatomist
                try:
                    a = HeadlessAnatomist('-b')
                except:
                    a = Anatomist('-b')
                self.set_anatomist(a)
        return self._anatomist

    def create_anatomist_view(self):
         '''
         This method must be defined in derived classes. It is
         responsible for the creation of the Anatomist scene. The 
         value returned by the method is a dictionary with two items :
         'objects' that contains the list of created Anatomist objects 
         and 'windows' that contains the list of anatomist windows created
         by this method.
         '''
         raise NotImplementedError()

    def snapshot(self, view_objects):
        '''
        This method is called to create a snapshot for this scene
        factory. view_objects must be the result
        of self.create_anatomist_view(). It creates a snapshot of 
        the first Anatomist window.
        '''
        windows = view_objects['windows']
        if windows:
            from soma.qt_gui.qt_backend import QtGui
            # still needed until fixed in Anatomist C++ lib
            #QtGui.qApp.processEvents()
            windows[0].snapshot(self.output, self.output_width,
                                self.output_height)

    def _run_process(self):
        '''
        Process execution method. First, it calls self.create_anatomist_view().
        Then, if self.snapshot is defined and not empty, 
        it calls self.snapshot(). Finally, if the process is interactive, all
        Anatomist windows created are displayed.
        '''
        view_objects = self.create_anatomist_view()
        if self.output:
            self.snapshot(view_objects)
        if self.is_interactive:
            for window in view_objects['windows']:
                window.show()
        return view_objects


class Anatomist3DWindowProcess(AnatomistSceneProcess):
    '''
    Specialization of AnatomistSceneProcess for scene with a single
    3D-like window. This adds to the process several parameters to
    control the created window point of view.
    '''
    reuse_window = Int(0)
    window_type = Enum(('Axial', 'Saggital', 'Coronal', '3D'))

    def get_window(self):
        a = self.anatomist
        if self.reuse_window:
            windows_per_id = dict((w.internalRep.winId(), w)
                                  for w in self.anatomist.getWindows())
            window = windows_per_id.get(self.reuse_window)
            if window is None:
                raise ValueError('Cannot find an Anatomist window with the '
                                 'given id (%d)' % self.reuse_window)
        else:
            window = self.anatomist.createWindow(self.window_type,
                                                 options={'hidden':True})
        return window


class AnatomistMultipleViewsProcess(AnatomistSceneProcess):
    '''
    Specialization of AnatomistSceneProcess for a scene with multiple Anatomist
    windows. The resulting snapshot will compose a large image according to the specified layout.
    '''
    view_layout_cols = Int(0)
    view_layout_rows = Int(0)
    margin = Int(5)

    def __init__(self, *args, **kwargs):
        super(AnatomistMultipleViewsProcess, self).__init__(*args, **kwargs)
        self.view_layout_position = None

    def snapshot(self, view_objects):
        windows = view_objects['windows']
        if windows:
            from soma.qt_gui.qt_backend import QtGui

            if self.view_layout_position:
                nc = max([x[1] for x in self.view_layout_position]) + 1
                nl = max([x[0] for x in self.view_layout_position]) + 1
            else:
                if self.view_layout_cols != 0:
                    nc = min(self.view_layout_cols, len(windows))
                    nl = int(math.ceil(float(len(windows)) / nc))
                elif self.view_layout_rows != 0:
                    nl = min(self.view_layout_rows, len(windows))
                    nc = int(math.ceil(float(len(windows)) / nl))
                else:
                    nc = int(math.ceil(math.sqrt(len(windows))))
                    nl = int(math.ceil(float(len(windows)) / nc))

            widths = [0] * nc
            heights = [0] * nl

            for i, win in enumerate(windows):
                w = 0
                h = 0
                if self.output_width or self.output_height:
                    w, h = self.output_width, self.output_height
                if w == 0 or h == 0:
                    w2, h2 = win.getInfos()['view_size']
                    if w == 0:
                        w = w2
                    if h == 0:
                        h = h2
                if self.view_layout_position:
                    l, c = self.view_layout_position[i]
                else:
                    c = i % nc
                    l = i / nc
                if widths[c] < w:
                    widths[c] = w
                if heights[l] < h:
                    heights[l] = h

            wpos = []
            p = 0
            for i in range(nc):
                wpos.append(p)
                p += widths[i] + self.margin
            hpos = []
            p = 0
            for i in range(nl):
                hpos.append(p)
                p += heights[i] + self.margin

            out_image = QtGui.QImage(wpos[-1] + widths[-1],
                                     hpos[-1] + heights[-1],
                                     QtGui.QImage.Format_RGB32)
            out_image.fill(0)
            painter = QtGui.QPainter(out_image)
            for i, win in enumerate(windows):
                if self.view_layout_position:
                    l, c = self.view_layout_position[i]
                else:
                    c = i % nc
                    l = i / nc
                if len(win.objects) == 0:
                    continue
                win.windowConfig(cursor_visibility=0)
                img = win.snapshotImage(self.output_width, self.output_height)
                win.windowConfig(cursor_visibility=1)
                painter.drawImage(wpos[c], hpos[l], img)
            del painter

            out_image.save(self.output)

