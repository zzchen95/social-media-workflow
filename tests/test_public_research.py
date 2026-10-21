import copy

from scripts.public_research import check, prepare, read_json, write_json


def sample(folder):
    run = read_json(folder / "run.json")
    run["status"] = "partial"
    run["platform_notes"] = {p: "公开资料覆盖有限，未取得完整榜单" for p in run["platform_notes"]}
    write_json(folder / "run.json", run)
    write_json(folder / "sources.json", [{
        "id": "S1", "url": "https://example.com/research", "title": "本周编辑观察",
        "observed_at": "2020-10-18T10:00:00-07:00", "published_on": "2020-10-16",
        "coverage_start": None, "coverage_end": None, "access_status": "read",
    }])
    item = {
        "id": "TT01", "platform": "tiktok", "topic": "测试主题", "style": "测试形式",
        "source_ids": ["S1"], "evidence_grade": "B", "period_scope": "week_mentioned",
        "original_post_verified": False, "rank_type": "unranked_candidate",
        "limitations": "测试数据；未独立核验原帖",
    }
    write_json(folder / "candidates.json", [item])
    (folder / "report.md").write_text("测试报告，非真实趋势。", encoding="utf-8")
    return item


def test_prepare_preserves_runs_and_seven_day_window(tmp_path):
    first = prepare(end_date="2020-10-18", output_root=tmp_path)
    (first / "report.md").write_text("保留已有结果", encoding="utf-8")
    second = prepare(end_date="2020-10-18", output_root=tmp_path)
    assert first != second
    assert (first / "report.md").read_text(encoding="utf-8") == "保留已有结果"
    assert read_json(first / "run.json")["window_start"] == "2020-10-12"
    assert read_json(second / "sources.json") == []
    assert check(second)["status"] == "prepared"


def test_background_does_not_fill_weekly_gap(tmp_path):
    folder = prepare(end_date="2020-10-18", output_root=tmp_path)
    item = sample(folder)
    background = copy.deepcopy(item)
    background.update(id="XH01", platform="xiaohongshu", evidence_grade="C", period_scope="longer_window")
    write_json(folder / "candidates.json", [item, background])
    result = check(folder)
    assert result["valid"]
    assert result["coverage"]["tiktok"]["weekly_candidates"] == 1
    assert result["coverage"]["xiaohongshu"]["gap"] == 10
    run = read_json(folder / "run.json")
    run["status"] = "completed"
    write_json(folder / "run.json", run)
    assert not check(folder)["valid"]


def test_rejects_missing_sources_and_false_verification(tmp_path):
    folder = prepare(end_date="2020-10-18", output_root=tmp_path)
    item = sample(folder)
    item.update(source_ids=["missing"], original_post_verified=True)
    write_json(folder / "candidates.json", [item, item])
    result = check(folder)
    assert not result["valid"]
    assert len(result["errors"]) >= 3


def test_rejects_old_article_as_this_week_and_bad_observation_date(tmp_path):
    folder = prepare(end_date="2020-10-18", output_root=tmp_path)
    sample(folder)
    sources = read_json(folder / "sources.json")
    sources[0].update(published_on="2020-10-02", observed_at="2020-10-18T10:00:00")
    write_json(folder / "sources.json", sources)
    assert not check(folder)["valid"]


def test_rolling_window_across_dst(tmp_path):
    folder = prepare(end_date="2020-03-10", output_root=tmp_path)
    run = read_json(folder / "run.json")
    assert run["window_start"] == "2020-03-04"
    assert run["timezone"] == "America/Los_Angeles"
    assert check(folder)["valid"]


def test_summary_uses_candidate_data_and_keeps_old_interface(tmp_path):
    folder = prepare(end_date="2020-10-18", output_root=tmp_path)
    item = sample(folder)
    items = [dict(item, id=f"C{i}", platform=p, evidence_grade=g,
                  period_scope="week_mentioned" if g == "B" else "undated")
             for i, (p, g) in enumerate([
                 ("tiktok", "B"), ("tiktok", "C"), ("instagram", "B"),
                 ("xiaohongshu", "C"), ("instagram", "C"), ("instagram", "B")])]
    for subset in (items, items[:2], []):
        write_json(folder / "candidates.json", subset)
        result = check(folder)
        summary = result["summary"]
        assert result["valid"]  # legacy run with no new search_log remains readable
        assert {"status", "coverage", "errors"} <= result.keys()
        assert summary["totals_match"]
        assert summary["total"] == len(subset) == sum(summary["by_platform"].values()) == sum(summary["by_grade"].values())
        assert summary["weekly_gap"]["xiaohongshu"] == 10
    write_json(folder / "candidates.json", items)
    assert check(folder)["summary"]["by_grade"] == {"B": 3, "C": 3}
