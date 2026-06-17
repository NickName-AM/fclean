---
phase: 03-tool-test-suite
reviewed: 2026-06-17T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - tests/test_utils.py
  - tests/test_generator.py
  - fclean/generators/feature.py
  - tests/test_templates.py
findings:
  critical: 0
  warning: 6
  info: 3
  total: 9
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-06-17
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Four files were reviewed: two test modules (`tests/test_utils.py`, `tests/test_generator.py`), one production module (`fclean/generators/feature.py`), and one additional test module (`tests/test_templates.py`). The implementation is broadly correct — path traversal is blocked by `validate_name`, the `dry_run` flag correctly suppresses all filesystem writes, and the skip-existing idempotency behaviour works as expected. No security vulnerabilities were found.

Defects are concentrated in test quality and one latent data-corruption risk in the production utility. Six warnings cover: silent lowercasing in `to_pascal_case`, missing exit-code assertions on three `validate_name` tests, weak integration coverage for `bloc` mode relative to all other state types, no test for the invalid `state_type` exit path, a riverpod test that accesses content by positional index rather than explicit key, and a misleading "Generated" print during dry runs. Three info items cover the `test_bloc_class_names` duplication, an unenforced `is_flutter_project` guard, and the forever-skipped provider test.

---

## Warnings

### WR-01: `to_pascal_case` uses `str.capitalize()` which silently lowercases non-initial characters

**File:** `fclean/generators/feature.py` (cross-ref: `fclean/generators/validator.py:13`)
**Issue:** `str.capitalize()` sets the first character to uppercase and **lowercases every subsequent character**. For a word segment like `"feature2A"`, it produces `"Feature2a"`, silently destroying the trailing `A`. The current `_NAME_RE` validator only admits `[a-z0-9_]`, so no existing caller can trigger this today. However, `to_pascal_case` is a public API exported from `fclean/__init__.py`, its docstring does not document the all-lowercase constraint, and any future relaxation of the validator (or a directly-called utility use) will produce incorrect Dart class names without any error. None of the tests exercises a segment that would expose this (all test segments are pure lowercase).

**Fix:** Replace `capitalize()` with an explicit head-uppercase that preserves the tail, and filter empty segments:
```python
def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase for Dart class names."""
    return "".join(
        word[:1].upper() + word[1:] for word in name.split("_") if word
    )
```
The `if word` guard also makes the trailing-underscore behaviour explicit instead of relying on `"".capitalize() == ""`.

---

### WR-02: Three `validate_name` failure tests never assert exit code

**File:** `tests/test_utils.py:42-49,52-54`
**Issue:** `test_validate_name_uppercase_exits` (line 42), `test_validate_name_leading_digit_exits` (line 47), and `test_validate_name_empty_exits` (line 52) all capture `SystemExit` but never assert `exc_info.value.code == 1`. These tests pass even if `validate_name` calls `sys.exit(0)` or `sys.exit(99)`. The three other error tests in the same file (`test_validate_name_invalid_exits`, `test_validate_name_hyphen_exits`, `test_validate_name_space_exits`) all correctly assert `exc_info.value.code == 1`. The inconsistency leaves part of the exit-code contract unguarded.

**Fix:**
```python
def test_validate_name_uppercase_exits():
    with pytest.raises(SystemExit) as exc_info:
        validate_name("User")
    assert exc_info.value.code == 1

def test_validate_name_leading_digit_exits():
    with pytest.raises(SystemExit) as exc_info:
        validate_name("1auth")
    assert exc_info.value.code == 1

def test_validate_name_empty_exits():
    with pytest.raises(SystemExit) as exc_info:
        validate_name("")
    assert exc_info.value.code == 1
```

---

### WR-03: `test_create_feature_creates_expected_files` asserts only 2 of 7+ files for `bloc` mode

**File:** `tests/test_generator.py:13-17`
**Issue:** The bloc integration test asserts only `auth_repository.dart` (domain layer) and `auth_bloc.dart` (presentation layer). All other state-type integration tests — `test_create_feature_cubit` (line 26), `test_create_feature_riverpod` (line 37), `test_create_feature_getx` (line 47) — each assert the full data layer (`auth_remote_datasource.dart`, `auth_local_datasource.dart`, `auth_repository_impl.dart`) plus their state-layer files. A regression that deletes data-layer files in `bloc` mode would go undetected by this test while being caught for every other state type.

**Fix:** Align bloc integration coverage with the other state-type tests:
```python
def test_create_feature_creates_expected_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "bloc")
    assert (tmp_path / "lib/features/auth/data/datasources/auth_remote_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/datasources/auth_local_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/repository/auth_repository_impl.dart").exists()
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/bloc/auth_event.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/bloc/auth_state.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/bloc/auth_bloc.dart").exists()
```

---

### WR-04: No test covers the invalid `state_type` exit path in `create_feature`

**File:** `tests/test_generator.py` (missing), cross-referenced with `fclean/generators/feature.py:70-76`
**Issue:** `feature.py` lines 70-76 guard against an unknown `state_type` string with `sys.exit(1)`. This entire branch has zero test coverage. A refactor that accidentally removes the guard, changes the error condition, or modifies `state_map` keys will silently break the exit behaviour.

**Fix:**
```python
def test_create_feature_invalid_state_type_exits(tmp_path, monkeypatch):
    import pytest
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc_info:
        create_feature("auth", "redux")
    assert exc_info.value.code == 1
```

---

### WR-05: `test_riverpod_typed` accesses template content by positional index instead of explicit key

**File:** `tests/test_templates.py:13`
**Issue:** `content = list(templates.values())[0]` retrieves the first dict value by insertion order. `get_riverpod_templates` currently returns a single-key dict, so index 0 is always the provider file. If a second key is added to the template (e.g., a separate state file), this line silently shifts to asserting against whichever key happens to sort first in insertion order — potentially asserting against the wrong file with no test failure.

**Fix:**
```python
def test_riverpod_typed():
    templates = get_riverpod_templates("user_profile")
    content = templates["presentation/providers/user_profile_provider.dart"]
    assert "StateNotifierProvider<" in content
    assert "UserProfileNotifier" in content
    assert "UserProfileState" in content
    assert "Provider((ref) => null)" not in content
```

---

### WR-06: `print("Generated feature: ...")` fires unconditionally during dry runs, producing misleading output

**File:** `fclean/generators/feature.py:93`
**Issue:** Line 93 always prints `"Generated feature: auth (State: bloc)"`. When `dry_run=True`, no files are created, so "Generated" is factually wrong. The tests `test_dry_run_no_files_written` and `test_dry_run_prints_all_expected_paths` do not assert the content or absence of this message, so the misleading output goes undetected.

**Fix:**
```python
    if dry_run:
        print(f"Dry run: would generate feature '{feature_name}' (State: {state_type or 'None'})")
    else:
        print(f"Generated feature: {feature_name} (State: {state_type or 'None'})")
```

---

## Info

### IN-01: Duplicate bloc class-name assertion between `test_generator.py` and `test_templates.py`

**File:** `tests/test_generator.py:4-10` and `tests/test_templates.py:20-25`
**Issue:** `test_bloc_class_names` and `test_bloc_template_class_names` both call `get_bloc_templates("user_profile")` and assert the same three strings (`UserProfileBloc`, `UserProfileEvent`, `UserProfileState`). The tests are functionally identical. A bloc template change requires updating both; a failure reports twice under different names.

**Fix:** Remove `test_bloc_class_names` from `tests/test_generator.py`. The template-level assertion belongs in `tests/test_templates.py`.

---

### IN-02: `is_flutter_project()` guard has no test coverage

**File:** `fclean/generators/feature.py:11-13`
**Issue:** `is_flutter_project()` is the only safeguard against running the tool outside a Flutter project. All integration tests call `create_feature()` directly, bypassing the guard. An accidental inversion of the condition (`not Path("pubspec.yaml").exists()` instead of `Path("pubspec.yaml").exists()`) would not be caught by any test.

**Fix:** Add two unit tests:
```python
def test_is_flutter_project_true(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pubspec.yaml").write_text("name: my_app\n")
    from fclean.generators.feature import is_flutter_project
    assert is_flutter_project() is True

def test_is_flutter_project_false(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from fclean.generators.feature import is_flutter_project
    assert is_flutter_project() is False
```

---

### IN-03: Permanently-skipped provider test will silently stay skipped when the feature lands

**File:** `tests/test_templates.py:54-59`
**Issue:** `@pytest.mark.skip` will continue skipping the test indefinitely even after `get_provider_templates` is implemented and exported. There is no mechanism to surface "this test should now be un-skipped." Using `pytest.mark.xfail(raises=ImportError, strict=True)` would flip to a test failure the moment the import succeeds, alerting the developer to remove the marker.

**Fix:**
```python
@pytest.mark.xfail(raises=ImportError, strict=True,
                   reason="Phase 5: provider/ChangeNotifier template pending STATE-01")
def test_provider_template_class_names():
    from fclean import get_provider_templates
    templates = get_provider_templates("auth")
    all_content = " ".join(templates.values())
    assert "AuthChangeNotifier" in all_content
```

---

_Reviewed: 2026-06-17_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
