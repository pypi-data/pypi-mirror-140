from typing import Union
import dataclasses
import random
from typing import Literal
import weakref

from maxoptics.utils.__pyfuture__ import fdict
from maxoptics.utils.base import error_print

class MaterialPart:
    def __init__(self, material_info, client) -> None:
        self.name = material_info['name']
        self.id = material_info['id']
        self.mesh_order = material_info['mesh_order']
        self.client_weak_ref = weakref.WeakMethod(client.get_material_table_data)
        
        
    @property
    def table_data(self):
        method = self.client_weak_ref()
        if method:
            return method(self.id)['table_data']
        else:
            error_print("Client was destoried! Can not establish connection.")
        

@dataclasses.dataclass()
class Material:
    name: str
    index_table: dict
    conductivity: float = 0
    color: str = hex(random.randint(0, 256 ** 3))[2:].upper()
    type: str = "List data"
    mesh_order: int = 2
    temperature: float = 300.0
    dispersionflag: int = 1
    id: int = 0

    def __post_init__(self):
        if not self.index_table:
            print("Error: index_table can not be set as empty dict")
            raise ValueError()
        __keys = list(self.index_table.keys())
        for _ in __keys:
            if not isinstance(_, float):
                print("Error: keys of index_table must be float")
                raise ValueError()

        __values = list(self.index_table.values())
        __lengths = set(len(_) for _ in __values)
        if not len(__lengths) == 1:
            print("Error: length of values of index_table must be consistent")
            raise ValueError()

        __length = tuple(__lengths)[0]

        if __length == 0:
            print("Error: values of index_table can not be empty")
            raise ValueError()

        elif __length <= 2:
            self._table_name = f"{self.type}_indexes"
            self._table_head = [
                {"name": "Wavelength (\u03bcm)",
                 "type": "wavelength_frequency"},
                {"name": "Re (index)", "type": "re"},
                {"name": "Im (index)", "type": "im"},
            ]

        # elif __length == 18:
        #     self._table_name = f"anisotropy_data"
        #     self._table_head = [
        #         {"name": "Wavelength", "type": "wavelength_frequency"},
        #         {"name": "rexx  ", "type": "rexx"},
        #         {"name": "imxx  ", "type": "imxx"},
        #         {"name": "rexy  ", "type": "rexy"},
        #         {"name": "imxy  ", "type": "imxy"},
        #         {"name": "rexz  ", "type": "rexz"},
        #         {"name": "imxz  ", "type": "imxz"},
        #         {"name": "reyx  ", "type": "reyx"},
        #         {"name": "imyx  ", "type": "imyx"},
        #         {"name": "reyy  ", "type": "reyy"},
        #         {"name": "imyy  ", "type": "imyy"},
        #         {"name": "reyz  ", "type": "reyz"},
        #         {"name": "imyz  ", "type": "imyz"},
        #         {"name": "rezx  ", "type": "rezx"},
        #         {"name": "imzx  ", "type": "imzx"},
        #         {"name": "rezy  ", "type": "rezy"},
        #         {"name": "imzy  ", "type": "imzy"},
        #         {"name": "rezz  ", "type": "rezz"},
        #         {"name": "imzz  ", "type": "imzz"},
        #         {"name": "ConductivityX  ", "type": "conductivityX"},
        #         {"name": "ConductivityY  ", "type": "conductivityY"},
        #         {"name": "ConductivityZ  ", "type": "conductivityZ"},
        #     ]
        else:
            print("Error: length of values of index_table can not be " + str(__length))
            raise ValueError()

    def to_dict(self):
        return {
            "name": self.name,
            "color": self.color,
            "type": self.type,
            "mesh_order": self.mesh_order,
            "temperature": self.temperature,
            "dispersionflag": self.dispersionflag,
            "public": False,
            "id": self.id,
            "data": {
                "conductivity": self.conductivity
            }, "table_data": {
                self._table_name: fdict(
                    table_head=self._table_head
                ) | {str(k): v for k, v in self.index_table.items()}
            }
        }

    def to_dict2(self):
        return {
            "name": self.name,
            "color": self.color,
            "type": self.type,
            "mesh_order": self.mesh_order,
            "temperature": self.temperature,
            "dispersionflag": self.dispersionflag,
            "public": False,
            "id": self.id,
            "data": {
                "conductivity": self.conductivity
            },
            "tables": {
                "table_data": [
                    dict(zip(("wavelength_frequency", "re", "im")
                             , (str(k * 1000000), *v)
                             )) for k, v in self.index_table.items()
                ]
            }
        }


@dataclasses.dataclass()
class Waveform:
    name: str
    para1: float
    para2: float
    bandwidth: float
    offset: float
    pulselength: float
    input_field: Literal["frequency", "wavelength"] = "frequency"
    input_type: Literal["center_span", "start_stop"] = "center_span"
    id: int = 0

    def __post_init__(self):
        if not self.input_field in ["frequency", "wavelength"]:
            print('Error: input_field must be in ["frequency", "wavelength"]')
            raise ValueError()
        if not self.input_type in ["center_span", "start_stop"]:
            print('Error: input_type must be in ["center_span", "start_stop"]')
            raise ValueError()

        def c(_):
            return 299.792458 / _

        f = self.input_field
        t = self.input_type
        a = self.para1
        b = self.para2
        self._data = ((f == "frequency") and (t == "center_span") and {
            "center_frequency": a,
            "frequency_span": b,
            "center_wavelength": c(a),
            "wavelength_span": c(a - b / 2) - c(a + b / 2),
            "frequency_start": a - b / 2,
            "frequency_stop": a + b / 2,
            "wavelength_start": c(a + b / 2),
            "wavelength_stop": c(a - b / 2)
        }) or ((f == "wavelength") and (t == "center_span") and {
            "center_frequency": c(a),
            "frequency_span": c(a - b / 2) - c(a + b / 2),
            "center_wavelength": a,
            "wavelength_span": b,
            "frequency_start": c(a + b / 2),
            "frequency_stop": c(a - b / 2),
            "wavelength_start": a - b / 2,
            "wavelength_stop": a + b / 2
        }) or ((f == "frequency") and (t == "start_stop") and {
            "center_frequency": (a + b) / 2,
            "frequency_span": b - a,
            "center_wavelength": (c(a) + c(b)) / 2,
            "wavelength_span": c(a) - c(b),
            "frequency_start": a,
            "frequency_stop": b,
            "wavelength_start": c(b),
            "wavelength_stop": c(a)
        }) or ((f == "wavelength") and (t == "start_stop") and {
            "center_frequency": (c(a) + c(b)) / 2,
            "frequency_span": c(a) - c(b),
            "center_wavelength": (a + b) / 2,
            "wavelength_span": b - a,
            "frequency_start": c(b),
            "frequency_stop": c(a),
            "wavelength_start": a,
            "wavelength_stop": b
        })

    def to_dict(self):
        return {
            "name": self.name,
            "data": {
                "bandwidth": self.bandwidth,
                "offset": self.offset,
                "pulselength": self.pulselength,
                **self._data
            },
            "public": False,
            "id": self.id,
        }
