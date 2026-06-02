# Requirements: fclean

**Defined:** 2026-06-02
**Core Value:** One command that generates a complete, correct Flutter Clean Architecture feature skeleton so developers never hand-write boilerplate again.

## v1 Requirements

### Bug Fixes (CORE)

- [ ] **CORE-01**: `fclean --features user_profile` generates `UserProfile` (not `User_profile`) in all Dart class names
- [ ] **CORE-02**: Feature and entity names are validated against `^[a-z][a-z0-9_]*$` — invalid names print a clear error and exit without writing files
- [ ] **CORE-03**: Riverpod template generates a typed `StateNotifierProvider<FeatureNotifier, FeatureState>` stub instead of `Provider((ref) => null)`

### Packaging & Structure (PKG)

- [ ] **PKG-01**: Project restructured from single-file `fclean.py` into a proper Python package layout (`fclean/cli.py`, `fclean/generators/`, `fclean/templates/`)
- [ ] **PKG-02**: `pyproject.toml` added with metadata, `requires-python = ">=3.8"`, and a `[project.scripts]` entry so `pip install .` makes `fclean` available as a CLI command
- [ ] **PKG-03**: `fclean --features auth --state bloc` works identically after restructure (no regression)

### Tool Test Suite (TEST)

- [ ] **TEST-01**: `pytest` test suite covers `to_pascal_case()` for single words, snake_case, and edge cases
- [ ] **TEST-02**: Tests cover `create_feature()` — verify the correct set of files is created in a temp directory for each `--state` option
- [ ] **TEST-03**: Tests cover all 5 template providers — verify generated Dart file contents match expected templates
- [ ] **TEST-04**: Tests cover input validation — invalid names raise errors, valid names pass
- [ ] **TEST-05**: Tests cover the `--dry-run` flag — no files written, expected paths printed

### UseCase Scaffolding (USE)

- [ ] **USE-01**: Running `fclean --features auth` generates `lib/features/auth/domain/usecases/use_case.dart` containing an abstract `UseCase<Type, Params>` base class
- [ ] **USE-02**: Running `fclean --features auth` generates `lib/features/auth/domain/usecases/auth_use_case.dart` containing a concrete stub class `AuthUseCase extends UseCase<...>`
- [ ] **USE-03**: UseCase base class uses a `call()` method (idiomatic Dart callable class pattern) returning `Future<Type>`

### State Management (STATE)

- [ ] **STATE-01**: `--state provider` generates a `ChangeNotifier`-based `*_notifier.dart` with a constructor that accepts a repository and stub `void` methods
- [ ] **STATE-02**: `--state provider` is listed in `--help` output alongside bloc/cubit/riverpod/getx

### Test Scaffolding (TSCF)

- [ ] **TSCF-01**: Running `fclean --features auth` generates mirrored test stub files under `test/features/auth/` for data, domain, and presentation layers
- [ ] **TSCF-02**: Generated test stubs import `package:flutter_test/flutter_test.dart` and contain a minimal `main()` with a placeholder `test()` call
- [ ] **TSCF-03**: Test scaffolding respects the same skip-if-exists rule as production scaffolding

### Developer Experience (DX)

- [ ] **DX-01**: `fclean --features auth --state bloc --dry-run` prints all paths that would be created without writing any files
- [ ] **DX-02**: When `--state` is omitted, fclean prints an explicit notice: `No state management files generated. Pass --state <lib> to scaffold a state layer.`

## v2 Requirements

### Distribution

- **DIST-01**: Package published to PyPI so `pip install fclean` works globally
- **DIST-02**: GitHub Actions CI runs tests on push and publishes on tag

### Customization

- **CFG-01**: `fclean.yaml` config file in the Flutter project root allows setting a default `--state` and custom output paths
- **CFG-02**: Users can override individual template files by placing `.fclean/templates/` in the Flutter project root

### Additional State Management

- **STATE-03**: `--state signals` generates a Signals-based notifier (if signals package gains adoption)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Non-Flutter project support | Tool is intentionally Flutter-specific |
| GUI or TUI interface | CLI is the right model for a code generator |
| Project initialization (flutter create) | fclean scaffolds features, not full projects |
| Plugin/extension system | Over-engineered for current scope; config file in v2 is sufficient |
| Interactive prompt mode | Adds complexity; flags are discoverable via --help |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CORE-01 | Phase 1 | Pending |
| CORE-02 | Phase 1 | Pending |
| CORE-03 | Phase 1 | Pending |
| PKG-01 | Phase 2 | Pending |
| PKG-02 | Phase 2 | Pending |
| PKG-03 | Phase 2 | Pending |
| TEST-01 | Phase 3 | Pending |
| TEST-02 | Phase 3 | Pending |
| TEST-03 | Phase 3 | Pending |
| TEST-04 | Phase 3 | Pending |
| TEST-05 | Phase 3 | Pending |
| USE-01 | Phase 4 | Pending |
| USE-02 | Phase 4 | Pending |
| USE-03 | Phase 4 | Pending |
| STATE-01 | Phase 5 | Pending |
| STATE-02 | Phase 5 | Pending |
| TSCF-01 | Phase 5 | Pending |
| TSCF-02 | Phase 5 | Pending |
| TSCF-03 | Phase 5 | Pending |
| DX-01 | Phase 6 | Pending |
| DX-02 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 21 total
- Mapped to phases: 21
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-02*
*Last updated: 2026-06-02 after initial definition*
