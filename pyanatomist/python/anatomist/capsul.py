from __future__ import print_function
from __future__ import absolute_import

import os
from capsul.api import InteractiveProcess
from traits.api import File, Enum, Int

class AnatomistSceneProcess(InteractiveProcess):
    '''
    Base class for all viewers and snapshot generators. All derived 
    classes must define a create_anatomist_view method that create 
    an anatomist window containing a scene.
    '''
    output = File(output=True)
    
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
                self.set_anatomist(HeadlessAnatomist())
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
            windows[0].snapshot(self.output)
    
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
            windows_per_id = dict((w.internalRep.winId(), w) for w in self.anatomist.getWindows())
            window = windows_per_id.get(self.reuse_window)
            if window is None:
                raise ValueError('Cannot find an Anatomist window with the given id (%d)' % self.reuse_window)
        else:
            window = self.anatomist.createWindow(self.window_type,  options={'hidden':True})
        return window

    