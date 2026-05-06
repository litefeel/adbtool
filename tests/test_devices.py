import pytest
from adbtool import adbtool
from adbtool.subcommands import adbdevice


def test_default():
    _assert_success("devices")


def _assert_success(cmd=None):
    args = [] if cmd is None else cmd.split()
    adbtool.main(args)


def _mock_adb_devices(monkeypatch, output):
    def fake_call(cmd):
        return output, True

    monkeypatch.setattr(adbdevice, "call", fake_call)
    monkeypatch.setattr(adbdevice, "getAdb", lambda: "adb-bin")


def test_get_devices_parses_unauthorized_without_crashing(monkeypatch):
    _mock_adb_devices(
        monkeypatch,
        """List of devices attached
1A151FDF6007GC         device product:oriole model:Pixel_6 device:oriole transport_id:2
R58N3519NEW            unauthorized transport_id:3
""",
    )

    devices = adbdevice.get_devices()

    assert [device.serial for device in devices] == ["1A151FDF6007GC", "R58N3519NEW"]
    assert devices[0].model == "Pixel_6"
    assert devices[1].state == "unauthorized"
    assert devices[1].model == ""


def test_do_argument_parser_fails_fast_when_all_includes_unauthorized(monkeypatch, capsys):
    _mock_adb_devices(
        monkeypatch,
        """List of devices attached
1A151FDF6007GC         device product:oriole model:Pixel_6 device:oriole transport_id:2
2c2c095d5f1d7ece       device product:a8sqltezc model:SM_G8870 device:a8sqltechn transport_id:1
R58N3519NEW            unauthorized transport_id:3
""",
    )

    args = type("Args", (), {"devices": ["a"]})()
    with pytest.raises(SystemExit) as exc:
        adbdevice.doArgumentParser(args)

    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "Device R58N3519NEW is unauthorized" in out
    assert "Please allow USB debugging" in out
    assert "Abort: all target devices must be available." in out


def test_do_argument_parser_allows_available_serial_when_other_device_is_unauthorized(monkeypatch):
    _mock_adb_devices(
        monkeypatch,
        """List of devices attached
1A151FDF6007GC         device product:oriole model:Pixel_6 device:oriole transport_id:2
R58N3519NEW            unauthorized transport_id:3
""",
    )

    args = type("Args", (), {"devices": ["1A"]})()
    serials, devices = adbdevice.doArgumentParser(args)

    assert serials == ["1A151FDF6007GC"]
    assert [device.state for device in devices] == ["device"]
