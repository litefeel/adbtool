from litefeel.pycommon.io import read_file
import yaml
from var_dump import var_dump


def get_value(key, map, default):
    if map is not None:
        return map.get(key, default)
    return None


def get_value_bool(key, map, default):
    if map is not None:
        value = map.get(key, default)
        return value == "true" or value == "True" or value == True

    return False


def copy_bool(key, map, obj, default=False):
    value = get_value_bool(key, map, default)
    setattr(obj, key, value)


def copy_value(key, map, obj, default=None):
    value = get_value(key, map, default)
    setattr(obj, key, value)


def copy_subconfig(key, map, subconfig):
    value = get_value(key, map, None)
    if value is not None:
        subconfig.load(value)


class PushConfig:
    def __init__(self):
        self.localdir = "."
        self.remotedir = "/sdcard"
        self.recursion = False
        self.paths = []

    def load(self, obj):
        copy_value("localdir", obj, self, ".")
        copy_value("remotedir", obj, self, "/sdcard")
        copy_value("paths", obj, self, [])
        copy_bool("recursion", obj, self, False)


class ApkConfig:
    def __init__(self):
        self.apkpath = None
        self.run = False

    def load(self, obj):
        copy_value("apkpath", obj, self, None)
        copy_bool("run", obj, self, False)


class Config:
    def __init__(self):
        self.push = PushConfig()
        self.apk = ApkConfig()

    def load(self, obj):
        copy_subconfig("push", obj, self.push)
        copy_subconfig("apk", obj, self.apk)

    def load_config(self, filename: str):
        data = read_file(filename)
        obj = yaml.load(data, Loader=yaml.loader.BaseLoader)
        var_dump(obj)
        self.load(obj)


if __name__ == "__main__":
    cfg = Config()
    cfg.load_config("tests/config.yml")
    var_dump(cfg)

