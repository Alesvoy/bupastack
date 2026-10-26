---
name: brainstorm-design
description: Guide the user through framing the problem, gathering references (their own or from Mobbin), and setting a direction per design, then build several runnable UI design alternatives in parallel, one subagent per design. Each design is built with the build-design skill and reviewed once by an independent reviewer. Use for design exploration, competing directions, or variants before selecting an implementation.
---

# Brainstorm design

Guide the user through framing the problem, gathering references, and choosing how many designs to build and a direction for each. Then start one subagent per design. Each builds its design with the `build-design` skill from its direction and references, and an independent reviewer checks it once. Designs open in their own browser tabs through `design-previews`. This stage explores in isolated folders; it does not install a winner into the app.

## 1. Frame the problem

Before any design work, help the user think the problem through. Read the project's instructions, product context, current UI, tokens, component library, and design documentation first, so you only ask what they don't already answer. Detect the actual platform and stack.

Ask these in chat (they are open questions, not multiple choice):

1. Who is this for?
2. What must they do on this surface? Name the main task.
3. What does the client need from it?
4. Which constraints matter: brand, stack, content, deadlines, accessibility?
5. In one sentence, what does success look like for the design?
6. Which one to three screens should each design cover, and which states must they show (empty, loading, error, success)?

Push for specifics. Challenge vague answers such as "everyone", "modern", or "user-friendly" by asking who exactly, doing what, and how they'd know it worked. The user writes the success sentence; you may suggest wording, but they own it. Play the framing back in a few lines and get a clear yes before moving on. Subagents cannot ask the user anything later, so settle required content, states, and anything that must stay untouched here too. Keep the scope to the one to three screens that matter most; a whole app is too much for one exploration.

## 2. Gather references

Aim for about two comparable products, two examples of the same flow, and two visual references. Ask the user to either share their own (screenshots or links) or describe the direction they have in mind so you can search Mobbin for them. They can do both.

To search, use the Mobbin tools: `search_screens` for single screens, `search_flows` for multi-step journeys, and `search_sections` for website sections such as a hero or pricing block. Describe one screen or flow per query, set `platform` to `web` or `ios`, and request `jpg` images. Look at the returned images yourself, and keep only the strongest few that fit the framing. If no Mobbin tools are available, say so and continue with the user's own references.

Show your picks as a short list: each one's app, a link to its `mobbin_url`, and one line on why it fits. Open each pick with the available computer-use browser controls in the user's existing signed-in browser. Mobbin needs that session, so use the browser they already use for Mobbin rather than the app's in-app browser. Then work with the user: search for more, drop what they reject, and repeat until they accept the set.

For every accepted reference, the user finishes the sentence "This works because..." You may suggest a reason, but they confirm it. Keep each reference's link, image URL, and reason for the run.

## 3. Set directions and count

Ask the user how many designs they want and what direction each should take. Directions must come from the user and should build on the accepted references. Help them get there: suggest which references could anchor which direction, and point out directions that are too similar to each other. A direction names what makes the design different: composition, density, hierarchy, navigation, and visual language, not just accent color. Every design keeps the same content, states, and scope.

Play the final list back, one line per design with the references it draws on, and get a clear yes. Never invent a direction the user has not confirmed, and start no subagent until every direction is confirmed.

## 4. Prepare the run

Read `design-previews` and its [run contract](../design-previews/references/run-contract.md). If sibling paths do not resolve, locate that installed skill in the catalog. Create the run with `init --count <n>`.

Write `brief.md` as facts, not design: the framing, the success sentence, the screens in scope, required content and states, constraints, and each confirmed direction in the user's words. Keep it to roughly 300 words. Do not prescribe layouts, first viewports, section lists, copy, or fixture volumes; those are the design work.

Save references under the run's `references/`: download each Mobbin `image_url` (the links expire after 30 days), copy any files the user shared, and list every reference in `references/references.md` with its link, its "This works because..." reason, and the directions it serves. Put real brand assets in `references/brand/` when they exist: logo files, product or project photography, brand colors and fonts from the client's site. Then register every candidate with `candidate --skill build-design --direction "<confirmed direction>"`, and start the `design-previews` server in the background. It serves unsealed designs too, at `<url>/candidates/<id>/preview/index.html`, which is the URL reviewers use.

## 5. Build

Read [worker instructions](references/worker-task.md) and adapt the template for each design. Each worker loads the `build-design` skill (`~/.codex/skills/build-design/SKILL.md`) and follows it: study the references, plan each screen, build, check once, hand off. Give each worker only the references its direction draws on, plus the brand assets.

This skill explicitly calls for subagents. Use one worker per design with a fresh, minimal context so it does not inherit this conversation's influences. Start every worker of one wave together. Queue waves when the count exceeds free slots, and finish every requested design. Never claim parallel work that ran sequentially. If subagents are unavailable, say so and offer sequential isolated builds.

## 6. Review

When a worker reports done, check its handoff covers the brief, the direction, and the screens in scope, and that the previews render. Then start a fresh worker with a fresh, minimal context as the reviewer for that design, using [review instructions](references/review-task.md). It follows `build-design`'s review rubric and writes `evidence/design-review.md`, ending in `Verdict: ready` or `Verdict: needs fixes`.

Whenever the review lists fixes, whatever the verdict, send the listed fixes back to the original worker for one fix round, then ask the same reviewer to re-check only those fixes. After that, the design is done either way: remaining issues are reported, not chased. Never start another round, and never stop to ask the user whether to continue; keep going until every design is reviewed.

## 7. Seal and present

Delete dot-directories from each candidate (reviewers keep their screenshots under `evidence/review/`, so they survive), then seal it with the `design-previews` script. Start or reopen the server and open each design in its own tab in the browser of the app driving the session, as `design-previews` describes. Verify every tab shows its design.

Give a short sentence per design: its direction, its review scores, and any issues left after the fix round. Disclose failed or image-only designs. Suggest the user try the main task in each tab at desktop and mobile widths, and test important flows with a real person when possible. Ask them to choose one design in chat. Do not choose on the user's behalf.

Once the user explicitly chooses a current revision, run `design-system` then `implement-design` for the selected scope. A choice already made in chat needs no second confirmation. If the user only wants exploration, leave the design tabs open and wait for their choice.
