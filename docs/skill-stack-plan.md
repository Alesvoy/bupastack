# Skill stack plan

This plan builds the workflow that [workflow.md](workflow.md) describes. When it's done, a coordinator thread hands a ticket to an engineer thread with one command. The engineer returns a reviewed PR with QA evidence, and the coordinator briefs you before anything merges.

The plan has ten steps, numbered 0 to 9. Steps 0 to 6 build and test everything on a branch, so running agents keep the current skills. Step 7 switches over in one window. Steps 8 and 9 pilot the new flow on real tickets and decide on the last skill. Along the way the plan does these things:

- retires the leftover `harness-engineering-*` folders and any other skill you mark as unused
- copies three third-party skill folders into `vendor/`
- changes four of your skills so each does one job
- creates `handoff-to-engineer`, and decides whether to create `deploy-and-qa`

## How to read this

Work through the steps in order. Each step ends with **Evidence** boxes. Check a box only when its evidence exists, such as a file, a command's output, a PR, or a thread transcript.

- **Who does the work.** An agent in a coordinator thread for this repo, using `/pstack:poteto-mode`. You approve every merge, in this repo and in client repos.
- **Where the work happens.** In the worktree that step 0 creates, on the `skill-stack` branch. `install.sh` symlinks the skills from `~/ai/bupastack`, so running agents keep the old skills until step 7. Never run the worktree's `install.sh` with your real `HOME`.
- **How a changed skill is tested.** A fresh agent with no context reads the worktree copy by its path, such as `~/ai/bupastack-skill-stack/shared/qa/SKILL.md`. It follows that copy on a realistic case in the sandbox repo from step 0. Record where it went wrong. That is the `qa` skill's own rule for testing skills.
- **Commits.** One commit per step, on the branch. Push only when you ask.
- **Private details.** This repo is public. Client names, repo names, accounts, PR numbers, and thread IDs go in `~/.agents/repos/readiness.md` on your machine, never in this repo.

## Step 0. Set up the branch and the sandbox

- [x] Create the worktree with `git -C ~/ai/bupastack worktree add ~/ai/bupastack-skill-stack -b skill-stack main`.
- [x] Move `~/ai/bupastack/docs/` into the worktree, and commit it there when you ask.
- [x] Run `gh api user -q .login` to see which GitHub account is active. Use your personal account for the sandbox, passed per command with `GH_TOKEN="$(gh auth token -u <personal-account>)"`.
- [x] Create a private sandbox repo under your personal account. Give it a small web app, an `AGENTS.md` with its check command and PR rules, a `verify` skill, and a T3 project.
- [x] List the work in flight. Run `t3_thread_list` with statuses `running` and `waiting` for each client project, and `list_scheduled_tasks` for each project. Save both lists in `~/.agents/repos/readiness.md`.
- [x] **Evidence.** `git -C ~/ai/bupastack status --short` prints nothing. `gh repo view <sandbox> --json visibility` says `PRIVATE`. The sandbox appears in `t3_project_list`. Both lists are saved.

## Step 1. Decide the open questions by experiment

### 1a. Confirm the engineer's reviewer

The workflow defaults to `sol-loop`. Test it against `thermo-nuclear-review` before building on it.

- [x] Pick three merged PRs whose first review found real defects. Record each PR's pre-fix head commit and its known defects in `~/.agents/repos/readiness.md`.
- [x] On each pre-fix head, run two reviewers with T3 `delegate_task`, both on `gpt-6.1-sol` at `xhigh`. One gets `sol-loop`'s round-1 review prompt. The other gets `thermo-nuclear-review`'s prompt. Neither may edit code.
- [x] Score each run on known defects found, false positives, and minutes taken.
- [x] Keep `sol-loop` unless `thermo-nuclear-review` finds more known defects without more false positives.
- [x] If `thermo-nuclear-review` wins, change the review step everywhere it appears: both docs, and the engineer steps in step 5. Keep `sol-loop`'s fix loop, severity rules, and round budget, and use `thermo-nuclear-review`'s prompt for the reviewer.
- [x] **Evidence.** The score table is in `~/.agents/repos/readiness.md`. The `sol-loop` entry in `workflow.md` states the outcome, without client details.

### 1b. Choose how screenshots reach a PR

Some client repos require screenshots attached to the PR, and agents had no way to attach them.

- [ ] In the sandbox repo, open a test PR. Have a Sol agent with computer use add two screenshots to its description through github.com.
- [ ] If that fails, test the fallback. The fallback pushes the screenshots to an evidence branch in the same repo and links them from the PR. It applies only where the repo's rules allow files outside the change.
- [ ] Record which method each client repo allows in `~/.agents/repos/readiness.md`.
- [ ] **Evidence.** A second signed-in account sees the screenshots on the test PR.

## Step 2. Choose what to retire

- [x] On the branch, delete `harness-engineering-project-bootstrap/` and `harness-engineering-track-task/` with `git rm -r`. Both hold only compiled Python caches from retired skills.
- [x] List every skill in `~/.agents/skills`, `~/.claude/skills`, and `~/.codex/skills` that the [skill table](workflow.md#find-a-skill-by-job) doesn't name. Save the list in `~/.agents/repos/readiness.md`, and mark each one keep or remove. Step 7 removes the marked ones.
- [x] Delete the global memory note that tells agents to use the retired harness-engineering skills, and its line in the memory index, in `~/.claude/projects/<home>/memory/`. It points at skills that no longer exist, so deleting it now is safe.
- [x] Decide the global memory note that tells agents to use GitHub MCP tools instead of `gh`. Every PR skill uses `gh`, so the note conflicts with them.
- [x] **Evidence.** `git ls-files | grep harness` prints nothing on the branch. `grep -ri harness-engineering` in the memory folder prints nothing. The skill list has a mark on every line.

## Step 3. Copy the third-party skills into `vendor/`

Copy only the skills the workflow uses. Installing a whole set brings skills that trigger on their own and compete with yours.

- [x] Create `vendor/grilling/` and `vendor/grill-me/` from `mattpocock/skills` at commit `5beb35b`, and `vendor/sol-loop/` from `t3dotgg/tstack` at commit `7de017b`. Give each folder a `SOURCE.md` with the upstream URL and the commit.
- [x] Make `install.sh` link `vendor/*` into `~/.agents/skills/`, and add the matching links in `~/.claude/skills/`, the same way it handles `shared/*`.
- [x] Add `vendor/` and its skills to the README's layout and skill tables.
- [x] **Evidence.** In the worktree, `HOME=$(mktemp -d) sh install.sh` creates links for `grilling`, `grill-me`, and `sol-loop` in both `.agents/skills` and `.claude/skills` under the temporary home.

## Step 4. Change your skills on the branch

### 4a. Make `review-pr` brief you and own the verdict

- [x] Put the briefing first in the output. It says what the PR does for users, why, how it was proven with screenshots, what could break, and what to look at yourself.
- [x] Replace the three reviewers with the four in [workflow.md](workflow.md#review-pr), which are ticket and evidence, repo rules, code quality, and correctness. The code-quality reviewer uses `thermo-nuclear-code-quality-review`'s rubric, and it blocks only on a real defect. The correctness reviewer is skipped when `sol-loop` approved the same head commit, and the report says so.
- [x] Base READY on passing CI. When the repo has no CI, base it on the engineer's recorded result of the repo's checks for that commit.
- [x] Post the verdict comment only when the caller asks for it. Name no models in the comment where repo rules forbid mentioning AI.
- [x] Delete pre-PR mode. `sol-loop` reviews the change before a PR exists.
- [ ] **Evidence.** A fresh agent follows the worktree copy on a sandbox PR. Its output runs briefing, then findings, then verdict. It posts the comment only when told to.

### 4b. Make `raise-pr` only open the PR

- [x] Delete the sections that run the pre-PR gate, `qa`, and `review-pr`, and the section that posts the verdict.
- [x] Add the ready-or-draft rule. Open ready when the evidence covers the head commit and shows no failures. Otherwise open a draft and list what's missing under **Not verified**.
- [x] Add the [PR description format](workflow.md#pr-description-format), with the QA table and the screenshot method from 1b.
- [x] Take the GitHub account from `~/.agents/repos/<repo>.md`, or from the repo's docs when that file doesn't exist. Keep the duplicate-PR check. Add `link_pull_request`.
- [x] Rewrite the frontmatter description so it no longer promises QA, review, or a verdict.
- [x] **Evidence.** A fresh agent follows the worktree copy on a sandbox branch twice, once with passing evidence and once with none. The first PR opens ready with screenshots. The second opens as a draft and lists what's missing.

### 4c. Make `merge-pr` merge only what you saw

- [x] Accept your request in the current thread for one PR, or for a list that names the PR. Save your exact words, with the time, in the ticket's **Handoff** section when there is a ticket. Refuse approvals relayed from another thread, and open-ended ones such as "merge everything".
- [x] Merge only the head commit you were briefed on. When the head changed, brief again and wait, unless only a clean merge of the base changed it and the PR's patch ID is unchanged.
- [x] When no current verdict comment exists, run `review-pr` and ask it to post.
- [x] Give a three-line summary before the merge. Name any deploy the merge triggers. A merge request also approves a deploy to a test environment. A production deploy needs your separate confirmation before the merge.
- [ ] **Evidence.** In the sandbox, a fresh agent follows the worktree copy through four cases. It refuses to merge without your words. It merges after "merge 7". It refuses an approval relayed from another thread. It briefs you again after a new commit.

### 4d. Make `qa` plan from the ticket

- [x] Take expected results from the ticket's acceptance criteria first, then from the PR description, commits, and code.
- [x] State when to use the local target and when to use the deployed target. Keep "never deploys".
- [x] Name each evidence folder after the commit it tested, and record that commit in the report. Save screenshots where `raise-pr` reads them.
- [x] **Evidence.** A fresh agent follows the worktree copy with a sample ticket. The test plan's expected results quote the acceptance criteria, and the evidence folder carries the commit.

### 4e. Check `cleanup-pr` in the dry run

- [ ] Leave `cleanup-pr` as it is for now. Step 5's dry run checks whether it removes the engineer's worktree once the engineer thread is settled. If it can't, add a step that settles the merged PR's idle engineer thread before removal.

## Step 5. Create `handoff-to-engineer` on the branch

- [x] Write `shared/handoff-to-engineer/SKILL.md`. Its parts, in order:
  - [x] **Role routing.** A thread whose first message says "You are the engineer" follows the engineer steps and never calls `t3_thread_launch`.
  - [x] **Coordinator steps.** Write the ticket from the template if none exists, creating `~/.agents/tickets/<repo>/` when needed. Check the ticket, pick the model, launch with `t3_thread_launch` in a worktree, schedule the check-in, and record the handoff. When the report arrives, run `review-pr` and ask it to post.
  - [x] **Rework.** When the verdict is BLOCKED, send the findings to the engineer thread with `t3_thread_send`, then review again after the engineer reports.
  - [x] **Engineer steps.** Implement, clean up with `deslop` and `no-comments`, and commit. Verify with the repo's checks and tests, the `verify` skill, and `qa`. Review with `sol-loop` and `thermo-nuclear-review`'s prompt, commit any fix, and rerun the affected checks and QA. Open the PR with `raise-pr`. Wait for CI and fix failures, or record the repo's checks when the repo has no CI. Report with `t3_thread_send`, then stop.
  - [x] **Check-in step.** Read the engineer thread. Stay quiet while it runs. Post one line when it stops without a report, waits on a question, or fails. Turn the check-in off once the report arrives.
  - [x] **Settings.** Take the Sol reviewer's effort from `~/.agents/model-routing.md`. The handoff counts as your request to push the ticket's branch.
  - [x] **Codex note.** When the T3 tools aren't listed, call one of them directly before treating them as missing.
  - [x] **Never.** Merge, deploy, force-push, or change anything outside the ticket's scope.
- [x] Write `references/ticket-template.md` and `references/report-format.md` from the formats in `workflow.md`.
- [x] Follow pstack's skill-authoring playbook. The frontmatter has `name` and `description`, every link resolves, and prose that doesn't change a decision is cut.
- [ ] **Evidence.** In the sandbox, a coordinator follows the worktree copy, and the engineer's first message points at the same path. Every one of these holds:
  - [x] A ticket with an open question is refused.
  - [x] A ready ticket launches an engineer thread in a new worktree.
  - [x] The engineer's transcript has no `t3_thread_launch` call.
  - [x] The PR opens with QA evidence and screenshots, after one QA run and one review loop per head commit.
  - [x] The report arrives in the coordinator thread, and the check-in turns itself off.
  - [ ] `review-pr` briefs you and posts the verdict without being asked.
  - [x] A planted BLOCKED finding goes back to the engineer, and the PR is fixed and reviewed again.
  - [x] After you merge, `cleanup-pr` removes the engineer's worktree, or reports why it kept it.

## Step 6. Prepare each client repo

Open one PR per client repo now. Merge them in step 7, so the repo docs and the live skills change together. The per-repo list lives in `~/.agents/repos/readiness.md`.

- [ ] Move the rules that lived only in prompts into `AGENTS.md`. Take them from `readiness.md` and from the prompts of the scheduled tasks listed in step 0. They include the PR format, banned words, merge rules, and deploy steps.
- [ ] Update the merge rules in `AGENTS.md`. The engineer runs the pre-PR gate before `raise-pr`, `review-pr` posts the verdict, and a repo without CI names the local checks that stand in for it.
- [ ] Add the screenshot method chosen in 1b.
- [ ] Make sure the repo has a `verify` skill that both Claude and Codex can see, in `.claude/skills/` and `.agents/skills/`. Make sure it has a release skill, or deploy steps in `AGENTS.md`. Generate a missing `verify` skill with `create-verification-skill`.
- [ ] List the defects that QA on a deployed environment found and local QA missed in the last month. For each one, add test data or a `verify` scenario that would have caught it. Stop when every listed defect is covered.
- [ ] Write `~/.agents/repos/<repo>.md` with the facts that only apply to your machine, such as the GitHub account, browser profile, and port locks.
- [ ] **Evidence.** Each repo PR is open with green checks. A fresh Codex agent lists the repo's `verify` skill. It answers three questions from the PR's docs and the local notes alone. How do I deploy? Which GitHub account do I use? How do I prove a UI change?

## Step 7. Switch over

Do every box in one sitting.

- [x] Run `t3_thread_list` with statuses `running` and `waiting` for each client project. Wait until no engineer thread is in the middle of a task.
- [x] Back up `~/.agents/model-routing.md`, then rewrite it to the [model routing table](workflow.md#model-routing).
- [x] Set `session hook: off` in `~/.claude/pstack-models.md` and `~/.codex/pstack-models.md`.
- [x] Merge the client repo PRs from step 6. You approve each one.
- [x] On the branch, update the README's rows for the changed and new skills, and link it to `docs/workflow.md`.
- [x] Save a snapshot of the links with `mkdir -p ~/.skills-backup && ls -l ~/.agents/skills ~/.claude/skills ~/.codex/skills > ~/.skills-backup/links-before.txt`.
- [x] Merge the branch with `git -C ~/ai/bupastack merge --no-ff skill-stack`, so one revert undoes it. Then run `~/ai/bupastack/install.sh`, which adds the links for the new folders.
- [x] Move the skills marked remove in step 2 into `~/.skills-backup/<date>/`. Don't delete them yet.
- [x] Save the prompt and schedule of each old scheduled task whose prompt retypes merge rules. Then delete those tasks with `delete_scheduled_task`.
- [x] **Evidence.** `ls -l ~/.agents/skills ~/.claude/skills` shows links for `handoff-to-engineer`, `grilling`, `grill-me`, and `sol-loop`. A new Claude thread and a new Codex thread list those skills and start without the `poteto-mode` instruction.
- [ ] **Rollback, if a check fails.** Each of these undoes one box above:
  - [ ] Run `git -C ~/ai/bupastack revert -m 1 <merge commit>`.
  - [ ] Remove the links that now point nowhere with `find -L ~/.agents/skills ~/.claude/skills -maxdepth 1 -type l -exec rm {} +`, then run `install.sh` again.
  - [ ] Move the removed skills back from `~/.skills-backup/<date>/`.
  - [ ] Recreate the deleted scheduled tasks from their saved prompts with `schedule_task`.
  - [ ] Restore the routing backup, and set `session hook: on` in both pstack sheets.
  - [ ] Revert the client repo PRs.
  - [ ] Compare `ls -l` of the skill folders with `links-before.txt`.

## Step 8. Pilot on real tickets

- [ ] Hand one small real ticket per client repo to `handoff-to-engineer`. Watch each one from handoff to cleanup. You approve each merge.
- [ ] **Evidence, per pilot.** Each of these holds:
  - [ ] The engineer's transcript shows one QA run and one review loop per head commit.
  - [ ] The PR description shows the screenshots.
  - [ ] You were briefed before the merge.
  - [ ] `merge-pr` and then `cleanup-pr` ran, and the engineer thread is settled.

## Step 9. Decide on `deploy-and-qa`

- [ ] After two pilots, check how often you typed the deploy-and-QA prompt from [workflow.md](workflow.md#7-deploy-and-qa-the-deployed-app). Build the skill if you typed it after most merges. Otherwise mark it "not built" in the skill table and stop here.
- [ ] If you build it, create a new worktree and branch the way step 0 does. Write `shared/deploy-and-qa/SKILL.md` there, as [workflow.md](workflow.md#deploy-and-qa) describes. Cover repos that deploy on merge, where the skill waits and checks instead of deploying. Cover sign-in that needs you, where it asks and waits.
- [ ] Test it in the sandbox from the worktree copy. Then merge it with `--no-ff` and run `install.sh` again, so the new folder gets its links.
- [ ] **Evidence.** One dev deploy and QA run in a client repo that has a release skill. The deployed version matches the merge commit, and the QA report has evidence for each scenario. In the same session, the skill refuses production without your request.

## The plan is done when

- [ ] Every box above is checked with its evidence.
- [ ] Every skill in the [skill table](workflow.md#find-a-skill-by-job) shows **current**, or "not built" for `deploy-and-qa`.
- [ ] The status banner and the "Run the loop today" section are gone from `workflow.md`.

## Appendix A. Why the plan is ordered this way

[workflow.md](workflow.md#why-the-stack-looks-like-this) explains why the stack uses these skills. This appendix covers only the order of the work.

- **Branch first, switch over once.** The skills are symlinks, so an edit on `main` changes every running agent at once. Building on a branch keeps running engineers on the skills they started with.
- **Sandbox before client repos.** Every changed skill runs end to end on a private sandbox first. A client repo never sees an untested skill.
- **Client repo docs merge with the skills.** The repo docs describe the new flow. Merging them at the switch-over avoids a window where a repo describes skills that aren't live.
- **`deploy-and-qa` last.** It depends on `qa` and on each repo's deploy steps. Building it only when the prompt keeps repeating avoids a skill nobody uses.

## Appendix B. Risks

- **Screenshot upload may not work.** Step 1b tests it first. If neither method works in a repo, the PR links to the evidence instead, and `review-pr` shows you the screenshots in the coordinator thread.
- **Sol reviews Sol.** The engineer's review always runs on Sol, so an engineer on Sol gets a reviewer from the same model family. The code-quality reviewer in `review-pr` runs on Claude, which adds a second family before the merge.
- **A rule found only in a prompt.** Step 6 moves the known ones. Any rule that turns up later goes into the repo's `AGENTS.md`, never into a skill.
- **T3 tools load late in Codex.** A Codex agent can miss the T3 tools on its first look. `handoff-to-engineer` tells it to call one directly before reporting them missing.
- **A pilot finds a gap.** Fix the skill on a new branch, test it in the sandbox, and switch it over the same way as step 7.
