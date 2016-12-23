
from anatomist.capsul import Anatomist3DWindowProcess
from traits.api import File
import unittest
from capsul.api import get_process_instance
import anatomist.headless as hana
from soma import aims
import numpy as np
import tempfile
import os


class SingleObjectViewer(Anatomist3DWindowProcess):

    input = File(output=False)

    def create_anatomist_view(self):
        # should not be imported in the module to avoid loading Qt too early
        from soma.qt_gui.qt_backend import QtGui
        obj = self.anatomist.loadObject(self.input)
        obj.setPalette('Blue-Red')
        win = self.get_window()
        win.addObjects(obj)

        items = {'objects': [obj], 'windows': [win]}

        return items


def prepare_volume():
    # create an object
    vol = aims.Volume(256, 256, 128, dtype='S16')
    vol.fill(0)
    nvol = np.asarray(vol)
    nvol[100:150, 80:180, 40:80, 0] = 100
    nvol[50:120, 120:160, 40:80, 0] = 200
    input_file_t = tempfile.mkstemp(prefix='pyanat_', suffix='.nii.gz')
    os.close(input_file_t[0])
    input_file = input_file_t[1]
    aims.write(vol, input_file)
    return input_file


class TestSingleViewer(unittest.TestCase):

    def setUp(self):
        viewer = get_process_instance(SingleObjectViewer())
        #viewer.is_interactive = True
        # instanciation here is very important to ensure VirtualGL libs
        # can be loaded NOW, before other libs are loaded.
        # If too late, use the following:
        # a = hana.HeadlessAnatomist('-b', allow_virtualgl=False)
        a = hana.HeadlessAnatomist('-b')
        #import anatomist.api as ana
        #a = ana.Anatomist('-b')
        viewer.set_anatomist(a)

        input_file = prepare_volume()
        self.input_file = input_file
        output_file_t = tempfile.mkstemp(prefix='pyanat_snapshot',
                                         suffix='.png')
        os.close(output_file_t[0])
        output_file = output_file_t[1]
        self.output_file = output_file

        viewer.input = input_file
        viewer.output = output_file
        viewer.output_width = 2000
        viewer.output_height = 1500
        self.viewer = viewer


    def test_class_user_parameters(self):
        viewer = self.viewer
        items = viewer()

        # read output image and test it
        image = aims.read(self.output_file)
        image_size = list(image.getSize()[:2])
        asked_size = [viewer.output_width, viewer.output_height]

        if viewer.is_interactive:
            # should not be imported in the module to avoid loading Qt
            # too early
            from soma.qt_gui.qt_backend import QtGui
            QtGui.qApp.exec_()

        self.assertEqual(image_size, asked_size)
        self.assertEqual(image.at(0, 0), aims.AimsRGB(255, 255, 255))
        self.assertEqual(image.at(272, 415), aims.AimsRGB(0, 0, 131))
        self.assertEqual(image.at(631, 892), aims.AimsRGB(131, 0, 0))
        self.assertEqual(image.at(1107, 812), aims.AimsRGB(115, 255, 139))
        self.assertEqual(image.at(1557, 1345), aims.AimsRGB(0, 0, 131))
        self.assertEqual(image.at(1950, 1409), aims.AimsRGB(255, 255, 255))

        del items

    def tearDown(self):
        os.unlink(self.input_file)
        #print('output:', self.output_file)
        os.unlink(self.output_file)


def test():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSingleViewer)
    runtime = unittest.TextTestRunner(verbosity=2).run(suite)
    return runtime.wasSuccessful()


if __name__ == "__main__":
    test()



