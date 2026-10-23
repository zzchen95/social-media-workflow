from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from scripts.agent_start import build_status
from scripts.public_research import prepare, read_json, write_json

ROOT = Path(__file__).resolve().parents[1]


def project(tmp_path):
    (tmp_path / "config").mkdir()
    shutil.copyfile(ROOT / "config/public_research.json", tmp_path / "config/public_research.json")
    return tmp_path


def checkpoint(root, name, purpose="content_work", version=1, artifacts=None):
    folder = root / "content/workflows" / name
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"checkpoint-v{version:03}.json"
    path.write_text(json.dumps({"schema_version": 1, "workflow_id": name, "purpose": purpose,
        "created_at": "2020-10-18T10:00:00-07:00", "mode": "exploratory",
        "stage_records": [{"stage": "production", "progress": "delivered", "artifacts": artifacts or []}],
        "deferred_inputs": [{"field": "media", "basis": "user_deferred"}]}), encoding="utf-8")
    return path


def test_new_checkout_has_no_execution_or_runtime_writes(tmp_path):
    root = project(tmp_path)
    before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))
    status = build_status(root)
    assert status["latest_usable_research"] is None
    assert status["workflow_selection"] == "no_content_workflow"
    assert before == sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))


def test_trial_is_not_selected_as_content_work(tmp_path):
    root = project(tmp_path)
    checkpoint(root, "trial", "workflow_trial")
    status = build_status(root)
    assert status["focus_candidate"] is None
    assert status["workflows"][0]["purpose"] == "workflow_trial"


def test_multiple_real_workflows_need_selection(tmp_path):
    root = project(tmp_path)
    checkpoint(root, "one")
    checkpoint(root, "two")
    status = build_status(root)
    assert status["workflow_selection"] == "needs_user_selection"
    assert status["focus_candidate"] is None


def test_corrupt_new_checkpoint_falls_back_with_recheck(tmp_path):
    root = project(tmp_path)
    old = checkpoint(root, "one")
    (old.parent / "checkpoint-v002.json").write_text("{broken", encoding="utf-8")
    status = build_status(root)["workflows"][0]
    assert status["checkpoint"].endswith("v001.json")
    assert status["needs_recheck"]
    assert status["newer_invalid_records"]
    assert status["deferred_inputs"][0]["field"] == "media"


def test_stage_recheck_is_preserved_in_summary(tmp_path):
    root = project(tmp_path)
    path = checkpoint(root, "one")
    record = read_json(path)
    record["stage_records"][0]["needs_recheck"] = True
    write_json(path, record)
    assert build_status(root)["workflows"][0]["needs_recheck"]


def test_digest_change_requires_recheck_and_external_not_read(tmp_path):
    root = project(tmp_path)
    target = root / "content/brief.md"
    target.parent.mkdir()
    target.write_text("before", encoding="utf-8")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    checkpoint(root, "one", artifacts=[{"path": "content/brief.md", "sha256": digest},
                                        {"path": "../../outside.json", "sha256": digest}])
    target.write_text("after", encoding="utf-8")
    status = build_status(root)["workflows"][0]
    assert status["needs_recheck"]
    assert [r["state"] for r in status["references"]] == ["digest_mismatch", "outside_or_symlink_not_checked"]


def test_prepared_research_does_not_replace_valid_older_research(tmp_path):
    root = project(tmp_path)
    output = root / "docs/reports/public-research"
    older = prepare(ROOT / "config/public_research.json", "2020-10-18", output)
    run = read_json(older / "run.json")
    run["status"] = "partial"
    write_json(older / "run.json", run)
    write_json(older / "sources.json", [{"id": "S", "url": "https://example.com/teaching", "title": "Synthetic only",
        "observed_at": "2020-10-18T10:00:00-07:00", "published_on": "2020-10-18", "access_status": "read"}])
    write_json(older / "candidates.json", [{"id": "T", "platform": "tiktok", "topic": "synthetic", "style": "synthetic",
        "source_ids": ["S"], "evidence_grade": "B", "period_scope": "week_mentioned", "original_post_verified": False,
        "rank_type": "unranked_candidate", "limitations": "not real evidence"}])
    prepare(ROOT / "config/public_research.json", "2020-10-19", output)
    status = build_status(root, datetime(2020, 10, 20, tzinfo=timezone.utc))
    assert status["latest_usable_research"]["window_end"] == "2020-10-18"
    assert status["latest_usable_research"]["freshness"] == "older_window"
    assert "prepared" in status["research_rejections"][0]["reason"]


def test_cli_does_not_generate_pycache_in_fresh_package(tmp_path):
    root = project(tmp_path)
    scripts = root / "scripts"
    scripts.mkdir()
    for name in ("agent_start.py", "public_research.py"):
        shutil.copyfile(ROOT / "scripts" / name, scripts / name)
    result = subprocess.run([sys.executable, str(scripts / "agent_start.py")], cwd=root,
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["index_only"]
    assert not list(root.rglob("__pycache__"))
    assert not (root / "content").exists()
