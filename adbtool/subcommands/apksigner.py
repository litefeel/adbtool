import argparse
import os
import tempfile
from typing import Optional

from ..cmd import call, getApksigner, getZipalign
from ..config import Config
from . import adbdevice

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


def sign(apks: list[str], key_args: str) -> None:
    if not apks:
        return

    apksigner = getApksigner()
    zipalign = getZipalign()
    last = len(apks) - 1

    with tempfile.TemporaryDirectory() as tempdirname:
        zipaligned = os.path.join(tempdirname, "zipaligned.apk").replace("\\", "/")
        for i in range(0, len(apks)):
            apk = apks[i]
            cmd = f'"{zipalign}"  4 "{apk}" "{zipaligned}"'
            _, isOk = call(cmd, True)
            if os.path.isfile(zipaligned):
                print("zipalign success")
                cmd = f'"{apksigner}" sign {key_args} --out {apk} "{zipaligned}"'
                _, isOk = call(cmd, True)
                print(isOk)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    path = args.apkpath or cfg.install.apkpath or "."
    path = os.path.abspath(os.path.join(BASE_DIR, path))

    ks = args.ks or cfg.sign.ks
    ks_pass = args.ks_pass or cfg.sign.ks_pass
    key_pass = args.key_pass or cfg.sign.key_pass
    ks_key_alias = args.ks_key_alias or cfg.sign.ks_key_alias

    if not ks or not ks_pass:
        ks = os.path.expanduser("~/.android/debug.keystore")
        ks_pass = "pass:android"

    print(ks)
    key_args = f'--ks "{ks}"  --ks-pass {ks_pass}'
    if ks_key_alias and key_pass:
        key_args = f"{key_args} --key-pass {key_pass} --ks-key-alias {ks_key_alias}"

    apks = filterApks(path, args.filter)

    if apks is not None:
        sign([apks], key_args)


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-f", "--filter", nargs="*", help="filtered by file name")
    parser.add_argument("--ks")
    parser.add_argument("--ks-pass", dest="ks_pass")
    parser.add_argument("--ks-key-alias", dest="ks_key_alias")
    parser.add_argument("--key-pass", dest="key_pass")
    # parser.add_argument(
    #     "-r", "--run", action="store_true", help="run app after install"
    # )
    parser.add_argument("apkpath", nargs="?")
    adbdevice.addArgumentParser(parser)
