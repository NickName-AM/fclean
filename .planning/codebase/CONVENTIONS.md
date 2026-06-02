# Coding Conventions

**Analysis Date:** 2026-06-02

## Overview

The project is a single-file Python CLI tool: `fclean.py`. All conventions are observed from this one file. There are no linting, formatting, or type-checking tools configured.

## Naming Patterns

**Files:**
- Snake_case: `fclean.py`
- One file per tool — no module splitting currently

**Functions:**
- Snake_case throughout: `is_flutter_project`, `get_bloc_templates`, `create_feature`, `main`
- Verb-noun pattern for actions: `create_feature`, `get_bloc_templates`
- Boolean checks prefixed with `is_`: `is_flutter_project`
- Template-getter functions follow pattern: `get_<state_type>_templates(feature)`

**Variables:**
- Snake_case: `feature_name`, `entity_name`, `base_path`, `sub_dirs`, `files_to_create`, `state_map`
- Descriptive: `parts`, `name`, `rel_path`, `content`

**Parameters:**
- Short but clear: `feature`, `feature_arg`, `state_type`
- `feature_arg` distinguishes the raw CLI input (e.g. `auth:user`) from parsed `feature_name`

**Generated Dart identifiers:**
- PascalCase for class names via `feature.capitalize()`: `AuthBloc`, `AuthEvent`
- Snake_case for filenames: `auth_bloc.dart`, `auth_event.dart`

## Code Organization Within `fclean.py`

1. Standard library imports at top (`sys`, `argparse`, `pathlib`)
2. Guard function (`is_flutter_project`) — environment validation
3. Template-getter functions grouped by state management library (bloc → cubit → riverpod → getx)
4. Core generation function (`create_feature`) — builds directory tree and writes files
5. Entry point (`main`) — CLI argument parsing and orchestration
6. `if __name__ == "__main__": main()` guard at end

## Error Handling

**Approach:** Minimal — only one explicit error path exists.

**Patterns observed:**
- Environment check exits early with `sys.exit(1)` and a printed error message: `"Error: This tool must be run from the root of a Flutter project."`
- File collision is handled silently: existing files are skipped with a `print(f"Skipping: ...")` message rather than raising an error
- No try/except blocks are present — filesystem errors (permissions, disk full) are unhandled
- No custom exception classes

**Error output:** Uses `print()` to stdout — no stderr separation or logging framework

## Docstrings and Comments

**Style:** Minimal.

- Only one function has a docstring: `is_flutter_project` — `"""Checks if the current directory contains a pubspec.yaml file."""`
- Remaining functions have no docstrings
- Inline comment used inside generated Dart output: `// TODO: implement event handler`
- No module-level docstring

**Guideline when adding functions:**
- Add a one-line docstring to any public function
- Complex logic should have inline `#` comments

## Code Style

**Formatting:**
- No formatter configured (no `.prettierrc`, `pyproject.toml`, or `ruff.toml`)
- 4-space indentation (PEP 8 compliant)
- Blank lines separate logical function groups (PEP 8 style)
- Line length appears under 100 chars

**Linting:**
- No linter configured (no `.flake8`, `.pylintrc`, `mypy.ini`, or `ruff` config)

**Type annotations:**
- None present — the codebase uses no type hints

**String style:**
- f-strings used throughout for all interpolation
- Multi-line strings use parenthesized concatenation: `f"..."\nf"..."` inside parens

## Data Structures

**Dispatch table pattern:** State type is resolved via a dict mapping strings to functions:

```python
state_map = {
    "bloc": get_bloc_templates,
    "cubit": get_cubit_templates,
    "riverpod": get_riverpod_templates,
    "getx": get_getx_templates
}
```

This pattern should be followed when adding new state management libraries — do not add `elif` chains; extend `state_map` instead.

**File manifest pattern:** Files to generate are collected into a `files_to_create` dict (`Path → str content`) before writing — enables collision-checking before any writes.

## CLI Design

- `argparse` for CLI parsing
- Required flags use `nargs="+"` for multi-value support
- Constrained choices via `choices=` on `--state`
- Feature + entity encoded in a single argument with `:` delimiter: `feature_name:entity_name`

## Patterns to Follow When Adding New Code

- Add new state library support by implementing `get_<library>_templates(feature)` returning `dict[str, str]` and registering it in `state_map` inside `create_feature`
- Place new guard/validation logic in a dedicated `is_*` function before `create_feature`
- Keep all filesystem writes going through the `files_to_create` manifest + collision-check loop
- Use `Path` (not `os.path`) for all filesystem operations
- Print user-facing messages with `print()` — keep output human-readable

---

*Convention analysis: 2026-06-02*
