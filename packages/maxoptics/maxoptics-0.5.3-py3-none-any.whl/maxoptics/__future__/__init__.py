from maxoptics.sdk import MaxOptics
from maxoptics.models import MosProject
import inspect


class Cell(MaxOptics):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self._methods = inspect.getmembers(self, lambda _: inspect.ismethod(_) and (_.__name__ not in dir(__class__)))
        self._layouts = inspect.getmembers(
            self, lambda _: isinstance(_, LayoutView) and (_.__name__ not in dir(__class__))
        )
        print(self._methods, self._layouts)

    class Layout:
        NotImplemented


class LayoutView(MosProject):
    def __init__(self, parent, token, name="Any", project_type="passive"):
        super().__init__(parent, token, name, project_type)
        self.name = self.__class__.__name__


class OpticalPort:
    pass
