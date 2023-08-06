from .base import *

structures = [
    "ArcWaveguide",
    "BezierCurve",
    "Circle",
    "Ellipse",
    "LinearTrapezoid",
    "Rectangle",
    "Ring",
    "SCurve",
    "Sector",
    "Triangle",
    "CustomPolygon",
]


# overrideMeshOrder字段的自动处理
# https://e.gitee.com/max-optics/issues/kanban/members?issue=I4TZAP
class MyTestCase(unittest.TestCase):
    def test_overrideMeshOrder(self):
        for i in structures:
            pprint(i)
            j = Base.pr.add(i)
            self.assertEqual(0, j["overrideMeshOrder"])
            j["meshOrder"] = 2
            self.assertEqual(1, j["overrideMeshOrder"])


if __name__ == '__main__':
    unittest.main()
