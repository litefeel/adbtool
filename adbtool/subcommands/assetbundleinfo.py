import argparse
from genericpath import isdir, isfile
import os
from posixpath import abspath
import re
import tempfile
import shutil
from litefeel.pycommon.io import makedirs
import asyncio

from ..cmd import call_async, get_unity_binary2text, get_unity_webextract
from ..config import Config
from ..errors import raise_error
from . import adbdevice

INFO_EXT = ".txt"


async def bine2text(file, unity_editor_dir):
    binary2text = get_unity_binary2text(unity_editor_dir)
    cmd = f'"{binary2text}" "{file}"'
    output, isOk = await call_async(cmd)
    if isOk:
        return file + ".txt"


async def extract(file, unity_editor_dir):
    webextract = get_unity_webextract(unity_editor_dir)
    cmd = f'"{webextract}" "{file}"'
    output, isOk = await call_async(cmd)
    if isOk:
        for root, _, files in os.walk(file + "_data"):
            for f in files:
                if not f.endswith(".resS"):
                    return os.path.join(root, f)


async def do_file(input: str, output: str, unity_editor_dir: str, sem: asyncio.Semaphore) -> None:
    if not os.path.isfile(input):
        raise_error(f"file not fond:{input}")

    async with sem:
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpunityfile = os.path.join(tmpdirname, "tmp.unity3d")
            shutil.copy(input, tmpunityfile)
            outfile = await extract(tmpunityfile, unity_editor_dir)
            assert outfile
            outfile = await bine2text(outfile, unity_editor_dir)
            assert outfile
            makedirs(output, True)
            shutil.copy(outfile, output)


def _collect_files(
    input_dir: str, output_dir: str, ext: str, filelist: list[tuple[str, str]]
) -> None:
    for root, dir, files in os.walk(input_dir):
        for f in files:
            if ext and not f.endswith(ext):
                continue
            input_file = os.path.join(root, f)
            rel_name = os.path.relpath(input_file, input_dir)
            output_file = os.path.join(output_dir, rel_name + INFO_EXT)
            filelist.append((input_file, output_file))


async def do_files(filelist: list[tuple[str, str]], unity_editor_dir: str) -> None:
    task_list = []
    sem = asyncio.Semaphore(16)
    for input, output in filelist:
        task = asyncio.create_task(do_file(input, output, unity_editor_dir, sem))
        task_list.append(task)
    await asyncio.gather(*task_list)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    output = args.output
    abpath = args.abpath
    unity_editor_dir = args.unityeditordir
    files: list[tuple[str, str]] = []
    if os.path.isfile(abpath):
        if output is None:
            output = abpath + INFO_EXT
        elif os.path.isdir(output):
            output = os.path.join(output, os.path.basename(abpath) + INFO_EXT)
        files.append((abpath, output))
    elif os.path.isdir(abpath):
        if output is None:
            output = abpath
        elif os.path.isfile(output):
            raise_error("output cannot be file when abpath is folder")
        _collect_files(abpath, output, args.ext, files)
    else:
        raise_error(f"abpath is not exits:{abpath}")

    asyncio.run(do_files(files, unity_editor_dir))


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-o", "--output", help="output file or folder")
    parser.add_argument(
        "-e", "--ext", nargs="?", const="", default=".unity3d", help="assetbundle extions name"
    )
    parser.add_argument("-u", "--unityeditordir", nargs="?", help="unity editor folder")
    parser.add_argument("abpath", help="assetbundle file or folder")
    adbdevice.addArgumentParser(parser)
