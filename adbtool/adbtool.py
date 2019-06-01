import argparse
import sys


# -------------- main ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options]", description="show android device list"
    )
    parser.add_argument(
        "-d",
        "--devices",
        nargs="+",
        help="filter of devices, [n | serial | a] n:index of list(start with 1), serial:at least 2 char, a:all",
    )
    parser.add_argument("-l", "--list", action="store_true", help="show devices list")

    args = parser.parse_args()
    if args.list:
        printDevices(getDevices())
        exit(0)

    devices = filterDevices(getDevices(), args.devices)
    printDevices(devices)
