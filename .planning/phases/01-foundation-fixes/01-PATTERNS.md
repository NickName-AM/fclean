# Phase 1: Foundation Fixes - Pattern Map

**Mapped:** 2026-06-02
**Files analyzed:** 2 (1 modified, 1 directory to create)
**Analogs found:** 2 / 2 (both from `fclean.py` itself — it is the only source file)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `fclean.py` (MODIFY) | utility + CLI script | transform (string) + request-response (CLI) | `fclean.py` itself | exact — in-place edits |
| `tests/` (CREATE stubs) | test | batch (unit assertions) | None — no test files exist | no analog |

---

## Pattern Assignments

### `fclean.py` — `to_pascal_case()` helper (CORE-01)

**Analog:** `fclean.py` itself — the existing template functions show the module-level helper placement convention.

**Existing import block** (lines 1-3):
```python
import sys
import argparse
from pathlib import Path
```

**Required addition — add `import re` to this block** (insert after line 1):
```python
import sys
import re
import argparse
from pathlib import Path
```

**Insertion point** — after imports, before `is_flutter_project()` (line 5). The new helpers occupy lines 5-20 in the modified file:

**`to_pascal_case()` pattern** (new, no analog — place at line 5):
```python
def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase for Dart class names.

    Examples:
        user_profile -> UserProfile
        auth -> Auth
        my_feature2 -> MyFeature2
    """
    return "".join(word.capitalize() for word in name.split("_"))
```

**All 9 `.capitalize()` call sites to replace** — enumerated by audit of `fclean.py`:

| Line | Current code | Replacement |
|------|-------------|-------------|
| 10 | `name = feature.capitalize()` | `name = to_pascal_case(feature)` |
| 31 | `name = feature.capitalize()` | `name = to_pascal_case(feature)` |
| 54 | `name = feature.capitalize()` | `name = to_pascal_case(feature)` |
| 89 | `f"abstract class {feature_name.capitalize()}RemoteDataSource {{}}"` | `f"abstract class {to_pascal_case(feature_name)}RemoteDataSource {{}}"` |
| 90 | `f"abstract class {feature_name.capitalize()}LocalDataSource {{}}"` | `f"abstract class {to_pascal_case(feature_name)}LocalDataSource {{}}"` |
| 93 | `f"class {feature_name.capitalize()}RepositoryImpl..."` | `f"class {to_pascal_case(feature_name)}RepositoryImpl..."` |
| 94 | `f"...{feature_name.capitalize()}Repository {{}}"` | `f"...{to_pascal_case(feature_name)}Repository {{}}"` |
| 96 | `f"abstract class {feature_name.capitalize()}Repository {{}}"` | `f"abstract class {to_pascal_case(feature_name)}Repository {{}}"` |
| 101 | `f"class {entity_name.capitalize()} {{}}"` | `f"class {to_pascal_case(entity_name)} {{}}"` |
| 103-104 | `{entity_name.capitalize()}Model ... {entity_name.capitalize()}` | `{to_pascal_case(entity_name)}Model ... {to_pascal_case(entity_name)}` |

Note: lines 103-104 contain 2 `.capitalize()` calls on `entity_name` — both must be replaced, bringing the total to 10 replacement sites (research says 10, code audit confirms 10 across the two inline f-strings).

---

### `fclean.py` — `validate_name()` + DX-02 notice (CORE-02, DX-02)

**Analog:** Existing `is_flutter_project()` guard pattern (lines 134-136) — same shape: a precondition check that calls `sys.exit(1)` with a message.

**Existing guard pattern to copy structure from** (lines 134-136):
```python
if not is_flutter_project():
    print("Error: This tool must be run from the root of a Flutter project.")
    sys.exit(1)
```

**Module-level compiled regex** — place immediately after `to_pascal_case()`, before `is_flutter_project()`:
```python
_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
```

**`validate_name()` pattern** — place after `_NAME_RE`, before `is_flutter_project()`:
```python
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

**Insertion point in `create_feature()`** — after the `parts = feature_arg.split(":")` block (currently lines 72-74), before `base_path = Path(...)` (currently line 76). This is the only correct placement — validation must precede all `mkdir` calls:
```python
def create_feature(feature_arg, state_type):
    parts = feature_arg.split(":")
    feature_name = parts[0]
    entity_name = parts[1] if len(parts) > 1 else None

    # Validate before any filesystem operations
    validate_name(feature_name)
    if entity_name is not None:
        validate_name(entity_name)

    base_path = Path("lib/features") / feature_name
    # ... rest unchanged
```

**DX-02 notice insertion point in `main()`** — after the `is_flutter_project()` guard (currently line 136), before the `for feature in args.features` loop (currently line 138):
```python
    if not is_flutter_project():
        print("Error: This tool must be run from the root of a Flutter project.")
        sys.exit(1)

    # DX-02: explicit notice when no state management requested
    if args.state is None:
        print("No state management files generated. Pass --state <lib> to scaffold a state layer.")

    for feature in args.features:
        create_feature(feature, args.state)
```

---

### `fclean.py` — `get_riverpod_templates()` replacement (CORE-03)

**Analog:** `get_bloc_templates()` (lines 9-28) — same function signature, same `name = to_pascal_case(feature)` local, same f-string dict return shape.

**Existing `get_bloc_templates()` as structural model** (lines 9-28):
```python
def get_bloc_templates(feature):
    name = feature.capitalize()       # <- becomes to_pascal_case(feature) after CORE-01
    return {
        f"presentation/bloc/{feature}_event.dart": f"abstract class {name}Event {{}}",
        ...
    }
```

**Full replacement body for `get_riverpod_templates()`** (currently lines 45-51):
```python
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

Note: `{feature}Provider` (snake_case variable name) is a known cosmetic issue per RESEARCH.md Pitfall 5 — it compiles but triggers `prefer_lower_camel_case` lint. Deferred to Phase 4+. Do not add scope to fix this in Phase 1.

---

### `tests/` directory — Wave 0 stub files (CREATE)

**Analog:** None — no test files exist in the project.

**Pattern source:** RESEARCH.md Validation Architecture section (lines 436-443) defines the exact file names and test function names required. Use these as the structural contract.

**Files to create:**

`tests/test_utils.py` — unit tests for `to_pascal_case()` and `validate_name()`:
```python
import sys
import pytest
sys.path.insert(0, ".")
from fclean import to_pascal_case, validate_name  # NOTE: adjust import path after Phase 2 restructure


def test_to_pascal_case_single_word():
    assert to_pascal_case("auth") == "Auth"


def test_to_pascal_case_snake():
    assert to_pascal_case("user_profile") == "UserProfile"


def test_to_pascal_case_with_digit():
    assert to_pascal_case("my_feature2") == "MyFeature2"


def test_validate_name_valid_passes():
    validate_name("auth")        # must not raise
    validate_name("user_profile")


def test_validate_name_invalid_exits():
    with pytest.raises(SystemExit) as exc_info:
        validate_name("../evil")
    assert exc_info.value.code == 1


def test_validate_name_uppercase_exits():
    with pytest.raises(SystemExit):
        validate_name("User")


def test_validate_name_leading_digit_exits():
    with pytest.raises(SystemExit):
        validate_name("1auth")


def test_validate_name_empty_exits():
    with pytest.raises(SystemExit):
        validate_name("")
```

`tests/test_templates.py` — unit tests for Riverpod typed template (CORE-03):
```python
import sys
sys.path.insert(0, ".")
from fclean import get_riverpod_templates


def test_riverpod_typed():
    templates = get_riverpod_templates("user_profile")
    content = list(templates.values())[0]
    assert "StateNotifierProvider<" in content
    assert "UserProfileNotifier" in content
    assert "UserProfileState" in content
    assert "Provider((ref) => null)" not in content
```

`tests/test_generator.py` — functional tests for class name generation (CORE-01 end-to-end):
```python
import sys
sys.path.insert(0, ".")
from fclean import get_bloc_templates


def test_bloc_class_names():
    templates = get_bloc_templates("user_profile")
    all_content = " ".join(templates.values())
    assert "UserProfileBloc" in all_content
    assert "UserProfileEvent" in all_content
    assert "UserProfileState" in all_content
    assert "User_profileBloc" not in all_content
```

**Import note for Phase 1:** `fclean.py` is a script, not a package — `from fclean import ...` requires that the helpers (`to_pascal_case`, `validate_name`, `get_bloc_templates`, `get_riverpod_templates`) are importable at module level. They are already module-level functions in `fclean.py`, so `sys.path.insert(0, ".")` + import by filename works for Phase 1. Phase 2 restructure changes these imports; stubs should use a comment to that effect.

---

## Shared Patterns

### Guard-then-exit (sys.exit(1))

**Source:** `fclean.py` lines 134-136
**Apply to:** `validate_name()` function, which copies the same pattern as the Flutter project check.

```python
if not is_flutter_project():
    print("Error: This tool must be run from the root of a Flutter project.")
    sys.exit(1)
```

The `validate_name()` function uses the same shape: check condition → `print(..., file=sys.stderr)` → `sys.exit(1)`.

### Module-level helper placement convention

**Source:** `fclean.py` lines 5-7 (`is_flutter_project()`)
**Apply to:** `to_pascal_case()`, `_NAME_RE`, `validate_name()` — all placed as module-level definitions before the template functions and `create_feature()`.

```python
def is_flutter_project():
    """Checks if the current directory contains a pubspec.yaml file."""
    return Path("pubspec.yaml").exists()
```

New helpers follow this pattern: short docstring, no class wrapper, module-level.

### Template function convention

**Source:** `fclean.py` lines 9-28 (`get_bloc_templates`)
**Apply to:** The `get_riverpod_templates()` replacement copies this exact signature and return shape.

```python
def get_bloc_templates(feature):
    name = feature.capitalize()   # becomes to_pascal_case(feature)
    return {
        f"<relative_path>": f"<dart content>"
    }
```

### pytest `SystemExit` assertion

**Source:** No existing analog — pattern from Python stdlib testing idiom.
**Apply to:** All `validate_name()` tests in `tests/test_utils.py`.

```python
with pytest.raises(SystemExit) as exc_info:
    validate_name("../evil")
assert exc_info.value.code == 1
```

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `tests/test_utils.py` | test | batch | No test files exist in the project |
| `tests/test_templates.py` | test | batch | No test files exist in the project |
| `tests/test_generator.py` | test | batch | No test files exist in the project |

These stubs are Wave 0 placeholders. Their content is fully specified in the Pattern Assignments section above. No codebase analog exists — use the RESEARCH.md Validation Architecture section as the structural contract.

---

## Metadata

**Analog search scope:** `/Users/abik/Development/projects/fclean/` — single file codebase (`fclean.py`, 142 lines)
**Files scanned:** 1 source file (`fclean.py`)
**Pattern extraction date:** 2026-06-02

**Key constraint:** Because the entire codebase is one file, all patterns for `fclean.py` modifications are extracted from that same file. The self-referential analog is exact — the planner should treat the existing function shapes, naming conventions, and import block as the authoritative patterns to extend (not replace).
