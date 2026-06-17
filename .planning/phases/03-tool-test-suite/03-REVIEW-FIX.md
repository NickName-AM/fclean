---
phase: 03-tool-test-suite
fixed_at: 2026-06-17T15:54:00Z
review_path: .planning/phases/03-tool-test-suite/03-REVIEW.md
iteration: 1
findings_in_scope: 6
fixed: 6
skipped: 0
status: all_fixed
---

# Phase 03: Code Review Fix Report

**Fixed at:** 2026-06-17T15:54:00Z
**Source review:** .planning/phases/03-tool-test-suite/03-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 6
- Fixed: 6
- Skipped: 0

## Fixed Issues

### WR-01: `to_pascal_case` uses `str.capitalize()` which silently lowercases non-initial characters

**Files modified:** `fclean/generators/validator.py`
**Commit:** c60f605
**Applied fix:** Replaced `word.capitalize()` with `word[:1].upper() + word[1:]` and added `if word` guard to filter empty segments from split. This preserves non-initial uppercase/digit characters and makes trailing-underscore behaviour explicit.

---

### WR-02: Three `validate_name` failure tests never assert exit code

**Files modified:** `tests/test_utils.py`
**Commit:** 64642b0
**Applied fix:** Added `as exc_info` capture and `assert exc_info.value.code == 1` to `test_validate_name_uppercase_exits`, `test_validate_name_leading_digit_exits`, and `test_validate_name_empty_exits`. Now consistent with the other three error tests in the same file.

---

### WR-03: `test_create_feature_creates_expected_files` asserts only 2 of 7+ files for `bloc` mode

**Files modified:** `tests/test_generator.py`
**Commit:** a97e2f7
**Applied fix:** Expanded the bloc integration test to assert all 7 expected files: `auth_remote_datasource.dart`, `auth_local_datasource.dart`, `auth_repository_impl.dart`, `auth_repository.dart`, `auth_event.dart`, `auth_state.dart`, and `auth_bloc.dart`. Now aligned with cubit, riverpod, and getx integration tests.

---

### WR-04: No test covers the invalid `state_type` exit path in `create_feature`

**Files modified:** `tests/test_generator.py`
**Commit:** b848b8b
**Applied fix:** Added `test_create_feature_invalid_state_type_exits` that calls `create_feature("auth", "redux")` and asserts `SystemExit` with `code == 1`, covering the guard at `feature.py:70-76`.

---

### WR-05: `test_riverpod_typed` accesses template content by positional index instead of explicit key

**Files modified:** `tests/test_templates.py`
**Commit:** 3387c9d
**Applied fix:** Replaced `content = list(templates.values())[0]` with `content = templates["presentation/providers/user_profile_provider.dart"]`. The key is now explicit and robust against future additions to the template dict.

---

### WR-06: `print("Generated feature: ...")` fires unconditionally during dry runs, producing misleading output

**Files modified:** `fclean/generators/feature.py`
**Commit:** 75afe30
**Applied fix:** Replaced the single unconditional `print(f"Generated feature: ...")` at line 93 with a conditional: dry runs print `"Dry run: would generate feature '...' (State: ...)"` and real runs print `"Generated feature: ... (State: ...)"`. Existing dry-run tests are unaffected as they only assert on dart filename strings.

---

_Fixed: 2026-06-17T15:54:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
