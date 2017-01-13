#!/usr/bin/python
#  encoding=utf-8

import os
import sys
import shlex
import subprocess


# return (output, isOk)
def call(cmd, printOutput=False):
    print("call %s" % cmd)
    output = None
    isOk = True
    if sys.platform == 'win32':
        args = cmd
    else:
        # linux must split arguments
        args = shlex.split(cmd)
    # output = subprocess.check_output(args)
    try:
        if printOutput:
            isOk = subprocess.call(args)
        else:
            output = subprocess.check_output(args)
        # print(output)
        return (output, isOk)
    except subprocess.CalledProcessError as e:
        print(e.output)
        return (e.output, isOk)


def getAdb():
    androidHome = os.getenv('ANDROID_HOME')
    if androidHome is None:
        androidHome = os.getenv('ANDROID_SDK')
    if androidHome is None:
        print('can not found ANDROID_HOME/ANDROID_SDK in environment value')
        return "adb"

    return os.path.join(androidHome, 'platform-tools/adb')
