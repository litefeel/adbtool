import yaml
from litefeel.pycommon.io import read_file
from var_dump import var_dump
from typing import Any


def get_value(key: str, map: dict[str, str], default: str | None) -> str | None:
    if map is not None:
        return map.get(key, default)
    return None


def get_value_bool(key: str, map: dict[str, str], default: bool | None) -> bool:
    if map is not None:
        value = map.get(key, default)
        return value in ("true", "True", True)

    return False


def copy_bool(key: str, map: dict[str, str], obj: Any, default: bool = False) -> None:
    value = get_value_bool(key, map, default)
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)


def copy_value(key, map, obj, default=None):
    value = get_value(key, map, default)
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)


def copy_subconfig(key: str, map: dict[str, str], subconfig: Any) -> None:
    value = get_value(key, map, None)
    if value:
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


class PullConfig:
    def __init__(self):
        self.stat = False
        self.localdir = "."
        self.remotedir = "/sdcard"
        self.paths = []

    def load(self, obj):
        copy_value("localdir", obj, self, ".")
        copy_value("remotedir", obj, self, "/sdcard")
        copy_value("paths", obj, self, [])
        copy_bool("stat", obj, self, False)


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


class SignConfig:
    _dct: dict[str, str]

    def __init__(self) -> None:
        self._dct = {}

    @property
    def ks(self):
        return self._dct["ks"]

    @property
    def ks_pass(self):
        return self._dct["ks-pass"]

    @property
    def ks_key_alias(self):
        return self._dct["ks-key-alias"]

    @property
    def key_pass(self):
        return self._dct["key-pass"]

    def load(self, obj):
        copy_value("ks", obj, self._dct, None)
        copy_value("ks-pass", obj, self._dct, None)
        copy_value("ks-key-alias", obj, self._dct, None)
        copy_value("key-pass", obj, self._dct, None)


class Config:
    def __init__(self):
        self.push = PushConfig()
        self.pull = PullConfig()
        self.apk = ApkConfig()
        self.install = InstallConfig()
        self.sign = SignConfig()

    def load(self, obj: Any) -> None:
        copy_subconfig("push", obj, self.push)
        copy_subconfig("pull", obj, self.pull)
        copy_subconfig("apk", obj, self.apk)
        copy_subconfig("install", obj, self.install)
        copy_subconfig("sign", obj, self.sign)

    def load_config(self, filename: str) -> None:
        data = read_file(filename)
        obj = yaml.load(data, Loader=yaml.BaseLoader)
        # var_dump(obj)
        self.load(obj)
