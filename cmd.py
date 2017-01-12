#!/usr/bin/python
#  encoding=utf-8

import os
import subprocess


# return (output, isOk)
def call(cmd, printOutput=False):
    # print("call %s" % cmd)
    output = None
    isOk = True
    try:
        if printOutput:
            isOk = subprocess.call(cmd)
        else:
            output = subprocess.check_output(cmd)
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
