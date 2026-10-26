---
name: qa
description: QA every change by hands-on proof that it works as intended - the app for UI and behavior, real runs for backend, scripts, CI, and skills, and a fresh agent following the instructions for docs and agent rules. Writes a test plan, hands it to a QA subagent, checks its evidence, and reports per scenario. Never N/A. Use for QA, browser checks, validating dev changes, or proving a fix works; not for code review or deployment.
---

# QA

Read the repo's `AGENTS.md` (or `CLAUDE.md`) and the docs it links for: how to run the app locally, its UI verification skill or script, hosted or dev access, test accounts, evidence location, and what local proof cannot prove. Repo rules win over this skill. Read `~/.agents/model-routing.md` for which model runs QA and how to delegate.

## QA Every Change

No change skips QA. Prove each changed part works the way it will actually be used:

| Change | Hands-on proof |
|---|---|
| UI or behavior | Drive the app (local, or the dev environment). |
| Backend, API, data | Run the real code path against local services: real inputs, real outputs, before and after. |
| Scripts, checks, validators | Run them on realistic inputs, including one that must fail and one that must pass. |
| CI workflows | Run each changed job's commands locally. After the push, confirm the workflow triggered and its latest run matches. |
| Skills and agent tooling | A fresh agent with no context runs the skill or tool on a realistic scenario; report where it went wrong. |
| Docs and agent rules | A fresh agent follows the changed instructions literally to do what they describe (dry-run anything irreversible), and reports every step that is wrong, ambiguous, or missing. Check links and paths too. |
| Config and dependencies | Build, start the app, and exercise a path that uses the change. |

A change touching several rows needs each row's proof.

## Choose The Target

- **Local** (default): this machine — the app in whatever mode the repo uses for auth-free testing, or the scripts, jobs, and docs being changed.
- **Dev / hosted**: an already deployed environment. This skill never deploys. If the change is not deployed there, say so and stop, or ask the user to approve a deploy separately.

## Write The Test Plan

From the diff, PR, or requirements, list 3–8 scenarios. For each: the steps, the expected result, and the evidence to capture (screenshot, console, network). Take expected results from the PR description, commit messages, and code, never from a guess; mark any assumption as one. Include:

- The main path of the change, before and after where it changes behavior.
- For a bug fix, the original failing case.
- One or two edge cases the diff makes likely (empty, long, error, permissions, narrow viewport, dark mode).
- Whether any step saves data. Default to no saves; name any save the plan allows.

## Delegate

Hand the plan to the QA role from the routing file, with one QA subagent per target. For docs, rules, and skills, the subagent must start without your context, so its confusion is real evidence. The task must stand alone, because the child sees no conversation history:

- The goal, the repo path, the branch and commit under test, and the URL or the command to start the app.
- The runtime the repo pins (`.nvmrc`, `engines`), with the exact `PATH` or version-manager command that selects it on this machine.
- The repo skill or script to use for driving the UI and for sign-in, by name.
- The full test plan.
- Limits: no code edits, commits, pushes, deploys, or data changes beyond what the plan allows. Do not reveal credentials.
- Cleanup: stop any dev server or browser session it started, and report anything left running.
- Report format: per scenario `pass | fail | blocked | plan mismatch` (the app works but differs from the plan's expectation), what was observed, and the evidence file path in the repo's evidence location, outside tracked files. For each defect: steps to reproduce, expected and actual results, and evidence.

Share the parent checkout so the child sees the running app and current changes. If sign-in needs the user (MFA, vault unlock, phone approval), relay the child's question to the user instead of guessing.

## Check The Evidence

Do not relay a pass you have not checked. Open the cited screenshots or logs and confirm they show the claimed result for the right build. Re-run or re-delegate scenarios whose evidence is missing or unconvincing. Before reporting a fail as a defect, check the intended behavior in the PR, commits, and code; a fail caused by a wrong expectation is a plan error, not a defect. Confirm a reported defect also fails on the base branch before calling it pre-existing.

## Report

A table of scenarios with result and evidence path, then defects ordered by impact, then what was not covered. Label local mock-mode proof as UI-only and anything not exercised against the real backend as unverified, using the repo's wording. Name the model that ran QA and whether routing fell back. Keep evidence out of tracked files.
