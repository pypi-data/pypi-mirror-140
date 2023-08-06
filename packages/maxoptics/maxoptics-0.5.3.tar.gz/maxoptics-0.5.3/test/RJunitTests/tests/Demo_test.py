from .base import *


class DemoTestCase(unittest.TestCase):
    def test_version(self):
        # self.assertEqual(True, False)  # add assertion here
        self.assertEqual(maxoptics.__VERSION__, "0.5.2")  # add assertion here

    def test_load_config(self):
        self.assertEqual(Path(__file__).parent / "maxoptics.conf", maxoptics.__CONFIGPATH__)

    def test_00_init(self):
        global cl
        cl = maxoptics.MosLibrary()

    def test_01_initProject(self):
        global pr
        pr = cl.create_project_as("Unittest")

    def test_02_warehouse(self):
        self.assertTrue(cl, "Initialization Failed")
        self.assertTrue(cl.user_materials)
        self.assertTrue(cl.user_waveforms)
        self.assertTrue(cl.public_materials)

    def test_03_h_zSpan_corr(self):
        rec = pr.add("Rectangle")
        self.assertEqual(rec['h'], rec['z_span'])
        rec['z_span'] = 10_000
        self.assertEqual(rec['h'], rec['z_span'])




if __name__ == '__main__':
    unittest.main()
