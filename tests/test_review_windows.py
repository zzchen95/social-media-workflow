from datetime import datetime

import pytest

from scripts.review_windows import calculate


@pytest.mark.parametrize("start", ["2020-03-07T12:00:00-08:00", "2020-10-31T12:00:00-07:00"])
def test_exact_hours_across_dst(start):
    result = calculate(start, "America/Los_Angeles")
    origin = datetime.fromisoformat(result["published_at_utc"])
    for label, hours in (("D1", 24), ("D7", 168)):
        target = result["targets"][label]
        assert (datetime.fromisoformat(target["target_utc"]) - origin).total_seconds() == hours * 3600
        assert datetime.fromisoformat(target["target_local"]) == datetime.fromisoformat(target["target_utc"])
    assert result["targets"]["D1"]["target_local"][11:16] != "12:00"


def test_date_only_never_fills_midnight():
    result = calculate("2020-10-18", "America/Los_Angeles")
    assert result["targets"] == {"D1": None, "D7": None}
    assert result["observed_age_hours"] is None


def test_late_observation_keeps_actual_age():
    result = calculate("2020-10-18T12:00:00-07:00", "America/Los_Angeles", "2020-10-19T19:00:00-07:00")
    assert result["observed_age_hours"] == 31
    assert result["targets"]["D1"]["sample_status"] == "late"
    assert result["targets"]["D1"]["delta_hours"] == 7


def test_missing_observation_is_unknown_not_zero():
    result = calculate("2020-10-18T12:00:00-07:00", "UTC")
    assert result["observed_age_hours"] is None
    assert result["targets"]["D7"]["sample_status"] == "unknown"


@pytest.mark.parametrize("start,end", [("2020-10-18T12:00:00", None),
                                      ("2020-10-18T12:00:00-07:00", "2020-10-17T12:00:00-07:00")])
def test_ambiguous_or_reversed_time_rejected(start, end):
    with pytest.raises(ValueError):
        calculate(start, "UTC", end)


def test_nonfinite_tolerance_rejected():
    with pytest.raises(ValueError):
        calculate("2020-10-18T12:00:00-07:00", "UTC", d1_tolerance=float("nan"))


def test_date_only_does_not_accept_ambiguous_data_cutoff():
    with pytest.raises(ValueError):
        calculate("2020-10-18", "UTC", "2020-10-19T12:00:00")
