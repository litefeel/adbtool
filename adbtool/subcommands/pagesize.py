"""
分析 SO 文件的页面大小信息工具

这个模块提供了用于分析 SO 文件的 LOAD 段信息的功能。它可以：
- 分析单个 SO 文件的页面大小信息
- 递归分析目录下所有 SO 文件的页面大小信息
- 通过 objdump 工具提取 SO 文件的 LOAD 段信息
"""

import argparse
import os


from ..cmd import call, get_objdump
from ..config import Config
from ..errors import raise_error
from . import adbdevice


def do_file(file: str) -> None:
    if not os.path.isfile(file):
        raise_error(f"file not fond:{file}")

    # 从配置中获取apksigner路径
    objdump = get_objdump()
    cmd = f'"{objdump}" -p "{file}"'
    output, isOk = call(cmd)
    if isOk:
        print(file)
        for line in output.splitlines():
            if line.lstrip().startswith("LOAD"):
                print(line)
    else:
        print(output)


def _collect_files(input_dir: str, filelist: list[str]) -> None:
    for root, dir, files in os.walk(input_dir):
        for f in files:
            if not f.endswith(".so"):
                continue
            input_file = os.path.join(root, f)
            filelist.append(input_file)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    ospath = args.path
    files: list[str] = []
    if os.path.isfile(ospath):
        files.append(ospath)
    elif os.path.isdir(ospath):
        _collect_files(ospath, files)
    else:
        raise_error(f"abpath is not exits:{ospath}")

    for file in files:
        do_file(file)


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", help="so file or folder")
    adbdevice.addArgumentParser(parser)
