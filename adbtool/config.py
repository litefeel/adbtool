from collections.abc import Mapping
from dataclasses import dataclass, field
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


@dataclass(slots=True)
class PushConfig:
    localdir: str = "."
    remotedir: str = "/sdcard"
    recursion: bool = False
    dontpush: bool = False
    paths: list[str] = field(default_factory=list)

    def load(self, obj: ConfigSection) -> None:
        self.localdir = get_value("localdir", obj, ".")
        self.remotedir = get_value("remotedir", obj, "/sdcard")
        self.paths = get_value("paths", obj, [])
        self.recursion = get_value_bool("recursion", obj, False)
        self.dontpush = get_value_bool("dontpush", obj, False)


@dataclass(slots=True)
class PullConfig:
    stat: bool = False
    localdir: str = "."
    remotedir: str = "/sdcard"
    paths: list[str] = field(default_factory=list)

    def load(self, obj: ConfigSection) -> None:
        self.localdir = get_value("localdir", obj, ".")
        self.remotedir = get_value("remotedir", obj, "/sdcard")
        self.paths = get_value("paths", obj, [])
        self.stat = get_value_bool("stat", obj, False)


@dataclass(slots=True)
class ProcfdConfig:
    procname: str = ""

    def load(self, obj: ConfigSection) -> None:
        self.procname = get_value("procname", obj, "")


@dataclass(slots=True)
class ApkConfig:
    apkpath: str | None = None
    run: bool = False

    def load(self, obj: ConfigSection) -> None:
        self.apkpath = get_value("apkpath", obj, None)
        self.run = get_value_bool("run", obj, False)


@dataclass(slots=True)
class InstallConfig:
    apkpath: str | None = None
    run: bool = False
    devices: str | None = None

    def load(self, obj: ConfigSection) -> None:
        self.devices = get_value("devices", obj, None)
        self.apkpath = get_value("apkpath", obj, None)
        self.run = get_value_bool("run", obj, False)


@dataclass(slots=True)
class SignConfig:
    ks: str | None = None
    ks_pass: str | None = None
    ks_key_alias: str | None = None
    key_pass: str | None = None

    def load(self, obj: ConfigSection) -> None:
        self.ks = get_value("ks", obj, None)
        self.ks_pass = get_value("ks-pass", obj, None)
        self.ks_key_alias = get_value("ks-key-alias", obj, None)
        self.key_pass = get_value("key-pass", obj, None)


@dataclass(slots=True)
class AssetBundleConfig:
    unityeditordir: str | None = None
    keepress: bool = False

    def load(self, obj: ConfigSection) -> None:
        self.unityeditordir = get_value("unityeditordir", obj, None)
        self.keepress = get_value_bool("keepress", obj, False)


@dataclass(slots=True)
class Config:
    push: PushConfig = field(default_factory=PushConfig)
    pull: PullConfig = field(default_factory=PullConfig)
    apk: ApkConfig = field(default_factory=ApkConfig)
    install: InstallConfig = field(default_factory=InstallConfig)
    sign: SignConfig = field(default_factory=SignConfig)
    procfd: ProcfdConfig = field(default_factory=ProcfdConfig)
    assetbundle: AssetBundleConfig = field(default_factory=AssetBundleConfig)
    groups: dict[str, "Config"] = field(default_factory=dict)

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
