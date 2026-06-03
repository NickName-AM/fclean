# Phase 2: Restructure & Package - Research

**Researched:** 2026-06-03
**Domain:** Python package restructuring and pip packaging
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PKG-01 | Project restructured from single-file `fclean.py` into a proper Python package layout (`fclean/cli.py`, `fclean/generators/`, `fclean/templates/`) | Module split pattern documented; `__init__.py` role, import re-exports, and test import update path all covered |
| PKG-02 | `pyproject.toml` added with metadata, `requires-python = ">=3.8"`, and a `[project.scripts]` entry so `pip install .` makes `fclean` available as a CLI command | Full `pyproject.toml` schema documented with verified examples; hatchling build backend chosen |
| PKG-03 | `fclean --features auth --state bloc` works identically after restructure (no regression) | Regression risk identified; test import update strategy documented; existing 12-test suite must remain green |
</phase_requirements>

---

## Summary

Phase 2 converts a 199-line single-file Python script into a proper importable package. The work splits into two clear parts: (1) creating the `fclean/` package directory tree with code distributed across submodules, and (2) adding a `pyproject.toml` that gives setuptools or hatchling enough information to build a wheel and install the `fclean` CLI entry point.

The codebase is minimal (stdlib only, no third-party dependencies) and already passes 12 tests. The primary technical risks are: (a) the test files currently use `sys.path.insert(0, ".")` and `from fclean import ...` — both imports will break after the rename and must be updated; and (b) `fclean.py` at the root and the new `fclean/` package directory cannot coexist because Python will prefer the directory, causing a silent import conflict. The root `fclean.py` must be removed as part of the same commit that creates the package.

The recommended build backend is hatchling, which is the PyPA-endorsed modern default for new projects. `tmp_path` is a pytest built-in fixture — there is no `pytest-tmp-path` package on PyPI, and the existing tests already use it correctly.

**Primary recommendation:** Create `fclean/` package with `__init__.py` that re-exports the public API, split source into submodules per the roadmap layout, update all test imports, add `pyproject.toml` using hatchling, then delete `fclean.py`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CLI argument parsing | `fclean/cli.py` | — | argparse `main()` is the entry point; isolated so entry point declaration in pyproject.toml has a single target |
| Feature generation logic | `fclean/generators/feature.py` | — | All directory creation and file-write orchestration belongs in one generator module |
| Name validation + utilities | `fclean/generators/validator.py` | — | Pure functions with no I/O; isolating them makes them trivially importable in tests |
| Template content providers | `fclean/templates/bloc.py` et al. | — | Each template file returns `dict[str, str]`; one file per state library keeps additions non-conflicting |
| Package public API | `fclean/__init__.py` | — | Re-exports functions the existing tests import so test update is mechanical |
| Build metadata + entry point | `pyproject.toml` | — | Standard Python packaging artifact; declares `fclean = "fclean.cli:main"` |

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| hatchling | 1.30.1 [VERIFIED: PyPI] | Build backend for `pyproject.toml` | PyPA-recommended modern backend; zero configuration for simple packages; respects `.gitignore`; no MANIFEST.in needed [CITED: packaging.python.org] |
| pytest | 9.0.3 [VERIFIED: PyPI, already installed] | Test runner | Already used by the project; `tmp_path` is built-in; no additional plugins needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| setuptools | 82.0.1 [VERIFIED: PyPI] | Alternative build backend | Only if hatchling causes friction; setuptools is the ecosystem default with the broadest compatibility |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| hatchling | setuptools | setuptools has wider compatibility but requires more boilerplate; hatchling is cleaner for new projects with no `setup.py` history |
| hatchling | flit-core | flit-core is even simpler but has fewer escape hatches; hatchling is better long-term as the project grows |

**Installation (editable dev install after pyproject.toml is added):**
```bash
pip3 install -e ".[dev]"
```

---

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| hatchling | PyPI | ~4 yrs (623 releases since 2021) | Very high (PyPA first-party) | github.com/pypa/hatch | [OK] | Approved |
| pytest | PyPI | ~16 yrs (190+ releases) | Extremely high | github.com/pytest-dev/pytest | [OK] | Approved |
| setuptools | PyPI | ~15 yrs (620+ releases) | Extremely high | github.com/pypa/setuptools | [OK] | Approved |

**Packages removed due to slopcheck [SLOP] verdict:** none

**IMPORTANT — `pytest-tmp-path` does not exist on PyPI.** The roadmap (Plan 2.2) mentions it as a dev dependency. This is incorrect: `tmp_path` is a built-in pytest fixture available since pytest 3.9, requiring no separate package. The `[project.optional-dependencies]` dev table should declare only `pytest` (already installed as 9.0.3). [VERIFIED: docs.pytest.org/en/stable/how-to/tmp_path.html]

---

## Architecture Patterns

### System Architecture Diagram

```
CLI invocation: fclean --features auth --state bloc
        │
        ▼
fclean/cli.py          argparse → (feature_args, state_type)
        │
        ▼
fclean/generators/
  validator.py         validate_name(), to_pascal_case()
  feature.py           create_feature()
        │
        ├──────────────────────────────────────────┐
        ▼                                          ▼
fclean/templates/              state_map dispatch table
  bloc.py  cubit.py            get_bloc_templates()
  riverpod.py  getx.py         get_cubit_templates()
                                ...etc
        │
        ▼
lib/features/<name>/   Flutter project filesystem (output)
```

### Recommended Project Structure
```
fclean/                    # Python package (replaces fclean.py)
├── __init__.py            # Re-exports: to_pascal_case, validate_name, create_feature, get_*_templates
├── cli.py                 # argparse + main() — entry point target for pyproject.toml
├── generators/
│   ├── __init__.py        # Empty — marks as package
│   ├── feature.py         # create_feature(), is_flutter_project()
│   └── validator.py       # validate_name(), to_pascal_case()
└── templates/
    ├── __init__.py        # Empty — marks as package
    ├── bloc.py            # get_bloc_templates(feature)
    ├── cubit.py           # get_cubit_templates(feature)
    ├── riverpod.py        # get_riverpod_templates(feature)
    └── getx.py            # get_getx_templates(feature)

tests/
├── test_utils.py          # Imports updated: from fclean import ...
├── test_generator.py      # Imports updated: from fclean import ...
└── test_templates.py      # Imports updated: from fclean import ...

pyproject.toml             # Build metadata + entry point
fclean.py                  # DELETED in this phase
```

**Note on flat layout vs src layout:** The roadmap specifies flat layout (`fclean/` at repo root). This is correct for a tool this size. The testing risk (accidentally importing from cwd) is fully mitigated by using `pip install -e .` during development — once installed editably, `import fclean` resolves to the installed package regardless of cwd. [CITED: packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/]

### Pattern 1: `__init__.py` Re-export Layer

**What:** `fclean/__init__.py` re-exports the public symbols that tests and external callers currently import from the top-level `fclean` module.
**When to use:** When splitting a single-file module into submodules while keeping the public API surface unchanged.
**Example:**
```python
# fclean/__init__.py
# Source: standard Python packaging practice [ASSUMED]
from fclean.generators.validator import to_pascal_case, validate_name
from fclean.generators.feature import create_feature
from fclean.templates.bloc import get_bloc_templates
from fclean.templates.cubit import get_cubit_templates
from fclean.templates.riverpod import get_riverpod_templates
from fclean.templates.getx import get_getx_templates

__all__ = [
    "to_pascal_case",
    "validate_name",
    "create_feature",
    "get_bloc_templates",
    "get_cubit_templates",
    "get_riverpod_templates",
    "get_getx_templates",
]
```
With this re-export, the existing test files only need their `sys.path.insert(0, ".")` lines removed — the `from fclean import ...` statements remain syntactically identical.

### Pattern 2: `pyproject.toml` for CLI Tool (hatchling)

**What:** Minimal `pyproject.toml` declaring build backend, metadata, and the `fclean` console script entry point.
**When to use:** Whenever you want `pip install .` or `pip install -e .` to install the CLI.
**Example:**
```toml
# Source: packaging.python.org/en/latest/guides/writing-pyproject-toml/ [CITED]
[build-system]
requires = ["hatchling >= 1.26"]
build-backend = "hatchling.build"

[project]
name = "fclean"
version = "0.1.0"
description = "Flutter Clean Architecture feature scaffold generator"
requires-python = ">=3.8"

[project.scripts]
fclean = "fclean.cli:main"

[project.optional-dependencies]
dev = ["pytest>=7"]
```

### Pattern 3: pytest Configuration in pyproject.toml

**What:** Add `[tool.pytest.ini_options]` to replace the `sys.path.insert(0, ".")` hack the tests currently use.
**When to use:** When tests need to import from a package that will be installed in editable mode.
**Example:**
```toml
# Source: docs.pytest.org/en/stable/explanation/pythonpath.html [CITED]
[tool.pytest.ini_options]
# pythonpath = ["."]  # Only needed if NOT using editable install
# With pip install -e ., no pythonpath config is needed at all.
```
After `pip install -e .`, pytest will find `fclean` on the Python path automatically. The `sys.path.insert(0, ".")` lines in all three test files should be removed entirely.

### Anti-Patterns to Avoid
- **Leaving `fclean.py` at the root alongside `fclean/` directory:** Python import resolution finds the package directory first, but the file's presence creates confusion. Remove `fclean.py` in the same commit that creates the `fclean/` directory.
- **Using `sys.path.insert` in test files post-restructure:** After `pip install -e .` and with a proper `pyproject.toml`, this is unnecessary and can mask real import errors. Remove from all three test files.
- **Declaring `pytest-tmp-path` as a dependency:** This package does not exist. `tmp_path` is built into pytest. Adding it will cause a pip install failure.
- **Forgetting `__init__.py` in subpackages:** Without `__init__.py` in `fclean/generators/` and `fclean/templates/`, Python 3 treats them as namespace packages, which works for imports but breaks the hatchling package-discovery scan. Include empty `__init__.py` files.
- **Putting `is_flutter_project()` in `cli.py` instead of `generators/feature.py`:** The function is a guard for the generation step, not a CLI concern. Keeping it close to `create_feature()` makes the generators self-contained and testable without an argparse harness.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Console script entry point | Manual shell script / symlink wrapper | `[project.scripts]` in `pyproject.toml` | pip handles PATH installation and Python version resolution automatically across all platforms |
| Temporary directories in tests | Manual `tempfile.mkdtemp()` + cleanup | `tmp_path` pytest built-in | Automatic cleanup on test teardown; returns `pathlib.Path`; zero boilerplate |
| Package discovery | Manual `packages=` list in setup.py | Hatchling auto-discovery | Hatchling finds all `fclean/` subpackages automatically from the directory structure |

**Key insight:** The entire packaging challenge for this project is ~15 lines of `pyproject.toml`. Do not over-engineer.

---

## Common Pitfalls

### Pitfall 1: `fclean.py` and `fclean/` coexist during transition
**What goes wrong:** If `fclean.py` exists at the root and `fclean/` also exists, `import fclean` resolves to the directory (package) in Python 3 — but leaving the file causes confusion, potential IDE issues, and will fail in edge cases where the file is on path before the directory.
**Why it happens:** Incremental refactoring: developer creates the package but forgets to delete the file.
**How to avoid:** Delete `fclean.py` in the same task/commit as creating `fclean/__init__.py`. Do not treat them as separate steps.
**Warning signs:** `python3 -c "import fclean; print(fclean.__file__)"` — if this prints `fclean.py`, the package is not being found.

### Pitfall 2: Tests break with `ModuleNotFoundError: No module named 'fclean'`
**What goes wrong:** After restructure, tests fail because neither the editable install nor the `sys.path` hack is in place.
**Why it happens:** Three things must happen together: (1) `fclean.py` deleted, (2) `fclean/` package created, (3) `pip install -e .` run. Doing only 1-2 of these leaves tests broken.
**How to avoid:** The plan must include a task to run `pip install -e .` (or `pip3 install -e .`) immediately after `pyproject.toml` is created and before any test run. Remove the `sys.path.insert(0, ".")` lines from all test files only after confirming the editable install resolves imports.
**Warning signs:** Running `python3 -m pytest` before `pip install -e .` will produce `ModuleNotFoundError`.

### Pitfall 3: Circular imports between submodules
**What goes wrong:** `fclean/generators/feature.py` imports from `fclean/templates/bloc.py`, and `fclean/__init__.py` imports from all submodules. If any template file imports from `fclean/__init__.py` (instead of directly from its sibling), a circular import occurs.
**Why it happens:** Developers habitually use `from fclean import to_pascal_case` even inside the package. Inside the package, this should be `from fclean.generators.validator import to_pascal_case`.
**How to avoid:** Inside the `fclean/` package, always use relative or direct absolute imports (e.g., `from fclean.generators.validator import ...`), never `from fclean import ...` (which goes through `__init__.py`).
**Warning signs:** `ImportError: cannot import name 'X' from partially initialized module 'fclean'`

### Pitfall 4: `hatchling` not installed in the build environment
**What goes wrong:** `pip install .` fails with `ModuleNotFoundError: No module named 'hatchling'` or a build backend error.
**Why it happens:** Hatchling is not part of the Python standard library or pip's bundled build tools. It must be installed or available.
**How to avoid:** Modern pip (>=19.0) automatically installs `[build-system].requires` in an isolated build environment. Running `pip3 install -e .` in a fresh environment will automatically fetch hatchling. No manual pre-installation needed.
**Warning signs:** Error during `pip install .` mentioning build backend or hatchling.

---

## Code Examples

Verified patterns from official sources:

### Complete `pyproject.toml` for fclean
```toml
# Source: packaging.python.org/en/latest/guides/writing-pyproject-toml/ [CITED]
[build-system]
requires = ["hatchling >= 1.26"]
build-backend = "hatchling.build"

[project]
name = "fclean"
version = "0.1.0"
description = "Flutter Clean Architecture feature scaffold generator"
readme = "README.md"
requires-python = ">=3.8"

[project.scripts]
fclean = "fclean.cli:main"

[project.optional-dependencies]
dev = ["pytest>=7"]
```

### Test file import update (post-restructure)
```python
# Before (fclean.py era):
import sys
sys.path.insert(0, ".")
from fclean import to_pascal_case, validate_name

# After (fclean/ package era, with pip install -e .):
# sys.path manipulation is gone; imports are identical:
from fclean import to_pascal_case, validate_name
```

### `fclean/cli.py` entry point
```python
# Source: current fclean.py main() function — move verbatim [ASSUMED pattern]
import argparse
import sys
from fclean.generators.feature import create_feature, is_flutter_project


def main():
    parser = argparse.ArgumentParser(description="fclean: Flutter Clean Architecture Generator")
    parser.add_argument("--features", nargs="+", required=True)
    parser.add_argument("--state", choices=["bloc", "cubit", "riverpod", "getx"])
    args = parser.parse_args()

    if not is_flutter_project():
        print("Error: This tool must be run from the root of a Flutter project.", file=sys.stderr)
        sys.exit(1)

    if args.state is None:
        print("No state management files generated. Pass --state <lib> to scaffold a state layer.")

    for feature in args.features:
        create_feature(feature, args.state)


if __name__ == "__main__":
    main()
```

### Verifying the entry point after install
```bash
# Source: standard pip editable install workflow [ASSUMED]
pip3 install -e ".[dev]"
which fclean        # Should print a path in your Python bin
fclean --help       # Should show argparse help
fclean --features auth --state bloc  # Regression test from PKG-03
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `setup.py` + `setup.cfg` | `pyproject.toml` only | PEP 517/518 (2017), PEP 621 (2021), widely adopted 2023+ | No `setup.py` needed; hatchling reads all metadata from `pyproject.toml` |
| `pytest-tmpdir` / `tmpdir` fixture | `tmp_path` built-in fixture | pytest 3.9 (2019) | `tmpdir` is deprecated; `tmp_path` is a `pathlib.Path` object with automatic cleanup |
| `sys.path.insert(0, ".")` in tests | `pip install -e .` + proper package | Editable installs standardized in PEP 660 (2021) | No test-specific path hacks; imports work identically to production installs |
| Manual `__init__.py` listing packages | Hatchling auto-discovery | Hatchling >=1.0 | All subdirectories with `__init__.py` are automatically included in the wheel |

**Deprecated/outdated:**
- `setup.py`: Do not create one. Hatchling reads everything from `pyproject.toml`.
- `MANIFEST.in`: Not needed with hatchling; it respects `.gitignore` automatically.
- `pytest-tmp-path` (the package): Does not exist. The fixture is built in.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `fclean/__init__.py` re-export pattern will keep existing test `from fclean import ...` statements syntactically unchanged | Architecture Patterns, Pattern 1 | Low — if wrong, test import lines need updating to use submodule paths directly (simple mechanical fix) |
| A2 | `is_flutter_project()` should live in `fclean/generators/feature.py` alongside `create_feature()` | Architecture Patterns | Low — could also live in `cli.py`; either location works; this is a style decision |
| A3 | The `pyproject.toml` version should start at `0.1.0` | Code Examples | Low — version number is arbitrary at this stage; any valid semver works |

**No assumptions with HIGH risk.** All critical claims (build system API, pytest fixture availability, package non-existence of pytest-tmp-path) are verified against official documentation.

---

## Open Questions

1. **Should `__init__.py` expose the entire current public API, or only the minimal surface?**
   - What we know: The three test files import `to_pascal_case`, `validate_name`, `create_feature`, `get_bloc_templates`, `get_riverpod_templates` from `fclean`
   - What's unclear: Whether future phases will want to import directly from submodules instead
   - Recommendation: Re-export everything the tests currently use; add more only as needed. This is the minimum change to keep PKG-03 green.

2. **`fclean.py` deletion: same commit as package creation, or a separate task?**
   - What we know: They cannot coexist safely; Python prefers the directory
   - Recommendation: Delete in the same task as creating `fclean/__init__.py`. The plan should structure this as a single atomic action.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | Package runtime | Yes | 3.14.5 | — |
| pip3 | `pip install -e .` | Yes | 26.1.1 | — |
| pytest | Test runner | Yes (installed) | 9.0.3 | — |
| hatchling | Build backend (auto-fetched by pip) | Not pre-installed | Latest fetched on demand | setuptools (widely available) |

**Missing dependencies with no fallback:** None — all blocking dependencies are present.

**Missing dependencies with fallback:** hatchling is not pre-installed but pip automatically fetches `[build-system].requires` in an isolated environment during `pip install`, so no manual install step is needed.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | None currently — will be embedded in `pyproject.toml` under `[tool.pytest.ini_options]` |
| Quick run command | `python3 -m pytest` |
| Full suite command | `python3 -m pytest -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PKG-01 | Package imports resolve from `fclean.*` submodules | smoke | `python3 -c "from fclean.cli import main; from fclean.generators.feature import create_feature; from fclean.generators.validator import to_pascal_case; print('OK')"` | No — Wave 0 |
| PKG-02 | `fclean` entry point is on PATH after install | smoke | `which fclean && fclean --help` | No — Wave 0 (manual verify) |
| PKG-03 | Existing 12 tests still pass | regression | `python3 -m pytest` | Yes (tests already exist) |

### Sampling Rate
- **Per task commit:** `python3 -m pytest`
- **Per wave merge:** `python3 -m pytest -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `pyproject.toml` — must exist before `pip install -e .` is possible
- [ ] `fclean/__init__.py` — must exist before any import tests can run
- [ ] `pip3 install -e ".[dev]"` must be run once after `pyproject.toml` is created

*(Existing 12 tests in `tests/` cover PKG-03 regression; no new test files are required for this phase.)*

---

## Security Domain

**Applicable ASVS Categories:** This phase makes no network calls, handles no user authentication, performs no cryptography, and processes no external data beyond CLI arguments already validated in Phase 1. Security review is not applicable to a pure packaging/restructure phase.

---

## Sources

### Primary (HIGH confidence)
- [packaging.python.org — Writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) — `[build-system]`, `[project]`, `[project.scripts]` schema
- [packaging.python.org — src vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) — layout tradeoffs
- [docs.pytest.org — tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html) — confirms built-in fixture, no external package needed
- [docs.pytest.org — import mechanisms](https://docs.pytest.org/en/stable/explanation/pythonpath.html) — editable install approach for test imports

### Secondary (MEDIUM confidence)
- PyPI package data (via `pip3 index versions` and PyPI JSON API) — versions for setuptools 82.0.1, hatchling 1.30.1, pytest 9.0.3
- slopcheck scan — all three packages rated [OK]

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — packages verified via PyPI; docs confirmed via official PyPA site
- Architecture: HIGH — split pattern follows directly from existing code structure
- Pitfalls: HIGH — all pitfalls are verifiable from code inspection and official docs
- `pytest-tmp-path` non-existence: HIGH — `pip3 index versions pytest-tmp-path` returned ERROR; official pytest docs confirm tmp_path is built-in

**Research date:** 2026-06-03
**Valid until:** 2026-09-03 (stable domain — Python packaging spec changes slowly)
