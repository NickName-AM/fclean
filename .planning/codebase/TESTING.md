# Testing Patterns

**Analysis Date:** 2026-06-02

## Current State

**No tests exist.** The project consists of a single file (`fclean.py`, 142 lines) with no accompanying test files, no test runner configuration, and no CI pipeline.

## Test Framework

**Runner:** None configured.

Recommended framework for this Python CLI project: `pytest` (standard for Python CLI tools).

**Config file:** Not present. Would live at `pyproject.toml` or `pytest.ini`.

**Run Commands (if tests were added):**
```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=fclean       # Coverage report (requires pytest-cov)
```

## Test File Organization

**Current:** No test files.

**Recommended layout when tests are added:**
```
fclean/
├── fclean.py
└── tests/
    ├── test_templates.py       # Unit tests for get_*_templates functions
    ├── test_create_feature.py  # Integration tests for create_feature (uses tmp_path)
    └── test_cli.py             # CLI argument parsing tests
```

**Naming convention to follow:**
- Test files: `test_<module_or_function_group>.py`
- Test functions: `test_<function>_<scenario>` (e.g. `test_create_feature_with_entity`)

## What Should Be Tested (Priority Order)

### High Priority — Core Logic

**`is_flutter_project()`** (`fclean.py:5`)
- Returns `True` when `pubspec.yaml` is present in cwd
- Returns `False` when `pubspec.yaml` is absent

**`get_bloc_templates(feature)`** (`fclean.py:9`)
- Returns correct dict keys (file paths) for given feature name
- Generated file content contains correct class names (PascalCase from `feature.capitalize()`)
- Same checks apply to `get_cubit_templates`, `get_riverpod_templates`, `get_getx_templates`

**`create_feature(feature_arg, state_type)`** (`fclean.py:71`)
- Creates expected directories under `lib/features/<name>/`
- Creates base files (remote datasource, local datasource, repository interface, repository impl)
- Creates entity + model files when `feature_arg` contains `:entity` suffix
- Does NOT create entity/model files when no entity is specified
- Does NOT overwrite existing files (skips with print message)
- Generates correct state management files when `state_type` is set
- Generates no state management files when `state_type` is `None`

### Medium Priority — CLI

**`main()` / `argparse` setup** (`fclean.py:127`)
- `--features` is required; exits with error when missing
- `--state` rejects values outside `["bloc", "cubit", "riverpod", "getx"]`
- Exits with code `1` when not in a Flutter project root

### Low Priority — Output

- Print messages are human-readable (smoke check)
- Skipped-file message includes relative path

## Testing Patterns to Use

**Filesystem isolation — use `pytest`'s `tmp_path` fixture:**
```python
def test_create_feature_creates_directories(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pubspec.yaml").touch()
    create_feature("auth", "bloc")
    assert (tmp_path / "lib/features/auth/data/datasources").is_dir()
```

**Testing CLI exit codes — use `subprocess` or `pytest`'s `capsys`:**
```python
import subprocess, sys
def test_exits_when_not_flutter_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = subprocess.run([sys.executable, "fclean.py", "--features", "auth"], capture_output=True)
    assert result.returncode == 1
```

**Template content assertions:**
```python
def test_bloc_template_class_names():
    templates = get_bloc_templates("auth")
    assert "class AuthBloc" in templates["presentation/bloc/auth_bloc.dart"]
    assert "class AuthEvent" in templates["presentation/bloc/auth_event.dart"]
```

## Mocking

**What to mock:**
- `Path.exists()` in `is_flutter_project` tests (alternative: use `monkeypatch.chdir` to a real tmp dir)
- `print()` via `capsys` if asserting on user-facing messages

**What NOT to mock:**
- Filesystem operations in `create_feature` — use `tmp_path` for real isolation instead

## Coverage

**Current:** 0% — no tests exist.

**Target:** Aim for 80%+ covering all template functions and the `create_feature` happy path + edge cases.

**View coverage:**
```bash
pytest --cov=fclean --cov-report=term-missing
```

## Test Coverage Gaps (Current)

| Area | Gap | Risk |
|------|-----|------|
| `is_flutter_project` | Untested | Low — trivial, but guards entry point |
| All `get_*_templates` | Untested | Medium — class name generation could regress |
| `create_feature` directory creation | Untested | High — core feature, no regression safety |
| `create_feature` file collision skip | Untested | High — data-safety feature entirely untested |
| `create_feature` entity conditional | Untested | Medium — entity/model logic could silently break |
| CLI `--state` validation | Untested | Low — handled by argparse |
| Non-Flutter-project exit | Untested | Medium — user-facing error path |

---

*Testing analysis: 2026-06-02*
