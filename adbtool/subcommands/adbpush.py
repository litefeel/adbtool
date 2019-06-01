import argparse
import hashlib
import json
import os
from typing import Callable, Dict

from litefeel.pycommon.io import read_file, write_file

from ..cmd import call, getAdb
from . import adbdevice

prefixLocal = "D:/work/MFM_CODE_Client/Trunk/MagicDoor/VFS/Android2/"
prefixRemote = "/sdcard/"

date_dict: Dict[str, str] = {}
g_serial = ""
hashfunc: Callable[[str], str]


g_local = ""
g_args = None


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
    return str(os.path.getmtime(g_local))


def parsePrefix(prefix):
    if prefix is not None and len(prefix) == 2:
        return (prefix[0], prefix[1])
    return (prefixLocal, prefixRemote)


def load_json(filename):
    if filename is None:
        return {}
    if os.path.exists(filename):
        return json.loads(read_file(filename))
    return {}


def pull(file: str, prefixLocal, prefixRemote):
    file = file.replace("\\", "/")
    local = file
    remote = file
    if file.startswith(prefixLocal):
        remote = prefixRemote + file[len(prefixLocal) :]

    _, isOk = call(
        '%s -s %s pull "%s" "%s"' % (getAdb(), g_serial, remote, local), True
    )
    return isOk


def push(file: str, prefixLocal, prefixRemote):
    file = file.replace("\\", "/")
    local = file
    remote = file
    refname: str = file
    if file.startswith(prefixLocal):
        remote = prefixRemote + file[len(prefixLocal) :]
        refname = file[len(prefixLocal) :]

    oldhash = date_dict.get(refname, "")
    nowhash = hashfunc(local)
    if oldhash != nowhash:
        rellocal = os.path.relpath(local, ".")
        call('%s -s %s push "%s" "%s"' % (getAdb(), g_serial, rellocal, remote), True)
        date_dict[refname] = nowhash


def filePush(path, prefixLocal, prefixRemote):
    files = os.listdir(path)
    for f in files:
        file = "%s/%s" % (path, f)
        if os.path.isfile(file):
            push(file, prefixLocal, prefixRemote)


def walkPush(path, prefixLocal, prefixRemote):
    for root, _, files in os.walk(path):
        for f in files:
            push("%s/%s" % (root, f), prefixLocal, prefixRemote)


def push_all(paths, local, remote, serial, hashjson):
    global g_serial, date_dict
    g_serial = serial

    if hashjson is not None:
        if not pull(hashjson, local, remote):
            if os.path.isfile(hashjson):
                os.remove(hashjson)

    # print(hashjsonfile)
    date_dict = load_json(hashjson)

    if len(paths) == 0:
        paths.append(".")
    for path in paths:
        path = os.path.abspath(path)
        if os.path.isfile(path):
            push(path, local, remote)
        elif os.path.isdir(path):
            if g_args.recursion:
                walkPush(path, local, remote)
            else:
                filePush(path, local, remote)
        else:
            print("%s: No such file or directory" % path)

    if hashjson is not None:
        write_file(hashjson, json.dumps(date_dict, sort_keys=True, indent=4))
        push(hashjson, local, remote)


def docommand(args):
    isOk, serials, devices = adbdevice.doArgumentParser(args)
    if isOk:
        exit(0)

    global g_args, g_local, hashfunc
    g_args = args
    g_local, remote = parsePrefix(args.prefix)

    paths = args.path[:]

    hashfunc = file_mtime if args.hash == "mtime" else file_sha1

    for device in devices:
        hashjson = "%s_%s.json" % (device.model, device.serial)
        hashjson = os.path.abspath(hashjson)
        push_all(paths, g_local, remote, device.serial, hashjson)


def addcommand(parser: argparse.ArgumentParser):
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
        "-p",
        dest="prefix",
        nargs=2,
        help="local prefix and remote prefix, will replace local prefix to remote prefix",
    )
    parser.add_argument("path", nargs="*", help="file or directory")
    adbdevice.addArgumentParser(parser)
