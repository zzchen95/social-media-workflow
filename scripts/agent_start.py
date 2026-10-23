"""Read-only navigation for a fresh agent; never execute the proposed next action."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.public_research import check as check_research


def read_record(path):
    if path.is_symlink() or path.stat().st_size > 2_000_000:
        raise ValueError("symlink or oversized navigation record")
    return json.loads(path.read_text(encoding="utf-8"))


def reference_status(root, artifact):
    value = artifact.get("path")
    if not isinstance(value, str) or not value:
        return {"path": value, "state": "missing_path"}
    # Do not dereference external media, credentials, or arbitrary paths.
    candidate = root / value
    if Path(value).is_absolute() or re.match(r"^[A-Za-z]:", value) or "\\" in value:
        return {"path": value, "state": "external_not_checked"}
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root) or candidate.is_symlink():
        return {"path": value, "state": "outside_or_symlink_not_checked"}
    relative = resolved.relative_to(root)
    allowed = relative.parts and relative.parts[0] in {"content", "docs"}
    if not allowed or resolved.suffix not in {".json", ".md", ".csv", ".txt", ".srt", ".vtt"}:
        return {"path": value, "state": "requires_targeted_check"}
    if not resolved.is_file():
        return {"path": value, "state": "missing_or_not_file"}
    if resolved.stat().st_size > 8_000_000:
        return {"path": value, "state": "large_file_not_checked"}
    expected = artifact.get("sha256")
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        return {"path": value, "state": "digest_not_provided"}
    actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
    return {"path": value, "state": "verified_digest" if actual == expected.lower() else "digest_mismatch"}


def build_status(root=ROOT, as_of=None):
    root = Path(root).resolve()
    config = read_record(root / "config/public_research.json")
    zone = ZoneInfo(config["timezone"])
    now = (as_of or datetime.now(zone)).astimezone(zone)
    result = {"schema_version": 1, "as_of": now.isoformat(), "index_only": True,
              "schedule_config": config.get("schedule"), "latest_usable_research": None,
              "research_rejections": [], "workflows": [], "issues": []}
    base = root / "docs/reports/public-research"
    runs = []
    if base.is_dir() and not base.is_symlink():
        for path in base.glob("*/run-*/run.json"):
            if path.resolve().is_relative_to(root) and re.fullmatch(r"run-\d+", path.parent.name):
                runs.append(path)
    runs.sort(key=lambda p: (p.parent.parent.name, int(p.parent.name[4:])), reverse=True)
    for path in runs:
        relative = path.parent.relative_to(root).as_posix()
        try:
            run = read_record(path)
            report = check_research(path.parent)
            if run["window_end"] > now.date().isoformat():
                raise ValueError("future window")
            if not report["valid"] or run["status"] not in {"completed", "partial"} or not report["summary"]["total"]:
                raise ValueError("not usable: " + run.get("status", "unknown"))
            result["latest_usable_research"] = {"path": relative, "status": run["status"],
                "window_start": run["window_start"], "window_end": run["window_end"],
                "freshness": "current_day_window" if run["window_end"] == now.date().isoformat() else "older_window",
                "summary": report["summary"]}
            break
        except (OSError, ValueError, KeyError, TypeError) as exc:
            result["research_rejections"].append({"path": relative, "reason": str(exc)})
    workflows = root / "content/workflows"
    if workflows.is_dir() and not workflows.is_symlink():
        for folder in sorted(workflows.iterdir()):
            if not folder.is_dir() or folder.is_symlink():
                continue
            versions = [p for p in folder.glob("checkpoint-v*.json") if re.fullmatch(r"checkpoint-v\d+\.json", p.name)]
            versions.sort(key=lambda p: int(p.stem.split("-v")[1]), reverse=True)
            invalid = []
            for path in versions:
                try:
                    record = read_record(path)
                    if record.get("workflow_id") != folder.name or record.get("schema_version") != 1:
                        raise ValueError("checkpoint identity/schema mismatch")
                    if not isinstance(record.get("stage_records"), list):
                        raise ValueError("stage_records must be an array")
                    created = datetime.fromisoformat(record["created_at"])
                    if created.utcoffset() is None:
                        raise ValueError("checkpoint time needs an offset")
                    refs = [reference_status(root, artifact) for stage in record["stage_records"]
                            for artifact in stage.get("artifacts", [])]
                    result["workflows"].append({"workflow_id": folder.name, "purpose": record.get("purpose", "unknown"),
                        "checkpoint": path.relative_to(root).as_posix(), "mode": record.get("mode"),
                        "stage_records": record["stage_records"], "deferred_inputs": record.get("deferred_inputs", []),
                        "next_action": record.get("next_action"), "references": refs,
                        "needs_recheck": bool(record.get("needs_recheck") or invalid
                            or any(stage.get("needs_recheck") for stage in record["stage_records"])
                            or any(r["state"] != "verified_digest" for r in refs)),
                        "newer_invalid_records": invalid})
                    break
                except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
                    invalid.append({"path": path.relative_to(root).as_posix(), "reason": str(exc)})
            else:
                if invalid:
                    result["issues"].extend(invalid)
    actual = [w for w in result["workflows"] if w["purpose"] == "content_work"]
    result["workflow_selection"] = "needs_user_selection" if len(actual) > 1 else "single_content_workflow" if actual else "no_content_workflow"
    result["focus_candidate"] = actual[0]["workflow_id"] if len(actual) == 1 else None
    result["guidance"] = "Use current user intent and the workflow skill; index recommendations never grant execution or approval."
    return result


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        result = build_status()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"ready": False, "reason": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
