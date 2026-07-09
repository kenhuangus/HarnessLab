"""Executable runner for Chapter 5."""

from __future__ import annotations

from .scenario import run


def main() -> int:
    result = run()
    print(result.to_json())
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
