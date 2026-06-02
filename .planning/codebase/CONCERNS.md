# Codebase Concerns

**Analysis Date:** 2026-06-02

## Tech Debt

**No test suite:**
- Issue: Zero tests exist for any functionality. No test runner, no test files.
- Files: `fclean.py` (entire tool)
- Impact: Any change to template strings, directory logic, or argument parsing can silently break output without detection.
- Fix approach: Add `pytest` + tests for `create_feature`, each template function, and the `is_flutter_project` guard.
- Severity: HIGH

**Flat single-file architecture:**
- Issue: All logic (CLI parsing, template strings, file I/O, directory creation) lives in one 142-line `fclean.py`. No separation of concerns.
- Files: `fclean.py`
- Impact: Any growth (new state libraries, new layer types, usecase scaffolding) will make the file unwieldy and hard to extend without refactoring.
- Fix approach: Split into `templates/`, `generators/`, and `cli.py` modules.
- Severity: MEDIUM

**`feature_name.capitalize()` is incorrect for multi-word names:**
- Issue: `capitalize()` only uppercases the first character and lowercases the rest. A feature name like `user_profile` produces `User_profile`, not `UserProfile`. The class names in generated Dart files will be syntactically wrong.
- Files: `fclean.py` lines 11, 32, 54, 89–104
- Impact: Generated Dart code will have malformed class names (e.g., `User_profileBloc` instead of `UserProfileBloc`).
- Fix approach: Replace `capitalize()` with a proper `to_pascal_case()` helper that splits on `_` and capitalizes each segment.
- Severity: HIGH

**No input validation on feature/entity names:**
- Issue: `feature_arg.split(":")` and downstream usages pass user-supplied strings directly into file paths and Dart class names with no validation. Names containing `/`, `..`, spaces, or Dart-reserved keywords are silently accepted.
- Files: `fclean.py` lines 72–74, 88–116
- Impact: Path traversal is possible (`--features ../../../etc:payload` would write files outside the project); invalid Dart identifiers produce broken generated code.
- Fix approach: Add a regex validation step (e.g., `^[a-z][a-z0-9_]*$`) on `feature_name` and `entity_name` before any file I/O.
- Severity: HIGH

**Riverpod template generates `Provider((ref) => null)`:**
- Issue: The riverpod template hard-codes `null` as the provider value, which is not a valid or useful starting point for any real feature.
- Files: `fclean.py` lines 46–51
- Impact: Generated code will cause a Dart type-inference error unless the developer immediately replaces `null`.
- Fix approach: Use a typed stub (e.g., `StateNotifierProvider<...>`) or at minimum document the placeholder clearly in a comment.
- Severity: MEDIUM

## Missing Error Handling

**`path.write_text()` has no error handling:**
- Issue: File write operations are bare — no try/except for `PermissionError`, `OSError`, or disk-full conditions.
- Files: `fclean.py` line 123
- Impact: The tool crashes with an unformatted Python traceback rather than a user-friendly message.
- Fix approach: Wrap in try/except and print a clear error before exiting with a non-zero code.
- Severity: MEDIUM

**`is_flutter_project()` only checks file existence, not validity:**
- Issue: Any directory containing a file literally named `pubspec.yaml` passes the guard, even if it is empty or malformed.
- Files: `fclean.py` lines 5–7
- Impact: Low — unlikely in practice, but the guard gives a false sense of project-type safety.
- Fix approach: Optionally read the first line of `pubspec.yaml` to confirm it is a Flutter manifest.
- Severity: LOW

## Fragile Areas

**`--features` is required but `--state` is optional with no fallback notice:**
- Issue: When `--state` is omitted, no state management files are generated and no message informs the user. The tool silently creates partial scaffolding.
- Files: `fclean.py` lines 113–116, 125
- Impact: Developers may not realize the state layer was skipped; the generated feature is structurally incomplete.
- Fix approach: Print an explicit notice when `state_type` is `None`.
- Severity: LOW

**`entity_name.capitalize()` same bug as feature name:**
- Issue: Entity names passed via `name:entity` syntax are also transformed with `capitalize()`, meaning `user_account` generates class `User_account` in Dart.
- Files: `fclean.py` lines 100–104
- Impact: Same as the feature name concern — broken Dart class names.
- Fix approach: Same `to_pascal_case()` helper.
- Severity: HIGH (same root cause as above)

## Missing Critical Features

**No `--dry-run` option:**
- Problem: Users cannot preview what files will be created before committing.
- Blocks: Safe use in CI or when experimenting with naming.

**No `usecase` scaffolding:**
- Problem: The `domain/usecases/` directory is created but no usecase file is generated. Clean Architecture requires at least one usecase stub per feature.
- Files: `fclean.py` line 82 (directory created), lines 87–116 (no usecase entry)
- Blocks: The generated skeleton is structurally incomplete for Clean Architecture.
- Severity: MEDIUM

## Dependencies at Risk

**No dependency management file:**
- Risk: No `requirements.txt`, `pyproject.toml`, or `setup.py` exists. The tool has no declared Python version or stdlib-only constraint documented.
- Impact: Reproducibility across environments is not guaranteed; `pip install fclean` is not possible.
- Migration plan: Add a minimal `pyproject.toml` with `requires-python = ">=3.8"` and a `[project.scripts]` entry.
- Severity: MEDIUM

## Test Coverage Gaps

**All functionality is untested:**
- What's not tested: Template string correctness, PascalCase conversion, file path construction, directory creation, overwrite-prevention guard, error exits.
- Files: `fclean.py` (entire file)
- Risk: Regressions in generated Dart syntax go unnoticed until a developer inspects the output.
- Priority: HIGH

---

*Concerns audit: 2026-06-02*
