#!/usr/bin/env python
#  encoding=utf-8

import os.path
import argparse
import re

from cmd import call
from cmd import getAapt
from cmd import getAdb

import adbdevice

def firstitem(arr):
    return arr[0] if len(arr) > 0 else None


def parse(apk):
    aapt = getAapt()
    cmd = '%s dump badging %s' % (aapt, apk)
    output, isOk = call(cmd)
    if isOk:
        packagename = firstitem(re.findall(r"package: name='(\S+?)'", output))
        activityname = firstitem(re.findall(r"launchable-activity: name='(\S+?)'", output))
        return '%s/%s' % (packagename, activityname)
    return None

# -------------- main ----------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='%(prog)s [options] apkpath',
        description='show apk packageName/activityName')
    parser.add_argument('-r', '--run', action="store_true",
        help='run app')
    parser.add_argument('apkpath', nargs='?')
    adbdevice.addArgumentParser(parser)

    args = parser.parse_args()

    isOk, serials = adbdevice.doArgumentParser(args)
    if isOk:
        exit(0)

    apkpath = os.path.abspath(args.apkpath)
    activity = parse(apkpath)
    if args.run and serials is not None:
        adb = getAdb()
        for serial in serials:
            cmd = '%s -s %s shell am start "%s"' % (adb, serial, activity)
            call(cmd)
    else:
        print(activity)
