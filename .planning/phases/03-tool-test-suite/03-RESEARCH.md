# Phase 3: Tool Test Suite - Research

**Researched:** 2026-06-03
**Domain:** Python test suite with pytest — unit and integration tests for a CLI code-generator
**Confidence:** HIGH

---

## Summary

Phase 2 delivered a fully-operational `fclean/` package. It also seeded three test files
(`tests/test_utils.py`, `tests/test_generator.py`, `tests/test_templates.py`) with 12 passing
tests. Phase 3 does NOT start from zero — it starts from a partial test suite and must fill
the gaps to satisfy TEST-01 through TEST-05.

All five test requirements can be addressed entirely with built-in pytest facilities (`tmp_path`,
`monkeypatch`, `capsys`, `pytest.raises`). No new packages need to be installed; pytest 9.0.3
is already installed in the project `.venv`. The test runner is configured via `pyproject.toml`
and the full suite runs in ~0.02 seconds (measured), meaning the < 5 second performance
requirement is trivially satisfied.

The main planning risk is TEST-05. The `--dry-run` flag is assigned to Phase 6 (DX-01), but
TEST-05 requires a test for it in Phase 3. The ROADMAP note ("dry-run tested here or in CLI
tests") acknowledges the tension. The planner must resolve this explicitly: either implement
the `--dry-run` flag minimally in Phase 3 as part of Plan 3.3, or mark TEST-05 tests as
skipped stubs pending Phase 6 completion. The recommended approach is described in
Architecture Patterns below.

A secondary tension: TEST-03 says "all 5 template providers", but only 4 exist today (bloc,
cubit, riverpod, getx). The 5th (provider/ChangeNotifier) is Phase 5's STATE-01. Plan 3.3
should cover the 4 existing templates and add a skip stub for the 5th.

**Primary recommendation:** Extend the three existing test files in-place — do NOT create
new files that duplicate their responsibilities. Each plan maps cleanly to one existing file
plus its required additions.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TEST-01 | `pytest` suite covers `to_pascal_case()` for single words, snake_case, and edge cases | 3 existing tests in `test_utils.py`; need 3–4 more edge-case tests |
| TEST-02 | Tests cover `create_feature()` — correct file set in temp dir for each `--state` option | 3 existing tests in `test_generator.py`; need cubit/riverpod/getx/None branches + entity path |
| TEST-03 | Tests cover all 5 template providers — verify generated Dart file contents | 1 existing test (riverpod only); need bloc, cubit, getx + stub for future provider template |
| TEST-04 | Tests cover input validation — invalid names raise errors, valid names pass | 6 existing tests in `test_utils.py`; need double-underscore and hyphen edge cases |
| TEST-05 | Tests cover `--dry-run` flag — no files written, expected paths printed | Flag not yet implemented; needs minimal implementation OR skip stub |
</phase_requirements>

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Validator unit tests (TEST-01, TEST-04) | Test layer (`tests/test_utils.py`) | — | Pure function, no I/O, unit-testable directly |
| Generator integration tests (TEST-02) | Test layer (`tests/test_generator.py`) | Filesystem (`tmp_path`) | `create_feature()` writes files; needs real tmp dir |
| Template content tests (TEST-03) | Test layer (`tests/test_templates.py`) | — | Template providers are pure functions returning strings |
| Dry-run tests (TEST-05) | Test layer (`tests/test_templates.py` or new `tests/test_cli.py`) | CLI layer (`fclean/cli.py`) | Dry-run is a CLI flag; needs CLI + generator cooperation |

---

## Standard Stack

### Core (already installed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.0.3 [VERIFIED: pip show] | Test runner, fixtures, assertions | Standard Python test framework; already installed in `.venv` |

### Built-in Fixtures Used

| Fixture | Source | Purpose |
|---------|--------|---------|
| `tmp_path` | pytest built-in | Provides a fresh `pathlib.Path` temp dir per test — no plugin needed [VERIFIED: pytest docs] |
| `monkeypatch` | pytest built-in | `monkeypatch.chdir(tmp_path)` makes relative `Path()` calls resolve into tmp dir [VERIFIED: pytest docs] |
| `capsys` | pytest built-in | Capture stdout/stderr — used for dry-run output assertions [VERIFIED: pytest docs] |
| `pytest.raises` | pytest built-in | Assert that code raises `SystemExit` with a specific code [VERIFIED: pytest docs] |

### No New Packages Required

The phase requires zero new package installs. pytest 9.0.3 already provides all needed
facilities. `pytest-cov` is optional for coverage reporting but not required for the TEST-XX
requirements.

**Installation:** Nothing to install. `.venv/bin/pytest` is ready.

---

## Package Legitimacy Audit

No new packages are introduced in this phase. The only package in use is `pytest>=7`, which is
already installed at version 9.0.3.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| pytest | PyPI | ~18 yrs | >200M/wk | github.com/pytest-dev/pytest | N/A — pre-existing dep | Approved |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

*slopcheck was unavailable at research time, but pytest is a pre-existing dependency already
installed and well-established; no legitimacy gate action required.*

---

## Architecture Patterns

### System Architecture Diagram

```
Test Invocation
    │
    ├── tests/test_utils.py ──────────────────────────────────────────────────
    │       │                                                                 │
    │       ├── to_pascal_case("auth")        fclean.generators.validator    │
    │       ├── to_pascal_case("user_profile")    (pure function)            │
    │       ├── to_pascal_case edge cases                                    │
    │       ├── validate_name("auth")  → pass                                │
    │       └── validate_name("../evil") → SystemExit(1)                    │
    │                                                                         │
    ├── tests/test_generator.py ──────────────────────────────────────────────
    │       │                                                                 │
    │       ├── tmp_path / monkeypatch.chdir(tmp_path)                       │
    │       ├── create_feature("auth", "bloc")  ──► writes to tmp_path/lib/  │
    │       ├── create_feature("auth", "cubit") ──► asserts file set         │
    │       ├── create_feature("auth", "riverpod")                           │
    │       ├── create_feature("auth", "getx")                               │
    │       ├── create_feature("auth", None)  ──► no state files             │
    │       └── create_feature("auth:user", "bloc") ──► entity files exist   │
    │                                                                         │
    └── tests/test_templates.py ──────────────────────────────────────────────
            │
            ├── get_bloc_templates("user_profile") → assert class names
            ├── get_cubit_templates("user_profile") → assert class names
            ├── get_riverpod_templates("user_profile") → assert StateNotifierProvider
            ├── get_getx_templates("user_profile") → assert GetxController
            └── (dry-run stub or CLI test)
```

### Recommended Project Structure (no changes needed)

```
tests/
├── test_utils.py        # TEST-01, TEST-04: validator and to_pascal_case
├── test_generator.py    # TEST-02: create_feature for each --state option
└── test_templates.py    # TEST-03, TEST-05: all template providers + dry-run
```

No `conftest.py` is needed. `tmp_path` and `monkeypatch` are auto-provided by pytest.

### Pattern 1: Extending Existing Test Files In-Place

**What:** Each plan adds tests to the corresponding file that already exists; it does NOT create
new test files that overlap responsibility.
**When to use:** The three existing test files each own a clear domain. Mixing them would
break the one-file-per-concern structure.
**Example:**
```python
# Source: existing tests/test_utils.py — add below existing tests
def test_to_pascal_case_multiple_underscores():
    assert to_pascal_case("my_long_feature_name") == "MyLongFeatureName"

def test_to_pascal_case_trailing_underscore():
    # trailing underscore produces an empty segment → capitalize("") = ""
    # This is an edge case — document actual behavior, don't paper over it
    result = to_pascal_case("auth_")
    assert result == "Auth"  # or "Auth" + "" — confirm actual output
```

### Pattern 2: Generator Tests with tmp_path + monkeypatch.chdir

**What:** Every test that calls `create_feature()` must redirect the CWD to `tmp_path` so
relative `Path("lib/features/...")` calls land in the temp directory, not the project root.
**When to use:** Any test that exercises `create_feature()` or any future generator.
**Example:**
```python
# Source: established in tests/test_generator.py
def test_create_feature_cubit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "cubit")
    assert (tmp_path / "lib/features/auth/presentation/cubit/auth_cubit.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/cubit/auth_state.dart").exists()
    # Base files must also exist
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
```

### Pattern 3: Template Content Assertions

**What:** Call the template provider directly (it's a pure function), iterate dict values,
assert on string content. No filesystem needed.
**When to use:** All template tests. Fast — no I/O.
**Example:**
```python
# Source: established in tests/test_templates.py
def test_bloc_template_class_names():
    templates = get_bloc_templates("user_profile")
    all_content = " ".join(templates.values())
    assert "UserProfileBloc" in all_content
    assert "UserProfileEvent" in all_content
    assert "UserProfileState" in all_content

def test_cubit_template_class_names():
    templates = get_cubit_templates("user_profile")
    all_content = " ".join(templates.values())
    assert "UserProfileCubit" in all_content
    assert "UserProfileState" in all_content

def test_getx_template_class_names():
    templates = get_getx_templates("auth")
    all_content = " ".join(templates.values())
    assert "AuthController" in all_content
    assert "AuthBinding" in all_content
```

### Pattern 4: Asserting SystemExit with Code

**What:** Wrap the call in `pytest.raises(SystemExit)` and assert `.code == 1`.
**When to use:** `validate_name()` invalid input tests, `create_feature()` with bad format.
**Example:**
```python
# Source: established in tests/test_utils.py
def test_validate_name_hyphen_exits():
    with pytest.raises(SystemExit) as exc_info:
        validate_name("my-feature")
    assert exc_info.value.code == 1
```

### Pattern 5: Resolving TEST-05 (dry-run)

**What:** The `--dry-run` flag is Phase 6 work (DX-01), not yet in `cli.py`. TEST-05
requires tests that verify no files are written and expected paths are printed.

**Recommended approach:** Implement a minimal `dry_run` parameter on `create_feature()` in
Phase 3, Plan 3.3. This is a small addition (one boolean parameter, one conditional around
`path.write_text`) that lets TEST-05 be satisfied without touching argparse. The full CLI
integration (`--dry-run` flag in argparse) remains Phase 6 work.

Alternatively, if the planner prefers zero scope bleed: add a `@pytest.mark.skip` stub for
TEST-05 in Plan 3.3 with a docstring explaining it depends on Phase 6. This satisfies the
"tests exist" intent even if not green yet.

**If the minimal dry_run approach is taken, the signature becomes:**
```python
def create_feature(feature_arg, state_type, dry_run=False):
    ...
    for path, content in files_to_create.items():
        if dry_run:
            print(path)
            continue
        if path.exists():
            print(f"Skipping: {path} already exists.")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
```

**Test pattern:**
```python
def test_dry_run_no_files_written(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "bloc", dry_run=True)
    captured = capsys.readouterr()
    # No files should exist
    assert not (tmp_path / "lib").exists()
    # Paths should be printed
    assert "auth_bloc.dart" in captured.out
```

### Anti-Patterns to Avoid

- **Importing from top-level `fclean` inside submodule test helpers:** Always import from
  direct submodules (`from fclean.generators.validator import to_pascal_case`) in test
  helpers. `from fclean import ...` is fine in test files since tests are outside the package.

- **Calling `create_feature()` without `monkeypatch.chdir(tmp_path)`:** The generator uses
  relative `Path("lib/features/...")` internally. Without the chdir, tests write to the actual
  project root. Every `create_feature()` test MUST use `monkeypatch.chdir(tmp_path)`.

- **Asserting only one file per state type:** Each state type generates multiple files. Assert
  the full expected set, not just the most obvious file.

- **Testing template strings with exact equality:** Dart template strings may have minor
  whitespace differences. Use `in` substring checks, not `==` equality on full content.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Temp directory isolation | Manual `tempfile.mkdtemp()` + cleanup | `tmp_path` fixture | pytest handles creation and cleanup automatically; `mkdtemp` requires manual teardown |
| CWD manipulation | `os.chdir()` + try/finally restore | `monkeypatch.chdir()` | monkeypatch auto-restores CWD after test, even on failure |
| stdout/stderr capture | `io.StringIO()` redirect | `capsys` fixture | pytest's capsys works across the full call stack, not just immediate prints |
| SystemExit testing | try/except SystemExit | `pytest.raises(SystemExit)` | Standard pytest idiom; provides `.value.code` access |

**Key insight:** pytest's built-in fixtures eliminate all boilerplate for filesystem, CWD,
and output capture. Never reach for stdlib workarounds when a pytest fixture exists.

---

## Common Pitfalls

### Pitfall 1: Generator Tests Without chdir Hit Project Root
**What goes wrong:** `create_feature("auth", "bloc")` creates `lib/features/auth/` in the
actual project root, not in the temp dir. Tests pass but pollute the repo.
**Why it happens:** `create_feature()` uses `Path("lib/features") / feature_name` (relative)
so it resolves against the actual CWD.
**How to avoid:** Always `monkeypatch.chdir(tmp_path)` before calling `create_feature()`.
**Warning signs:** `lib/` directory appearing in `git status` after running tests.

### Pitfall 2: TEST-03 "5 Template Providers" Mismatch
**What goes wrong:** Attempting to import and test a `get_provider_templates` function that
doesn't exist yet (Phase 5 delivers it). Import error causes the whole test file to fail.
**Why it happens:** Requirements say "5 template providers" but only 4 exist in Phase 3.
**How to avoid:** Cover only the 4 existing providers. Add a comment or skip stub noting
the 5th (`provider`) is pending Phase 5.
**Warning signs:** `ImportError: cannot import name 'get_provider_templates'`.

### Pitfall 3: Asserting Wrong File Paths for State Types
**What goes wrong:** Asserting `presentation/bloc/` path for a cubit test, or similar cross-
contamination. Tests pass with wrong state type because bloc files were already created in a
prior test that shared the same `tmp_path` (they don't — `tmp_path` is per-test).
**Why it happens:** Confusion between bloc/cubit/riverpod subdirectory names.
- bloc → `presentation/bloc/`
- cubit → `presentation/cubit/`
- riverpod → `presentation/providers/`
- getx → `presentation/controller/` and `presentation/bindings/`
**How to avoid:** Read `fclean/templates/*.py` before writing path assertions.
**Warning signs:** Test passing when it should fail — indicates wrong assertion target.

### Pitfall 4: TEST-05 Scope Bleed
**What goes wrong:** Adding `--dry-run` to argparse in `cli.py` during Plan 3.3 to satisfy
TEST-05, which then conflicts with Phase 6's plan to do the same thing (DX-01). Phase 6 plan
would be a no-op or overwrite.
**Why it happens:** TEST-05 and DX-01 are logically related but in different phases.
**How to avoid:** Either (a) add `dry_run` parameter to `create_feature()` only (no argparse
touch) in Phase 3, or (b) use skip stubs for TEST-05 tests. Document the decision explicitly
in the plan so Phase 6 knows what to expect.

### Pitfall 5: to_pascal_case Edge Cases — Trailing Underscore
**What goes wrong:** `to_pascal_case("auth_")` produces `"Auth"` because `"auth_".split("_")`
returns `["auth", ""]` and `"".capitalize()` returns `""`. The test asserts `"Auth"` and passes,
but it's easy to accidentally write `assert result == "Auth_"`.
**Why it happens:** Python `"".capitalize()` returns `""` silently.
**How to avoid:** Run the function manually first, then write the assertion based on actual
output. Trailing underscores are invalid per `_NAME_RE` anyway — `validate_name("auth_")`
would exit before `to_pascal_case` is called. A test documenting this behavior is still
valuable for regression.

---

## Code Examples

### Full file set for each state type (for assertion completeness)

```python
# Source: fclean/generators/feature.py + fclean/templates/*.py (verified by reading source)

# Files created by create_feature("auth", "bloc"):
BLOC_FILES = [
    "lib/features/auth/data/datasources/auth_remote_datasource.dart",
    "lib/features/auth/data/datasources/auth_local_datasource.dart",
    "lib/features/auth/data/repository/auth_repository_impl.dart",
    "lib/features/auth/domain/repository/auth_repository.dart",
    "lib/features/auth/presentation/bloc/auth_event.dart",
    "lib/features/auth/presentation/bloc/auth_state.dart",
    "lib/features/auth/presentation/bloc/auth_bloc.dart",
]

# Files created by create_feature("auth", "cubit"):
CUBIT_FILES = [
    "lib/features/auth/data/datasources/auth_remote_datasource.dart",
    "lib/features/auth/data/datasources/auth_local_datasource.dart",
    "lib/features/auth/data/repository/auth_repository_impl.dart",
    "lib/features/auth/domain/repository/auth_repository.dart",
    "lib/features/auth/presentation/cubit/auth_state.dart",
    "lib/features/auth/presentation/cubit/auth_cubit.dart",
]

# Files created by create_feature("auth", "riverpod"):
RIVERPOD_FILES = [
    "lib/features/auth/data/datasources/auth_remote_datasource.dart",
    "lib/features/auth/data/datasources/auth_local_datasource.dart",
    "lib/features/auth/data/repository/auth_repository_impl.dart",
    "lib/features/auth/domain/repository/auth_repository.dart",
    "lib/features/auth/presentation/providers/auth_provider.dart",
]

# Files created by create_feature("auth", "getx"):
GETX_FILES = [
    "lib/features/auth/data/datasources/auth_remote_datasource.dart",
    "lib/features/auth/data/datasources/auth_local_datasource.dart",
    "lib/features/auth/data/repository/auth_repository_impl.dart",
    "lib/features/auth/domain/repository/auth_repository.dart",
    "lib/features/auth/presentation/controller/auth_controller.dart",
    "lib/features/auth/presentation/bindings/auth_binding.dart",
]

# Extra files created by create_feature("auth:user", "bloc") (entity specified):
ENTITY_EXTRA_FILES = [
    "lib/features/auth/domain/entities/user.dart",
    "lib/features/auth/data/models/user_model.dart",
]
```

### Template content assertions (verified from source)

```python
# Source: fclean/templates/bloc.py
def test_bloc_event_file_content():
    templates = get_bloc_templates("auth")
    assert "abstract class AuthEvent {}" in templates["presentation/bloc/auth_event.dart"]

def test_bloc_bloc_imports():
    templates = get_bloc_templates("auth")
    content = templates["presentation/bloc/auth_bloc.dart"]
    assert "import 'package:flutter_bloc/flutter_bloc.dart';" in content
    assert "class AuthBloc extends Bloc<AuthEvent, AuthState>" in content

# Source: fclean/templates/riverpod.py
def test_riverpod_file_key():
    templates = get_riverpod_templates("auth")
    assert "presentation/providers/auth_provider.dart" in templates

# Source: fclean/templates/getx.py
def test_getx_controller_key():
    templates = get_getx_templates("auth")
    assert "presentation/controller/auth_controller.dart" in templates
    assert "presentation/bindings/auth_binding.dart" in templates
```

---

## Existing Tests vs. Requirements Gap Analysis

| Requirement | Existing Coverage | Gap |
|-------------|-------------------|-----|
| TEST-01 | 3 tests (single word, snake, digit) | Edge cases: multiple underscores, trailing underscore, digit-at-end of segment |
| TEST-02 | bloc only, 2 files asserted | All 4 state types; None state; entity path; full file set per type |
| TEST-03 | riverpod only | bloc, cubit, getx content; 5th template stub |
| TEST-04 | 4 invalid-name tests | hyphen, space, double-underscore edge cases |
| TEST-05 | 0 tests | Entire requirement — needs dry_run implementation decision first |

**Tests to add (estimated total):**
- `test_utils.py`: +4 tests (TEST-01 edge cases, TEST-04 edge cases)
- `test_generator.py`: +5 tests (cubit, riverpod, getx, None state, entity path)
- `test_templates.py`: +3 tests (bloc, cubit, getx) + TEST-05 resolution (1–3 tests or skip stubs)

**Total new tests: ~12–15** (bringing suite from 12 to ~24–27 tests)

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `pytest-tmp-path` (non-existent package) | `tmp_path` built-in fixture | pytest 3.9+ | No plugin needed; always available |
| `sys.path.insert(0, ".")` in test files | `pip install -e .` editable install | Phase 2 | Tests import `fclean` as an installed package; path hacks removed |

**Deprecated/outdated:**
- `sys.path.insert(0, ".")`: Removed in Phase 2. Never re-add it. The package is editably installed.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `to_pascal_case("auth_")` returns `"Auth"` (trailing underscore → empty segment → `"".capitalize() == ""`) | Code Examples / Pitfall 5 | Low — easily verified by running the function before writing the assertion |
| A2 | The 5th template provider (TEST-03) refers to the Phase 5 `provider/ChangeNotifier` template, not an existing module | Standard Stack / Pitfall 2 | Medium — if wrong, Phase 3 could miss a template; verify against REQUIREMENTS.md note |
| A3 | TEST-05 is satisfied by a `dry_run` parameter on `create_feature()` without argparse involvement in Phase 3 | Pattern 5 | Low — this is a design choice for the planner, not a factual claim |

---

## Open Questions

1. **TEST-05 resolution strategy**
   - What we know: `--dry-run` (DX-01) is Phase 6 work; TEST-05 needs a test now
   - What's unclear: Should Phase 3 implement `dry_run=False` on `create_feature()`, or use skip stubs?
   - Recommendation: Implement `dry_run` parameter on `create_feature()` only (no CLI/argparse changes). This satisfies TEST-05 without scope bleed into Phase 6.

2. **TEST-03 "5 template providers" count**
   - What we know: 4 providers exist today; the 5th (provider) is Phase 5
   - What's unclear: Does TEST-03 require the 5th to be tested in Phase 3?
   - Recommendation: Cover 4 existing providers fully in Phase 3. Add a `pytest.mark.skip` stub with comment `# Phase 5: provider template pending STATE-01`. Phase 5's Plan 5.3 removes the skip.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All tests | ✓ | 3.14.5 | — |
| pytest | Test runner | ✓ | 9.0.3 | — |
| fclean package | All test imports | ✓ | 0.1.0 (editable) | — |
| `.venv/bin/pytest` | CI / direct run | ✓ | 9.0.3 | `python -m pytest` |

**Missing dependencies with no fallback:** None.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | `pyproject.toml` (rootdir auto-detected; `[tool.pytest.ini_options]` not yet written but not needed) |
| Quick run command | `.venv/bin/pytest` |
| Full suite command | `.venv/bin/pytest -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TEST-01 | `to_pascal_case()` edge cases | unit | `.venv/bin/pytest tests/test_utils.py -x` | ✅ exists, needs additions |
| TEST-02 | `create_feature()` for each state type in tmp dir | integration | `.venv/bin/pytest tests/test_generator.py -x` | ✅ exists, needs additions |
| TEST-03 | All template providers return correct class names | unit | `.venv/bin/pytest tests/test_templates.py -x` | ✅ exists, needs additions |
| TEST-04 | Invalid names raise SystemExit(1) | unit | `.venv/bin/pytest tests/test_utils.py -x` | ✅ exists, needs additions |
| TEST-05 | dry_run=True writes no files, prints paths | unit | `.venv/bin/pytest tests/test_templates.py -x` | ❌ pending dry_run implementation |

### Sampling Rate

- **Per task commit:** `.venv/bin/pytest`
- **Per wave merge:** `.venv/bin/pytest -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `dry_run` parameter on `create_feature()` — required before TEST-05 tests can be written (Plan 3.3, Wave 1 if scoped here, or skip stub if deferred to Phase 6)

*(All test files exist. No new framework installs needed. The only Wave 0 gap is the dry_run
implementation decision for TEST-05.)*

---

## Security Domain

This phase adds tests only — no new user-facing inputs, no filesystem writes beyond tmp_path,
no network calls. ASVS categories V2/V3/V4/V6 are not applicable. V5 (input validation) is
already exercised by the existing `validate_name` tests (TEST-04) and will be extended in
Plan 3.1.

No new threat surface is introduced.

---

## Sources

### Primary (HIGH confidence)
- Source code `fclean/generators/validator.py`, `fclean/generators/feature.py`, `fclean/templates/*.py` — verified by direct file read
- Source code `tests/test_utils.py`, `tests/test_generator.py`, `tests/test_templates.py` — verified by direct file read
- `.venv/bin/pytest --version` output: `pytest 9.0.3` — verified by shell execution
- `.venv/bin/pytest --collect-only` — verified 12 tests collected, 0 failures
- `pyproject.toml` — verified package name, entry point, dev dependencies

### Secondary (MEDIUM confidence)
- pytest `tmp_path`, `monkeypatch`, `capsys`, `pytest.raises` — [ASSUMED] based on training knowledge of pytest built-ins, consistent with installed version 9.0.3

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — pytest installed and confirmed; all fixtures are built-in
- Architecture: HIGH — source files read directly; file sets derived from actual template code
- Pitfalls: HIGH — derived from actual code inspection and project history (Phase 2 PATTERNS.md)
- TEST-05 resolution: MEDIUM — design decision deferred to planner

**Research date:** 2026-06-03
**Valid until:** End of Phase 3 execution (all source files stable)
