---
name: handoff-to-engineer
description: Hand a ticket with no open questions from a coordinator thread to a new engineer thread in its own worktree, check on the engineer every 20 minutes, and get its PR reviewed. The engineer thread follows the `engineer` skill. Use when the user asks to hand off a ticket or types /handoff-to-engineer <ticket path>. Never merges or deploys.
---

# Handoff to engineer

## Coordinator steps

1. **Find or write the ticket.** Use the path the user gave. When no ticket file exists, write one from [references/ticket-template.md](references/ticket-template.md) with what this thread agreed, at `~/.agents/tickets/<repo>/<slug>.md`. Create the folder if it's missing.
2. **Check the ticket.** Refuse to hand off while the ticket has an empty header line or required section, or while **Open questions** isn't `None`. Name what's missing, and offer to resolve it with the `grilling` skill.
3. **Pick the model.** Use the model the user named. Otherwise use the "Engineer, UI work" row of `~/.agents/model-routing.md` when the ticket's Surface includes UI, and the "Engineer, other work" row when it doesn't.
4. **Launch the engineer** with `t3_thread_launch`:
   - `title`: `Engineer <slug>`
   - `workspaceStrategy`: `{type: "worktree", baseRef: "<base branch>", branch: "<ticket branch>", startFromOrigin: true}`
   - `modelSelection`: the row's provider, model, and effort, with the IDs that `orchestrator_capabilities` lists
   - `message`: this kickoff, with this thread's ID from `t3_thread_configuration` called without arguments. The engineer skill path is the output of `realpath <folder of this SKILL.md>/../engineer/SKILL.md`. If that file is missing, stop and tell the user. Write the ticket path absolute, with `~` expanded.

   ```
   You are the engineer for this ticket. Follow the engineer skill at <engineer skill path>.
   Ticket: <ticket path>
   Coordinator thread: <coordinator thread ID>
   ```

   Send these three lines exactly. Put every instruction, link, or constraint the engineer needs into the ticket before launching. The engineer skill treats any extra line as a question back to you and doesn't act on it. On Claude Code, a `PreToolUse` hook blocks a launch whose kickoff departs from these lines, or an `Engineer` launch with no message.
5. **Schedule the check-in** every 20 minutes with `schedule_task`. Pass `schedule: {type: "interval", everyMs: 1200000}`, `bindToCurrentThread: true`, and this prompt:

   ```
   Check-in for <slug>: run the check-in step of the handoff-to-engineer skill at <path of this SKILL.md> for <ticket path>.
   ```
6. **Record the handoff.** Write the engineer thread ID, the branch, and the check-in ID in the ticket's **Handoff** section.

While the engineer works, handle what arrives:

- **A question.** Answer it from the ticket, or ask the user and pass their answer on with `t3_thread_send`. Add each answer to the ticket.
- **The report.** It arrives in the format in [report-format.md](../engineer/references/report-format.md), as a ready or a blocked report. Turn off the check-in with `delete_scheduled_task`. For every ready report, the first one and each one after rework, run [review-pr](../review-pr/SKILL.md) on its PR, and ask it to post the verdict. Do this even when the report's Departures or a disputed review finding need the user's decision. The briefing's "Decisions for you" line puts each decision to the user, with your recommendation. For a blocked report, go to [Rework](#rework).
- **The user's request to stop the engineer.** Interrupt its thread with `t3_thread_interrupt`, and turn off its check-in.
- **The merge.** After merge-pr merges the PR, settle the engineer thread with `t3_thread_organize` and `action: "settle"`. If cleanup-pr kept the engineer's worktree because the thread still held it, run cleanup-pr again.

## Rework

Send the engineer what it needs with `t3_thread_send`:

- After a BLOCKED verdict, send review-pr's blocking findings.
- After a blocked report, answer its **Needs** from the ticket, or ask the user. Add the answer to the ticket, then send it.

Then schedule a new check-in as in step 5, and record its ID in **Handoff**. When the engineer reports again, handle the report as above.

## Check-in step

The scheduled check-in runs this step in the coordinator thread. Read the engineer thread that the ticket's **Handoff** section names, with `t3_thread_read`.

- While the engineer runs, end the turn without a message.
- When it has stopped without a report, is waiting on a question, or has failed, post one line here, such as `Check-in, <slug>: the engineer stopped 25 minutes ago without a report. Its last step was QA. I told it to continue from QA.` Answer a waiting question as the coordinator steps say. Otherwise tell the engineer with `t3_thread_send` to continue from its last step. Never start a second engineer on the branch.
- Once its report has arrived, turn off the check-in.

## Codex note

Codex can load the T3 tools late. When they aren't listed, call one directly, such as `orchestrator_capabilities`, before you treat them as missing.

## Never

Never merge, deploy, force-push, write or delete data in a shared environment, or change anything outside the ticket's scope.
