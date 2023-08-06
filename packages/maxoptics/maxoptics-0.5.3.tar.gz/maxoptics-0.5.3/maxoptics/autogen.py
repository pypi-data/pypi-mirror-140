from pathlib import Path
import os
from collections import defaultdict
from pprint import pp
from typing import Mapping
import yaml
from copy import deepcopy

from maxoptics.utils.base import error_print
from maxoptics.component import ProjectComponent
from maxoptics.config import BASEDIR
from maxoptics.utils.__pyfuture__ import fdict
import uuid


def init_method(self, name, __reserve__={}):
    """A overload `Constructor` for recursive inherition.

    Args:
        name (str): Class name.
        __reserve__ (dict, optional): `__dict__` of super class. Default values in super class overwrite those in junior class. Defaults to {}.
    """
    __reserve__ = __reserve__ or self.__class__.__dict__
    for k, v in __reserve__.items():
        try:
            setattr(self, k, deepcopy(v))
        except:
            setattr(self, k, v)

    self.name = name
    self.id = str(uuid.uuid4())


def showInfo(self):
    """Print all Info."""
    self.list_all_dict(self.__dict__, 0)


class __ClassColle:
    """`A collection of components. The real useful object is the instance of this class `ClassColle`(see the end of file).

    Raises:
        FileNotFoundError: File not found.

    Returns:
        object: A instance filled with components' information.
    """

    basedir = BASEDIR / "autogen"
    colle = {}
    belongs = defaultdict(lambda: defaultdict(lambda: []))

    def __init__(self) -> None:
        """Collect all models files in ./autogen dir, form name-path pair for later use."""
        if os.path.exists(self.basedir):
            for fn in os.listdir(self.basedir):
                fp = self.basedir / fn
                fn = fn[:-5]
                self.colle[fn] = fp
        else:
            error_print("The 'autogen' dir is missing, please consider reinstall this library")

    def new(self, name: str):
        """Create a component object.

        Args:
            name (str): The name of component.

        Raises:
            FileNotFoundError: This component is not founded in library.

        Returns:
            ProjectComponent: A component class, can be polygen, monitor, solver, etc. For use, initialization need.
        """
        if not self.colle[name]:
            raise FileNotFoundError()

        # The Component is still recorded as path to component base files
        if isinstance(self.colle[name], str) or isinstance(self.colle[name], Path):
            self.__retrive(name)

        # The Component is recorded as a tuple (class_name, orm, dict) for `type()` invoke
        if isinstance(self.colle[name], list):

            this = self.colle[name]
            supers = list(this[1])
            this_dict = this[2]
            this_dict["showInfo"] = showInfo
            this_dict["__init__"] = init_method
            for i in range(len(supers)):
                sup = supers[i]
                if sup == "__object__":
                    supers[i] = ProjectComponent
                else:
                    supers[i] = self.new(sup)
                    if "type" in this_dict:
                        this_dict["type"].update(supers[i].__dict__)
                    elif "base" in this_dict:
                        this_dict["base"].update(supers[i].__dict__)

                    if "attrs" in supers[i].__dict__:
                        this_dict["attrs"].update(supers[i].__dict__["attrs"])
            this[1] = tuple(supers)
            self.colle[name] = type(*this)
        return self.colle[name]

    def __retrive(self, name):
        """Turn path-to-file to base information

        Args:
            name (str): Name of component.
        """
        # TODO: record basic information into a `dataclass` instead of a tuple
        assert self.colle[name]
        fp = self.colle[name]
        with open(fp, "r") as f:
            obj = yaml.load(f, yaml.SafeLoader)
            name = obj["name"]
            mros = obj["mros"]
            belong = obj["belong"]
            attributes = obj["attributes"]
            self.colle[name] = [name, mros, attributes]
            self.belongs[name] = defaultdict(lambda: [], belong)

    def inject(self, name, mros, attrs={}, __belong2="", **kws):
        """Update on base files.

        Args:
            name (str): Component name.
            mros (list): `Method Resolution Order`.
            attrs (dict, optional): Attributes. Defaults to {}.
            __belong2 (str, optional): Get current tree from a larger tree. This string record its root. Defaults to "".

        Returns:
            [type]: [description]
        """
        print(f"Update on {name}")

        def merge_dict(d1: dict, d2: dict):
            """Merge two dict elementwisely.

            Args:
                d1 (dict): Input dict one.
                d2 (dict): Input dict two.

            Returns:
                dict: The merged dict.
            """
            # TODO: instead of returning the merged dict, replace dict 1 inplace
            output = dict()
            for k in set(list(d1.keys()) + list(d2.keys())):
                if k not in d1:
                    output[k] = d2[k]
                elif k not in d2:
                    output[k] = d1[k]
                else:
                    if isinstance(d1[k], (list, int, str, float, tuple)) and isinstance(
                        d2[k], (list, int, str, float, tuple)
                    ):
                        output[k] = d1[k]
                    elif isinstance(d1[k], dict) and isinstance(d2[k], dict):
                        output[k] = merge_dict(d1[k], d2[k])
                    elif isinstance(d1[k], type(d2[k])):
                        output[k] = d1[k]
                    else:
                        print(k, "TypeError!\nBetween:\n", d1[k], "\n", d2[k])
                        # raise TypeError
                        uin = input("Overwrite?(y/n):")
                        if uin in ["y", "Y", "yes"]:
                            output[k] = d2[k]
                        elif uin in ["n", "N", "no"]:
                            output[k] = d1[k]
                        else:
                            print("Aborted.")
                            exit(0)

            return output

        # Merge it with a old file
        if name in self.colle:
            # List: prepared, pathlike: raw file
            if not isinstance(self.colle[name], list):
                self.__retrive(name)
            # self.colle[name][-1].update(fdict(attrs) | kws)
            self.colle[name][-1] = merge_dict(self.colle[name][-1], fdict(attrs) | kws)
            if __belong2:
                project_type, root = __belong2
                if root not in self.belongs[name][project_type]:  # defaultdict
                    self.belongs[name][project_type].append(root)

        # Create a brand new file
        else:
            self.colle[name] = [name, mros, fdict({"name": name}) | attrs | kws]
            if __belong2:
                project_type, root = __belong2
                self.belongs[name][project_type].append(root)

    def rmredundancy(self):
        """Clean up components' base files."""
        for cl in self.colle:
            if isinstance(self.colle[cl], Path):
                continue
            for k in list(self.colle[cl][2].keys()):
                try:
                    if "__delete__" in self.colle[cl][2][k]:
                        if isinstance(self.colle[cl][2][k], list):
                            self.colle[cl][2][k] = []
                        elif isinstance(self.colle[cl][2][k], dict):
                            self.colle[cl][2][k] = {}
                except:
                    pass

    def store(self):
        """Store all components' information to yaml."""
        for cl in self.colle:
            if isinstance(self.colle[cl], Path):
                continue
            obj = self.colle[cl]
            belongs = self.belongs[cl]
            for k in belongs:
                belongs[k] = list(set(belongs[k]))
            with open(self.basedir / (cl + ".yaml"), "w") as f:
                yaml.dump(
                    {
                        "name": obj[0],
                        "mros": list(obj[1]),
                        "belong": dict(belongs),
                        "attributes": dict(obj[2]),
                    },
                    f,
                    Dumper=yaml.SafeDumper,
                )

    def available(self, name):
        """Check whether component is already loaded to self.colle.

        Args:
            name (str): Component_name.

        Returns:
            bool: Whether is loaded.
        """
        if name == "__object__":
            return True
        elif isinstance(self.colle[name], list):
            return False
        else:
            return True

    def restore(self):
        """Expired. In no case you should use this method."""
        for fp in map(lambda _: self.basedir / _, os.listdir(self.basedir)):
            with open(fp, "r") as f:
                obj = yaml.load(f, yaml.SafeLoader)
                name = obj["name"]
                mros = obj["mros"]
                belong = obj["belong"]
                attributes = obj["attributes"]
                self.colle[name] = [name, mros, attributes]
                self.belongs[name] = belong

        while True:
            rest_keys = filter(lambda k: isinstance(self.colle[k], list), self.colle)
            for cl in rest_keys:
                if all(map(lambda _: self.available(_), self.colle[cl][1])):
                    self.colle[cl] = type(*self.colle[cl])


ClassColle = __ClassColle()
