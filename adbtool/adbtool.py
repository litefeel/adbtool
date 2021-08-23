import argparse
import os
from argparse import _SubParsersAction
from typing import Any

from litefeel.pycommon.io import read_file

from .config import Config
from .subcommands import (
    adbdevice,
    adbpush,
    apkinfo,
    apkinstall,
    apkuninstall,
    apksigner,
    assetbundleinfo,
)

_VERSION_FILE_NAME = "version.txt"


def get_version() -> str:
    dir_of_this_script = os.path.split(__file__)[0]
    version_file_path = os.path.join(dir_of_this_script, _VERSION_FILE_NAME)
    return read_file(version_file_path).strip()


class Command:
    def __init__(self, name: str, command: Any, help: str):
        self.name = name
        self.command = command
        self.help = help


def addsubcommands(subparser: argparse._SubParsersAction, commands: list[Command]) -> None:
    for cmd in commands:
        parser = subparser.add_parser(cmd.name, help=cmd.help)
        parser.set_defaults(docommand=cmd.command.docommand)
        cmd.command.addcommand(parser)


def add_global_params(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-c", "--config", dest="config", help="global config")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )


def main(_args=None):
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options]", description="show android device list"
    )

    add_global_params(parser)

    commands = [
        Command("devices", adbdevice, "show android device list"),
        Command("push", adbpush, "push files to android device"),
        Command("install", apkinstall, "install apk file"),
        Command("uninstall", apkuninstall, "uninstall apk file"),
        Command("apk", apkinfo, "show apk packageName/activityName"),
        Command("sign", apksigner, "sign apk with android debug(only windows)"),
        Command("ab", assetbundleinfo, "extract unity asset bundle information"),
    ]

    subparser = parser.add_subparsers(title="sub commands", dest="subcommand")
    addsubcommands(subparser, commands)

    args = parser.parse_args(_args)
    if args.subcommand is None:
        parser.print_help()
        exit(0)

    cfg = Config()
    if args.config is not None:
        cfg.load_config(args.config)
    args.docommand(args, cfg)


# -------------- main ----------------
if __name__ == "__main__":
    main()
