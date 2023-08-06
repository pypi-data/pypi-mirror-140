# coding=utf-8
from __future__ import annotations

from maxoptics import __MAINPATH__
from pathlib import Path
from dataclasses import dataclass
import os
import yaml

from maxoptics import __CONFIGPATH__

BASEDIR = Path(os.path.dirname(os.path.abspath(__file__)))


@dataclass()
class Config:
    SERVERAPI: str = ""
    SERVERPORT: int = 80
    OUTPUTDIR: Path = ""
    DEFAULTUSER: str = ""
    DEFAULTPASSWORD: str = ""

    # Preference
    BETA: bool = False
    DEBUG: bool = False
    VERBOSE: bool = False
    COLOR: bool = False

    # Base
    DragonURLTemplate: str = "http://{}:{}/api/%s/"
    WhaleURLTemplate: str = "http://{}:{}/whale/api/%s/"

    # Private
    Token: str = ""


if __CONFIGPATH__:
    f = open(__CONFIGPATH__)
elif "default.conf" in os.listdir(BASEDIR):
    f = open(BASEDIR / "default.conf")
else:
    f = None

if f:
    try:
        user_config = yaml.load(f, yaml.BaseLoader)
        for k in user_config:
            v = user_config[k]
            setattr(Config, str(k).upper(), v)
    except Exception:
        print("default.conf is corrupted! Please rewrite it")
        exit(1)

    f.close()


if not Config.OUTPUTDIR:
    Config.OUTPUTDIR = __MAINPATH__ / "logs"
else:
    Config.OUTPUTDIR = Path(Config.OUTPUTDIR)
