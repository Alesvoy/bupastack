---
name: raise-pr
description: Create or update a pull request that is safe to merge on arrival - runs the repo's pre-PR gate, QA, and a pre-PR review, then opens the PR with a plain-language description and a merge verdict pinned to the head SHA. Use when asked to raise, open, or update a PR or its description; not for merging or deploying.
---

# Raise PR

## Read The Repo Rules First

Read the repo's `AGENTS.md` (or `CLAUDE.md`) and the PR, git-convention, and validation docs it links. They supply the remote, base branch, GitHub account, branch and commit naming, required checks, evidence rules, and deploy boundaries. Repo rules win over this skill. Where the repo is silent, use plain `git`/`gh`, the default branch as base, and Conventional Commits.

**GitHub account.** If the repo names a `gh` account, scope it per command instead of switching accounts:

```sh
GH_TOKEN="$(gh auth token -u <account>)" gh <command> -R <owner>/<repo>
git -c credential.helper= -c credential.helper='!f() { echo username=x-access-token; echo "password=$(gh auth token -u <account>)"; }; f' push -u origin "$(git branch --show-current)"
```

Never print a token, write it to a file, or run `gh auth switch` / `gh auth setup-git`. If the repo's git remote uses SSH, use plain `git` and skip the credential helper.

## Prepare

The goal is a PR that is safe to merge the moment it opens. Everything CI or a reviewer would catch is caught here first.

1. Inspect `git status --short --branch`, the full branch diff against the remote base, and staged/unstaged changes. If on the base branch or a non-conforming branch, create or rename a purpose branch per the repo's conventions. Preserve unrelated work and stage explicit paths only.
2. A request to open or update the PR authorizes the scoped commits, push, PR write, and verdict comment; do not ask again. It does not authorize a merge, deployment, or unrelated cleanup.

## Pre-PR Gate

Run the repo's Merge Contract gate (in `AGENTS.md`; if absent, the checks its validation docs and CI workflows run). Use the runtime the repo pins.

1. Fetch and rebase or merge the latest base so the gate runs against what will actually merge.
2. Run every local equivalent of the CI jobs the diff triggers, required and advisory alike. A check CI would fail is a failure here, even if GitHub would not block on it.
3. Validate the branch name, every commit subject, and the planned PR title with the repo's validators.
4. Update ledgers and baselines the contract names in the same commit as the change that moves them.
5. Record failures as they are; never present them as passes. Check whether a failing test also fails on the base branch. Fix anything this diff caused before continuing.

## QA

Run the [qa skill](../qa/SKILL.md) for every change, whatever its type, unless current QA evidence already covers the final diff. List blocked and environment-only items without counting them as passes. Never commit run output or screenshots. Label anything not proven against the real backend or hosted environment as unverified, using the repo's wording.

## Review Before Opening

Commit, then run [review-pr](../review-pr/SKILL.md) in pre-PR mode on the branch. Fix blocking findings that are within this change's scope, rerun the affected gate checks, and re-review the new commits. Stop after three rounds, or sooner when a finding needs the user's decision: then open as a draft and list the open findings under Known blockers.

## Write The Description

Use the repo's PR description format if it has one. Otherwise write for a reviewer new to the codebase: short bullets, plain words, only the context needed.

1. **Summary**: 1–3 bullets, biggest impact first, old and new behavior for the user.
2. **Review focus**: 1–3 priorities from the actual diff. Link the code, say what to check and why.
3. **Validation**: commands and results, then before/after evidence for the same scenario. Bug fixes need the failing case before and the corrected case after. Name what remains unverified.
4. **Known blockers**: missing proof and baseline failures, or `None`. If required evidence cannot be obtained, say what and why and open as a draft.
5. **Deployment**: only when deployed or planned.
6. Cut anything that does not help a reviewer understand, focus, or verify the change.

End the body with your tool's attribution line if its instructions require one.

## Publish

1. Commit with a subject that passes the repo's commit check. Skip for a metadata-only update. Do not rewrite published history unless asked.
2. Push the branch with the account from the repo rules.
3. Look for an existing open PR first: `gh pr list -R <owner>/<repo> --head "$(git branch --show-current)" --state open --json number,url,baseRefName,headRefName,isDraft`. Update a matching PR; do not silently retarget one whose base differs.
4. Write the body to a temporary file outside the repo and pass `--body-file` to `gh pr create --base <base> -R <owner>/<repo>` or `gh pr edit`. Title it per the repo's PR title rule. Open ready for review only when the review verdict was READY; otherwise open as a draft.
5. If a write times out or is ambiguous, re-read the remote state before retrying so you cannot create a duplicate PR.

## Post The Verdict

1. Confirm the remote head SHA equals the reviewed SHA. If they differ, review the new commits first.
2. Wait for CI on that head (`gh pr checks <number> -R <owner>/<repo> --watch`), and judge each check by its latest run. Rerun a known-flaky job once, as the contract allows, before calling it failed.
3. Post the merge verdict from review-pr as a PR comment (`gh pr comment <number> --body-file <file>`), with the CI results filled in. It is READY only if review-pr's verdict was READY and every CI check passed. If CI failed, fix it, push, and repeat this section; do not leave a stale READY verdict on an older SHA.

## Verify And Hand Off

```sh
gh pr view <number> -R <owner>/<repo> --json url,title,body,baseRefName,headRefName,headRefOid,isDraft,files,statusCheckRollup
```

Check the title, body, base/head, draft state, file list, and verdict comment against the intended diff. Report check states accurately.

Return the PR URL, a short change summary, the verdict, validation and blockers, and the branch. A READY verdict means the user can ask for [merge-pr](../merge-pr/SKILL.md). Opening a PR does not trigger cleanup; after a confirmed merge, use [cleanup-pr](../cleanup-pr/SKILL.md).
