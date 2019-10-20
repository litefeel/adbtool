import os
import shlex
import subprocess
import sys


# return (output, isOk)
def call(cmd: str, printOutput=False):
    # print(f"{printOutput = }, {cmd = }")
    if sys.platform == "win32":
        args = cmd
    else:
        # linux must split arguments
        args = shlex.split(cmd)
    try:
        if printOutput:
            isOk = subprocess.call(args) == 0
            return None, isOk
        else:
            data = subprocess.check_output(args)
            # python3 output is bytes
            output = data.decode("utf-8")
            return output, True
    except subprocess.CalledProcessError as callerr:
        print(f"{cmd = }, {callerr.output = }", file=sys.stderr)
        return (callerr.output, False)
    except IOError as ioerr:
        print(f"{cmd = }, {ioerr = }", file=sys.stderr)
        return None, False


def getAdb():
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        # print('can not found ANDROID_HOME/ANDROID_SDK in environment value')
        return "adb"

    return os.path.join(androidHome, "platform-tools/adb")


def versionnum(a: str):
    arr = a.split(".")
    arr.reverse()
    multiple = 1
    n = 0
    for i in range(0, min(len(arr), 3)):
        n += int(arr[i]) * multiple
        multiple *= 1000
    return n


def getAapt(vername=None):
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        print("can not found ANDROID_HOME/ANDROID_SDK in environment value")
        return "aapt"

    aaptname = "aapt.exe" if sys.platform == "win32" else "aapt"

    buildtools = os.path.join(androidHome, "build-tools")
    if os.path.isdir(buildtools):
        dirs = os.listdir(buildtools)
        dirs.sort(reverse=True, key=versionnum)
        for dir in dirs:
            filename = os.path.join(buildtools, dir, aaptname)
            if os.path.isfile(filename):
                return filename

    print("can not found aapt in ANDROID_HOME/ANDROID_SDK")
