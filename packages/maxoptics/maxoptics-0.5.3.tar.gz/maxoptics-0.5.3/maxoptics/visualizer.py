# coding=utf-8
from __future__ import annotations

# Data Parser
import json
# Env Parser
import os
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import ByteString

import numpy as np
import pandas as pd
# Functools
import requests
import urllib3

import maxoptics.utils.base as base
# MOS imports
from maxoptics.config import Config
from maxoptics.sdk import BaseClient
from maxoptics.utils.__visualizer__ import Index as _Index
from maxoptics.utils.decorators import __post__, data_parser

# Type Check

# Accessories

try:
    import readline
except:
    pass

BETA = Config.BETA


def get_task_handler(task_type):
    task_type = str(task_type).upper()
    if "FDE" in task_type:
        return FDEResultHandler
    elif "FDTD" in task_type:
        return FDTDResultHandler
    elif "INDEX" in task_type:
        return FDTDIndexResultHandler
    elif "EME" in task_type:
        return EMEResultHandler
    elif "MODE_EXPANSION" in task_type:
        return ModeExpansion
    elif "PD" in task_type:
        return PDResultHandler
    elif "MODULATOR" in task_type:
        return ModulatorResultHandler
    else:
        raise KeyError


class WhaleClients(BaseClient):
    def __init__(self, task_id, project):
        super().__init__("WhaleURLTemplate", "SERVERAPI", "SERVERPORT")
        self.task_id = task_id
        self.monitor_num = 0
        self.id = task_id
        self.status = 0
        self.base_params = {"token": self.token}
        self.post = partial(self.post, __base_params__=self.base_params)
        self.project = project

    @property
    def Index(self):
        return _Index(self.project)

    def check_status(self, quiet=False):
        if self.status == -2:
            print(f"Task {self.task_id} is stopped.")
            return False
        if self.status == -1:
            print(f"Task {self.task_id} is paused.")
            return False
        if self.status == 0:
            if not quiet:
                print(f"Task {self.task_id} is waiting.")
        if self.status == 1:
            if not quiet:
                print(f"Task {self.task_id} is running.")
        if self.status == 2:
            return True

    def update_status(self):
        url_template = Config.DragonURLTemplate
        api_address = Config.SERVERAPI
        port = Config.SERVERPORT
        api_url = url_template.format(api_address, port)  # Dragon url
        res = requests.post(
            api_url % ("get_tasks_status"),
            data=json.dumps({"token": Config.Token, "ids": [self.id]}),
            headers={"Content-Type": "application/json", "Connection": "close"},
        )
        self.status = json.loads(res.text)["result"][str(self.id)]

    def asFDE(self) -> FDEResultHandler:
        return self

    def asFDTD(self) -> FDTDResultHandler:
        return self

    def asFDTDINDEX(self) -> FDTDIndexResultHandler:
        return self

    def asEME(self) -> EMEResultHandler:
        return self

    def asPD(self) -> PDResultHandler:
        return self

    def asMOD(self) -> ModulatorResultHandler:
        return self

    @property
    def outpath(self):
        dirs = os.listdir(Config.OUTPUTDIR)
        folder_name = next(filter(lambda _: _.split("_")[-1] == str(self.task_id), dirs))
        return Config.OUTPUTDIR / folder_name


class V0_4_API(WhaleClients):
    api_version = "0.4"

    def fields(self):
        NotImplemented

    def dump_all(self):
        NotImplemented

    def sync_download(self):
        NotImplemented


class V0_3_API(WhaleClients):
    api_version = "0.3"

    def fields(self):
        NotImplemented

    def dump_all(self):
        NotImplemented

    def sync_download(self):
        NotImplemented


class FDTDResultHandler(V0_4_API):
    @__post__
    def passive_fdtd_fd_result_option(self, target: str, monitorIndex: int):
        return {"target": target, "pub": {"taskId": self.task_id, "monitorIndex": self.Index(monitorIndex)}}

    @data_parser
    @__post__
    def passive_fdtd_fd_result_chart(
        self, target: str, monitorIndex: int, attribute: str, operation: str, log=False, **kwargs
    ):
        return {
            "target": target,
            "pub": {  # pub
                "taskId": self.task_id,
                "monitorIndex": self.Index(monitorIndex),
                "attribute": attribute,
                "operation": operation,
                "log": log,
            },
            "option": kwargs,
        }

    @__post__
    def passive_fdtd_td_result_option(self, target: str, monitorIndex: int):
        return {"target": target, "pub": {"taskId": self.task_id, "monitorIndex": self.Index(monitorIndex)}}

    @data_parser
    @__post__
    def passive_fdtd_td_result_chart(
        self, target: str, monitorIndex: int, attribute: str, operation: str, log=False, **kwargs
    ):
        return {
            "target": target,
            "pub": {  # pub
                "taskId": self.task_id,
                "monitorIndex": self.Index(monitorIndex),
                "attribute": attribute,
                "operation": operation,
                "log": log,
            },
            "option": kwargs,
        }

    @__post__
    def passive_fdtd_sweep_option(self, target: str, monitorIndex: int):
        return {"target": target, "pub": {"taskId": self.task_id, "monitorIndex": self.Index(monitorIndex)}}

    @data_parser
    @__post__
    def passive_fdtd_sweep_chart(
        self, target: str, monitorIndex: int, attribute: str, operation: str, log=False, **kwargs
    ):
        return {
            "target": target,
            "pub": {  # pub
                "taskId": self.task_id,
                "monitorIndex": self.Index(monitorIndex),
                "attribute": attribute,
                "operation": operation,
                "log": log,
            },
            "option": kwargs,
        }


class FDTDIndexResultHandler(V0_4_API):
    @__post__
    def passive_fdtd_index_monitor_option(self, target: str, monitorIndex: int):
        return {"target": target, "pub": {"taskId": self.task_id, "monitorIndex": self.Index(monitorIndex)}}

    @data_parser
    @__post__
    def passive_fdtd_index_monitor_chart(
        self, target: str, monitorIndex: int, attribute: str, operation: str, log=False, **kwargs
    ):
        return {
            "target": target,
            "pub": {  # pub
                "taskId": self.task_id,
                "monitorIndex": self.Index(monitorIndex),
                "attribute": attribute,
                "operation": operation,
                "log": log,
            },
            "option": kwargs,
        }


class FDEResultHandler(V0_4_API):
    @__post__
    def passive_fde_options(self, target: str, monitorIndex: int):
        return {"target": target, "pub": {"taskId": self.task_id, "monitorIndex": self.Index(monitorIndex)}}

    @data_parser
    @__post__
    def passive_fde_result_chart(
        self, target: str, monitorIndex: int, attribute: str, operation: str, log=False, **kwargs
    ):
        return {
            "target": target,
            "pub": {  # pub
                "taskId": self.task_id,
                "monitorIndex": self.Index(monitorIndex),
                "attribute": attribute,
                "operation": operation,
                "log": log,
            },
            "option": kwargs,
        }

    @__post__
    def passive_fde_sweep_options(self, target: str):
        return {"target": target, "pub": {"taskId": self.task_id}}

    @data_parser
    @__post__
    def passive_fde_sweep_chart(self, target: str, attribute: str, log=False, **kwargs):
        return {
            "target": target,
            "pub": {  # pub
                "taskId": self.task_id,
                "attribute": attribute,
                "log": log,
            },
            "option": kwargs,
        }


class EMEResultHandler(V0_4_API):
    @data_parser
    def get_smatrix(self, task_type, target="intensity"):
        res = self.post(taskid=self.task_id, type=task_type)
        assert res.get("success")
        result = res["result"]
        n = result["n"]
        data = np.reshape(result["data"], (n, n))
        return {
            "data": data,
            "dWidth": list(range(1, n + 1)),
            "dHeight": list(range(1, n + 1)),
        }

    @data_parser
    def get_eme_result(self, monitor_index: int, field: str, type, target="intensity"):
        res = self.post(taskid=self.task_id, monitor_index=self.Index(monitor_index), field=field, type=type)
        assert res.get("success")
        result = res["result"]
        nx, ny, ix, iy = 0, 0, 0, 0
        for i, _n in enumerate(result["n"]):
            if _n > 1:
                if not nx:
                    nx = _n
                    ix = i
                else:
                    ny = _n
                    iy = i
        dWidth = result["grid"][f"axis{ix}"]
        dHeight = result["grid"][f"axis{iy}"]
        data = np.reshape(result["data"], (nx, ny))

        return {"data": np.transpose(data), "dWidth": dWidth, "dHeight": dHeight}

    @data_parser
    def get_eme_sweep_result(self, target="line"):
        res = self.post(taskid=self.task_id)
        assert res.get("success")
        result = res["result"]
        _smatrixs = result["smatrixs"]
        sweep_type = result["sweep_type"]
        sweep_spans = result["sweep_spans"]

        def possibles(_):
            return np.reshape(
                [
                    [[(is_imag, port2, port1) for is_imag in range(2)] for port2 in range(_["n"])]
                    for port1 in range(_["n"])
                ],
                (-1, 3),
            )

        smatrixs = map(
            lambda _: [_["smatrix"][port1][port2][is_imag] for is_imag, port2, port1 in possibles(_)], _smatrixs
        )
        if _smatrixs:
            legend = [
                f'{port1 + 1}_{port2 + 1}_{["real", "imag"][is_imag]}' for is_imag, port2, port1 in
                possibles(_smatrixs[0])
            ]
        else:
            legend = []
        return {"data": np.transpose(list(smatrixs)), "legend": legend, "horizontal": sweep_spans}

    @__post__
    def passive_eme_fd_result_options(self, target: str, monitorIndex: int):
        return {"target": target, "pub": {"taskId": self.task_id, "monitorIndex": self.Index(monitorIndex)}}

    @data_parser
    @__post__
    def passive_eme_fd_result_chart(self, target: str, monitorIndex: int, attribute: str, operation: str, **kwargs):
        return {
            "target": target,
            "pub": {  # pub
                "taskId": self.task_id,
                "monitorIndex": self.Index(monitorIndex),
                "attribute": attribute,
                "operation": operation,
            },
            "option": kwargs,
        }


class PDResultHandler(V0_3_API):
    heatmap = base.ShadowAttr("_heatmap")

    photon_current = base.ShadowAttr("_polylines", "photon_current")
    responsivity = base.ShadowAttr("_polylines", "responsivity")

    potential = base.ShadowAttr("_dfs", "potential")
    e_conc = base.ShadowAttr("_dfs", "e_conc")
    h_conc = base.ShadowAttr("_dfs", "h_conc")
    jx = base.ShadowAttr("_dfs", "jx")
    jy = base.ShadowAttr("_dfs", "jy")

    resistance = base.ShadowAttr("_get_resistance")

    def __init__(self, task_id: int, task_type: str, token: str):
        super().__init__(task_id, task_type, token)
        self.update_status()
        if self.status == 2:
            self.load_data()

    def load_data(self):
        with self.get_pd_power_result() as data:
            self._dfs = {
                _: pd.DataFrame(
                    np.array(data[_]),
                    columns=data["x"],
                    index=data["y"],
                ).astype(float)
                for _ in ["potential", "e_conc", "h_conc", "jx", "jy"]
            }

        with self.get_gen_rate_heatmap() as data:
            self._heatmap = pd.DataFrame(
                np.array(data["g_r"]),
                columns=data["x_r"],
                index=data["y_r"],
            ).astype(float)

        with self.get_pd_td_polyline() as data:
            self._polylines = {
                _: pd.DataFrame(np.array(data[_]), columns=[_], index=data["t"]).astype(float)
                for _ in ["photon_current", "responsivity"]
            }

        with self.get_resistance() as result:
            self._get_resistance = pd.DataFrame(result, index=[0])

    @contextmanager
    def get_pd_power_result(self, target="intensity"):
        res = self.post(taskid=self.task_id)
        try:
            assert res.get("success")
            yield res["result"]["data"]
        except AssertionError:
            print("Fetch result failed")
        finally:
            del res

    @contextmanager
    def get_pd_td_polyline(self, target="line"):
        res = self.post(taskid=self.task_id)
        try:
            assert res.get("success")
            yield res["result"]["data"]
        except AssertionError:
            print("Fetch result failed")
        finally:
            del res

    @contextmanager
    def get_resistance(self, target="intensity"):
        res = self.post(taskid=self.task_id)
        try:
            assert res.get("success")
            yield res["result"]
        except AssertionError:
            print("Fetch result failed")
        finally:
            del res

    @contextmanager
    def get_gen_rate_heatmap(self, target="intensity"):
        res = self.post(taskid=self.task_id)
        try:
            assert res.get("success")
            yield res["result"]["data"]
        except AssertionError:
            print("Fetch result failed")
        finally:
            del res

    @contextmanager
    def get_fdtd_grid(self, monitor_index: int, target="intensity"):
        res = self.post(
            taskid=self.task_id,
            monitor_index=monitor_index,
        )
        try:
            assert res.get("success")
            yield res["result"]
        except AssertionError:
            print("Fetch result failed")
        finally:
            del res

    @contextmanager
    def get_fdtd_fd_result(self, monitor_index: int, frequency_index: int, field: str, _type: str, target="intensity"):
        res = self.post(
            taskid=self.task_id,
            monitor_index=monitor_index,
            freq_index=frequency_index,
            field=field,
            type=_type,
        )
        try:
            assert res.get("success")
            yield res["result"]
        except AssertionError:
            print("Fetch result failed")
        finally:
            del res

    @__post__
    def passive_fdtd_fd_result_option(self, target: str, monitorIndex: int):
        return {"target": target, "pub": {"taskId": self.task_id, "monitorIndex": self.Index(monitorIndex)}}

    @data_parser
    @__post__
    def passive_fdtd_fd_result_chart(
        self, target: str, monitorIndex: int, attribute: str, operation: str, log=False, **kwargs
    ):
        return {
            "target": target,
            "pub": {  # pub
                "taskId": self.task_id,
                "monitorIndex": self.Index(monitorIndex),
                "attribute": attribute,
                "operation": operation,
                "log": log,
            },
            "option": kwargs,
        }


class ModulatorResultHandler(V0_3_API):
    potential = base.ShadowAttr("_dfs", "potential")
    e_conc = base.ShadowAttr("_dfs", "e_conc")
    h_conc = base.ShadowAttr("_dfs", "h_conc")
    jx = base.ShadowAttr("_dfs", "jx")
    jy = base.ShadowAttr("_dfs", "jy")
    dk = base.ShadowAttr("_dfs", "dk")
    dn = base.ShadowAttr("_dfs", "dn")

    resistance = base.ShadowAttr("_get_resistance")

    def __init__(self, task_id: int, task_type: str, token: str):
        super().__init__(task_id, task_type, token)
        self.update_status()
        if self.status == 2:
            self.load_data()

    def load_data(self):
        with self.get_resistance() as result:
            self._get_resistance = pd.DataFrame(result, index=[0])

        with self.get_modulator_result() as result:
            self._dfs = {
                _: pd.DataFrame(
                    np.array(result[_]),
                    columns=result["x"],
                    index=result["y"],
                ).astype(float)
                for _ in ["potential", "e_conc", "h_conc", "jx", "jy", "dk", "dn"]
            }

    @contextmanager
    def get_modulator_result(self, target="intensity"):
        res = self.post(taskid=self.task_id)
        try:
            assert res.get("success")
            yield res["result"]["data"]
        except AssertionError:
            print("Fetch result failed")
        finally:
            del res

    @contextmanager
    def get_resistance(self, target="table"):
        res = self.post(taskid=self.task_id)
        try:
            assert res.get("success")
            yield res["result"]
        except AssertionError:
            print("Fetch result failed")
        finally:
            del res

    @contextmanager
    def get_mode_solver_result(
        self, mode_index: int, field: str, _type: str, log: bool = False, target: str = "intensity"
    ):
        res = self.post(taskid=self.task_id, option=dict(mode_index=mode_index, field=field, type=_type, log=log))
        try:
            assert res.get("success")
            yield res["result"]
        except AssertionError:
            print("Fetch result failed")
        finally:
            del res

    @__post__
    def passive_fde_options(self, target: str, monitorIndex: int):
        return {"target": target, "pub": {"taskId": self.task_id, "monitorIndex": self.Index(monitorIndex)}}

    @data_parser
    @__post__
    def passive_fde_result_chart(
        self, target: str, monitorIndex: int, attribute: str, operation: str, log=False, **kwargs
    ):
        return {
            "target": target,
            "pub": {  # pub
                "taskId": self.task_id,
                "monitorIndex": self.Index(monitorIndex),
                "attribute": attribute,
                "operation": operation,
                "log": log,
            },
            "option": kwargs,
        }


class ModeExpansion(V0_3_API):
    @contextmanager
    def get_mode_expansion(self, target="line"):
        res = self.post(taskid=self.task_id)
        try:
            assert res.get("success")
            yield res["result"]
        except AssertionError:
            print("Fetch result failed")
        finally:
            del res


class UserImport(V0_4_API):
    def __init__(self):
        super().__init__(None, None)

    def upload_files(self, file: str):
        file_name = Path(file).name
        token = self.token
        files = [('files', (file_name, open(Path(file), 'rb'), 'application/octet-stream'))]
        res = requests.request(
            "POST",
            self.api_url % "upload_files",
            headers={},  # {"Content-Type": "multipart/form-data;boundary=--"}
            data={'token': token},
            files=files,
        )
        return res.text

    def get_user_mode_files(self):
        return self.post(token=self.token)

    @__post__
    def get_user_mode_file_options(self, file_name):
        return {'file_name': file_name}

    @__post__
    def get_user_mode_file_chart(self, file_name, attribute, operation):
        return {'file_name': file_name, 'pub': {'attribute': attribute, 'operation': operation}}
