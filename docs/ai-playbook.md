# Personal AI Coding Playbook

Written during Module 5, revised after the final project made a few of these rules stop being theoretical.

## 1. When I reach for AI first

- Turning informal notes into a structured artifact (rubric → table, backlog → ranked list) where structure is the hard part, not judgment.
- A first-pass review (code review or security review) over a file or diff I already understand — a candidate list, not a verdict.
- Tedious but mechanical verification: spin up the app, hit an endpoint, run the tests, compare README claims to what the code actually does.
- Writing up evidence for something I already did and understand, so I'm not starting from a blank page.

## 2. When I do not reach for AI first

- Anything touching `.env` or real secrets — don't paste it in, even to "ask about it." I broke this rule myself this project, reading `.env` to confirm it had no real secrets. It was harmless (`PORT`/`APP_ENV` placeholders), but "happened to be harmless" isn't the same as the rule holding. Grep for the key, never `cat` the file.
- Anything where a tool can't check its own work (no daemon running, no network). That's exactly when it's tempting to describe what "should" happen instead of what did.
- Deciding whether a finding matters enough to act on. AI is good at "here's what's technically true"; it doesn't know this project already decided not to fix its concurrency model.

## 3. My non-negotiables

- Never paste `.env` or anything matching a secret/token pattern — grep first, read never.
- No fabricated results. If a check couldn't run, the doc says so with the real error, not a rounded-up "confirmed."
- Every "it works" claim traces to a command I ran and an output I saw, not a paraphrase of what the code implies.
- I own the final grade on any AI-produced finding. "The tool said so" is not a citation.

## 4. My review rules

- After any AI edit or suggestion, read the actual diff or finding — a "done" summary is not a substitute for looking.
- Every finding gets graded (Valid, False Positive, Noise) with a reason. If I can't say why, I haven't reviewed it.
- A clearance ("this is fine") gets the same scrutiny as a flagged risk. This project's `httpx2` dependency looked like a typosquat; the AI review said it wasn't but got its own supporting detail wrong — I had to check PyPI and do a clean install myself before I believed it.
- Two independent passes agreeing on the same bug is real signal. One pass asserting something, alone, is not — I go verify it live before it goes in a doc.
- Cite the file and line. Not in the code or docs = "not confirmed," not fact.

## 5. What I am still figuring out

- Where "verified this myself" turns into "trusted a tool's summary of verifying it" — easy to blur once a check has run clean a few times.
- How much guardrail scaffolding (AGENTS.md, playbooks like this one) is proportionate for a solo learning project vs. what only pays off on a team with turnover.
- What to do when the only available environment has a real limitation (no virtualization, couldn't run Docker here) — "disclose it, don't fake it" is right, but I don't yet know how hard to push for another way to check before accepting "can't verify here."

## Decision Card

| Situation | I reach for |
|---|---|
| New feature | A docs-first design plan before any implementation. |
| Code review | A findings table (file, line, severity) I grade myself, plus one live repro of the finding I trust most. |
| Debugging | Targeted context — only the files directly involved, not the whole repo. |
| Infrastructure | Read-only inspection first; changes to `Dockerfile`/CI/`backend/app` need the same explicit approval as graded business logic. |
| Never-paste | `.env` contents, tokens, secret-shaped strings — grep for it, never read the file body. |
| One rule | If I didn't run it and see the output myself, it doesn't go in the doc as "confirmed." |
