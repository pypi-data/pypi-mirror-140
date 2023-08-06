from maxoptics.utils.__pyfuture__ import fdict
from maxoptics.utils.__visualizer__ import arg_description, fillargs

from typing import Callable
from functools import wraps
import inspect


def __post__(func: Callable):
    @wraps(func)
    def wrapper(*args, **kws):
        self, *__args__ = args

        try:
            # Check whether fit the args
            result = self.post(url=func.__name__, **func(*args, **kws))

            if result.get("success") is False:
                print(func.__name__, " failed", f"{result = }")
                print("Incorrect response:", result)

            return result["result"]

        except TypeError as e:
            # print("Input should be\n", "\n".join(
            #     map(lambda _: arg_description[_], __args)))
            print(e)

        return func(self, *args, **kws)

    return wrapper


def data_parser(func: Callable):
    from maxoptics.models import TaskFile

    @wraps(func)
    def wrapper(*args, **kws):
        self, *__args__ = args
        # __kwargs__, __args = fillargs(func, args, kws)
        return TaskFile(
            func(*args, **kws),
            self,
            *__args__,
            **(
                fdict(kws)
                | (
                    dict(zip(inspect.getfullargspec(func).args[::-1], inspect.getfullargspec(func).defaults))
                    if bool(inspect.getfullargspec(func).defaults)
                    else {}
                )
            ),
        )

    return wrapper
