import argparse
import importlib.metadata
import os
import sys
from dataclasses import dataclass
from typing import Protocol

from .config import Config
from .subcommands import (adb, adbdevice, adbpull, adbpush, apkinfo, apkinstall,
                          apksigner, apkuninstall, assetbundleinfo, asshader,
                          il2cpp, malioc, pagesize, procfd)


def get_version() -> str:
    return importlib.metadata.version("adbtool")


class CommandModule(Protocol):
    def docommand(self, args: argparse.Namespace, cfg: Config) -> None:
        ...

    def addcommand(self, parser: argparse.ArgumentParser) -> None:
        ...


@dataclass(slots=True)
class Command:
    name: str
    command: CommandModule
    help: str
    add_help: bool = True


def addsubcommands(
    subparser: argparse._SubParsersAction, commands: list[Command]
) -> dict[str, argparse.ArgumentParser]:
    command_parsers: dict[str, argparse.ArgumentParser] = {}
    for cmd in commands:
        parser = subparser.add_parser(cmd.name, help=cmd.help, add_help=cmd.add_help)
        parser.set_defaults(docommand=cmd.command.docommand)
        cmd.command.addcommand(parser)
        command_parsers[cmd.name] = parser
    return command_parsers


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
    parser.add_argument(
        "-g",
        "--group",
        help="select group from config, default global config: ~/adbtool.yml",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {get_version()}")


def main(_args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    add_global_params(parser)

    commands = [
        Command("adb", adb, "forward adb arguments to selected devices"),
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
        Command("malioc", malioc, "mali offline compile"),
        Command("procfd", procfd, "print proc all fd"),
        Command("pagesize", pagesize, "print page size for so file"),
    ]

    subparser = parser.add_subparsers(title="sub commands", dest="subcommand")
    command_parsers = addsubcommands(subparser, commands)

    args, extra = parser.parse_known_args(_args)
    if args.subcommand is None:
        if extra:
            parser.error(f"unrecognized arguments: {' '.join(extra)}")
        parser.print_help()
        sys.exit(0)

    cfg = Config()
    configpath = args.config or args.default_config
    if not configpath and args.group:
        configpath = os.path.expanduser("~/adbtool.yml")
    if configpath:
        realpath = os.path.expanduser(configpath)
        if not os.path.isfile(realpath):
            parser.error(f"can not find config file: {configpath}")

        cfg.load_config(realpath)

    if args.group:
        cfg = cfg.groups.get(args.group, None)
        if cfg is None:
            parser.error(f"can not find group: {args.group}")

    if args.subcommand == "adb":
        if extra:
            if extra[0] != "--":
                parser.error("adb arguments must follow '--'")
            args.adb_args = extra[1:]
        elif args.devices == []:
            args.adb_args = []
        elif args.devices is None:
            command_parsers["adb"].print_help()
            sys.exit(0)
        else:
            parser.error("adb arguments must follow '--'")
    elif extra:
        parser.error(f"unrecognized arguments: {' '.join(extra)}")

    args.docommand(args, cfg)


# -------------- main ----------------
if __name__ == "__main__":
    main()
