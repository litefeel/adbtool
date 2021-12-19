# Adbtool
A friendly android adb command-line tool

[![Test 😎](https://github.com/litefeel/adbtool/workflows/Test%20%F0%9F%98%8E/badge.svg)](https://github.com/litefeel/adbtool/actions)
[![PyPI](https://img.shields.io/pypi/v/adbtool.svg)](https://pypi.org/project/adbtool/)
[![PyPI](https://img.shields.io/pypi/l/adbtool.svg)](https://pypi.org/project/adbtool/)


### Python Requirements
* python 3.9+
* Android SDK


### Commands


~~~
adbt -h
usage: adbt [options]

show android device list

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        global config
  --version             show program's version number and exit

sub commands:
  {devices,push,install,uninstall,apk,sign,ab,il2cpp}
    devices             show android device list
    push                push files to android device
    install             install apk file
    uninstall           uninstall apk file
    apk                 show apk packageName/activityName
    sign                sign apk with android debug(only windows)
    ab                  extract unity asset bundle information
    il2cpp              extract unity il2cpp information
~~~

---

~~~
adbt devices -h
usage: adbt [options] devices [-h] [-d DEVICES [DEVICES ...]] [-l]

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICES [DEVICES ...], --devices DEVICES [DEVICES ...]
                        filter of devices, [n | serial | a] n:index of list(start with 1), serial:at least 2 char,
                        a:all
  -l, --list            show devices list
~~~
---
~~~
adbt push -h
usage: adbt [options] push [-h] [-r] [-n] [-j [HASHJSON]] [--hash [{sha1,mtime}]] [--localdir LOCALDIR]
                           [--remotedir REMOTEDIR] [--dontpush] [-d [DEVICES [DEVICES ...]]]
                           [path [path ...]]

positional arguments:
  path                  file or directory

optional arguments:
  -h, --help            show this help message and exit
  -r                    recursion all file
  -n                    only push new file by last modify files, see -j
  -j [HASHJSON]         hash json file, default: ./$deviceMode_$deviceSerial.json
  --hash [{sha1,mtime}]
                        hash function: mtime or sha1, default:mtime
  --localdir LOCALDIR   local prefix and remote prefix, will replace local prefix to remote prefix
  --remotedir REMOTEDIR
                        local prefix and remote prefix, will replace local prefix to remote prefix
  --dontpush            only outout json file, not really push file to remote
  -d [DEVICES [DEVICES ...]], --devices [DEVICES [DEVICES ...]]
                        filter of devices, [a | n | serial] a: all devices n: index of devices list(start with 1)
                        serial: devices serial (at least 2 char) not argument is show device list
~~~
---
~~~
adbt install -h
usage: adbt [options] install [-h] [-f [FILTER [FILTER ...]]] [-r] [-d [DEVICES [DEVICES ...]]] [apkpath]

positional arguments:
  apkpath

optional arguments:
  -h, --help            show this help message and exit
  -f [FILTER [FILTER ...]], --filter [FILTER [FILTER ...]]
                        filtered by file name
  -r, --run             run app after install
  -d [DEVICES [DEVICES ...]], --devices [DEVICES [DEVICES ...]]
                        filter of devices, [a | n | serial] a: all devices n: index of devices list(start with 1)
                        serial: devices serial (at least 2 char) not argument is show device list
~~~
---
~~~
adbt apk -h
usage: adbt [options] apk [-h] [-r] [-d [DEVICES [DEVICES ...]]] [apkpath]

positional arguments:
  apkpath

optional arguments:
  -h, --help            show this help message and exit
  -r, --run             run app
  -d [DEVICES [DEVICES ...]], --devices [DEVICES [DEVICES ...]]
                        filter of devices, [a | n | serial] a: all devices n: index of devices list(start with 1)
                        serial: devices serial (at least 2 char) not argument is show device list
~~~
