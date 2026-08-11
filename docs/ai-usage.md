# Personal AI Usage Rules

**Status:** Draft — rules 2 and 3 pending course evidence
**Source:** Derived only from `docs/governance-worksheet.md`

Three personal rules for how I use AI coding tools during this course, drafted from my governance
worksheet notes only. Rules without direct evidence in the worksheet are marked as missing rather
than invented.

| Rule category | Draft rule | Evidence from my notes | What is still vague? | Revised rule |
|---|---|---|---|---|
| 1. What I will never paste | Never paste anything containing secrets, tokens, credentials, or production config into an AI chat. | Risk rubric, High tier: "credentials, tokens, secrets, production config, real customer/user data, regulated data, or code I am not authorized to share." Also the Task Tracker Code row's safer version: "keep confirming that `.env` stays out of anything shared," and the Dockerfile/CI YAML row's safer version: "grep for `secrets.`, `env:`, or hardcoded tokens before pasting CI config." | "Never paste secrets" doesn't say *how* you'd know before pasting — the notes give a specific check (grep for `secrets.`, `env:`, hardcoded tokens, confirm `.env` excluded) but that check isn't stated as a required step, only as a "safer future" suggestion. | Before pasting any file, terminal output, or config into an AI chat, grep it for `.env` references, the literal strings `secrets.` or `env:`, and anything that looks like a credential or token. If any match, exclude that file or section — do not paste it "just this once." |
| 2. What I will always verify before accepting | Missing - add course evidence | The worksheet's "Ambiguity to resolve" column repeatedly asks me to confirm a fact before finalizing a *risk classification* (e.g. "Confirm public vs. private before finalizing," "What exactly was in the test output... that distinction is the difference between Low and a mild Medium bump") — but this is about verifying facts for a risk rating, not about verifying an AI-generated code suggestion or answer before accepting it into my work. | N/A — there's nothing in these notes yet about checking AI's actual output (code correctness, whether a suggested fix matches the real business rule, etc.), so a rule here would be invented, not evidenced. | Missing - add course evidence |
| 3. How I will record AI contributions | Missing - add course evidence | The worksheet contains a risk rubric and a table of what was shared and its risk level — it does not mention logging, attribution, commit tagging, or any other way of recording that AI was involved in a piece of work. | N/A — same issue: no basis in these notes to draft a concrete rule without inventing one. | Missing - add course evidence |

## Next step

Only rule 1 has real support in the worksheet. Rules 2 and 3 need new entries in
`docs/governance-worksheet.md` (e.g., a specific instance where I did or didn't verify an AI
suggestion, or a specific way I tagged/logged AI help) before they can become concrete rules
instead of guesses.
