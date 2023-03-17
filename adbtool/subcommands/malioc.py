import argparse
import os
import re
import tempfile
from dataclasses import dataclass
from typing import Iterator

from litefeel.pycommon.io import read_lines, write_file, write_lines

from ..cmd import call, get_malioc
from ..config import Config
from ..errors import raise_error

_SHADER_NAME_REGEX = re.compile('Shader "(.+)" {')


@dataclass
class ShaderInfo:
    global_keywords: str
    local_keywords: str
    vert: str
    frag: str


def _read_shadername(lines: Iterator[str]) -> str:
    while True:
        line = next(lines)
        if match := _SHADER_NAME_REGEX.match(line):
            return match.group(1)


def _read_keyword(lines: Iterator[str], prefix: str) -> str:
    while True:
        line = next(lines)
        if line.startswith(prefix):
            return line.removeprefix(prefix)


def _read_shader_body(lines: Iterator[str], key: str) -> str:
    _read_keyword(lines, "#ifdef " + key)
    lst: list[str] = []
    empty_last_line = False
    while True:
        line = next(lines)
        if line == "#endif" and empty_last_line:
            return "\n".join(lst)
        lst.append(line)
        empty_last_line = line == ""


def _parse_shader(lines: Iterator[str]) -> tuple[str, list[ShaderInfo]]:
    shadername = _read_shadername(lines)

    infos = []
    try:
        while True:
            global_keywords = _read_keyword(lines, "Global Keywords: ")
            local_keywords = _read_keyword(lines, "Local Keywords: ")
            vert = _read_shader_body(lines, "VERTEX")
            frag = _read_shader_body(lines, "FRAGMENT")
            if "INSTANCING_ON" in global_keywords:
                vert = vert.replace('#version 300 es', '#version 310 es')
                frag = frag.replace('#version 300 es', '#version 310 es')
            infos.append(ShaderInfo(global_keywords, local_keywords, vert, frag))
    except StopIteration:
        pass
    return shadername, infos


def _append_output(text:str, lst:list[str])->None:
    for line in text.replace('\r\n', '\n').splitlines(keepends=False):
        lst.append('    ' + line)


def do_file(file: str, output_file: str) -> None:
    shadername, infos = _parse_shader(iter(read_lines(file)))

    lst = [shadername, "\n"]
    malioc = get_malioc()

    with tempfile.TemporaryDirectory() as tmpdirname:
        vertfile = os.path.join(tmpdirname, "shader.vert")
        fragfile = os.path.join(tmpdirname, "shader.frag")
        outputfile = os.path.join(tmpdirname, "output.txt")
        for info in infos:
            lst.append("=================================================")
            lst.append("Global Keywords:" + info.global_keywords)
            lst.append("Local Keywords:" + info.global_keywords)
            write_file(vertfile, info.vert)
            write_file(fragfile, info.frag)
            lst.append("----------------------vert-----------------------")
            cmd = f'"{malioc}" -d "{vertfile}"'
            output, ok = call(cmd)
            _append_output(output, lst)
            lst.append("----------------------frag----------------------")
            cmd = f'"{malioc}" -d "{fragfile}"'
            output, ok = call(cmd)
            _append_output(output, lst)
            lst.append("")

    write_lines(output_file, lst)


def do_folder(input_dir: str, output_dir: str) -> None:
    for root, dir, files in os.walk(input_dir):
        for f in files:
            if not f.endswith(".shader"):
                continue
            input_file = os.path.join(root, f)
            rel_name = os.path.relpath(input_file, input_dir)
            output_file = os.path.join(output_dir, rel_name)
            do_file(input_file, output_file)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    output = args.output
    shaderpath = args.shaderpath

    if os.path.isfile(shaderpath):
        if output is None:
            output = shaderpath + ".txt"
        elif os.path.isdir(output):
            output = os.path.join(output, os.path.basename(shaderpath))
        do_file(shaderpath, output)
    # elif os.path.isdir(shaderpath):
    #     if output is None:
    #         output = shaderpath
    #     elif os.path.isfile(output):
    #         raise_error("output cannot be file when shaderpath is folder")
    #     do_folder(shaderpath, output, SimplifyType(args.simplify))
    else:
        raise_error(f"shaderpath is not exits:{shaderpath}")


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("shaderpath", help="asset stuido shader preview file")
    parser.add_argument("output", nargs="?", help="output file or folder")


# if __name__ == "__main__":
#     do_file(r"E:\Projects\adbtool\adbtool\subcommands\Untitled-2.cpp", r"E:\Projects\adbtool\adbtool\subcommands\Untitled-2.cpp.txt")
