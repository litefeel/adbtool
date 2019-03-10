import argparse
import json
import os
import os.path
from cmd import call, getAdb

from litefeel.pycommon.io import read_file, write_file

import adbdevice

# bat
# @echo off
# rem %cd% 工作目录/当前目录
# rem %~dp0 bat文件所在目录

# rem 启用延迟扩展，一行语句中延迟变量赋值
# setlocal ENABLEDELAYEDEXPANSION

# set rpstr=E:/work/zeus/GameEditors/UIEdit/res/
# set xxx=/sdcard/hookzeus/
# set localpath=%cd%/%1
# set localpath=%localpath:\=/%

# set remotepath=%localpath:E:/work/zeus/GameEditors/UIEdit/res/=!xxx!%
# echo %localpath%
# echo %remotepath%
# adb push %localpath% %remotepath%


prefixLocal = "D:/work/MFM_CODE_Client/MagicDoor/VFS/Android/main/"
prefixRemote = "/sdcard/main/"

date_dict = {}
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


def push(file: str, prefixLocal, prefixRemote):
    file = file.replace("\\", "/")
    local = file
    remote = file
    refname = file
    if file.startswith(prefixLocal):
        remote = prefixRemote + file[len(prefixLocal) :]
        refname = file[len(prefixLocal) :]

    oldtime = date_dict.get(refname, 0)
    mtime = os.path.getmtime(local)
    if mtime != oldtime:
        call('%s -s %s push "%s" "%s"' % (getAdb(), g_serial, local, remote), True)
        date_dict[refname] = mtime


def filePush(path, prefixLocal, prefixRemote):
    files = os.listdir(path)
    for f in files:
        file = "%s/%s" % (path, f)
        if os.path.isfile(file):
            push(file, prefixLocal, prefixRemote)


def walkPush(path, prefixLocal, prefixRemote):
    for root, dirs, files in os.walk(path):
        for f in files:
            push("%s/%s" % (root, f), prefixLocal, prefixRemote)


def push_all(paths, local, remote, serial, datejson):
    global g_serial, date_dict
    g_serial = serial

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
        push_all(paths, local, remote, device.serial, datejson)
