import argparse
import os

import pytest

from adbtool import cmd
from adbtool.subcommands import hdcdevice


def test_get_hdc_uses_configured_tool_directory(monkeypatch):
    monkeypatch.setattr(cmd.sys, "platform", "win32")

    assert cmd.getHdc(r"D:\Harmony SDK\toolchains") == os.path.join(
        r"D:\Harmony SDK\toolchains", "hdc.exe"
    )


def test_get_hdc_uses_existing_windows_default(monkeypatch):
    monkeypatch.setattr(cmd.sys, "platform", "win32")
    monkeypatch.setattr(cmd.os.path, "isfile", lambda path: True)

    assert cmd.getHdc() == os.path.join(cmd._DEFAULT_WINDOWS_HDC_DIR, "hdc.exe")


def test_get_hdc_falls_back_to_path(monkeypatch):
    monkeypatch.setattr(cmd.sys, "platform", "win32")
    monkeypatch.setattr(cmd.os.path, "isfile", lambda path: False)

    assert cmd.getHdc() == "hdc"


def _mock_hdc_targets(monkeypatch, output, returncode=0):
    calls = []

    def fake_call_argv(args, printOutput=False):
        calls.append((list(args), printOutput))
        return output, returncode

    monkeypatch.setattr(hdcdevice, "call_argv", fake_call_argv)
    return calls


def test_hdc_devices_are_parsed_and_sorted(monkeypatch):
    calls = _mock_hdc_targets(
        monkeypatch,
        "serial-b USB Connected localhost hdc\r\nserial-a TCP Offline localhost hdc\r\n",
    )

    devices = hdcdevice.get_devices("hdc-bin")

    assert calls == [(["hdc-bin", "list", "targets", "-v"], False)]
    assert [device.serial for device in devices] == ["serial-a", "serial-b"]
    assert [device.online for device in devices] == [False, True]


def test_hdc_uart_devices_are_ignored_case_insensitively(monkeypatch):
    _mock_hdc_targets(
        monkeypatch,
        "serial-uart UART Connected localhost hdc\n"
        "serial-mixed UaRt Connected localhost hdc\n"
        "serial-usb USB Connected localhost hdc\n"
        "serial-tcp TCP Connected localhost hdc\n"
        "legacy-serial\n",
    )

    devices = hdcdevice.get_devices("hdc-bin")

    assert [device.serial for device in devices] == [
        "legacy-serial",
        "serial-tcp",
        "serial-usb",
    ]
    assert devices[0].connection_type == ""


def test_hdc_uart_devices_do_not_affect_listing_or_selection(monkeypatch, capsys):
    _mock_hdc_targets(
        monkeypatch,
        "serial-uart UART Connected localhost hdc\nserial-usb USB Connected localhost hdc\n",
    )
    devices = hdcdevice.get_devices("hdc-bin")

    hdcdevice.print_devices(devices)

    output = capsys.readouterr().out
    assert "serial-uart" not in output
    assert "serial-usb" in output
    assert [device.serial for device in hdcdevice.select_devices(devices, ["1"])] == ["serial-usb"]
    assert hdcdevice.select_devices(devices, ["a"]) == devices
    assert hdcdevice.select_devices(devices, ["serial-uart"]) == []


def test_hdc_empty_target_marker_is_ignored(monkeypatch):
    _mock_hdc_targets(monkeypatch, "[Empty]\n")

    assert hdcdevice.get_devices("hdc-bin") == []


def test_hdc_device_selection_supports_index_prefix_and_all():
    devices = [
        hdcdevice.Device("serial-a USB Connected localhost hdc"),
        hdcdevice.Device("serial-b USB Connected localhost hdc"),
    ]

    assert [device.serial for device in hdcdevice.select_devices(devices, ["1"])] == ["serial-a"]
    assert [device.serial for device in hdcdevice.select_devices(devices, ["serial-b"])] == [
        "serial-b"
    ]
    assert hdcdevice.select_devices(devices, ["a"]) == devices


def test_hdc_device_list_request_does_not_select_targets(monkeypatch, capsys):
    _mock_hdc_targets(monkeypatch, "serial-a USB Connected localhost hdc\n")
    args = argparse.Namespace(devices=[])

    serials, devices = hdcdevice.doArgumentParser(args, "hdc-bin")

    assert serials == []
    assert devices == []
    assert "serial-a" in capsys.readouterr().out


def test_hdc_offline_target_aborts(monkeypatch, capsys):
    _mock_hdc_targets(monkeypatch, "serial-a USB Offline localhost hdc\n")
    args = argparse.Namespace(devices=None)

    with pytest.raises(SystemExit) as exc:
        hdcdevice.doArgumentParser(args, "hdc-bin")

    assert exc.value.code == 1
    assert "HDC device serial-a is Offline" in capsys.readouterr().out
