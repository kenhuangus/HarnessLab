from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'-]*")


def word_count(path: Path) -> int:
    return len(WORD_RE.findall(path.read_text(encoding="utf-8")))


def check_readmes() -> list[str]:
    failures: list[str] = []
    readmes = [ROOT / "README.md"] + [ROOT / "chapters" / f"ch{i:02d}" / "README.md" for i in range(1, 11)]
    for readme in readmes:
        if not readme.exists():
            failures.append(f"missing README: {readme.relative_to(ROOT)}")
            continue
        count = word_count(readme)
        if count < 2000:
            failures.append(f"{readme.relative_to(ROOT)} has {count} words, expected at least 2000")
    return failures


def run_tests() -> int:
    return subprocess.call([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=ROOT)


def main() -> int:
    exit_code = run_tests()
    failures = check_readmes()
    for failure in failures:
        print(failure, file=sys.stderr)
    return 1 if exit_code or failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

