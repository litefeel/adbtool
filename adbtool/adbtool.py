import argparse
import sys
from typing import List

from .subcommands import adbdevice


class Command:
    def __init__(self, name: str, addcommand, docommand):
        self.name = name
        self.addcommand = addcommand
        self.docommand = docommand


def addsubcommands(subparser: argparse._SubParsersAction, commands: List[Command]):
    for cmd in commands:
        parser = subparser.add_parser(cmd.name)
        parser.set_defaults(docommand=cmd.docommand)
        cmd.addcommand(parser)


# -------------- main ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options]", description="show android device list"
    )

    commands = [Command("device", adbdevice.addcommand, adbdevice.docommand)]

    subparser = parser.add_subparsers(title="sub commands", dest="subcommand")
    addsubcommands(subparser, commands)

    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    else:
        args.docommand(args)
