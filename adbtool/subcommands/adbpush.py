import argparse
import hashlib
import json
import os
from typing import Callable

from litefeel.pycommon.io import read_file, write_file

from ..cmd import call, getAdb
from ..config import Config, PushConfig
from . import adbdevice

date_dict: dict[str, str] = {}
g_serial = ""
hashfunc: Callable[[str], str]
errors = []

push_cfg: PushConfig


def file_sha1(file: str) -> str:
    sha1 = hashlib.sha1()
    with open(file, mode="rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


def file_mtime(file: str) -> str:
    return str(os.path.getmtime(push_cfg.localdir))


def load_json(filename: str) -> dict:
    if filename is None:
        return {}
    if os.path.exists(filename):
        return json.loads(read_file(filename))
    return {}


def pull(file: str, prefixLocal: str, prefixRemote: str) -> bool:
    file = file.replace("\\", "/")
    local = file
    remote = file
    if file.startswith(prefixLocal):
        remote = prefixRemote + file[len(prefixLocal) :]

    _, isOk = call(
        '"%s" -s %s pull "%s" "%s"' % (getAdb(), g_serial, remote, local), True
    )
    return isOk


def push(file: str, prefixLocal: str, prefixRemote: str, dontpush: bool) -> None:
    file = file.replace("\\", "/")
    local = file
    remote = file
    relname: str = file
    if file.startswith(prefixLocal):
        remote = prefixRemote + file[len(prefixLocal) :]
        relname = file[len(prefixLocal) :]

    oldhash = date_dict.get(relname, "")
    nowhash = hashfunc(local)

    if oldhash != nowhash or dontpush:
        isOk = True
        if not dontpush:
            rellocal = os.path.relpath(local, ".")
            _, isOk = call(
                '"%s" -s %s push "%s" "%s"' % (getAdb(), g_serial, rellocal, remote), True
            )
        if isOk:
            date_dict[relname] = nowhash
        else:
            errors.append(relname)


def filePush(path, prefixLocal, prefixRemote, dontpush):
    files = os.listdir(path)
    for f in files:
        file = "%s/%s" % (path, f)
        if os.path.isfile(file):
            push(file, prefixLocal, prefixRemote, dontpush)


def walkPush(path, prefixLocal, prefixRemote, dontpush):
    for root, _, files in os.walk(path):
        for f in files:
            push("%s/%s" % (root, f), prefixLocal, prefixRemote, dontpush)


def push_all(cfg: PushConfig, serial: str, hashjson: str) -> None:
    global g_serial, date_dict
    g_serial = serial
    errors.clear()

    local = cfg.localdir
    remote = cfg.remotedir

    if hashjson is not None:
        if not pull(hashjson, local, remote):
            if os.path.isfile(hashjson):
                os.remove(hashjson)

    # print(hashjsonfile)
    date_dict = load_json(hashjson)

    for path in cfg.paths:
        path = os.path.abspath(path)
        if os.path.isfile(path):
            push(path, local, remote, cfg.dontpush)
        elif os.path.isdir(path):
            if cfg.recursion:
                walkPush(path, local, remote, cfg.dontpush)
            else:
                filePush(path, local, remote, cfg.dontpush)
        else:
            print("%s: No such file or directory" % path)

    if hashjson is not None:
        write_file(hashjson, json.dumps(date_dict, sort_keys=True, indent=4))
        if not cfg.dontpush:
            push(hashjson, local, remote, cfg.dontpush)

    if len(errors) > 0:
        print("error paths:")
        map(print, errors)


def _is_relpath(path, root):
    if not path.startswith(root):
        return False
    if len(path) == len(root):
        return True
    return path[len(root)] == "/"


def _normal_path(p, root):
    if os.path.isabs(p):
        p = p.replace("\\", "/")
    else:
        p = os.path.abspath(p).replace("\\", "/")
        if not _is_relpath(p, root):
            p = os.path.join(root, p)
    p = os.path.abspath(p).replace("\\", "/")
    return p if os.path.exists(p) and _is_relpath(p, root) else None


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    serials, devices = adbdevice.doArgumentParser(args)
    if not serials:
        exit(0)

    global push_cfg

    push_cfg = cfg.push

    if args.dontpush:
        push_cfg.dontpush = True

    if args.localdir is not None:
        push_cfg.localdir = args.localdir
    push_cfg.localdir = os.path.abspath(push_cfg.localdir).replace("\\", "/")
    if args.remotedir is not None:
        push_cfg.remotedir = args.remotedir

    if args.recursion:
        push_cfg.recursion = True

    paths = args.path[:] or push_cfg.paths or ["."]
    paths = [_normal_path(p, push_cfg.localdir) for p in paths]
    push_cfg.paths = [p for p in paths if p]

    global hashfunc
    hashfunc = file_mtime if args.hash == "mtime" else file_sha1

    for device in devices:
        hashjson = "%s_%s.json" % (device.model, device.serial)
        hashjson = os.path.abspath(hashjson)
        push_all(push_cfg, device.serial, hashjson)


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-r", dest="recursion", action="store_true", help="recursion all file"
    )
    parser.add_argument(
        "-n",
        dest="newst",
        action="store_true",
        help="only push new file by last modify files, see -j",
    )
    parser.add_argument(
        "-j",
        dest="hashjson",
        action="store",
        nargs="?",
        default="",
        help="hash json file, default: ./$deviceMode_$deviceSerial.json",
    )
    parser.add_argument(
        "--hash",
        dest="hash",
        nargs="?",
        default="sha1",
        choices=["sha1", "mtime"],
        help="hash function: mtime or sha1, default:mtime",
    )
    parser.add_argument(
        "--localdir",
        dest="localdir",
        help="local prefix and remote prefix, will replace local prefix to remote prefix",
    )
    parser.add_argument(
        "--remotedir",
        dest="remotedir",
        help="local prefix and remote prefix, will replace local prefix to remote prefix",
    )
    parser.add_argument(
        "--dontpush",
        dest="dontpush",
        action="store_true",
        help="only outout json file, not really push file to remote",
    )
    parser.add_argument("path", nargs="*", help="file or directory")
    adbdevice.addArgumentParser(parser)
