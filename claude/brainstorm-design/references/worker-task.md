# Worker task template

Replace every bracketed field before sending. The worker gets one design, not the other designs' plans. Resolve every path: a `general-purpose` subagent starts from a clean context and receives nothing but this prompt string.

Parallel workers share a scratchpad and a browser; both collide. The template keeps each worker's scratch and captures inside its own candidate directory.

```text
Build design [ID/title] for this design exploration.

Load the build-design skill (~/.claude/skills/build-design/SKILL.md) and follow its five steps.
Impeccable's quality floor for step 3: ~/.claude/skills/impeccable/reference/craft-floor.md
Brief: [absolute brief.md]. Run contract: [absolute run-contract.md].
Success sentence: [the user's success sentence].
Your direction, confirmed by the user: [direction in the user's words].
Screens in scope: [one to three screens].
Your references: [absolute image paths, each with its "This works because..." reason].
Brand assets: [absolute paths under references/brand/, or "none"].
Stack: [stack]. Output folder: [absolute candidate directory].

Write design-plan.md and handoff.md in your candidate directory. Deliver source/,
a self-contained preview/index.html with its assets (relative URLs; hash or
in-memory routes, since the preview server has no SPA fallback), tokens.json,
and evidence/verification.md with desktop and mobile captures of every screen.
Use fixture data only; no production connections or copied secrets.

Keep every scratch file, helper script, and browser profile inside a dot-prefixed
folder in your candidate directory. Write through absolute paths rooted there, and
abort if that path variable is empty. Capture with a headless browser and your own
--user-data-dir, never a shared browser. You may use helper subagents for checks.
Do not build other designs, change run metadata, edit evidence/design-review.md,
or touch the app at [path, if any].

Check once and stop, as build-design says. Report the files, how to reproduce the
build, and known issues. Stay available: the coordinator may send up to five
review fixes for one fix round.
```
