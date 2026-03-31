import argparse
import os

from ..cmd import call_argv, getAdb
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


def filterApks(fileorpath: str, filters) -> list[str]:
    if os.path.isdir(fileorpath):
        apks = getApks(fileorpath, filters)
        if len(apks) == 0:
            print("can not found apk file in %s " % fileorpath)
            exit(1)
        return [getNewst(apks)]
    return [fileorpath]


def install(apks: list[str], serials: list[str], run: bool, force: bool) -> None:
    adb = getAdb()
    subcommand = "install-multi-package" if len(apks) > 1 else "install"
    install_args = ["-d", "-r"] if force else ["-r"]
    target_apk = apks[-1]

    for serial in serials:
        cmd = [adb, "-s", serial, subcommand, *install_args, *apks]
        _, code = call_argv(cmd, True)
        isOk = code == 0
        print(isOk)
        if isOk and run:
            apkinfo.run(target_apk, [serial])


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    serials, devices = adbdevice.doArgumentParser(args)
    if not serials:
        exit(0)

    paths = args.apkpath or [cfg.install.apkpath or "."]
    paths = [os.path.abspath(os.path.join(BASE_DIR, path)) for path in paths]

    apks: list[str] = []
    for path in paths:
        apks.extend(filterApks(path, args.filter))

    if serials is not None and apks:
        install(apks, serials, args.run or cfg.install.run, args.force)


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-f", "--force", action="store_true", help="install with adb -d -r")
    parser.add_argument("--filter", nargs="*", help="filtered by file name")
    parser.add_argument(
        "-r", "--run", action="store_true", help="run app after install"
    )
    parser.add_argument("apkpath", nargs="*")
    adbdevice.addArgumentParser(parser)
