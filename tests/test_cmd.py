import pytest

from adbtool import adbtool
from adbtool.subcommands import adb as adbcommand


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
    _mock_devices(monkeypatch, ["serial-1"])

    adbtool.main(["adb", "--", "devices"])

    assert calls == [(["adb-bin", "-s", "serial-1", "devices"], True)]


def test_adb_passthrough_option_like_args(monkeypatch):
    calls = _mock_adb(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])

    adbtool.main(["adb", "--", "-H", "localhost", "devices"])

    assert calls == [(["adb-bin", "-s", "serial-1", "-H", "localhost", "devices"], True)]


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
    _mock_devices(monkeypatch, ["serial-1"])

    adbtool.main(["adb", "--", "-d", "shell"])

    assert calls == [(["adb-bin", "-s", "serial-1", "-d", "shell"], True)]


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
    _mock_devices(monkeypatch, ["serial-1"])

    adbtool.main(["adb", "--", "-h"])

    assert calls == [(["adb-bin", "-s", "serial-1", "-h"], True)]


def test_adb_without_passthrough_args_shows_help(monkeypatch):
    calls = _mock_adb(monkeypatch)

    with pytest.raises(SystemExit) as exc:
        adbtool.main(["adb"])

    assert exc.value.code == 0
    assert calls == []


def test_adb_with_empty_passthrough_runs_bare_adb_for_selected_device(monkeypatch):
    calls = _mock_adb(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1"])

    adbtool.main(["adb", "--"])

    assert calls == [(["adb-bin", "-s", "serial-1"], True)]


def test_adb_with_devices_flag_and_no_values_only_lists_devices(monkeypatch):
    calls = _mock_adb(monkeypatch)
    _mock_devices(monkeypatch, [], devices=[])

    adbtool.main(["adb", "-d"])

    assert calls == []


def test_adb_without_device_selection_does_not_run_for_multiple_devices(monkeypatch):
    calls = _mock_adb(monkeypatch)
    _mock_devices(monkeypatch, ["serial-1", "serial-2"], devices=[object(), object()])

    adbtool.main(["adb", "--", "devices"])

    assert calls == []


def test_adb_passthrough_exit_code(monkeypatch):
    _mock_adb(monkeypatch, returncodes=[17])
    _mock_devices(monkeypatch, ["serial-1"])

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
