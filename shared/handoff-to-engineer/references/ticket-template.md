# Ticket template

Write the ticket at `~/.agents/tickets/<repo>/<slug>.md`, outside every repo. Every header line and section is required, except **Constraints**, which is optional, and **Handoff**, which `handoff-to-engineer` fills.

```markdown
# <What changes, in plain words>

Repo: <repo>   Base branch: <base branch>   Branch: <branch>
Kind: <feature, bug, or chore>   Surface: <one or more of UI, backend, data, and docs>

## Goal
<Who notices what, in one or two sentences.>

## Context
- <Links to specs, designs, and screenshots.>
- <Each decision, with its date.>

## Scope
In: <what the change touches>
Out (don't touch): <what stays as it is>

## Acceptance criteria
1. <A testable result, and how to see it.>

## Edge cases
- <A case the change makes likely.>

## How to verify
- The repo's checks and tests from AGENTS.md.
- The verify skill's <journeys>.
- QA: <scenarios, screen widths, themes, and test data>.

## Constraints
<Feature flags, data rules, migrations, and performance limits.>

## Open questions
<Each open question, numbered. "None." when nothing is open.>

## Handoff
<Engineer thread ID, branch, and check-in ID. merge-pr adds the user's merge requests with their times.>
```
