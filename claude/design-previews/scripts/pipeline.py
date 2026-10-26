#!/usr/bin/env python3
"""Create, inspect, and serve durable local design runs without dependencies."""

import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit
from uuid import uuid4

SKILLS = ("none", "build-design")
IGNORED = {"node_modules", ".git", "__pycache__", ".DS_Store", ".cache", ".next"}
LOCK = threading.RLock()


def now():
    """Return a portable UTC timestamp for persisted review records."""
    return datetime.now(timezone.utc).isoformat()


def read_json(path, default=None):
    """Read a record, using the default only when it has not been created."""
    return json.loads(path.read_text()) if path.exists() else default


def write_json(path, value):
    """Replace one record atomically so browser reads never see partial JSON."""
    temporary = path.with_name(path.name + "." + uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def manifest(run):
    """Reject incompatible runs before accessing their candidate records."""
    data = read_json(run / "manifest.json")
    if not data or data.get("schemaVersion") != 1:
        raise ValueError("Not a supported design run (schemaVersion must be 1)")
    return data


def candidate_path(run, candidate_id):
    """Resolve only an ID registered in this run."""
    if candidate_id not in manifest(run)["candidateIds"]:
        raise ValueError("Unknown candidate")
    path = run / "candidates" / candidate_id
    if path.is_symlink() or path.resolve().parent != (run / "candidates").resolve():
        raise ValueError("Candidate must be a directory inside this run")
    return path


def content_files(candidate):
    """Enumerate portable artifacts, excluding dependency and build caches."""
    for directory, folders, files in os.walk(candidate):
        folders[:] = sorted(name for name in folders if name not in IGNORED)
        for name in folders + sorted(files):
            path = Path(directory) / name
            relative = path.relative_to(candidate)
            if name in IGNORED or relative.as_posix() == "candidate.json":
                continue
            if path.is_symlink():
                raise ValueError("Copy candidate assets instead of symlinking them: " + str(relative))
            if path.is_file():
                yield path


def fingerprint(candidate):
    """Bind approval to the source, preview, tokens, handoff, and evidence bytes."""
    digest = hashlib.sha256()
    for path in content_files(candidate):
        digest.update(path.relative_to(candidate).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def validate_output(candidate):
    """Check structural completeness; visual quality still needs human/agent review."""
    for name in ("preview/index.html", "tokens.json", "handoff.md", "evidence/verification.md", "evidence/design-review.md"):
        path = candidate / name
        if not path.is_file() or not path.read_text().strip():
            raise ValueError("Missing or empty artifact: " + name)
    if not (candidate / "evidence/design-review.md").read_text().strip().splitlines()[-1].startswith("Verdict: "):
        raise ValueError("The design review is unfinished: evidence/design-review.md must end with a 'Verdict: ' line")
    tokens = read_json(candidate / "tokens.json")
    if not isinstance(tokens, dict) or not tokens:
        raise ValueError("tokens.json must be a nonempty object")
    files = list(content_files(candidate))
    if not any(p.relative_to(candidate).parts[0] == "source" for p in files):
        raise ValueError("Editable source is required in source/")
    if not any(p.relative_to(candidate).parts[0] == "evidence" and
               p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") for p in files):
        raise ValueError("At least one actual viewport capture is required in evidence/")


def inspect_run(run):
    """Return current candidate availability and whether the saved choice is still valid."""
    data = manifest(run)
    candidates = []
    for candidate_id in data["candidateIds"]:
        path = candidate_path(run, candidate_id)
        item = read_json(path / "candidate.json")
        item = dict(item)
        item["currentRevision"] = None
        item["selectable"] = False
        if item["status"] == "ready":
            try:
                validate_output(path)
                item["currentRevision"] = fingerprint(path)
                item["selectable"] = item["revision"] == item["currentRevision"]
                if not item["selectable"]:
                    item["reason"] = "Artifacts changed. Inspect and seal this revision again."
            except (ValueError, OSError) as error:
                item["reason"] = str(error)
        item["previewUrl"] = "/candidates/" + candidate_id + "/preview/index.html"
        candidates.append(item)
    selection = read_json(run / "selection.json")
    valid = bool(selection and any(c["selectable"] and c["id"] == selection["candidateId"] and
                                  c["revision"] == selection["revision"] for c in candidates))
    return {**data, "candidates": candidates, "selection": selection, "selectionValid": valid}


def choose(run, candidate_id, revision, source, statement):
    """Record explicit user input only for a current, sealed candidate revision."""
    state = inspect_run(run)
    item = next((c for c in state["candidates"] if c["id"] == candidate_id), None)
    if not item or not item["selectable"] or item["revision"] != revision:
        raise ValueError("Design changed or is incomplete. Refresh and explicitly choose the current revision.")
    if not isinstance(statement, str) or not statement.strip():
        raise ValueError("The user's explicit selection statement is required")
    record = {"candidateId": candidate_id, "revision": revision, "chosenAt": now(),
              "source": source, "statement": statement.strip()}
    write_json(run / "selection.json", record)
    return record


def init_run(args):
    """Allocate a distinct run; never overwrite an existing workspace."""
    if args.count < 1:
        raise ValueError("Design count must be a positive integer")
    root = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex[:8]
    run = Path(args.run_dir).expanduser().resolve() if args.run_dir else root / "claude/design-pipeline/runs" / run_id
    run.mkdir(parents=True, exist_ok=False)
    ids = ["design-" + str(n) for n in range(1, args.count + 1)]
    write_json(run / "manifest.json", {"schemaVersion": 1, "id": run_id, "title": args.title,
               "projectRoot": str(Path(args.project).expanduser().resolve()) if args.project else None,
               "createdAt": now(), "candidateIds": ids})
    (run / "brief.md").write_text("# " + args.title + "\n\n")
    for candidate_id in ids:
        path = run / "candidates" / candidate_id
        for child in ("source", "preview", "evidence"):
            (path / child).mkdir(parents=True, exist_ok=True)
        write_json(path / "candidate.json", {"id": candidate_id, "title": candidate_id,
                   "skill": "none", "direction": "", "status": "pending", "revision": None, "reason": ""})
    return {"runDir": str(run), "candidateIds": ids}


def serve(run, port):
    """Host candidate previews on loopback so each design can open in its own browser tab."""
    manifest(run)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, status, content, kind):
            self.send_response(status)
            self.send_header("Content-Type", kind + ("; charset=utf-8" if kind.startswith("text/") else ""))
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Access-Control-Allow-Origin", "*")
            try:
                self.end_headers()
                self.wfile.write(content)
            except (BrokenPipeError, ConnectionResetError):
                # Reloading a tab can abort an in-flight preview response.
                pass

        def do_GET(self):
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                self.respond(403, b"Use the printed loopback URL", "text/plain")
                return
            try:
                parts = unquote(urlsplit(self.path).path).strip("/").split("/")
                if len(parts) < 4 or parts[0] != "candidates" or parts[2] not in ("preview", "evidence"):
                    raise ValueError("File not available")
                root = candidate_path(run, parts[1]) / parts[2]
                relative = Path(*parts[3:])
                if any(p.startswith(".") or p in IGNORED or p == ".." for p in relative.parts):
                    raise ValueError("File not available")
                path = root / relative
                if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                    raise ValueError("File not available")
                # Parent symlinks can expose files even if the leaf itself is ordinary.
                if any(p.is_symlink() for p in [root, *path.parents] if p.is_relative_to(run)):
                    raise ValueError("File not available")
                self.respond(200, path.read_bytes(), mimetypes.guess_type(path)[0] or "application/octet-stream")
            except (ValueError, OSError) as error:
                self.respond(404, str(error).encode(), "text/plain")

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = "http://127.0.0.1:" + str(server.server_port)
    previews = {c["id"]: url + c["previewUrl"] for c in inspect_run(run)["candidates"] if c["selectable"]}
    print(json.dumps({"url": url, "runDir": str(run), "previews": previews}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    """Keep all coordinator mutations behind a small, reusable command interface."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("init", help="Create a fresh design run")
    create.add_argument("--title", required=True)
    create.add_argument("--count", type=int, required=True)
    create.add_argument("--project")
    create.add_argument("--run-dir")
    for name in ("inspect", "candidate", "seal", "choose", "serve"):
        command = commands.add_parser(name)
        command.add_argument("--run", required=True)
        if name in ("candidate", "seal", "choose"):
            command.add_argument("--id", required=True)
        if name == "candidate":
            command.add_argument("--title")
            command.add_argument("--skill", choices=SKILLS)
            command.add_argument("--direction")
            command.add_argument("--status", choices=("pending", "running", "failed"))
            command.add_argument("--reason")
        if name == "choose":
            command.add_argument("--revision", required=True)
            command.add_argument("--user-statement", required=True)
        if name == "serve":
            command.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    try:
        if args.command == "init":
            result = init_run(args)
        else:
            run = Path(args.run).expanduser().resolve()
            if args.command == "serve":
                serve(run, args.port)
                return
            if args.command == "inspect":
                result = inspect_run(run)
            else:
                path = candidate_path(run, args.id)
                item = read_json(path / "candidate.json")
                if args.command == "candidate":
                    for key in ("title", "skill", "direction", "status", "reason"):
                        if getattr(args, key) is not None:
                            item[key] = getattr(args, key)
                    write_json(path / "candidate.json", item)
                    result = item
                elif args.command == "seal":
                    validate_output(path)
                    item.update(status="ready", revision=fingerprint(path), reason="")
                    write_json(path / "candidate.json", item)
                    result = item
                else:
                    result = choose(run, args.id, args.revision, "user-chat", args.user_statement)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
