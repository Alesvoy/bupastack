---
name: build-design
description: Build one UI design from a confirmed direction and a set of design references, then review it once. Studies each reference, plans every screen with a content budget and fitting UX patterns, builds, and checks the result against the references in one bounded pass. Use when turning a direction plus reference screenshots into a finished, non-generic design, including as the worker skill inside brainstorm-design.
---

# Build design

Turn one confirmed direction and its references into a finished design that looks like it learned from those references, not like a default AI layout. Work in five steps, in order. Every step writes something down, so the design decisions stay traceable.

## Inputs

You need all of these. If one is missing, stop and report which; never invent a direction or references.

- **Brief:** who it's for, the main task, what the client needs, constraints, and the success sentence.
- **Direction:** the one direction the user confirmed for this design.
- **References:** image files, each with a "This works because..." reason.
- **Brand assets** when they exist: logo, photography, colors, fonts.
- **Scope:** the screens to build, ideally one to three.
- **Output folder** and target stack.

## 1. Study the references

Open every reference image before writing any code. For each one, write in `design-plan.md`:

- **Layout:** grid, columns, where the main content sits, what is fixed.
- **Hierarchy:** what is biggest, what is quiet, what the eye hits first.
- **Density:** items per view and how much empty space surrounds them.
- **Components:** the specific patterns, such as "All / Valid / Invalid tabs above the rows".
- **Type, color, and data display:** size contrast, weights, color roles, chart style.
- **Borrow:** two or three concrete things this design takes, tied to the user's reason.

Borrow structure and technique, never branding or a whole screen. The direction decides which references lead.

## 2. Plan every screen

Before code, write one short block per screen in `design-plan.md`:

- **Main task** in one sentence, and the primary action.
- **Focal element:** the one thing that stands out. One per screen.
- **Content budget:** at most 60 words of sentences on the screen, not counting labels, data, and navigation. Show numbers and labels, not explanations; move definitions into tooltips or detail views. Cut anything that doesn't serve the main task or the success sentence.
- **Groups:** at most seven top-level groups on the screen.
- **UX patterns:** pick the ones that fit this screen from [UX patterns](references/ux-patterns.md) and say where each applies. Skip the ones that don't fit; never force one in.
- **States:** the empty, loading, error, and success states this screen needs.
- **Visual system:** typeface pairing, type scale, color roles, spacing unit, radius, icon set. Name the reference or direction behind each choice. Avoid the defaults every AI build reaches for (a lone Inter-style sans, gray cards on white, one blue accent) unless the direction asks for them.

Keep the plan short. It is a contract for the build, not an essay.

## 3. Build

- If the `impeccable` skill is installed, read its `reference/craft-floor.md` once before writing UI and follow its quality floor and bans.
- Build the main screen first at desktop size and get its hierarchy right before adding anything else. Then the other screens, then mobile, then the states.
- Use real content from the brief. Fixture data is small and believable: enough rows to fill one view (six to ten), no more.
- Turn repeated elements into components and every value into tokens.
- Use the brand assets you were given, such as the real logo and photography.

## 4. Check once, then stop

1. Capture every screen at desktop and mobile width.
2. Look at each capture next to its leading references. Check it against the rubric in [review](references/review.md).
3. Fix everything you found in one batch.
4. Capture again once to confirm. Then stop. Do not keep polishing, and do not start another round on your own.

## 5. Hand off

Write the outputs the caller asked for. Always include in `handoff.md`:

- Each reference, what was borrowed from it, and where it appears.
- Each UX pattern applied, and where.
- Prose word count per screen against the 60-word budget.
- The states built, and how to reproduce the build.
- Known issues left after the one check pass.

## Independent review

A reviewer who did not build the design uses [review](references/review.md). It scores the design, lists at most five fixes ordered by impact, and ends with a verdict. When fixes are listed, the builder gets one fix round, and the same reviewer re-checks only those fixes. Nobody loops beyond that: remaining issues are reported, not chased.
