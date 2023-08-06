from collections import defaultdict
from maxoptics.error import InvalidInputError
from maxoptics.utils.base import error_print
import inspect
from typing import Any, List

arg_description = defaultdict(
    None,
    {
        "monitor_index": "int; start with 0; 监视器索引",
        "freq_index": "int; start with 0; 频率索引值",
        "time_index": "int; start with 0; 时间索引值",
        "mode_index": "int; 模式索引",
        "field": 'str; 分量: "*", "E*", "H*", "Ex", "Ey", "Ez"," Hx", "Hy", "Hz", "H", "E", "Px", "Py", "Pz", "Energy tensity"',
        "type": 'str; "amplitude", "phase", "Real", "Imaginary"',
        "plot": 'str; 以某一维度为横轴因变量，可选值："time" / "x" / "y" / "z"',
        "slice": '选中一维做plot，则其他维度就要做切片:\n默认值为0，为1则为选中 {"time_index": 0, "x_index": 0, "y_index": 0, "z_index": 0}',
        "log": "bool; 是否取对数（以10为底数）",
        "img": "bool; 是否导出为图片",
    },
)
arg_description.update(
    {
        "option": '请求参数, 包含{"mode_index": , "field": , "type": , "log": False, "img": False}\n'
        + "\n".join(["-- " + s + ":" + arg_description[s] for s in ["mode_index", "field", "type", "log", "img"]])
    }
)


def fillargs(f, args, kws):
    spec = inspect.getargspec(f)
    __args = spec.args[1:]
    print(spec.args)  # RM
    __defaults = spec.defaults
    result = dict().fromkeys(__args)
    # Default values
    __values = __args[::-1]
    __defaults = __defaults[::-1] if __defaults else []
    for i in range(len(__defaults)):
        result[__values[i]] = __defaults[i]

    for i in range(len(args)):
        result[__args[i]] = args[i]

    for k in result:
        if k in kws:
            result[k] = kws[k]

    return result, __args


class Index:
    def __init__(self, project) -> None:
        self.project = project

    def __call__(self, index_info) -> Any:
        from maxoptics.models import ProjectComponent

        if isinstance(index_info, int):
            return index_info
        elif isinstance(index_info, ProjectComponent):
            _component = index_info
            shift = 0
            if _component in self.project.monitors:
                return shift + self.project.monitors.index(_component)
            shift += len(self.project.monitors)

            if _component in self.project.ports:
                return shift + self.project.ports.index(_component)

            error_print("This component can't be filled to result visualizer's methods")
            raise InvalidInputError()
        else:
            error_print(f"Got an unexpected input: {index_info}")
            raise InvalidInputError()
