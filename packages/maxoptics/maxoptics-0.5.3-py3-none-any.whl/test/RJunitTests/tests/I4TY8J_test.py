from .base import *

# structure设置新值，structure使用默认值
# https://e.gitee.com/max-optics/issues/kanban/members?issue=I4TY8J



class I4TY8JTestCase(unittest.TestCase):
    def test_ArcWaveguide(self):
        _ = Base.pr.add("ArcWaveguide")
        with self.assertRaises(KeyError) as err:
            _["x_min"]
        with self.assertRaises(KeyError) as err:
            _["x_max"]
        with self.assertRaises(KeyError) as err:
            _["y_min"]
        with self.assertRaises(KeyError) as err:
            _["y_max"]

    def test_BezierCurve(self):
        _ = Base.pr.add("BezierCurve")
        with self.assertRaises(KeyError) as err:
            _["x_min"]
        with self.assertRaises(KeyError) as err:
            _["x_max"]
        with self.assertRaises(KeyError) as err:
            _["y_min"]
        with self.assertRaises(KeyError) as err:
            _["y_max"]

    def test_Circle(self):
        _ = Base.pr.add("Circle")
        with self.assertRaises(KeyError) as err:
            _["x_min"]
        with self.assertRaises(KeyError) as err:
            _["x_max"]
        with self.assertRaises(KeyError) as err:
            _["y_min"]
        with self.assertRaises(KeyError) as err:
            _["y_max"]

    def test_Ellipse(self):
        _ = Base.pr.add("Ellipse")
        with self.assertRaises(KeyError) as err:
            _["x_min"]
        with self.assertRaises(KeyError) as err:
            _["x_max"]
        with self.assertRaises(KeyError) as err:
            _["y_min"]
        with self.assertRaises(KeyError) as err:
            _["y_max"]

    def test_LinearTrapezoid(self):
        _ = Base.pr.add("LinearTrapezoid")
        with self.assertRaises(KeyError) as err:
            _["x_min"]
        with self.assertRaises(KeyError) as err:
            _["x_max"]
        with self.assertRaises(KeyError) as err:
            _["y_min"]
        with self.assertRaises(KeyError) as err:
            _["y_max"]

    def test_Rectangle(self):
        _ = Base.pr.add("Rectangle")
        self.assertIsInstance(_["x_min"], float)
        self.assertIsInstance(_["x_max"], float)
        self.assertIsInstance(_["y_min"], float)
        self.assertIsInstance(_["y_max"], float)

    def test_Ring(self):
        _ = Base.pr.add("Ring")
        with self.assertRaises(KeyError) as err:
            _["x_min"]
        with self.assertRaises(KeyError) as err:
            _["x_max"]
        with self.assertRaises(KeyError) as err:
            _["y_min"]
        with self.assertRaises(KeyError) as err:
            _["y_max"]

    def test_SCurve(self):
        _ = Base.pr.add("SCurve")
        with self.assertRaises(KeyError) as err:
            _["x_min"]
        with self.assertRaises(KeyError) as err:
            _["x_max"]
        with self.assertRaises(KeyError) as err:
            _["y_min"]
        with self.assertRaises(KeyError) as err:
            _["y_max"]

    def test_Sector(self):
        _ = Base.pr.add("Sector")
        with self.assertRaises(KeyError) as err:
            _["x_min"]
        with self.assertRaises(KeyError) as err:
            _["x_max"]
        with self.assertRaises(KeyError) as err:
            _["y_min"]
        with self.assertRaises(KeyError) as err:
            _["y_max"]

    def test_Triangle(self):
        _ = Base.pr.add("Triangle")
        with self.assertRaises(KeyError) as err:
            _["x_min"]
        with self.assertRaises(KeyError) as err:
            _["x_max"]
        with self.assertRaises(KeyError) as err:
            _["y_min"]
        with self.assertRaises(KeyError) as err:
            _["y_max"]

    def test_CustomPolygon(self):
        _ = Base.pr.add("CustomPolygon")
        with self.assertRaises(KeyError) as err:
            _["x_min"]
        with self.assertRaises(KeyError) as err:
            _["x_max"]
        with self.assertRaises(KeyError) as err:
            _["y_min"]
        with self.assertRaises(KeyError) as err:
            _["y_max"]


if __name__ == '__main__':
    unittest.main()
