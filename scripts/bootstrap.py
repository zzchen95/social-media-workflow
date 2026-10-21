"""Set up a repo-local environment, or check without installing anything."""
import argparse
from pathlib import Path
import subprocess
import sys
import venv
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parents[1]


def env_python(folder):
    return folder / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def check():
    if sys.version_info < (3, 11):
        print("Python 3.11+ is required.", file=sys.stderr)
        return 1
    try:
        ZoneInfo("America/Los_Angeles")
    except ZoneInfoNotFoundError:
        print("Timezone data missing. Install tzdata into this interpreter, then retry.", file=sys.stderr)
        return 1
    result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_share.py")], cwd=ROOT)
    if result.returncode:
        return result.returncode
    print("Local files and timezone checked. Client skill discovery and media tools still need their own verification.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only check; no environment creation or install")
    args = parser.parse_args()
    if args.check:
        return check()
    if sys.version_info < (3, 11):
        print("Python 3.11+ is required.", file=sys.stderr)
        return 1
    folder = ROOT / ".venv"
    executable = env_python(folder)
    if folder.exists():
        if not (folder / "pyvenv.cfg").is_file() or not executable.is_file():
            print("Existing .venv is not usable on this system; no files overwritten.", file=sys.stderr)
            return 1
    else:
        venv.EnvBuilder(with_pip=True).create(folder)
    subprocess.run([str(executable), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")], cwd=ROOT, check=True)
    return subprocess.run([str(executable), str(__file__), "--check"], cwd=ROOT).returncode


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Setup did not finish: {exc}. Existing files were preserved; retry after resolving the reported issue.", file=sys.stderr)
        raise SystemExit(1)
