from functools import wraps
from types import FunctionType
from maxoptics.utils.__visualizer__ import fillargs, arg_description

def __post__(func: FunctionType):
    @wraps(func)
    def wrapper(*args, **kws):
        self, *args = args
        if isinstance(self, FunctionType):
            __function__ = self

            @wraps(__function__)
            def wrapper(self, *args, **kws):
                suffix_in, __args = fillargs(func, args, kws)
                try:
                    # func(self, *args, **kws)
                    suffix_out = self.post(url=func.__name__, **suffix_in)
                    try:

                        if suffix_out["success"] is False:
                            print(func.__name__, " failed", f"{suffix_out = }")
                    except Exception as e:
                        print("Incorrect Response:", suffix_out)
                    kws.update(suffix_out["result"])
                    core_out = __function__(self, *args, **kws)
                    return fdict(core_out) | suffix_out["result"]
                except TypeError as e:
                    print("Input should be\n", "\n".join(map(lambda _: arg_description[_], __args)))
                    print(e)

            return wrapper
        else:  # TODO: add annotation
            result, __args = fillargs(func, args, kws)
            try:
                func(self, *args, **kws)  # Check whether fit the args
                res = self.post(url=func.__name__, **result)
                try:
                    if res["success"] is False:
                        print(func.__name__, " failed", f"{res = }")
                except Exception as e:
                    print("Incorrect Response:", res)

                return res["result"]
            except TypeError as e:
                print("Input should be\n", "\n".join(map(lambda _: arg_description[_], __args)))
                print(e)

    return wrapper
