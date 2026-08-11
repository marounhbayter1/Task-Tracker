# Module 5 Governance Retrospective — What I Shared With AI Coding Tools

**Status:** Draft
**Module:** 5 — Task Tracker

This note classifies the risk level of the material shared with AI coding tools during this
course, using the risk rubric below, and records safer alternatives for future sessions.

## Risk rubric

- **Low**: public code, course toy project code, no sensitive data, no proprietary logic.
- **Medium**: private but non-sensitive code, internal implementation details, or non-public repo
  context with no secrets and no PII.
- **High**: credentials, tokens, secrets, production config, real customer/user data, regulated
  data, or code I am not authorized to share.

## Classification

| Item shared | Risk | Reason | Safer future version | Ambiguity to resolve |
|---|---|---|---|---|
| Task Tracker Code (`backend/app/*.py`, `models.py`, `storage.py`, etc.) | **Low**, content-based | This is the documented course project (README: "Module 4 course project"); the code contains no hardcoded secrets, credentials, or proprietary business logic — confirmed by direct inspection and a grep for secret-like patterns during the Module 5 audit. | Keep pasting only the specific file(s) relevant to the question rather than the whole tree, and keep confirming that `.env` stays out of anything shared — it already contains no secrets by content, so the main lever left is scope, not redaction. | Repo visibility is not established. The Medium tier includes "non-public repo context" as its own trigger, independent of secrets — if this is a private GitHub repo (not a public course fork), that clause alone could move this from Low to Medium regardless of content. Confirm public vs. private before finalizing. |
| Frontend code (`frontend/index.html`) | **Low** | Pure client-side static HTML/CSS/JS with no build step; confirmed during the Module 5 audit to contain no API keys, tokens, or secrets — only a hardcoded `localhost:8000` API URL, which is a dev convenience, not sensitive data. | No change needed for content; if the app ever gains a real backend URL, an API key, or analytics ID, re-check before pasting again. | Same repo-visibility question as row 1 — if the whole repo is private, this file inherits that context even though its own content is clean. |
| Dockerfile and CI YAML | **Low** | Both were read during the audit: `Dockerfile` uses only the public `python:3.11-slim` base image and installs from `requirements.txt` with no embedded credentials; `.github/workflows/ci.yml` runs `pytest` and a local `docker build` with no `secrets.*` references, no deployment step, and no cloud/registry credentials. | Continue the practice used in this review — grep for `secrets.`, `env:`, or hardcoded tokens before pasting CI config, especially once/if a real deploy step is added (that's when CI YAML risk typically jumps to Medium/High). | None beyond the same repo-visibility question — content-wise this pair is clean regardless of public/private status, since there's genuinely nothing secret in either file today. |

## Rubric note

Three of the four items above hinge on the same unresolved fact: whether this repository is
public or private. The rubric treats "non-public repo context" as sufficient for Medium on its
own, separate from whether secrets are present, so resolving that one fact could uniformly shift
the Task Tracker Code, Frontend Code, and Dockerfile/CI YAML rows from Low to Medium without any
new evidence about the code itself.
