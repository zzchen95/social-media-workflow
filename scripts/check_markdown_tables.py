"""Check GFM pipe-table column counts outside fenced code blocks (read-only)."""
import argparse
import sys
import json
from pathlib import Path
import re


def cells(line):
    # A pipe is escaped iff immediately preceded by an odd number of backslashes.
    parts, start, slashes = [], 0, 0
    for index, char in enumerate(line):
        if char == "|" and slashes % 2 == 0:
            parts.append(line[start:index].strip())
            start = index + 1
        slashes = slashes + 1 if char == "\\" else 0
    parts.append(line[start:].strip())
    if len(parts) == 1:
        return None
    if not parts[0]:
        parts.pop(0)
    if parts and not parts[-1]:
        parts.pop()
    return parts


def check_tables(text):
    errors, previous, expected, fence = [], None, None, None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence, previous, expected = marker[1], None, None
            continue
        row = cells(line)
        if row and all(re.fullmatch(r":?-+:?", cell) for cell in row) and previous:
            expected = len(row)
            if len(previous[1]) != expected:
                errors.append({"line": previous[0], "expected": expected, "actual": len(previous[1])})
        elif expected and row:
            if len(row) != expected:
                errors.append({"line": number, "expected": expected, "actual": len(row)})
        else:
            expected = None
        previous = (number, row) if row else None
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()
    results = []
    for path in args.files:
        try:
            errors = check_tables(path.read_text(encoding="utf-8"))
            results.append({"file": str(path), "errors": errors, "valid": not errors})
        except OSError as exc:
            results.append({"file": str(path), "error": str(exc), "valid": False})
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(result["valid"] for result in results) else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
