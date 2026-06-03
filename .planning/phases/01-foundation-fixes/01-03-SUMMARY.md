---
phase: 01-foundation-fixes
plan: 03
subsystem: testing
tags: [python, pytest, riverpod, dart, flutter, state-management, clean-architecture, tdd]

# Dependency graph
requires:
  - 01-01 (to_pascal_case at module level in fclean.py — used by rewritten get_riverpod_templates)
  - 01-02 (validate_name wired into create_feature — names safe before get_riverpod_templates is called)
provides:
  - get_riverpod_templates rewritten to emit typed StateNotifierProvider<Notifier, State> stub
  - FeatureState class and FeatureNotifier extends StateNotifier<FeatureState> in generated Dart
  - Class names are PascalCase via to_pascal_case (UserProfileNotifier, UserProfileState)
  - tests/test_templates.py with test_riverpod_typed locking the CORE-03 fix
affects:
  - All later phases that call get_riverpod_templates or --state riverpod

# Tech tracking
tech-stack:
  added: []
  patterns: [TDD RED/GREEN (test commit then feat commit), typed Riverpod StateNotifierProvider pattern]

key-files:
  created:
    - tests/test_templates.py
  modified:
    - fclean.py

key-decisions:
  - "get_riverpod_templates follows get_bloc_templates convention: name = to_pascal_case(feature) as first line"
  - "Provider variable name kept as snake_case {feature}Provider (deferred cosmetic per RESEARCH.md Pitfall 5 and Open Question 2 — prefer_lower_camel_case lint is out of scope for CORE-03)"
  - "tests/test_templates.py created in TDD RED phase (commit c5b68fb) — test_templates.py file satisfies both Task 1 RED gate and Task 2 deliverable"

patterns-established:
  - "Riverpod template pattern: FeatureState class + FeatureNotifier extends StateNotifier<FeatureState> + StateNotifierProvider<Notifier, State>"
  - "TDD RED commit (test) then GREEN commit (feat) per task — test file created before implementation"

requirements-completed:
  - CORE-03

# Metrics
duration: 3min
completed: 2026-06-03
---

# Phase 1 Plan 03: Riverpod Template Fix Summary

**get_riverpod_templates rewritten from bare `Provider((ref) => null)` to typed `StateNotifierProvider<UserProfileNotifier, UserProfileState>` with companion State and Notifier classes, locked by a passing pytest assertion**

## Performance

- **Duration:** 3 min
- **Started:** 2026-06-03T03:00:00Z
- **Completed:** 2026-06-03T03:03:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Rewrote `get_riverpod_templates(feature)` in fclean.py: sets `name = to_pascal_case(feature)`, emits `{name}State {}`, `{name}Notifier extends StateNotifier<{name}State>` with constructor, and `StateNotifierProvider<{name}Notifier, {name}State>((ref) { return {name}Notifier(); })`
- Removed the untyped `Provider((ref) => null)` form — `grep -c 'Provider((ref) => null)' fclean.py` returns 0
- Created `tests/test_templates.py` with `test_riverpod_typed` asserting all four behavioral conditions; all 10 tests across the full test suite pass

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED):** Add failing test for typed Riverpod StateNotifierProvider stub - `c5b68fb` (test)
2. **Task 1 (GREEN):** Rewrite get_riverpod_templates to emit typed StateNotifierProvider stub - `7904e0f` (feat)

_Note: Task 2 (tests/test_templates.py) was created in the TDD RED phase (c5b68fb) — both tasks' acceptance criteria are satisfied by these two commits._

## Files Created/Modified

- `fclean.py` — `get_riverpod_templates` rewritten: added `name = to_pascal_case(feature)`, replaced single untyped provider line with 8-line Dart stub containing State/Notifier classes and StateNotifierProvider
- `tests/test_templates.py` — Created with `sys.path.insert(0, ".")` import header, NOTE comment for Phase 2 restructure, `test_riverpod_typed` function asserting typed stub and absence of old form

## Decisions Made

- `to_pascal_case(feature)` used for all Dart class names (UserProfileState, UserProfileNotifier) — consistent with get_bloc_templates and get_cubit_templates convention
- Provider variable name stays `{feature}Provider` (snake_case) — the `prefer_lower_camel_case` Dart lint is a cosmetic concern explicitly deferred in RESEARCH.md Pitfall 5 and Open Question 2; it compiles and works correctly
- tests/test_templates.py created in the TDD RED phase as the test-first commit, satisfying both the TDD gate requirement and Task 2's deliverable in a single commit

## Deviations from Plan

None — plan executed exactly as written. TDD RED/GREEN protocol followed. All acceptance criteria met on first attempt.

## Threat Surface Scan

No new security-relevant surface introduced. The feature name is validated upstream by `validate_name()` (plan 01-02) before any template function is called. The template adds no new untrusted input paths. Consistent with T-01-03 disposition in plan threat model.

## Known Stubs

None — no placeholder values, hardcoded empty returns, or TODO data sources were introduced in this plan. (The `// TODO: implement event handler` line in `get_bloc_templates` is a pre-existing intentional developer prompt in the generated Dart output, not introduced by this plan.)

## TDD Gate Compliance

- RED gate: `test(01-03)` commit `c5b68fb` — PRESENT
- GREEN gate: `feat(01-03)` commit `7904e0f` — PRESENT (after RED)
- REFACTOR gate: Not needed — implementation was clean on first pass

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All three CORE requirements (CORE-01, CORE-02, CORE-03) are now fixed and test-locked
- `--state riverpod` generates a compilable typed Riverpod file instead of `Provider<Null>`
- Full test suite: 10 tests pass across test_utils.py, test_generator.py, test_templates.py
- Phase 1 foundation-fixes complete — ready for Phase 2 (package restructure)

---
*Phase: 01-foundation-fixes*
*Completed: 2026-06-03*
