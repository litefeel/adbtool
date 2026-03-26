import argparse
import os

from ..cmd import call, getAdb
from ..config import Config
from . import adbdevice, apkinfo

# BASE_DIR="F:/release"
BASE_DIR = ""


def getApks(path, filters):
    apks = [filename for filename in os.listdir(path) if filename.endswith(".apk")]
    if filters is not None:

        def myfilterfun(filename):
            for f in filters:
                if f not in filename:
                    return False
            return True

        apks = [filename for filename in apks if myfilterfun(filename)]
    return [os.path.join(path, filename) for filename in apks]


def getNewst(apks: list[str]) -> str | None:
    if len(apks) == 0:
        return None
    apks = sorted(apks, key=os.path.getmtime, reverse=True)
    return apks[0]


def filterApks(fileorpath: str, filters) -> str | None:
    apk = fileorpath

    if os.path.isdir(fileorpath):
        apks = getApks(fileorpath, filters)
        if len(apks) == 0:
            print("can not found apk file in %s " % fileorpath)
            exit(1)
        apk = getNewst(apks)
    return apk


def install(apks: list[str], serials: list[str], run: bool) -> None:
    adb = getAdb()
    last = len(apks) - 1
    for i, apk in enumerate(apks):
        isrun = run and last == i
        for serial in serials:
            cmd = '"%s" -s %s install -r "%s"' % (adb, serial, apk)
            _, isOk = call(cmd, True)
            print(isOk)
            if isOk and isrun:
                apkinfo.run(apk, [serial])


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    serials, devices = adbdevice.doArgumentParser(args)
    if not serials:
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
