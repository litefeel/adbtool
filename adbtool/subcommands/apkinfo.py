import argparse
from os import error
import os.path
import re

from ..cmd import call, getAapt, getAdb
from ..config import Config
from ..errors import raise_error
from . import adbdevice


def firstitem(arr):
    return arr[0] if len(arr) > 0 else None


def parse(apk):
    aapt = getAapt()
    cmd = '"%s" dump badging "%s"' % (aapt, apk)
    output, isOk = call(cmd)
    if isOk:
        packagename = firstitem(re.findall(r"package: name='(\S+?)'", output))
        activityname = firstitem(
            re.findall(r"launchable-activity: name='(\S+?)'", output)
        )
        return (packagename, activityname, output)
    return (None, None, None)


def stop(apk, serials):
    packagename, _, _ = parse(apk)
    adb = getAdb()
    for serial in serials:
        cmd = '"%s" -s %s shell am force-stop "%s"' % (adb, serial, packagename)
        call(cmd)


def run(apk, serials):
    packagename, activityname, _ = parse(apk)
    adb = getAdb()
    for serial in serials:
        cmd = '"%s" -s %s shell am start -S "%s/%s"' % (
            adb,
            serial,
            packagename,
            activityname,
        )
        call(cmd)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    if args.apkpath is not None:
        cfg.apk.apkpath = args.apkpath

    if cfg.apk.apkpath is None:
        raise_error("Missing parameter: apkpath")
        return

    apkpath = os.path.abspath(cfg.apk.apkpath)
    if not os.path.isfile(apkpath):
        raise_error("apkpath is not file")
        return

    if args.run:
        serials, _ = adbdevice.doArgumentParser(args)
        run(apkpath, serials)
    elif args.stop:
        serials, _ = adbdevice.doArgumentParser(args)
        stop(apkpath, serials)
    else:
        packagename, activityname, output = parse(apkpath)
        print(output)


def addcommand(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-r", "--run", action="store_true", help="run app")
    group.add_argument("-s", "--stop", action="store_true", help="run app")
    parser.add_argument("apkpath", nargs="?")
    adbdevice.addArgumentParser(parser)
