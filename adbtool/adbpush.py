#!/usr/bin/env python
#  encoding=utf-8

import os, os.path
import argparse

from cmd import call
from cmd import getAdb


# bat
# @echo off
# rem %cd% 工作目录/当前目录
# rem %~dp0 bat文件所在目录

# rem 启用延迟扩展，一行语句中延迟变量赋值
# setlocal ENABLEDELAYEDEXPANSION

# set rpstr=E:/work/zeus/GameEditors/UIEdit/res/
# set xxx=/sdcard/hookzeus/
# set localpath=%cd%/%1
# set localpath=%localpath:\=/%

# set remotepath=%localpath:E:/work/zeus/GameEditors/UIEdit/res/=!xxx!%
# echo %localpath%
# echo %remotepath%
# adb push %localpath% %remotepath%




prefixLocal  = "E:/work/zeus/GameEditors/UIEdit/res/"
prefixRemote = "/sdcard/hookzeus/"


def parsePrefix(prefix):
    if prefix is not None and len(prefix) == 2:
        return (prefix[0], prefix[1])
    return (prefixLocal, prefixRemote)


def push(file, prefixLocal, prefixRemote):
    file = file.replace('\\', '/')
    local = file
    remote = file
    if file.startswith(prefixLocal):
        remote = prefixRemote + file[len(prefixLocal):]
    call("%s push %s %s" % (getAdb(), local, remote), True)

def filePush(path, prefixLocal, prefixRemote):
    files = os.listdir(path)
    for f in files:
        file = "%s/%s" % (path, f)
        if os.path.isfile(file):
            push(file, prefixLocal, prefixRemote)

def walkPush(path, prefixLocal, prefixRemote):
    for root, dirs, files in os.walk(path):
        for f in files:
            push("%s/%s" % (root, f), prefixLocal, prefixRemote)


# -------------- main ----------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='%(prog)s [options] [path]',
        description='push file to android device')
    parser.add_argument('-r', dest='recursion', action="store_true",
        help='recursion all file')
    parser.add_argument('-p', dest='prefix', nargs=2,
        help='local prefix and remote prefix, will replace local prefix to remote prefix')
    parser.add_argument('path', nargs='*', 
        help='file or directory')


    args = parser.parse_args()

    local, remote = parsePrefix(args.prefix)

    paths = args.path[:]
    if len(paths) == 0:
        paths.append('.')
    for path in paths:
        path = os.path.abspath(path)
        if os.path.isfile(path):
            push(path, local, remote)
        elif os.path.isdir(path):
            if args.recursion:
                walkPush(path, local, remote)
            else:
                filePush(path, local, remote)
        else:
            print("%s: No such file or directory" % path)
