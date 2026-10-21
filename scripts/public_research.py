"""Prepare and check research artifacts. Browsing is performed by ChatGPT tools."""
import argparse
import sys
from collections import Counter
from datetime import date, datetime, timedelta
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config/public_research.json"
PLATFORMS = {"xiaohongshu", "tiktok", "instagram"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_config(path):
    config = read_json(path)
    if config["mode"] != "public_web_no_login":
        raise ValueError("第一步只支持 public_web_no_login")
    if {p["id"] for p in config["platforms"]} != PLATFORMS or len(config["platforms"]) != 3:
        raise ValueError("必须配置三个独立平台")
    if config["lookback_days"] < 1 or config["target_candidates_per_platform"] < 1:
        raise ValueError("研究窗口和目标数量必须为正数")
    ZoneInfo(config["timezone"])
    return config


def prepare(config_path=DEFAULT_CONFIG, end_date=None, output_root=None):
    config = load_config(config_path)
    now = datetime.now(ZoneInfo(config["timezone"]))
    end = date.fromisoformat(end_date) if end_date else now.date()
    if end > now.date():
        raise ValueError("研究截止日期不能在未来")
    start = end - timedelta(days=config["lookback_days"] - 1)
    base = Path(output_root) if output_root else ROOT / config["output_root"]
    parent = base / end.isoformat()
    parent.mkdir(parents=True, exist_ok=True)
    # Atomic mkdir prevents concurrent runs from overwriting each other's artifacts.
    for number in range(1, 10000):
        folder = parent / f"run-{number:03d}"
        try:
            folder.mkdir()
            break
        except FileExistsError:
            continue
    else:
        raise ValueError("当天运行目录已满")
    write_json(folder / "config.snapshot.json", config)
    write_json(folder / "run.json", {
        "schema_version": 1,
        "status": "prepared",
        "mode": config["mode"],
        "created_at": now.isoformat(),
        "window_start": start.isoformat(),
        "window_end": end.isoformat(),
        "timezone": config["timezone"],
        "config_sha256": hashlib.sha256((folder / "config.snapshot.json").read_bytes()).hexdigest(),
        "platform_notes": {p: "待研究；尚无采集结果" for p in sorted(PLATFORMS)},
    })
    write_json(folder / "sources.json", [])
    write_json(folder / "candidates.json", [])
    (folder / "report.md").write_text(
        f"# 三平台公开趋势研究：{start} 至 {end}\n\n"
        "状态：prepared，尚未采集。\n\n"
        "由 ChatGPT 使用公开搜索和网页读取完成研究后，替换此空白报告。\n",
        encoding="utf-8",
    )
    return folder


def valid_url(value):
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc) and not parsed.username and not parsed.password


def summarize_candidates(candidates, target):
    """Count raw candidate records; validity remains the responsibility of check()."""
    platforms = Counter(item.get("platform") for item in candidates)
    grades = Counter(item.get("evidence_grade") for item in candidates)
    return {
        "total": len(candidates),
        "by_platform": {p: platforms[p] for p in sorted(PLATFORMS)},
        "by_grade": {g: grades[g] for g in ("B", "C")},
        "weekly_gap": {p: max(0, target - sum(
            item.get("platform") == p and item.get("evidence_grade") == "B"
            and item.get("period_scope") == "week_mentioned" for item in candidates
        )) for p in sorted(PLATFORMS)},
        "totals_match": (len(candidates) == sum(platforms[p] for p in PLATFORMS)
                         == sum(grades[g] for g in ("B", "C"))),
    }


def check(folder):
    folder = Path(folder)
    run = read_json(folder / "run.json")
    config = load_config(folder / "config.snapshot.json")
    sources = read_json(folder / "sources.json")
    candidates = read_json(folder / "candidates.json")
    errors = []
    if run["config_sha256"] != hashlib.sha256((folder / "config.snapshot.json").read_bytes()).hexdigest():
        errors.append("配置快照已更改")
    start, end = date.fromisoformat(run["window_start"]), date.fromisoformat(run["window_end"])
    if end - start != timedelta(days=config["lookback_days"] - 1):
        errors.append("研究窗口与配置不一致")
    if run.get("status") not in {"prepared", "completed", "partial", "blocked"}:
        errors.append("运行状态无效")
    source_map = {}
    for source in sources:
        sid = source.get("id")
        if not sid or sid in source_map:
            errors.append(f"来源 ID 缺失或重复：{sid}")
        source_map[sid] = source
        if not valid_url(source.get("url")) or not source.get("title"):
            errors.append(f"来源链接或标题无效：{sid}")
        if source.get("access_status") not in {"read", "limited", "blocked"}:
            errors.append(f"来源访问状态无效：{sid}")
        try:
            observed = datetime.fromisoformat(source["observed_at"])
            if observed.utcoffset() is None:
                raise ValueError("需要时区")
        except (ValueError, TypeError, KeyError):
            errors.append(f"来源观察时间需要包含时区：{sid}")
        for field in ("published_on", "coverage_start", "coverage_end"):
            if source.get(field) is not None:
                try:
                    date.fromisoformat(source[field])
                except (ValueError, TypeError):
                    errors.append(f"来源日期无效：{sid}.{field}")
        if bool(source.get("coverage_start")) != bool(source.get("coverage_end")):
            errors.append(f"来源统计期必须包含起止日期：{sid}")
        if source.get("coverage_start") and source.get("coverage_end") and source["coverage_start"] > source["coverage_end"]:
            errors.append(f"来源统计期倒置：{sid}")
    ids, weekly, background = set(), Counter(), Counter()
    for item in candidates:
        cid, platform = item.get("id"), item.get("platform")
        if not cid or cid in ids:
            errors.append(f"候选 ID 缺失或重复：{cid}")
        ids.add(cid)
        if platform not in PLATFORMS:
            errors.append(f"平台无效：{cid}")
        if not item.get("topic") or not item.get("style") or not item.get("limitations"):
            errors.append(f"候选缺少 topic、style 或限制说明：{cid}")
        if item.get("rank_type") != "unranked_candidate":
            errors.append(f"第一步候选不能标为官方排名：{cid}")
        if type(item.get("original_post_verified")) is not bool:
            errors.append(f"原帖核验必须为布尔值：{cid}")
        refs = item.get("source_ids", [])
        if not refs or any(s not in source_map for s in refs):
            errors.append(f"候选来源缺失或无法对应：{cid}")
        linked = [source_map[s] for s in refs if s in source_map]
        if not any(s.get("access_status") in {"read", "limited"} for s in linked):
            errors.append(f"候选不能仅依赖访问失败的来源：{cid}")
        grade, scope = item.get("evidence_grade"), item.get("period_scope")
        if grade == "B" and scope == "week_mentioned":
            # A date on an article is evidence of mention, never proof of weekly popularity.
            def mentioned_this_week(source):
                try:
                    published = source.get("published_on")
                    if published and start <= date.fromisoformat(published) <= end:
                        return True
                    a, b = source.get("coverage_start"), source.get("coverage_end")
                    return bool(a and b and date.fromisoformat(a) <= end and date.fromisoformat(b) >= start)
                except (ValueError, TypeError):
                    return False
            if not any(mentioned_this_week(s) for s in linked):
                errors.append(f"本周提及缺少日期依据：{cid}")
            weekly[platform] += 1
        elif grade == "C" and scope in {"longer_window", "undated"}:
            background[platform] += 1
        else:
            errors.append(f"证据等级和时间范围不匹配：{cid}")
        if item.get("original_post_verified") and (
            not valid_url(item.get("original_post_url")) or not item.get("original_observation")
        ):
            errors.append(f"原帖已核验必须记录链接和观察：{cid}")
    target = config["target_candidates_per_platform"]
    coverage = {p: {"weekly_candidates": weekly[p], "background_references": background[p],
                    "target": target, "gap": max(0, target - weekly[p])} for p in sorted(PLATFORMS)}
    gaps = any(v["gap"] for v in coverage.values())
    if run.get("status") != "prepared":
        if not (folder / "report.md").read_text(encoding="utf-8").strip():
            errors.append("缺少研究报告")
        if gaps and run.get("status") == "completed":
            errors.append("本周候选不足时应标为 partial 或 blocked")
        if run.get("status") == "blocked" and candidates:
            errors.append("已有有效候选时应保留为 partial")
        if any(not str(run.get("platform_notes", {}).get(p, "")).strip() for p in PLATFORMS):
            errors.append("每个平台必须记录覆盖情况和限制")
    return {"valid": not errors, "status": run.get("status"), "coverage": coverage,
            "summary": summarize_candidates(candidates, target), "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare", help="创建空白运行目录；不会搜索网页")
    prep.add_argument("--date", help="截止日期 YYYY-MM-DD；默认按配置时区取今天")
    prep.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    prep.add_argument("--output-root", type=Path)
    validate = sub.add_parser("check", help="校验来源、证据与窗口；不会证明来源内容真实")
    validate.add_argument("folder", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            print(prepare(args.config, args.date, args.output_root))
        else:
            result = check(args.folder)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["valid"] else 1
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f"研究文件错误：{exc}\n")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
