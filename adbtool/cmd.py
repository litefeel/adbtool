#!/usr/bin/env python
#  encoding=utf-8

import os
import sys
import shlex
import subprocess
import math

# return (output, isOk)
def call(cmd, printOutput=False):
    # print("call %s" % cmd)
    output = None
    isOk = True
    if sys.platform == "win32":
        args = cmd
    else:
        # linux must split arguments
        args = shlex.split(cmd)
    try:
        if printOutput:
            isOk = subprocess.call(args) == 0
        else:
            output = subprocess.check_output(args)
            # python3 output is bytes
            output = output.decode("utf-8")
        return (output, isOk)
    except subprocess.CalledProcessError as e:
        print(e.output)
        return (e.output, isOk)


def getAdb():
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        # print('can not found ANDROID_HOME/ANDROID_SDK in environment value')
        return "adb"

    return os.path.join(androidHome, "platform-tools/adb")


def versionnum(a):
    arr = a.split(".")
    multiple = 10000
    n = 0
    for i in range(0, min(len(arr), 3)):
        n += int(arr[i]) * multiple
        multiple /= 100
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

