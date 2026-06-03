---
phase: 01-foundation-fixes
plan: 01
subsystem: testing
tags: [python, pytest, snake_case, pascal_case, dart, clean-architecture]

# Dependency graph
requires: []
provides:
  - to_pascal_case helper function at module level in fclean.py
  - All 10 class-name construction sites use to_pascal_case instead of str.capitalize()
  - tests/test_utils.py with to_pascal_case unit tests
  - tests/test_generator.py with BLoC class-name end-to-end assertion
affects:
  - 01-02 (validate_name tests import from same fclean module; sys.path pattern established)
  - 01-03 (get_riverpod_templates will call to_pascal_case)
  - all later phases that generate Dart class names

# Tech tracking
tech-stack:
  added: [pytest (dev dependency)]
  patterns: [TDD RED/GREEN/REFACTOR, sys.path.insert(0,".") for script imports in tests]

key-files:
  created:
    - tests/test_utils.py
    - tests/test_generator.py
    - .gitignore
  modified:
    - fclean.py

key-decisions:
  - "to_pascal_case implemented as split-on-underscore + capitalize each segment — pure stdlib, zero deps"
  - "tests use sys.path.insert(0, '.') with a NOTE comment flagging the import change required after Phase 2 restructure"
  - "to_pascal_case placed at module level before is_flutter_project() — consistent with existing helper placement convention"

patterns-established:
  - "Module-level string utility helpers before template functions in fclean.py"
  - "Test files import via sys.path.insert(0, '.') for Phase 1 script-mode"
  - "TDD RED commit (test) then GREEN commit (feat) per-task"

requirements-completed:
  - CORE-01

# Metrics
duration: 3min
completed: 2026-06-03
---

# Phase 1 Plan 01: PascalCase Fix Summary

**to_pascal_case helper added to fclean.py replacing str.capitalize() at all 10 Dart class-name construction sites, with pytest test scaffolds locking the fix**

## Performance

- **Duration:** 3 min
- **Started:** 2026-06-03T02:47:58Z
- **Completed:** 2026-06-03T02:50:42Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added `to_pascal_case(name: str) -> str` at module level in fclean.py that splits on `_` and capitalizes each segment, correctly converting `user_profile` -> `UserProfile`
- Replaced all 10 `.capitalize()` class-name construction sites in get_bloc_templates, get_cubit_templates, get_getx_templates, and create_feature
- Created tests/test_utils.py and tests/test_generator.py; all 4 tests pass with `python3 -m pytest tests/test_utils.py tests/test_generator.py -x -q`

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED):** Add failing tests for to_pascal_case and BLoC class names - `463621a` (test)
2. **Task 1 (GREEN):** Add to_pascal_case helper and replace all capitalize() sites - `2e79307` (feat)
3. **Task 2:** Test files committed as part of RED phase above - covered by `463621a`

**Additional:** `.gitignore` for Python cache artifacts - `faf8f31` (chore)

_Note: TDD tasks have multiple commits (test RED -> feat GREEN). Task 2 test files were created in the RED phase commit._

## Files Created/Modified

- `fclean.py` - Added to_pascal_case helper; replaced 10 .capitalize() call sites in template functions and create_feature
- `tests/test_utils.py` - Unit tests for to_pascal_case (single word, snake_case, digit suffix)
- `tests/test_generator.py` - End-to-end assertion that get_bloc_templates("user_profile") produces UserProfileBloc/Event/State
- `.gitignore` - Ignores __pycache__ and .pytest_cache directories

## Decisions Made

- `to_pascal_case` uses `"".join(word.capitalize() for word in name.split("_"))` — stdlib-only, no `re` needed for this helper (the `import re` shown in PATTERNS.md is for plan 01-02's `validate_name`; not added here since it is not needed by this plan's scope)
- The single remaining `.capitalize()` call inside `to_pascal_case`'s own implementation body is intentional and does not violate the "zero class-name sites use .capitalize() directly" invariant

## Deviations from Plan

None — plan executed exactly as written. The plan's verification command `grep -c '\.capitalize()' fclean.py | grep -qx 0` technically fails due to the `word.capitalize()` inside `to_pascal_case`'s own body, but this is the implementation the plan itself specifies. All behavioral acceptance criteria pass.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `to_pascal_case` is available at module level for all subsequent plans to import
- Test infrastructure (pytest, sys.path pattern) is established for plans 01-02 and 01-03
- Plan 01-02 (validate_name) can add its tests to tests/test_utils.py following the same import pattern

---
*Phase: 01-foundation-fixes*
*Completed: 2026-06-03*
