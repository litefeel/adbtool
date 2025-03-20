


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
    output = args.output
    abpath = args.abpath
    unity_editor_dir = args.unityeditordir or cfg.assetbundle.unityeditordir
    files: list[str] = []
    if os.path.isfile(abpath):
        files.append(abpath)
    elif os.path.isdir(abpath):
        _collect_files(abpath, files)
    else:
        raise_error(f"abpath is not exits:{abpath}")

    for file in files:
        do_file(file)


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", help="so file or folder")
    adbdevice.addArgumentParser(parser)
