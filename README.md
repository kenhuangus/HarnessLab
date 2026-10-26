# **HarnessLab**

> 🌐 **Interactive Course Slide Deck (GitHub Pages):**  
> **[https://kenhuangus.github.io/harness-engineering-tutorial-slides/](https://kenhuangus.github.io/harness-engineering-tutorial-slides/)**

HarnessLab is the public companion lab repository for **Harness Engineering: Design Patterns for Securing Long-Horizon Multi-Agent AI Systems** by Ken Huang.

The book argues that the decisive artifact in production agentic AI is not a clever prompt, a single model, or a single guardrail. The decisive artifact is the harness: the control plane that mediates what agents may know, remember, decide, delegate, execute, observe, resume, and improve. This repository turns that argument into runnable code. Each chapter has an executable scenario, a teaching README, and a deterministic result object that records what the harness allowed, blocked, escalated, or preserved as evidence.

The labs are deliberately dependency-free so that a student can run them with a normal Python installation and no cloud account, no paid model API, no live secrets, and no vendor-specific setup. That constraint is important. A production harness may integrate identity providers, model gateways, workflow engines, observability backends, vaults, DLP services, policy engines, sandboxes, CI systems, and ticketing platforms. HarnessLab keeps the first learning surface small enough to inspect while preserving the control-plane shape that those production systems need.

## Purpose

HarnessLab teaches secure harness engineering by making every control concrete. The core package models task-scoped identity, audience-bound credentials, intent contracts, context quarantine, memory ledgers, evidence envelopes, runtime checkpoints, fleet back-pressure, and data-governance routing. These are not final enterprise implementations. They are compact reference forms designed to be read in class, extended in assignments, and mapped to production platforms. The value of the repository is that students can inspect a whole harness pattern in one sitting, then ask how the same pattern would be expressed in a model gateway, policy engine, workflow engine, or platform service.

The labs also teach hill climbing as an engineering discipline. Long-horizon agents rarely move in a straight line from prompt to answer. They search locally over plans, tool calls, code changes, context, memory, evidence, evaluator feedback, and recovery states. That search creates value when the harness makes it bounded, observable, reversible, and evidence-driven. The same search creates risk when authority expands silently, when low-trust context becomes durable memory, when traces are too thin to explain a decision, or when a subagent acts under another agent's broad credentials. HarnessLab makes that tension visible in code.

## Tutorial Slides & Course Material

An interactive tutorial slide presentation is available for instructors, students, and practitioners:
- **Interactive Slide Deck:** [Hands-On Harness Engineering Tutorial Slides](https://kenhuangus.github.io/harness-engineering-tutorial-slides/)
- **Slide Deck Source Repository:** [github.com/kenhuangus/harness-engineering-tutorial-slides](https://github.com/kenhuangus/harness-engineering-tutorial-slides)
- **Book Reference:** [Harness Engineering (Kindle)](https://www.amazon.com/dp/B0HF3F86YM)

## Quick Start

Use Python 3.11 or later.

```bash
git clone https://github.com/kenhuangus/HarnessLab.git
cd HarnessLab
python -m pip install -e .
python -m harnesslab.cli list
python -m harnesslab.cli run ch07 --json
python -m harnesslab.cli run all
```

The installed console command is also available:

```bash
harnesslab list
harnesslab run all
```

Every chapter runner returns a `LabResult` with `chapter`, `title`, `passed`, `score`, `summary`, `decisions`, and `artifacts`. The decisions are the teaching surface. They show where the harness allowed low-risk work, denied an unsafe route, escalated an action for human approval, warned about drift, quarantined hostile context, or preserved evidence for replay. The artifacts show the state that would matter in production: a delegation chain, checkpoint, memory ledger entry, trace envelope, queue state, lineage record, or compliance hash.

Each chapter also stores an actual captured run under `chapters/chXX/LabResult/`. Those folders contain the parsed `result.json`, raw `stdout.txt`, raw `stderr.txt`, and a short README so instructors can compare expected evidence with a fresh local run. Each captured `LabResult/` folder is committed with the chapter so instructors can compare expected evidence with a fresh local run.

## Chapter Map

Titles match the published Kindle edition.

Chapter 1, **Harness as the Control Plane for Long-Horizon Multi-Agent Systems**, introduces the secure harness as the reference architecture for controlled agentic search. The lab starts with an unsafe shared-tool swarm and maps it to a control and evidence matrix.

Chapter 2, **Autonomy: Graduated Control and Human Oversight**, treats autonomy as a ladder instead of a switch. The lab demonstrates capability budgets, approval queues, non-waivable controls, authority expiry, renewal, and rollback hooks.

Chapter 3, **Identity: Per-Agent Identity and Delegation Chains**, replaces shared tokens with accountable agent, task, workload, tool, and resource identities. The lab exercises audience-bound credentials, revocation, pause/resume rotation, and least-privilege scope checks.

Chapter 4, **Intent: Contracts, Drift Detection, and Authorization by Purpose**, treats declared purpose as an authorization boundary. The lab checks tool scope, data scope, risk, evidence, stale goals, safe rewriting, and purpose-bound reauthorization.

Chapter 5, **Context: Trust Tiers, Provenance, and Context-Poisoning Containment**, treats context as both information and authority. The lab releases only trusted and fresh context, quarantines external instructions, blocks lethal-trifecta egress, and preserves quarantine evidence.

Chapter 6, **Memory: State Firewall, Ledger, and Forgetting**, treats memory as future behavior. The lab gates memory writes, records state in a ledger, promotes safe handoffs, isolates tenants, expires records, and tombstones poisoned memory.

Chapter 7, **Observability, Evals, and Hill-Climbing Evidence**, turns traces into the evidentiary layer for improvement. The lab emits redacted spans, hashes artifacts, builds replay bundles, detects benchmark regression, and governs recursive improvement.

Chapter 8, **Runtime Steering: Intervention, Policy Injection, and Safe Rollback**, shows how to steer a run after execution begins. The lab observes, warns, pauses, blocks, kills, quarantines, recovers, replays, compensates, and expires bounded policy overlays.

Chapter 9, **Scalability: Fleet Coordination Without Cascading Failure**, moves from a single run to a fleet. The lab covers tenant bulkheads, global queues, quota escalation, rate-limit back-pressure, idempotent retries, compromised-worker quarantine, and capacity epochs.

Chapter 10, **Data Governance: Classification-Aware Tools, Egress, and Compliance**, makes data governance a runtime property of the harness. The lab routes labeled data through approved profiles, blocks unsafe egress and residency drift, escalates secret leakage, persists labels across resume, and proves erasure across memory plus trace evidence.

## Teaching Method

The preferred teaching sequence is run, inspect, extend, and review. First, run a chapter and read the JSON output without looking at the implementation. Ask students to identify which decision represents the unsafe path and which artifact would matter to an auditor or incident responder. Second, inspect `scenario.py` and locate the harness control that changed the outcome. Third, extend the scenario with one realistic failure: stale approval after a pause, subagent use of a parent credential, external context that carries instructions, memory promotion from an untrusted source, a trace that omits an artifact hash, a retry that repeats a non-idempotent action, or a data label that disappears before egress. Fourth, review whether the new control preserves useful agency while making the run bounded, justified, traced, interruptible, and recoverable.

This sequence keeps the material from becoming a vocabulary tour. Students should not leave with a list of terms; they should leave with the habit of asking what authority is being granted, what purpose justifies it, what context informed it, what state will outlive it, what evidence explains it, and what recovery path remains. That habit is the core of secure harness engineering.

## Practitioner Use

For practitioner workshops, treat HarnessLab as a tabletop-to-code bridge. A security architect can run the Chapter 5 context lab and compare it with an internal retrieval pipeline. A platform team can run the Chapter 8 runtime-steering lab and ask whether its own agent platform can pause a compromised run without destroying forensic evidence. A governance team can run Chapter 10 and ask where labels are lost between intake, tools, memory, traces, and output. A DevSecOps team can wire the CLI into CI and use the tests as examples for policy-as-test gates.

The repository is also useful for design reviews. Pick one chapter, run the lab, and map every decision to an internal system. If the internal platform lacks a corresponding component, decide whether the gap belongs in the model gateway, tool gateway, workflow engine, identity plane, memory service, trace backend, CI pipeline, or governance layer. Then ask what evidence would convince a reviewer that the control worked. The goal is not to copy the toy implementation. The goal is to identify the production boundary that needs an explicit contract.

## Enterprise Platform Mapping

HarnessLab uses dependency-free standard library primitives to ensure universal accessibility in educational settings. When implementing these patterns in production enterprise environments, map each lab control to enterprise infrastructure:

| HarnessLab Primitive | Control Plane Responsibility | Enterprise Production Analogues |
|---|---|---|
| `CredentialBroker` | Task-scoped identity, audience-bound tokens, and parent-child delegation chains | SPIFFE/SPIRE workload identities, OAuth2 audience tokens, AWS IAM Roles Anywhere, HashiCorp Vault agent tokens |
| `CapabilityBudget` | Graduated autonomy ceilings, token spend limits, and non-waivable operational controls | API Gateway rate limiters, Envoy token buckets, AWS Bedrock service quotas, FinOps spend alert policies |
| `IntentContract` | Purpose-bound authorization, semantic drift detection, and transparent call rewriting | OPA/Rego purpose policies, Cedar authorization rules, Langfuse prompt version contracts, API gateway query sanitizers |
| `ContextFirewall` | Trust tier classification, indirect prompt injection containment, and lethal-trifecta blocks | NeMo Guardrails, AWS Bedrock Guardrails, Azure AI Content Safety, Llama Guard, Lakera Gandalf filters |
| `MemoryFirewall` | State write-gates, tenant-partitioned ledgers, TTL expiration, and tombstone forgetting | PostgreSQL Row-Level Security (RLS), Redis with TTL + immutable tombstone audit tables, Mem0 / Zep tenant partitions |
| `Tracer` & `EvidenceEnvelope` | PII span redaction, cryptographic SHA-256 evidence sealing, and replay bundles | OpenTelemetry (OTel) collectors, Jaeger trace streams, Sigstore artifact signing, Langfuse/Arize evaluation suites |
| `RuntimeController` | Real-time intervention (pause/kill), temporary policy overlays, and compensation rollback | Temporal.io workflow signals, AWS Step Functions compensation sagas, Kubernetes pod lifecycle hooks |
| `FleetCoordinator` | Tenant bulkheads, priority queues, back-pressure delays, and idempotency ledgers | RabbitMQ/Kafka partitioned queues, Redis distributed locks, Celery task de-duplication, Envoy circuit breakers |
| `DataGovernanceEngine` | Data classification routing, geographic residency enforcement, and verifiable erasure | Microsoft Purview, Immuta, Privacera, Presidio DLP proxies, AWS Macie, HashiCorp boundary egress policies |

## Student Learning Path

To obtain maximum instructional value from this course, students and practitioners should follow a four-tier learning trajectory:

1. **Foundational Execution (Run & Inspect):** Run each chapter via `python -m harnesslab.cli run chXX --json`. Inspect the returned `decisions` array. Map which decisions were allowed, which were blocked, and which required human escalation.
2. **Forensic Evidence Verification:** Open `chapters/chXX/LabResult/result.json`. Compare your fresh local run against the pre-captured baseline. Identify the exact cryptographic hash, quarantine finding, or tombstone that serves as audit evidence.
3. **Failure Injection & Edge Testing:** Modify `chapters/chXX/scenario.py` with one realistic failure scenario (for example, attempting to call an unapproved database tool in Chapter 1, exceeding token budgets in Chapter 2, forging an audience token in Chapter 3, or sending EU healthcare records to a US endpoint in Chapter 10). Re-run the CLI and verify that the harness halts or sanitizes the operation.
4. **Capstone Production Synthesis:** Synthesize all ten control patterns into a production multi-agent specification for your own organization. Identify where your current architecture relies solely on prompt compliance rather than deterministic control plane boundaries.

## Student and Instructor Course Resources

The repository includes a comprehensive curriculum suite to support individual self-study, corporate engineering bootcamps, and university graduate seminars:

- **Master Syllabus (`SYLLABUS.md`):** Complete course curriculum with three delivery tracks (4-Hour Executive Briefing, 2-Day Engineering Bootcamp, 4-Week University Seminar), learning outcomes, Socratic discussion prompts, and the 5-step teaching protocol.
- **Practitioner Lab Workbook (`WORKBOOK.md`):** Detailed laboratory worksheets for all 10 chapters, covering observation exercises, failure-injection experiments, forensic checkpoint analysis, and the 5-Gate Production Readiness Certification checklist.
- **Quick Reference Manual (`QUICK_REFERENCE.md`):** One-page desk reference covering the 5 policy decisions, trust tiers, data classifications, action risks, the 7-step runtime steering lifecycle, and CLI cheatsheet.
- **Automated Verification CLI (`harnesslab verify`):** Built-in CLI diagnostic command (`python -m harnesslab.cli verify`) that tests local runtime environment, executes all 10 chapter scenarios, validates 5 core safety invariants, evaluates the capstone fleet, and outputs a tamper-evident SHA-256 completion certificate.
- **Architecture Decision Records (`adr/`):** Enterprise ADR template (`adr/TEMPLATE.md`) and a canonical worked example (`adr/ADR-001-deterministic-control-plane.md`) explaining why deterministic code gateways are chosen over probabilistic prompt judges.
- **Enterprise Capstone Starter (`capstone/`):** Fully runnable multi-agent Autonomous Security Remediation Fleet (`python -m harnesslab.cli capstone`) and automated test suite (`capstone/test_capstone.py`) demonstrating Triage, Patch, and Deploy agents satisfying all 5 production gates.


## Long-Running Agents

Long-running agents are the reason this repository emphasizes state. A short chatbot can fail in a single response. A long-horizon agent can fail because it resumes with stale context, renews credentials incorrectly, promotes unsafe memory, loses a trace boundary, retries a non-idempotent action, or carries a data label into the wrong region. Each chapter therefore includes a long-running-agent angle, and each lab includes at least one artifact that could survive beyond a single model call: a checkpoint, ledger entry, delegation chain, trace envelope, queue state, policy overlay, or lineage record.

When extending the labs, pay attention to what happens at pause and resume. Credentials may need rotation. Intent may need renewal. Context may need freshness checks. Memory may need promotion gates. Traces may need continuity. Runtime policy overlays may need expiry. Fleet queues may need idempotency. Data labels may need to persist across summaries, memory, traces, and outputs. These are the places where long-running systems quietly become unsafe even when every individual tool call looks reasonable.

## Quality Gates

The repository includes tests and a QA script because the labs are part of a book project, not disposable demos. `python -m unittest discover -s tests` verifies the core controls and registered lab execution. `python -m unittest discover -s tests` verifies the core controls and registered lab execution. GitHub Actions runs unit tests and executes every chapter lab across supported Python versions.

The quality bar is intentionally practical. A chapter is not complete because it prints JSON. It must show a success path and a bounded unsafe path. It must return deterministic artifacts. It must be readable without external services. It must teach the chapter's pattern rather than merely naming it. It must avoid repeated filler text, because repeated filler hides weak thinking and makes the course material harder to trust.

## Repository Structure

The repository has three layers. The first layer is `harnesslab/`, which contains the reusable control-plane primitives. `core.py` defines the security and governance vocabulary used across the labs: identities, task credentials, tool calls, policy decisions, intent contracts, context items, memory records, trace spans, evidence envelopes, checkpoints, runtime control, fleet coordination, and data-governance routing. `labs.py` is the registry that binds the public chapter keys to their scenario modules. `cli.py` is the thin command-line surface used by students and CI. This separation matters because students can see which ideas are shared harness infrastructure and which ideas belong to a specific chapter.

The second layer is `chapters/`. Each chapter folder contains its own `scenario.py`, `run.py`, README, and `LabResult/` folder. The scenario implements the chapter's executable teaching case. The runner keeps the direct module command simple. The README explains the security pattern, the failure mode, the long-running-agent concern, and the interpretation of the returned evidence. The `LabResult/` folder preserves a real run as JSON plus raw command output. Chapter folders should remain independent teaching modules; a student should be able to study Chapter 4 intent contracts without needing to understand every detail of Chapter 9 fleet coordination.

The third layer is the quality and release layer. `tests/` verifies the core contract and confirms that every registered lab runs. `.github/workflows/ci.yml` runs unit tests and executes every chapter lab across supported Python versions. `CONTRACTS.md` records the interface rules that chapter implementations must preserve. `SECURITY.md` clarifies that the project contains simulated unsafe paths for teaching, while still treating framework bugs, misleading controls, or accidental leakage as real security issues.
