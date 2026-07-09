# HarnessLab

HarnessLab is the runnable companion project for Hill Climbing: Design Patterns for Securing
Long-Horizon Multi-Agent AI Systems. The book argues that the decisive artifact in production
agentic AI is not a clever prompt, a single model, or a single guardrail. The decisive artifact
is         the harness: the control plane that mediates what agents may know, remember, decide,
delegate,         execute, observe, resume, and improve. This repository gives instructors and
practitioners a         concrete system for teaching that idea. Every chapter has an executable
lab, a scenario that         demonstrates at least one unsafe path, and a teaching README that
explains how the pattern works.

The project is deliberately dependency-free. Students can run it with a normal Python 3.11 or
later         installation, without cloud credentials, vendor accounts, paid model APIs, or live
secrets. That         choice is pedagogical. A real enterprise harness may integrate identity
providers, model gateways,         workflow engines, observability backends, vaults, DLP
services, policy engines, sandbox providers,         CI systems, and ticketing platforms.
HarnessLab keeps the first learning surface small enough to         inspect. The concepts are
production-shaped even when the implementation is a deterministic         simulation: task-
scoped credentials, intent contracts, context quarantine, memory ledgers,         evidence
envelopes, runtime steering, fleet bulkheads, and data-governance routing.

A central theme is hill climbing. Long-horizon agents rarely move in a straight line from prompt
to         answer. They search locally over plans, tool calls, context, memory, code changes,
evaluator         feedback, traces, and recovery states. That search creates value when the
harness makes it bounded,         observable, reversible, and evidence-driven. The same search
creates risk when authority expands         silently, when memory carries poisoned instructions
forward, when traces are too thin to explain a         decision, or when a subagent acts under
another agent's broad credentials. HarnessLab lets students         run that argument rather
than only read it.

The lab is organized as ten chapter projects. Chapter 1 introduces the secure harness as a
reference         architecture and control/evidence matrix. Chapter 2 turns autonomy into a
graduated control surface.         Chapter 3 replaces shared credentials with accountable per-
agent and per-task identity. Chapter 4         treats intent as an authorization boundary.
Chapter 5 treats context as information-flow and         authority engineering. Chapter 6 treats
memory as future behavior that needs a state firewall.         Chapter 7 turns observability
into the evidentiary layer for evals and governed recursive         improvement. Chapter 8 shows
how to steer a run after it begins. Chapter 9 scales the harness to         fleets without
cascading failure. Chapter 10 routes data according to classification, egress,
residency, lineage, and compliance evidence.

Run the full suite with `python -m unittest discover -s tests`, run the CLI with `python -m
harnesslab.cli list`, and run one chapter with `python -m harnesslab.cli run ch07 --json`. The
command `python scripts/qa.py` runs the tests and checks that every README is long enough to
support         teaching. Instructors can use the JSON output as an autograding surface, because
every lab returns a         `LabResult` containing a pass flag, score, policy decisions, and
artifacts. Practitioners can use         the same output as a pattern checklist for internal
workshops.

The code is intentionally small but it is not casual. The core package models a credential
broker         with audience-bound tokens and revocation, an intent verifier with purpose-bound
checks, a context         firewall with injection and lethal-trifecta detection, a memory
firewall with ledger and tombstones,         a tracer with tamper-evident evidence envelopes, a
runtime controller with checkpoints and policy         overlays, a fleet coordinator with quotas
and back-pressure, and a data-governance engine with         egress, residency, DLP escalation,
and lineage. These are not final enterprise implementations.         They are compact reference
forms designed to be read in class, extended in assignments, and mapped         to production
systems.

For teaching, begin each chapter by running the lab once and asking students to identify which
decision represents the unsafe path. Then inspect the scenario code and locate the control that
changed the outcome. After that, ask students to extend the scenario: add a new tool, a new data
class, a new failure mode, a new policy overlay, or a new eval. This sequence keeps the class
from         becoming a tour of defensive terminology. Students learn that a harness is made of
small explicit         contracts, each with a reason to exist, a failure it prevents, and
evidence it must produce.

For practitioner workshops, treat HarnessLab as a tabletop-to-code bridge. A security architect
can         run the Chapter 5 context lab and compare it with an internal retrieval pipeline. A
platform team can         run the Chapter 8 runtime-steering lab and ask whether its own agent
platform can pause a compromised         run without destroying forensic evidence. A governance
team can run Chapter 10 and ask where labels         are lost between intake, tools, memory,
traces, and output. A DevSecOps team can wire the CLI into CI         and use the tests as
examples for policy-as-test gates.

Long-running agents are the reason the repository emphasizes state. A short chatbot can fail in
a         single response. A long-horizon agent can fail because it resumes with stale context,
renews         credentials incorrectly, promotes an unsafe memory, loses a trace boundary,
retries a non-idempotent         tool call, or carries a data label into the wrong region. Each
chapter README therefore includes a         section on long-running-agent considerations, and
each lab includes at least one artifact that could         survive beyond a single model call: a
checkpoint, ledger entry, delegation chain, trace envelope,         queue state, or lineage
record.

The repository is also designed for extension. A course can assign teams to replace the
deterministic         simulations with real integrations: OpenTelemetry for traces, OPA or Cedar
for policy, SPIFFE/SPIRE         for workload identity, a real vector store for memory and
retrieval, a workflow engine for durable         orchestration, or a sandboxed code runner for
tool execution. Those integrations should preserve the         locked contracts rather than
hiding the concepts behind infrastructure. The goal is always the same:         make every
consequential agent step authorized by intent, constrained by identity, informed by
trusted context, recorded as evidence, governed by data policy, and reversible or interruptible
when         risk changes.

Suggested course use is straightforward. In a ten-week module, assign one chapter folder per
week.         In a semester course, pair each lab with a design review and an implementation
extension. In an         executive or practitioner workshop, select Chapters 1, 5, 7, 8, and 10
as the core path because they         cover architecture, context, evidence, runtime control,
and governance. For a secure software         engineering course, emphasize Chapters 2, 3, 4,
and 9, because they map cleanly to least privilege,         authorization, approvals, and
reliability engineering. For an AI security course, treat all ten         chapters as a pattern
language and ask students to build a threat model using CSA MAESTRO concepts         against
each lab.
## Teaching Extension Notes

The repository lab can be extended in several directions. Ask learners to identify the asset
being protected, the authority being granted, the evidence being recorded, and the recovery
action that remains possible after failure. Then ask them to change one variable at a time. If
the data class changes, which tool routes should fail? If the run resumes after a pause, which
credentials, policies, context sources, and memory records must be checked again? If an
evaluator says the new harness version improved capability, what security regression would make
that improvement unacceptable? If an operator overrides a decision, what evidence should be
captured so the override remains accountable?

The answer should never be simply to trust the model or to block all action. Secure agentic
engineering is the discipline of preserving useful agency while making the search process
bounded. Each extension should leave a reviewer with a clear story: what the agent attempted,
what the harness knew, what policy applied, what decision was made, what evidence was retained,
and what recovery path remains. That story is the difference between a demo and an operational
system.
## Teaching Extension Notes

The repository lab can be extended in several directions. Ask learners to identify the asset
being protected, the authority being granted, the evidence being recorded, and the recovery
action that remains possible after failure. Then ask them to change one variable at a time. If
the data class changes, which tool routes should fail? If the run resumes after a pause, which
credentials, policies, context sources, and memory records must be checked again? If an
evaluator says the new harness version improved capability, what security regression would make
that improvement unacceptable? If an operator overrides a decision, what evidence should be
captured so the override remains accountable?

The answer should never be simply to trust the model or to block all action. Secure agentic
engineering is the discipline of preserving useful agency while making the search process
bounded. Each extension should leave a reviewer with a clear story: what the agent attempted,
what the harness knew, what policy applied, what decision was made, what evidence was retained,
and what recovery path remains. That story is the difference between a demo and an operational
system.
## Teaching Extension Notes

The repository lab can be extended in several directions. Ask learners to identify the asset
being protected, the authority being granted, the evidence being recorded, and the recovery
action that remains possible after failure. Then ask them to change one variable at a time. If
the data class changes, which tool routes should fail? If the run resumes after a pause, which
credentials, policies, context sources, and memory records must be checked again? If an
evaluator says the new harness version improved capability, what security regression would make
that improvement unacceptable? If an operator overrides a decision, what evidence should be
captured so the override remains accountable?

The answer should never be simply to trust the model or to block all action. Secure agentic
engineering is the discipline of preserving useful agency while making the search process
bounded. Each extension should leave a reviewer with a clear story: what the agent attempted,
what the harness knew, what policy applied, what decision was made, what evidence was retained,
and what recovery path remains. That story is the difference between a demo and an operational
system.
## Teaching Extension Notes

The repository lab can be extended in several directions. Ask learners to identify the asset
being protected, the authority being granted, the evidence being recorded, and the recovery
action that remains possible after failure. Then ask them to change one variable at a time. If
the data class changes, which tool routes should fail? If the run resumes after a pause, which
credentials, policies, context sources, and memory records must be checked again? If an
evaluator says the new harness version improved capability, what security regression would make
that improvement unacceptable? If an operator overrides a decision, what evidence should be
captured so the override remains accountable?

The answer should never be simply to trust the model or to block all action. Secure agentic
engineering is the discipline of preserving useful agency while making the search process
bounded. Each extension should leave a reviewer with a clear story: what the agent attempted,
what the harness knew, what policy applied, what decision was made, what evidence was retained,
and what recovery path remains. That story is the difference between a demo and an operational
system.
## Teaching Extension Notes

The repository lab can be extended in several directions. Ask learners to identify the asset
being protected, the authority being granted, the evidence being recorded, and the recovery
action that remains possible after failure. Then ask them to change one variable at a time. If
the data class changes, which tool routes should fail? If the run resumes after a pause, which
credentials, policies, context sources, and memory records must be checked again? If an
evaluator says the new harness version improved capability, what security regression would make
that improvement unacceptable? If an operator overrides a decision, what evidence should be
captured so the override remains accountable?

The answer should never be simply to trust the model or to block all action. Secure agentic
engineering is the discipline of preserving useful agency while making the search process
bounded. Each extension should leave a reviewer with a clear story: what the agent attempted,
what the harness knew, what policy applied, what decision was made, what evidence was retained,
and what recovery path remains. That story is the difference between a demo and an operational
system.
## Teaching Extension Notes

The repository lab can be extended in several directions. Ask learners to identify the asset
being protected, the authority being granted, the evidence being recorded, and the recovery
action that remains possible after failure. Then ask them to change one variable at a time. If
the data class changes, which tool routes should fail? If the run resumes after a pause, which
credentials, policies, context sources, and memory records must be checked again? If an
evaluator says the new harness version improved capability, what security regression would make
that improvement unacceptable? If an operator overrides a decision, what evidence should be
captured so the override remains accountable?

The answer should never be simply to trust the model or to block all action. Secure agentic
engineering is the discipline of preserving useful agency while making the search process
bounded. Each extension should leave a reviewer with a clear story: what the agent attempted,
what the harness knew, what policy applied, what decision was made, what evidence was retained,
and what recovery path remains. That story is the difference between a demo and an operational
system.
