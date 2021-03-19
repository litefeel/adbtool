import os
import shlex
import subprocess
import sys

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
    return ""
