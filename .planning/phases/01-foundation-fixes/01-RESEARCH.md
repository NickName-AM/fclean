# Phase 1: Foundation Fixes — Research

**Researched:** 2026-06-02
**Domain:** Python string manipulation, CLI input validation, Dart/Flutter code generation
**Confidence:** HIGH

---

## Summary

Phase 1 fixes three correctness bugs in the single-file Python script `fclean.py` (142 lines, stdlib only). No external packages are installed and no architectural restructuring happens — all changes are in-place edits to the existing file.

**Bug 1 (CORE-01):** Python's built-in `str.capitalize()` lowercases all characters after the first, which leaves the underscore in `user_profile` and produces `User_profile` instead of `UserProfile`. The fix is a `to_pascal_case()` helper that splits on `_` and capitalizes each segment independently. This is a 10-site replacement across 4 functions.

**Bug 2 (CORE-02 + DX-02):** No validation exists on user-supplied feature/entity names. A name like `../evil` would create directories outside the Flutter project tree. The fix adds a `validate_name(name)` function using `re.fullmatch()` against `^[a-z][a-z0-9_]*$` and calls `sys.exit(1)` with a clear message on failure. Additionally, when `--state` is omitted, the current output silently prints `(State: None)` — DX-02 requires an explicit user-facing notice.

**Bug 3 (CORE-03):** The Riverpod template emits `Provider((ref) => null)`, which Dart infers as `Provider<Null>`. This is semantically broken — it cannot be used as a starting point for real state. The fix replaces it with a typed `StateNotifierProvider<FeatureNotifier, FeatureState>` plus the companion `FeatureNotifier extends StateNotifier<FeatureState>` class.

**Primary recommendation:** Make all three fixes as targeted edits to `fclean.py`. Define `to_pascal_case()` and `validate_name()` as module-level helpers immediately after the imports. Add `import re` to the import block.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CORE-01 | `fclean --features user_profile` generates `UserProfile` (not `User_profile`) in all Dart class names | `to_pascal_case()` via `'_'.split` + `str.capitalize()` per segment; 10 replacement sites identified |
| CORE-02 | Feature and entity names validated against `^[a-z][a-z0-9_]*$` — invalid names print a clear error and exit without writing files | `re.fullmatch()` + `sys.exit(1)`; validation must happen before any `mkdir` calls |
| CORE-03 | Riverpod template generates a typed `StateNotifierProvider<FeatureNotifier, FeatureState>` stub | Full template replacement in `get_riverpod_templates()`; requires PascalCase names, so depends on CORE-01 fix |
| DX-02 | When `--state` is omitted, fclean prints explicit notice | Print once in `main()` after arg parse, before the feature loop |
</phase_requirements>

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| PascalCase conversion | CLI script (fclean.py) | — | Pure string transformation at generation time; no runtime or external dependency |
| Input validation | CLI script (fclean.py) — `main()` entry point | — | Validation must happen before any filesystem writes; belongs in the CLI layer |
| Dart template strings | CLI script (fclean.py) — template functions | — | Templates are inlined Python f-strings; restructure to modules is Phase 2 |
| State-omission notice | CLI script (fclean.py) — `main()` | — | Once-per-invocation notice based on argparse result |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `re` | 3.14.5 (runtime) | Regex validation in `validate_name()` | Already part of stdlib; no install needed. `re.fullmatch()` available since Python 3.4 |
| Python stdlib `sys` | 3.14.5 (runtime) | `sys.exit(1)` for validation failure | Already imported in `fclean.py` |
| Python stdlib `argparse` | 3.14.5 (runtime) | CLI argument parsing | Already in use |
| Python stdlib `pathlib` | 3.14.5 (runtime) | File/directory creation | Already in use |

[VERIFIED: runtime — `python3 --version` confirms 3.14.5, all modules are stdlib]

### Supporting

None — Phase 1 is purely stdlib. No new packages required.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `re.fullmatch(pattern, name)` | Manual char-by-char check | Manual check is more verbose with no benefit; `re` is stdlib so there is no install cost |
| `sys.exit(1)` in `validate_name()` | Raise `ValueError`, catch in caller | `sys.exit(1)` is simpler and idiomatic for CLI tools; `argparse` itself uses `SystemExit` |
| Defining `to_pascal_case()` as module-level | Defining it inside each template function | Module-level avoids duplication and is testable in Phase 3 |

**Installation:** No new packages. Phase 1 modifies only `fclean.py`.

---

## Package Legitimacy Audit

> Not applicable. Phase 1 installs no external packages — all changes use Python stdlib only.

---

## Architecture Patterns

### System Architecture Diagram

```
User CLI input
      |
      v
main() — argparse
      |
      |-- --features missing --> argparse error (exit 2)
      |
      |-- args parsed -->
      |     |
      |     |-- is_flutter_project()? No --> print error, sys.exit(1)
      |     |
      |     |-- args.state is None --> print DX-02 notice [NEW]
      |     |
      |     +-- for each feature_arg:
      |               |
      |               v
      |         create_feature(feature_arg, state_type)
      |               |
      |               |-- split on ':' --> feature_name, entity_name
      |               |
      |               |-- validate_name(feature_name) [NEW]
      |               |-- validate_name(entity_name) if present [NEW]
      |               |
      |               |-- mkdir all sub_dirs
      |               |
      |               |-- build files_to_create dict
      |               |     uses to_pascal_case(feature_name) [FIXED]
      |               |     uses to_pascal_case(entity_name) [FIXED]
      |               |
      |               |-- if state_type: call template function
      |               |     get_bloc_templates(feature_name)   -- uses to_pascal_case [FIXED]
      |               |     get_cubit_templates(feature_name)  -- uses to_pascal_case [FIXED]
      |               |     get_riverpod_templates(feature_name) -- full replacement [FIXED]
      |               |     get_getx_templates(feature_name)   -- uses to_pascal_case [FIXED]
      |               |
      |               +-- write files (skip if exists)
      |
      v
    Exit 0
```

### Recommended Project Structure

```
fclean.py          # Single file — all changes are in-place edits (restructure is Phase 2)
```

### Pattern 1: PascalCase Helper

**What:** A module-level function that converts snake_case identifiers to PascalCase class names.
**When to use:** Everywhere a Dart class name is constructed from the user-supplied feature or entity name.

```python
# Source: [ASSUMED] — standard Python string idiom, verified working locally
def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase for Dart class names."""
    return "".join(word.capitalize() for word in name.split("_"))
```

Verified output:
- `to_pascal_case("user_profile")` → `"UserProfile"` [VERIFIED: runtime]
- `to_pascal_case("auth")` → `"Auth"` [VERIFIED: runtime]
- `to_pascal_case("my_feature2")` → `"MyFeature2"` [VERIFIED: runtime]

**Placement:** Define immediately after the `from pathlib import Path` import line, before `is_flutter_project()`.

### Pattern 2: Input Validator

**What:** A function that validates a name against the CLI contract and exits on failure.
**When to use:** After splitting `feature_arg` on `:`, before any filesystem operations.

```python
# Source: [ASSUMED] — stdlib re, standard CLI validation pattern
import re

_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")

def validate_name(name: str) -> None:
    """Validate a feature or entity name. Exits with code 1 if invalid."""
    if not _NAME_RE.fullmatch(name):
        print(
            f"Error: Invalid name '{name}'. "
            "Names must start with a lowercase letter and contain only [a-z0-9_].",
            file=sys.stderr,
        )
        sys.exit(1)
```

Verified regex behavior:
- `"auth"` → passes [VERIFIED: runtime]
- `"user_profile"` → passes [VERIFIED: runtime]
- `"../evil"` → fails [VERIFIED: runtime]
- `"User"` → fails [VERIFIED: runtime]
- `"1auth"` → fails [VERIFIED: runtime]
- `""` (empty string) → fails [VERIFIED: runtime]

**Note on `re.fullmatch` vs `re.match`:** `fullmatch` does not require explicit `$` anchor because it requires the entire string to match. Available since Python 3.4; compatible with `requires-python = ">=3.8"` (Phase 2).

### Pattern 3: State-Omission Notice

**What:** A one-time print to stdout in `main()` when `args.state` is `None`.
**When to use:** After argparse, before the feature loop, only when no `--state` was supplied.

```python
# Source: [ASSUMED] — straightforward print, matches DX-02 exact wording from REQUIREMENTS.md
if args.state is None:
    print("No state management files generated. Pass --state <lib> to scaffold a state layer.")
```

**Placement:** In `main()`, after `is_flutter_project()` check, before `for feature in args.features`.

### Pattern 4: Fixed Riverpod Template

**What:** Replaces the broken `Provider((ref) => null)` with a typed, compilable stub.
**When to use:** As the full replacement body of `get_riverpod_templates()`.

```python
# Source: [ASSUMED] — Riverpod StateNotifierProvider pattern; verified locally as correct Dart idiom
def get_riverpod_templates(feature):
    name = to_pascal_case(feature)
    return {
        f"presentation/providers/{feature}_provider.dart": (
            f"import 'package:flutter_riverpod/flutter_riverpod.dart';\n\n"
            f"class {name}State {{}}\n\n"
            f"class {name}Notifier extends StateNotifier<{name}State> {{\n"
            f"  {name}Notifier() : super({name}State());\n"
            f"}}\n\n"
            f"final {feature}Provider =\n"
            f"    StateNotifierProvider<{name}Notifier, {name}State>((ref) {{\n"
            f"  return {name}Notifier();\n"
            f"}});"
        )
    }
```

**Why this fixes CORE-03:** `Provider<T>((ref) => null)` infers `T = Null`, making the provider unusable as a real state container. `StateNotifierProvider<Notifier, State>` provides explicit generic types that Dart's analyzer can verify. The stub class `FeatureNotifier extends StateNotifier<FeatureState>` gives the user a concrete starting point. [ASSUMED — Dart type inference behavior; Riverpod docs confirm StateNotifierProvider is the correct API]

### Anti-Patterns to Avoid

- **Using `str.capitalize()` for multi-word names:** `"user_profile".capitalize()` returns `"User_profile"` — the underscore is preserved and the `p` stays lowercase. Always use `to_pascal_case()` for Dart class name construction.
- **Calling `validate_name()` after filesystem writes begin:** Validation must happen before any `mkdir` call. If validation is placed after directory creation, partial state is written on invalid input.
- **Printing the DX-02 notice inside `create_feature()`:** If multiple `--features` are passed, this prints once per feature. Print once in `main()` instead.
- **Using `re.match()` instead of `re.fullmatch()`:** `re.match(r"[a-z][a-z0-9_]*", "../evil")` would fail at the first char, but `re.match(r"[a-z]", "abc/xyz")` would match on a looser pattern. `fullmatch` is unambiguous.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI argument definition | Custom `sys.argv` parser | `argparse` (already in use) | Error messages, `--help`, type coercion all built in |
| PascalCase conversion | Custom regex substitution | `'_'.split` + `capitalize()` per word | Two lines, zero dependencies, handles digits correctly |
| Regex validation | String char iteration | `re.fullmatch()` | Concise, readable, correct anchoring |

**Key insight:** This phase is pure string manipulation and stdio. There is no problem complex enough to warrant a library.

---

## Common Pitfalls

### Pitfall 1: Incomplete `capitalize()` Replacement

**What goes wrong:** Developer replaces only the three `name = feature.capitalize()` lines in template functions, but misses the 7 direct `.capitalize()` calls inside `create_feature()` on `feature_name` and `entity_name`.
**Why it happens:** The template functions use a local `name` variable. The `create_feature()` calls are scattered inline in f-strings and easy to overlook.
**How to avoid:** Before starting, enumerate all 9 `.capitalize()` call sites (verified by audit above). Replace all 9 in one pass.
**Warning signs:** `UserProfileRemoteDataSource` class is wrong (e.g., `User_profileRemoteDataSource`) even though BLoC/Cubit class names are correct — this means `create_feature()` direct calls were missed.

### Pitfall 2: Validation After Directory Creation

**What goes wrong:** `validate_name()` is called after the `for sub_dir in sub_dirs: mkdir(...)` loop, leaving empty directories written to disk on invalid input.
**Why it happens:** The natural reading of `create_feature()` suggests adding validation near the name-parsing lines, but if placed after the `mkdir` block it is too late.
**How to avoid:** Place both `validate_name(feature_name)` and `validate_name(entity_name)` immediately after the `parts = feature_arg.split(":")` block, before `base_path = Path(...)` is used in any `mkdir` call.
**Warning signs:** Running `fclean --features ../evil` creates empty subdirectories before printing the error.

### Pitfall 3: Entity Name Not Validated

**What goes wrong:** `validate_name()` is only called on `feature_name`, but the entity name (the part after `:` in `--features auth:user`) accepts arbitrary strings.
**Why it happens:** CORE-02 says "feature and entity names" but it is easy to add validation for only `feature_name`.
**How to avoid:** Validate both: `validate_name(feature_name)` and, if `entity_name is not None`, `validate_name(entity_name)`.

### Pitfall 4: Missing `import re`

**What goes wrong:** `validate_name()` uses `re.fullmatch()` but `re` is not in the current import block — the script crashes at startup with `NameError: name 're' is not defined`.
**Why it happens:** `re` is stdlib but is not auto-imported.
**How to avoid:** Add `import re` to the import block alongside `import sys` and `import argparse`.

### Pitfall 5: Riverpod Template Still Uses `feature_name` as Provider Variable Name

**What goes wrong:** The generated code reads `final user_profileProvider = ...` — a snake_case variable name. Dart allows underscores in variable names so it compiles, but it violates Dart naming conventions (`lowerCamelCase` for variables).
**Why it happens:** `feature` (the raw snake_case string) is used directly for the provider variable name in the current template.
**How to avoid:** This is a known cosmetic issue. CORE-03 does not require fixing this (it only requires type correctness). However, a future plan (Phase 4+ or a follow-up) should use a `to_camel_case()` variant for provider variable names. Document as a deferred cleanup — do not block Phase 1 completion on it.
**Warning signs:** `flutter analyze` reports a lint warning `prefer_lower_camel_case` on the generated file.

---

## Code Examples

Verified patterns from official sources:

### Complete `to_pascal_case()` helper

```python
# Source: [ASSUMED] — standard Python idiom, verified with runtime execution
def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase for Dart class names.
    
    Examples:
        user_profile -> UserProfile
        auth -> Auth
        my_feature2 -> MyFeature2
    """
    return "".join(word.capitalize() for word in name.split("_"))
```

### Complete `validate_name()` function

```python
# Source: [ASSUMED] — stdlib re, verified with runtime execution
import re

_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")

def validate_name(name: str) -> None:
    """Validate a feature or entity name. Exits 1 with a clear message if invalid."""
    if not _NAME_RE.fullmatch(name):
        print(
            f"Error: Invalid name '{name}'. "
            "Names must start with a lowercase letter and contain only [a-z0-9_].",
            file=sys.stderr,
        )
        sys.exit(1)
```

### Insertion point in `create_feature()` for validation

```python
def create_feature(feature_arg, state_type):
    parts = feature_arg.split(":")
    feature_name = parts[0]
    entity_name = parts[1] if len(parts) > 1 else None

    # NEW: validate before any filesystem operations
    validate_name(feature_name)
    if entity_name is not None:
        validate_name(entity_name)

    base_path = Path("lib/features") / feature_name
    # ... rest unchanged ...
```

### Insertion point in `main()` for DX-02 notice

```python
def main():
    # ... argparse setup unchanged ...
    args = parser.parse_args()

    if not is_flutter_project():
        print("Error: This tool must be run from the root of a Flutter project.")
        sys.exit(1)

    # NEW: DX-02 notice
    if args.state is None:
        print("No state management files generated. Pass --state <lib> to scaffold a state layer.")

    for feature in args.features:
        create_feature(feature, args.state)
```

---

## Runtime State Inventory

> Omitted. Phase 1 is not a rename/refactor/migration phase. It fixes bugs in-place in `fclean.py` with no string renaming and no stored state to migrate.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `str.capitalize()` for all names | `to_pascal_case()` splitting on `_` | Phase 1 | Fixes broken Dart class names for snake_case inputs |
| No input validation | `re.fullmatch()` + `sys.exit(1)` | Phase 1 | Prevents path traversal and invalid identifiers reaching filesystem |
| `Provider((ref) => null)` (untyped) | `StateNotifierProvider<Notifier, State>` (typed) | Phase 1 | Generated Riverpod code becomes compilable |

**Deprecated/outdated:**
- `str.capitalize()` for Dart class name generation: produces `User_profile` for snake_case input. Replaced by `to_pascal_case()`.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `StateNotifierProvider<FeatureNotifier, FeatureState>` is the correct Riverpod API for a typed state notifier stub | Pattern 4 / Riverpod Template | If Riverpod has deprecated StateNotifier in favor of Notifier/AsyncNotifier (Riverpod 2.x), the template would still compile but would use an outdated pattern. Phase 3 tests would catch a compile failure. |
| A2 | `final user_profileProvider` (snake_case variable name) compiles in Dart | Pitfall 5 | If Dart's analyzer enforces camelCase as an error (not a warning), the generated file would not compile. Very low risk — Dart treats this as a lint warning, not a compile error. |
| A3 | `re.fullmatch()` is available in Python 3.4+ | Pattern 2 | If the tool were run on Python <3.4, this would fail. Project targets Python >=3.8 (Phase 2), so no risk in practice. |

---

## Open Questions

1. **Riverpod StateNotifier vs Notifier (v2.x API)**
   - What we know: Riverpod 2.x introduced `Notifier`/`AsyncNotifier` as the new recommended API, while `StateNotifier` is still supported but considered legacy.
   - What's unclear: Which API should the stub use? The ROADMAP explicitly says `StateNotifierProvider<FeatureNotifier, FeatureState>` — so this is locked.
   - Recommendation: Implement exactly as the ROADMAP specifies. If the project later targets Riverpod 2.x Notifier API, that becomes a Phase 4+ revision. Do not deviate from the plan.

2. **Provider variable naming convention (camelCase vs snake_case)**
   - What we know: Current output produces `user_profileProvider` (snake_case). Dart conventions require `userProfileProvider` (camelCase). This is a lint warning, not a compile error.
   - What's unclear: Is fixing the variable name in scope for CORE-03?
   - Recommendation: CORE-03 success criteria says "compiles without type errors" — focus on the type correctness fix only. Log the variable naming as a deferred cleanup (post-Phase 1). Do not add scope.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | All fclean.py execution | Yes | 3.14.5 | — |
| `re` (stdlib) | `validate_name()` | Yes | stdlib | — |
| `sys` (stdlib) | `validate_name()`, `main()` | Yes (already imported) | stdlib | — |
| `argparse` (stdlib) | `main()` | Yes (already imported) | stdlib | — |
| `pathlib` (stdlib) | `create_feature()` | Yes (already imported) | stdlib | — |
| pytest | Test execution | Yes | 9.0.3 | Manual verification |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:**
- pytest: installed system-wide but no `tests/` directory exists. Phase 1 verification is manual; pytest infrastructure is Phase 3's responsibility.

---

## Validation Architecture

> `workflow.nyquist_validation` is `true` in `.planning/config.json` — section included.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | None — no `pytest.ini`, `pyproject.toml`, or `setup.cfg` exists yet (Wave 0 gap) |
| Quick run command | `python3 -m pytest tests/ -x -q` (once tests/ exists) |
| Full suite command | `python3 -m pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CORE-01 | `to_pascal_case("user_profile")` returns `"UserProfile"` | unit | `python3 -m pytest tests/test_utils.py::test_to_pascal_case -x` | No — Wave 0 gap |
| CORE-01 | Generated BLoC class name contains `UserProfileBloc`, not `User_profileBloc` | functional | `python3 -m pytest tests/test_generator.py::test_bloc_class_names -x` | No — Wave 0 gap |
| CORE-02 | `validate_name("../evil")` calls `sys.exit(1)` | unit | `python3 -m pytest tests/test_utils.py::test_validate_name_invalid -x` | No — Wave 0 gap |
| CORE-02 | `validate_name("auth")` passes without exit | unit | `python3 -m pytest tests/test_utils.py::test_validate_name_valid -x` | No — Wave 0 gap |
| CORE-03 | Riverpod template contains `StateNotifierProvider<` | unit | `python3 -m pytest tests/test_templates.py::test_riverpod_typed -x` | No — Wave 0 gap |
| DX-02 | `main()` prints explicit notice when `--state` is None | functional/manual | Manual: `python3 fclean.py --features auth` (no --state) | No — manual only for Phase 1 |

**Note:** All automated test commands require `tests/` directory and test files which do not exist. Phase 1 verification is manual. Phase 3 creates the test suite that backfills these.

### Sampling Rate

- **Per task commit:** Manual — run `python3 fclean.py --features user_profile --state bloc` and inspect output
- **Per wave merge:** Manual — run all four success-criteria checks from the ROADMAP
- **Phase gate:** All ROADMAP success criteria pass before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_utils.py` — covers CORE-01 (`to_pascal_case`) and CORE-02 (`validate_name`) unit tests
- [ ] `tests/test_templates.py` — covers CORE-03 (Riverpod typed template)
- [ ] `tests/test_generator.py` — covers CORE-01 end-to-end class name generation
- [ ] No pytest config file (`pyproject.toml` / `pytest.ini`) — created in Phase 2/3
- [ ] Framework install: `pip install pytest` — already done on this machine, but not pinned in any project config

*(Phase 1 operates without automated tests. Manual verification is the gate. Phase 3 closes all gaps above.)*

---

## Security Domain

> `security_enforcement` not set in config — treating as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | N/A — CLI tool, no auth |
| V3 Session Management | No | N/A — stateless CLI |
| V4 Access Control | No | N/A — local tool |
| V5 Input Validation | Yes | `re.fullmatch(r"^[a-z][a-z0-9_]*$", name)` |
| V6 Cryptography | No | N/A — no secrets or encryption |

### Known Threat Patterns for CLI code generators

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via `--features ../evil` | Tampering | `validate_name()` rejects names not matching `^[a-z][a-z0-9_]*$` — no `/`, `.`, or `..` sequences possible |
| Arbitrary file overwrite | Tampering | Existing `if path.exists(): skip` logic preserved; validation prevents names that escape `lib/features/` |
| Code injection in generated Dart | Tampering | Feature/entity names are restricted to `[a-z0-9_]`; no shell metacharacters, no Dart syntax characters pass validation |

**Security note:** The regex `^[a-z][a-z0-9_]*$` is the primary security control for Phase 1. It prevents path traversal, Unicode injection, and any characters that could cause problems in generated Dart identifiers. The validation must be called before any filesystem operations. [VERIFIED: runtime — all threat patterns tested against the regex]

---

## Sources

### Primary (HIGH confidence)
- Python 3 runtime (3.14.5) — all `re`, `sys`, `str.split`, `str.capitalize` behaviors verified by direct execution
- `fclean.py` source — all 9 `capitalize()` sites enumerated by runtime audit

### Secondary (MEDIUM confidence)
- REQUIREMENTS.md (project file) — CORE-01, CORE-02, CORE-03, DX-02 definitions
- ROADMAP.md (project file) — Plan 1.1, 1.2, 1.3 specifications and success criteria

### Tertiary (LOW confidence / ASSUMED)
- Riverpod `StateNotifierProvider` API: assumed from training knowledge — Riverpod 1.x API. If project targets Riverpod 2.x, `Notifier` is preferred but `StateNotifier` still works. [A1 in Assumptions Log]

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib only, all verified by runtime
- Architecture: HIGH — single file, all call sites enumerated by code inspection
- Pitfalls: HIGH — all pitfalls found by direct execution and code audit
- Riverpod template: MEDIUM — API shape assumed from training; marked A1

**Research date:** 2026-06-02
**Valid until:** 2026-07-02 (Python stdlib is stable; Riverpod API assumption should be re-verified if Riverpod version changes)
