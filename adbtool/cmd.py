import os
import shlex
import subprocess
import sys
import asyncio

from semantic_version import Version

from .errors import raise_error


# return (output, isOk)
def call(cmd: str, printOutput: bool = False) -> tuple[str, bool]:
    # print(f"{printOutput = }, {cmd = }")
    if sys.platform == "win32":
        args = cmd
    else:
        # linux must split arguments
        args = shlex.split(cmd)
    try:
        if printOutput:
            isOk = subprocess.call(args) == 0
            return "", isOk

        data = subprocess.check_output(args)
        # python3 output is bytes
        output = data.decode("utf-8")
        return output, True
    except subprocess.CalledProcessError as callerr:
        print(f"cmd = {cmd}, callerr.output = {callerr.output}", file=sys.stderr)
        return (callerr.output, False)
    except IOError as ioerr:
        print(f"cmd = {cmd}, ioerr = {ioerr}", file=sys.stderr)
        return "", False


async def call_async(cmd: str, printOutput: bool = False) -> tuple[str, bool]:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    isOk = proc.returncode == 0

    output = ""
    if stdout:
        output = stdout.decode("utf-8")
    if printOutput:
        if output:
            print(output)
        if stderr:
            print(stderr.decode("utf-8"))
    return output, isOk


def getAdb() -> str:
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK_ROOT")
    if androidHome is None:
        # print('can not found ANDROID_HOME/ANDROID_SDK in environment value')
        return "adb"

    return os.path.join(androidHome, "platform-tools/adb")


def getAapt() -> str:
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK_ROOT")
    if androidHome is None:
        print("can not found ANDROID_HOME/ANDROID_SDK in environment value")
        return "aapt"

    aaptname = "aapt.exe" if sys.platform == "win32" else "aapt"

    buildtools = os.path.join(androidHome, "build-tools")
    if os.path.isdir(buildtools):
        vers = list(map(lambda v: Version(v), os.listdir(buildtools)))
        vers.sort(reverse=True)
        for ver in vers:
            filename = os.path.join(buildtools, str(ver), aaptname)
            if os.path.isfile(filename):
                return filename

    raise_error("can not found aapt in ANDROID_HOME/ANDROID_SDK")


def getZipalign() -> str:
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK_ROOT")
    if androidHome is None:
        print("can not found ANDROID_HOME/ANDROID_SDK in environment value")
        return "zipalign"

    # aaptname = "apksigner.bat" if sys.platform == "win32" else "apksigner.bat"
    aaptname = "zipalign.exe"

    buildtools = os.path.join(androidHome, "build-tools")
    if os.path.isdir(buildtools):
        vers = list(map(lambda v: Version(v), os.listdir(buildtools)))
        vers.sort(reverse=True)
        for ver in vers:
            filename = os.path.join(buildtools, str(ver), aaptname)
            if os.path.isfile(filename):
                return filename

    raise_error("can not found aapt in ANDROID_HOME/ANDROID_SDK")


def getApksigner() -> str:
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK_ROOT")
    if androidHome is None:
        print("can not found ANDROID_HOME/ANDROID_SDK in environment value")
        return "apksigner"

    # aaptname = "apksigner.bat" if sys.platform == "win32" else "apksigner.bat"
    aaptname = "apksigner.bat"

    buildtools = os.path.join(androidHome, "build-tools")
    if os.path.isdir(buildtools):
        vers = list(map(lambda v: Version(v), os.listdir(buildtools)))
        vers.sort(reverse=True)
        for ver in vers:
            filename = os.path.join(buildtools, str(ver), aaptname)
            if os.path.isfile(filename):
                return filename

    raise_error("can not found aapt in ANDROID_HOME/ANDROID_SDK")


def get_unity_editor_dir(editor_dir: str) -> str:
    def is_editor_dir(dir):
        if dir is None:
            return False
        if os.path.isdir(dir):
            if os.path.isfile(os.path.join(dir, "Unity.exe")):
                return True
        return False

    if is_editor_dir(editor_dir):
        return editor_dir
    editor_dir = os.getenv("UNITY_EDITOR_ROOT") or ""
    if is_editor_dir(editor_dir):
        return editor_dir
    raise_error("can not found unity editor")


def get_unity_binary2text(unity_editor_dir):
    return os.path.join(get_unity_editor_dir(unity_editor_dir), "Data/Tools/binary2text.exe")


def get_unity_webextract(unity_editor_dir):
    return os.path.join(get_unity_editor_dir(unity_editor_dir), "Data/Tools/WebExtract.exe")
