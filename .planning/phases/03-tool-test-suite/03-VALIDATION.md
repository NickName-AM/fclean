---
phase: 3
slug: tool-test-suite
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-03
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 |
| **Config file** | `pyproject.toml` (rootdir auto-detected) |
| **Quick run command** | `.venv/bin/pytest` |
| **Full suite command** | `.venv/bin/pytest -v` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/pytest`
- **After every plan wave:** Run `.venv/bin/pytest -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~1 second

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | TEST-01 | — | N/A | unit | `.venv/bin/pytest tests/test_utils.py -x` | ✅ | ⬜ pending |
| 03-01-02 | 01 | 1 | TEST-04 | — | N/A | unit | `.venv/bin/pytest tests/test_utils.py -x` | ✅ | ⬜ pending |
| 03-02-01 | 02 | 1 | TEST-02 | — | N/A | integration | `.venv/bin/pytest tests/test_generator.py -x` | ✅ | ⬜ pending |
| 03-03-01 | 03 | 1 | TEST-03 | — | N/A | unit | `.venv/bin/pytest tests/test_templates.py -x` | ✅ | ⬜ pending |
| 03-03-02 | 03 | 1 | TEST-05 | — | N/A | unit | `.venv/bin/pytest tests/test_templates.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `dry_run` parameter on `create_feature()` in `fclean/generators/feature.py` — required before TEST-05 tests can be written (Plan 3.3 decision point)

*All three test files already exist. No new framework installs needed. The only Wave 0 gap is the `dry_run` implementation decision for TEST-05.*

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
