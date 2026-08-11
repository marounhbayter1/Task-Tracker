# Architecture Documentation — Context-Strategy Comparison Log

**Status:** Draft
**Module:** 5 — Task Tracker

This log compares three context strategies used to independently produce a one-page architecture
doc for this repo — `docs/architecture-A.md` (minimal/full inspection), `docs/architecture-B.md`
(structured context via `AGENTS.md` + file summaries), and `docs/architecture-C.md` (targeted
context via three anchor files: `backend/app/main.py`, `models.py`, `storage.py`).

## 1. Strategy comparison table

| Strategy | What it got right | What it got wrong, missed, or invented | Best suited for |
|---|---|---|---|
| **A — Minimal (full repo inspection)** | Full `Task`/`ActivityEvent` field lists (including `id`, `assignee`, `created_at`/`updated_at`); exact `201` status code and full request flow; exact frontend API URL (`http://localhost:8000`) and CORS origin; correctly flagged real unknowns (repo visibility, concurrent-write behavior, Docker volume persistence, the `httpx2` anomaly) instead of guessing at them. | Nothing invented. One concrete miss: it states storage is "rewritten to one JSON file on every mutation" but never mentions that `storage.py`'s loader also tolerates a legacy *list*-shaped JSON file as a fallback — a detail Strategy C caught and A didn't, despite A having read the same file. | A comprehensive, canonical architecture doc meant to cover the whole system (backend + frontend + tests/CI) in one pass, where completeness and accuracy matter more than the cost of reading everything. |
| **B — Structured (AGENTS.md + file summaries)** | Project-purpose paragraph matches A closely; every stated fact traces cleanly to AGENTS.md or the file summaries; disciplined about marking gaps ("not stated in this context") instead of inventing — zero fabrication. | Missed real, existing fields: `id`, `assignee`, `created_at`, `updated_at` on `Task`, and `id`/`task_id`/`message`/`timestamp` on `ActivityEvent` — not because they don't exist, but because AGENTS.md's business-rules section never enumerated them. Also missed the `201` status code and the frontend's exact API URL, both absent from AGENTS.md's text. These are honest omissions, not invented facts — the gap is in the curated source, not in B's discipline. | A quick, low-cost refresh or onboarding doc when a trusted, already-current summary document (like AGENTS.md) exists and full field-level precision isn't the point — e.g., explaining behavior/business rules rather than exact schemas. |
| **C — Targeted (3 anchor files: `main.py`, `models.py`, `storage.py`)** | Recovered the *full* `Task`/`ActivityEvent` field lists (better than B on this specific point, matching A) because it read `models.py` directly; got the exact `201` status and `response_model_exclude_none` detail; uniquely caught the dual JSON-shape fallback in `storage.py` that A's own draft omitted; consistently used "not visible from the files I read" for anything delegated to `business_rules.py`/`tags.py` rather than guessing. | Has no idea a frontend exists at all (a bigger gap than B, which at least knew there was a static Kanban page from AGENTS.md). Doesn't know the tag limits (≤10/≤30 chars) or the exact status-transition matrix that both A and B captured, since those live in files it was told not to read. No knowledge of tests, CI, Docker, or the `httpx2` dependency anomaly. Nothing invented. | Deep, precise documentation of one subsystem or code path when the reviewer already has (or doesn't need) the surrounding context — e.g., documenting exactly how the core CRUD/persistence mechanism works, or reviewing a PR that only touches those specific files. |

## 2. Verdict

For the canonical `docs/architecture.md`, **Strategy A** is the right choice. The doc's job is to
describe the whole system in one page — backend, storage, frontend, and the real operational
unknowns — and A is the only draft that got the full `Task`/`ActivityEvent` schemas right, stated
the exact request-flow status code, correctly named the frontend's hardcoded API URL, and still
flagged genuine unresolved questions (repo visibility, concurrent writes, Docker volume
persistence, the `httpx2` oddity) without inventing answers to them. Strategy C was more precise
about its three files — it even caught a storage-loader detail A's own draft missed — but it has
zero visibility into the frontend, tests, or CI, which disqualifies it as a whole-repo reference.
Strategy B's discipline (never inventing, always flagging gaps) is exactly the right instinct, but
its gaps — missing `id`/`assignee`/timestamps, missing status codes — are a direct consequence of
AGENTS.md not enumerating them, meaning B's accuracy is capped by how complete the curated source
is, not by anything B did wrong.

## 3. Context-engineering rule

For task shape "produce a canonical, whole-repo architecture or onboarding doc," I use Strategy A
(full inspection) because only it reliably captures cross-cutting facts — full schemas, exact
status codes, frontend behavior — that no single curated summary or file subset is guaranteed to
include. For task shape "document or review a specific, already-scoped subsystem" (e.g., a PR
touching a known set of files), I use Strategy C (targeted anchor files) because it gets full
precision on those files at a fraction of the context cost, and its "not visible from the files I
read" discipline stops it from inventing facts about the rest of the system it wasn't asked to
cover.
