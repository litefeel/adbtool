import pytest
from adbtool import adbtool


def test_default():
    _assert_success("devices")


def _assert_success(cmd=None):
    args = [] if cmd is None else cmd.split()
    adbtool.main(args)
