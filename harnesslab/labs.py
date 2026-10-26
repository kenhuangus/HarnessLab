"""Chapter registry and execution helpers."""

from __future__ import annotations

import importlib
from dataclasses import dataclass

from .core import LabResult


@dataclass(frozen=True)
class Chapter:
    key: str
    title: str
    module: str


CHAPTERS: tuple[Chapter, ...] = (
    Chapter("ch01", "Harness as the Control Plane for Long-Horizon Multi-Agent Systems", "chapters.ch01.scenario"),
    Chapter("ch02", "Autonomy: Graduated Control and Human Oversight", "chapters.ch02.scenario"),
    Chapter("ch03", "Identity: Per-Agent Identity and Delegation Chains", "chapters.ch03.scenario"),
    Chapter("ch04", "Intent: Contracts, Drift Detection, and Authorization by Purpose", "chapters.ch04.scenario"),
    Chapter("ch05", "Context: Trust Tiers, Provenance, and Context-Poisoning Containment", "chapters.ch05.scenario"),
    Chapter("ch06", "Memory: State Firewall, Ledger, and Forgetting", "chapters.ch06.scenario"),
    Chapter("ch07", "Observability, Evals, and Hill-Climbing Evidence", "chapters.ch07.scenario"),
    Chapter("ch08", "Runtime Steering: Intervention, Policy Injection, and Safe Rollback", "chapters.ch08.scenario"),
    Chapter("ch09", "Scalability: Fleet Coordination Without Cascading Failure", "chapters.ch09.scenario"),
    Chapter("ch10", "Data Governance: Classification-Aware Tools, Egress, and Compliance", "chapters.ch10.scenario"),
)


def get_chapter(key: str) -> Chapter:
    normalized = key.lower().strip()
    for chapter in CHAPTERS:
        if chapter.key == normalized:
            return chapter
    known = ", ".join(chapter.key for chapter in CHAPTERS)
    raise KeyError(f"unknown chapter {key!r}; expected one of: {known}")


def run_lab(key: str) -> LabResult:
    chapter = get_chapter(key)
    module = importlib.import_module(chapter.module)
    result = module.run()
    if not isinstance(result, LabResult):
        raise TypeError(f"{chapter.module}.run() returned {type(result)!r}, expected LabResult")
    if result.chapter != chapter.key:
        raise ValueError(f"{chapter.module}.run() returned chapter {result.chapter!r}, expected {chapter.key!r}")
    return result


def run_all_labs() -> list[LabResult]:
    return [run_lab(chapter.key) for chapter in CHAPTERS]

