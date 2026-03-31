import os

import pytest

from adbtool import adbtool
from adbtool.subcommands import apkinstall


def _mock_install(monkeypatch, returncodes=None):
    calls = []
    codes = [0] if returncodes is None else list(returncodes)

    def fake_get_adb():
        return "adb-bin"

    def fake_call_argv(args, printOutput=False):
        calls.append((list(args), printOutput))
        return "", codes.pop(0) if codes else 0

    monkeypatch.setattr(apkinstall, "getAdb", fake_get_adb)
    monkeypatch.setattr(apkinstall, "call_argv", fake_call_argv)
    return calls


def _mock_devices(monkeypatch, serials, devices=None):
    actual_devices = [object() for _ in serials] if devices is None else devices

    def fake_do_argument_parser(args):
        return list(serials), list(actual_devices)

    monkeypatch.setattr(apkinstall.adbdevice, "doArgumentParser", fake_do_argument_parser)


def _mock_run(monkeypatch):
    calls = []

    def fake_run(apk, serials):
        calls.append((apk, list(serials)))

    monkeypatch.setattr(apkinstall.apkinfo, "run", fake_run)
    return calls


def _mock_fs(monkeypatch, directories=None, mtimes=None):
    directory_map = {} if directories is None else {os.path.abspath(k): v for k, v in directories.items()}
    mtime_map = {} if mtimes is None else {os.path.abspath(k): v for k, v in mtimes.items()}

    def fake_isdir(path):
        return os.path.abspath(path) in directory_map

    def fake_listdir(path):
        return list(directory_map[os.path.abspath(path)])

    def fake_getmtime(path):
        return mtime_map[os.path.abspath(path)]

    monkeypatch.setattr(apkinstall.os.path, "isdir", fake_isdir)
    monkeypatch.setattr(apkinstall.os, "listdir", fake_listdir)
    monkeypatch.setattr(apkinstall.os.path, "getmtime", fake_getmtime)


def test_install_help_shows_force_and_filter(capsys):
    with pytest.raises(SystemExit) as exc:
        adbtool.main(["install", "-h"])

    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "-f, --force" in out
    assert "--filter [FILTER ...]" in out
    assert "[apkpath ...]" in out


def test_install_single_apk_uses_install_r(monkeypatch):
    calls = _mock_install(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    _mock_fs(monkeypatch)
    apk = os.path.join(os.getcwd(), "app.apk")

    adbtool.main(["install", apk])

    assert calls == [(["adb-bin", "-s", "serial-1", "install", "-r", apk], True)]


def test_install_force_adds_d_and_r(monkeypatch):
    calls = _mock_install(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    _mock_fs(monkeypatch)
    apk = os.path.join(os.getcwd(), "app.apk")

    adbtool.main(["install", "-f", apk])

    assert calls == [(["adb-bin", "-s", "serial-1", "install", "-d", "-r", apk], True)]


def test_install_multiple_apks_uses_multi_package(monkeypatch):
    calls = _mock_install(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    _mock_fs(monkeypatch)
    apk1 = os.path.join(os.getcwd(), "base.apk")
    apk2 = os.path.join(os.getcwd(), "config.apk")

    adbtool.main(["install", apk1, apk2])

    assert calls == [
        (
            [
                "adb-bin",
                "-s",
                "serial-1",
                "install-multi-package",
                "-r",
                apk1,
                apk2,
            ],
            True,
        )
    ]


def test_install_filter_only_applies_to_directories(monkeypatch):
    calls = _mock_install(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    explicit_apk = os.path.join(os.getcwd(), "manual.apk")
    apk_dir = os.path.join(os.getcwd(), "outputs")
    old_match = os.path.join(apk_dir, "match-old.apk")
    new_match = os.path.join(apk_dir, "match-new.apk")
    other = os.path.join(apk_dir, "other.apk")
    _mock_fs(
        monkeypatch,
        directories={apk_dir: ["match-old.apk", "match-new.apk", "other.apk"]},
        mtimes={old_match: 100, new_match: 200, other: 300},
    )

    adbtool.main(["install", explicit_apk, apk_dir, "--filter", "match"])

    assert calls == [
        (
            [
                "adb-bin",
                "-s",
                "serial-1",
                "install-multi-package",
                "-r",
                explicit_apk,
                new_match,
            ],
            True,
        )
    ]


def test_install_run_uses_last_apk_after_success(monkeypatch):
    calls = _mock_install(monkeypatch)
    run_calls = _mock_run(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    _mock_fs(monkeypatch)
    apk1 = os.path.join(os.getcwd(), "base.apk")
    apk2 = os.path.join(os.getcwd(), "feature.apk")

    adbtool.main(["install", "-r", apk1, apk2])

    assert calls == [
        (
            [
                "adb-bin",
                "-s",
                "serial-1",
                "install-multi-package",
                "-r",
                apk1,
                apk2,
            ],
            True,
        )
    ]
    assert run_calls == [(apk2, ["serial-1"])]


def test_install_run_skips_launch_on_failure(monkeypatch):
    _mock_install(monkeypatch, returncodes=[1])
    run_calls = _mock_run(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    _mock_fs(monkeypatch)
    apk = os.path.join(os.getcwd(), "app.apk")

    adbtool.main(["install", "-r", apk])

    assert run_calls == []
