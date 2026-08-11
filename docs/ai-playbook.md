# Personal AI Coding Playbook

## 1. When I reach for AI first

- Turning informal notes into a structured artifact (rubric → table, backlog → ranked list) where the structure is the hard part, not the judgment.

## 2. When I do not reach for AI

- Anything involving `.env` contents or real secrets — don't paste it in even to "ask a question about it."


## 3. My non-negotiables

- Never paste `.env`, or anything matching `secrets.`/`env:`/hardcoded-token patterns — grep first.


## 4. My review rules

- After any AI edit, read the actual diff — don't trust a "done" summary as a substitute for looking.

## 5. What I am still figuring out
- Keeping prompts as simple as possible while still preserving every detail the AI actually needs to act correctly.

## Decision Card

- For a new feature I reach for: a docs-first design plan before any implementation.
- For a code review I reach for: a structured findings table (severity + evidence + confidence), then an adversarial grading pass before trusting any finding.
- For debugging I reach for: targeted context — read only the files directly involved, not the whole repo.
- For infrastructure I reach for: read-only inspection first; treat any actual change as needing the same explicit approval as `backend/app/`.
- I will never paste `.env` contents or anything matching a secret/token pattern into an AI tool.
- My one rule is: cite the file, don't invent the finding.
