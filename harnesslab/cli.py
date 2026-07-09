"""Command-line interface for HarnessLab."""

from __future__ import annotations

import argparse
import json
import sys

from .labs import CHAPTERS, run_all_labs, run_lab


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="harnesslab", description="Run HarnessLab chapter scenarios.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List available chapter labs.")
    run = sub.add_parser("run", help="Run a chapter lab or all labs.")
    run.add_argument("chapter", help="Chapter key such as ch01, or 'all'.")
    run.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        for chapter in CHAPTERS:
            print(f"{chapter.key}\t{chapter.title}")
        return 0

    if args.command == "run":
        results = run_all_labs() if args.chapter == "all" else [run_lab(args.chapter)]
        if args.json:
            print(json.dumps([result.to_dict() for result in results], indent=2, sort_keys=True))
        else:
            for result in results:
                status = "PASS" if result.passed else "FAIL"
                print(f"{result.chapter} {status} score={result.score:.3f} {result.title}")
                print(f"  {result.summary}")
        return 0 if all(result.passed for result in results) else 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

