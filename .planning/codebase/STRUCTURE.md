# Codebase Structure

**Analysis Date:** 2026-06-02

## Directory Layout

```
fclean/
├── fclean.py         # Entire tool — CLI entry, validation, scaffolding, templates
├── README.md         # Usage docs and examples
└── .planning/
    └── codebase/     # GSD codebase analysis documents
```

The project is intentionally minimal: the complete implementation lives in a single Python file with no packages, modules, or build system.

## Key File Locations

**Entry Point:**
- `fclean.py`: The only source file. Contains all functions, template strings, and the `main()` entry point.

**Documentation:**
- `README.md`: Usage guide covering CLI flags, argument formats, and example invocations.

**Planning:**
- `.planning/codebase/`: GSD mapper output — not part of the tool itself.

## Module / Function Organization (within `fclean.py`)

Functions are arranged by responsibility in a top-to-bottom order that mirrors the execution flow:

| Lines | Function | Role |
|-------|----------|------|
| 5–7 | `is_flutter_project()` | Project guard / validation |
| 9–28 | `get_bloc_templates(feature)` | BLoC boilerplate template provider |
| 30–43 | `get_cubit_templates(feature)` | Cubit boilerplate template provider |
| 45–51 | `get_riverpod_templates(feature)` | Riverpod boilerplate template provider |
| 53–69 | `get_getx_templates(feature)` | GetX boilerplate template provider |
| 71–125 | `create_feature(feature_arg, state_type)` | Core scaffolding orchestrator |
| 127–139 | `main()` | CLI arg parsing and top-level dispatch |
| 141–142 | `if __name__ == "__main__"` | Python entry-point guard |

## Naming Conventions

**Files:**
- Single snake_case Python file: `fclean.py`
- Generated Dart files follow the pattern: `<feature_name>_<role>.dart` (e.g., `auth_bloc.dart`, `auth_repository.dart`)

**Functions:**
- Snake_case: `create_feature`, `get_bloc_templates`, `is_flutter_project`
- Template providers prefixed with `get_` and suffixed with `_templates`

**Generated directories:**
- All lowercase snake_case, matching Flutter conventions: `data/datasources`, `domain/usecases`, `presentation/pages`

## Configuration File Locations

- No configuration files exist in this project
- The tool itself requires no config — behavior is entirely driven by CLI flags at runtime
- The target Flutter project must have `pubspec.yaml` at its root (detected, not read)

## Generated Output Layout (in Target Flutter Project)

When run against a Flutter project, fclean creates the following structure under `lib/features/`:

```
lib/features/<feature_name>/
├── data/
│   ├── datasources/
│   │   ├── <feature>_remote_datasource.dart
│   │   └── <feature>_local_datasource.dart
│   ├── models/
│   │   └── <entity>_model.dart          # only if entity provided
│   └── repository/
│       └── <feature>_repository_impl.dart
├── domain/
│   ├── entities/
│   │   └── <entity>.dart                # only if entity provided
│   ├── repository/
│   │   └── <feature>_repository.dart
│   └── usecases/                        # empty, populated manually
└── presentation/
    ├── pages/                           # empty, populated manually
    ├── widgets/                         # empty, populated manually
    └── <state-management-files>         # varies by --state flag:
        │                                #   bloc:     bloc/, event, state, bloc files
        │                                #   cubit:    cubit/, state and cubit files
        │                                #   riverpod: providers/<feature>_provider.dart
        └──                              #   getx:     controller/ + bindings/ files
```

## Where to Add New Code

**New state management library support:**
- Add a `get_<library>_templates(feature)` function in `fclean.py` following the existing pattern (lines 9–69)
- Register it in the `state_map` dict inside `create_feature()` at `fclean.py:106`
- Add the new value to `choices` in the `--state` argparse argument at `fclean.py:130`

**New core scaffolding files (always generated):**
- Add entries to the `files_to_create` dict inside `create_feature()` starting at `fclean.py:87`

**New CLI flags:**
- Add `parser.add_argument(...)` calls inside `main()` at `fclean.py:127`
- Pass new values through to `create_feature()` as additional parameters

**Tests (not yet present):**
- A `tests/` directory at the project root is the natural location
- Unit test targets: each `get_*_templates()` function and `create_feature()` with a temp directory fixture

---

*Structure analysis: 2026-06-02*
