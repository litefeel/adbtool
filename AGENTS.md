# AGENTS.md

This file gives Codex agents the project-specific context needed to work in this
repository.

## Project Overview

- `adbtool` is a Python 3.10+ package that provides the `adbt` command-line tool.
- The package entry point is declared in `pyproject.toml`:
  `adbt = "adbtool.adbtool:main"`.
- Core package code lives in `adbtool/`.
- CLI subcommands live in `adbtool/subcommands/`.
- Tests live in `tests/`.
- Android SDK tools are discovered through `ANDROID_HOME`, `ANDROID_SDK`, or
  `ANDROID_SDK_ROOT` when needed.

## Repository Layout

- `adbtool/adbtool.py`: main CLI parser, global options, and subcommand dispatch.
- `adbtool/cmd.py`: subprocess wrappers and Android/Unity tool path discovery.
- `adbtool/config.py`: YAML config loading and device/group configuration.
- `adbtool/subcommands/*.py`: individual `adbt` subcommands.
- `tests/`: pytest coverage for CLI parsing and command behavior.
- `tests/config.yml`: test fixture for global config behavior.
- `test/adbtooltest.apk`: APK fixture used by tests/examples.
- `README.md`: user-facing command examples and behavior notes.
- `pyproject.toml`: package metadata, dependencies, dependency groups, script
  entry point, and Ruff configuration.
- `uv.lock`: locked dependency graph for reproducible uv installs.

## Development Commands

Use these commands from the repository root.

```powershell
uv sync
uv run pytest
uv run pytest tests/test_cmd.py
uv run ruff format adbtool tests
```

The project uses Hatchling as its build backend:

```powershell
uv build
```

## Code Style

- Follow `.editorconfig`: UTF-8, spaces, 4-space indentation, final newline.
- Follow `pyproject.toml`: Ruff line length is 100.
- Keep public CLI behavior compatible with README examples unless the user
  explicitly asks for a behavior change.
- Prefer typed function signatures for new code, matching the current style.
- Use `call_argv()` for argument-list subprocess execution when possible.
  Prefer it over constructing shell strings for new subprocess behavior.
- Keep subcommand modules focused: define `addcommand(parser)` and
  `docommand(args, cfg)` for new subcommands.

## Testing Guidance

- Run `uv run pytest` before finishing changes when feasible.
- For parser or CLI dispatch changes, add focused tests under `tests/`.
- For subprocess behavior, mock `call`, `call_argv`, `getAdb`, or related tool
  discovery functions instead of requiring real Android SDK tools or devices.
- Avoid tests that require a connected Android device unless the user explicitly
  asks for integration testing.
- If changing README command examples, update or add tests for the corresponding
  parser behavior.

## ADB And External Tool Constraints

- Do not run real `adb`, `aapt`, `zipalign`, `apksigner`, Unity, or Mali Offline
  Compiler commands unless the user explicitly asks for a live integration check.
- When changing Android SDK discovery, preserve lookup order unless there is a
  clear reason to change it:
  `ANDROID_HOME`, then `ANDROID_SDK`, then `ANDROID_SDK_ROOT`.
- Be careful with Windows-specific behavior in signing and tool discovery paths.
- `adbt adb` has special parsing behavior: native adb arguments must appear after
  `--`. Preserve this contract unless explicitly changing it.
