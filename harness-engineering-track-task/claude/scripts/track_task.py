#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


SECTION_ORDER = ("open", "in-flight", "waiting", "shipped")
SECTION_ALIASES = {
    "open": (
        "## Open asks (not yet scoped)",
        "## Open asks",
    ),
    "in-flight": ("## In flight",),
    "waiting": (
        "## Waiting",
        "## Waiting on client",
    ),
    "shipped": ("## Shipped",),
}


@dataclass(frozen=True)
class WorkspaceResolution:
    root: Path
    name: str
    kind: str
    client: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append one item to a workspace-level INBOX.md file.",
    )
    parser.add_argument("--text", required=True, help="Entry text to append.")
    parser.add_argument(
        "--section",
        required=True,
        choices=SECTION_ORDER,
        help="Inbox section to append to.",
    )
    parser.add_argument(
        "--client",
        help="Explicit Liturga client slug. Use when cwd is outside the client tree.",
    )
    parser.add_argument(
        "--workspace-root",
        help="Explicit workspace root for non-Liturga workspaces.",
    )
    parser.add_argument(
        "--cwd",
        default=str(Path.cwd()),
        help="Working directory used for workspace detection. Defaults to the current directory.",
    )
    parser.add_argument(
        "--base-dir",
        default="~/liturga/clients",
        help="Base Liturga clients directory. Defaults to ~/liturga/clients.",
    )
    args = parser.parse_args()
    if args.client and args.workspace_root:
        parser.error("Use either --client or --workspace-root, not both.")
    return args


def normalize_entry(text: str) -> str:
    entry = " ".join(text.split()).strip()
    if entry.startswith("- "):
        entry = entry[2:].lstrip()
    if not entry:
        raise ValueError("Entry text cannot be empty.")
    return f"- {entry}"


def detect_client(base_dir: Path, cwd: Path) -> str | None:
    try:
        relative = cwd.resolve().relative_to(base_dir.resolve())
    except ValueError:
        return None
    return relative.parts[0] if relative.parts else None


def detect_git_root(cwd: Path) -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    root = result.stdout.strip()
    if not root:
        return None
    return Path(root).resolve()


def titleize(name: str) -> str:
    words = name.replace("-", " ").replace("_", " ").split()
    return " ".join(word.capitalize() for word in words) or name


def resolve_workspace(args: argparse.Namespace) -> WorkspaceResolution:
    base_dir = Path(args.base_dir).expanduser().resolve()
    cwd = Path(args.cwd).expanduser().resolve()

    if args.workspace_root:
        root = Path(args.workspace_root).expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"Workspace root not found: {root}")
        return WorkspaceResolution(
            root=root,
            name=titleize(root.name),
            kind="explicit",
            client=None,
        )

    if args.client:
        client_dir = base_dir / args.client
        if not client_dir.is_dir():
            raise ValueError(f"Client directory not found: {client_dir}")
        return WorkspaceResolution(
            root=client_dir.resolve(),
            name=titleize(args.client),
            kind="liturga-client",
            client=args.client,
        )

    client = detect_client(base_dir, cwd)
    if client:
        client_dir = base_dir / client
        if not client_dir.is_dir():
            raise ValueError(f"Client directory not found: {client_dir}")
        return WorkspaceResolution(
            root=client_dir.resolve(),
            name=titleize(client),
            kind="liturga-client",
            client=client,
        )

    git_root = detect_git_root(cwd)
    if git_root and git_root.is_dir():
        return WorkspaceResolution(
            root=git_root,
            name=titleize(git_root.name),
            kind="git",
            client=None,
        )

    raise ValueError(
        "Could not infer the workspace root. Pass --client <client>, "
        "--workspace-root <path>, or run from inside ~/liturga/clients/<client>/... "
        "or a git repository."
    )


def build_template(workspace_name: str) -> str:
    return (
        f"# {workspace_name} inbox\n\n"
        "Capture buffer for asks that will wait, are blocked, or need scoping before execution. "
        "Managed by `/harness-engineering-track-task`. "
        "Execution plans live under `docs/exec-plans/active/`.\n\n"
        "## Open asks (not yet scoped)\n\n"
        "- (empty)\n\n"
        "## In flight\n\n"
        "- (empty)\n\n"
        "## Waiting\n\n"
        "- (empty)\n\n"
        "## Shipped\n\n"
        "- (empty)\n"
    )


def ensure_template(inbox_path: Path, workspace_name: str) -> bool:
    if inbox_path.exists():
        return False
    inbox_path.write_text(build_template(workspace_name), encoding="utf-8")
    return True


def fuzzy_section_key(line: str) -> str | None:
    lower = line.lower()
    if not lower.startswith("## "):
        return None
    if "open" in lower:
        return "open"
    if "flight" in lower:
        return "in-flight"
    if "waiting" in lower:
        return "waiting"
    if "shipped" in lower:
        return "shipped"
    return None


def locate_section(lines: list[str], section: str) -> tuple[int, int, str]:
    for alias in SECTION_ALIASES[section]:
        for index, line in enumerate(lines):
            if line.strip() == alias:
                return index, find_section_end(lines, index), line.strip()

    for index, line in enumerate(lines):
        if fuzzy_section_key(line) == section:
            return index, find_section_end(lines, index), line.strip()

    raise ValueError(f"Missing section heading for {section}.")


def find_section_end(lines: list[str], section_start: int) -> int:
    for index in range(section_start + 1, len(lines)):
        if lines[index].startswith("## "):
            return index
    return len(lines)


def append_to_section(content: str, section: str, bullet: str) -> tuple[str, str]:
    lines = content.splitlines()
    section_start, section_end, heading = locate_section(lines, section)

    before = lines[: section_start + 1]
    body = lines[section_start + 1 : section_end]
    after = lines[section_end:]

    while body and body[0] == "":
        body = body[1:]
    while body and body[-1] == "":
        body = body[:-1]
    while after and after[0] == "":
        after = after[1:]

    body = [line for line in body if line.strip() != "- (empty)"]

    updated_lines = before + [""] + body + [bullet, ""]
    if after:
        updated_lines.extend(after)

    return "\n".join(updated_lines).rstrip("\n") + "\n", heading


def count_section_items(content: str, section: str) -> int:
    try:
        lines = content.splitlines()
        section_start, section_end, _ = locate_section(lines, section)
    except ValueError:
        return 0

    count = 0
    for line in lines[section_start + 1 : section_end]:
        stripped = line.strip()
        if stripped.startswith("- ") and stripped != "- (empty)":
            count += 1
    return count


def main() -> int:
    args = parse_args()

    try:
        resolution = resolve_workspace(args)
        bullet = normalize_entry(args.text)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    inbox_path = resolution.root / "INBOX.md"
    created = ensure_template(inbox_path, resolution.name)

    try:
        updated_content, section_heading = append_to_section(
            inbox_path.read_text(encoding="utf-8"),
            args.section,
            bullet,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    inbox_path.write_text(updated_content, encoding="utf-8")

    print(f"workspace_kind={resolution.kind}")
    print(f"workspace_root={resolution.root}")
    print(f"workspace_name={resolution.name}")
    print(f"client={resolution.client or ''}")
    print(f"created={'true' if created else 'false'}")
    print(f"section={args.section}")
    print(f"section_heading={section_heading}")
    print(f"path={inbox_path}")
    print(f"bullet={bullet}")
    for section in SECTION_ORDER:
        print(f"count_{section.replace('-', '_')}={count_section_items(updated_content, section)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
