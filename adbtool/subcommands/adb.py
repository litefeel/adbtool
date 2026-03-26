import argparse

from ..cmd import call_argv, getAdb
from ..config import Config


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    del cfg
    _, returncode = call_argv([getAdb(), *args.adb_args], printOutput=True)
    if returncode != 0:
        raise SystemExit(returncode)


def addcommand(_: argparse.ArgumentParser) -> None:
    pass
