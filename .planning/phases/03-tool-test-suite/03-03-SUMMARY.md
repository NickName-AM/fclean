---
phase: 03-tool-test-suite
plan: "03"
subsystem: tests/generators
tags: [tests, dry-run, templates, tdd]
dependency_graph:
  requires: []
  provides: [TEST-03, TEST-05]
  affects: [fclean/generators/feature.py, tests/test_templates.py]
tech_stack:
  added: []
  patterns: [capsys+tmp_path+monkeypatch dry-run testing, substring-in template assertions, pytest.mark.skip stub]
key_files:
  created: []
  modified:
    - fclean/generators/feature.py
    - tests/test_templates.py
    - pyproject.toml
decisions:
  - "dry_run added as a parameter (not a CLI flag) — --dry-run flag is Phase 6 (DX-01) scope"
  - "sub_dirs mkdir loop guarded with if not dry_run: to prevent lib/ creation in dry-run mode"
  - "pythonpath=['.'] added to [tool.pytest.ini_options] so pytest resolves fclean from the worktree source rather than the editable install pointing to the main project branch"
  - "5th provider template documented as a skip stub pending Phase 5 STATE-01"
metrics:
  duration: "~20 minutes"
  completed: "2026-06-03T16:53:57Z"
  tasks_completed: 3
  files_modified: 3
---

# Phase 03 Plan 03: Template Tests and dry_run Parameter Summary

Closed TEST-03 and TEST-05. Added `dry_run=False` parameter to `create_feature()` that prints intended file paths and writes nothing when `True`. Extended `tests/test_templates.py` with bloc/cubit/getx template content tests (TEST-03), a skip stub for the 5th provider template pending Phase 5, and two dry-run tests proving zero filesystem writes and correct path output (TEST-05). Full suite: 19 passed, 1 skipped, 0 failed.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add dry_run parameter to create_feature | a0e1b7d | fclean/generators/feature.py |
| 2 | Add bloc/cubit/getx template content tests (TEST-03) | 68df3d9 | tests/test_templates.py |
| 3 | Add dry_run tests (TEST-05) | 0003f9d | tests/test_templates.py, pyproject.toml |

## What Was Built

**`fclean/generators/feature.py`** — `create_feature(feature_arg, state_type, dry_run=False)`:
- Signature extended with `dry_run=False`; existing callers (cli.py, all tests) unaffected
- `sub_dirs` mkdir loop guarded with `if not dry_run:` — prevents `lib/` creation in dry-run
- Write loop first branch: when `dry_run` is `True`, prints `path` and `continue`s — no directory creation, no file write

**`tests/test_templates.py`** — 7 active tests, 1 skip stub:
- `test_bloc_template_class_names`: joined values contain UserProfileBloc/Event/State
- `test_bloc_template_bloc_file_content`: flutter_bloc import + class AuthBloc declaration present
- `test_cubit_template_class_names`: joined values contain UserProfileCubit/State
- `test_cubit_template_keys`: cubit.dart and state.dart keys present
- `test_getx_template_keys`: controller and bindings keys present
- `test_provider_template_class_names`: `@pytest.mark.skip` — Phase 5 pending
- `test_dry_run_no_files_written`: lib/ absent, auth_bloc.dart in stdout
- `test_dry_run_prints_all_expected_paths`: repository/datasource/bloc paths in stdout

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] pytest could not resolve fclean from worktree source**
- **Found during:** Task 3 (dry_run tests)
- **Issue:** The editable install pth file points to `/Users/abik/Development/projects/fclean` (main branch), not the worktree. When pytest ran in the worktree directory, it imported `create_feature` from the main project's `feature.py` which still had the old signature. Tests failed with `TypeError: create_feature() got an unexpected keyword argument 'dry_run'`.
- **Fix:** Added `[tool.pytest.ini_options] pythonpath = ["."]` to worktree's `pyproject.toml`. This prepends the worktree root to sys.path, ensuring `fclean` is resolved from the worktree source — the standard pytest pattern for this scenario (supported since pytest 7.0, worktree uses 9.0.3).
- **Files modified:** `pyproject.toml`
- **Commit:** 0003f9d

## Verification

- `.venv/bin/pytest -q`: 19 passed, 1 skipped, 0 failed
- `git status --porcelain lib/`: empty (no repo-root leakage)
- `inspect.signature(create_feature)` contains `dry_run` parameter
- Test counts: 5 active (bloc x2, cubit x2, getx x1) + 1 skip + 2 dry_run = 7 active + 1 skipped (matches plan target)

## Threat Model Compliance

All T-03-03 and T-03-04 mitigations verified:
- `dry_run=False` default preserves existing non-dry-run write path unchanged
- `not (tmp_path / "lib").exists()` assertion passes — lib/ never created in dry-run
- `git status --porcelain lib/` is empty — no repo-root leakage
- No new packages installed (T-03-SC accept disposition confirmed)

## Self-Check: PASSED

- fclean/generators/feature.py: FOUND
- tests/test_templates.py: FOUND
- pyproject.toml (updated): FOUND
- Commits: a0e1b7d, 68df3d9, 0003f9d all exist in git log
