from litefeel.pycommon.io import read_file
import yaml
from var_dump import var_dump


def get_value(key, map):
    if map is not None:
        return map.get(key, None)
    return None


class PushConfig:
    def __init__(self):
        self.localdir = "."
        self.remotedir = "/sdcard"
        self.recursion = False
        self.paths = []

    def load(self, obj):
        localdir = get_value("localdir", obj)
        if localdir is not None:
            self.localdir = localdir
        remotedir = get_value("remotedir", obj)
        if remotedir is not None:
            self.remotedir = remotedir
        paths = get_value("paths", obj)
        if paths is not None:
            self.paths = paths
        recursion = get_value("recursion", obj)
        if recursion is not None:
            self.recursion = recursion == True


class Config:
    def __init__(self):
        self.push = PushConfig()

    def load(self, obj):
        push = get_value("push", obj)
        if push is not None:
            self.push.load(push)

    def load_config(self, filename: str):
        data = read_file(filename)
        obj = yaml.load(data, Loader=yaml.loader.BaseLoader)
        var_dump(obj)
        self.load(obj)


if __name__ == "__main__":
    cfg = Config()
    cfg.load_config("test/config.yml")

