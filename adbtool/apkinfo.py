#!/usr/bin/env python
#  encoding=utf-8

import os.path
import argparse
import re

from cmd import call
from cmd import getAapt

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
    parser.add_argument('apkpath', nargs='?')

    args = parser.parse_args()
    apkpath = os.path.abspath(args.apkpath)

    print(parse(apkpath))

