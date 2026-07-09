from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harnesslab.labs import CHAPTERS

CHAPTER_KEYS = {chapter.key for chapter in CHAPTERS}


def result_dir(chapter: str) -> Path:
    return ROOT / "chapters" / chapter / "LabResult"


def capture_chapter(chapter: str) -> None:
    if chapter not in CHAPTER_KEYS:
        known = ", ".join(sorted(CHAPTER_KEYS))
        raise ValueError(f"unknown chapter {chapter!r}; expected one of: {known}")

    command = [sys.executable, "-m", "harnesslab.cli", "run", chapter, "--json"]
    completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    out_dir = result_dir(chapter)
    out_dir.mkdir(parents=True, exist_ok=True)
    stdout = completed.stdout.strip() + "\n"
    stderr = completed.stderr.strip() + ("\n" if completed.stderr.strip() else "")
    (out_dir / "stdout.txt").write_text(stdout, encoding="utf-8")
    (out_dir / "stderr.txt").write_text(stderr, encoding="utf-8")

    if completed.returncode != 0:
        raise RuntimeError(f"{chapter} run failed with exit code {completed.returncode}; see {out_dir / 'stderr.txt'}")

    payload = json.loads(completed.stdout)
    if not isinstance(payload, list) or len(payload) != 1:
        raise RuntimeError(f"{chapter} CLI output did not contain exactly one result object")
    result = payload[0]
    (out_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    readme = f"""# **LabResult for {chapter.upper()}**

This folder stores the captured run result for `{chapter}`.

Generated command:

```bash
python -m harnesslab.cli run {chapter} --json
```

Files:

- `result.json`: parsed `LabResult` object returned by the public HarnessLab CLI.
- `stdout.txt`: raw standard output from the CLI run.
- `stderr.txt`: raw standard error from the CLI run. This should normally be empty.

The repository QA gate validates that this result is present, parseable, chapter-matched, passing, and supported by decisions and artifacts.
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture actual HarnessLab chapter run results.")
    parser.add_argument("chapters", nargs="*", help="Chapter keys to capture, e.g. ch01 ch02. Defaults to all chapters.")
    args = parser.parse_args()
    targets = args.chapters or [chapter.key for chapter in CHAPTERS]

    for chapter in targets:
        capture_chapter(chapter)
        print(f"captured {chapter} -> {result_dir(chapter).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
