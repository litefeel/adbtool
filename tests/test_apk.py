import pytest
from pytest import raises
from adbtool import adbtool


# def test_default():
#     _assert_success("apk")

APK_INFO = "com.litefeel.adbtoolapk/com.litefeel.adbtoolapk.MainActivity\n"


def test_apkinfo(capsys):
    adbtool.main(["apk", "./test/adbtooltest.apk"])
    captured = capsys.readouterr()
    assert captured.out == APK_INFO
    assert captured.err == ""


def test_missing_path(capsys):
    with pytest.raises(SystemExit, match="Missing parameter: apkpath"):
        adbtool.main(["apk"])
