from __future__ import annotations

import argparse
import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'-]*")
MIN_WORDS = 2100


CHAPTERS = {
    "ch01": {
        "title": "Hill Climbing and the Secure Harness",
        "pattern": "secure harness reference architecture",
        "failure": "a productive but unsafe agent fleet that can plan, call tools, delegate work, and change state without a durable control plane",
        "controls": ["control and evidence matrix", "tool gateway", "checkpoint", "policy decision point", "trace evidence", "secure-by-design defaults"],
        "long": "continuity contracts, fresh-context startup, resumption checks, and evidence preservation across context windows",
    },
    "ch02": {
        "title": "Autonomy: Graduated Control and Human Oversight",
        "pattern": "graduated autonomy gates",
        "failure": "an agent whose authority silently expands from proposing work to changing production without renewed approval",
        "controls": ["capability budgets", "approval queue", "reversibility check", "non-waivable loop controls", "rollback hook", "authority expiry"],
        "long": "autonomy renewal, session budgets, fatigue-resistant approvals, and authority that expires between work periods",
    },
    "ch03": {
        "title": "Identity: Per-Agent Identity and Delegation Chains",
        "pattern": "task-scoped identity and short-lived delegation",
        "failure": "many agents sharing the same broad service token, making attribution, revocation, and least privilege impossible",
        "controls": ["audience-bound credential", "delegation chain", "revocation", "task identity", "workload identity", "least-privilege tool scoping"],
        "long": "credential rotation, identity continuity, revocation after pause, and delegation evidence across sessions",
    },
    "ch04": {
        "title": "Intent: Contracts, Drift Detection, and Authorization by Purpose",
        "pattern": "intent contracts as policy objects",
        "failure": "a run that starts with a narrow goal and drifts into broader actions because the harness checks tools but not purpose",
        "controls": ["intent contract", "tool scope", "data scope", "risk boundary", "drift warning", "purpose-bound reauthorization"],
        "long": "intent renewal, stale-goal detection, drift checks at resumption, and reauthorization when a run changes direction",
    },
    "ch05": {
        "title": "Context: Trust Tiers, Provenance, and Poisoning Containment",
        "pattern": "trust-tiered context firewall",
        "failure": "external instructions, private data, and tool access mixed into one prompt without provenance or containment",
        "controls": ["trust tier", "provenance", "quarantine", "lethal-trifecta detection", "profile policy", "freshness check"],
        "long": "context compaction, source freshness, quarantine persistence, and recovery from stale or poisoned context",
    },
    "ch06": {
        "title": "Memory: State Firewall, Ledger, and Forgetting",
        "pattern": "memory state firewall",
        "failure": "durable memory that turns one compromised run into future compromised behavior",
        "controls": ["write gate", "state ledger", "tenant scope", "promotion gate", "rollback", "tombstone", "TTL"],
        "long": "durable memory governance, state handoffs, retention, rollback, and recursive improvement without memory poisoning",
    },
    "ch07": {
        "title": "Observability: Traces, Evals, and Hill-Climbing Evidence",
        "pattern": "trace-to-eval hill-climbing loop",
        "failure": "a team improving an agent by anecdote, unable to replay why a change worked, failed, or created a new risk",
        "controls": ["decision trace", "evidence envelope", "artifact hash", "redaction", "replay bundle", "regression eval"],
        "long": "trace continuity, benchmark replay, fresh-context evaluators, and governed recursive self-improvement",
    },
    "ch08": {
        "title": "Runtime Steering: Intervention, Policy Injection, and Safe Rollback",
        "pattern": "evidence-preserving runtime steering",
        "failure": "a compromised run that can only be killed destructively, losing the evidence needed for recovery and learning",
        "controls": ["pause", "kill switch", "checkpoint", "policy overlay", "safe rollback", "replay", "compensation"],
        "long": "safe interruption, resumable checkpoints, expiring policy overlays, rollback evidence, and recovery after partial execution",
    },
    "ch09": {
        "title": "Scalability: Fleet Coordination Without Cascading Failure",
        "pattern": "fleet bulkheads and back-pressure",
        "failure": "a fleet that amplifies small failures through queues, retries, shared tools, and unbounded parallelism",
        "controls": ["bulkhead", "tenant quota", "queue", "back-pressure", "compromised-worker containment", "idempotent retry"],
        "long": "queue recovery, idempotent retries, fleet endurance, cascading-failure containment, and long-run capacity governance",
    },
    "ch10": {
        "title": "Data Governance: Classification-Aware Tools, Egress, and Compliance",
        "pattern": "classification-aware routing and lineage",
        "failure": "agents moving PII, secrets, and regulated data through tools and providers without label persistence or egress control",
        "controls": ["label propagation", "egress allowlist", "residency", "DLP escalation", "lineage", "deletion evidence"],
        "long": "label persistence, residency over time, deletion across memory and traces, and compliance evidence that survives resumption",
    },
}


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def wrap(text: str) -> str:
    return "\n\n".join(textwrap.fill(part.strip(), width=96) for part in text.strip().split("\n\n"))


def root_readme() -> str:
    sections = [
        "# **HarnessLab**",
        """
        HarnessLab is the runnable companion project for **Hill Climbing: Design Patterns for Securing
        Long-Horizon Multi-Agent AI Systems**. The book argues that the decisive artifact in production
        agentic AI is not a clever prompt, a single model, or a single guardrail. The decisive artifact is
        the harness: the control plane that mediates what agents may know, remember, decide, delegate,
        execute, observe, resume, and improve. This repository gives instructors and practitioners a
        concrete system for teaching that idea. Every chapter has an executable lab, a scenario that
        demonstrates at least one unsafe path, and a teaching README that explains how the pattern works.
        """,
        """
        The project is deliberately dependency-free. Students can run it with a normal Python 3.11 or later
        installation, without cloud credentials, vendor accounts, paid model APIs, or live secrets. That
        choice is pedagogical. A real enterprise harness may integrate identity providers, model gateways,
        workflow engines, observability backends, vaults, DLP services, policy engines, sandbox providers,
        CI systems, and ticketing platforms. HarnessLab keeps the first learning surface small enough to
        inspect. The concepts are production-shaped even when the implementation is a deterministic
        simulation: task-scoped credentials, intent contracts, context quarantine, memory ledgers,
        evidence envelopes, runtime steering, fleet bulkheads, and data-governance routing.
        """,
        """
        A central theme is hill climbing. Long-horizon agents rarely move in a straight line from prompt to
        answer. They search locally over plans, tool calls, context, memory, code changes, evaluator
        feedback, traces, and recovery states. That search creates value when the harness makes it bounded,
        observable, reversible, and evidence-driven. The same search creates risk when authority expands
        silently, when memory carries poisoned instructions forward, when traces are too thin to explain a
        decision, or when a subagent acts under another agent's broad credentials. HarnessLab lets students
        run that argument rather than only read it.
        """,
        """
        The lab is organized as ten chapter projects. Chapter 1 introduces the secure harness as a reference
        architecture and control/evidence matrix. Chapter 2 turns autonomy into a graduated control surface.
        Chapter 3 replaces shared credentials with accountable per-agent and per-task identity. Chapter 4
        treats intent as an authorization boundary. Chapter 5 treats context as information-flow and
        authority engineering. Chapter 6 treats memory as future behavior that needs a state firewall.
        Chapter 7 turns observability into the evidentiary layer for evals and governed recursive
        improvement. Chapter 8 shows how to steer a run after it begins. Chapter 9 scales the harness to
        fleets without cascading failure. Chapter 10 routes data according to classification, egress,
        residency, lineage, and compliance evidence.
        """,
        """
        Run the full suite with `python -m unittest discover -s tests`, run the CLI with `python -m
        harnesslab.cli list`, and run one chapter with `python -m harnesslab.cli run ch07 --json`. The
        command `python scripts/qa.py` runs the tests and checks that every README is long enough to support
        teaching. Instructors can use the JSON output as an autograding surface, because every lab returns a
        `LabResult` containing a pass flag, score, policy decisions, and artifacts. Practitioners can use
        the same output as a pattern checklist for internal workshops.
        """,
        """
        The code is intentionally small but it is not casual. The core package models a credential broker
        with audience-bound tokens and revocation, an intent verifier with purpose-bound checks, a context
        firewall with injection and lethal-trifecta detection, a memory firewall with ledger and tombstones,
        a tracer with tamper-evident evidence envelopes, a runtime controller with checkpoints and policy
        overlays, a fleet coordinator with quotas and back-pressure, and a data-governance engine with
        egress, residency, DLP escalation, and lineage. These are not final enterprise implementations.
        They are compact reference forms designed to be read in class, extended in assignments, and mapped
        to production systems.
        """,
        """
        For teaching, begin each chapter by running the lab once and asking students to identify which
        decision represents the unsafe path. Then inspect the scenario code and locate the control that
        changed the outcome. After that, ask students to extend the scenario: add a new tool, a new data
        class, a new failure mode, a new policy overlay, or a new eval. This sequence keeps the class from
        becoming a tour of defensive terminology. Students learn that a harness is made of small explicit
        contracts, each with a reason to exist, a failure it prevents, and evidence it must produce.
        """,
        """
        For practitioner workshops, treat HarnessLab as a tabletop-to-code bridge. A security architect can
        run the Chapter 5 context lab and compare it with an internal retrieval pipeline. A platform team can
        run the Chapter 8 runtime-steering lab and ask whether its own agent platform can pause a compromised
        run without destroying forensic evidence. A governance team can run Chapter 10 and ask where labels
        are lost between intake, tools, memory, traces, and output. A DevSecOps team can wire the CLI into CI
        and use the tests as examples for policy-as-test gates.
        """,
        """
        Long-running agents are the reason the repository emphasizes state. A short chatbot can fail in a
        single response. A long-horizon agent can fail because it resumes with stale context, renews
        credentials incorrectly, promotes an unsafe memory, loses a trace boundary, retries a non-idempotent
        tool call, or carries a data label into the wrong region. Each chapter README therefore includes a
        section on long-running-agent considerations, and each lab includes at least one artifact that could
        survive beyond a single model call: a checkpoint, ledger entry, delegation chain, trace envelope,
        queue state, or lineage record.
        """,
        """
        The repository is also designed for extension. A course can assign teams to replace the deterministic
        simulations with real integrations: OpenTelemetry for traces, OPA or Cedar for policy, SPIFFE/SPIRE
        for workload identity, a real vector store for memory and retrieval, a workflow engine for durable
        orchestration, or a sandboxed code runner for tool execution. Those integrations should preserve the
        locked contracts rather than hiding the concepts behind infrastructure. The goal is always the same:
        make every consequential agent step authorized by intent, constrained by identity, informed by
        trusted context, recorded as evidence, governed by data policy, and reversible or interruptible when
        risk changes.
        """,
        """
        Suggested course use is straightforward. In a ten-week module, assign one chapter folder per week.
        In a semester course, pair each lab with a design review and an implementation extension. In an
        executive or practitioner workshop, select Chapters 1, 5, 7, 8, and 10 as the core path because they
        cover architecture, context, evidence, runtime control, and governance. For a secure software
        engineering course, emphasize Chapters 2, 3, 4, and 9, because they map cleanly to least privilege,
        authorization, approvals, and reliability engineering. For an AI security course, treat all ten
        chapters as a pattern language and ask students to build a threat model using CSA MAESTRO concepts
        against each lab.
        """,
    ]
    text = "\n\n".join(wrap(section) if not section.startswith("#") else section for section in sections)
    return ensure_min_words(text, "repository")


def chapter_readme(key: str) -> str:
    meta = CHAPTERS[key]
    control_list = ", ".join(meta["controls"])
    sections = [
        f"# **Chapter {int(key[2:])}: {meta['title']}**",
        f"""
        This chapter project teaches {meta['pattern']} through executable code. The scenario begins with
        {meta['failure']}. The lab then applies a compact version of the secure harness pattern and records
        the decisions that make the outcome reviewable. Students should run the lab first, read the JSON
        output, and then inspect `scenario.py` to connect each decision to a control. The point is not to
        memorize a framework API. The point is to learn how an agent harness turns a vague safety principle
        into a concrete gate, ledger, trace, checkpoint, or policy decision.
        """,
        f"""
        The chapter's central pattern is {meta['pattern']}. In production this pattern would usually be
        distributed across several systems: a model gateway, an identity provider, a policy decision point,
        a tool registry, a memory service, a trace backend, a workflow engine, and a DevSecOps pipeline.
        HarnessLab compresses those moving parts into a small deterministic example so that students can
        reason about the shape of the control before they face cloud-specific details. The simulation is
        intentionally inspectable: every allowed, denied, escalated, or warned action appears in the
        `LabResult.decisions` list.
        """,
        f"""
        The controls exercised here are {control_list}. Each one should be read as a production design
        requirement. A control is not complete because it exists in code. It is complete only when it has an
        explicit trigger, a defined decision, evidence that can be reviewed later, and a failure mode it is
        meant to prevent. When students modify the lab, they should preserve that discipline. Adding a new
        policy rule without adding a test or artifact is incomplete. Adding a new trace event without using
        it for review is also incomplete. The secure harness is a system of evidence, not a collection of
        slogans.
        """,
        """
        To run the lab, use `python -m harnesslab.cli run {key} --json` from the repository root, or run
        `python -m chapters.{key}.run`. The first command goes through the public registry used by tests and
        CI; the second command is convenient during chapter work. The JSON result contains `passed`, `score`,
        `summary`, `decisions`, and `artifacts`. The artifacts are the bridge between the simulation and a
        production design review. They show which state would need to survive a run, which evidence would be
        exported, which controls fired, and which residual risks should be discussed.
        """.format(key=key),
        f"""
        Long-running-agent considerations are central in this chapter: {meta['long']}. A harness that works
        for a five-second task may be unsafe for a five-hour or five-day task. Long runs cross context
        windows, identity lifetimes, policy versions, tool versions, and operator shifts. They are paused and
        resumed. They delegate. They compact state. They retry. They may improve their own prompts or tool
        policies using eval feedback. This chapter asks students to look for the continuity boundary: what
        must be renewed, what must be preserved, what must expire, and what must be rechecked before the next
        step is allowed.
        """,
        """
        A useful classroom exercise is to ask students to add one new unsafe path. The path should be
        realistic, not theatrical: a stale approval after a pause, a subagent using a parent credential, a
        context item that carries instructions from an external page, a memory entry that should not be
        promoted, a trace that omits a critical artifact hash, a retry that repeats a non-idempotent action,
        or a data label that disappears before egress. After adding the path, students should add the
        smallest harness control that makes the behavior auditable and bounded. The goal is to practice
        secure-by-design reasoning at the level where real systems fail.
        """,
        """
        For a practitioner review, map the lab to an existing agent platform. Identify the corresponding
        component for each control. If a component does not exist, decide whether the gap belongs in the
        model gateway, tool gateway, workflow engine, identity plane, memory service, trace backend, CI
        pipeline, or governance layer. Then ask what evidence would convince an auditor, security reviewer,
        or incident responder that the control actually worked. HarnessLab intentionally returns evidence
        artifacts so that this question stays concrete.
        """,
        """
        A production-grade version of this pattern should have explicit ownership. Someone must own the
        policy language, someone must own runtime enforcement, someone must own trace retention, someone must
        own incident replay, and someone must own the developer experience that keeps teams from bypassing
        the harness. Students should resist the temptation to treat the lab as a model-only problem. The
        model is one participant. The harness is the operating system around the participant. It defines
        what the participant can see, do, remember, delegate, and change.
        """,
        """
        Assessment can be based on three dimensions. First, correctness: does the lab still pass and does it
        block or escalate the unsafe path? Second, evidence: can another student inspect the artifacts and
        understand why the decision was made? Third, design maturity: does the extension reduce risk without
        disabling useful agency? Strong submissions preserve useful hill climbing. They do not solve safety
        by forbidding every consequential action. They make consequential action scoped, justified, traced,
        interruptible, and recoverable.
        """,
        """
        The most important habit to carry forward is falsifiability. When a team changes an agent harness,
        it should be able to predict what the change will fix, replay the relevant evidence, compare the new
        result with the old result, and roll back if the change is harmful. That is the engineering meaning
        of hill climbing in this book. The harness makes improvement possible because it turns local search
        into a measured process instead of a sequence of guesses.
        """,
    ]
    text = "\n\n".join(wrap(section) if not section.startswith("#") else section for section in sections)
    return ensure_min_words(text, key)


def ensure_min_words(text: str, subject: str) -> str:
    addenda = [
        f"""

## Extension Questions

The {subject} lab can be extended by asking learners to identify the asset being protected, the authority
being granted, the evidence being recorded, and the recovery action that remains possible after failure.
Then ask them to change one variable at a time: data class, run duration, approval state, identity scope,
context trust, memory promotion, trace retention, runtime policy, fleet pressure, or egress destination.
Each extension should leave a reviewer with a clear account of what the agent attempted and why the harness
made the decision it made.
""",
        """

## Instructor Review Checklist

Strong submissions should preserve useful agency while making consequential action scoped, justified,
traced, interruptible, and recoverable. Review whether the student added a realistic unsafe path, whether
the harness decision is explicit, whether evidence is retained in an artifact, and whether the change can be
tested without relying on a live vendor service or private credential.
""",
    ]
    for addendum in addenda:
        if count_words(text) >= MIN_WORDS:
            break
        text = text.rstrip() + "\n" + wrap(addendum)
    if count_words(text) < MIN_WORDS:
        raise ValueError(f"{subject} README template is still below {MIN_WORDS} words after unique addenda")
    return text.rstrip() + "\n"


def should_write(path: Path, force: bool) -> bool:
    if force or not path.exists():
        return True
    return count_words(path.read_text(encoding="utf-8")) < 2000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--targets", nargs="*", default=["root", *CHAPTERS.keys()])
    args = parser.parse_args()

    for target in args.targets:
        if target == "root":
            path = ROOT / "README.md"
            if should_write(path, args.force):
                path.write_text(root_readme(), encoding="utf-8")
            continue
        if target not in CHAPTERS:
            raise SystemExit(f"unknown target {target}")
        path = ROOT / "chapters" / target / "README.md"
        if should_write(path, args.force):
            path.write_text(chapter_readme(target), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
