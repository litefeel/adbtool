import argparse

from ..cmd import call_argv, getHdc
from ..config import Config
from . import hdcdevice


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    hdc = getHdc(cfg.hdc)

    if args.devices is None:
        _, returncode = call_argv([hdc, *args.hdc_args], printOutput=True)
        if returncode != 0:
            raise SystemExit(returncode)
        return

    serials, _ = hdcdevice.doArgumentParser(args, hdc)
    if args.devices == [] or not serials:
        return

    last_returncode = 0
    for serial in serials:
        _, returncode = call_argv([hdc, "-t", serial, *args.hdc_args], printOutput=True)
        if returncode != 0:
            last_returncode = returncode

    if last_returncode != 0:
        raise SystemExit(last_returncode)


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.usage = "%(prog)s [-h] [-d [DEVICE]] -- [hdc_args ...]"
    hdcdevice.addArgumentParser(parser)
