import argparse
from genericpath import isdir, isfile
import os
from posixpath import abspath
import re
import tempfile
import shutil

from ..cmd import call, get_unity_binary2text, get_unity_webextract
from ..config import Config
from ..errors import raise_error
from . import adbdevice

INFO_EXT = ".txt"


def bine2text(file, unity_editor_dir):
    binary2text = get_unity_binary2text(unity_editor_dir)
    cmd = f'"{binary2text}" "{file}"'
    output, isOk = call(cmd)
    if isOk:
        return file +".txt"

def extract(file, unity_editor_dir):
    webextract = get_unity_webextract(unity_editor_dir)
    cmd = f'"{webextract}" "{file}"'
    output, isOk = call(cmd)
    if isOk:
        for root, dirs, files in os.walk(file+"_data"):
            for f in files:
                if not f.endswith('.resS'):
                    return os.path.join(root, f)
                    
def do_file(input_file, output_file, unity_editor_dir):
    if not os.path.isfile(input_file):
        raise_error(f'file not fond:{input_file}')

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpunityfile = os.path.join(tmpdirname, 'tmp.unity3d')
        shutil.copy(input_file, tmpunityfile)
        outfile = extract(tmpunityfile, unity_editor_dir)
        assert outfile
        outfile = bine2text(outfile, unity_editor_dir)
        assert outfile
        shutil.copy(outfile, output_file)

def do_folder(input_dir:str, output_dir:str, ext:str, unity_editor_dir):
    for root, dir, files in os.walk(input_dir):
        for f in files:
            if ext and not f.endswith(ext):
                continue
            input_file = os.path.join(root, f)
            rel_name = os.path.relpath(input_file, input_dir)
            output_file = os.path.join(output_dir, rel_name + INFO_EXT)
            do_file(input_file, output_file, unity_editor_dir)
            break


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    output = args.output
    abpath = args.abpath
    unity_editor_dir = args.unityeditordir
    if os.path.isfile(abpath):
        if output is None:
            output = abpath + INFO_EXT
        elif os.path.isdir(output):
            output = os.path.join(output, os.path.basename(abpath) + INFO_EXT)
        do_file(abpath, output, unity_editor_dir)
    elif os.path.isdir(abpath):
        if output is None:
            output = abpath
        elif os.path.isfile(output):
            raise_error("output cannot be file when abpath is folder")
        do_folder(abpath, output, args.ext, unity_editor_dir)
    else:
        raise_error(f"abpath is not exits:{abpath}")


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-o", "--output", help="output file or folder")
    parser.add_argument("-e", "--ext", nargs='?', const='', default=".unity3d", help="assetbundle extions name")
    parser.add_argument('-u', '--unityeditordir',nargs='?', help='unity editor folder')
    parser.add_argument("abpath", help="assetbundle file or folder")
    adbdevice.addArgumentParser(parser)
