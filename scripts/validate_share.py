"""Check distributable skills, local references, config and tracked-file boundaries."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

from check_markdown_tables import check_tables

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {"social-media-workflow", "public-social-research", "social-content-planning", "social-content-production", "social-performance-review"}
PRIVATE_DIRS = {"content", "media", "data", ".venv", "venv", "__pycache__", ".pytest_cache", "dist"}
PRIVATE_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".log", ".pem", ".key", ".pyc", ".mp4", ".mov", ".wav"}


def private_path(path):
    return (any(part in PRIVATE_DIRS for part in path.parts)
            or path.as_posix().startswith(("docs/reports/", "config/local/"))
            or path.name == ".env" or path.name.startswith(".env.")
            or path.suffix in PRIVATE_SUFFIXES)


def package_files():
    # Inspect tracked files so force-added private files cannot hide behind .gitignore.
    if (ROOT / ".git").exists():
        result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
        tracked = [ROOT / p.decode("utf-8") for p in result.stdout.split(b"\0") if p]
        if tracked:
            return tracked
    return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.relative_to(ROOT).parts and not private_path(p.relative_to(ROOT))]


def unfenced(text):
    return re.sub(r"(?ms)^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?^ {0,3}\1\s*$", "", text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="Also parse YAML using the development dependency PyYAML")
    args = parser.parse_args()
    errors = []
    skill_paths = list((ROOT / ".agents/skills").glob("*/SKILL.md"))
    if {p.parent.name for p in skill_paths} != SKILLS:
        errors.append("Expected exactly the five documented skills")
    for path in skill_paths:
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
        if not match:
            errors.append(f"Missing frontmatter: {path.relative_to(ROOT)}")
            continue
        metadata = match.group(1)
        if not re.search(rf"^name:\s*{re.escape(path.parent.name)}\s*$", metadata, re.M):
            errors.append(f"Skill name mismatch: {path.parent.name}")
        if not re.search(r"^description:\s*\S.+$", metadata, re.M):
            errors.append(f"Missing skill description: {path.parent.name}")
        if args.full:
            try:
                import yaml
                parsed = yaml.safe_load(metadata)
                assert parsed["name"] == path.parent.name and parsed["description"]
                ui = path.parent / "agents/openai.yaml"
                if ui.exists():
                    interface = yaml.safe_load(ui.read_text(encoding="utf-8"))["interface"]
                    assert 25 <= len(interface["short_description"]) <= 64
                    assert "$" + path.parent.name in interface["default_prompt"]
            except (ImportError, ValueError, KeyError, TypeError, AssertionError) as exc:
                errors.append(f"YAML check failed for {path.parent.name}: {exc}")
    config = json.loads((ROOT / "config/public_research.json").read_text(encoding="utf-8"))
    if config.get("schedule", {}).get("enabled") is not False or config.get("schedule", {}).get("automation_id"):
        errors.append("Shared config must not contain an active automation")
    files = package_files()
    relative_files = {p.relative_to(ROOT).as_posix() for p in files}
    required = {"config/public_research.json", "scripts/public_research.py", "scripts/check_markdown_tables.py",
                "scripts/agent_start.py", "scripts/review_windows.py", "START_HERE.md", "README.md", "AGENTS.md",
                "docs/implementation/jianying-capability.md",
                ".agents/skills/social-content-production/references/jianying-computer-use.md",
                ".agents/skills/social-performance-review/references/retention-to-edit.md"}
    for missing in sorted(required - relative_files):
        errors.append(f"Required distribution file not tracked/included: {missing}")
    checked_links = 0
    for path in files:
        relative = path.relative_to(ROOT)
        if private_path(relative):
            errors.append(f"Private/runtime file tracked: {relative.as_posix()}")
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            errors.append(f"Nonportable file: {relative}")
            continue
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"/home/[^\s]+|/mnt/[a-z]/Users/[^\s]+|[A-Z]:\\Users\\", text):
            errors.append(f"Machine-specific home path in {relative}")
        if text.count("```") % 2:
            errors.append(f"Unclosed code fence in {relative}")
        for item in check_tables(text):
            errors.append(f"Table column mismatch in {relative}:{item['line']}")
        for target in re.findall(r"\]\(([^)]+)\)", unfenced(text)):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            target = unquote(target.split("#", 1)[0].strip("<>"))
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                errors.append(f"Missing/outside reference in {relative}: {target}")
            checked_links += 1
    print(json.dumps({"valid": not errors, "skills": len(skill_paths), "files": len(files), "local_links": checked_links, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
