import json
import os
import threading
import zipfile

import pytest

from adbtool import adbtool
from adbtool.subcommands import apkinstall


def _write_xapk(tmp_path, manifest=None, files=None, name="app.xapk"):
    xapk = tmp_path / name
    actual_manifest = {"package_name": "com.example.app"} if manifest is None else manifest
    actual_files = {"com.example.app.apk": b"apk"} if files is None else files
    with zipfile.ZipFile(xapk, "w") as archive:
        archive.writestr("manifest.json", json.dumps(actual_manifest))
        for path, data in actual_files.items():
            archive.writestr(path, data)
    return xapk


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
    directory_map = (
        {} if directories is None else {os.path.abspath(k): v for k, v in directories.items()}
    )
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
    assert "--filter FILTER" in out
    assert "-d, --devices [DEVICE]" in out
    assert "[apkpath ...]" in out


def test_install_repeatable_comma_separated_devices_do_not_consume_apk(monkeypatch):
    calls = _mock_install(monkeypatch)
    parsed_devices = []

    def fake_do_argument_parser(args):
        parsed_devices.append(args.devices)
        return ["serial-1"], [object()]

    monkeypatch.setattr(apkinstall.adbdevice, "doArgumentParser", fake_do_argument_parser)
    _mock_fs(monkeypatch)
    apk = os.path.join(os.getcwd(), "app.apk")

    adbtool.main(["install", "-d", "1,emulator-5554", "-d", "2", apk])

    assert parsed_devices == [["1", "emulator-5554", "2"]]
    assert calls == [(["adb-bin", "-s", "serial-1", "install", "-r", apk], True)]


def test_install_filter_supports_repeated_options_and_commas(monkeypatch):
    calls = _mock_install(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    parsed_filters = []
    apk = os.path.join(os.getcwd(), "app.apk")

    def fake_filter_apks(path, filters):
        parsed_filters.append(filters)
        return [path]

    monkeypatch.setattr(apkinstall, "filterApks", fake_filter_apks)

    adbtool.main(["install", "--filter", "ZGame,arm64", "--filter", "gp", apk])

    assert parsed_filters == [["ZGame", "arm64", "gp"]]
    assert calls == [(["adb-bin", "-s", "serial-1", "install", "-r", apk], True)]


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


def test_install_runs_multiple_serials_in_parallel(monkeypatch):
    calls = []
    entered = []
    release = threading.Event()
    both_started = threading.Event()
    lock = threading.Lock()

    def fake_get_adb():
        return "adb-bin"

    def fake_call_argv(args, printOutput=False):
        with lock:
            calls.append((list(args), printOutput))
            entered.append(args[2])
            if len(entered) == 2:
                both_started.set()
        assert both_started.wait(1), "expected both installs to start before either completed"
        assert release.wait(1), "timed out waiting to release parallel install"
        return "", 0

    monkeypatch.setattr(apkinstall, "getAdb", fake_get_adb)
    monkeypatch.setattr(apkinstall, "call_argv", fake_call_argv)
    _mock_devices(monkeypatch, ["serial-1", "serial-2"])
    _mock_fs(monkeypatch)
    apk = os.path.join(os.getcwd(), "app.apk")

    worker = threading.Thread(target=adbtool.main, args=(["install", apk],))
    worker.start()
    assert both_started.wait(1), "install did not dispatch both serials concurrently"
    release.set()
    worker.join(1)

    assert not worker.is_alive()
    assert calls == [
        (["adb-bin", "-s", "serial-1", "install", "-r", apk], True),
        (["adb-bin", "-s", "serial-2", "install", "-r", apk], True),
    ]


def test_install_run_only_launches_successful_serials(monkeypatch):
    _mock_install(monkeypatch, returncodes=[0, 1])
    run_calls = _mock_run(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1", "serial-2"])
    _mock_fs(monkeypatch)
    apk = os.path.join(os.getcwd(), "app.apk")

    adbtool.main(["install", "-r", apk])

    assert run_calls == [(apk, ["serial-1"])]


def test_install_directory_selects_newest_apk_or_xapk(tmp_path):
    apk = tmp_path / "matching-old.apk"
    xapk = tmp_path / "matching-new.xapk"
    ignored = tmp_path / "matching-newest.txt"
    apk.write_bytes(b"apk")
    xapk.write_bytes(b"xapk")
    ignored.write_bytes(b"ignored")
    os.utime(apk, (100, 100))
    os.utime(xapk, (200, 200))
    os.utime(ignored, (300, 300))

    assert apkinstall.filterApks(str(tmp_path), ["matching"]) == [str(xapk)]


def test_install_single_apk_xapk_uses_install_and_cleans_temp_files(monkeypatch, tmp_path):
    calls = _mock_install(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    xapk = _write_xapk(tmp_path)

    adbtool.main(["install", str(xapk)])

    assert len(calls) == 1
    command, print_output = calls[0]
    assert command[:6] == ["adb-bin", "-s", "serial-1", "install", "-r", command[5]]
    assert command[5].endswith(os.path.join("apks", "000-com.example.app.apk"))
    assert print_output is True
    assert not os.path.exists(command[5])


def test_install_split_xapk_pushes_obb_then_runs_base(monkeypatch, tmp_path):
    calls = _mock_install(monkeypatch)
    run_calls = _mock_run(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    obb_path = "Android/obb/com.example.app/main.1.com.example.app.obb"
    manifest = {
        "package_name": "com.example.app",
        "split_apks": [{"id": "config.arm64_v8a", "file": "config.arm64.apk"}],
        "expansions": [
            {
                "file": obb_path,
                "install_location": "EXTERNAL_STORAGE",
                "install_path": obb_path,
            }
        ],
    }
    xapk = _write_xapk(
        tmp_path,
        manifest,
        {
            "config.arm64.apk": b"split",
            obb_path: b"obb",
            "com.example.app.apk": b"base",
        },
    )

    adbtool.main(["install", "--force", "--run", str(xapk)])

    assert len(calls) == 3
    install_command = calls[0][0]
    assert install_command[:7] == [
        "adb-bin",
        "-s",
        "serial-1",
        "install-multiple",
        "-d",
        "-r",
        install_command[6],
    ]
    assert install_command[6].endswith(os.path.join("apks", "000-com.example.app.apk"))
    assert install_command[7].endswith(os.path.join("apks", "001-config.arm64.apk"))
    assert calls[1] == (
        [
            "adb-bin",
            "-s",
            "serial-1",
            "shell",
            "mkdir",
            "-p",
            "/sdcard/Android/obb/com.example.app",
        ],
        True,
    )
    push_command = calls[2][0]
    assert push_command[:5] == ["adb-bin", "-s", "serial-1", "push", push_command[4]]
    assert push_command[4].endswith(os.path.join("obb", "000-main.1.com.example.app.obb"))
    assert push_command[5] == f"/sdcard/{obb_path}"
    assert run_calls == [(install_command[6], ["serial-1"])]
    assert not os.path.exists(install_command[6])
    assert not os.path.exists(push_command[4])


def test_install_xapk_apk_failure_skips_obb_and_run(monkeypatch, tmp_path):
    calls = _mock_install(monkeypatch, returncodes=[1])
    run_calls = _mock_run(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    obb_path = "Android/obb/com.example.app/main.1.com.example.app.obb"
    xapk = _write_xapk(
        tmp_path,
        {
            "package_name": "com.example.app",
            "expansions": [{"file": obb_path, "install_path": obb_path}],
        },
        {"com.example.app.apk": b"apk", obb_path: b"obb"},
    )

    adbtool.main(["install", "--run", str(xapk)])

    assert len(calls) == 1
    assert run_calls == []


def test_install_xapk_obb_failure_skips_run(monkeypatch, tmp_path):
    calls = _mock_install(monkeypatch, returncodes=[0, 0, 1])
    run_calls = _mock_run(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    obb_path = "Android/obb/com.example.app/main.1.com.example.app.obb"
    xapk = _write_xapk(
        tmp_path,
        {
            "package_name": "com.example.app",
            "expansions": [{"file": obb_path, "install_path": obb_path}],
        },
        {"com.example.app.apk": b"apk", obb_path: b"obb"},
    )

    adbtool.main(["install", "--run", str(xapk)])

    assert len(calls) == 3
    assert calls[-1][0][3] == "push"
    assert run_calls == []


@pytest.mark.parametrize("other_name", ["second.xapk", "second.apk"])
def test_install_xapk_rejects_other_install_inputs(monkeypatch, tmp_path, other_name):
    calls = _mock_install(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    xapk = tmp_path / "app.xapk"
    other = tmp_path / other_name

    with pytest.raises(SystemExit, match="xapk file must be installed by itself"):
        adbtool.main(["install", str(xapk), str(other)])

    assert calls == []


def _invalid_xapk_missing_manifest(tmp_path):
    xapk = tmp_path / "missing-manifest.xapk"
    with zipfile.ZipFile(xapk, "w") as archive:
        archive.writestr("com.example.app.apk", b"apk")
    return xapk


def _invalid_xapk_bad_manifest(tmp_path):
    xapk = tmp_path / "bad-manifest.xapk"
    with zipfile.ZipFile(xapk, "w") as archive:
        archive.writestr("manifest.json", "{")
        archive.writestr("com.example.app.apk", b"apk")
    return xapk


def _invalid_xapk_no_apk(tmp_path):
    return _write_xapk(tmp_path, files={}, name="no-apk.xapk")


def _invalid_xapk_ambiguous_base(tmp_path):
    return _write_xapk(
        tmp_path,
        files={"one.apk": b"one", "two.apk": b"two"},
        name="ambiguous-base.xapk",
    )


def _invalid_xapk_missing_expansion(tmp_path):
    obb_path = "Android/obb/com.example.app/main.1.com.example.app.obb"
    return _write_xapk(
        tmp_path,
        {
            "package_name": "com.example.app",
            "expansions": [{"file": obb_path, "install_path": obb_path}],
        },
        name="missing-expansion.xapk",
    )


def _invalid_xapk_unsafe_install_path(tmp_path):
    return _write_xapk(
        tmp_path,
        {
            "package_name": "com.example.app",
            "expansions": [
                {
                    "file": "main.obb",
                    "install_path": "Android/obb/com.example.app/../../main.obb",
                }
            ],
        },
        {"com.example.app.apk": b"apk", "main.obb": b"obb"},
        name="unsafe-install-path.xapk",
    )


def _invalid_xapk_unsafe_member(tmp_path):
    xapk = tmp_path / "unsafe-member.xapk"
    with zipfile.ZipFile(xapk, "w") as archive:
        archive.writestr("manifest.json", json.dumps({"package_name": "com.example.app"}))
        archive.writestr("../com.example.app.apk", b"apk")
    return xapk


@pytest.mark.parametrize(
    "factory, expected_error",
    [
        (_invalid_xapk_missing_manifest, "missing manifest.json"),
        (_invalid_xapk_bad_manifest, "Expecting property name"),
        (_invalid_xapk_no_apk, "contains no APK files"),
        (_invalid_xapk_ambiguous_base, "can not determine the base APK"),
        (_invalid_xapk_missing_expansion, "missing OBB expansion file"),
        (_invalid_xapk_unsafe_install_path, "contains an unsafe path"),
        (_invalid_xapk_unsafe_member, "contains an unsafe path"),
    ],
)
def test_install_rejects_invalid_xapk_before_adb(monkeypatch, tmp_path, factory, expected_error):
    calls = _mock_install(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    xapk = factory(tmp_path)

    with pytest.raises(SystemExit, match=expected_error):
        adbtool.main(["install", str(xapk)])

    assert calls == []


def test_install_rejects_corrupt_xapk_before_adb(monkeypatch, tmp_path):
    calls = _mock_install(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])
    xapk = tmp_path / "corrupt.xapk"
    xapk.write_bytes(b"not a zip")

    with pytest.raises(SystemExit, match="File is not a zip file"):
        adbtool.main(["install", str(xapk)])

    assert calls == []
