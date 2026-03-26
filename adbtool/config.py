from collections.abc import Mapping
from typing import Protocol, TypeVar, cast

import yaml
from litefeel.pycommon.io import read_file

ConfigSection = Mapping[str, object]
T = TypeVar("T")


class SupportsLoad(Protocol):
    def load(self, obj: ConfigSection) -> None:
        ...


def get_value(key: str, obj: ConfigSection, default: T) -> T:
    return cast(T, obj.get(key, default))


def get_value_bool(key: str, obj: ConfigSection, default: bool = False) -> bool:
    value = obj.get(key, default)
    return value in ("true", "True", True)


def copy_subconfig(key: str, obj: ConfigSection, subconfig: SupportsLoad) -> None:
    value = obj.get(key)
    if isinstance(value, Mapping):
        subconfig.load(value)


class PushConfig:
    def __init__(self) -> None:
        self.localdir: str = "."
        self.remotedir: str = "/sdcard"
        self.recursion: bool = False
        self.dontpush: bool = False
        self.paths: list[str] = []

    def load(self, obj: ConfigSection) -> None:
        self.localdir = get_value("localdir", obj, ".")
        self.remotedir = get_value("remotedir", obj, "/sdcard")
        self.paths = get_value("paths", obj, [])
        self.recursion = get_value_bool("recursion", obj, False)
        self.dontpush = get_value_bool("dontpush", obj, False)


class PullConfig:
    def __init__(self) -> None:
        self.stat: bool = False
        self.localdir: str = "."
        self.remotedir: str = "/sdcard"
        self.paths: list[str] = []

    def load(self, obj: ConfigSection) -> None:
        self.localdir = get_value("localdir", obj, ".")
        self.remotedir = get_value("remotedir", obj, "/sdcard")
        self.paths = get_value("paths", obj, [])
        self.stat = get_value_bool("stat", obj, False)


class ProcfdConfig:
    def __init__(self) -> None:
        self.procname: str = ""

    def load(self, obj: ConfigSection) -> None:
        self.procname = get_value("procname", obj, "")


class ApkConfig:
    def __init__(self) -> None:
        self.apkpath: str | None = None
        self.run: bool = False

    def load(self, obj: ConfigSection) -> None:
        self.apkpath = get_value("apkpath", obj, None)
        self.run = get_value_bool("run", obj, False)


class InstallConfig:
    def __init__(self) -> None:
        self.apkpath: str | None = None
        self.run: bool = False
        self.devices: str | None = None

    def load(self, obj: ConfigSection) -> None:
        self.devices = get_value("devices", obj, None)
        self.apkpath = get_value("apkpath", obj, None)
        self.run = get_value_bool("run", obj, False)


class SignConfig:
    _dct: dict[str, str | None]

    def __init__(self) -> None:
        self._dct = {}

    @property
    def ks(self) -> str | None:
        return self._dct.get("ks")

    @property
    def ks_pass(self) -> str | None:
        return self._dct.get("ks-pass")

    @property
    def ks_key_alias(self) -> str | None:
        return self._dct.get("ks-key-alias")

    @property
    def key_pass(self) -> str | None:
        return self._dct.get("key-pass")

    def load(self, obj: ConfigSection) -> None:
        self._dct["ks"] = get_value("ks", obj, None)
        self._dct["ks-pass"] = get_value("ks-pass", obj, None)
        self._dct["ks-key-alias"] = get_value("ks-key-alias", obj, None)
        self._dct["key-pass"] = get_value("key-pass", obj, None)


class AssetBundleConfig:
    def __init__(self) -> None:
        self.unityeditordir: str | None = None
        self.keepress: bool = False

    def load(self, obj: ConfigSection) -> None:
        self.unityeditordir = get_value("unityeditordir", obj, None)
        self.keepress = get_value_bool("keepress", obj, False)


class Config:
    def __init__(self) -> None:
        self.push = PushConfig()
        self.pull = PullConfig()
        self.apk = ApkConfig()
        self.install = InstallConfig()
        self.sign = SignConfig()
        self.procfd = ProcfdConfig()
        self.assetbundle = AssetBundleConfig()
        self.groups: dict[str, Config] = {}

    def load(self, obj: ConfigSection) -> None:
        copy_subconfig("push", obj, self.push)
        copy_subconfig("pull", obj, self.pull)
        copy_subconfig("apk", obj, self.apk)
        copy_subconfig("install", obj, self.install)
        copy_subconfig("sign", obj, self.sign)
        copy_subconfig("procfd", obj, self.procfd)
        copy_subconfig("ab", obj, self.assetbundle)

    def load_config(self, filename: str) -> None:
        data = read_file(filename)
        obj = cast(ConfigSection, yaml.load(data, Loader=yaml.BaseLoader))
        self.load(obj)
        self.parse_groups(obj)

    def parse_groups(self, obj: ConfigSection) -> None:
        groups = obj.get("groups")
        if isinstance(groups, Mapping):
            for key, value in groups.items():
                if not isinstance(key, str) or not isinstance(value, Mapping):
                    continue
                group = Config()
                group.load(value)
                self.groups[key] = group
        else:
            self.groups = {}
