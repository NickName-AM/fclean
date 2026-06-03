---
phase: 02-restructure-package
plan: 01
subsystem: packaging
tags: [python-package, module-restructure, submodules, hatchling]

# Dependency graph
requires:
  - phase: 01-foundation-fixes
    provides: Corrected to_pascal_case(), validate_name(), encoding="utf-8" bug fix, WR-01/WR-03 guards
provides:
  - fclean/ Python package with generators/ and templates/ subpackages
  - fclean/__init__.py re-export layer exposing seven public symbols
  - fclean/cli.py as fclean.cli:main entry point for pyproject.toml [project.scripts]
  - fclean/generators/validator.py with to_pascal_case() and validate_name()
  - fclean/generators/feature.py with create_feature() and is_flutter_project()
  - fclean/templates/bloc.py, cubit.py, riverpod.py, getx.py with get_*_templates()
  - Root fclean.py deleted
affects: [02-02-PLAN, pyproject-packaging, test-suite]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Direct submodule imports inside fclean/ (never 'from fclean import' to prevent circular imports)
    - Zero-byte __init__.py markers for hatchling auto-discovery of subpackages
    - Leaf-first dependency graph layout (validator -> templates -> feature -> cli -> __init__)

key-files:
  created:
    - fclean/__init__.py
    - fclean/cli.py
    - fclean/generators/__init__.py
    - fclean/generators/validator.py
    - fclean/generators/feature.py
    - fclean/templates/__init__.py
    - fclean/templates/bloc.py
    - fclean/templates/cubit.py
    - fclean/templates/riverpod.py
    - fclean/templates/getx.py
  modified:
    - fclean.py (deleted)

key-decisions:
  - "Leaf-first creation order: validator and templates before feature.py to avoid forward-reference errors during import"
  - "Direct submodule import discipline enforced: from fclean.generators.validator import ..., never from fclean import ... inside the package (prevents circular import via partially-initialized __init__.py)"
  - "Zero-byte __init__.py markers for generators/ and templates/ required for hatchling auto-discovery to include both subdirectories in the wheel"

patterns-established:
  - "Import discipline: all intra-package imports use full submodule paths (from fclean.generators.validator import X), never short package paths (from fclean import X)"
  - "Public API surface: fclean/__init__.py re-exports seven symbols via __all__ for backward compat with existing test imports"

requirements-completed: [PKG-01]

# Metrics
duration: 10min
completed: 2026-06-03
---

# Phase 2 Plan 01: Restructure Package Summary

**199-line fclean.py split into a proper Python package with generators/ and templates/ subpackages, direct-submodule import discipline enforced, and fclean/__init__.py re-exporting all seven public symbols**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-06-03T12:00:00Z
- **Completed:** 2026-06-03T12:09:34Z
- **Tasks:** 2
- **Files modified:** 11 (10 created, 1 deleted)

## Accomplishments
- Created fclean/ package with generators/ and templates/ subpackages, each with zero-byte __init__.py markers for hatchling auto-discovery
- Extracted to_pascal_case(), validate_name(), and _NAME_RE verbatim into fclean/generators/validator.py (leaf of dependency graph, no intra-package imports)
- Extracted get_bloc_templates(), get_cubit_templates(), get_riverpod_templates(), get_getx_templates() into dedicated template modules each importing to_pascal_case via direct submodule path
- Extracted is_flutter_project() and create_feature() into fclean/generators/feature.py with all prior bug fixes (encoding="utf-8", WR-01 single-colon guard, WR-03 unknown-state guard) intact
- Created fclean/cli.py with main() as the fclean.cli:main entry point
- Created fclean/__init__.py exposing all seven public symbols via __all__ using direct submodule import paths
- Deleted fclean.py so the package directory is the sole fclean resolution target

## Task Commits

Each task was committed atomically:

1. **Task 1: Create leaf submodules — validator and four template providers** - `2b8b6f2` (feat)
2. **Task 2: Create feature.py, cli.py, __init__.py and delete fclean.py** - `39c72ff` (feat)

## Files Created/Modified
- `fclean/__init__.py` - Public API re-export layer with __all__ listing seven symbols
- `fclean/cli.py` - argparse main() entry point for fclean.cli:main script target
- `fclean/generators/__init__.py` - Zero-byte subpackage marker for hatchling discovery
- `fclean/generators/validator.py` - to_pascal_case(), _NAME_RE, validate_name() (leaf; no intra-package imports)
- `fclean/generators/feature.py` - is_flutter_project(), create_feature() with all prior bug fixes
- `fclean/templates/__init__.py` - Zero-byte subpackage marker for hatchling discovery
- `fclean/templates/bloc.py` - get_bloc_templates() with direct submodule import
- `fclean/templates/cubit.py` - get_cubit_templates() with direct submodule import
- `fclean/templates/riverpod.py` - get_riverpod_templates() with direct submodule import
- `fclean/templates/getx.py` - get_getx_templates() with direct submodule import
- `fclean.py` - Deleted (package directory is now sole resolution target)

## Decisions Made
- Leaf-first creation order (validator -> templates -> feature -> cli -> __init__) avoids forward-reference errors during staged creation
- Direct submodule import discipline: all imports inside fclean/ use full paths (from fclean.generators.validator import ...) to prevent circular imports through the partially-initialized __init__.py
- Zero-byte __init__.py markers (not namespace packages) required so hatchling includes both subdirectories in the wheel

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Threat Flags

No new threat surface introduced. This plan is a pure Python packaging restructure — no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. The circular-import mitigation (T-02-02) was enforced via direct-submodule import discipline and verified by grep gate (grep -r "from fclean import" fclean/ returns empty).

## Known Stubs
None. All seven public symbols are fully implemented and produce correct Dart output. No placeholder values, hardcoded empty returns, or TODO stubs exist in the created files.

## Next Phase Readiness
- fclean/ package structure is ready for Plan 02-02 (pyproject.toml packaging with hatchling)
- Import paths for [project.scripts] entry point: fclean.cli:main is implemented in fclean/cli.py
- All seven public symbols importable via both fclean.* submodule paths and from fclean import ...

---
*Phase: 02-restructure-package*
*Completed: 2026-06-03*
