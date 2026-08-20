# Adbtool
A friendly android adb command-line tool

[![Test 😎](https://github.com/litefeel/adbtool/workflows/Test%20%F0%9F%98%8E/badge.svg)](https://github.com/litefeel/adbtool/actions)
[![PyPI](https://img.shields.io/pypi/v/adbtool.svg)](https://pypi.org/project/adbtool/)
[![PyPI](https://img.shields.io/pypi/l/adbtool.svg)](https://pypi.org/project/adbtool/)


### Python Requirements
* python 3.13+
* uv
* Android SDK (for APK/XAPK commands)
* HarmonyOS/OpenHarmony SDK (for HDC commands and HAP installs)


### Development

~~~
uv sync
uv run pytest
uv run pytest tests/test_cmd.py
uv run ruff format adbtool tests
uv build
~~~


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
  {adb,hdc,devices,push,install,uninstall,apk,sign,ab,il2cpp}
    adb                 forward adb arguments to selected devices
    hdc                 forward hdc arguments to selected devices
    devices             show android device list
    push                push files to android device
    install             install apk, xapk, or hap file
    uninstall           uninstall apk file
    apk                 show apk packageName/activityName
    sign                sign apk with android debug(only windows)
    ab                  extract unity asset bundle information
    il2cpp              extract unity il2cpp information
~~~

---

~~~
adbt adb -- devices
adbt adb -d 1 -- shell
adbt adb -d a -- shell pwd
adbt adb -d 1 -d emulator-5554 -- shell
adbt adb -d 1,emulator-5554 -- shell
adbt adb -- -H localhost devices
adbt adb -d 1 -- -d shell
~~~

`adbt adb` supports the same device selection flow as `install`, and adb arguments must
be placed after `--`.

- `-d/--devices` before `--` belongs to `adbt adb`
- repeat `-d/--devices` or separate selectors with commas to select multiple devices
- everything after `--` is passed to the real `adb` binary without extra parsing
- `adbt adb -h` shows the `adbt` subcommand help
- `adbt adb -- -h` shows the real `adb` help

~~~
adbt adb -h
usage: adbt adb [-h] [-d [DEVICE]] -- [adb_args ...]
~~~

---

~~~
adbt hdc -- shell
adbt hdc -d 1 -- shell
adbt hdc -d a -- shell pwd
adbt hdc -d 1 -d serial-prefix -- shell
adbt hdc -d 1,serial-prefix -- shell
adbt hdc -- -h
~~~

`adbt hdc` uses the HDC target list and follows the same selection and argument
forwarding rules as `adbt adb`.

- `-d/--devices` before `--` selects HDC targets by index, serial prefix, or `a`
- repeat `-d/--devices` or separate selectors with commas to select multiple targets
- everything after `--` is passed to the real `hdc` binary without extra parsing
- each selected target is invoked as `hdc -t <serial> ...`
- `adbt hdc -h` shows the `adbt` subcommand help
- `adbt hdc -- -h` shows the real `hdc` help
- the HDC tool directory uses the top-level `hdc` setting in `adbtool.yml`

~~~
adbt hdc -h
usage: adbt hdc [-h] [-d [DEVICE]] -- [hdc_args ...]
~~~

---

~~~
adbt devices -h
usage: adbt [options] devices [-h] [-d DEVICE] [-l]

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --devices DEVICE
                        filter of devices, [n | serial | a]; repeat the option or separate values with commas
  -l, --list            show devices list
~~~
---
~~~
adbt push -h
usage: adbt [options] push [-h] [-r] [-n] [-j [HASHJSON]] [--hash [{sha1,mtime}]] [--localdir LOCALDIR]
                           [--remotedir REMOTEDIR] [--dontpush] [-d [DEVICE]]
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
  -d, --devices [DEVICE]
                        filter of devices, [a | n | serial] a: all devices n: index of devices list(start with 1)
                        serial: devices serial (at least 2 char); repeat the option or separate values with commas;
                        not argument is show device list
~~~
---
~~~
adbt install -h
usage: adbt [options] install [-h] [-f] [--filter FILTER] [-r] [-d [DEVICE]] [apkpath ...]

positional arguments:
  apkpath               apk/xapk/hap file or directory

optional arguments:
  -h, --help            show this help message and exit
  -f, --force           allow downgrade and replace existing app
  --filter FILTER       filter by file name; repeat the option or separate values with commas
  -r, --run             run app after install
  -d, --devices [DEVICE]
                        filter of devices, [a | n | serial] a: all devices n: index of devices list(start with 1)
                        serial: devices serial (at least 2 char); repeat the option or separate values with commas;
                        not argument is show device list
~~~

- `install` accepts APK, XAPK, and HAP files. A directory selects the newest matching package.
- multiple APK paths use `adb install-multi-package`; an XAPK must be installed by itself.
- XAPK split APKs use `adb install-multiple`; declared OBB files are pushed to `/sdcard/Android/obb/<package>/` after installation.
- default install mode uses `adb -r`; `-f/--force` upgrades it to `adb -d -r`.
- HAP files use `hdc -t <device> install -r`; `-f/--force` upgrades it to `-d -r`.
- multiple HAP paths are installed together; HAP cannot be mixed with APK/XAPK, and `--run` is not supported for HAP.
- configure the HDC tool directory with the top-level `hdc` key in `adbtool.yml`. On Windows, the DevEco Studio default is checked before PATH:

~~~yaml
hdc: C:\Program Files\Huawei\DevEco Studio\sdk\default\openharmony\toolchains
~~~

- repeat `--filter` or separate filter values with commas when all terms must match.

~~~powershell
adbt install -d a C:\path\app.apk
adbt install -d a C:\path\game.xapk
adbt install -d a C:\path\app.hap
adbt install -d 1 -d emulator-5554 C:\path\app.apk
adbt install --filter ZGame,arm64 --filter gp C:\path\builds
~~~

---
~~~
adbt apk -h
usage: adbt [options] apk [-h] [-r] [-d [DEVICE]] [apkpath]

positional arguments:
  apkpath

optional arguments:
  -h, --help            show this help message and exit
  -r, --run             run app
  -d, --devices [DEVICE]
                        filter of devices, [a | n | serial] a: all devices n: index of devices list(start with 1)
                        serial: devices serial (at least 2 char); repeat the option or separate values with commas;
                        not argument is show device list
~~~
