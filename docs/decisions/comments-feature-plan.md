# Design Note: Comments on Tasks

**Status:** Draft — planning only, no implementation
**Module:** 5 — Task Tracker

## 1. Data Model

New comment models belong in `backend/app/models.py`, following the exact pattern already
established there for tasks:

- `CommentCreate` (request body: `author`, `body`) and `CommentResponse` (`id`, `task_id`,
  `author`, `body`, `created_at`) — mirroring the `TaskCreate`/`TaskResponse` split
  (`models.py:22-30`, `167-178`).
- Both would set `model_config = ConfigDict(extra="forbid")`, matching every existing model in
  this file (`models.py:23`, `89`, `168`, `182`), so an unknown field in a comment body is
  rejected with `422` the same way it already is for tasks.
- `author` and `body` need `field_validator`s that strip whitespace and enforce length, directly
  mirroring `TaskCreate.validate_title` (`models.py:32-57`): strip, reject if empty, reject if
  over the limit (100 for `author`, 2000 for `body`). `tags.py`'s `normalize_tags` is not a good
  fit here — it governs a *list* of short strings with a count cap, not a single long string, so
  it isn't reused directly.
- No `CommentUpdate` model is proposed. Nothing in the existing codebase (task `PATCH` plus the
  status-transition rules in `business_rules.py`) implies whether comments should be editable —
  this is a genuine new decision, not something inferred from what's here (see Open Questions).

**Storage placement:** `backend/app/storage.py` currently holds exactly two module-level
collections — `_tasks: dict[str, TaskResponse]` and `_activity_events: list[ActivityEvent]`
(`storage.py:45-47`) — both persisted together in `backend/data/tasks.json` as
`{"tasks": [...], "activity": [...]}` (`storage.py:36-42`). Comments are append-only, per-task
records, structurally closer to `ActivityEvent` (created once, never mutated) than to `TaskResponse`
(mutated via `PATCH`). The natural extension is a third collection, e.g.
`_comments: list[CommentResponse]`, filtered by `task_id` at read time the same way
`get_all_tasks` filters by `status`/`priority` (`storage.py:93-119`).

## 2. API Routes

This repo has no separate route files — every endpoint is a decorated function directly in
`backend/app/main.py` (confirmed: the entire file, 242 lines, contains all routes inline, no
`APIRouter`). New comment routes would follow the same flat pattern:

| Method | Path | Request body | Response body | Error cases |
|---|---|---|---|---|
| `POST` | `/tasks/{task_id}/comments` | `CommentCreate` (`author`, `body`) | `CommentResponse`, `201` | `404` if the task doesn't exist (check via `storage.get_task_by_id`, same as `update_task`/`delete_task` do today, `main.py:180-186`); `422` on blank/oversized `author`/`body` or an unknown field, via pydantic validation exactly like task creation (`main.py:48-74`) |
| `GET` | `/tasks/{task_id}/comments` | — | `list[CommentResponse]` | `404` if the task doesn't exist — **open question**: should this check run at all, or should a nonexistent task with no comments just return `200` + `[]`? (See Open Questions.) |

Response conventions to carry over: `response_model_exclude_none=True` and explicit
`status_code=status.HTTP_201_CREATED` on create, matching `create_task` (`main.py:41-46`); the
`404` detail message should reuse the exact existing phrasing
`f"Task with id {task_id} not found"` (`main.py:134`, `185`, `223`) rather than inventing new
wording, since that string is already a repo convention.

No `PATCH`/`DELETE` route for individual comments is proposed in this plan — there's no existing
precedent for a similarly-shaped "always-append" child record in this codebase to model it after,
so it needs its own explicit decision.

A secondary, non-required design choice: should `add_comment` also call `_append_activity`
(`storage.py:50-59`), the same way `add_task`, `update_task`, and `delete_task` already do
(`storage.py:88`, `184-186`, `207`)? This would make comment creation show up in `GET /activity`
alongside `create`/`update`/`status_change`/`delete` — consistent with the existing pattern, but
not automatic just because the pattern exists.

## 3. Tests

`tests/test_tasks.py` uses a consistent naming convention across all 24 existing tests:
`test_<action>_<condition>_returns_<result>` (e.g. `test_create_task_missing_title_returns_422`,
`test_get_task_by_id_not_found_returns_404_with_detail`). `tests/conftest.py` provides a `client`
fixture, a `created_task` fixture (POSTs one fixture task), and an autouse `_reset_storage`
fixture that calls `storage._reset()` before and after every test (`conftest.py:13-17`). Comment
tests would reuse these fixtures rather than inventing new setup.

**Happy path**
- `test_create_comment_valid_returns_201_with_full_body`
- `test_list_comments_returns_comments_for_task`
- `test_list_comments_empty_task_returns_200_and_empty_list` (mirrors
  `test_list_tasks_empty_returns_200_and_empty_list`, `test_tasks.py:106-110`)

**Validation**
- `test_create_comment_missing_author_returns_422`
- `test_create_comment_blank_author_returns_422`
- `test_create_comment_author_over_100_chars_returns_422`
- `test_create_comment_missing_body_returns_422`
- `test_create_comment_blank_body_returns_422`
- `test_create_comment_body_over_2000_chars_returns_422`
- `test_create_comment_unknown_field_returns_422` (mirrors
  `test_create_task_unknown_field_returns_422`, `test_tasks.py:97-103`, assuming `CommentCreate`
  also forbids extra fields)

**Edge cases**
- `test_create_comment_on_missing_task_returns_404`
- `test_list_comments_on_missing_task_returns_404` (pending the open question on whether this
  check should exist at all)
- `test_create_comment_ignores_client_supplied_created_at` (mirrors this repo's existing care
  that `created_at`/`updated_at` are always server-set, never client-supplied — `storage.py:74`,
  `83-84`)

## 4. Frontend Changes

The only frontend file is `frontend/index.html` — a single static file, no build step, no
framework, plain `fetch`/`document.querySelector`/template-string rendering (confirmed by reading
the full file). There is currently **no per-task detail view and no comments UI of any kind.**

Task cards are rendered by `renderTask()` (`index.html:652-675`) showing title, description,
priority, assignee, tags, and an Edit button. The Edit button opens the existing create/edit modal
(`#task-modal-backdrop`, `index.html:480-533`), which is a plain form — it has no sub-list
rendering today.

Concrete changes:
- Extend the existing task modal with a comments section (list + a small "add comment" form),
  since that modal already exists as the only per-task surface in the UI — a new dedicated view
  is an alternative but not implied by anything currently in the file.
- Add `fetchComments(taskId)` following the exact pattern already used for `fetchActivity()`
  (`index.html:746-761`) — a `GET` call on modal-open — plus a `submitComment()` following the
  pattern of `saveTask()` (`index.html:902-968`) for the `POST` on form submit.
- Reuse `escapeHtml()` (`index.html:643-650`) when rendering `author`/`body`, matching how every
  other dynamic value in this file is already escaped before insertion into `innerHTML` — this is
  an existing repo convention, not a new precaution.
- Reuse the existing field-error pattern (`showFieldError`, `.field-error` elements,
  `index.html:414-418`, `890-895`) for comment-form validation messages (blank/oversized
  `author`/`body`), rather than introducing a new error-display mechanism.
- User-visible result: opening a task via Edit would show its existing comments (author, body,
  a formatted timestamp — reusing `formatActivityTimestamp()`, `index.html:689-699`) plus a small
  form to add a new one; validation errors would appear inline the same way task-form errors do
  today.

## 5. Migration Notes

`backend/data/tasks.json` currently has exactly two top-level keys, `"tasks"` and `"activity"`
(`storage.py:16`, `40`). `_load_state()` already defaults each to `[]` if absent via
`raw_data.get("tasks", [])` / `raw_data.get("activity", [])` (`storage.py:25-26`) — adding a third
key, `"comments"`, would follow the same defaulting behavior, so **existing data files without a
`"comments"` key would not break** on load.

No changes to `TaskResponse` (`models.py:167-178`) are implied — comments are a separate
collection referencing `task_id`, not a field embedded on the task itself, unless the team
explicitly wants a denormalized `comment_count` or similar on `TaskResponse` (see Open Questions).

The `Dockerfile` copies only `backend/app` into the image, not `backend/data` — comments require
no Docker-specific migration step beyond the code change itself; the JSON shape evolves at
runtime through the same `_load_state` defaulting behavior described above.

## 6. Open Questions

1. **Cascade behavior on task deletion.** `delete_task` (`storage.py:192-209`) currently touches
   only `_tasks` and appends one activity event — nothing about a child collection. Should
   deleting a task also delete its comments, block deletion while comments exist, or leave
   orphaned comment records in storage?
2. **Activity-log integration.** Should comment creation call `_append_activity` with a new
   event type (e.g. `"comment_added"`), consistent with `create`/`update`/`status_change`/
   `delete` (`storage.py` calls at lines `88`, `184-186`, `207`)? This directly affects what
   `GET /activity` returns and what the frontend's activity panel displays.
3. **404 semantics for listing comments on a missing task.** Should `GET /tasks/{task_id}/comments`
   check task existence and 404, or should a nonexistent-task query just return `200` + `[]`
   (mirroring `test_list_tasks_empty_returns_200_and_empty_list`,`test_tasks.py:106-110`)? These
   are meaningfully different API contracts.
4. **Editability.** Can a comment be edited or deleted after creation? Nothing in the existing
   `TaskUpdate`/`business_rules.py` pattern answers this for a brand-new resource type — it needs
   its own decision, not an inference from task behavior.
5. **Author identity.** Should `author` remain a permanent free-text string, or is it meant to
   anticipate a future real user/identity system? The repo explicitly documents "No
   authentication or authorization... there is no user model" (`README.md` §9, `AGENTS.md` §3),
   so `author` as free text is consistent with today's scope — but worth confirming it's not
   meant to imply otherwise.

## Files read

`AGENTS.md`, `README.md`, `backend/app/main.py`, `backend/app/models.py`, `backend/app/storage.py`,
`backend/app/business_rules.py`, `backend/app/tags.py`, `requirements.txt`, `tests/conftest.py`,
`tests/test_tasks.py`, `frontend/index.html`, `Dockerfile`, `.github/workflows/ci.yml`,
`docs/decisions/in-memory-storage-decision.md`. All were read in full during this review; before
writing this plan, `git status` was checked against `backend/`, `frontend/`, `tests/`, `AGENTS.md`,
`README.md`, `requirements.txt`, `Dockerfile`, and `.github/` to confirm none had changed since
those reads (only `AGENTS.md` shows as untracked/new, as expected).

## Assumptions to verify

- That comments should be a flat, append-only collection (like `ActivityEvent`) rather than
  nested inside each task record — this is a design choice modeled on the closest existing
  pattern, not something the repo already dictates.
- That `CommentCreate` should forbid extra fields (`extra="forbid"`), matching every other request
  model — reasonable given the consistency of the existing pattern, but not something a comment
  feature is forced into.
- That comments require no auth/ownership check beyond "does this task exist," consistent with
  the rest of the app being fully open (README §9) — would need revisiting if auth is ever added.
- That the frontend should extend the existing task modal rather than introduce a new dedicated
  task-detail view — the file's current structure has no detail view to extend, so this is the
  lower-effort option, not a confirmed product decision.
- That comment length limits (1-100 for `author`, 1-2000 for `body`) should be enforced with the
  exact same strip-then-check-length pattern as `title`, rather than any different normalization —
  reasonable by analogy, not verified against a spec.
