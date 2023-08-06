from maxoptics.base import Material
from .base import *
import seaborn as sns
import matplotlib.pyplot as plt

from maxoptics.utils.attach_port import attach_port
from maxoptics.plot.PolygonLike import compromised_transform


class PortAttachmentTestCase(unittest.TestCase):
    def test_(self):
        PortAT1 = Material("PortAT1", {1.55e-06: [30, 0]})
        PortAT2 = Material("PortAT2", {1.55e-06: [10, 0]})
        Base.cl.ensure_materials([PortAT1, PortAT2], "passive", replace=True)
        project = Base.cl.create_project_as("TestAttach")
        project.add("Rectangle").update(x_max=10, y_max=4, y_min=-3,
                                        materialId=Base.cl.user_materials["PortAT2"]["id"])
        project.add("ArcWaveguide").update(innerRadius=8, outerRadius=12, rotate_z=10,
                                           materialId=Base.cl.user_materials["PortAT1"]["id"])

        project.add("EME")
        port = project.add("EmePort")

        xysize = [20, 20]
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_xlim((-xysize[0], xysize[0]))
        ax.set_ylim((-xysize[1], xysize[1]))

        for _ in project.__dict__["polygons"]:
            item = compromised_transform(_)
            ax.add_patch(item.__plot__())
        plt.show()

        attach_port(project, port, (10, 0))
        pprint(port.attrs)
        self.assertAlmostEqual(4, port['y_max'])
        self.assertAlmostEqual(-3, port['y_min'])

        project.save()


if __name__ == '__main__':
    unittest.main()
