---
phase: 1
slug: foundation-fixes
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-02
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — Wave 0 installs pytest |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | CORE-01 | — | N/A | unit | `python -m pytest tests/test_utils.py -x -q` | ❌ W0 | ⬜ pending |
| 1-02-01 | 02 | 1 | CORE-02 | — | reject malformed input | unit | `python -m pytest tests/test_validator.py -x -q` | ❌ W0 | ⬜ pending |
| 1-02-02 | 02 | 1 | DX-02 | — | N/A | unit | `python -m pytest tests/test_cli.py -x -q` | ❌ W0 | ⬜ pending |
| 1-03-01 | 03 | 2 | CORE-03 | — | N/A | unit | `python -m pytest tests/test_templates.py -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py` — test package marker
- [ ] `tests/test_utils.py` — stubs for CORE-01 (to_pascal_case)
- [ ] `tests/test_validator.py` — stubs for CORE-02 (validate_name)
- [ ] `tests/test_cli.py` — stubs for DX-02 (--state omission notice)
- [ ] `tests/test_templates.py` — stubs for CORE-03 (riverpod template)
- [ ] `pytest` install — `pip install pytest` if not present

*Note: Phase 3 will expand these stubs into full test suites. Wave 0 here creates minimal test files to enable TDD feedback during Phase 1 execution.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Riverpod template compiles in Flutter project | CORE-03 | Requires Flutter SDK | Copy generated template into test Flutter project; run `flutter analyze` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
