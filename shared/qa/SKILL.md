---
name: qa
description: QA any change, including docs and skills, with hands-on proof that it works as intended, locally or on an environment where it's already deployed. Plans expected results from the ticket's acceptance criteria, hands the plan to an independent QA subagent, checks its evidence, and reports per scenario. Never N/A. Use for QA, browser checks, validating changes on dev, or proving a fix works. Not for code review or deployment.
---

# QA

Read the repo's `AGENTS.md` (or `CLAUDE.md`) and the docs it links for how to run the app locally, its `verify` skill or script, deployed environments, sign-in, test accounts, and what local proof can't prove. Then read `~/.agents/repos/<repo>.md` when it exists, for this machine's browser profile and port locks. Repo rules win over this skill.

## QA every change

No change skips QA. Prove each changed part works the way people will use it:

| Change | Hands-on proof |
|---|---|
| UI or behavior | Drive the app. |
| Backend, API, data | Run the real code path against local services, with real inputs and outputs, before and after. |
| Scripts, checks, validators | Run them on realistic inputs, including one that must fail and one that must pass. |
| CI workflows | Run each changed job's commands locally. After the push, confirm the workflow triggered and its latest run matches. |
| Skills and agent tooling | A fresh agent with no context runs the skill or tool on a realistic case, and reports where it went wrong. |
| Docs and agent rules | A fresh agent follows the changed instructions literally, dry-running anything irreversible, and reports every wrong, unclear, or missing step. Check links and paths too. |
| Config and dependencies | Build, start the app, and exercise a path that uses the change. |

A change that touches several rows needs each row's proof.

## Choose the target

- **Local** is the default, for a branch that hasn't merged. Drive the app on this machine in the repo's test mode, with the repo's `verify` skill when there is one. Run changed scripts, jobs, and docs here too.
- **Deployed** is for an environment the caller names. Confirm that it runs the commit under test. If it doesn't, say so and stop. This skill never deploys.

## Write the test plan

List 3 to 8 scenarios, each with steps, the expected result, and the evidence to capture, such as a screenshot, console output, or network log. Take expected results from the ticket's acceptance criteria first, quoting the criterion, then from the PR description, commits, and code. The ticket is the file the caller names, or the one in `~/.agents/tickets/<repo>/` that names the branch. Never guess, and mark any assumption as one. Include:

- The main path of the change, before and after where behavior changes.
- For a bug fix, the original failing case.
- One or two edge cases the diff makes likely, such as empty, long, error, permissions, narrow viewport, or dark mode.
- Whether any step saves data. Default to no saves. On a deployed environment, allow a save only when the user approved it for this run.

## Run once per commit

Each run tests one commit. Save its evidence outside the repo, in `~/verify-evidence/<ticket slug or branch>/<short commit>/`, and never commit it. The slug is the ticket's filename without `.md`. On a later commit, rerun each scenario that failed, was blocked, or exercises a file in `git diff --name-only <the commit it ran on>..<commit>`. Carry the rest forward with the commit they ran on, their evidence path, and why the diff can't change them. When unsure, rerun. If every scenario carries forward, skip the subagent. Evidence covers a commit when every scenario ran on it or was carried forward to it.

## Delegate

Hand the plan to a QA subagent on the "QA, local and deployed" row of `~/.agents/model-routing.md`, one per target. In T3 Code, use `delegate_task` so it runs on the routed model and effort. Elsewhere, use your runtime's subagent tool and say that routing fell back. Share the parent checkout so it sees the running app and current changes. It sees no conversation history, so the task must stand alone. For docs, rules, and skills, leave out your own context, so its confusion is real evidence. Include:

- The goal, the repo path, the branch and full commit under test, and the URL or the command that starts the app.
- The runtime the repo pins (`.nvmrc`, `engines`), with the exact `PATH` or version-manager command that selects it on this machine.
- The repo skill or script for driving the UI and for sign-in, by name. Without a repo sign-in skill, use [sign-in-with-1password](../sign-in-with-1password/SKILL.md).
- The full test plan, and the evidence folder.
- Limits: no code edits, commits, pushes, deploys, or data changes beyond what the plan allows. Reveal no credentials.
- Cleanup: stop any dev server or browser session it started, and report anything left running.
- The report format: per scenario `pass`, `fail`, `blocked`, or `plan mismatch` (the app works but differs from the plan), what it saw, and the evidence file path. For each defect, the steps to reproduce, the expected and actual results, and the evidence.

When sign-in needs the user, such as for MFA, a vault unlock, or a phone approval, relay the subagent's question to the user and wait.

## Check the evidence

Don't relay a pass you haven't checked. Open the cited screenshots or logs and confirm they show the claimed result for the commit under test. Re-run or re-delegate scenarios whose evidence is missing or unconvincing. Before you report a fail as a defect, check the intended behavior in the ticket, PR, commits, and code. A fail caused by a wrong expectation is a plan error, not a defect. Confirm that a defect also fails on the base branch before you call it pre-existing.

## Report

Write the report in the thread and as `report.md` in the commit's evidence folder, where [raise-pr](../raise-pr/SKILL.md) reads it and the screenshots it cites. Start with the full commit tested and the target. Then give a table of scenarios with the result, the commit each ran on, and the evidence path. Then list defects ordered by impact, then what wasn't covered. Label local mock-mode proof as UI-only, and anything not run against the real backend as unverified, in the repo's wording. Name the model that ran QA, and say whether routing fell back.
