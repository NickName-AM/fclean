<!-- refreshed: 2026-06-02 -->
# Architecture

**Analysis Date:** 2026-06-02

## System Overview

fclean is a single-file Python CLI tool that scaffolds Flutter Clean Architecture feature directories and boilerplate files. It runs from a Flutter project root and generates a standardized `lib/features/<name>/` tree with correct layer separation and imports.

```text
┌──────────────────────────────────────────────────┐
│              CLI Entry Point                      │
│  argparse: --features, --state  (`fclean.py:127`) │
└─────────────────────┬────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────┐
│           Validation Gate                         │
│  is_flutter_project() — checks pubspec.yaml       │
│  (`fclean.py:5`)                                  │
└─────────────────────┬────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────┐
│         Feature Scaffolding Engine                │
│  create_feature(feature_arg, state_type)          │
│  (`fclean.py:71`)                                 │
│                                                   │
│  ┌─────────────┐  ┌──────────────┐               │
│  │ Dir Creator │  │ File Writer  │               │
│  │ Path.mkdir  │  │ write_text() │               │
│  └─────────────┘  └──────────────┘               │
└─────────────────────┬────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────┐
│       State Management Template Providers         │
│  get_bloc_templates()       (`fclean.py:9`)       │
│  get_cubit_templates()      (`fclean.py:30`)      │
│  get_riverpod_templates()   (`fclean.py:45`)      │
│  get_getx_templates()       (`fclean.py:53`)      │
└──────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────┐
│       Output: Flutter Project Filesystem          │
│  lib/features/<name>/data/                        │
│  lib/features/<name>/domain/                      │
│  lib/features/<name>/presentation/               │
└──────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | Location |
|-----------|----------------|----------|
| `main()` | Parse CLI args, validate project, iterate features | `fclean.py:127` |
| `is_flutter_project()` | Guard: confirm `pubspec.yaml` exists in cwd | `fclean.py:5` |
| `create_feature()` | Orchestrate dir creation, core file writes, template injection | `fclean.py:71` |
| `get_bloc_templates()` | Return BLoC event/state/bloc file content map | `fclean.py:9` |
| `get_cubit_templates()` | Return Cubit state/cubit file content map | `fclean.py:30` |
| `get_riverpod_templates()` | Return Riverpod provider file content map | `fclean.py:45` |
| `get_getx_templates()` | Return GetX controller/binding file content map | `fclean.py:53` |

## Pattern Overview

**Overall:** Single-module procedural CLI with a strategy-like dispatch table for template selection.

**Key Characteristics:**
- All logic lives in one file (`fclean.py`) with no imports beyond stdlib (`sys`, `argparse`, `pathlib`)
- Template providers are pure functions — they receive a feature name and return a `dict[str, str]` mapping relative paths to file contents
- The `state_map` dict (`fclean.py:106`) is the strategy dispatch: `state_type` key selects the template function at runtime
- File writes are idempotent — existing files are skipped, never overwritten (`fclean.py:119`)

## Layers (Generated Output Structure)

The tool generates the following Clean Architecture layers inside the target Flutter project:

**Data Layer** (`lib/features/<name>/data/`):
- `datasources/` — remote and local data source abstracts
- `models/` — data models extending domain entities (only if entity name provided)
- `repository/` — `RepositoryImpl` implementing domain interface

**Domain Layer** (`lib/features/<name>/domain/`):
- `entities/` — pure domain entity classes (only if entity name provided)
- `repository/` — abstract repository interface
- `usecases/` — directory created, files populated manually

**Presentation Layer** (`lib/features/<name>/presentation/`):
- `pages/` and `widgets/` — always created empty
- State management files injected here based on `--state` flag

## Data Flow

### Primary Execution Path

1. CLI invoked: `python3 fclean.py --features auth:user --state bloc` (`fclean.py:141`)
2. `argparse` parses `--features` (list) and `--state` (enum choice) (`fclean.py:129`)
3. `is_flutter_project()` checks for `pubspec.yaml`; exits with error if absent (`fclean.py:134`)
4. Loop calls `create_feature(feature, state_type)` for each feature arg (`fclean.py:138`)
5. `create_feature` splits `feature_arg` on `:` to extract feature name and optional entity name (`fclean.py:72`)
6. Eight subdirectories created under `lib/features/<name>/` (`fclean.py:78`)
7. Core files (datasources, repository interface/impl) written into `files_to_create` dict (`fclean.py:87`)
8. If entity name provided, entity + model files appended (`fclean.py:99`)
9. `state_map[state_type]` called to get template dict; merged into `files_to_create` (`fclean.py:113`)
10. Each path written if not already existing; skipped with message otherwise (`fclean.py:118`)

## Entry Points

**CLI Entry:**
- Location: `fclean.py:141` (`if __name__ == "__main__": main()`)
- Triggers: Direct Python execution (`python3 fclean.py`)
- Responsibilities: Delegates entirely to `main()`

## Architectural Constraints

- **No external dependencies:** Only Python stdlib — no pip install required
- **CWD-relative output:** All generated paths resolve relative to the process working directory, not the script location
- **Global state:** None — all data is passed via function arguments or local variables
- **Circular imports:** Not applicable (single module)
- **No dry-run mode:** Writes happen immediately with no preview or rollback

## Error Handling

**Strategy:** Minimal — validate project root upfront, skip (not fail) on existing files.

**Patterns:**
- `is_flutter_project()` returns bool; `main()` calls `sys.exit(1)` on false (`fclean.py:135`)
- File-level conflicts print a skip message and continue; no exception is raised (`fclean.py:120`)
- No try/except blocks — filesystem errors surface as unhandled exceptions

## Anti-Patterns

### No `--dry-run` flag

**What happens:** Files are written immediately on every invocation with no preview.
**Why it's wrong:** Users cannot verify what will be generated before committing filesystem changes.
**Do this instead:** Accept a `--dry-run` flag in `main()` and pass it through `create_feature()` to print paths without writing.

### Feature name not validated

**What happens:** Any string (including paths with `/`, spaces, or special chars) is accepted as a feature name and used directly in `Path` construction (`fclean.py:76`).
**Why it's wrong:** Malformed input can create unintended directory structures.
**Do this instead:** Validate feature name against `^[a-z][a-z0-9_]*$` after parsing in `create_feature()`.

---

*Architecture analysis: 2026-06-02*
