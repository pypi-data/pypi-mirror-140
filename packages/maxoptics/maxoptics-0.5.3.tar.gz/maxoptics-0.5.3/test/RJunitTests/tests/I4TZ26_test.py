from base import *


class I4TZ26TestCase(unittest.TestCase):
    def test_00_upload(self):
        upl = Base.cl.get_uploader()
        import pathlib
        pprint(pathlib.Path("./src/field_new/te_0_n.mat").stat())
        # with open("./src/field_new/te_0_n.mat", 'rb') as f:
        res = upl.upload_files("./src/field_new/te_0_n.mat")

        pprint(res)

    def test_get_user_mode_files(self):
        pass

    def test_get_user_mode_file_options(self):
        pass

    def test_get_user_mode_file_chart(self):
        pass


if __name__ == '__main__':
    unittest.main()
