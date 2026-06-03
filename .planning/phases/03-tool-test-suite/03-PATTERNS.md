# Phase 3: Tool Test Suite - Pattern Map

**Mapped:** 2026-06-03
**Files analyzed:** 4 (3 modified test files + 1 modified source file)
**Analogs found:** 4 / 4

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tests/test_utils.py` | test | request-response (pure function) | `tests/test_utils.py` (existing) | exact — extend in-place |
| `tests/test_generator.py` | test | file-I/O (tmp_path + monkeypatch) | `tests/test_generator.py` (existing) | exact — extend in-place |
| `tests/test_templates.py` | test | request-response (pure function) | `tests/test_templates.py` (existing) | exact — extend in-place |
| `fclean/generators/feature.py` | generator / service | file-I/O | `fclean/generators/feature.py` (existing) | exact — add dry_run param |

---

## Pattern Assignments

### `tests/test_utils.py` (test, request-response)

**Analog:** `tests/test_utils.py` (existing file, lines 1–41)

**Imports pattern** (lines 1–2):
```python
import pytest
from fclean import to_pascal_case, validate_name
```

**Core unit test pattern — to_pascal_case** (lines 5–14):
```python
def test_to_pascal_case_single_word():
    assert to_pascal_case("auth") == "Auth"


def test_to_pascal_case_snake():
    assert to_pascal_case("user_profile") == "UserProfile"


def test_to_pascal_case_with_digit():
    assert to_pascal_case("my_feature2") == "MyFeature2"
```

**Tests to add for TEST-01 (edge cases):**
```python
# Multiple underscores
def test_to_pascal_case_multiple_underscores():
    assert to_pascal_case("my_long_feature_name") == "MyLongFeatureName"

# Trailing underscore — "auth_".split("_") → ["auth", ""], "".capitalize() → ""
def test_to_pascal_case_trailing_underscore():
    result = to_pascal_case("auth_")
    assert result == "Auth"  # empty last segment, not "Auth_"

# Digit at end of segment
def test_to_pascal_case_digit_end_segment():
    assert to_pascal_case("feature2_auth") == "Feature2Auth"
```

**SystemExit assertion pattern** (lines 22–41):
```python
def test_validate_name_invalid_exits():
    with pytest.raises(SystemExit) as exc_info:
        validate_name("../evil")
    assert exc_info.value.code == 1


def test_validate_name_uppercase_exits():
    with pytest.raises(SystemExit):
        validate_name("User")
```

**Tests to add for TEST-04 (edge cases):**
```python
# Hyphen — not matched by _NAME_RE = r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$"
def test_validate_name_hyphen_exits():
    with pytest.raises(SystemExit) as exc_info:
        validate_name("my-feature")
    assert exc_info.value.code == 1

# Space — not matched by _NAME_RE
def test_validate_name_space_exits():
    with pytest.raises(SystemExit) as exc_info:
        validate_name("my feature")
    assert exc_info.value.code == 1

# Double underscore — not matched by _NAME_RE (requires single _ between segments)
def test_validate_name_double_underscore_exits():
    with pytest.raises(SystemExit) as exc_info:
        validate_name("my__feature")
    assert exc_info.value.code == 1
```

---

### `tests/test_generator.py` (test, file-I/O)

**Analog:** `tests/test_generator.py` (existing file, lines 1–24)

**Imports pattern** (line 1):
```python
from fclean import get_bloc_templates, create_feature
```

**Core tmp_path + monkeypatch.chdir pattern** (lines 13–17):
```python
def test_create_feature_creates_expected_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "bloc")
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/bloc/auth_bloc.dart").exists()
```

**Tests to add for TEST-02 — full file sets per state type:**

Cubit (subdirectory: `presentation/cubit/`):
```python
def test_create_feature_cubit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "cubit")
    assert (tmp_path / "lib/features/auth/data/datasources/auth_remote_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/datasources/auth_local_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/repository/auth_repository_impl.dart").exists()
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/cubit/auth_state.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/cubit/auth_cubit.dart").exists()
```

Riverpod (subdirectory: `presentation/providers/`):
```python
def test_create_feature_riverpod(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "riverpod")
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/providers/auth_provider.dart").exists()
```

GetX (subdirectories: `presentation/controller/` and `presentation/bindings/`):
```python
def test_create_feature_getx(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "getx")
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/controller/auth_controller.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/bindings/auth_binding.dart").exists()
```

None state (no state files created):
```python
def test_create_feature_no_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", None)
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    # No bloc/cubit/riverpod/getx directory should exist
    assert not (tmp_path / "lib/features/auth/presentation/bloc").exists()
    assert not (tmp_path / "lib/features/auth/presentation/cubit").exists()
    assert not (tmp_path / "lib/features/auth/presentation/providers").exists()
    assert not (tmp_path / "lib/features/auth/presentation/controller").exists()
```

Entity path (feature_arg format `feature:entity`):
```python
def test_create_feature_with_entity(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth:user", "bloc")
    assert (tmp_path / "lib/features/auth/domain/entities/user.dart").exists()
    assert (tmp_path / "lib/features/auth/data/models/user_model.dart").exists()
```

---

### `tests/test_templates.py` (test, request-response)

**Analog:** `tests/test_templates.py` (existing file, lines 1–11)

**Imports pattern** (line 1):
```python
from fclean import get_riverpod_templates
```

Extend to:
```python
from fclean import (
    get_bloc_templates,
    get_cubit_templates,
    get_riverpod_templates,
    get_getx_templates,
)
```

**Core template content assertion pattern** (lines 4–11):
```python
def test_riverpod_typed():
    templates = get_riverpod_templates("user_profile")
    content = list(templates.values())[0]
    assert "StateNotifierProvider<" in content
    assert "UserProfileNotifier" in content
    assert "UserProfileState" in content
    assert "Provider((ref) => null)" not in content
```

**Tests to add for TEST-03 — remaining template providers:**

Bloc (joins all values, checks class names in content):
```python
def test_bloc_template_class_names():
    templates = get_bloc_templates("user_profile")
    all_content = " ".join(templates.values())
    assert "UserProfileBloc" in all_content
    assert "UserProfileEvent" in all_content
    assert "UserProfileState" in all_content

def test_bloc_template_bloc_file_content():
    templates = get_bloc_templates("auth")
    content = templates["presentation/bloc/auth_bloc.dart"]
    assert "import 'package:flutter_bloc/flutter_bloc.dart';" in content
    assert "class AuthBloc extends Bloc<AuthEvent, AuthState>" in content
```

Cubit (keys are `presentation/cubit/`):
```python
def test_cubit_template_class_names():
    templates = get_cubit_templates("user_profile")
    all_content = " ".join(templates.values())
    assert "UserProfileCubit" in all_content
    assert "UserProfileState" in all_content

def test_cubit_template_keys():
    templates = get_cubit_templates("auth")
    assert "presentation/cubit/auth_cubit.dart" in templates
    assert "presentation/cubit/auth_state.dart" in templates
```

GetX (keys are `presentation/controller/` and `presentation/bindings/`):
```python
def test_getx_template_class_names():
    templates = get_getx_templates("auth")
    all_content = " ".join(templates.values())
    assert "AuthController" in all_content
    assert "AuthBinding" in all_content

def test_getx_template_keys():
    templates = get_getx_templates("auth")
    assert "presentation/controller/auth_controller.dart" in templates
    assert "presentation/bindings/auth_binding.dart" in templates
```

5th template stub (Phase 5 pending):
```python
import pytest

@pytest.mark.skip(reason="Phase 5: provider/ChangeNotifier template pending STATE-01")
def test_provider_template_class_names():
    from fclean import get_provider_templates
    templates = get_provider_templates("auth")
    all_content = " ".join(templates.values())
    assert "AuthChangeNotifier" in all_content
```

**TEST-05 — dry-run tests (uses capsys + tmp_path + monkeypatch):**
```python
def test_dry_run_no_files_written(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "bloc", dry_run=True)
    captured = capsys.readouterr()
    # No files should exist under lib/
    assert not (tmp_path / "lib").exists()
    # Expected paths printed to stdout
    assert "auth_bloc.dart" in captured.out

def test_dry_run_prints_all_expected_paths(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "bloc", dry_run=True)
    captured = capsys.readouterr()
    assert "auth_repository.dart" in captured.out
    assert "auth_remote_datasource.dart" in captured.out
    assert "auth_bloc.dart" in captured.out
```

---

### `fclean/generators/feature.py` (generator/service, file-I/O)

**Analog:** `fclean/generators/feature.py` (existing file, lines 1–90)

**Current signature** (line 16):
```python
def create_feature(feature_arg, state_type):
```

**Signature change for dry_run support:**
```python
def create_feature(feature_arg, state_type, dry_run=False):
```

**Write loop pattern** (lines 82–87 — the section to extend):
```python
    for path, content in files_to_create.items():
        if path.exists():
            print(f"Skipping: {path} already exists.")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
```

**Modified write loop with dry_run guard:**
```python
    for path, content in files_to_create.items():
        if dry_run:
            print(path)
            continue
        if path.exists():
            print(f"Skipping: {path} already exists.")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
```

---

## Shared Patterns

### Fixture Usage Pattern
**Source:** `tests/test_generator.py`, lines 13–17
**Apply to:** All tests that call `create_feature()` (test_generator.py and test_templates.py TEST-05 tests)
```python
def test_create_feature_creates_expected_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "bloc")
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
```
Rule: every `create_feature()` call MUST be preceded by `monkeypatch.chdir(tmp_path)`.

### SystemExit Assertion Pattern
**Source:** `tests/test_utils.py`, lines 22–25
**Apply to:** All invalid-input tests in test_utils.py
```python
with pytest.raises(SystemExit) as exc_info:
    validate_name("../evil")
assert exc_info.value.code == 1
```

### Template Content Assertion Pattern
**Source:** `tests/test_generator.py`, lines 4–10
**Apply to:** All template provider tests in test_templates.py
```python
# Use substring checks (in), never full-content equality (==)
all_content = " ".join(templates.values())
assert "UserProfileBloc" in all_content
```

### Import Convention
**Source:** `tests/test_utils.py` line 2, `tests/test_generator.py` line 1
**Apply to:** All test files
```python
# Import from top-level fclean package (editable install — no sys.path hacks needed)
from fclean import to_pascal_case, validate_name
from fclean import get_bloc_templates, create_feature
```

---

## No Analog Found

All files have close analogs. No entries in this section.

---

## Key Codebase Facts (for planner reference)

### _NAME_RE regex (validator.py, line 16)
```python
_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
```
This rejects: uppercase, leading digit, empty string, hyphen, space, double underscore, trailing underscore.

### Template return key structure (for path assertion accuracy)

| Template | Dict keys (relative paths) |
|----------|---------------------------|
| bloc | `presentation/bloc/{f}_event.dart`, `presentation/bloc/{f}_state.dart`, `presentation/bloc/{f}_bloc.dart` |
| cubit | `presentation/cubit/{f}_state.dart`, `presentation/cubit/{f}_cubit.dart` |
| riverpod | `presentation/providers/{f}_provider.dart` |
| getx | `presentation/controller/{f}_controller.dart`, `presentation/bindings/{f}_binding.dart` |

### Base files always created by create_feature() (regardless of state type)
```
lib/features/{f}/data/datasources/{f}_remote_datasource.dart
lib/features/{f}/data/datasources/{f}_local_datasource.dart
lib/features/{f}/data/repository/{f}_repository_impl.dart
lib/features/{f}/domain/repository/{f}_repository.dart
```

### Entity files created only when `feature:entity` format is used
```
lib/features/{f}/domain/entities/{e}.dart
lib/features/{f}/data/models/{e}_model.dart
```

---

## Metadata

**Analog search scope:** `tests/`, `fclean/generators/`, `fclean/templates/`
**Files scanned:** 9 (`test_utils.py`, `test_generator.py`, `test_templates.py`, `feature.py`, `validator.py`, `bloc.py`, `cubit.py`, `riverpod.py`, `getx.py`)
**Pattern extraction date:** 2026-06-03
