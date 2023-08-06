import inspect
import os
import sys
from pathlib import Path

try:
    __MAINPATH__ = Path(inspect.getfile(sys.modules.get("__main__"))).parent
    if os.path.exists(__MAINPATH__ / "maxoptics.conf"):
        __CONFIGPATH__ = __MAINPATH__ / "maxoptics.conf"
    elif os.path.exists(__MAINPATH__.parent / "maxoptics.conf"):
        __CONFIGPATH__ = __MAINPATH__.parent / "maxoptics.conf"
    elif os.path.exists(__MAINPATH__.parent.parent / "maxoptics.conf"):
        __CONFIGPATH__ = __MAINPATH__.parent.parent / "maxoptics.conf"
    else:
        ind = list(sys.modules.keys()).index("maxoptics")
        secondary_path = Path(inspect.getfile(list(sys.modules.values())[ind - 1]))
        if os.path.exists(secondary_path.parent / "maxoptics.conf"):
            __CONFIGPATH__ = secondary_path.parent / "maxoptics.conf"
        elif os.path.exists(secondary_path.parent.parent / "maxoptics.conf"):
            __CONFIGPATH__ = secondary_path.parent.parent / "maxoptics.conf"
        elif os.path.exists(secondary_path.parent.parent.parent / "maxoptics.conf"):
            __CONFIGPATH__ = secondary_path.parent.parent.parent / "maxoptics.conf"
        else:
            __CONFIGPATH__ = ''

except AttributeError:
    print("Warning: No __main__ modules found, using the default configuration")
    __CONFIGPATH__ = ""
    __MAINPATH__ = Path(".")

except TypeError:
    print("Warning: No __main__ modules found, using the default configuration")
    __CONFIGPATH__ = ""
    __MAINPATH__ = Path(".")

# Version Number
__VERSION__ = "0.5.3"


class MosLibrary:
    def __new__(cls, **kws):
        from .sdk import MaxOptics

        cls.mos_instance = MaxOptics(**kws)
        return cls.mos_instance
