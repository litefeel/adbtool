import argparse
import os

from ..cmd import call, getAdb
from ..config import Config, PullConfig
from . import adbdevice

g_serial = ""

pull_cfg: PullConfig


def pull(file: str, localdir: str, remotedir: str, stat: bool) -> None:
    remote = f"{remotedir}/{file}"
    local = f"{localdir}/{os.path.dirname(file)}"

    stat_args = "-a" if stat else ""

    cmd = f'"{getAdb()}" -s {g_serial} pull {stat_args} "{remote}" "{local}"'
    call(cmd, True)


def pull_all(cfg: PullConfig, serial: str) -> None:
    global g_serial
    g_serial = serial

    local = cfg.localdir
    remote = cfg.remotedir

    for path in cfg.paths:
        pull(path, local, remote, cfg.stat)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    serials, devices = adbdevice.doArgumentParser(args)
    if not serials:
        exit(0)

    global pull_cfg

    pull_cfg = cfg.pull

    if args.stat:
        pull_cfg.stat = True

    if args.localdir is not None:
        pull_cfg.localdir = args.localdir
    pull_cfg.localdir = os.path.abspath(pull_cfg.localdir).replace("\\", "/")
    if args.remotedir is not None:
        pull_cfg.remotedir = args.remotedir

    paths = args.path[:] or pull_cfg.paths or ["."]
    pull_cfg.paths = [p for p in paths if p]

    for device in devices:
        pull_all(pull_cfg, device.serial)


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-s", "--stat", dest="stat", action="store_true", help="preserve file timestamp and mode"
    )
    parser.add_argument(
        "-l",
        "--localdir",
        dest="localdir",
        help="local prefix and remote prefix, will replace local prefix to remote prefix",
    )
    parser.add_argument(
        "-r",
        "--remotedir",
        dest="remotedir",
        help="local prefix and remote prefix, will replace local prefix to remote prefix",
    )
    parser.add_argument("path", nargs="*", help="file or directory")
    adbdevice.addArgumentParser(parser)
