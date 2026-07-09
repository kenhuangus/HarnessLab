from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'-]*")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)


def word_count(path: Path) -> int:
    return len(WORD_RE.findall(path.read_text(encoding="utf-8")))


def normalized_blocks(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"(?:\r?\n){2,}", text)
    normalized = []
    for block in blocks:
        compact = re.sub(r"\s+", " ", block).strip()
        if len(compact) >= 160:
            normalized.append(compact)
    return normalized


def duplicate_headings(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    headings = [match.group(1).strip().lower() for match in HEADING_RE.finditer(text)]
    seen: set[str] = set()
    duplicates: list[str] = []
    for heading in headings:
        if heading in seen and heading not in duplicates:
            duplicates.append(heading)
        seen.add(heading)
    return duplicates


def check_readmes() -> list[str]:
    failures: list[str] = []
    readmes = [ROOT / "README.md"] + [ROOT / "chapters" / f"ch{i:02d}" / "README.md" for i in range(1, 11)]
    global_blocks: dict[str, Path] = {}
    for readme in readmes:
        if not readme.exists():
            failures.append(f"missing README: {readme.relative_to(ROOT)}")
            continue
        count = word_count(readme)
        if count < 2000:
            failures.append(f"{readme.relative_to(ROOT)} has {count} words, expected at least 2000")
        for heading in duplicate_headings(readme):
            failures.append(f"{readme.relative_to(ROOT)} repeats heading: {heading}")
        local_blocks: set[str] = set()
        for block in normalized_blocks(readme):
            if block in local_blocks:
                failures.append(f"{readme.relative_to(ROOT)} repeats a long paragraph: {block[:120]}...")
            local_blocks.add(block)
            if block in global_blocks and global_blocks[block] != readme:
                failures.append(
                    f"{readme.relative_to(ROOT)} duplicates a long paragraph from "
                    f"{global_blocks[block].relative_to(ROOT)}: {block[:120]}..."
                )
            else:
                global_blocks[block] = readme
    return failures


def check_lab_results() -> list[str]:
    failures: list[str] = []
    for chapter_num in range(1, 11):
        chapter = f"ch{chapter_num:02d}"
        folder = ROOT / "chapters" / chapter / "LabResult"
        if not folder.exists():
            failures.append(f"missing LabResult folder: {folder.relative_to(ROOT)}")
            continue
        result_path = folder / "result.json"
        stdout_path = folder / "stdout.txt"
        stderr_path = folder / "stderr.txt"
        readme_path = folder / "README.md"
        for path in (result_path, stdout_path, stderr_path, readme_path):
            if not path.exists():
                failures.append(f"missing LabResult file: {path.relative_to(ROOT)}")
        if not result_path.exists() or not stdout_path.exists():
            continue

        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{result_path.relative_to(ROOT)} is not valid JSON: {exc}")
            continue

        required = {"chapter", "title", "passed", "score", "summary", "decisions", "artifacts"}
        missing = required - set(result)
        if missing:
            failures.append(f"{result_path.relative_to(ROOT)} missing keys: {sorted(missing)}")
        if result.get("chapter") != chapter:
            failures.append(f"{result_path.relative_to(ROOT)} chapter mismatch: {result.get('chapter')!r}")
        if result.get("passed") is not True:
            failures.append(f"{result_path.relative_to(ROOT)} did not capture a passing run")
        if not isinstance(result.get("score"), int | float) or result.get("score", 0) < 0.8:
            failures.append(f"{result_path.relative_to(ROOT)} score below expected threshold")
        if not result.get("decisions"):
            failures.append(f"{result_path.relative_to(ROOT)} has no decisions")
        if not result.get("artifacts"):
            failures.append(f"{result_path.relative_to(ROOT)} has no artifacts")

        try:
            stdout_result = json.loads(stdout_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{stdout_path.relative_to(ROOT)} is not valid JSON: {exc}")
            continue
        if not isinstance(stdout_result, list) or stdout_result != [result]:
            failures.append(f"{stdout_path.relative_to(ROOT)} does not match result.json")
    return failures


def run_tests() -> int:
    return subprocess.call([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=ROOT)


def main() -> int:
    exit_code = run_tests()
    failures = [*check_readmes(), *check_lab_results()]
    for failure in failures:
        print(failure, file=sys.stderr)
    return 1 if exit_code or failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
