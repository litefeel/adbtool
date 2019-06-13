import sys


def raise_error(err, code=1):
    print(err, file=sys.stderr)
    exit(code)

