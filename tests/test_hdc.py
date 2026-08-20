import argparse
import os

import pytest

from adbtool import adbtool, cmd
from adbtool.subcommands import hdc as hdccommand
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


def _mock_hdc_command(monkeypatch, serials=None, devices=None, returncodes=None):
    selected_serials = ["serial-1"] if serials is None else list(serials)
    selected_devices = [object() for _ in selected_serials] if devices is None else list(devices)
    codes = [0] if returncodes is None else list(returncodes)
    calls = []
    hdc_dirs = []
    selectors = []

    def fake_get_hdc(hdc_dir=None):
        hdc_dirs.append(hdc_dir)
        return "hdc-bin"

    def fake_do_argument_parser(args, hdc):
        assert hdc == "hdc-bin"
        selectors.append(args.devices)
        return list(selected_serials), list(selected_devices)

    def fake_call_argv(args, printOutput=False):
        calls.append((list(args), printOutput))
        return "", codes.pop(0) if codes else 0

    monkeypatch.setattr(hdccommand, "getHdc", fake_get_hdc)
    monkeypatch.setattr(hdccommand.hdcdevice, "doArgumentParser", fake_do_argument_parser)
    monkeypatch.setattr(hdccommand, "call_argv", fake_call_argv)
    return calls, hdc_dirs, selectors


def test_hdc_passthrough_arguments(monkeypatch):
    calls, _, _ = _mock_hdc_command(monkeypatch)

    adbtool.main(["hdc", "--", "shell", "pwd"])

    assert calls == [(["hdc-bin", "-t", "serial-1", "shell", "pwd"], True)]


def test_hdc_passthrough_option_like_arguments(monkeypatch):
    calls, _, _ = _mock_hdc_command(monkeypatch)

    adbtool.main(["hdc", "--", "-l", "5", "shell"])

    assert calls == [(["hdc-bin", "-t", "serial-1", "-l", "5", "shell"], True)]


def test_hdc_passthrough_with_device_selectors(monkeypatch):
    calls, _, selectors = _mock_hdc_command(
        monkeypatch,
        serials=["serial-1", "serial-2"],
    )

    adbtool.main(["hdc", "-d", "1,serial-2", "-d", "a", "--", "shell"])

    assert selectors == [["1", "serial-2", "a"]]
    assert calls == [
        (["hdc-bin", "-t", "serial-1", "shell"], True),
        (["hdc-bin", "-t", "serial-2", "shell"], True),
    ]


def test_hdc_passthrough_uses_configured_hdc_directory(monkeypatch, tmp_path):
    calls, hdc_dirs, _ = _mock_hdc_command(monkeypatch)
    config_path = tmp_path / "config.yml"
    config_path.write_text("hdc: D:\\Harmony\\toolchains\n", encoding="utf-8")

    adbtool.main(["-c", str(config_path), "hdc", "--", "shell"])

    assert hdc_dirs == [r"D:\Harmony\toolchains"]
    assert calls == [(["hdc-bin", "-t", "serial-1", "shell"], True)]


def test_hdc_passthrough_help_uses_subcommand_help(monkeypatch):
    calls, hdc_dirs, _ = _mock_hdc_command(monkeypatch)

    with pytest.raises(SystemExit) as exc:
        adbtool.main(["hdc", "-h"])

    assert exc.value.code == 0
    assert calls == []
    assert hdc_dirs == []


def test_hdc_passthrough_native_help(monkeypatch):
    calls, _, _ = _mock_hdc_command(monkeypatch)

    adbtool.main(["hdc", "--", "-h"])

    assert calls == [(["hdc-bin", "-t", "serial-1", "-h"], True)]


def test_hdc_without_passthrough_args_shows_help(monkeypatch):
    calls, hdc_dirs, _ = _mock_hdc_command(monkeypatch)

    with pytest.raises(SystemExit) as exc:
        adbtool.main(["hdc"])

    assert exc.value.code == 0
    assert calls == []
    assert hdc_dirs == []


def test_hdc_with_empty_passthrough_runs_bare_hdc_for_selected_device(monkeypatch):
    calls, _, _ = _mock_hdc_command(monkeypatch)

    adbtool.main(["hdc", "--"])

    assert calls == [(["hdc-bin", "-t", "serial-1"], True)]


def test_hdc_with_devices_flag_and_no_values_only_lists_devices(monkeypatch):
    calls, _, selectors = _mock_hdc_command(monkeypatch, serials=[], devices=[])

    adbtool.main(["hdc", "-d"])

    assert selectors == [[]]
    assert calls == []


def test_hdc_without_device_selection_does_not_run_for_multiple_devices(monkeypatch):
    calls, _, _ = _mock_hdc_command(
        monkeypatch,
        serials=["serial-1", "serial-2"],
    )

    adbtool.main(["hdc", "--", "shell"])

    assert calls == []


def test_hdc_passthrough_exit_code(monkeypatch):
    _mock_hdc_command(monkeypatch, returncodes=[17])

    with pytest.raises(SystemExit) as exc:
        adbtool.main(["hdc", "--", "shell"])

    assert exc.value.code == 17


def test_hdc_passthrough_uses_last_nonzero_exit_code(monkeypatch):
    _mock_hdc_command(
        monkeypatch,
        serials=["serial-1", "serial-2", "serial-3"],
        returncodes=[11, 0, 17],
    )

    with pytest.raises(SystemExit) as exc:
        adbtool.main(["hdc", "-d", "a", "--", "shell"])

    assert exc.value.code == 17


def test_hdc_requires_double_dash_for_passthrough():
    with pytest.raises(SystemExit) as exc:
        adbtool.main(["hdc", "shell"])

    assert exc.value.code == 2


def test_hdc_requires_double_dash_after_device_filter():
    with pytest.raises(SystemExit) as exc:
        adbtool.main(["hdc", "-d", "shell"])

    assert exc.value.code == 2
