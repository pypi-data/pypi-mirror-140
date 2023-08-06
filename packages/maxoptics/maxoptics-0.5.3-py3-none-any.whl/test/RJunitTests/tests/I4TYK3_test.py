from .base import *

c = 299792458


# port设置新值，port使用默认值
# https://e.gitee.com/max-optics/issues/kanban/members?issue=I4TYK3
class I4TYK3TestCase(unittest.TestCase):
    def test_EMEPort(self):
        emeport = Base.pr.add("EmePort")
        with self.assertRaises(KeyError) as err: emeport["bend_lacation"]
        self.assertEqual(0, emeport["bend_location"])
        emeport["start_frequency"] = 123123
        self.assertAlmostEqual(c / 1_000_000 / 123123, emeport["stop_wavelength"])
        emeport["stop_frequency"] = 123123
        self.assertAlmostEqual(c / 1_000_000 / 123123, emeport["start_wavelength"])

    def test_FDTDPort(self):
        fdtdport = Base.pr.add("FDTDPort")
        with self.assertRaises(KeyError) as err: fdtdport["bend_lacation"]
        self.assertEqual(0, fdtdport["bend_location"])
        fdtdport["start_frequency"] = 123123
        self.assertAlmostEqual(c / 1_000_000 / 123123, fdtdport["stop_wavelength"])
        fdtdport["stop_frequency"] = 123123
        self.assertAlmostEqual(c / 1_000_000 / 123123, fdtdport["start_wavelength"])


if __name__ == '__main__':
    unittest.main()
