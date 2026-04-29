#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys


DEFAULT_INBOX_TEMPLATE = """# Inbox

## Open asks

## In flight

## Waiting on client

## Shipped
"""

CODE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".swift",
    ".ts",
    ".tsx",
}

COMMON_VALIDATION_SCRIPT_NAMES = {
    "build": "Build",
    "check": "General check",
    "lint": "Lint",
    "test": "Tests",
    "typecheck": "Typecheck",
    "type-check": "Typecheck",
}

COMMON_MAKE_TARGET_NAMES = {
    "build": "Build",
    "check": "General check",
    "lint": "Lint",
    "test": "Tests",
    "typecheck": "Typecheck",
    "type-check": "Typecheck",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold the minimum harness-engineering project surface.",
    )
    parser.add_argument(
        "--root",
        default=str(Path.cwd()),
        help="Repository root to scaffold. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--project-name",
        help="Override the project name used in templates. Defaults to the repo directory name.",
    )
    parser.add_argument(
        "--stack",
        choices=["auto", "generic", "js-ts", "python"],
        default="auto",
        help="Stack hint used to pick the app root. Defaults to auto-detect.",
    )
    parser.add_argument(
        "--app-root",
        help="Explicit application code root, relative to the repo root.",
    )
    parser.add_argument(
        "--no-domain-layout",
        action="store_true",
        help="Skip creating the minimal domain-first code layout even if it would be safe.",
    )
    return parser.parse_args()


def detect_stack(root: Path) -> str:
    if (
        (root / "package.json").exists()
        or (root / "tsconfig.json").exists()
        or any(root.glob("tsconfig.*.json"))
        or (root / "jsconfig.json").exists()
    ):
        return "js-ts"
    if (
        (root / "pyproject.toml").exists()
        or (root / "setup.py").exists()
        or (root / "requirements.txt").exists()
    ):
        return "python"
    return "generic"


def detect_python_app_root(root: Path) -> Path:
    src_dir = root / "src"
    if src_dir.is_dir():
        packages = [
            path
            for path in src_dir.iterdir()
            if path.is_dir() and not path.name.startswith(".") and (path / "__init__.py").exists()
        ]
        if len(packages) == 1:
            return Path("src") / packages[0].name
    packages = [
        path
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and (path / "__init__.py").exists()
    ]
    if len(packages) == 1:
        return Path(packages[0].name)
    return Path("src")


def detect_app_root(root: Path, stack: str, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    if stack == "python":
        return detect_python_app_root(root)
    return Path("src")


def count_code_files(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for file_path in path.rglob("*"):
        if file_path.is_file() and file_path.suffix in CODE_EXTENSIONS:
            total += 1
    return total


def domain_layout_safe(root: Path, app_root: Path) -> tuple[bool, str]:
    app_root_path = root / app_root
    if not app_root_path.exists():
        return True, "app root does not exist yet"
    if (app_root_path / "domains").exists():
        return True, "domains directory already exists"
    file_count = count_code_files(app_root_path)
    if file_count <= 5:
        return True, f"small existing source tree ({file_count} code files)"
    return False, f"existing source tree under {app_root} is nontrivial ({file_count} code files)"


def load_track_task_template(skills_root: Path) -> str:
    track_task_script = (
        skills_root / "harness-engineering-track-task" / "scripts" / "track_task.py"
    )
    if not track_task_script.exists():
        return DEFAULT_INBOX_TEMPLATE

    spec = importlib.util.spec_from_file_location("track_task_template", track_task_script)
    if spec is None or spec.loader is None:
        return DEFAULT_INBOX_TEMPLATE

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    build_template = getattr(module, "build_template", None)
    if callable(build_template):
        template = build_template("Inbox")
        if isinstance(template, str) and template.strip():
            return template

    template = getattr(module, "TEMPLATE", DEFAULT_INBOX_TEMPLATE)
    if isinstance(template, str) and template.strip():
        return template
    return DEFAULT_INBOX_TEMPLATE


def load_asset(skill_dir: Path, relative_name: str) -> str:
    return (skill_dir / "assets" / relative_name).read_text(encoding="utf-8")


def render_template(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def ensure_directory(path: Path, created: list[str], root: Path) -> None:
    if path.exists():
        return
    path.mkdir(parents=True, exist_ok=True)
    created.append(str(path.relative_to(root)))


def ensure_gitkeep(path: Path, created: list[str], preserved: list[str], root: Path) -> None:
    if path.exists():
        preserved.append(str(path.relative_to(root)))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    created.append(str(path.relative_to(root)))


def ensure_file(path: Path, content: str, created: list[str], preserved: list[str], root: Path) -> None:
    if path.exists():
        preserved.append(str(path.relative_to(root)))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(str(path.relative_to(root)))


def parse_make_targets(makefile: Path) -> set[str]:
    targets: set[str] = set()
    if not makefile.exists():
        return targets

    target_pattern = re.compile(r"^([A-Za-z0-9_.-]+)\s*:(?![=])")
    for line in makefile.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.startswith("\t") or line.lstrip().startswith("#"):
            continue
        match = target_pattern.match(line)
        if match:
            targets.add(match.group(1))
    return targets


def read_package_scripts(package_json: Path) -> dict[str, str]:
    if not package_json.exists():
        return {}
    try:
        payload = json.loads(package_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    scripts = payload.get("scripts")
    if not isinstance(scripts, dict):
        return {}
    return {key: value for key, value in scripts.items() if isinstance(key, str) and isinstance(value, str)}


def iter_package_json_files(root: Path) -> list[Path]:
    candidates = [root / "package.json"]
    for directory_name in ("apps", "packages"):
        parent = root / directory_name
        if not parent.is_dir():
            continue
        for child in sorted(parent.iterdir()):
            package_json = child / "package.json"
            if package_json.exists():
                candidates.append(package_json)
    return candidates


def pyproject_has_pytest_evidence(pyproject: Path) -> bool:
    if not pyproject.exists():
        return False
    content = pyproject.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"^\s*\[tool\.pytest\.ini_options\]", content, re.MULTILINE):
        return True

    dependency_sections = {
        "project.dependencies",
        "project.optional-dependencies",
        "dependency-groups",
        "tool.poetry.dependencies",
        "tool.poetry.group.dev.dependencies",
        "tool.poetry.group.test.dependencies",
    }
    current_section = ""
    for line in content.splitlines():
        section_match = re.match(r"^\s*\[([^\]]+)\]", line)
        if section_match:
            current_section = section_match.group(1)
            continue
        if current_section in dependency_sections and value_contains_pytest(line):
            return True
        if re.match(r"^\s*(dependencies|optional-dependencies|dependency-groups)\s*=", line) and value_contains_pytest(line):
            return True
    return False


def value_contains_pytest(value: object) -> bool:
    if isinstance(value, str):
        return bool(re.search(r"(^|[^A-Za-z0-9_-])pytest([^A-Za-z0-9_-]|$)", value))
    if isinstance(value, list):
        return any(value_contains_pytest(item) for item in value)
    if isinstance(value, dict):
        return any(
            (isinstance(key, str) and key == "pytest") or value_contains_pytest(item)
            for key, item in value.items()
        )
    return False


def has_pytest_evidence(root: Path) -> tuple[bool, str | None]:
    pytest_config_files = [
        "pytest.ini",
        ".pytest.ini",
        "tox.ini",
        "setup.cfg",
    ]
    for filename in pytest_config_files:
        path = root / filename
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if filename in {"pytest.ini", ".pytest.ini"} or re.search(r"^\s*\[pytest\]", content, re.MULTILINE):
            return True, filename

    pyproject = root / "pyproject.toml"
    if pyproject_has_pytest_evidence(pyproject):
        return True, "pyproject.toml"

    requirements_files = [
        "requirements.txt",
        "requirements-dev.txt",
        "dev-requirements.txt",
        "test-requirements.txt",
    ]
    for filename in requirements_files:
        path = root / filename
        if path.exists() and value_contains_pytest(path.read_text(encoding="utf-8", errors="ignore")):
            return True, filename

    return False, None


def discover_validation_commands(root: Path) -> list[tuple[str, str, str]]:
    commands: list[tuple[str, str, str]] = []
    seen: set[str] = set()

    make_targets = parse_make_targets(root / "Makefile")
    for target, label in COMMON_MAKE_TARGET_NAMES.items():
        if target in make_targets:
            command = f"make {target}"
            commands.append((label, command, "Makefile"))
            seen.add(command)

    for package_json in iter_package_json_files(root):
        scripts = read_package_scripts(package_json)
        if not scripts:
            continue
        package_dir = package_json.parent
        package_source = package_json.relative_to(root).as_posix()
        prefix = "" if package_dir == root else f"cd {package_dir.relative_to(root).as_posix()} && "
        for script_name, label in COMMON_VALIDATION_SCRIPT_NAMES.items():
            if script_name not in scripts:
                continue
            command = f"{prefix}npm run {script_name}"
            if command in seen:
                continue
            commands.append((label, command, package_source))
            seen.add(command)

    has_pytest, pytest_source = has_pytest_evidence(root)
    test_dirs = [root / "tests", root / "test"]
    if has_pytest and pytest_source and any(path.is_dir() for path in test_dirs):
        command = "python -m pytest"
        if command not in seen:
            commands.append(("Tests", command, pytest_source))
            seen.add(command)

    return commands


def render_validation_guide(commands: list[tuple[str, str, str]]) -> str:
    lines = [
        "# Validation Guide",
        "",
        "Use this guide to choose proof by change type. Prefer the strongest relevant check that exists in this repo.",
        "If a required check cannot run, record the concrete blocker and the weaker proof used instead.",
        "",
        "## Change-Type Checks",
        "",
        "| Change type | Command or tool | Proof provided | Source |",
        "| --- | --- | --- | --- |",
    ]
    for label, command, source in commands:
        lines.append(f"| {label} | `{command}` | {label} command completes successfully. | `{source}` |")
    lines.extend(
        [
            "",
            "## General Rules",
            "",
            "- Match the proof to the files changed and cite the command or blocker in the final report.",
            "- Do not invent validation commands. If this guide is too sparse, run `$harness-engineering-validation-map`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error=root directory not found: {root}", file=sys.stderr)
        return 2

    stack = detect_stack(root) if args.stack == "auto" else args.stack
    app_root = detect_app_root(root, stack, args.app_root)
    project_name = args.project_name or root.name

    skill_dir = Path(__file__).resolve().parents[1]
    skills_root = skill_dir.parent

    replacements = {
        "${PROJECT_NAME}": project_name,
        "${APP_ROOT_DISPLAY}": app_root.as_posix(),
    }

    created: list[str] = []
    preserved: list[str] = []

    docs_dirs = [
        root / "docs" / "exec-plans" / "active",
        root / "docs" / "exec-plans" / "completed",
        root / "docs" / "design-docs",
        root / "docs" / "product-specs",
        root / "docs" / "references",
        root / "docs" / "generated",
    ]

    for directory in docs_dirs:
        ensure_directory(directory, created, root)
        ensure_gitkeep(directory / ".gitkeep", created, preserved, root)

    agents_template = render_template(load_asset(skill_dir, "AGENTS.md.tmpl"), replacements)
    architecture_template = render_template(load_asset(skill_dir, "ARCHITECTURE.md.tmpl"), replacements)
    inbox_template = load_track_task_template(skills_root)
    validation_commands = discover_validation_commands(root)

    ensure_file(root / "AGENTS.md", agents_template, created, preserved, root)
    ensure_file(root / "ARCHITECTURE.md", architecture_template, created, preserved, root)
    ensure_file(root / "INBOX.md", inbox_template, created, preserved, root)
    validation_guide_path = root / "docs" / "validation-guide.md"
    if validation_commands:
        validation_guide = render_validation_guide(validation_commands)
        ensure_file(validation_guide_path, validation_guide, created, preserved, root)
    elif validation_guide_path.exists():
        preserved.append(str(validation_guide_path.relative_to(root)))

    domain_created = False
    domain_reason = "skipped by request"

    if not args.no_domain_layout:
        safe, reason = domain_layout_safe(root, app_root)
        domain_reason = reason
        if safe:
            domain_dirs = [
                root / app_root / "domains",
                root / app_root / "infra" / "providers",
                root / app_root / "app" / "wiring",
            ]
            for directory in domain_dirs:
                ensure_directory(directory, created, root)
                ensure_gitkeep(directory / ".gitkeep", created, preserved, root)
            domain_created = True

    print(f"root={root}")
    print(f"stack={stack}")
    print(f"app_root={app_root.as_posix()}")
    print(f"domain_layout={'created' if domain_created else 'skipped'}")
    print(f"domain_layout_reason={domain_reason}")
    if validation_guide_path.exists():
        validation_state = "preserved" if "docs/validation-guide.md" in preserved else "created"
    else:
        validation_state = "skipped; run $harness-engineering-validation-map if validation remains unclear"
    print(f"validation_guide={validation_state}")
    print("created:")
    for item in created:
        print(f"  - {item}")
    print("preserved:")
    for item in preserved:
        print(f"  - {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
