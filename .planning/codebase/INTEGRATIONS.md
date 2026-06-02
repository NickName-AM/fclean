# External Integrations

**Analysis Date:** 2026-06-02

## APIs & External Services

**None.** `fclean` is a fully offline, local code-generation CLI tool. It makes no network calls and integrates with no external APIs or services.

## Data Storage

**Databases:** None

**File Storage:**
- Local filesystem only — all output is written to the current working directory via `pathlib.Path`
- Reads: checks for `pubspec.yaml` to validate Flutter project root
- Writes: creates directories and `.dart` scaffold files under `lib/features/<feature>/`

**Caching:** None

## Authentication & Identity

**Auth Provider:** None — no authentication of any kind

## Monitoring & Observability

**Error Tracking:** None

**Logs:**
- `print()` to stdout only
- Outputs one line per file skipped (already exists) and one summary line per feature generated

## CI/CD & Deployment

**Hosting:** Not applicable — local CLI tool, not a service

**CI Pipeline:** None detected (no `.github/`, `.gitlab-ci.yml`, or similar)

## Environment Configuration

**Required env vars:** None

**Secrets location:** Not applicable

## Webhooks & Callbacks

**Incoming:** None

**Outgoing:** None

## Flutter Ecosystem Dependencies (Generated Code Only)

The tool generates boilerplate that references Flutter packages. These are not dependencies of `fclean` itself — they are packages the target Flutter project must declare in its own `pubspec.yaml`:

| State Library Flag | Flutter Package Referenced in Output |
|--------------------|---------------------------------------|
| `--state bloc`     | `flutter_bloc`                        |
| `--state cubit`    | `flutter_bloc`                        |
| `--state riverpod` | `flutter_riverpod`                    |
| `--state getx`     | `get`                                 |

No version constraints are enforced or injected by `fclean` — import strings are written verbatim into generated `.dart` files.

---

*Integration audit: 2026-06-02*
