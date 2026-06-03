# Roadmap: fclean

**Created:** 2026-06-02
**Goal:** Evolve fclean from a personal script into a properly structured, tested, and distributable Flutter Clean Architecture scaffolding tool.

## Phase Overview

| Phase | Name | Focus | Requirements |
|-------|------|--------|-------------|
| 1 | 3/3 | Complete   | 2026-06-03 |
| 2 | 2/2 | Complete   | 2026-06-03 |
| 3 | Tool Test Suite | pytest coverage for all generators | TEST-01 – TEST-05 |
| 4 | UseCase Scaffolding | Abstract base + concrete stubs | USE-01, USE-02, USE-03 |
| 5 | Extended Scaffolding | Provider + test file generation | STATE-01, STATE-02, TSCF-01 – TSCF-03 |
| 6 | Developer Experience | dry-run, polish, README | DX-01 |

---

## Phase 1: Foundation Fixes

**Goal:** The generated Dart code is syntactically correct and the CLI rejects invalid input.
**Requirements:** CORE-01, CORE-02, CORE-03, DX-02
**Plans:** 3/3 plans complete

**Why first:** The PascalCase bug and lack of validation produce broken generated code. Nothing else can be trusted until these are fixed.

> **Wave order:** All three plans edit `fclean.py`, so they run sequentially (no file-ownership overlap allowed in a wave). Wave 1: 01-01 → Wave 2: 01-02 → Wave 3: 01-03 (01-03 also needs `to_pascal_case` from 01-01).

### Plans

- [x] 01-01-PLAN.md — PascalCase conversion: add `to_pascal_case()`, replace all 10 `.capitalize()` sites (CORE-01) [Wave 1]
- [x] 01-02-PLAN.md — Input validation + DX-02 notice: `validate_name()` before any mkdir, `--state` omission notice (CORE-02, DX-02) [Wave 2]
- [x] 01-03-PLAN.md — Fix Riverpod template: typed `StateNotifierProvider<FeatureNotifier, FeatureState>` stub (CORE-03) [Wave 3]

**Plan 1.1 — PascalCase Conversion**
- Replace all `capitalize()` calls with a `to_pascal_case()` helper that splits on `_` and capitalizes each segment
- Apply to both feature names and entity names
- Covers: CORE-01

**Plan 1.2 — Input Validation + State Omission Notice**
- Add `validate_name(name)` that checks `^[a-z][a-z0-9_]*$` and raises `SystemExit` with a clear message on failure
- Call it for feature name and entity name after split
- Print explicit notice when `--state` is omitted
- Covers: CORE-02, DX-02

**Plan 1.3 — Fix Riverpod Template**
- Replace bare `Provider((ref) => null)` with a typed `StateNotifierProvider<FeatureNotifier, FeatureState>` stub
- Add the accompanying `FeatureNotifier extends StateNotifier<FeatureState>` class
- Covers: CORE-03

### Success Criteria
- `fclean --features user_profile --state bloc` generates `UserProfileBloc`, `UserProfileEvent`, `UserProfileState` (no underscore in class names)
- `fclean --features ../evil` prints a validation error and exits 1
- Riverpod template compiles without type errors in a Flutter project

---

## Phase 2: Restructure & Package

**Goal:** fclean is a proper Python package installable via `pip install .`.
**Requirements:** PKG-01, PKG-02, PKG-03
**Plans:** 2/2 plans complete

**Why second:** Adding more features to a 142-line single file will create maintenance debt. The module structure must be established before new features are layered in.

> **Wave order:** 02-01 creates the `fclean/` package and deletes `fclean.py` (Wave 1). 02-02 adds `pyproject.toml`, installs editably, and updates test imports (Wave 2) — it requires the `fclean.cli:main` entry-point target to exist first, so it cannot run until 02-01 completes.

### Plans

- [x] 02-01-PLAN.md — Module layout: split `fclean.py` into `fclean/` package submodules with re-export `__init__.py`, delete `fclean.py` (PKG-01) [Wave 1]
- [x] 02-02-PLAN.md — pyproject.toml + entry point: hatchling build, `fclean = "fclean.cli:main"`, editable install, remove `sys.path` hacks, regression-verify 12 tests (PKG-02, PKG-03) [Wave 2]

**Plan 2.1 — Module Layout**
- Create `fclean/` package directory with `__init__.py`
- Split `fclean.py` into:
  - `fclean/cli.py` — argparse + `main()` entry point
  - `fclean/generators/feature.py` — `create_feature()` and directory/file logic
  - `fclean/generators/validator.py` — `validate_name()`, `to_pascal_case()`
  - `fclean/templates/bloc.py`, `cubit.py`, `riverpod.py`, `getx.py` — template provider functions
- Delete root `fclean.py` in the same plan (Python prefers the directory; coexistence causes import confusion)
- Covers: PKG-01

**Plan 2.2 — pyproject.toml + Entry Point**
- Add `pyproject.toml` with `[project]`, `requires-python = ">=3.8"`, `[project.scripts] fclean = "fclean.cli:main"`, `[build-system]` using hatchling
- Add `pytest` as `[project.optional-dependencies] dev` (NOT `pytest-tmp-path` — that package does not exist; `tmp_path` is a built-in pytest fixture)
- Verify `pip install -e .` makes `fclean` available on PATH and the 12 existing tests stay green
- Covers: PKG-02, PKG-03

### Success Criteria
- `pip install -e .` succeeds in a clean venv
- `fclean --features auth --state bloc` works identically to before
- All logic is in `fclean/` submodules, `fclean.py` root file is removed

---

## Phase 3: Tool Test Suite

**Goal:** A `pytest` suite validates all generators, templates, and validators.
**Requirements:** TEST-01, TEST-02, TEST-03, TEST-04, TEST-05
**Plans:** 3 plans

**Why third:** Tests must be written against the new module layout (Phase 2) to be maintainable. Adding features in Phases 4–5 without tests would mean shipping untested code.

> **Wave order:** All three plans run in **Wave 1** (parallel). File ownership is disjoint: 03-01 owns `tests/test_utils.py`, 03-02 owns `tests/test_generator.py`, 03-03 owns `fclean/generators/feature.py` + `tests/test_templates.py`. No file overlap → no inter-plan dependency.

> **TEST-05 decision (per 03-RESEARCH.md Pattern 5):** Phase 3 adds a minimal `dry_run` parameter to `create_feature()` only — the `--dry-run` argparse flag remains Phase 6 (DX-01) work. **TEST-03 decision:** only the 4 existing template providers (bloc/cubit/riverpod/getx) are tested; the 5th (provider/ChangeNotifier) is a documented skip stub pending Phase 5 (STATE-01).

### Plans

- [ ] 03-01-PLAN.md — Validator/util edge-case tests: `to_pascal_case()` (multi/trailing underscore, digit segment) + `validate_name()` (hyphen, space, double underscore) in `tests/test_utils.py` (TEST-01, TEST-04) [Wave 1]
- [ ] 03-02-PLAN.md — Generator tests: `create_feature()` cubit/riverpod/getx/None branches + entity path with full file-set assertions in `tests/test_generator.py` (TEST-02) [Wave 1]
- [ ] 03-03-PLAN.md — Template content tests + dry_run: bloc/cubit/getx assertions, 5th-provider skip stub, `dry_run` param on `create_feature()` + dry-run tests in `tests/test_templates.py` (TEST-03, TEST-05) [Wave 1]

### Success Criteria
- `pytest` runs and passes with zero failures
- Coverage includes all template providers and the create_feature path for each state type
- Tests run in < 5 seconds (no Flutter required)

---

## Phase 4: UseCase Scaffolding

**Goal:** Generated features include a `UseCase<Type, Params>` abstract base class and a concrete stub.
**Requirements:** USE-01, USE-02, USE-03
**Plans:** 3 plans

**Why fourth:** This is the most-requested missing feature. The module structure from Phase 2 makes it straightforward to add without touching unrelated code.

### Plans

**Plan 4.1 — UseCase Base Class Template**
- Add `fclean/templates/usecase.py` with a function returning `use_case.dart` content
- Template: `abstract class UseCase<Type, Params> { Future<Type> call(Params params); }`
- Write the file to `lib/features/<name>/domain/usecases/use_case.dart` in `create_feature()`
- Covers: USE-01, USE-03

**Plan 4.2 — Concrete UseCase Stub**
- Add `<feature>_use_case.dart` template stub extending the base class
- Class: `class FeatureUseCase extends UseCase<void, NoParams> { ... }`
- Include a `NoParams` class or reference pattern in the same file
- Write to `lib/features/<name>/domain/usecases/<feature>_use_case.dart`
- Covers: USE-02

**Plan 4.3 — UseCase Tests**
- Extend test suite to cover usecase file generation
- Assert correct class names, correct Dart syntax patterns

### Success Criteria
- `fclean --features auth` generates both `use_case.dart` and `auth_use_case.dart` in `domain/usecases/`
- `AuthUseCase` extends `UseCase<void, NoParams>` in generated code
- New tests pass

---

## Phase 5: Extended Scaffolding

**Goal:** Provider state management is supported, and features generate mirrored test stub files.
**Requirements:** STATE-01, STATE-02, TSCF-01, TSCF-02, TSCF-03
**Plans:** 3 plans

### Plans

**Plan 5.1 — Provider Template**
- Add `fclean/templates/provider.py` with a `ChangeNotifier`-based `*_notifier.dart` stub
- Class accepts a repository in its constructor; stub methods call through to the repository
- Register in the `state_map` dispatch dict
- Covers: STATE-01, STATE-02

**Plan 5.2 — Test File Scaffolding**
- Extend `create_feature()` to also write test stubs under `test/features/<name>/`
- Mirror structure: `data/`, `domain/`, `presentation/` with one stub test file per layer
- Each stub: `import 'package:flutter_test/flutter_test.dart'; void main() { test('todo', () {}); }`
- Respects skip-if-exists rule
- Covers: TSCF-01, TSCF-02, TSCF-03

**Plan 5.3 — Extended Tests**
- Tests for Provider template content
- Tests for test file generation paths and stub contents
- Remove the Phase 3 `@pytest.mark.skip` stub for the provider template (now implemented)

### Success Criteria
- `fclean --features auth --state provider` generates `auth_notifier.dart` with a valid ChangeNotifier class
- `fclean --features auth` generates `test/features/auth/data/`, `domain/`, `presentation/` with stub test files
- All new tests pass

---

## Phase 6: Developer Experience

**Goal:** The tool is polished and documented for open-source users.
**Requirements:** DX-01
**Plans:** 2 plans

### Plans

**Plan 6.1 — Dry-Run Flag**
- Add `--dry-run` flag to argparse in `cli.py`
- Pass flag through to `create_feature()` — the `dry_run` parameter already exists (added in Phase 3 for TEST-05); this plan only wires the argparse flag to it
- Covers: DX-01

**Plan 6.2 — README + Help Text**
- Write a proper `README.md` with installation, usage examples, and `--help` output
- Improve argparse descriptions and epilog
- Show generated directory tree in README

### Success Criteria
- `fclean --features auth --state bloc --dry-run` prints all 15+ expected paths and exits 0 with no files written
- README covers installation, all `--state` options, the `--features name:entity` syntax, and dry-run

---

## Milestone: v1.0 — Distributable fclean

**Complete when:** All 6 phases done, README exists, `pip install .` works, tests pass.

**Next milestone:** PyPI publication + GitHub Actions CI/CD (v2 requirements).

---

*Roadmap created: 2026-06-02*
*Review trigger: after each phase completes*
