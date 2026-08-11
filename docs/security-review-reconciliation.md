# Module 5 Security Review — AI/Manual Reconciliation

**Status:** Draft 
**Module:** 5 — Task Tracker

This note reconciles the AI-generated security audit findings against the student's manual
security scan of the same repository, per the Module 5 review exercise.

## 1. Reconciliation table

Manual scan findings were **not yet provided** at the time this file was created ("None Yet").
As a result, the **Agreement** and **You-only** columns are empty by necessity, not because the
AI review found everything — re-run this reconciliation once the manual findings are added.

| Agreement | AI-only | You-only |
|---|---|---|
| — | F1: unbounded `description`/`assignee` fields (Valid) | — |
| — | F2: unpinned dependencies in `requirements.txt` (Noise) | — |
| — | F3: `httpx2` unusual dependency name — **needs evidence** (unverified against PyPI) | — |
| — | F4: no authentication on any endpoint (Valid, documented course-scope) | — |
| — | F5: `storage.py` crashes on corrupted/invalid `tasks.json` at startup (Valid) | — |
| — | F6: no visible request body size limit (Noise, unconfirmed) | — |
| — | F7: `task_id` path param has no format constraint (Noise) | — |
| — | F8: frontend hardcodes `http://localhost:8000` (Noise, course-scope) | — |
| — | F9: no CI dependency/security scanning (Noise) | — |
| — | F10: no Dockerfile `HEALTHCHECK` (Noise) | — |

## 2. Observation on the shape of AI coverage

AI coverage is entirely static-code-driven — it caught things visible by reading files (missing
validators, missing error handling, unpinned deps, an odd dependency name) but has zero findings
that would require running the app, exercising the storage layer under real load, or forming a
judgment call from actually using the Kanban board/UI. Until manual findings are added, this list
can't show what a hands-on reviewer catches that a read-only code pass doesn't (e.g. UX-driven
security gaps, actual runtime error behavior, or things only visible by clicking through the
frontend) — that gap is exactly what the You-only column exists to surface.

## 3. Top-3 security backlog (from Valid findings only)

| Rank | Finding | Why it matters | Suggested owner | Next action |
|---|---|---|---|---|
| 1 | F4 — No authentication on any endpoint (`backend/app/main.py`) | Currently intentional and documented for course scope (README §9, AGENTS.md §3), but it's the single finding that would matter most if this app ever moved past localhost — every task and activity record is fully open to anyone who can reach the port. | Course/project owner (scope decision) → backend (implementation if scope changes) | Get an explicit decision recorded: stays out-of-scope for Module 5, or gets a milestone in a future module. Don't let it linger as an implicit assumption. |
| 2 | F5 — `storage.py` has no error handling around loading/parsing `backend/data/tasks.json` (`storage.py:12-33,47`) | This runs at process import time with no try/except — a corrupted file or a hand-edited record that fails pydantic validation takes the entire app down with no recovery path. Directly evidenced, not speculative. | Backend | Wrap `_load_state()` in error handling that logs clearly and either fails fast with an actionable message or falls back to an empty store, instead of an unhandled traceback on boot. |
| 3 | F1 — `description`/`assignee` have no length bound (`models.py:26,29,92,95`) | Combined with F4 (no auth) and the full-file-rewrite-on-every-write storage design, an unbounded field is a concrete, repo-specific bloat/DoS vector rather than generic advice. | Backend | Add a max-length validator on `description` and `assignee`, following the same pattern already used for `title` (200 chars) and tags (30 chars). |

**Not ranked, flagged instead:** F3 (`httpx2`) is Valid-pending-verification, not yet a confirmed
backlog item — it needs a PyPI lookup before it can be prioritized.

## Source

Full finding descriptions, severities, evidence, and grading rationale (Valid / False Positive /
Noise) for F1–F10 are in the security audit and grading conversation for this module; this file
captures only the reconciliation, observation, and backlog outputs of that review.
