import argparse

from ..cmd import call, getAdb
from ..config import Config

_IGNORE_PREFIXS = ("List of devices attached", "* daemon")


class Device:
    """docstring for Device"""

    __slots__ = ("serial", "state", "online", "product", "model", "device", "raw")

    def __init__(self, line: str):
        self.raw = line
        arr = line.split()
        details = dict(item.split(":", 1) for item in arr[2:] if ":" in item)
        self.serial = arr[0]
        self.state = arr[1]
        self.online = self.state == "device"
        self.product = details.get("product", "")
        self.model = details.get("model", "")
        self.device = details.get("device", "")


def listOneItem(arr, index):
    if 0 < index <= len(arr):
        return arr[index - 1]
    return None


def get_devices() -> list[Device]:
    output, isOk = call('"%s" devices -l' % getAdb())
    devices: list[Device] = []
    if isOk:
        output = output.replace("\r\n", "\n").strip()
        lines = output.split("\n")
        if len(lines) > 1:
            # skip first line "List of devices attached"
            for line in lines:
                if line and not line.startswith(_IGNORE_PREFIXS):
                    devices.append(Device(line))
    devices.sort(key=lambda x: x.serial.lower())
    return devices


def printUnavailableDevices(devices: list[Device]) -> None:
    for device in devices:
        if device.online:
            continue

        if device.state == "unauthorized":
            print(
                f"Device {device.serial} is unauthorized. "
                "Please allow USB debugging on the device and try again."
            )
        elif device.state == "offline":
            print(
                f"Device {device.serial} is offline. "
                "Please reconnect it or run `adb reconnect` and try again."
            )
        else:
            print(f"Device {device.serial} is {device.state}.")


def selectDevices(devices: list[Device], args) -> list[Device]:
    if len(devices) == 0:
        print("No devices connected")
        return []

    if args is None:
        if len(devices) == 1:
            return devices[:]
        print("devices count:%d  please set devices command" % len(devices))
        return devices[:]

    selects: list[Device] = []
    for arg in args:
        device = None
        if len(arg) == 1:
            if arg == "a":
                return devices[:]
            device = listOneItem(devices, int(arg))
        elif len(arg) >= 2:
            tmp = getDevicesBySerial(devices, arg)
            if len(tmp) == 1:
                device = tmp[0]
            elif len(tmp) > 1:
                print("serial prefix %s is not unique" % arg)
                return []
        if device is not None:
            selects.append(device)
    return selects


def getDevicesBySerial(devices:list[Device], serial):
    serial = serial.lower()
    return [device for device in devices if device.serial.lower().startswith(serial)]


# return
#   List: matched devices
def filterDevices(devices: list[Device], args) -> list[Device]:
    return [device for device in selectDevices(devices, args) if device.online]


def printDevices(devices: list[Device]):
    if devices is None:
        return
    for i, device in enumerate(devices, start=1):
        print(f"{i:<3} {device.raw}")


##### for other script
def getSerials(devices: list[Device]) -> list[str]:
    return [device.serial for device in devices]


def addArgumentParser(parser):
    parser.add_argument(
        "-d",
        "--devices",
        nargs="*",
        help="""filter of devices, [a | n | serial]
            a: all devices
            n: index of devices list(start with 1)
            serial: devices serial (at least 2 char)
            not argument is show device list""",
    )


def doArgumentParser(args) -> tuple[list[str], list[Device]]:
    devices = get_devices()
    if args.devices is not None and len(args.devices) == 0:
        printDevices(devices)
        return ([], [])

    devices = selectDevices(devices, args.devices)
    unavailable_devices = [device for device in devices if not device.online]
    if unavailable_devices:
        printUnavailableDevices(unavailable_devices)
        print("Abort: all target devices must be available.")
        raise SystemExit(1)

    serials = getSerials(devices)
    return (serials, devices)


def docommand(args: argparse.Namespace, cfg: Config) -> None:
    if args.list:
        printDevices(get_devices())
        exit(0)

    devices = filterDevices(get_devices(), args.devices)
    printDevices(devices)


##### end for other script
# -------------- main ----------------
def addcommand(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-d",
        "--devices",
        nargs="+",
        help="filter of devices, [n | serial | a] n:index of list(start with 1), serial:at least 2 char, a:all",
    )
    parser.add_argument("-l", "--list", action="store_true", help="show devices list")
