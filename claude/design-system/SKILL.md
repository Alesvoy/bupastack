---
name: design-system
description: Establish, extend, or replace an app's design system from an explicitly selected design. Use after reviewing design alternatives or when the user approves a concrete design reference; preserves existing authority unless a full revamp is requested.
user-invocable: true
argument-hint: "[run path or selected reference]"
---

# Design system

Make the selected design reproducible across the requested app scope. Extract what the user actually chose from source and rendered output; do not generate a new aesthetic.

## Resolve the selected reference

For a pipeline run, read `design-previews`'s [run contract](../design-previews/references/run-contract.md), then run its `inspect` command. The sibling path resolves from this skill's own directory; locate the installed `design-previews` directory if it does not. Read the brief, selected candidate's source, preview, tokens, handoff, evidence, and current `selection.json`. Opening or viewing a design's tab is not selection. No valid final selection means no app or design-system mutation: reopen the design tabs and ask the user to choose. A stale selection requires renewed explicit choice of the changed revision. Do not approve it yourself.

An explicit choice already recorded in `selection.json` or made unambiguously in chat satisfies the selection requirement. Record chat selection with the `design-previews` script; do not request the same approval again. For an outside reference, require the user's explicit selection, preserve a local snapshot/source reference, and record it in the handoff. An image-only reference supports visual extraction but cannot establish unobserved behaviors or exact source values.

Read project instructions and inspect actual design authority: source tokens, theme configuration, shared components, docs, and existing rendered UI. Missing `DESIGN.md` alone is not proof that no design system exists. Identify the target repo from the brief or user; do not assume the current cwd is the integration destination.

## Choose the scope of change

- **No existing system:** establish one using the selected design's actual values and reusable patterns.
- **Existing system, ordinary addition/refinement:** preserve and extend it. Reuse equivalent tokens/components; add what the selected scope needs. Do not recolor unrelated screens through a global token as a shortcut. Use scoped aliases or component variants when necessary to reproduce the chosen surface.
- **Explicit full design revamp:** make the selected design the new authority. Snapshot the old design docs/tokens into the run for traceability, then replace conflicting active values and documentation so there is one current system. Update affected themes, imports, generated sidecars, or consumers required by the agreed global scope. Do not leave contradictory active systems or spread old and new defaults arbitrarily. Preserve product behavior, data, routes, and factual copy.

The user's original request for a full revamp plus explicit design selection is sufficient; do not ask again. Selection alone does not expand a component/screen request into an app-wide revamp. If the chosen design genuinely cannot be reproduced within the authorized boundary, explain the concrete conflict and ask only for that unresolved scope decision.

## Establish the source of truth

Extract semantic colors and states, typography/font files and licenses, spacing, dimensions, radii, elevation, borders, breakpoints, density, icon usage, and motion actually present in the selected implementation. Map raw values into the project's existing token format where possible. Capture reusable component contracts and key states. Keep guidance proportional: a selected component does not justify a large framework, new package, or invented patterns for unseen screens.

Implement the token/theme changes and reusable primitives necessary for the selected scope. Update the existing canonical design documentation, or create `DESIGN.md` when no convention exists. Include authority/provenance, tokens and code locations, component usage, responsive/theme rules, and a concise distinction between shared rules and intentional surface exceptions. Documentation must match the code. Do not leave a generated recommendation file as the source of truth if it differs from the selected preview.

Preserve the selected artifact. Record changes in the run's `system-handoff.md`: candidate ID/revision, target project, create/extend/replace mode and its authorization, token/component mappings, files changed, global effects, checks, limitations, and what implement-design must port. If invoked outside a pipeline, put the handoff in the user's artifact workspace and state its path.

Check affected theme/component rendering and relevant project checks. For a revamp, verify representative existing consumers as well as the chosen surface. Changes needed only to wire the selected page belong in the next stage. Do not claim unseen screens have been redesigned merely because they inherit new tokens.

If the user requested the complete pipeline, continue directly into `implement-design` through the Skill tool. If they asked only for a design system, deliver the system and handoff without adding unrelated screens. Tell the user when more UI work needs a new `/brainstorm-design` scope.
