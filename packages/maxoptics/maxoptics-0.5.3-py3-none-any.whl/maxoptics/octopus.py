import os
import platform
from maxoptics.config import Config, BASEDIR
from maxoptics.visualizer import get_task_handler
from maxoptics.utils.base import error_print
import asyncio
import subprocess
import threading
import time
from pathlib import Path


def monitor_on(proj, task, func, token, mode):
    result = get_task_handler(task["task_type"])(task["id"], proj)
    thread0 = threading.Thread(
        target=peek_task_status, args=(proj, task, func, token, mode, result), name="Task: " + str(task)
    )
    thread0.setDaemon(True)
    thread0.start()
    return result


def peek_task_status(proj, task, func, token, mode, result):
    task_id = task["id"]
    task_type = task["task_type"]
    task = None
    file_dir = Config.OUTPUTDIR
    visualizer_path = BASEDIR / "visualizer.py"
    # task_path = Path()
    dest = file_dir / f"{str(proj.name)}_{str(task_id)}" / "log"
    os.makedirs(dest, exist_ok=True)

    def notify(status):
        pltfm = platform.system()
        # sio.connect('http://'+config['SERVERAPI'])
        # sio.wait()

        if pltfm == "Darwin":
            command = f"clear; python3 {visualizer_path} {status} {proj.id} {task_id} {token} {task_type}"
            with open(dest / "monitor.command", "w") as f:
                f.write(command)
            res = os.system(f"cd {dest}; chmod +x monitor.command; open -n monitor.command")

        elif pltfm == "Windows":
            bat = f"python {visualizer_path} {status} {proj.id} {task_id} {token} {task_type}"
            with open(dest / "monitor.bat", "w") as f:
                f.write(bat)
            # os.chdir(dest)
            cmd = "start cmd.exe /c " + str(dest / "monitor.bat")
            os.system(cmd)

        elif pltfm == "Linux":
            os.system(f"gnome-terminal -e 'python {visualizer_path} {status} {proj.id} {task_id} {token} {task_type}'")

    lines = ("Waiting from {} to {}\n\n", "Running from {} to {}\n\n", "Ended @ {}\n\n", "{}")
    addons = [[time.asctime(time.localtime(time.time())), "NOW"], ["...", "..."], ["..."], [""]]
    MAXRETRY = 5
    _RETRY = 0
    while True:
        try:
            tasks = func(proj)
            assert tasks
        except Exception as e:
            _RETRY += 1
            print("Error arises when updating task status:\n", e)
            if not (MAXRETRY - _RETRY):
                raise e
            else:
                continue
        _RETRY = 0
        localtime = time.asctime(time.localtime(time.time()))
        for t in tasks:
            if t["task_id"] == task_id:
                task = t

        if not (task):
            addons[3][0] = "The task record is MISSING"
            error_print("The task record is MISSING")
            exit()

        children_task = list(filter(lambda _: _["root_task"] == task["task_id"], tasks))
        if task["status"] == 0:
            if children_task:
                task["status"] = sum([_["status"] for _ in children_task]) / (2 * len(children_task))
        if task["status"] == 0:
            addons[0][1] = f"NOW ({localtime})"
        elif 0 < task["status"] <= 1:
            result.start_time = localtime
            result.start_time_raw = time.time()
            if addons[1][0] == "...":
                addons[0][1] = localtime
                addons[1][0] = localtime
            addons[1][1] = f"NOW ({localtime})"
        else:
            result.end_time = localtime
            result.end_time_raw = time.time()
            addons[1][1] = localtime
            addons[2][0] = localtime
            if task["status"] == 1:
                addons[3][0] = "The task SUCCEED"
            if task["status"] == -2:
                addons[3][0] = "The task FAILED"
            if task["status"] == -1:
                addons[3][0] = "The task PAUSED"
            if addons[1][0] == "...":
                result.start_time_raw = time.time() - 3
                addons[0][1] = localtime
                addons[1][0] = localtime
            break

        with open(dest / "status.log", "w") as f:
            f.writelines([line.format(*addon) for line, addon in zip(lines, addons)])

        result.status = task["status"]
        time.sleep(3)

    with open(dest / "status.log", "w") as f:
        f.writelines([line.format(*addon) for line, addon in zip(lines, addons)])
    time.sleep(0.1)
    if mode == "t" or mode == "terminal":
        notify(task["status"])
    # elif mode == 'i':
    result.status = task["status"]
