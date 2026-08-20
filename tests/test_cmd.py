import os

import pytest

from adbtool import adbtool, cmd
from adbtool.subcommands import adb as adbcommand


def _clear_android_sdk_env(monkeypatch):
    for env_var in cmd._ANDROID_SDK_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)


def test_android_home_uses_environment_variable_priority(monkeypatch):
    monkeypatch.setenv("ANDROID_HOME", "android-home")
    monkeypatch.setenv("ANDROID_SDK", "android-sdk")
    monkeypatch.setenv("ANDROID_SDK_ROOT", "android-sdk-root")

    assert cmd._get_android_home() == "android-home"

    monkeypatch.delenv("ANDROID_HOME")
    assert cmd._get_android_home() == "android-sdk"

    monkeypatch.delenv("ANDROID_SDK")
    assert cmd._get_android_home() == "android-sdk-root"


def test_android_home_uses_existing_windows_default(monkeypatch):
    _clear_android_sdk_env(monkeypatch)
    monkeypatch.setattr(cmd.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\test\AppData\Local")
    expected = os.path.join(r"C:\Users\test\AppData\Local", "Android", "Sdk")
    monkeypatch.setattr(cmd.os.path, "isdir", lambda path: path == expected)

    assert cmd._get_android_home() == expected


def test_android_home_ignores_missing_windows_default(monkeypatch):
    _clear_android_sdk_env(monkeypatch)
    monkeypatch.setattr(cmd.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\test\AppData\Local")
    monkeypatch.setattr(cmd.os.path, "isdir", lambda path: False)

    assert cmd._get_android_home() is None


def test_android_home_does_not_use_windows_default_on_other_platforms(monkeypatch):
    _clear_android_sdk_env(monkeypatch)
    monkeypatch.setattr(cmd.sys, "platform", "linux")
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\test\AppData\Local")

    assert cmd._get_android_home() is None


@pytest.mark.parametrize(
    ("getter", "fallback"),
    [
        (cmd.getAdb, "adb"),
        (cmd.getAapt, "aapt"),
        (cmd.getZipalign, "zipalign"),
        (cmd.getApksigner, "apksigner"),
        (cmd.get_objdump, "objdump"),
    ],
)
def test_android_tools_fall_back_to_path_without_sdk(monkeypatch, getter, fallback):
    monkeypatch.setattr(cmd, "_get_android_home", lambda: None)

    assert getter() == fallback


def _mock_adb(monkeypatch, returncodes=None):
    calls = []
    codes = [0] if returncodes is None else list(returncodes)

    def fake_get_adb():
        return "adb-bin"

    def fake_call_argv(args, printOutput=False):
        calls.append((list(args), printOutput))
        return "", codes.pop(0) if codes else 0

    monkeypatch.setattr(adbcommand, "getAdb", fake_get_adb)
    monkeypatch.setattr(adbcommand, "call_argv", fake_call_argv)
    return calls


def _mock_devices(monkeypatch, serials, devices=None):
    actual_devices = [object() for _ in serials] if devices is None else devices

    def fake_do_argument_parser(args):
        return list(serials), list(actual_devices)

    monkeypatch.setattr(adbcommand.adbdevice, "doArgumentParser", fake_do_argument_parser)


def test_adb_passthrough_devices_requires_double_dash(monkeypatch):
    calls = _mock_adb(monkeypatch)

    adbtool.main(["adb", "--", "devices"])

    assert calls == [(["adb-bin", "devices"], True)]


def test_adb_passthrough_option_like_args(monkeypatch):
    calls = _mock_adb(monkeypatch)

    adbtool.main(["adb", "--", "-H", "localhost", "devices"])

    assert calls == [(["adb-bin", "-H", "localhost", "devices"], True)]


def test_adb_passthrough_with_device_filter(monkeypatch):
    calls = _mock_adb(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"], devices=[object()])

    adbtool.main(["adb", "-d", "1", "--", "shell"])

    assert calls == [(["adb-bin", "-s", "serial-1", "shell"], True)]


def test_adb_passthrough_multiple_devices(monkeypatch):
    calls = _mock_adb(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1", "serial-2"])

    adbtool.main(["adb", "-d", "a", "--", "shell", "pwd"])

    assert calls == [
        (["adb-bin", "-s", "serial-1", "shell", "pwd"], True),
        (["adb-bin", "-s", "serial-2", "shell", "pwd"], True),
    ]


def test_adb_passthrough_allows_native_adb_dash_d(monkeypatch):
    calls = _mock_adb(monkeypatch)

    adbtool.main(["adb", "--", "-d", "shell"])

    assert calls == [(["adb-bin", "-d", "shell"], True)]


def test_adb_passthrough_with_global_config(monkeypatch):
    calls = _mock_adb(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"], devices=[object()])

    adbtool.main(["-c", "tests/config.yml", "adb", "-d", "1", "--", "shell"])

    assert calls == [(["adb-bin", "-s", "serial-1", "shell"], True)]


def test_adb_passthrough_help_uses_subcommand_help(monkeypatch):
    calls = _mock_adb(monkeypatch)

    with pytest.raises(SystemExit) as exc:
        adbtool.main(["adb", "-h"])

    assert exc.value.code == 0
    assert calls == []


def test_adb_passthrough_adb_help(monkeypatch):
    calls = _mock_adb(monkeypatch)

    adbtool.main(["adb", "--", "-h"])

    assert calls == [(["adb-bin", "-h"], True)]


def test_adb_without_passthrough_args_shows_help(monkeypatch):
    calls = _mock_adb(monkeypatch)

    with pytest.raises(SystemExit) as exc:
        adbtool.main(["adb"])

    assert exc.value.code == 0
    assert calls == []


def test_adb_with_empty_passthrough_runs_bare_adb_without_device_selection(monkeypatch):
    calls = _mock_adb(monkeypatch)
    monkeypatch.setattr(
        adbcommand.adbdevice,
        "doArgumentParser",
        lambda args: pytest.fail("device selection must not run without -d"),
    )

    adbtool.main(["adb", "--"])

    assert calls == [(["adb-bin"], True)]


def test_adb_with_devices_flag_and_no_values_only_lists_devices(monkeypatch):
    calls = _mock_adb(monkeypatch)
    _mock_devices(monkeypatch, [], devices=[])

    adbtool.main(["adb", "-d"])

    assert calls == []


def test_adb_without_device_option_does_not_query_devices(monkeypatch):
    calls = _mock_adb(monkeypatch)
    monkeypatch.setattr(
        adbcommand.adbdevice,
        "doArgumentParser",
        lambda args: pytest.fail("device selection must not run without -d"),
    )

    adbtool.main(["adb", "--", "devices"])

    assert calls == [(["adb-bin", "devices"], True)]


def test_adb_passthrough_exit_code(monkeypatch):
    _mock_adb(monkeypatch, returncodes=[17])

    with pytest.raises(SystemExit) as exc:
        adbtool.main(["adb", "--", "devices"])

    assert exc.value.code == 17


def test_non_adb_unknown_args_still_fail():
    with pytest.raises(SystemExit) as exc:
        adbtool.main(["devices", "-x"])

    assert exc.value.code == 2


def test_adb_requires_double_dash_for_passthrough():
    with pytest.raises(SystemExit) as exc:
        adbtool.main(["adb", "devices"])

    assert exc.value.code == 2


def test_adb_requires_double_dash_after_device_filter():
    with pytest.raises(SystemExit) as exc:
        adbtool.main(["adb", "-d", "shell"])

    assert exc.value.code == 2


def test_unknown_global_args_do_not_leak_into_adb_passthrough():
    with pytest.raises(SystemExit) as exc:
        adbtool.main(["-x", "adb", "--", "shell"])

    assert exc.value.code == 2
