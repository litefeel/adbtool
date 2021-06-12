import argparse
import os
from typing import Optional

from ..cmd import call, getApksigner
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


def getNewst(apks: list[str]) -> Optional[str]:
    if len(apks) == 0:
        return None
    apks = sorted(apks, key=os.path.getmtime, reverse=True)
    return apks[0]


def filterApks(fileorpath: str, filters) -> Optional[str]:
    apk = fileorpath

    if os.path.isdir(fileorpath):
        apks = getApks(fileorpath, filters)
        if len(apks) == 0:
            print("can not found apk file in %s " % fileorpath)
            exit(1)
        apk = getNewst(apks)
    return apk


def sign(apks: list[str]) -> None:
    adb = getApksigner()
    last = len(apks) - 1

    defaultkeystor = os.path.expanduser("~/.android/debug.keystore")
    print(defaultkeystor)
    # defaultkeystor = r"C:\Users\Administrator\.android\debug.keystore"
    storepass = "android"
    for i in range(0, len(apks)):
        apk = apks[i]
        cmd = '"%s" sign --ks "%s" --ks-pass pass:android "%s"' % (adb, defaultkeystor, apk)
        _, isOk = call(cmd, True)
        print(isOk)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    path = args.apkpath or cfg.install.apkpath or "."
    path = os.path.abspath(os.path.join(BASE_DIR, path))

    apks = filterApks(path, args.filter)

    if apks is not None:
        sign([apks])


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-f", "--filter", nargs="*", help="filtered by file name")
    # parser.add_argument(
    #     "-r", "--run", action="store_true", help="run app after install"
    # )
    parser.add_argument("apkpath", nargs="?")
    adbdevice.addArgumentParser(parser)
