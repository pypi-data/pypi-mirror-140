from collections import defaultdict
from copy import deepcopy
from json.decoder import JSONDecodeError
import pandas as pd
import numpy as np
import os
from maxoptics.component import EmptyComponent, ProjectComponent
from maxoptics.config import BASEDIR
from maxoptics.error import InvalidInputError
from .gdstools import GdsParser
from maxoptics.utils.__pyfuture__ import fdict
from maxoptics.autogen import ClassColle

from maxoptics.utils.base import classifier, error_print, info_print, printf, warn_print

from functools import singledispatchmethod
from typing import Any, Awaitable, Callable

class MosProject(object):
    """
    Project Class, for basic structure/simulation addition, project configuration and so on
    """

    def __init__(self, parent, token, name="Any", project_type="passive"):
        from maxoptics.sdk import MaxOptics

        self.id: int
        self.version: str
        self.__parent__: MaxOptics = parent
        self.token: str = token
        self.name: str = name
        self.type: str = project_type
        self.solver_name: str = ""
        self.solver_type: str = ""
        self.components: dict[str, ProjectComponent] = defaultdict(lambda: EmptyComponent())
        self.appendix: dict[str, ProjectComponent] = {}
        self.tasks: list[dict] = []
        self.running_tasks: list[Any] = []
        self.ports: list[ProjectComponent] = []
        self.monitors: list[ProjectComponent] = []
        self.solver: ProjectComponent = EmptyComponent(intended=True)
        self.sources: list[ProjectComponent] = []
        self.port_groups: list[ProjectComponent] = []
        self.polygons: list[ProjectComponent] = []
        self.others: list[ProjectComponent] = []
        self.DOCUMENT: ProjectComponent = self.add("Document")

    def resize(self, w=None, h=None, dx=None, dy=None):
        """Soon will expire.
        Resize the canvas of project.
        You can write those attributes directly into `DOCUMENT` of project now, so you should never use this method.
        """

        class VerificationError(Exception):
            def __init__(self, msg="", code=0):
                self.msg = msg
                self.code = code

        def verify(num):
            if num is None:
                return
            if num < 0:
                raise VerificationError(msg="Input cannot be negative!")
            if num == 0:
                raise VerificationError(msg="Input cannot be zero!")
            # More
            return num

        try:
            if verify(w):
                self.DOCUMENT["attrs"]["w"] = w
            if verify(h):
                self.DOCUMENT["attrs"]["h"] = h
            if verify(dx):
                self.DOCUMENT["attrs"]["drawGrid"]["dx"] = dx
            if verify(dy):
                self.DOCUMENT["attrs"]["drawGrid"]["dy"] = dy
        except VerificationError as e:
            error_print(e.msg)
            return
        return

    def add(self, class_name, name="") -> ProjectComponent:
        """Add a component to this project.
        Where this component will be attached will be determined by its `belong2` attribute.
        Most of component will be attached to `DOCUMENT` component, which is created with project simultaneously`

        Args:
            class_name (str): The type of the component.
            name (str, optional): The name of the component. Defaults to "".

        Raises:
            InvalidInputError: A unknown type is given.
            NotImplementedError: This component is not supported in this project yet.
            NotImplementedError: [description]
            e: JSONDecodeError
            e: Unknown error

        Returns:
            ProjectComponent: The added component.
        """
        try:
            curr_components = os.listdir(BASEDIR / "autogen")
            curr_components = list(
                map(lambda _: _[:-5] if _.endswith(".json") or _.endswith(".yaml") else _, curr_components)
            )
            if not "__CONCRETE__" + class_name in curr_components:
                curr_components_upper = list(map(lambda _: _.upper(), curr_components))
                if "__CONCRETE__" + class_name.upper() in curr_components_upper:
                    _ind = curr_components_upper.index("__CONCRETE__" + class_name.upper())
                    class_name = (
                        curr_components[_ind][len("__CONCRETE__") - 1 :]
                        if curr_components[_ind].startswith("__CONCRETE__")
                        else curr_components[_ind]
                    )
                else:
                    info_print(f"Not supported component: {class_name = }")
                    raise InvalidInputError()

            __cls__ = ClassColle.new("__CONCRETE__" + class_name)
            __belong2__ = ClassColle.belongs["__CONCRETE__" + class_name][self.type]
            if not __belong2__:
                error_print(f"The component {class_name} cannot be added to {self.type} project")
                raise NotImplementedError
            name = name or class_name
            while True:
                if name in self.components:
                    name += " copy"
                else:
                    break
            c = __cls__(name)
            class_type = classifier(class_name, c)
            try:
                getattr(self, class_type).append(c)
            except:
                setattr(self, class_type, c)

            self.components[name] = c
            if "$" in __belong2__[-1]:
                plc = str(__belong2__[0]).split("<----")[-1]
                self.appendix[plc] = c
                return c

            elif "." in __belong2__:
                error_print("NotImplemented")
                raise NotImplementedError()

            elif "*" in __belong2__ and class_name == "MatrixSweep":
                if class_name == "MatrixSweep":
                    self.DOCUMENT["attrs"]["sweep"] = {self.solver_type.lower(): c}
                    self.DOCUMENT["attrs"]["tarSweep"] = [
                        str(self.solver_type.lower()),
                        str(self.solver.id),
                    ]
                return c

            else:
                all_component = list(
                    map(
                        lambda _: (
                            self.components[_].__class__.__name__,
                            self.components[_].name,
                        ),
                        self.components,
                    )
                )
                __matches = list(filter(lambda _: _[0] in __belong2__, all_component))
                if len(__matches) == 1:
                    __match = __matches[0]
                    the_component = self.components[__match[1]]
                    the_component.adopt_component(c)
                else:
                    if len(__matches) == 0:
                        error_print(f"Please Check Prerequisite: {__belong2__} Added")
                    else:

                        matched_components = [i[1] for i in __matches]
                        warn_print(f"Multiple prerequisite object founded: {matched_components}")
                        while True:
                            res = input("Add to which? :")
                            res = res.strip().strip("'").strip('"')
                            if res in self.components:
                                the_component = self.components[res]
                                the_component.adopt_component(c)
                                break
                            else:
                                warn_print("Object not found (press Ctrl+C to exit)")
                if class_name in ["FDE", "FDTD", "EME"]:
                    self.solver_type = class_name
                    self.solver = self.components[name]
                    self.DOCUMENT["attrs"]["tarSrc"]["type"] = class_name
                    self.DOCUMENT["attrs"]["tarSrc"]["id"] = c.id
                return c
        except JSONDecodeError as e:
            error_print("Broken Model File!")
            raise e
        except Exception as e:
            import traceback

            traceback.print_exc()
            error_print("System Error!", e)
            raise e

    def getItemByName(self, name):
        """ """
        res = self.components[name]
        if res is None:
            import traceback

            error_print("No component with name", name)
            traceback.print_exc()
            raise InvalidInputError
        return res

    def __getitem__(self, name: str):
        return self.getItemByName(name)

    def __setitem__(self, name: str, value: Any):
        self.components[name] = value

    def formatComponents(self):
        self.appendix = dict(self.appendix)
        _appendix = {}
        try:
            for k in self.appendix:
                if bool(self.appendix[k]):
                    if (
                        ProjectComponent in self.appendix[k].__class__.__mro__
                        and "export" in self.appendix[k].__dir__()
                    ):
                        _appendix[k] = self.appendix[k].export
                    else:
                        _appendix[k] = self.appendix[k]

        except AssertionError:
            error_print("Project save failed, %s" % "because of setattr failure")
            raise InvalidInputError()
        else:
            data = {
                "history": {"steps": [], "cursor": 0},
                "result": [],
            }
            data.update(_appendix)

            return data

    def export(self, name: str = None, format="json"):
        self.__parent__.export_project(self, name, format=format)

    def save(self):
        return self.__parent__.save_project(self)

    def run(self, task_type=None, project_type="", __timeout__=-1, *args, **kwargs):
        return self.__parent__.create_task(self, task_type, project_type, __timeout__, *args, **kwargs)

    def asyrun(self, task_type=None, mode="", __timeout__=0, *args, **kwargs):
        return self.__parent__.async_create_task(self, task_type, mode, __timeout__, *args, **kwargs)

    def gds_import(self, gdsfile, cellname, layer, material, zmin, zmax):
        model = GdsParser.GdsModel(self, self.__parent__)
        return model.gds_import(gdsfile, cellname, layer, material, zmin, zmax)

    def add_polygon(self, points):
        model = GdsParser.GdsModel(self, self.__parent__)
        return model.gen_polygon(points)


class TaskFile:
    def __init__(self, data, task, *args, **kwargs):
        self.task_id = task.task_id
        self.task = task
        self.raw_data = data
        self.args = args
        self.kwargs = kwargs
        self.data_type = str(kwargs.get("target") or args[0])
        for thing in data:
            setattr(self, thing, data[thing])

        if "table" in self.data_type.lower():
            self.columns = self.raw_data.get("header") or self.raw_data.get("columns")
            self.index = self.raw_data.get("index") or None
            self.index_label = self.raw_data.get("index_label") or None

        elif "line" in self.data_type.lower():
            self.data = np.transpose(self.raw_data["data"])
            legends = self.raw_data.get("legend") or self.raw_data.get("columns") or ["data"]
            self.columns = legends
            self.index = self.raw_data.get("horizontal") or self.raw_data.get("index")
            self.index_label = self.raw_data.get("index_label") or None

        elif "intensity" in self.data_type.lower():
            self.columns = self.raw_data.get("dWidth") or self.raw_data.get("columns")
            self.index = self.raw_data.get("dHeight") or self.raw_data.get("index")
            self.index_label = self.raw_data.get("index_label") or None

        else:
            print("Invalid target type!")
            print(self.data_type)
            raise InvalidInputError

    @property
    def DataFrame(self):
        df = pd.DataFrame().from_records(data=self.data, columns=self.columns)
        df.index = self.index
        return df

    # TODO: def __enter__(self):

    # TODO: def __exit__(self):

    # TODO: def __del__(self):


class JSasync:
    """ """

    def __init__(self, waiting4: Awaitable, runnow: Callable) -> None:
        self.waiting4 = waiting4
        self.runnow = runnow
        self.successor = None

    @property
    def dest(self):
        return self.successor.dest if self.successor else self.__await__()

    def then(self, f) -> Any:
        self.func = f

        async def func():
            result = await self.waiting4
            return self.func(result)

        self.successor = JSasync(func(), self.runnow)
        return self.successor

    def now(self):
        return self.runnow()

    def __await__(self):
        return self.waiting4

