---
phase: 03-tool-test-suite
reviewed: 2026-06-03T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - tests/test_utils.py
  - tests/test_generator.py
  - fclean/generators/feature.py
  - tests/test_templates.py
  - pyproject.toml
findings:
  critical: 1
  warning: 4
  info: 3
  total: 8
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-06-03T00:00:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Five files reviewed: three test modules (`test_utils.py`, `test_generator.py`, `test_templates.py`), the core feature generator (`fclean/generators/feature.py`), and the package manifest (`pyproject.toml`). The test suite covers happy-path and idempotency cases well. The critical defect is that `test_create_feature_no_state` provides false coverage — it passes while leaving the actual output behavior entirely unverified. Four warnings address brittleness in the riverpod template test, a non-asserting util test, a silent data-corruption risk in `to_pascal_case`, and a missing test for the invalid-state-type code path. Three info items cover test duplication, packaging notes, and a fragile skipped-test import.

---

## Critical Issues

### CR-01: `test_create_feature_no_state` passes without verifying the data-layer output — false coverage

**File:** `tests/test_generator.py:58-65`

**Issue:** The test is named `test_create_feature_no_state` and is supposed to document the behaviour when `state_type=None`. It asserts only that `domain/repository/auth_repository.dart` exists and that four `presentation/` subdirectories do not exist. It makes **no assertion** about the data layer (`data/datasources/`, `data/repository/`). In practice, `create_feature("auth", None)` creates all four data-layer files unconditionally (lines 44-54 of `feature.py` build `files_to_create` regardless of `state_type`). The test is silent on whether this is intentional. Two mutually exclusive behaviours are possible and neither is verified:

- **Intended behaviour A:** `None` means "no presentation layer, full data layer still generated" — the test should assert that data-layer files *do* exist, documenting this as a feature.
- **Intended behaviour B:** `None` means "minimal scaffold — no generated files beyond the domain repository" — the implementation is wrong and the test fails to catch it.

Either way, the test currently passes while leaving a concrete behaviour gap undocumented and unguarded. Any future refactor that accidentally starts or stops creating data-layer files when `state_type=None` will not be caught.

**Fix (for Intended Behaviour A — data layer always created):**

```python
def test_create_feature_no_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", None)
    # domain layer
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    # data layer is still generated even with no state management
    assert (tmp_path / "lib/features/auth/data/datasources/auth_remote_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/datasources/auth_local_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/repository/auth_repository_impl.dart").exists()
    # no presentation state dirs
    assert not (tmp_path / "lib/features/auth/presentation/bloc").exists()
    assert not (tmp_path / "lib/features/auth/presentation/cubit").exists()
    assert not (tmp_path / "lib/features/auth/presentation/providers").exists()
    assert not (tmp_path / "lib/features/auth/presentation/controller").exists()
```

---

## Warnings

### WR-01: `test_riverpod_typed` asserts against positional dict index instead of explicit key

**File:** `tests/test_templates.py:13`

**Issue:** `content = list(templates.values())[0]` retrieves the first dict value by insertion order. `get_riverpod_templates` currently returns a single-key dict, so index 0 is always the provider file. If a second key is added to the template function (e.g., a state file), this test silently shifts to asserting against whichever key happens to be first in the new dict, potentially asserting against the wrong file with no failure.

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

### WR-02: `test_validate_name_valid_passes` has no explicit assertion

**File:** `tests/test_utils.py:31-33`

**Issue:** The test body calls `validate_name("auth")` and `validate_name("user_profile")` with no `assert` statement and no `pytest.raises` context. The implicit assertion is that no `SystemExit` is raised. This works today because `validate_name` calls `sys.exit(1)` on failure, which pytest catches as a test error. However it provides zero signal if the function is changed to return an error value rather than exit, or if a silent regression is introduced (e.g., validation is accidentally skipped). The test name promises something it does not enforce.

**Fix:**

```python
def test_validate_name_valid_passes():
    # Neither call should raise SystemExit
    try:
        validate_name("auth")
        validate_name("user_profile")
    except SystemExit:
        pytest.fail("validate_name raised SystemExit for a valid name")
```

---

### WR-03: `to_pascal_case` uses `str.capitalize()` which silently lowercases non-initial characters

**File:** `fclean/generators/validator.py:13`

**Issue:** `str.capitalize()` lowercases every character after the first. For input `"feature2A"` it produces `"Feature2a"` (the trailing `A` is destroyed). The current validator blocks all uppercase input (`_NAME_RE` only allows `[a-z0-9_]`), so no existing caller can trigger this today. However the function is a general utility exposed in `__init__.py`, the docstring does not document the all-lowercase constraint, and a future caller relaxing that assumption (or a future entity name with a digit+letter segment like `"oauth2_token"`) will get silent corruption. The tests do not exercise this edge case.

**Fix:** Replace `capitalize()` with a manual head-uppercase that preserves remaining characters, and drop empty segments explicitly:

```python
def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase for Dart class names."""
    return "".join(
        word[:1].upper() + word[1:] for word in name.split("_") if word
    )
```

The `if word` filter also makes the trailing-underscore behaviour explicit (empty segment is dropped) rather than relying on `"".capitalize() == ""`.

---

### WR-04: No test covers the invalid `state_type` exit path in `create_feature`

**File:** `tests/test_generator.py` (missing coverage), cross-referenced with `fclean/generators/feature.py:70-76`

**Issue:** Lines 70-76 of `feature.py` guard against unknown `state_type` strings with a `sys.exit(1)`. This code path has zero test coverage. Any refactor of the guard condition (e.g., changing the comparison, altering the `state_map` keys, or accidentally removing the guard) will not be caught.

**Fix:**

```python
def test_create_feature_invalid_state_type_exits(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc_info:
        create_feature("auth", "redux")
    assert exc_info.value.code == 1
```

---

## Info

### IN-01: Duplicate assertion between `test_generator.py` and `test_templates.py`

**File:** `tests/test_generator.py:4-10` and `tests/test_templates.py:20-26`

**Issue:** `test_bloc_class_names` in `test_generator.py` and `test_bloc_template_class_names` in `test_templates.py` assert the exact same three class-name strings (`UserProfileBloc`, `UserProfileEvent`, `UserProfileState`) against `get_bloc_templates("user_profile")`. The two tests are functionally identical. A failure will appear twice in the test run with different IDs, obscuring the root cause, and maintenance of both is required for any bloc template change.

**Fix:** Remove `test_bloc_class_names` from `test_generator.py`; it belongs in `test_templates.py`.

---

### IN-02: `print(f"Generated feature: ...")` executes unconditionally, including during dry run

**File:** `fclean/generators/feature.py:93`

**Issue:** Line 93 prints `"Generated feature: auth (State: bloc)"` even when `dry_run=True`. During a dry run, no files are created, so the message is misleading ("Generated" implies creation). The test `test_dry_run_no_files_written` does not assert the absence of this message, so the false output goes undetected.

**Fix:**

```python
    if dry_run:
        print(f"Dry run complete. Would generate feature: {feature_name} (State: {state_type if state_type else 'None'})")
    else:
        print(f"Generated feature: {feature_name} (State: {state_type if state_type else 'None'})")
```

Update the dry-run tests to assert the new message is absent or correct.

---

### IN-03: Skipped test imports an unresolved symbol without a collection-safe guard

**File:** `tests/test_templates.py:54-59`

**Issue:** The `@pytest.mark.skip` decorated test imports `from fclean import get_provider_templates` inside the test body. The body-level import is only evaluated at execution time, not at collection time, so pytest never raises `ImportError` while the skip is active. This is safe today. However when the skip is eventually removed (Phase 5), if `get_provider_templates` has not been added to `fclean/__init__.py`, the test raises an opaque `ImportError` instead of a clear assertion failure. The skip reason string `"Phase 5: ..."` is in a comment, not in the `reason=` parameter of `pytest.mark.skip`.

**Fix:** Move the reason into `reason=` and guard the import:

```python
@pytest.mark.skip(reason="Phase 5: provider/ChangeNotifier template pending STATE-01")
def test_provider_template_class_names():
    try:
        from fclean import get_provider_templates
    except ImportError:
        pytest.skip("get_provider_templates not yet exported from fclean")
    templates = get_provider_templates("auth")
    all_content = " ".join(templates.values())
    assert "AuthChangeNotifier" in all_content
```

---

_Reviewed: 2026-06-03T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
