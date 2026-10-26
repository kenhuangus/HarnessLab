"""Command-line interface for HarnessLab."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from .labs import CHAPTERS, run_all_labs, run_lab
from .verify import run_verify


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="harnesslab", description="Run HarnessLab chapter scenarios, verifications, and capstones.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List available chapter labs.")

    run = sub.add_parser("run", help="Run a chapter lab or all labs.")
    run.add_argument("chapter", help="Chapter key such as ch01, or 'all'.")
    run.add_argument("--json", action="store_true", help="Print machine-readable JSON.")

    verify = sub.add_parser("verify", help="Run automated student verification and readiness certification.")
    verify.add_argument("--ch", default=None, help="Verify only a specific chapter (e.g. ch01).")
    verify.add_argument("--json", action="store_true", help="Output verification report as JSON.")

    capstone = sub.add_parser("capstone", help="Run multi-agent security remediation fleet capstone demonstration.")
    capstone.add_argument("--json", action="store_true", help="Print capstone results as JSON.")

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

    if args.command == "verify":
        return run_verify(selected_chapter=args.ch, as_json=args.json)

    if args.command == "capstone":
        try:
            from capstone.remediation_fleet import run_capstone
            res = run_capstone()
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print("=" * 76)
                print(" HARNESSLAB CAPSTONE: AUTONOMOUS SECURITY REMEDIATION FLEET")
                print("=" * 76)
                print(f" Triage Status  : {res['triage_status']}")
                print(f" Quarantine     : {res.get('quarantine_findings')}")
                print(f" Patch Status   : {res['patch_status']}")
                print(f" Diff SHA-256   : {res['patch_diff_hash'][:16]}...")
                print(f" Deploy Status  : {res['deploy_status']}")
                print(f" Evidence Hash  : {res['evidence_envelope_hash']}")
                print(f" Decisions Total: {res['total_decisions_recorded']}")
                print("=" * 76)
            return 0
        except Exception as exc:
            print(f"Failed to execute capstone: {exc}", file=sys.stderr)
            return 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
