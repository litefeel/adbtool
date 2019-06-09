import pytest
from adbtool import config
from adbtool import adbtool


def test_config():
    config.Config().load_config("tests/config.yml")


def test_default():
    _assert_success()


def test_help():
    _assert_success("-h")


def test_version():
    _assert_success("--version")


def _assert_success(cmd=None):
    args = [] if cmd is None else cmd.split()
    with pytest.raises(SystemExit) as exc:
        adbtool.main(args)
    assert exc.value.code == 0
