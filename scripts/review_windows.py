"""Calculate D1/D7 targets in UTC, with explicit precision and observation age."""
import argparse
from datetime import date, datetime, timedelta, timezone
import json
import math
import sys
from zoneinfo import ZoneInfo


def aware(value):
    parsed = datetime.fromisoformat(value)
    if parsed.utcoffset() is None:
        raise ValueError("timestamp must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def calculate(published_at, zone_name, data_through=None, d1_tolerance=3, d7_tolerance=12):
    zone = ZoneInfo(zone_name)
    for value in (d1_tolerance, d7_tolerance):
        if not math.isfinite(value) or value < 0:
            raise ValueError("tolerances must be finite and nonnegative")
    end = aware(data_through) if data_through else None
    try:
        date.fromisoformat(published_at)
        date_only = len(published_at) == 10
    except ValueError:
        date_only = False
    if date_only:
        return {"precision": "date_only", "timezone": zone_name, "published_at": published_at,
                "data_through": data_through, "observed_age_hours": None, "targets": {"D1": None, "D7": None}}
    start = aware(published_at)
    if end and end < start:
        raise ValueError("data cutoff precedes publication")
    age = (end - start).total_seconds() / 3600 if end else None
    targets = {}
    for label, hours, tolerance in (("D1", 24, d1_tolerance), ("D7", 168, d7_tolerance)):
        target = start + timedelta(hours=hours)
        delta = age - hours if age is not None else None
        status = "unknown" if delta is None else "early" if delta < -tolerance else "late" if delta > tolerance else "within_tolerance"
        targets[label] = {"target_utc": target.isoformat(), "target_local": target.astimezone(zone).isoformat(),
                          "tolerance_hours": tolerance, "delta_hours": delta, "sample_status": status}
    return {"precision": "timestamp", "timezone": zone_name, "published_at_utc": start.isoformat(),
            "published_at_local": start.astimezone(zone).isoformat(), "data_through_utc": end.isoformat() if end else None,
            "observed_age_hours": age, "targets": targets}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published-at", required=True)
    parser.add_argument("--timezone", required=True)
    parser.add_argument("--data-through")
    parser.add_argument("--d1-tolerance-hours", type=float, default=3)
    parser.add_argument("--d7-tolerance-hours", type=float, default=12)
    args = parser.parse_args()
    try:
        result = calculate(args.published_at, args.timezone, args.data_through, args.d1_tolerance_hours, args.d7_tolerance_hours)
    except (ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
