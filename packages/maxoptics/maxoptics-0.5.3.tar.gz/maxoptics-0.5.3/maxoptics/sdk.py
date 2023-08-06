# coding=utf-8
from asyncio import events
import os
import json
from typing import Sequence

from maxoptics.base.BaseClient import BaseClient
from maxoptics.base.BaseDataCls import Material, Waveform
from maxoptics.error import APIError, InvalidInputError
from maxoptics.utils.MosSubmodules import PublicMaterials, UserMaterials, UserWaveforms
from maxoptics.utils.base import (
    success_print,
    error_print,
    info_print,
)
from maxoptics.models import JSasync, MosProject
from maxoptics.constraints.retailer import project_prerun, get_default_async_flag, get_default_async
from maxoptics.config import Config, BASEDIR
from maxoptics.visualizer import get_task_handler, UserImport
import inspect
import time
import threading
from collections import defaultdict
from pathlib import Path
# from urllib3 import exceptions
from maxoptics.octopus import monitor_on
from copy import deepcopy

import re
import asyncio

BETA = Config.BETA
DEBUG = Config.DEBUG


class MaxOptics(BaseClient):
    def __init__(self, no_login=False):
        from maxoptics import __VERSION__

        """ """
        print("====================================MaxOptics Studio===================================")
        print("=                                                                                     =")
        print("=                                 Copyright Infomation                                =")
        print("=           Built by Shanghai Maxoptics Information Technology Co.,Ltd.               =")
        print(f"=                              Version: V{__VERSION__} with GDS import                        =")
        print("=    Based on Python3.8+ and MOS suite Dragon, Octopus, Shark and Whale services      =")
        print("=                                                                                     =")
        print("=======================================================================================")

        super().__init__("DragonURLTemplate", "SERVERAPI", "SERVERPORT")
        self.projects = {}
        self.remote_projects = {}
        self.thread_status = True
        self.async_tasks = []

        self.public_materials = PublicMaterials(self)
        self.user_materials = UserMaterials(self, "passive")
        self.user_waveforms = UserWaveforms(self)
        self.__search_projects_for_dolphin()

    def waiting(self):
        """ """
        t = threading.Thread(target=self.wait, name="Waiting")
        # t.setDaemon(True)
        t.start()

    def wait(self):
        """ """
        info_print("......", end=" ")
        while self.thread_status:
            info_print(".", end=" ", flush=True)
            time.sleep(1)

    def search_projects(self):
        return self.__search_projects_for_dolphin()

    def export_project(self, project: MosProject, name: str = None, format="json") -> None:
        name = name if name else project.name
        proj_type = project.type
        params = {"token": self.token, "project_id": project.id}
        result = self.post(**params)
        if result["success"] is False:
            error_print("Export Failed, %s" % result["result"]["msg"])
            return
        else:
            os.makedirs(Config.OUTPUTDIR / "exports", exist_ok=True)
            with open(Config.OUTPUTDIR / "exports" / f"{name}.{proj_type}", "w") as f:
                if format == "json":
                    f.write(json.dumps(result["result"]))
            info_print("Project ", project.name, end=" ")
            success_print(" Saved.")
            return

    def delete_many_projects(self, projects_id):
        params = {"token": self.token, "projects_id": projects_id}
        result = self.post(**params)
        if result["success"] is False:
            error_print("Recover Project Failed, %s" % result["result"]["msg"])
            return
        else:
            return

    def import_project(self, name: str, path: str, verbose=False) -> MosProject:
        project_type = path.split(".")[-1]
        with open(path) as f:
            data = json.load(f)
        public_material = self.search_public_materials()
        # public_waveform = self.search_waveforms()
        materials = data.get("materials", [])
        # all_material = []
        # all_material.extend(materials)
        # all_material.extend(public_material)
        # print(public_material)
        # print(public_waveform)
        waveforms = data.get("waveforms", [])
        project = data["data"]
        exec_list = {"m": {}, "w": {}}

        for i in self.post(
            url="create_materials", token=self.token, materials_info=materials, project_type=project_type
        )["result"]["result"]:
            exec_list["m"][str(i["original_id"])] = i["id"]
        for i in public_material:
            exec_list["m"][str(i["id"])] = i["id"]
        for i in self.post(url="create_waveforms", token=self.token, waveforms_info=waveforms)["result"]["result"]:
            exec_list["w"][str(i["original_id"])] = i["id"]
        # for i in public_waveform:
        #     exec_list["w"][str(i["id"])] = i["id"]

        proj = self.create_project_as(name, silent=True, imported=True, project_type=project_type)
        proj.appendix.update(dict(sweep=project["sweep"]))

        proj.resize(
            project["tree"]["attrs"]["w"],
            project["tree"]["attrs"]["h"],
            project["tree"]["attrs"]["drawGrid"]["dx"],
            project["tree"]["attrs"]["drawGrid"]["dy"],
        )

        def rep(s: str):
            return re.sub("[\\(\\)\\-\\+]", "_", s)

        def ana(inp):
            if isinstance(inp, str):
                return f"'{inp}'"
            else:
                return inp

        def assign_value(l, component):
            for attr in l:
                if attr in ["name", "_objLink"]:
                    continue
                if component.get(attr, silent=True) != None:
                    if isinstance(l[attr], dict):
                        # if verbose:
                        #     print(rep(component.name), ".update(", str(ana(l[attr])),")", sep="")
                        # component.update(deepcopy(l[attr]))
                        assign_value(l[attr], component)
                    else:
                        if verbose:
                            print(rep(component.name), f'["{attr}"]', "=", str(ana(l[attr])), sep="")
                        component.set(attr, deepcopy(l[attr]), escape=["*"])

        assign_value(project["tree"]["attrs"], proj.DOCUMENT)

        for child in project["tree"]["children"]:
            project["tree"]["children"] += child["children"]
            component = proj.add(child["type"]["name"], child["name"])
            if verbose:
                print(
                    rep(child["name"]),
                    "=",
                    proj.name,
                    ".add(",
                    '"{}", '.format(child["type"]["name"]),
                    '"{}"'.format(child["name"]),
                    ")",
                    sep="",
                )

            assign_value({"attrs": child["attrs"], "id": child.get("id")}, component)
            if component.get("background_material", silent=True) != None and component.get("background_material"):
                component["background_material"] = exec_list["m"][str(component.get("background_material"))]
            if component.get("materialId", silent=True) != None and component.get("materialId"):
                component["materialId"] = exec_list["m"][str(component.get("materialId"))]
            if component.get("waveform_id", silent=True) != None and component.get("waveform_id"):
                component["waveform_id"] = exec_list["w"][str(component.get("waveform_id"))]

        proj.save()
        return proj

    def create_project_as(
        self,
        name=None,
        order=None,
        silent=False,
        imported=False,
        project_type="passive",
    ) -> MosProject:
        self.search_projects()
        try:
            if name:
                project_id = (
                    self.remote_projects[name]["id"]
                    if "id" in self.remote_projects[name]
                    else self.remote_projects[name]["project_id"]
                )
                project_version = (
                    self.remote_projects[name]["version"]
                    if "version" in self.remote_projects[name]
                    else self.remote_projects[name]["current_ptr"]
                )
            elif order:
                name = "Untitle"
                project_id = (
                    list(self.remote_projects.values())[order]["id"]
                    if "id" in list(self.remote_projects.values())[order]
                    else list(self.remote_projects.values())[order]["project_id"]
                )
                name = list(self.remote_projects.values())[order]["name"]
                project_version = (
                    list(self.remote_projects.values())[order]["version"]
                    if "version" in list(self.remote_projects.values())[order]
                    else list(self.remote_projects.values())[order]["current_ptr"]
                )
            elif not silent:
                error_print(
                    "You may input one of: name, order, 1\n \
                client.projects contains related information"
                )
                raise InvalidInputError
            else:
                raise InvalidInputError
            # self.untrash_many_projects(project_id)
        except KeyError as e:
            res = self.create_project(name=name, project_type=project_type)
            project_id = res.id
            project_version = res.version

        self.projects[name] = MosProject(self, self.token, name, project_type=project_type)
        self.projects[name].id = project_id
        self.projects[name].version = project_version
        info_print("Project ", name, end=" ")
        success_print("Created.")
        info_print("project name: ", name)
        info_print("project id: ", self.projects[name].id)
        info_print("project version: ", self.projects[name].version)
        if not imported:
            info_print("This is a empty project, rebuilding needed")
        return self.projects[name]

    def ensure_materials(self, materials: Sequence[Material], project_type: str, replace=False):
        """Ensure the materials exist.
        If replace is set to True, this method will change existing materials attribute.
        This action is kind of DANGEROUS because the same materials might be used in other projects,
        and you may change them unintentionally.

        Args:
            materials (Sequence[Material]): A Sequence of dicts. Attributes lies in dicts
            project_type (str): passive or active
            replace (bool, optional): Whether to override the existing materials. Defaults to False.
        """
        used_names = UserMaterials(self, project_type).names
        used_ids = UserMaterials(self, project_type).ids
        new: Sequence[Material] = []
        repeated: Sequence[Material] = []
        for i, info in enumerate(materials):
            if info.name in used_names:
                info.id = used_ids[i]
                repeated.append(info)
            else:
                new.append(info)

        self.__create_materials([_.to_dict() for _ in new], project_type)
        if replace:
            self.__change_materials([_.to_dict2() for _ in repeated])
        self.user_materials.reload()

    def ensure_waveforms(self, waveforms: Sequence[Waveform], replace=False):
        """Ensure the waveforms exist.
        If replace is set to True, this method will change existing waveforms attribute.
        This action is kind of DANGEROUS because the same waveforms might be used in other projects,
        and you may change them unintentionally.

        Args:
            waveforms(Sequence[Waveform]): A Sequence of dicts. Attributes lies in dicts.
            replace(bool, optional): Whether to override the existing waveforms. Defaults to False.
        """

        used_names = UserWaveforms(self).names
        used_ids = UserWaveforms(self).ids
        new = []
        repeated = []
        for i, info in enumerate(waveforms):
            if info.name in used_names:
                info.id = used_ids[i]
                repeated.append(info)
            else:
                new.append(info)

        self.__create_waveforms([_.to_dict() for _ in new])
        if replace:
            self.__change_waveforms([_.to_dict() for _ in repeated])
        self.user_waveforms.reload()



    def search_materials(self, url="") -> list:
        """
        搜索材料
        @param 空
        """
        params = {"token": self.token}

        result = self.post(url=url, **params)
        if result["success"] is False:
            error_print("Material search Failed, %s" % result["result"]["msg"])
            return []
        else:
            self.materials = result["result"]["result"]
            return result["result"]["result"]

    def search_public_materials(self) -> list:
        """
        搜索材料
        @param 空
        """
        params = {"token": self.token}

        result = self.post(url="get_public_materials", **params)
        if result["success"] is False:
            error_print("材料搜索失败, %s" % result["result"]["msg"])
            return []
        else:
            self.materials = result["result"]["public_materials"]
            return result["result"]["public_materials"]

    def search_waveforms(self) -> list:
        """ """
        params = {"token": self.token}

        result = self.post(**params)
        if result["success"] is False:
            error_print("Waveform search Failed, %s" % result["result"]["msg"])
            return []
        else:
            self.waveforms = result["result"]["result"]
            return result["result"]["result"]

    def create_project(self, name: str, project_type="passive") -> MosProject:
        """ """
        # if type == 'passive':
        path = Path(BASEDIR) / "static_modules" / "ProjectSample.json"
        with open(path, "r", encoding="utf8") as f:
            empty_project_data = json.load(f)
        params = {
            "token": self.token,
            "name": name,
            "data": empty_project_data,
            "dirty": True,
            "project_type": project_type,
        }
        result = self.post(**params)
        if result["success"] is False:
            error_print("Project creation Failed, %s" % result["result"]["msg"])
            raise APIError(result["result"]["msg"])
        else:
            self.projects[name] = MosProject(self, self.token, name, project_type=project_type)
            self.projects[name].id = result["result"]["id"]
            self.projects[name].type = project_type
            self.projects[name].version = result["result"]["version"]
            info_print("Project ", name, end=" ")
            success_print("Created.")
            info_print("project name: ", name)
            info_print("project id: ", self.projects[name].id)
            info_print("project version: ", self.projects[name].version)
            return self.projects[name]

    def save_project(self, proj: MosProject):
        """ """
        project_prerun(proj)
        data = dict(proj.formatComponents())
        if not data:
            error_print("Project save Failed, %s" % "because of setattr failure")
            exit(0)
        params = {
            "token": self.token,
            "id": proj.id,
            "data": data,
        }
        # warn_print(f'{params=}')
        result = self.post(**params)
        if result["success"] is False:
            error_print("Project save Failed, %s" % result["result"]["msg"])
            exit(0)
        else:
            success_print("Project", proj.name, "Saved.")

    def create_task(self, proj: MosProject, task_type=None, project_type="", __timeout__=-1, *args, **kws):
        """ """
        mode = ""
        if isinstance(proj, int):
            if "async_flag" in kws:
                async_flag = kws.pop("async_flag")
            else:
                async_flag = get_default_async(project_type, task_type)

                params = dict(
                    **{"token": self.token, "project_id": proj, "tasktype": task_type},
                    **({"async": async_flag} if async_flag else {}),
                )
        else:
            kws = defaultdict(lambda: False, kws)

            kws["dep_task"]
            dep_task = int(kws.pop("dep_task"))
            kws["task_info"]
            task_info = kws.pop("task_info") or None
            kws["link_task_id"]
            link_task_id = kws.pop("link_task_id") or []
            task_type = task_type if task_type else proj.solver_type

            if "async_flag" in kws:
                async_flag = kws.pop("async_flag")
            else:
                async_flag = get_default_async_flag(proj)

            if BETA:
                print(f"RUN TASK WITH {task_type = }, {async_flag = }, {dep_task = }")

            if task_type == "ModeSolver":
                task_type = "fde"
            if task_type.upper() == "EME_SWEEP":
                # TODO: This part should rm
                proj.solver["propagation"] = 1
                if not kws["start"] and kws["start"] and kws["stop"] and kws["number_of_points"] and kws["para"]:
                    error_print("Please Input value of start, stop, number_of_points, para")
                    raise InvalidInputError
                if "stop" in kws:
                    proj.solver["stop"] = kws["stop"]
                proj.solver["start"] = kws["start"] if "start" in kws else 0
                proj.solver["number_of_points"] = kws["number_of_points"] if "number_of_points" in kws else 5
                proj.solver["parameter"] = kws["para"] if "para" in kws else 0
                proj.save()
            else:
                for k in kws:
                    proj.solver[k] = kws[k]

            params = dict(
                **{"token": self.token, "project_id": proj.id, "tasktype": task_type},
                **({"async": async_flag} if async_flag else {}),
                **({"dep_task": dep_task} if dep_task else {}),
                **({"task_info": task_info} if task_info else {}),
                **({"link_task_id": link_task_id} if link_task_id else {}),
            )
        result = self.post(**params)
        if result["success"] is False:
            error_print("Task startup Failed, %s" % result["result"]["msg"])
            raise Exception
        else:
            info_print("Project ", proj.name, end=" ")
            success_print(
                "Task started. id {}.\n You can open file {} to check task status".format(
                    str(result["result"]["id"]),
                    str(Config.OUTPUTDIR / (str(proj.name) + "_" + str(result["result"]["id"])) / "log" / "status.log"),
                )
            )
            task = dict(**result["result"], **{"task_type": task_type})
            res = monitor_on(proj, task, self.get_tasks, self.token, mode)
            proj.running_tasks.append(res)

            if __timeout__ == -1:
                task = res
                time.sleep(3)
                while True:
                    if task.check_status(quiet=True) is None:
                        time.sleep(5)
                    else:
                        return res

            elif __timeout__ == 0:
                return res

            elif __timeout__ > 0:
                task = res
                time.sleep(3)
                __timeout__ -= 3
                while True:
                    if task.check_status(quiet=True) is None:
                        time.sleep(5)
                        __timeout__ -= 5
                        if __timeout__ <= 0:
                            error_print(f"{task.id} TIMEOUT")
                            return task
                    else:
                        return task

            else:
                raise InvalidInputError

    def get_tasks(self, proj, **kws):
        """ """
        params = {"token": self.token, "project_id": proj.id, "only_completed": False}
        result = self.post(**params, **kws)
        if result["success"] is False:
            error_print("Search project Failed, %s" % result["result"]["msg"])
        else:
            silent = inspect.stack()[1][3] == "peek_task_status"
            if not silent:
                info_print("Project ", proj.name, end=" ")
                success_print("Succeed.")
            proj.tasks = result["result"]["tasklist"]
        return proj.tasks

    def awaiting(self, depth=-1):
        dep = 0
        while self.async_tasks and (depth == -1 or dep < depth):
            this_round = [_.dest for _ in self.async_tasks]
            self.async_tasks = []
            comb = asyncio.gather(*this_round)
            loop = events.get_event_loop()
            loop.run_until_complete(comb)
            dep += 1

    def wait_latest(self):
        index = len(self.async_tasks) - 1
        temp_asys = [self.async_tasks.pop()]
        while temp_asys:
            this_round = [_.dest for _ in temp_asys]
            comb = asyncio.gather(*this_round)
            loop = events.get_event_loop()
            loop.run_until_complete(comb)
            temp_asys = self.async_tasks[index:] if len(self.async_tasks) > index else []

    def async_task(self, cor) -> JSasync:
        asynker = JSasync(cor, self.wait_latest)
        self.async_tasks.append(asynker)
        return asynker

    def async_create_task(self, proj: MosProject, task_type=None, mode="", *args, **kwargs) -> JSasync:
        task = self.create_task(proj, task_type, mode, 0, *args, __timeout__=-1, **kwargs)

        async def waiting():
            if not task:
                return
            while True:
                await asyncio.sleep(5)
                status = task.check_status(quiet=True)
                if status != None:
                    if status:
                        return task
                    else:
                        return False

        return self.async_task(waiting())

    def restore_task(self, task_id, task_type):
        file_dir = Config.OUTPUTDIR
        dest = file_dir / f"{str(task_id)}" / "log"
        os.makedirs(dest, exist_ok=True)
        # todo: restore project at the same time
        task = get_task_handler(task_type)(task_id, task_type, self.token, None)
        task.update_status()
        return task

    def __untrash_many_projects(self, id):
        params = {"token": self.token, "projects_id": [id]}
        result = self.post(url="untrash_many_projects", **params)
        if result["success"] is False:
            error_print("Recover Project Failed, %s" % result["result"]["msg"])
            return
        else:
            return

    def __search_projects_for_dolphin(self):
        """
        搜索工程
        @param 空
        """
        params = {"token": self.token, "batch_size": 1000}

        result = self.post(url="search_projects_for_dolphin", **params)
        if result["success"] is False:
            error_print("Search project Failed, %s" % result["result"]["msg"])
        else:
            projects = result["result"]["projects_info"]
            for project in projects:
                self.remote_projects[project["name"]] = project
        return self.remote_projects

    def __create_materials(self, materials_info, project_type: str):
        params = {"token": self.token, "materials_info": materials_info, "project_type": project_type}
        result = self.post(url="create_materials", **params)
        if result["success"] is False:
            error_print("Material creation failed, %s" % result["result"]["msg"])
        else:
            return result["result"]["result"]

    def __change_materials(self, materials_info):
        params = {"token": self.token, "materials_info": materials_info}
        result = self.post(url="change_materials", **params)
        if result["success"] is False:
            error_print("Material modification failed, %s" % result["result"]["msg"])
        else:
            return result["result"]

    def __create_waveforms(self, waveforms_info):
        """ """
        params = {"token": self.token, "waveforms_info": waveforms_info}
        result = self.post(url="create_waveforms", **params)
        if result["success"] is False:
            error_print("Waveform creation Failed, %s" % result["result"]["msg"])
        else:
            return result["result"]["result"]

    def __change_waveforms(self, waveforms_info):
        params = {"token": self.token, "waveforms_info": waveforms_info}
        result = self.post(url="change_waveforms", **params)
        if result["success"] is False:
            error_print("Waveform modification failed, %s" % result["result"]["msg"])
        else:
            return result["result"]

    def get_material_table_data(self, material_id):
        params = {"token": self.token, "material_id": material_id}
        result = self.post(url = "get_material_table_data", **params)
        if result["success"] is False:
            error_print("Material table data fetching failed, %s" % result["result"]["msg"])
        else:
            return result["result"]

    @staticmethod
    def get_uploader():
        return UserImport()


    def __del__(self):
        self.token = ""
        # self.logout()
        info_print("MaxOptics Studio SDK Exited")
