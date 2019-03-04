#!/usr/bin/env python
#  encoding=utf-8

import os, os.path
import argparse
import sys

from cmd import call
from cmd import getAdb
import apkinfo
import adbdevice

# BASE_DIR="F:/release"
BASE_DIR=""

def getApks(path, filters):
    apks = os.listdir(path)
    apks = filter(lambda filename: filename.endswith('.apk'), apks)
    if filters is not None:
        def myfilterfun(filename):
            for f in filters:
                if f not in filename:
                    return False
            return True
        apks = filter(myfilterfun, apks)
    apks = map(lambda filename: os.path.join(path, filename), apks)
    return apks


def getNewst(apks):
    if len(apks) == 0:
        return None
    apks = sorted(apks, cmp=lambda fa, fb: int(os.path.getmtime(fb) - os.path.getmtime(fa)))
    return apks[0]


def filterApks(fileorpath, filters):
    apk = fileorpath
    if os.path.isdir(fileorpath):
        apks = getApks(fileorpath, filters)
        if len(apks) == 0:
            print('can not found apk file in %s ' % fileorpath)
            exit(1)
        apk = getNewst(apks)
    return apk


def install(apks, serials, run):
    adb = getAdb()
    last = len(apks) - 1
    for i in range(0, len(apks)):
        apk = apks[i]
        isrun = run and last == i
        for serial in serials:
            cmd = '%s -s %s install -r "%s"' % (adb, serial, apk)
            _, isOk = call(cmd, True)
            print(isOk)
            if isOk and isrun:
                activity = apkinfo.parse(apk)
                cmd = '%s -s %s shell am start "%s"' % (adb, serial, activity)
                call(cmd)


# -------------- main ----------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='%(prog)s [options] [path]',
        description='install apk file.')
    parser.add_argument('-f', '--filter', nargs='*',
        help='filtered by file name')
    parser.add_argument('-r', '--run', action="store_true",
        help='run app after install')
    parser.add_argument('path', nargs='?')
    adbdevice.addArgumentParser(parser)

    args = parser.parse_args()

    isOk, serials, devices = adbdevice.doArgumentParser(args)
    if isOk:
        exit(0)

    path = args.path if args.path is not None else '.'
    path = os.path.abspath(os.path.join(BASE_DIR, path))

    apks = filterApks(path, args.filter)

    if serials is not None and apks is not None:
        install([apks], serials, args.run)
