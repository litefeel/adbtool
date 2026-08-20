import argparse

from ..argparse_utils import CommaSeparatedAppendAction
from ..cmd import call_argv

_EMPTY_TARGETS = "[empty]"


class Device:
    __slots__ = ("serial", "connection_type", "state", "online", "raw")

    def __init__(self, line: str):
        self.raw = line
        parts = line.split()
        self.serial = parts[0]
        self.connection_type = parts[1] if len(parts) >= 2 else ""
        self.state = parts[2] if len(parts) >= 3 else "Connected"
        self.online = self.state.casefold() == "connected"


def get_devices(hdc: str) -> list[Device]:
    output, returncode = call_argv([hdc, "list", "targets", "-v"])
    if returncode != 0:
        return []

    devices = [
        Device(line.strip())
        for line in output.replace("\r\n", "\n").split("\n")
        if line.strip() and line.strip().casefold() != _EMPTY_TARGETS
    ]
    devices = [device for device in devices if device.connection_type.casefold() != "uart"]
    devices.sort(key=lambda device: device.serial.casefold())
    return devices


def _get_device_by_index(devices: list[Device], index: int) -> Device | None:
    if 0 < index <= len(devices):
        return devices[index - 1]
    return None


def _get_devices_by_serial(devices: list[Device], serial: str) -> list[Device]:
    serial = serial.casefold()
    return [device for device in devices if device.serial.casefold().startswith(serial)]


def select_devices(devices: list[Device], selectors: list[str] | None) -> list[Device]:
    if not devices:
        print("No HDC devices connected")
        return []

    if selectors is None:
        if len(devices) > 1:
            print(f"devices count:{len(devices)}  please set devices command")
        return devices[:]

    selected: list[Device] = []
    for selector in selectors:
        if selector == "a":
            return devices[:]

        device = None
        if len(selector) == 1 and selector.isdigit():
            device = _get_device_by_index(devices, int(selector))
        elif len(selector) >= 2:
            matches = _get_devices_by_serial(devices, selector)
            if len(matches) == 1:
                device = matches[0]
            elif len(matches) > 1:
                print(f"serial prefix {selector} is not unique")
                return []

        if device is not None:
            selected.append(device)
    return selected


def print_devices(devices: list[Device]) -> None:
    for index, device in enumerate(devices, start=1):
        print(f"{index:<3} {device.raw}")


def _print_unavailable_devices(devices: list[Device]) -> None:
    for device in devices:
        if not device.online:
            print(f"HDC device {device.serial} is {device.state}.")


def addArgumentParser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-d",
        "--devices",
        action=CommaSeparatedAppendAction,
        nargs="?",
        metavar="DEVICE",
        help="""filter of devices, [a | n | serial]
            a: all devices
            n: index of devices list(start with 1)
            serial: devices serial (at least 2 char)
            repeat the option or separate values with commas
            not argument is show device list""",
    )


def doArgumentParser(args: argparse.Namespace, hdc: str) -> tuple[list[str], list[Device]]:
    devices = get_devices(hdc)
    if args.devices is not None and len(args.devices) == 0:
        print_devices(devices)
        return [], []

    devices = select_devices(devices, args.devices)
    unavailable_devices = [device for device in devices if not device.online]
    if unavailable_devices:
        _print_unavailable_devices(unavailable_devices)
        print("Abort: all target devices must be available.")
        raise SystemExit(1)

    return [device.serial for device in devices], devices
