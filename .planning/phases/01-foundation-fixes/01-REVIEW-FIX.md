---
phase: 01-foundation-fixes
status: all_fixed
fix_scope: critical_warning
findings_in_scope: 6
fixed: 6
skipped: 0
iteration: 1
files_reviewed_list:
  - fclean.py
  - tests/test_generator.py
  - tests/test_templates.py
  - tests/test_utils.py
---

# Phase 01 Code Review Fix Report

## Summary

All 6 Critical and Warning findings from `01-REVIEW.md` were fixed and committed atomically.

## Fixes Applied

### CR-01 — `path.relative_to(Path.cwd())` crash on re-run
**File:** `fclean.py:159`  
**Commit:** `e01315a`  
**Fix:** Replaced `path.relative_to(Path.cwd())` with `path` directly in the skip message. The path is already relative so no conversion is needed; the `ValueError` crash on every second invocation is eliminated.

### CR-02 — Regex permits trailing/consecutive underscores
**File:** `fclean.py:18`  
**Commit:** `f1a745f`  
**Fix:** Changed `_NAME_RE` from `^[a-z][a-z0-9_]*$` to `^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$`. The new pattern requires non-empty segments between underscores, rejecting `auth_`, `my__feature`, and `_auth`.

### WR-01 — Extra colon segments silently discarded
**File:** `fclean.py:107-108`  
**Commit:** `bca605c`  
**Fix:** Added `len(parts) > 2` guard after `feature_arg.split(":")`. Extra segments now cause a clear stderr error and `exit 1` instead of silent discard.

### WR-02 — `write_text()` without explicit encoding
**File:** `fclean.py:162`  
**Commit:** `5d4a63d`  
**Fix:** Added `encoding="utf-8"` to `path.write_text(content)` for portable behavior on Windows.

### WR-03 — Unknown `state_type` silently ignored
**File:** `fclean.py:152-155`  
**Commit:** `a610480`  
**Fix:** Added `state_type is not None and state_type not in state_map` guard before the dispatch block. Unknown state types now `exit 1` with a message listing valid choices.

### WR-04 — `create_feature` untested (filesystem path)
**File:** `tests/test_generator.py`  
**Commit:** `a5de72a`  
**Fix:** Added two integration tests (`test_create_feature_creates_expected_files`, `test_create_feature_skip_existing_does_not_crash`) using `tmp_path` + `monkeypatch.chdir`. All 12 tests pass.
