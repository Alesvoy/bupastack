---
name: handoff-to-engineer
description: Hand a ticket with no open questions from a coordinator thread to a new engineer thread in its own worktree, check on the engineer every 20 minutes, and get its PR reviewed. It also holds the steps an engineer thread follows from ticket to PR. Use when the user asks to hand off a ticket or types /handoff-to-engineer <ticket path>, and in any thread whose first message says "You are the engineer". Never merges or deploys.
---

# Handoff to engineer

## Pick your role first

If this thread's first message says "You are the engineer", follow the [engineer steps](#engineer-steps), and never call `t3_thread_launch`. Otherwise you are the coordinator, so follow the [coordinator steps](#coordinator-steps). In an engineer thread, these steps set the order of work, and other skills run only when a step calls them.

## Coordinator steps

1. **Find or write the ticket.** Use the path the user gave. When no ticket file exists, write one from [references/ticket-template.md](references/ticket-template.md) with what this thread agreed, at `~/.agents/tickets/<repo>/<slug>.md`. Create the folder if it's missing.
2. **Check the ticket.** Refuse to hand off while the ticket has an empty header line or required section, or while **Open questions** isn't `None`. Name what's missing, and offer to resolve it with the `grilling` skill.
3. **Pick the model.** Use the model the user named. Otherwise use the "Engineer, UI work" row of `~/.agents/model-routing.md` when the ticket's Surface includes UI, and the "Engineer, other work" row when it doesn't.
4. **Launch the engineer** with `t3_thread_launch`:
   - `title`: `Engineer <slug>`
   - `workspaceStrategy`: `{type: "worktree", baseRef: "<base branch>", branch: "<ticket branch>", startFromOrigin: true}`
   - `modelSelection`: the row's provider, model, and effort, with the IDs that `orchestrator_capabilities` lists
   - `message`: this kickoff, with the absolute path of this file, and this thread's ID from `t3_thread_configuration` called without arguments

   ```
   You are the engineer for this ticket. Follow the engineer steps in the handoff-to-engineer skill at <path of this SKILL.md>.
   Ticket: <ticket path>
   Coordinator thread: <this thread's ID>
   ```
5. **Schedule the check-in** every 20 minutes with `schedule_task`. Pass `schedule: {type: "interval", everyMs: 1200000}`, `bindToCurrentThread: true`, and this prompt:

   ```
   Check-in for <slug>: run the check-in step of the handoff-to-engineer skill at <path of this SKILL.md> for <ticket path>.
   ```
6. **Record the handoff.** Write the engineer thread ID, the branch, and the check-in ID in the ticket's **Handoff** section.

While the engineer works, handle what arrives:

- **A question.** Answer it from the ticket, or ask the user and pass their answer on with `t3_thread_send`. Add each answer to the ticket.
- **The report.** Turn off the check-in with `delete_scheduled_task`. For a ready report, run [review-pr](../review-pr/SKILL.md) on its PR, and ask it to post the verdict. For a blocked report, go to [Rework](#rework).
- **The user's request to stop the engineer.** Interrupt its thread with `t3_thread_interrupt`, and turn off its check-in.
- **The merge.** After merge-pr merges the PR, settle the engineer thread with `t3_thread_organize` and `action: "settle"`. If cleanup-pr kept the engineer's worktree because the thread still held it, run cleanup-pr again.

## Rework

Send the engineer what it needs with `t3_thread_send`:

- After a BLOCKED verdict, send review-pr's blocking findings.
- After a blocked report, answer its **Needs** from the ticket, or ask the user. Add the answer to the ticket, then send it.

Then schedule a new check-in as in step 5, and record its ID in **Handoff**. When the engineer reports again, handle the report as above.

## Engineer steps

Read the ticket, the repo's `AGENTS.md` and the docs it links, and `~/.agents/repos/<repo>.md` when it exists. Repo rules win over this skill and the skills it calls.

1. **Implement.** Make the smallest change that meets every acceptance criterion. Add tests for the new behavior, and update the docs it changes. Clean up the diff with pstack's `deslop` and `no-comments` skills, then commit the change, its tests, and its docs together.
2. **Verify.** Run the repo's checks and tests, including any pre-PR gate in `AGENTS.md`. Run the repo's `verify` skill on the features you touched. Then run [qa](../qa/SKILL.md) against the local app.
3. **Review.** Run the `sol-loop` skill against the ticket's base branch. Commit each fix, then rerun the checks it affects and qa, so the evidence covers the final commit. If `sol-loop` ends stuck, carry on, and give both sides in the report's Review line.
4. **Open the PR** with [raise-pr](../raise-pr/SKILL.md).
5. **Wait for CI** on the head commit. Fix each failure as in step 3, update the PR with raise-pr, and wait again. When the repo has no CI, record the result of the repo's checks on the head commit instead.
6. **Report** to the coordinator thread with `t3_thread_send`, in the format in [references/report-format.md](references/report-format.md). Then stop.

When you can't make QA or CI pass, set the PR to draft, and send a blocked report.

When the ticket leaves a question open, send it to the coordinator thread with `t3_thread_send`. Keep working on everything that doesn't depend on the answer.

When the coordinator sends findings or an answer, make the fixes as in step 3. Then update the PR with raise-pr, wait for CI, and report again.

## Check-in step

The scheduled check-in runs this step in the coordinator thread. Read the engineer thread that the ticket's **Handoff** section names, with `t3_thread_read`.

- While the engineer runs, end the turn without a message.
- When it has stopped without a report, is waiting on a question, or has failed, post one line here, such as `Check-in, <slug>: the engineer stopped 25 minutes ago without a report. Its last step was QA. I told it to continue from QA.` Answer a waiting question as the coordinator steps say. Otherwise tell the engineer with `t3_thread_send` to continue from its last step. Never start a second engineer on the branch.
- Once its report has arrived, turn off the check-in.

## Settings

- The engineer runs `sol-loop`'s Sol reviewer at the effort in the "Engineer's review with `sol-loop`" row of `~/.agents/model-routing.md`.
- In the Sol reviewer's brief, replace `sol-loop`'s review instructions (from "Read surrounding code" to the severity line) with the prompt of pstack's `thermo-nuclear-review` skill, without its "Final Response" section. Keep `sol-loop`'s header lines, severity labels, reply format, round budget, and ledger. A test on past PRs with known defects found more of them with this prompt.
- The handoff counts as the user's request to push the ticket's branch and update its PR.

## Codex note

Codex can load the T3 tools late. When they aren't listed, call one directly, such as `orchestrator_capabilities`, before you treat them as missing.

## Never

Never merge, deploy, force-push, write or delete data in a shared environment, or change anything outside the ticket's scope. The engineer puts each departure from the ticket in its report, for the user to decide.
