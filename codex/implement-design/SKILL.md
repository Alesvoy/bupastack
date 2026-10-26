---
name: implement-design
description: Integrate an explicitly chosen design into a component, screen, landing page, or MVP, preserving the selected source and visual behavior. Use after design selection; does not brainstorm a new look.
---

# Implement design

Deliver the design the user selected, at the scope they selected. Prefer porting the candidate's source and assets into the application's existing architecture to re-creating it from a prose summary.

## Verify the handoff

Read `design-previews`'s [run contract](../design-previews/references/run-contract.md), the run brief, and the current `inspect` output. Resolve sibling skills through the catalog if needed. Read the explicitly selected candidate's source, preview, tokens, handoff, visual evidence, and `selection.json`. Opening or viewing a design's tab is not selection. No valid final selection means no implementation: reopen the design tabs and ask for a choice. Stale selections need renewed explicit choice; an existing valid selection needs no repeated confirmation. Never choose on the user's behalf.

For an approved outside design, record the reference and user's selection in a local handoff before integration. If only an image exists, distinguish visible requirements from unknown interactions and disclose that exact source fidelity cannot be established. Build only the behavior supported by the user's scope and project context.

Inspect the target project's instructions, build commands, components, design authority, and current behavior. Use the target path from the brief, not an incidental cwd. Read `system-handoff.md`; if missing or tied to a different selected revision, run `design-system` first. A later invocation can reuse an unchanged handoff after verifying the target files still match it. Full revamp authorization carries forward; narrow requests remain narrow.

## Integrate faithfully

Port the chosen component/screen/site into native project modules, routing, hooks, and data flows. Adapt imports and implementation mechanics while preserving layout, typography, colors, assets, density, responsive behavior, and interactions. Keep working business logic, permissions, validation, accessibility, and localization. Follow project architecture rather than copying a standalone prototype's shortcuts into production.

Replace fixtures with existing APIs/state only within the requested integration. Do not invent backend endpoints, credentials, business claims, payment flows, or hidden functionality to make a prototype seem finished. If the requested MVP includes new behavior, implement it according to the user's agreed scope and project rules. If a missing integration materially blocks the intended result, describe that specific dependency and continue independent authorized work.

Match all requested states, not only the initial screenshot. Keep hover/focus/active/disabled states, overlays, loading/empty/error behavior, and mobile layout consistent with the selected design. Fix functional or accessibility defects without silently changing its identity. If a necessary correction visibly changes an approved design, show the difference and explain it; ask for direction only when it requires an unresolved design/scope choice.

Do not rerun an aesthetic generator, combine runners-up, substitute a different font or asset without explanation, or add screens the user did not choose. A missing asset/license or an incompatible dependency is a concrete limitation to resolve with the closest faithful supported option and disclose. Reuse the existing stack and dependencies where possible.

## Verify and deliver

Build/run the integration and compare real captures of the implemented UI against the preserved candidate at the same viewport, theme, content, and state. Check responsive targets and the important interaction paths; inspect side by side, since text inspection cannot establish visual fidelity. Run relevant existing checks required by the project. Work in bounded passes: inspect all target views, fix demonstrated defects in a batch, confirm. Do not claim pixel accuracy or complete QA without evidence.

Record in `implementation.md` at the run root: selected candidate/revision, target files, build/check results, before/reference/after captures, integration behavior, and any remaining deviations or limitations. If selection changed while working, reconcile with the user's latest explicit choice before continuing; never silently implement a previously chosen candidate after the user switches.

Finish with the implemented scope, verification, and any material limitation. Do not imply all app screens were redesigned when only one surface was selected. Close with a concise next-use cue: “For more components or screens, run `$brainstorm-design` with the updated scope.” Publishing, merging, and production release remain governed by the user's separate instructions.
