import argparse
import sys
from typing import List

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


# -------------- main ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options]", description="show android device list"
    )

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
    else:
        args.docommand(args)
