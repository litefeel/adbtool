import yaml
from litefeel.pycommon.io import read_file
from var_dump import var_dump
from typing import Any


def get_value(key: str, map: dict[str, str], default: Any) -> Any:
    if map is not None:
        return map.get(key, default)
    return None


def get_value_bool(key, map, default) -> bool:
    if map is not None:
        value = map.get(key, default)
        return value in ("true", "True", True)

    return False


def copy_bool(key, map, obj, default=False):
    value = get_value_bool(key, map, default)
    setattr(obj, key, value)


def copy_value(key, map, obj, default=None):
    value = get_value(key, map, default)
    setattr(obj, key, value)


def copy_subconfig(key: str, map: Any, subconfig: Any) -> None:
    value = get_value(key, map, None)
    if value is not None:
        subconfig.load(value)


class PushConfig:
    def __init__(self):
        self.localdir = "."
        self.remotedir = "/sdcard"
        self.recursion = False
        self.dontpush = False
        self.paths = []

    def load(self, obj):
        copy_value("localdir", obj, self, ".")
        copy_value("remotedir", obj, self, "/sdcard")
        copy_value("paths", obj, self, [])
        copy_bool("recursion", obj, self, False)
        copy_bool("dontpush", obj, self, False)


class ApkConfig:
    def __init__(self):
        self.apkpath = None
        self.run = False

    def load(self, obj):
        copy_value("apkpath", obj, self, None)
        copy_bool("run", obj, self, False)


class InstallConfig:
    def __init__(self):
        self.apkpath = None
        self.run = False
        self.devices = None

    def load(self, obj):
        copy_value("devices", obj, self, None)
        copy_value("apkpath", obj, self, None)
        copy_bool("run", obj, self, False)


class Config:
    def __init__(self):
        self.push = PushConfig()
        self.apk = ApkConfig()
        self.install = InstallConfig()

    def load(self, obj: Any) -> None:
        copy_subconfig("push", obj, self.push)
        copy_subconfig("apk", obj, self.apk)
        copy_subconfig("install", obj, self.install)

    def load_config(self, filename: str) -> None:
        data = read_file(filename)
        obj = yaml.load(data, Loader=yaml.BaseLoader)
        # var_dump(obj)
        self.load(obj)
