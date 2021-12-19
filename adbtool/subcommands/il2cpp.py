import argparse
import os
from zipfile import ZipFile

from genericpath import isdir, isfile
from litefeel.pycommon.io import makedirs, write_file

from ..cmd import call
from ..config import Config
from ..errors import raise_error


def extract(file, output_folder):
    zipfile = ZipFile(file, 'r')
    write_file(os.path.join(output_folder, "libil2cpp.so"), zipfile.read("lib/arm64-v8a/libil2cpp.so"))
    write_file(os.path.join(output_folder, "global-metadata.dat"), zipfile.read("assets/bin/Data/Managed/Metadata/global-metadata.dat"))
    zipfile.close()

def do_file(apkfile, output_folder):
    if not os.path.isfile(apkfile):
        raise_error(f'file not fond:{apkfile}')

    extract(apkfile, output_folder)
    il2cppso = os.path.join(output_folder, "libil2cpp.so")
    metadatadat = os.path.join(output_folder, "global-metadata.dat")
    cmd = f'Il2CppDumper.exe "{il2cppso}" "{metadatadat}" "{output_folder}"'
    call(cmd)

def docommand(args: argparse.Namespace, cfg: Config) -> None:
    output = args.output
    apkpath = args.apkpath
    if os.path.isfile(apkpath):
        if output is None:
            output = os.path.splitext(apkpath)[0]
        makedirs(output)
        do_file(apkpath, output)
    else:
        raise_error(f"apkpath is not exits:{apkpath}")


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-o", "--output", help="output file or folder")
    parser.add_argument("apkpath", help="apk file")
