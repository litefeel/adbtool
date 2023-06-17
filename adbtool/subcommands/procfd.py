import argparse
from enum import IntEnum, auto
import os

from ..cmd import call, getAdb
from ..config import Config, ProcfdConfig
from . import adbdevice

g_serial = ""

# class OutputType(IntEnum):
#     List = 1
#     Count = auto()

def _get_pid(procname: str) -> str:
    cmd = f'"{getAdb()}" -s {g_serial} shell "ps -A | grep {procname}"'
    print(cmd)
    output, isok = call(cmd, False)
    assert output
    if not isok or not output:
        raise BaseException(f"No such process: {procname}")
    return output.split()[1]

def _print_proc_fd(pid: str) -> None:
    cmd = f'"{getAdb()}" -s {g_serial} shell ls -lha /proc/{pid}/fd'
    call(cmd, True)

def _print_proc(cfg: ProcfdConfig, serial: str) -> None:
    global g_serial
    g_serial = serial

    pid = _get_pid(cfg.procname)
    _print_proc_fd(pid)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    serials, devices = adbdevice.doArgumentParser(args)
    if not serials:
        exit(0)

    g_cfg = cfg.procfd

    procname = args.procname or g_cfg.procname
    assert procname
    g_cfg.procname = procname

    for device in devices:
        _print_proc(g_cfg, device.serial)


def addcommand(parser: argparse.ArgumentParser) -> None:
    # parser.add_argument(
    #     "-p",
    #     "--pname",
    #     dest="procname",
    #     help="process name, will pull all files in /proc/<pid>/fd/",
    # )
    # parser.add_argument(
    #     "-t",
    #     "--type",
    #     dest="_type",
    #     help="type 1:count 2:list 3:all",
    # )
    parser.add_argument("procname", nargs="?", help="process name, will pull all files in /proc/<pid>/fd/")
    adbdevice.addArgumentParser(parser)
