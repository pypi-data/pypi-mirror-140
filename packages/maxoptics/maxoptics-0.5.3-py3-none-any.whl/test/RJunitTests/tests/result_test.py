from .base import *


class ResultTestCase(unittest.TestCase):
    def test_emeres(self):
        task = Base.cl.restore_task(24402, "EME").asEME()
        res = task.get_smatrix("ABS")
        pprint(res.DataFrame)


if __name__ == '__main__':
    unittest.main()
