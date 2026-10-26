# Design review

Used by the builder for its one self-check, and by an independent reviewer who did not build the design. Review what renders, not what the code intends.

## How to review

1. Read the brief, the direction, `design-plan.md`, and `handoff.md`.
2. Open the leading reference images.
3. Open every screen at desktop and mobile width, using your own headless browser, never a shared one. Try the main task once, with the mouse and with the keyboard.
4. Score each area from 1 (poor) to 5 (excellent), with one line of evidence (a screen, a region, or a file).

## Rubric

| Area | What a 5 looks like |
|---|---|
| Glance test | Within five seconds you can say what the screen is for and what to do next. |
| Main task | The success sentence can be achieved without instructions. |
| Direction | The design clearly follows its confirmed direction and differs from the other designs. |
| References | The borrowed layout, hierarchy, and components listed in the plan are visibly there. |
| Content economy | Each screen stays within its 60-word budget of sentences; nothing is there that doesn't serve the task. |
| Focus | Exactly one focal element per screen; the rest steps back. |
| Craft | Type scale, spacing, alignment, and color are consistent and intentional; nothing looks default. |
| UX patterns | The chosen patterns are applied where the plan says; none is forced or manipulative. |
| States and mobile | The planned empty, loading, error, and success states exist; mobile keeps the main task usable. |
| Accessibility | Text contrast passes WCAG AA, focus is visible, and the main task works by keyboard. |

Also flag these AI tells when you see them: explanatory sentences on every card, cards nested in cards, identical card grids, small uppercase labels above every heading, gradient text, emoji as icons, decorative charts with no insight, and made-up placeholder names or claims.

## Output

Write `evidence/design-review.md`:

1. The score table with evidence.
2. Only the fixes worth making now, at most five, ordered by impact. Zero is fine. Each fix names the screen, the problem, and the change. No style nitpicks unless they break the rubric.
3. A last line of exactly `Verdict: ready` or `Verdict: needs fixes`. Choose "needs fixes" when an area scores 2 or lower or the main task fails. Any listed fix gets one fix round either way, so list only what is worth fixing now.

On a re-check after the fix round, check only the listed fixes, update the file, and give a final verdict. Do not add new findings; mention any new severe problem under "Known issues" without changing the verdict rules.
