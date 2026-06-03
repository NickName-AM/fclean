---
phase: 01-foundation-fixes
plan: 02
subsystem: validation
tags: [python, input-validation, security, path-traversal, dx, pytest]

# Dependency graph
requires:
  - 01-01 (to_pascal_case placement established; sys.path import pattern in tests)
provides:
  - validate_name() at module level in fclean.py
  - _NAME_RE compiled regex at module level in fclean.py
  - import re added to import block
  - Both feature_name and entity_name validated before any mkdir in create_feature()
  - DX-02 explicit notice in main() when --state is omitted
  - validate_name unit tests in tests/test_utils.py
affects:
  - 01-03 (create_feature now validates names; entity names are safe for all downstream templates)
  - All phases where create_feature() is called (names are guaranteed to match ^[a-z][a-z0-9_]*$)

# Tech tracking
tech-stack:
  added: [re (stdlib — already stdlib, now imported)]
  patterns: [guard-then-exit (sys.exit(1) on validation failure), pytest SystemExit assertion with exc_info.value.code check]

key-files:
  created: []
  modified:
    - fclean.py
    - tests/test_utils.py

key-decisions:
  - "validate_name uses re.fullmatch (not re.match) so partial-prefix names like '../evil' cannot slip through"
  - "_NAME_RE compiled once at module level — zero per-call overhead for validation"
  - "DX-02 notice printed once in main() before the feature loop, not inside create_feature(), to avoid one-per-feature repetition"
  - "Validation placed immediately after name parsing (before base_path = Path(...)) per Pitfall 2 in RESEARCH.md"

requirements-completed:
  - CORE-02
  - DX-02

# Metrics
duration: 2min
completed: 2026-06-03
---

# Phase 1 Plan 02: Input Validation and DX-02 Notice Summary

**validate_name() added to fclean.py with regex guard preventing path traversal; DX-02 explicit state-omission notice added to main(); five validate_name unit tests added to test_utils.py**

## Performance

- **Duration:** 2 min
- **Started:** 2026-06-03T02:52:32Z
- **Completed:** 2026-06-03T02:54:08Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added `import re` to the import block (between `import sys` and `import argparse`)
- Added `_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")` at module level, immediately after `to_pascal_case()`
- Added `validate_name(name: str) -> None` that prints to `sys.stderr` and calls `sys.exit(1)` on regex mismatch
- Wired `validate_name(feature_name)` and `validate_name(entity_name)` into `create_feature()` before `base_path = Path(...)` — preventing any filesystem writes on invalid input
- Added `if args.state is None: print("No state management files generated. Pass --state <lib> to scaffold a state layer.")` in `main()`, once per invocation
- Extended `tests/test_utils.py`: added `import pytest`, extended the `from fclean import` line to include `validate_name`, and added 5 validate_name test functions; all 8 tests (3 to_pascal_case + 5 validate_name) pass

## Task Commits

Each task was committed atomically:

1. **Task 1:** Add validate_name, _NAME_RE, and DX-02 notice to fclean.py — `a294314` (feat)
2. **Task 2:** Add validate_name unit tests to tests/test_utils.py — `031a6cf` (test)

## Files Created/Modified

- `fclean.py` — Added `import re`, `_NAME_RE`, `validate_name()`; wired validation into `create_feature()`; added DX-02 notice in `main()`
- `tests/test_utils.py` — Added `import pytest`, extended import, added 5 validate_name test functions

## Decisions Made

- `re.fullmatch` chosen over `re.match` — fullmatch requires the entire string to match, so a name like `../evil` is correctly rejected even without an explicit `$` anchor in the pattern
- `_NAME_RE` compiled at module level (not inside `validate_name`) — no per-call recompilation overhead; consistent with Python idiom for module-level constants
- DX-02 notice placed in `main()` before the feature loop, not inside `create_feature()` — placing it inside `create_feature()` would print once per feature when multiple `--features` args are passed, violating the "once per invocation" requirement

## Deviations from Plan

None - plan executed exactly as written. All acceptance criteria met on first attempt.

## Threat Surface Scan

The validate_name() function is the primary security control for T-01-02 (path traversal via `--features ../evil`) and T-01-02b (code injection via Dart identifier interpolation). Both threats now have active mitigations:

- `validate_name("../evil")` exits 1 with error before any mkdir — no partial directory creation
- `validate_name("User")`, `validate_name("1auth")`, `validate_name("")` all exit 1
- Entity names validated separately — `--features auth:../evil` is blocked

No new security-relevant surface was introduced beyond what is documented in the plan's threat model.

## Known Stubs

None — no placeholder values, hardcoded empty returns, or TODO data sources were introduced in this plan.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `validate_name` is importable at module level for Plan 01-03 and all subsequent plans
- `tests/test_utils.py` now covers both `to_pascal_case` and `validate_name` — ready for Plan 01-03 to add template tests
- `fclean --features ../evil` exits 1 without creating directories — security invariant holds
- `fclean --features auth` (no --state) prints the DX-02 notice once

## Self-Check: PASSED

- fclean.py: FOUND
- tests/test_utils.py: FOUND
- .planning/phases/01-foundation-fixes/01-02-SUMMARY.md: FOUND
- commit a294314 (Task 1): FOUND
- commit 031a6cf (Task 2): FOUND

---
*Phase: 01-foundation-fixes*
*Completed: 2026-06-03*
