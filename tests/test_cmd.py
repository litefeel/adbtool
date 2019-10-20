import pytest
from adbtool.cmd import versionnum


def test_versionnum(capsys):
    # with capsys.disabled():
    assert versionnum("100.678.9") == 100678009

