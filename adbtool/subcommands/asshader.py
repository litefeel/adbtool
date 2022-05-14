import argparse
from enum import Enum, IntEnum
import os
from zipfile import ZipFile

from genericpath import isdir, isfile
from litefeel.pycommon.io import makedirs, write_lines, read_lines

from ..cmd import call
from ..config import Config
from ..errors import raise_error


class SimplifyType(IntEnum):
    Format = 1
    RemoveContent = 2


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
    _format(lines)
    write_lines(output_file, lines)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    output = args.output
    input = args.shader
    if os.path.isfile(input):
        if output is None:
            output = input
        makedirs(output, isfile=True)
        do_file(input, output, SimplifyType(args.simplify))
    else:
        raise_error(f"shader is not exits:{input}")


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-s",
        "--simplify",
        nargs="?",
        choices=[SimplifyType.Format.value, SimplifyType.RemoveContent.value],
        default=1,
        type=int,
        help="simplify file 1:format 2:remove shader content",
    )
    parser.add_argument("-o", "--output", help="output file or folder")
    parser.add_argument("shader", help="asset stuido shader preview file")
