# Technology Stack

**Analysis Date:** 2026-06-02

## Languages

**Primary:**
- Python 3 - CLI tool implementation (`fclean.py`)
- Dart - Target language for generated scaffold files (output only, not part of the tool itself)

## Runtime

**Environment:**
- Python 3 (developed and tested against Python 3.x; no explicit version pin)
- No `.python-version`, `pyproject.toml`, `setup.py`, `setup.cfg`, or `requirements.txt` present

**Package Manager:**
- None — the tool has zero third-party Python dependencies
- No lockfile (not needed)

## Frameworks

**Core:**
- None — uses Python standard library only

**Testing:**
- Not configured (no test framework, no test files)

**Build/Dev:**
- None detected

## Key Dependencies

**Standard Library Modules Used:**
- `sys` — exit on validation failure (`sys.exit(1)`)
- `argparse` — CLI argument parsing (`--features`, `--state`)
- `pathlib.Path` — file/directory creation and path manipulation

**No third-party dependencies.**

## Configuration

**Environment:**
- No environment variables required
- No configuration files
- Tool is invoked directly: `python3 fclean.py --features <name> --state <lib>`

**Build:**
- None — single-file script, no build step

## Platform Requirements

**Development:**
- Python 3.x (standard library only)
- Must be run from the root of a Flutter project (validated via `pubspec.yaml` presence check)

**Production:**
- Same as development — no install, packaging, or deployment step
- Target environment: developer's local machine inside a Flutter project directory

## Generated Output Languages

The tool scaffolds Dart source files for Flutter projects. Supported state management targets:
- `bloc` — generates `*_event.dart`, `*_state.dart`, `*_bloc.dart` using `flutter_bloc`
- `cubit` — generates `*_state.dart`, `*_cubit.dart` using `flutter_bloc`
- `riverpod` — generates `*_provider.dart` using `flutter_riverpod`
- `getx` — generates `*_controller.dart`, `*_binding.dart` using `get`

---

*Stack analysis: 2026-06-02*
