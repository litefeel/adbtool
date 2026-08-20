import argparse

from ..cmd import call_argv, getAdb
from ..config import Config
from . import adbdevice


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    del cfg
    adb = getAdb()

    if args.devices is None:
        _, returncode = call_argv([adb, *args.adb_args], printOutput=True)
        if returncode != 0:
            raise SystemExit(returncode)
        return

    serials, _ = adbdevice.doArgumentParser(args)
    if args.devices == [] or not serials:
        return

    last_returncode = 0
    for serial in serials:
        _, returncode = call_argv([adb, "-s", serial, *args.adb_args], printOutput=True)
        if returncode != 0:
            last_returncode = returncode

    if last_returncode != 0:
        raise SystemExit(last_returncode)


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.usage = "%(prog)s [-h] [-d [DEVICES ...]] -- [adb_args ...]"
    adbdevice.addArgumentParser(parser)
