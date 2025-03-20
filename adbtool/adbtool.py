import argparse
import importlib.metadata
import os
from typing import Any

from .config import Config
from .subcommands import (adbdevice, adbpull, adbpush, apkinfo, apkinstall,
                          apksigner, apkuninstall, assetbundleinfo, asshader,
                          il2cpp, malioc, pagesize, procfd)


def get_version() -> str:
    return importlib.metadata.version("adbtool")


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
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--config", dest="config", help="global config")
    group.add_argument(
        "-d",
        "--default_config",
        action="store_const",
        const="~/adbtool.yml",
        help="default global config: ~/adbtool.yml",
    )
    group.add_argument(
        "-g",
        "--group",
        help="select group from config, default global config: ~/adbtool.yml",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {get_version()}")


def main(_args=None):
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options]", description="show android device list"
    )

    add_global_params(parser)

    commands = [
        Command("devices", adbdevice, "show android device list"),
        Command("push", adbpush, "push files to android device"),
        Command("pull", adbpull, "pull files to android device"),
        Command("install", apkinstall, "install apk file"),
        Command("uninstall", apkuninstall, "uninstall apk file"),
        Command("apk", apkinfo, "show apk packageName/activityName"),
        Command("sign", apksigner, "sign apk with android debug(only windows)"),
        Command("ab", assetbundleinfo, "extract unity asset bundle information"),
        Command("il2cpp", il2cpp, "extract unity il2cpp information"),
        Command("asshader", asshader, "simplify asset studio shader preview data"),
        Command("malioc", malioc, "mail offline compile"),
        Command("procfd", procfd, "print proc all fd"),
        Command("pagesize", pagesize, "print page size for so file"),
    ]

    subparser = parser.add_subparsers(title="sub commands", dest="subcommand")
    addsubcommands(subparser, commands)

    args = parser.parse_args(_args)
    if args.subcommand is None:
        parser.print_help()
        exit(0)

    cfg = Config()
    configpath = args.config or args.default_config
    if configpath:
        realpath = os.path.expanduser(configpath)
        if not os.path.isfile(realpath):
            parser.error(f"can not fond config file: {configpath}")

        cfg.load_config(realpath)

    args.docommand(args, cfg)


# -------------- main ----------------
if __name__ == "__main__":
    main()
