import argparse
import os
from enum import IntEnum, auto

from litefeel.pycommon.io import makedirs, read_lines, write_lines

from ..config import Config
from ..errors import raise_error


class SimplifyType(IntEnum):
    Format = 1
    RemoveContent = auto()
    OnlyKeyWord = auto()


def _lstrips(lines: list[str]) -> None:
    for i in range(len(lines)):
        lines[i] = lines[i].lstrip()


def _format(lines: list[str]) -> None:
    space = ""
    for i in range(len(lines)):
        line = lines[i]

        prev_space = space
        n = 0
        if "{" in line:
            n += 1
        if "}" in line:
            n -= 1

        if n > 0:
            space += "\t"
        elif n < 0:
            space = space[:-1]

        if "{" in line:
            lines[i] = prev_space + line
        else:
            lines[i] = space + line


def _remove_shader_content(lines: list[str]) -> list[str]:
    skipCurLine = False
    hasSubProgram = False
    output_lines = []
    for line in lines:
        if hasSubProgram:
            if line == '""':
                continue
            if not line.startswith("Keywords {"):
                if '"' in line:
                    skipCurLine = not skipCurLine
                    continue
                if skipCurLine:
                    continue
                else:
                    hasSubProgram = False
        if line.startswith("SubProgram "):
            hasSubProgram = True
        output_lines.append(line)
    return output_lines


def do_file(file: str, output_file: str, simply: SimplifyType) -> None:
    lines = read_lines(file)
    _lstrips(lines)

    if simply == SimplifyType.RemoveContent:
        lines = _remove_shader_content(lines)
    elif simply == SimplifyType.OnlyKeyWord:
        lines = list(set([line for line in lines if "Keywords {" in line]))
        lines.sort()
    _format(lines)
    write_lines(output_file, lines)


def do_folder(input_dir: str, output_dir: str, simply: SimplifyType) -> None:
    for root, dir, files in os.walk(input_dir):
        for f in files:
            if not f.endswith(".shader"):
                continue
            input_file = os.path.join(root, f)
            rel_name = os.path.relpath(input_file, input_dir)
            output_file = os.path.join(output_dir, rel_name)
            do_file(input_file, output_file, simply)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    output = args.output
    shaderpath = args.shaderpath

    if os.path.isfile(shaderpath):
        if output is None:
            output = shaderpath
        elif os.path.isdir(output):
            output = os.path.join(output, os.path.basename(shaderpath))
        do_file(shaderpath, output, SimplifyType(args.simplify))
    elif os.path.isdir(shaderpath):
        if output is None:
            output = shaderpath
        elif os.path.isfile(output):
            raise_error("output cannot be file when shaderpath is folder")
        do_folder(shaderpath, output, SimplifyType(args.simplify))
    else:
        raise_error(f"shaderpath is not exits:{shaderpath}")


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-s",
        "--simplify",
        nargs="?",
        choices=[SimplifyType.Format.value, SimplifyType.RemoveContent.value, SimplifyType.OnlyKeyWord.value],
        default=SimplifyType.Format.value,
        type=int,
        help=f"simplify file 1:format 2:remove shader content 3:only keyworkd keeps default:{SimplifyType.Format.value}",
    )
    parser.add_argument("-o", "--output", help="output file or folder")
    parser.add_argument("shaderpath", help="asset stuido shader preview file")
