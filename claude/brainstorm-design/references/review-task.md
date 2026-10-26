# Review task template

Send this to a fresh `general-purpose` subagent (never a fork) once a worker reports done. The reviewer must not be the worker that built the design.

```text
Review design [ID/title]. Do not edit the design; your only output is
[absolute candidate directory]/evidence/design-review.md.

Follow the review rubric in [absolute build-design references/review.md].
Brief: [absolute brief.md]. Direction: [direction in the user's words].
Leading references: [absolute image paths]. Plan and handoff: [absolute
design-plan.md and handoff.md].
Open every screen at [preview URL] at desktop and mobile width with a headless
browser and your own --user-data-dir under [absolute candidate directory]/.review.
Save your screenshots under [absolute candidate directory]/evidence/review/;
.review is deleted before sealing.

End the file with "Verdict: ready" or "Verdict: needs fixes". Stay available:
after one fix round you will be asked to re-check only the listed fixes.
```
