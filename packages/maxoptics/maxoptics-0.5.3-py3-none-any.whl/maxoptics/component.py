# coding=utf-8
from pathlib import Path
from turtle import position

from numpy import angle
from maxoptics.config import Config
from maxoptics.utils.base import (
    info_print,
    warn_print,
    success_print,
    error_print,
    nearest_words_with_damerau_levenshtein_distance,
)
from typing import Any
from maxoptics.constraints.router import general_res
from maxoptics.utils.__pyfuture__ import fstr

BETA = Config.BETA


class ProjectComponent:
    """A basic class that will be inherited by all components.

    Args:
        metaclass (ABCMeta, optional): Abstract Basic Class. Defaults to ABCMeta.
    """

    def __init__(self):
        """Add some basic attributes."""
        self.children = []
        self.locked = False
        self.disabled = False
        self.id = ""
        self.name = ""

    def showInfo(self):
        """Show informations in this component."""
        pass

    def adopt_component(self, component):
        """Add component to `children` attribute

        Args:
            component (ProjectComponent): A component.
        """
        # TODO: add assert
        self.children.append(component)

    @property
    def export(self):
        """Tidy up attributes and form a dictionary.

        Returns:
            dict: A serializable object for output.
        """
        result = dict(self.__dict__)

        def clean(d: dict):
            """Remove excrescent key-value. Transform components in `children` into dictionaries too.

            Args:
                d (dict): To be clean.

            Returns:
                dict: The cleaned.
            """
            for k in list(d.keys()):
                if k.startswith("__") or k == "showInfo" or k == "_abc_impl":
                    d.pop(k)

            for k in list(d.keys()):
                v = d[k]
                if isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
                    continue
                try:
                    d[k] = v.export
                except:
                    try:
                        d[k] = [_.export for _ in v]
                    except:
                        pass
                try:
                    d[k] = clean(d[k])
                except:
                    pass
            return d

        result = clean(result)
        for k in list(result.keys()):
            if k.startswith("__") or k == "showInfo" or k == "_abc_impl":
                result.pop(k)

        if not "__dirty__" in self.__dict__:
            self.__dirty__ = False
        else:
            # assert not self.__dirty__
            pass
        return result

    def get(self, name, silent=False):
        """Get method. Can get any leaf on the attribute tree.

        Args:
            name (str): The name of the attribute.
            silent (bool, optional): Whether to alert when the key was not found. Defaults to False.

        Returns:
            Any: The value.
        """
        attrs = {}
        flag = True

        def __extract(origin, name):
            nonlocal flag
            this_layer: list[dict] = []
            next_layer: list[dict] = [origin]
            while next_layer:
                this_layer = next_layer
                next_layer = []
                for dic in this_layer:
                    if name in dic:
                        return dic[name]
                    for v in dic.values():
                        if isinstance(v, dict):
                            next_layer.append(v)
            flag = False

        res = __extract(self.export, name)
        if flag:
            return res
        else:
            if silent:
                return
            else:
                error_print("A Invalid value retrieval, inputs are {}".format(name))
                raise KeyError("A Invalid value retrieval, inputs are {}".format(name))

    def set(self, name: str, value, escape=None) -> None:
        """Set method. Can set any leaf on the attribute tree.

        Args:
            name (str): The key.
            value (Any): The value.
            escape (list, optional): If `'*'` in escape, no constrain will be checked. Otherwise, any key in escape will be ignored while checking constrains. Defaults to None.

        Returns:
            None: No return.
        """

        flag = {"flag": False}

        def __assign(origin, name, value, flag):
            this_layer: list[dict] = []
            next_layer: list[dict] = [origin]
            while next_layer:
                this_layer = next_layer
                next_layer = []
                for dic in this_layer:
                    if name in dic:
                        flag["flag"] = True
                        dic[name] = value
                    for v in dic.values():
                        if isinstance(v, dict):
                            next_layer.append(v)
            return

        if name != "__dirty__":
            try:
                trees = [self.export]
                trees[0].pop("children")
                for tree in trees:
                    __assign(tree, name, value, flag)

            except Exception as e:
                print("Sth wrong1", e)
                import traceback

                traceback.print_exc()
            if not flag["flag"]:
                self.__dirty__ = True
                warn_print(
                    '\rInput is "{}"\nMost likely you want to input one of  {} \n'.format(
                        name, nearest_words_with_damerau_levenshtein_distance(self.export, "".join(name))
                    )
                )
            else:
                if escape is None:
                    new_escape = []
                    new_escape.append(name)
                    if BETA:
                        print("escape is None", name)
                    general_res.check(self, name, new_escape)
                else:
                    if BETA:
                        print("escape is not None", escape)
                    if name not in escape:
                        escape.append(name)
                    general_res.check(self, name, escape)
        else:
            self.__dict__[name] = value
            return super().__setattr__(name, value)

    def update(self, *args, **kwargs) -> None:
        """Just like `dict.update`."""
        for arg in args:
            if not isinstance(arg, dict):
                error_print("Wrong input type !!! Dict needed")
                self.__dirty__ = True
                return
            else:
                kwargs.update(arg)
        for key in kwargs:
            self.set(key, kwargs[key])

    def __getitem__(self, name) -> Any:
        """Alias of `get`

        Args:
            name (str): Key.

        Returns:
            Any: Value.
        """
        return self.get(name, silent=False)

    def __setitem__(self, name: str, value: Any):
        """Alias of `set`

        Args:
            name (str): Key.
            value (Any): Value.
        Returns:
            None.
        """
        return self.set(name, value)

    def check_status(self):
        return self.__dirty__

    def list_all_dict(self, dict_a, level):
        """
        Print the __dict__ as a tree form
        """
        level += 1
        if isinstance(dict_a, dict):
            # if level != 1:
            print("")
            for x in range(len(dict_a)):
                temp_key = list(dict_a.keys())[x]
                info_print("-" * 3 * level + ">", end=" ")
                info_print(temp_key, end=" ")
                print(":", end=" ")
                temp_value = dict_a[temp_key]
                self.list_all_dict(temp_value, level)
        elif isinstance(dict_a, list):
            if len(dict_a) == 0:
                print("[]")
            for x in range(len(dict_a)):
                self.list_all_dict(dict_a[x], level)
            print("")
        else:
            # print(dict_a)
            pass

    def formatComponents(self):
        pass


class Structure(ProjectComponent):
    """Expired"""

    def __init__(self):
        super(Structure, self).__init__()

    def showInfo(self):
        """ """
        self.list_all_dict(self.__dict__, 0)

    # @abstractmethod
    def validate(self):
        """ """
        pass


class Simulation(ProjectComponent):
    """Expired"""

    def __init__(self):
        super(Simulation, self).__init__()

    def showInfo(self):
        """ """
        # print('NotImplemented!')
        try:
            print(self.export)
        except:
            print(self.__dict__)
        pass


class Port(Simulation):
    def __init__(self):
        super(Port, self).__init__()


class Solver(ProjectComponent):
    """Expired"""

    def __init__(self):
        super(Solver, self).__init__()

    def showInfo(self):
        """ """
        # print('暂未实现！')
        try:
            print(self.export)
        except:
            print(self.__dict__)
        pass


class EmptyComponent(ProjectComponent):
    """A `ProjectComponent` that `__bool__` returns `False`."""

    def __init__(self, intended=False):
        super().__init__()
        if not intended:
            error_print("A empty project is referenced")

    def showInfo(self):
        ...

    # @abstractmethod
    def run(self, mode="t", task_type=None):
        ...

    def __repr__(self) -> str:
        return (
            "This is a invalid component that will only show up when a non-existed project component name is referenced"
        )

    def __bool__(self) -> bool:
        return False

    def export(self):
        return None


class OpticalPort:
    def __init__(self, name, position, angle) -> None:
        self.name = name
        self.position = position
        self.angle = angle

    def __align__(self, project):
        solver_type = project.solver_type
