import argparse
import json
import os
import os.path
from cmd import call, getAdb
from typing import Dict

from litefeel.pycommon.io import read_file, write_file

import adbdevice

prefixLocal = "D:/work/MFM_CODE_Client/Trunk/MagicDoor/VFS/Android2/"
prefixRemote = "/sdcard/"

date_dict: Dict[str, float] = {}
g_serial = ""


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

    oldtime = date_dict.get(refname, 0)
    mtime = os.path.getmtime(local)
    if mtime != oldtime:
        rellocal = os.path.relpath(local, ".")
        call('%s -s %s push "%s" "%s"' % (getAdb(), g_serial, rellocal, remote), True)
        date_dict[refname] = mtime


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


def push_all(paths, local, remote, serial, datejson):
    global g_serial, date_dict
    g_serial = serial

    if datejson is not None:
        if not pull(datejson, local, remote):
            if os.path.isfile(datejson):
                os.remove(datejson)

    # print(datejsonfile)
    date_dict = load_json(datejson)

    if len(paths) == 0:
        paths.append(".")
    for path in paths:
        path = os.path.abspath(path)
        if os.path.isfile(path):
            push(path, local, remote)
        elif os.path.isdir(path):
            if args.recursion:
                walkPush(path, local, remote)
            else:
                filePush(path, local, remote)
        else:
            print("%s: No such file or directory" % path)

    if datejson is not None:
        write_file(datejson, json.dumps(date_dict, sort_keys=True, indent=4))
        push(datejson, local, remote)


# -------------- main ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options] [path]", description="push file to android device"
    )
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
        dest="datejson",
        action="store",
        nargs="?",
        default="",
        help="date json file, default: ./$deviceMode_$deviceSerial.json",
    )
    parser.add_argument(
        "-p",
        dest="prefix",
        nargs=2,
        help="local prefix and remote prefix, will replace local prefix to remote prefix",
    )
    parser.add_argument("path", nargs="*", help="file or directory")
    adbdevice.addArgumentParser(parser)

    args = parser.parse_args()
    isOk, serials, devices = adbdevice.doArgumentParser(args)
    if isOk:
        exit(0)

    local, remote = parsePrefix(args.prefix)

    paths = args.path[:]

    for device in devices:
        datejson = "%s_%s.json" % (device.model, device.serial)
        datejson = os.path.abspath(datejson)
        push_all(paths, local, remote, device.serial, datejson)
