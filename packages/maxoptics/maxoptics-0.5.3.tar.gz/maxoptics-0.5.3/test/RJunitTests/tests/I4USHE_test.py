from .base import *
from maxoptics.base import Material, Waveform
from random import random

from maxoptics import httpio


# ensure_material/ensure_waveform(replace=True) 卻創建了新的record
# https://e.gitee.com/max-optics/issues/kanban/members?issue=I4USHE
class I4USHETestCase(unittest.TestCase):
    def test_ensure_material(self):
        mat_name = "UT0"
        n = random()
        mat = Material(mat_name, {1.55e-06: [n, 0]})
        pprint(mat.to_dict2())
        Base.cl.ensure_materials([mat], "passive", True)
        Base.cl.user_materials.reload()
        pprint(Base.cl.user_materials[mat_name])
        self.assertAlmostEqual(n,
                               Base.cl.user_materials[mat_name]['table_data']['List data_indexes']['1.55e-06'][0])

    def test_ensure_waveform(self):
        wav_name = "UT0"
        n = random()
        wav = Waveform(wav_name, n, 0, 0, 0, 0)
        Base.cl.ensure_waveforms([wav], True)
        Base.cl.user_waveforms.reload()
        pprint(Base.cl.user_waveforms[wav_name])
        self.assertAlmostEqual(n,
                               Base.cl.user_waveforms[wav_name]['data']['center_frequency'])


if __name__ == '__main__':
    unittest.main()
