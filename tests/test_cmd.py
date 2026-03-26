import pytest

from adbtool import adbtool
from adbtool.subcommands import adb as adbcommand


def _mock_adb(monkeypatch, returncode=0):
    calls = []

    def fake_get_adb():
        return "adb-bin"

    def fake_call_argv(args, printOutput=False):
        calls.append((list(args), printOutput))
        return "", returncode

    monkeypatch.setattr(adbcommand, "getAdb", fake_get_adb)
    monkeypatch.setattr(adbcommand, "call_argv", fake_call_argv)
    return calls


def test_adb_passthrough_devices(monkeypatch):
    calls = _mock_adb(monkeypatch)

    adbtool.main(["adb", "devices"])

    assert calls == [(["adb-bin", "devices"], True)]


def test_adb_passthrough_option_like_args(monkeypatch):
    calls = _mock_adb(monkeypatch)

    adbtool.main(["adb", "-H", "localhost", "devices"])

    assert calls == [(["adb-bin", "-H", "localhost", "devices"], True)]


def test_adb_passthrough_dash_d(monkeypatch):
    calls = _mock_adb(monkeypatch)

    adbtool.main(["adb", "-d", "shell"])

    assert calls == [(["adb-bin", "-d", "shell"], True)]


def test_adb_passthrough_with_global_config(monkeypatch):
    calls = _mock_adb(monkeypatch)

    adbtool.main(["-c", "tests/config.yml", "adb", "devices"])

    assert calls == [(["adb-bin", "devices"], True)]


def test_adb_passthrough_help(monkeypatch):
    calls = _mock_adb(monkeypatch)

    adbtool.main(["adb", "-h"])

    assert calls == [(["adb-bin", "-h"], True)]


def test_adb_passthrough_exit_code(monkeypatch):
    _mock_adb(monkeypatch, returncode=17)

    with pytest.raises(SystemExit) as exc:
        adbtool.main(["adb", "devices"])

    assert exc.value.code == 17


def test_non_adb_unknown_args_still_fail():
    with pytest.raises(SystemExit) as exc:
        adbtool.main(["devices", "-x"])

    assert exc.value.code == 2


def test_unknown_global_args_do_not_leak_into_adb_passthrough():
    with pytest.raises(SystemExit) as exc:
        adbtool.main(["-x", "adb", "shell"])

    assert exc.value.code == 2
