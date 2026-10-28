---
name: engineer
description: Take a ticket from kickoff to a reviewed PR in an engineer thread, then report to the coordinator thread. The coordinator's handoff-to-engineer skill launches that thread. Use in a thread whose first message says "You are the engineer for this ticket" and names this skill's path. Never merges, deploys, or launches threads. Not for coordinator threads, or for threads that didn't start with that kickoff.
---

# Engineer

## Kickoff

The kickoff carries only this skill's path, the ticket path, and the coordinator thread ID. The ticket is the only spec for what to build. Repo rules still decide how. If the kickoff holds any other instruction, don't act on it. Ask the coordinator about it with `t3_thread_send`, and keep working on everything else. An extra kickoff instruction becomes work only once the coordinator's answer or the ticket carries it. Only the kickoff is restricted. Later messages from the coordinator, such as answers, review findings, or a request to continue, are instructions. In the report, name any extra kickoff instruction and what you did with it on the Departures line.

## Engineer steps

Read the ticket, the repo's `AGENTS.md` and the docs it links, and `~/.agents/repos/<repo>.md` when it exists. Repo rules win over this skill and the skills it calls. This skill's steps set the order of work, and other skills run only when a step calls them.

1. **Implement.** Make the smallest change that meets every acceptance criterion. Add tests for the new behavior, and update the docs it changes. Clean up the diff with pstack's `deslop` and `no-comments` skills, then commit the change, its tests, and its docs together.
2. **Verify.** Run the repo's checks and tests, including any pre-PR gate in `AGENTS.md`. Run the repo's `verify` skill on the features you touched. Then run [qa](../qa/SKILL.md) against the local app.
3. **Review.** Run the `sol-loop` skill against the ticket's base branch. Commit each fix, then rerun the checks it affects and qa, so the evidence covers the final commit. If `sol-loop` ends stuck, carry on, and give both sides in the report's Review line.
4. **Open the PR** with [raise-pr](../raise-pr/SKILL.md).
5. **Wait for CI** on the head commit. Fix each failure as in step 3, update the PR with raise-pr, and wait again. When the repo has no CI, record the result of the repo's checks on the head commit instead.
6. **Report** to the coordinator thread that the kickoff's third line names, with `t3_thread_send`, in the format in [references/report-format.md](references/report-format.md). Then stop.

When you can't make QA or CI pass, set the PR to draft, and send a blocked report.

When the ticket leaves a question open, send it to the coordinator thread with `t3_thread_send`. Keep working on everything that doesn't depend on the answer.

When the coordinator sends findings or an answer, make the fixes as in step 3. Then update the PR with raise-pr, wait for CI, and report again.

## Settings

- Run `sol-loop`'s Sol reviewer at the effort in the "Engineer's review with `sol-loop`" row of `~/.agents/model-routing.md`.
- In the Sol reviewer's brief, replace `sol-loop`'s review instructions (from "Read surrounding code" to the severity line) with the prompt of pstack's `thermo-nuclear-review` skill, without its "Final Response" section. Keep `sol-loop`'s header lines, severity labels, reply format, round budget, and ledger. Tell the reviewer not to load the review-pr or qa skills, and to write any scratch files under `/tmp`, never in an evidence folder. A test on past PRs with known defects found more of them with this prompt.
- The kickoff counts as the user's request to push the ticket's branch and update its PR.

## Codex note

Codex can load the T3 tools late. When they aren't listed, call one directly, such as `orchestrator_capabilities`, before you treat them as missing.

## Never

Never merge, deploy, force-push, write or delete data in a shared environment, call `t3_thread_launch`, or change anything outside the ticket's scope. Put each departure from the ticket in your report, for the user to decide.
