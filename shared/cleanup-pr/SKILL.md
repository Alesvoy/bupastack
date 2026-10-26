---
name: cleanup-pr
description: Clean up a completed PR task after its merge is confirmed. Remove task worktrees and temporary files and screenshots, fast-forward the local base branch, delete the task's local branches. Use after a requested merge or for post-merge cleanup; approval alone is not enough.
---

# Cleanup PR

Read the repo's `AGENTS.md` (or `CLAUDE.md`) and its post-merge policy, if any, for the remote, GitHub account, base branch, and the repo's temporary-file locations. Repo rules win over this skill. If the repo names a `gh` account, prefix each `gh` call with `GH_TOKEN="$(gh auth token -u <account>)"` and pass git the one-off credential helper shown below. If the repo's git remote uses SSH, use plain `git` and skip the credential helper.

A requested merge includes this cleanup once merged; an explicit cleanup request also authorizes these task-scoped local removals. This skill does not approve, merge, deploy, or delete remote branches.

## Confirm The Merge And Scope

1. Resolve the PR from the request or task history and read its state:

   ```sh
   gh pr view <number> -R <owner>/<repo> --json url,state,mergedAt,mergeCommit,headRefName,headRefOid,baseRefName
   git -c credential.helper= -c credential.helper='!f() { echo username=x-access-token; echo "password=$(gh auth token -u <account>)"; }; f' fetch origin
   git worktree list --porcelain
   ```

   Without a named account, use plain `gh` and `git fetch origin`. Require `MERGED` and confirm the merge commit is in `origin/<base>`. Approval, closing without merge, or a pushed branch is not a merge. Otherwise keep everything and report why.
2. List the exact task worktrees, local branches, and temporary files from the conversation, recorded paths, and git state: review worktrees, screenshots, browser-tool folders such as `.playwright-mcp/` and `.playwright-cli/`, untracked run output, the repo's listed temporary files, and temporary PR body files. A shared name prefix is not proof of ownership. Do not sweep `/tmp` or all worktrees.
3. Inspect each candidate's HEAD, tracked changes, untracked and ignored files, and running processes. Keep unknown or shared files and unfinished work; do not modify tracked files during cleanup. Never remove the main checkout, the worktree the current session runs in, or a worktree another session uses (app-managed worktrees such as `.claude/worktrees/*` included).
4. Before removing a worktree or branch, prove every local commit is preserved: its tip is an ancestor of `origin/<base>`, or exactly the PR's merged head with the merge commit in `origin/<base>` (squash merges). Commits after the merged head must be kept.

## Update The Base Branch

Find the base branch's checkout with `git worktree list --porcelain`. In its clean, idle checkout, run `git merge --ff-only origin/<base>`. If it is not checked out anywhere, fast-forward the ref only after proving the old tip is an ancestor of `origin/<base>`. Do not switch an unrelated checkout to update it.

If the main checkout is on the completed task branch and clean, switch it to the base branch before deleting the task branch. Leave a dirty, active, or diverged checkout alone: do not reset, stash, or force. Record the blocker and continue with independent safe cleanup.

## Remove Task Artifacts And Worktrees

1. Stop only processes and browser sessions the task owns, such as a dev server it started. Move the shell to a surviving checkout before removing its directory.
2. Delete only the inventoried disposable paths. Check directory contents and symlinks before recursive deletion.
3. Remove each safe linked worktree with `git worktree remove <exact-path>`. Do not use `--force`, delete registered worktrees by hand, or run a blanket `git clean`. If removal fails, keep the worktree and report why.
4. Delete the task's local branches with `git branch -d <branch>`. If it refuses only because a squash merge changed ancestry, `git branch -D` is allowed for the exact verified merged head with no worktree using it. Never delete the base branch or unrelated branches.

## Verify And Report

Recheck `git worktree list --porcelain`, local branches, and the inventoried paths. Confirm the local base branch equals `origin/<base>`, or report why not.

Report the PR, removed worktrees, branches, and artifacts, the updated base SHA, and anything kept with its reason. Do not claim complete cleanup while remnants or the base update remain blocked.
