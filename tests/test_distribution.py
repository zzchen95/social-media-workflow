"""Verify the share package works outside its author's checkout."""
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def checkout(tmp_path):
    target = tmp_path / "clean-checkout"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(
        ".git", ".venv", "__pycache__", ".pytest_cache", "content", "media", "reports", "local"))
    return target


def run(checkout, script, *args):
    return subprocess.run([sys.executable, str(checkout / "scripts" / script), *args],
                          cwd=checkout, capture_output=True, text=True, encoding="utf-8")


def test_readonly_bootstrap_in_fresh_directory(checkout):
    result = run(checkout, "bootstrap.py", "--check")
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (checkout / ".venv").exists()
    assert not (checkout / "content").exists()
    assert not (checkout / "docs/reports").exists()


def test_missing_skill_resource_fails_validation(checkout):
    (checkout / "docs/implementation/step2-templates.md").unlink()
    result = run(checkout, "validate_share.py")
    assert result.returncode != 0
    assert "step2-templates.md" in result.stdout


def test_force_added_runtime_file_is_rejected(checkout):
    subprocess.run(["git", "init", "--quiet"], cwd=checkout, check=True)
    private = checkout / "content/private-note.txt"
    private.parent.mkdir()
    private.write_text("synthetic private fixture, never a real account", encoding="utf-8")
    subprocess.run(["git", "add", "-f", "content/private-note.txt"], cwd=checkout, check=True)
    result = run(checkout, "validate_share.py")
    assert result.returncode != 0
    assert "Private/runtime file tracked: content/private-note.txt" in result.stdout


def test_bootstrap_does_not_clobber_existing_directory(checkout):
    folder = checkout / ".venv"
    folder.mkdir()
    marker = folder / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    result = run(checkout, "bootstrap.py")
    assert result.returncode != 0
    assert marker.read_text(encoding="utf-8") == "keep"


def test_untracked_shared_config_cannot_pass_repository_check(checkout):
    subprocess.run(["git", "init", "--quiet"], cwd=checkout, check=True)
    subprocess.run(["git", "add", "README.md"], cwd=checkout, check=True)
    assert (checkout / "config/public_research.json").exists()
    result = run(checkout, "validate_share.py")
    assert result.returncode != 0
    assert "Required distribution file not tracked/included: config/public_research.json" in result.stdout
