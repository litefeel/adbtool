# Adbtool
A friendly android adb command-line tool

[![Build Status](https://travis-ci.org/litefeel/adbtool.svg?branch=master)](https://travis-ci.org/litefeel/adbtool)
[![Software License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/litefeel/adbtool/blob/master/LICENSE)


### Python Requirements
* python 3.2+


### Commands


~~~
adbdevice.py -h
usage: adbdevice.py [options]

show android device list

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICES [DEVICES ...], --devices DEVICES [DEVICES ...]
                        filter of devices, [n | serial | a] n:index of
                        list(start with 1), serial:at least 2 char, a:all
  -l, --list            show devices list
~~~

---

~~~
adbpush.py -h
usage: adbpush.py [options] [path]

push file to android device

positional arguments:
  path              file or directory

optional arguments:
  -h, --help        show this help message and exit
  -r                recursion all file
  -p PREFIX PREFIX  local prefix and remote prefix, will replace local prefix
                    to remote prefix

~~~
---
~~~
apkinfo.py -h
usage: apkinfo.py [options] apkpath

show apk packageName/activityName

positional arguments:
  apkpath

optional arguments:
  -h, --help            show this help message and exit
  -r, --run             run app
  -d [DEVICES [DEVICES ...]], --devices [DEVICES [DEVICES ...]]
                        filter of devices, [a | n | serial] a: all devices n:
                        index of devices list(start with 1) serial: devices
                        serial (at least 2 char) not argument is show device
                        list
~~~
---
~~~
apkinstall.py -h
usage: apkinstall.py [options] [path]

install apk file.

positional arguments:
  path

optional arguments:
  -h, --help            show this help message and exit
  -f [FILTER [FILTER ...]], --filter [FILTER [FILTER ...]]
                        filtered by file name
  -r, --run             run app after install
  -d [DEVICES [DEVICES ...]], --devices [DEVICES [DEVICES ...]]
                        filter of devices, [a | n | serial] a: all devices n:
                        index of devices list(start with 1) serial: devices
                        serial (at least 2 char) not argument is show device
                        list
~~~
