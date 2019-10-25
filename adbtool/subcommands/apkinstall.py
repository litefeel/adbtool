import argparse
import os
import sys
from typing import List

from ..cmd import call, getAdb
from ..config import Config
from . import adbdevice, apkinfo

# BASE_DIR="F:/release"
BASE_DIR = ""


def getApks(path, filters):
    apks = os.listdir(path)
    apks = filter(lambda filename: filename.endswith(".apk"), apks)
    if filters is not None:

        def myfilterfun(filename):
            for f in filters:
                if f not in filename:
                    return False
            return True

        apks = filter(myfilterfun, apks)
    apks = map(lambda filename: os.path.join(path, filename), apks)
    return list(apks)


def getNewst(apks):
    if len(apks) == 0:
        return None
    apks = sorted(apks, key=os.path.getmtime, reverse=True)
    return apks[0]


def filterApks(fileorpath, filters):
    apk = fileorpath
    if os.path.isdir(fileorpath):
        apks = getApks(fileorpath, filters)
        if len(apks) == 0:
            print("can not found apk file in %s " % fileorpath)
            exit(1)
        apk = getNewst(apks)
    return apk


def install(apks: List[str], serials: List[str], run: bool) -> None:
    adb = getAdb()
    last = len(apks) - 1
    for i in range(0, len(apks)):
        apk = apks[i]
        isrun = run and last == i
        for serial in serials:
            cmd = '%s -s %s install -r "%s"' % (adb, serial, apk)
            _, isOk = call(cmd, True)
            print(isOk)
            if isOk and isrun:
                activity = apkinfo.parse(apk)
                cmd = '%s -s %s shell am start -S "%s"' % (adb, serial, activity)
                call(cmd)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    isOk, serials, devices = adbdevice.doArgumentParser(args)
    if isOk:
        exit(0)

    path = args.apkpath or cfg.install.apkpath or "."
    path = os.path.abspath(os.path.join(BASE_DIR, path))

    apks = filterApks(path, args.filter)

    if serials is not None and apks is not None:
        install([apks], serials, args.run or cfg.install.run)


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-f", "--filter", nargs="*", help="filtered by file name")
    parser.add_argument(
        "-r", "--run", action="store_true", help="run app after install"
    )
    parser.add_argument("apkpath", nargs="?")
    adbdevice.addArgumentParser(parser)
