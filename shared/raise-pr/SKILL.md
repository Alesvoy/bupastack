---
name: raise-pr
description: Open or update a pull request that follows the repo's PR rules, with a plain-language description, the QA results and screenshots, and a ready or draft state set by the evidence for the head commit. Use when asked to raise, open, or update a PR or its description. Doesn't run checks, QA, or reviews, post a verdict, merge, or deploy.
---

# Raise PR

Read the repo's `AGENTS.md` (or `CLAUDE.md`) and the PR and git-convention docs it links, then `~/.agents/repos/<repo>.md` when it exists. They supply the remote, base branch, branch and title format, evidence rules, and screenshot method. Repo rules win over this skill. Where the repo is silent, use the default branch as base and Conventional Commits.

A request to raise or update the PR authorizes the scoped commits, the push, and the PR write. It doesn't authorize a merge, a deploy, or unrelated cleanup.

## Use the right GitHub account

Take the account from `~/.agents/repos/<repo>.md`, or from the repo's docs when that file doesn't exist. Scope it to each command instead of switching accounts:

```sh
GH_TOKEN="$(gh auth token -u <account>)" gh <command> -R <owner>/<repo>
git -c credential.helper= -c credential.helper='!f() { echo username=x-access-token; echo "password=$(gh auth token -u <account>)"; }; f' push -u origin "$(git branch --show-current)"
```

Never print a token, write it to a file, or run `gh auth switch` or `gh auth setup-git`. If the git remote uses SSH, use plain `git` and skip the credential helper.

## Prepare the branch

Inspect `git status --short --branch` and the diff against the remote base. On the base branch, or on a branch that breaks the repo's naming rule, create or rename a branch that follows it. Commit uncommitted work for this change in the repo's commit format, staging explicit paths only. Keep unrelated work, and don't rewrite published history unless asked.

Where the repo's rules forbid mentioning AI, name no model or AI tool in commits or the PR, and add no attribution or co-author line. Otherwise follow your tool's attribution instructions.

## Set ready or draft from the evidence

Find the evidence for the head commit: the repo's check results from this thread, and the QA report in the folder that [qa](../qa/SKILL.md) names after the commit. Find it with `find ~/verify-evidence -type d -name <short head sha>`. Don't run checks, QA, or reviews here.

Open the PR ready for review only when the evidence covers the head commit, as qa defines, and shows no failures. Otherwise open it as a draft and list what's missing under **Not verified**. Apply the same rule when you update a PR, with `gh pr ready` or `gh pr ready --undo`.

## Write the description

Use the repo's PR format when it has one. Otherwise write these `##` sections, in this order, in plain words a reader takes in within a minute:

1. **What this does.** Old behavior, then new behavior, for the people who use it.
2. **Why.** One or two sentences.
3. **How it was tested.** A table with `Scenario`, `Result`, and `Evidence` columns, then before and after screenshots of the main scenario.
4. **Risks.** What could break, and what to check.
5. **Not verified.** What the evidence doesn't cover, or "Nothing".
6. **Out of scope.** What this PR leaves for later.

Add screenshots by the method that the repo's docs or `~/.agents/repos/<repo>.md` name. If neither names one, link the evidence paths. Never commit evidence to the PR's branch.

## Open or update the PR

1. Push the branch with the account above.
2. Look for an open PR first: `gh pr list -R <owner>/<repo> --head "$(git branch --show-current)" --state open --json number,url,baseRefName,isDraft`. Update a match. Don't silently retarget one whose base differs.
3. Write the body to a temporary file outside the repo. Pass it with `--body-file` to `gh pr edit <number>`, or to `gh pr create --base <base> -R <owner>/<repo>` with `--draft` when the evidence calls for it. Title the PR by the repo's title rule.
4. If a write times out or its result is unclear, re-read the remote state before you retry, so you never create a duplicate PR.
5. When the T3 `link_pull_request` tool is available, link the PR to this thread.

## Check and hand off

```sh
gh pr view <number> -R <owner>/<repo> --json url,title,body,baseRefName,headRefName,headRefOid,isDraft,files
```

Check the title, body, base, head, draft state, and files against the intended change. Return the PR URL, the head commit, ready or draft, and what isn't verified.
