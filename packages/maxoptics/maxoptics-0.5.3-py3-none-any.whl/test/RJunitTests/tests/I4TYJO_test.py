from .base import *


# monitor设置新值，monitor使用默认值
# https://e.gitee.com/max-optics/issues/kanban/members?issue=I4TYJO
class I4TYJOTestCase(unittest.TestCase):
    def test_ModeExpansion(self):
        mod_ins = Base.pr.add("ModeExpansion")
        with self.assertRaises(KeyError) as err:
            mod_ins["frequencyPlotResult"]

        with self.assertRaises(KeyError) as err:
            mod_ins["modePlotsResult"]

        c = 299792458
        mod_ins["frequency"] = 200
        self.assertAlmostEqual(c / 1_000_000 / 200, mod_ins["wavelength"])

        mod_ins["wavelength"] = 123123
        self.assertAlmostEqual(c / 1_000_000 / 123123, mod_ins["frequency"])


if __name__ == '__main__':
    unittest.main()
