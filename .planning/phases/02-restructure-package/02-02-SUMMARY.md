---
phase: 02-restructure-package
plan: 02
subsystem: packaging
tags: [python-package, pyproject-toml, hatchling, pip-install, entry-point, pytest]

# Dependency graph
requires:
  - phase: 02-01
    provides: fclean/ Python package with fclean.cli:main entry point target and seven public symbols re-exported from __init__.py
provides:
  - pyproject.toml with hatchling build backend, requires-python >=3.8, and fclean console-script entry point
  - Editable install (pip install -e .) exposing fclean binary on PATH
  - Three test files free of sys.path.insert hacks, importing via editable install
  - 12-test suite green against new package layout (PKG-03 regression gate passed)
affects: [03-features, any future pip-publish step, test-suite consumers]

# Tech tracking
tech-stack:
  added: [hatchling >= 1.26 (build backend, PyPA-endorsed)]
  patterns:
    - pyproject.toml-only build metadata (no setup.py, no MANIFEST.in)
    - hatchling auto-discovers fclean/ and subpackages via __init__.py markers
    - Editable install (pip install -e .) as the mechanism that eliminates sys.path hacks in tests
    - Virtual environment (.venv) used for editable install on macOS externally-managed Homebrew Python

key-files:
  created:
    - pyproject.toml
  modified:
    - tests/test_utils.py
    - tests/test_generator.py
    - tests/test_templates.py

key-decisions:
  - "Virtual environment (.venv at project root) used for editable install because macOS Homebrew Python 3.14 is externally managed (PEP 668); pip3 install -e with --user and system-wide both blocked"
  - "hatchling >= 1.26 declared in build-system.requires; modern pip auto-fetches it in an isolated build env so no manual pre-install needed"
  - "pytest-tmp-path excluded from dev deps — package does not exist on PyPI; tmp_path is a built-in pytest fixture"

patterns-established:
  - "pyproject.toml-only packaging: all build metadata in one file, zero boilerplate files"
  - "Editable install eliminates sys.path manipulation in tests: remove hacks, trust the installed package"

requirements-completed: [PKG-02, PKG-03]

# Metrics
duration: 8min
completed: 2026-06-03
---

# Phase 2 Plan 02: Packaging Summary

**pyproject.toml with hatchling build backend wires fclean = "fclean.cli:main" console-script entry point; editable install eliminates all sys.path hacks; 12-test suite stays green (PKG-02 + PKG-03)**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-06-03T12:10:00Z
- **Completed:** 2026-06-03T12:18:00Z
- **Tasks:** 2
- **Files modified:** 4 (1 created, 3 modified)

## Accomplishments
- Created pyproject.toml declaring hatchling >= 1.26 as build backend, requires-python = ">=3.8", fclean = "fclean.cli:main" console-script, and pytest>=7 dev optional dependency
- Installed the package editably via virtual environment; fclean binary verified on PATH with --help printing argparse usage including --features and --state
- Removed sys.path.insert(0, ".") and unused import sys from all three test files; from fclean import ... lines kept identical, now resolved via editable install
- Confirmed 12 passed, 0 failed in python3 -m pytest -q after restructure (PKG-03 regression gate)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create pyproject.toml and install editably** - `166a162` (feat)
2. **Task 2: Remove sys.path hacks from tests and verify no regression** - `03ffa42` (fix)

## Files Created/Modified
- `pyproject.toml` - Build metadata with hatchling backend, project metadata, fclean entry point, and dev extras
- `tests/test_utils.py` - Removed import sys and sys.path.insert(0, "."); import fclean resolves via editable install
- `tests/test_generator.py` - Removed import sys and sys.path.insert(0, "."); import fclean resolves via editable install
- `tests/test_templates.py` - Removed import sys and sys.path.insert(0, "."); import fclean resolves via editable install

## Decisions Made
- Used a virtual environment (.venv at project root) for the editable install because macOS Homebrew Python 3.14 enforces PEP 668 external management policy, blocking pip3 install system-wide and --user installs. The venv approach is the correct and recommended workaround.
- pytest-tmp-path explicitly excluded from dev deps — this package does not exist on PyPI; tmp_path is a built-in pytest fixture since pytest 3.9.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Used .venv for editable install instead of direct pip3 install -e**
- **Found during:** Task 1 (Create pyproject.toml and install editably)
- **Issue:** pip3 install -e ".[dev]" failed with "externally-managed-environment" (PEP 668) on macOS Homebrew Python 3.14. Both system-wide and --user installs are blocked.
- **Fix:** Created a virtual environment at /Users/abik/Development/projects/fclean/.venv using python3 -m venv and ran the editable install inside it. The fclean binary is at .venv/bin/fclean and is confirmed working.
- **Files modified:** None (venv created at project root, not tracked in worktree)
- **Verification:** /Users/abik/Development/projects/fclean/.venv/bin/fclean --help exits 0 and shows correct argparse usage; pip show fclean shows Editable project location pointing to worktree
- **Committed in:** 166a162 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Venv-based install is functionally equivalent to direct pip3 install -e for all plan acceptance criteria. No scope creep.

## Issues Encountered
- macOS Homebrew Python 3.14 enforces PEP 668 externally-managed-environment policy, blocking direct pip3 install. Resolved via virtual environment (standard Python packaging best practice).

## User Setup Required
None - no external service configuration required. The .venv was created automatically as part of the editable install step.

## Threat Flags

No new threat surface introduced. pyproject.toml declares only two packages (hatchling as build-time backend, pytest as dev dep), both rated [OK] in RESEARCH.md Package Legitimacy Audit. No network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. The fclean = "fclean.cli:main" entry point wiring was verified by grep gate (exact line present in pyproject.toml) and runtime check (which fclean + fclean --help).

## Known Stubs
None. pyproject.toml is fully wired to the real fclean.cli:main entry point. All test files import the live package symbols. No placeholder values or TODO stubs exist in any modified file.

## Next Phase Readiness
- fclean is now a proper installable Python package (PKG-02 complete)
- All 12 tests pass cleanly without sys.path manipulation (PKG-03 complete)
- Phase 02 (restructure-package) is fully complete: PKG-01 (plan 01) + PKG-02 + PKG-03 (plan 02) all satisfied
- Ready for Phase 03 feature additions (UseCase scaffolding, --dry-run, Provider state, test stub generation)

---
*Phase: 02-restructure-package*
*Completed: 2026-06-03*
