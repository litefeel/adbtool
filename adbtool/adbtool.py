import argparse
import sys
from typing import List

from .config import Config
from .subcommands import adbdevice, adbpush, apkinfo, apkinstall


class Command:
    def __init__(self, name: str, command, help):
        self.name = name
        self.command = command
        self.help = help


def addsubcommands(subparser: argparse._SubParsersAction, commands: List[Command]):
    for cmd in commands:
        parser = subparser.add_parser(cmd.name, help=cmd.help)
        parser.set_defaults(docommand=cmd.command.docommand)
        cmd.command.addcommand(parser)


def add_global_params(parser: argparse.ArgumentParser):
    parser.add_argument("-c", "--config", dest="config", help="global config")


def main():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options]", description="show android device list"
    )

    add_global_params(parser)

    commands = [
        Command("device", adbdevice, "show android device list"),
        Command("push", adbpush, "push files to android device"),
        Command("install", apkinstall, "install apk file"),
        Command("apk", apkinfo, "show apk packageName/activityName"),
    ]

    subparser = parser.add_subparsers(title="sub commands", dest="subcommand")
    addsubcommands(subparser, commands)

    args = parser.parse_args()
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
