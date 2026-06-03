# fclean

## What This Is

A Python CLI tool that scaffolds Flutter Clean Architecture feature directories with a single command. Run `fclean --features auth:user --state bloc` from any Flutter project root and get a fully structured data/domain/presentation skeleton with correct imports, abstract interfaces, and state management boilerplate — ready to write business logic into.

## Core Value

One command that generates a complete, correct Flutter Clean Architecture feature skeleton so developers never hand-write boilerplate again.

## Requirements

### Validated

- ✓ Scaffold data/domain/presentation layer directories per feature — existing
- ✓ Generate datasource, repository interface, and repository implementation stubs — existing
- ✓ Support BLoC, Cubit, Riverpod, and GetX state management via `--state` flag — existing
- ✓ Accept multiple features in one command (`--features auth:user product:item`) — existing
- ✓ Skip (not overwrite) existing files on re-run — existing
- ✓ Validate Flutter project root via `pubspec.yaml` presence — existing

### Active (Phase 02 complete — package restructured, pyproject.toml added, 12 tests green)

- [ ] Fix PascalCase conversion — `auth_profile` → `AuthProfile` (not `Auth_profile`)
- [ ] Generate abstract `UseCase<Type, Params>` base class once per feature in `domain/usecases/`
- [ ] Generate a concrete usecase stub per feature extending the base class
- [ ] Improve Riverpod template — typed `StateNotifierProvider` stub instead of bare `null`
- [ ] Add Provider (flutter_provider) as a fifth `--state` option
- [ ] Add `--dry-run` flag — print all paths that would be created without writing
- [ ] Scaffold test stubs mirroring the feature structure under `test/features/<name>/`
- [ ] Validate feature/entity names against `^[a-z][a-z0-9_]*$` with a clear error message
- [ ] Package as a proper `pip install fclean` CLI (`pyproject.toml`, `fclean` entry point)
- [ ] Restructure from single-file script to module layout (`cli/`, `templates/`, `generators/`)
- [ ] Add test suite covering template correctness, PascalCase conversion, and validation

### Out of Scope

- Non-Flutter project support — tool is Flutter-specific by design
- GUI or TUI interface — CLI is the right model for a code generator
- Custom template loading from user config — adds complexity, not needed for v1
- Full project initialization (flutter create equivalent) — fclean scaffolds features, not projects
- Plugin/extension system — over-engineered for current scope

## Context

This tool was built as a personal productivity script and works for its core purpose, but has structural and correctness issues that prevent it from being a tool others can rely on. The most critical bug is the `capitalize()` call on snake_case names (e.g., `user_profile` → `User_profile` in Dart class names, which is syntactically invalid). The tool has no tests, no packaging, and no usecase scaffolding — all of which are needed before it can be recommended to other Flutter developers.

The target audience is Flutter developers who follow Clean Architecture. They expect generated code to be idiomatic Dart — proper PascalCase class names, properly typed interfaces, and the standard layer structure.

## Constraints

- **Language**: Python 3.8+ — stdlib-only for the generator core; dev dependencies (pytest) are acceptable
- **Dependencies**: Keep runtime dependencies to zero (no pip install required to use the generated code)
- **Compatibility**: Generated Dart must be valid for Flutter 3.x with current state library versions
- **No breaking changes**: Existing `--features` and `--state` CLI interface must be preserved

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Abstract `UseCase<T, P>` base class | User-specified; standard Clean Architecture pattern for typed usecase contracts | — Pending |
| Module restructure before feature work | Cannot grow features cleanly on a 142-line single-file base | — Pending |
| Test scaffolding as v1 feature | Users want test stubs generated alongside code — not deferred | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-03 — Phase 01 (foundation-fixes) complete. CORE-01, CORE-02, CORE-03, DX-02 validated and test-locked.*
