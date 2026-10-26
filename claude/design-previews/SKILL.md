---
name: design-previews
description: Create or reopen a design run and open each design alternative in its own browser tab inside the Claude or Codex app, then record the user's final choice from chat. Use for reviewing designs, including outputs from brainstorm-design.
user-invocable: true
argument-hint: "[init|serve|inspect] [run path or title]"
---

# Design previews

Open every design in its own tab in the browser built into the app driving the session, so the user reviews them where they already work. This is a global skill: detect the current project and keep run data outside its working tree by default. The bundled Python 3.9+ script needs no packages or build step.

## Start or resume

Read [the run contract](references/run-contract.md) before creating or changing a run. Resolve this skill's actual directory rather than assuming a fixed home path; commands below use `previews_skill` for it. A user-level install lives at `~/.claude/skills/design-previews`; a vendored copy lives under the project's `.claude/skills/`.

```sh
python3 "$previews_skill/scripts/pipeline.py" init --title "Settings alternatives" --count 3 --project "$project_root"
python3 "$previews_skill/scripts/pipeline.py" serve --run "$run_dir"
```

`init` prints the new run directory. Omit `--project` for a standalone concept. `--run-dir` chooses a custom location; existing directories are never overwritten. The default storage root is `$XDG_DATA_HOME/claude/design-pipeline/runs`, falling back to `~/.local/share/claude/design-pipeline/runs`. Reopen by running `serve` with the existing run directory. Ask which run only if context and saved run titles cannot resolve it.

## Add designs

The coordinator owns run metadata; workers own separate candidate directories. Register direction and skill with `candidate`, then use `seal` only after inspecting the output:

```sh
python3 "$previews_skill/scripts/pipeline.py" candidate --run "$run_dir" --id design-1 --title "Compact workspace" --skill none --direction "Dense controls, broad content area" --status running
python3 "$previews_skill/scripts/pipeline.py" seal --run "$run_dir" --id design-1
```

Each candidate includes editable source, a self-contained `preview/index.html`, assets, design tokens, a handoff, verification evidence, and a design review whose last line is `Verdict: ready` or `Verdict: needs fixes`. See the contract for the exact layout. Preserve the candidate's real design. Serve built static output with relative asset paths. Framework prototypes should use their own dependency tree and fixture data, then export a static preview. Never point a candidate at a live authenticated application or production API.

For existing alternatives, copy their source and built previews into separate candidate folders and document provenance. Screenshots alone can be shown using an HTML image wrapper, but label the candidate as an image-only reference and explain that interaction and source fidelity cannot be verified. It cannot satisfy a request for a working implementation prototype without additional source work.

Failed or unfinished designs get no tab; report their status and reason in chat. Never pass off a placeholder as a finished alternative. Revisions go in a fresh run when an earlier selected version needs preserving; do not rewrite an approved snapshot.

## Open each design in a tab

`serve` binds to `127.0.0.1`, chooses a free port, and prints JSON whose `previews` map has one URL per ready design. Run it in a persistent background shell. A design sealed after the server starts is served too, at `<url>/candidates/<id>/preview/index.html`.

Open one tab per design in the browser of the app you are running in. Never open the other app's browser:

- **Claude app:** call `preview_start` with each preview URL. Every call opens a new tab in the browser pane.
- **Codex app:** use the computer-use browser controls to create one visible `iab` tab per preview URL, then call `tab.markDeliverable()` on each tab so they stay open after the turn.
- **Elsewhere:** use any available browser tool, one tab per design.

Confirm each tab shows its design, not an error. Then list in chat each design's ID, title, direction, and the first 8 characters of its revision, plus the run path. Keep the server alive for review. Stop only its own process when asked or when replacing it. Restart the same run if the session ends; previews and selection remain on disk. Do not deploy previews unless separately requested.

## Choose

The user chooses in chat. No design is chosen by default, and opening, viewing, or discussing a design is not approval. When the user names one design unambiguously, record that choice without asking again. Use the revision you presented and verify it is still current; do not substitute a newly sealed revision that the user has not seen:

```sh
python3 "$previews_skill/scripts/pipeline.py" choose --run "$run_dir" --id design-2 --revision "$revision" --user-statement "Use design 2"
```

Never run `choose` to infer the user's preference, to pick your favorite, or to bypass a missing answer. An explicit revision is required so the command cannot silently approve changed output. A later source change makes the choice stale; implementation waits for renewed explicit choice of the new revision. `inspect` prints status, revisions, and selection validity.

```sh
python3 "$previews_skill/scripts/pipeline.py" inspect --run "$run_dir"
```

Report partial output honestly. After the user chooses, continue with `design-system` and then `implement-design`, each invoked through the Skill tool, for the authorized scope.
