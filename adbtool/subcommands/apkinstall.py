import argparse
import json
import os
import posixpath
import re
import shutil
import tempfile
import zipfile
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath

from ..argparse_utils import CommaSeparatedAppendAction
from ..cmd import call_argv, getAdb, getHdc
from ..config import Config
from . import adbdevice, apkinfo, hdcdevice

# BASE_DIR="F:/release"
BASE_DIR = ""
_PACKAGE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$")


@dataclass(slots=True)
class _XapkExpansion:
    local_path: str
    install_path: str


@dataclass(slots=True)
class _XapkPackage:
    apks: list[str]
    base_apk: str
    expansions: list[_XapkExpansion]


def getApks(path, filters):
    apks = [
        filename
        for filename in os.listdir(path)
        if filename.lower().endswith((".apk", ".xapk", ".hap"))
    ]
    if filters is not None:

        def myfilterfun(filename):
            for f in filters:
                if f not in filename:
                    return False
            return True

        apks = [filename for filename in apks if myfilterfun(filename)]
    return [os.path.join(path, filename) for filename in apks]


def getNewst(apks: list[str]) -> str | None:
    if len(apks) == 0:
        return None
    apks = sorted(apks, key=os.path.getmtime, reverse=True)
    return apks[0]


def filterApks(fileorpath: str, filters) -> list[str]:
    if os.path.isdir(fileorpath):
        apks = getApks(fileorpath, filters)
        if len(apks) == 0:
            print("can not found apk, xapk, or hap file in %s " % fileorpath)
            exit(1)
        return [getNewst(apks)]
    return [fileorpath]


def _validate_archive_path(path: object, description: str) -> str:
    if not isinstance(path, str) or not path:
        raise ValueError(f"{description} must be a non-empty string")
    if "\\" in path:
        raise ValueError(f"{description} contains an invalid path separator: {path}")

    parts = path.split("/")
    if (
        PurePosixPath(path).is_absolute()
        or PureWindowsPath(path).is_absolute()
        or any(part in ("", ".", "..") for part in parts)
    ):
        raise ValueError(f"{description} contains an unsafe path: {path}")
    return "/".join(parts)


def _copy_archive_member(
    archive: zipfile.ZipFile, member: zipfile.ZipInfo, destination: str
) -> None:
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    with archive.open(member) as source, open(destination, "wb") as target:
        shutil.copyfileobj(source, target)


def _get_base_apk(package_name: str, apk_members: list[str]) -> str:
    preferred_names = (f"{package_name}.apk", "base.apk")
    for preferred_name in preferred_names:
        matches = [name for name in apk_members if PurePosixPath(name).name == preferred_name]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ValueError(f"multiple base APK candidates named {preferred_name}")

    if len(apk_members) == 1:
        return apk_members[0]
    raise ValueError("can not determine the base APK")


def _extract_xapk(xapk_path: str, output_dir: str) -> _XapkPackage:
    try:
        with zipfile.ZipFile(xapk_path) as archive:
            members: dict[str, zipfile.ZipInfo] = {}
            casefold_names: set[str] = set()
            for member in archive.infolist():
                if member.is_dir():
                    continue
                name = _validate_archive_path(member.filename, "archive member")
                casefold_name = name.casefold()
                if name in members or casefold_name in casefold_names:
                    raise ValueError(f"duplicate archive member: {name}")
                members[name] = member
                casefold_names.add(casefold_name)

            manifest_member = members.get("manifest.json")
            if manifest_member is None:
                raise ValueError("missing manifest.json")
            with archive.open(manifest_member) as manifest_file:
                manifest = json.load(manifest_file)
            if not isinstance(manifest, dict):
                raise ValueError("manifest.json must contain a JSON object")

            package_name = manifest.get("package_name")
            if not isinstance(package_name, str) or not _PACKAGE_NAME_PATTERN.fullmatch(
                package_name
            ):
                raise ValueError("manifest.json contains an invalid package_name")

            apk_members = sorted(name for name in members if name.lower().endswith(".apk"))
            if not apk_members:
                raise ValueError("archive contains no APK files")

            split_apks = manifest.get("split_apks", [])
            if not isinstance(split_apks, list):
                raise ValueError("manifest.json split_apks must be a list")
            for split in split_apks:
                if not isinstance(split, dict):
                    raise ValueError("manifest.json contains an invalid split_apks entry")
                split_path = _validate_archive_path(split.get("file"), "split APK path")
                if split_path not in members or not split_path.lower().endswith(".apk"):
                    raise ValueError(f"missing split APK file: {split_path}")

            base_member = _get_base_apk(package_name, apk_members)
            ordered_apk_members = [base_member]
            ordered_apk_members.extend(name for name in apk_members if name != base_member)

            extracted_apks: list[str] = []
            base_apk = ""
            for index, name in enumerate(ordered_apk_members):
                destination = os.path.join(
                    output_dir,
                    "apks",
                    f"{index:03d}-{PurePosixPath(name).name}",
                )
                _copy_archive_member(archive, members[name], destination)
                extracted_apks.append(destination)
                if name == base_member:
                    base_apk = destination

            expansions = manifest.get("expansions", [])
            if not isinstance(expansions, list):
                raise ValueError("manifest.json expansions must be a list")

            extracted_expansions: list[_XapkExpansion] = []
            expansion_sources: set[str] = set()
            expansion_destinations: set[str] = set()
            expected_prefix = f"Android/obb/{package_name}/"
            for index, expansion in enumerate(expansions):
                if not isinstance(expansion, dict):
                    raise ValueError("manifest.json contains an invalid expansion entry")
                source_path = _validate_archive_path(expansion.get("file"), "expansion file")
                install_path = _validate_archive_path(
                    expansion.get("install_path"), "expansion install_path"
                )
                if source_path in expansion_sources:
                    raise ValueError(f"duplicate expansion file: {source_path}")
                if install_path in expansion_destinations:
                    raise ValueError(f"duplicate expansion install_path: {install_path}")
                if source_path not in members or not source_path.lower().endswith(".obb"):
                    raise ValueError(f"missing OBB expansion file: {source_path}")
                if not install_path.startswith(
                    expected_prefix
                ) or not install_path.lower().endswith(".obb"):
                    raise ValueError(
                        f"expansion install_path must be under {expected_prefix}: {install_path}"
                    )

                destination = os.path.join(
                    output_dir,
                    "obb",
                    f"{index:03d}-{PurePosixPath(source_path).name}",
                )
                _copy_archive_member(archive, members[source_path], destination)
                extracted_expansions.append(_XapkExpansion(destination, install_path))
                expansion_sources.add(source_path)
                expansion_destinations.add(install_path)

            return _XapkPackage(extracted_apks, base_apk, extracted_expansions)
    except (OSError, RuntimeError, UnicodeDecodeError, ValueError, zipfile.BadZipFile) as error:
        raise SystemExit(f"invalid xapk file {xapk_path}: {error}") from error


def install(apks: list[str], serials: list[str], run: bool, force: bool) -> None:
    adb = getAdb()
    subcommand = "install-multi-package" if len(apks) > 1 else "install"
    install_args = ["-d", "-r"] if force else ["-r"]
    target_apk = apks[-1]

    def install_one(serial: str) -> int:
        cmd = [adb, "-s", serial, subcommand, *install_args, *apks]
        _, code = call_argv(cmd, True)
        return code

    with ThreadPoolExecutor(max_workers=len(serials)) as executor:
        futures: list[tuple[str, Future[int]]] = [
            (serial, executor.submit(install_one, serial)) for serial in serials
        ]
        for serial, future in futures:
            isOk = future.result() == 0
            print(isOk)
            if isOk and run:
                apkinfo.run(target_apk, [serial])


def install_haps(haps: list[str], serials: list[str], hdc: str, force: bool) -> None:
    install_args = ["-d", "-r"] if force else ["-r"]

    def install_one(serial: str) -> int:
        _, code = call_argv([hdc, "-t", serial, "install", *install_args, *haps], printOutput=True)
        return code

    with ThreadPoolExecutor(max_workers=len(serials)) as executor:
        futures: list[Future[int]] = [executor.submit(install_one, serial) for serial in serials]
        for future in futures:
            print(future.result() == 0)


def _install_xapk(package: _XapkPackage, serials: list[str], run: bool, force: bool) -> None:
    adb = getAdb()
    subcommand = "install-multiple" if len(package.apks) > 1 else "install"
    install_args = ["-d", "-r"] if force else ["-r"]

    def install_one(serial: str) -> int:
        cmd = [adb, "-s", serial, subcommand, *install_args, *package.apks]
        _, code = call_argv(cmd, True)
        if code != 0:
            return code

        for expansion in package.expansions:
            remote_path = f"/sdcard/{expansion.install_path}"
            remote_dir = posixpath.dirname(remote_path)
            _, code = call_argv([adb, "-s", serial, "shell", "mkdir", "-p", remote_dir], True)
            if code != 0:
                return code
            _, code = call_argv(
                [adb, "-s", serial, "push", expansion.local_path, remote_path], True
            )
            if code != 0:
                return code
        return 0

    with ThreadPoolExecutor(max_workers=len(serials)) as executor:
        futures: list[tuple[str, Future[int]]] = [
            (serial, executor.submit(install_one, serial)) for serial in serials
        ]
        for serial, future in futures:
            is_ok = future.result() == 0
            print(is_ok)
            if is_ok and run:
                apkinfo.run(package.base_apk, [serial])


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    paths = args.apkpath or [cfg.install.apkpath or "."]
    paths = [os.path.abspath(os.path.join(BASE_DIR, path)) for path in paths]

    apks: list[str] = []
    for path in paths:
        apks.extend(filterApks(path, args.filter))

    if not apks:
        return

    xapks = [path for path in apks if path.lower().endswith(".xapk")]
    haps = [path for path in apks if path.lower().endswith(".hap")]
    if haps:
        if len(haps) != len(apks):
            raise SystemExit("hap files can not be installed with apk or xapk files")
        if args.run or cfg.install.run:
            raise SystemExit("--run is not supported for hap files")

        hdc = getHdc(cfg.hdc)
        serials, _ = hdcdevice.doArgumentParser(args, hdc)
        if not serials:
            return
        install_haps(haps, serials, hdc, args.force)
        return

    serials, _ = adbdevice.doArgumentParser(args)
    if not serials:
        return

    if xapks:
        if len(apks) != 1:
            raise SystemExit("an xapk file must be installed by itself")
        with tempfile.TemporaryDirectory(prefix="adbtool-xapk-") as temp_dir:
            package = _extract_xapk(xapks[0], temp_dir)
            _install_xapk(package, serials, args.run or cfg.install.run, args.force)
        return

    install(apks, serials, args.run or cfg.install.run, args.force)


def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-f", "--force", action="store_true", help="allow downgrade and replace existing app"
    )
    parser.add_argument(
        "--filter",
        action=CommaSeparatedAppendAction,
        metavar="FILTER",
        help="filter by file name; repeat the option or separate values with commas",
    )
    parser.add_argument("-r", "--run", action="store_true", help="run app after install")
    parser.add_argument("apkpath", nargs="*", help="apk/xapk/hap file or directory")
    adbdevice.addArgumentParser(parser)
