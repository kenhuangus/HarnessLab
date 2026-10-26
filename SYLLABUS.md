# Course Syllabus & Teaching Guide: Hands-On Harness Engineering

**Companion Curriculum for:** *Harness Engineering: Design Patterns for Securing Long-Horizon Multi-Agent AI Systems*  
**Instructor:** Ken Huang, CISSP (Adjunct Professor, University of San Francisco)  
**Laboratory Codebase:** [https://github.com/kenhuangus/HarnessLab](https://github.com/kenhuangus/HarnessLab)  
**Slide Deck:** [https://kenhuangus.github.io/harness-engineering-tutorial-slides](https://kenhuangus.github.io/harness-engineering-tutorial-slides)

---

## 1. Course Overview & Learning Objectives

This course teaches software engineers, security architects, and technical leaders how to design, build, and verify deterministic control planes for autonomous multi-agent AI systems.

While probabilistic foundation models generate code, reason over unstructured inputs, and plan multi-step workflows, enterprise deployments require deterministic guarantees around identity, resource budgets, state mutation, and compliance. This course establishes the engineering discipline required to run autonomous agents reliably over long execution horizons.

### Terminal Course Objectives
By completing this course and its associated laboratory exercises, students will be able to:
1. **Differentiate Control Plane vs. Model Layer:** Architect decoupled systems where non-deterministic model generation is bounded by deterministic policy gateways.
2. **Implement Audience-Bound Identity:** Issue and verify cryptographic delegation tokens that prevent privilege escalation across agent tiers.
3. **Quarantine Context Poisoning:** Build multi-tier context firewalls that isolate external, untrusted inputs and neutralize indirect prompt injections.
4. **Enforce State Firewalls & Tombstones:** Manage agent memory using immutable ledgers with cryptographic rollback and dual-layer GDPR erasure.
5. **Mitigate Fleet Cascading Failures:** Apply concurrency bulkheads, idempotency keys, and rate-limiting backpressure across multi-agent swarms.
6. **Pass Production Readiness Gates:** Audit and certify agent systems against the 5-Gate Production Readiness framework before release.

---

## 2. Flexible Course Delivery Formats

This curriculum is structured for three delivery modalities:

| Format | Target Audience | Duration | Scope |
|---|---|---|---|
| **Format A: Executive & Lead Architect Intensive** | CTOs, VP Engineering, Chief Risk/Security Officers, Principal Architects | 4 Hours (Half-Day) | Chapters 1, 3, 5, 7, 10 + Enterprise Architecture Mapping + Production Readiness Gates |
| **Format B: Engineering Bootcamp** | Platform Engineers, Backend Engineers, Applied AI Engineers | 2 Days (16 Hours) | All 10 Chapters + Hands-On Failure Injections + Capstone Fleet Project |
| **Format C: University / Graduate Seminar** | Master of Science in CS / Software Engineering / Cybersecurity Students | 4 Weeks (12 Hours) | Weekly reading, lab worksheets, Architecture Decision Record (ADR) submissions, and Capstone Defense |

---

## 3. Chapter-by-Chapter Curriculum & Lab Schedule

### Module 1: Architectural Foundations (Chapters 1–3)
- **Chapter 1: Harness as the Control Plane for Long-Horizon Multi-Agent Systems**
  - *Core Concepts:* Deterministic control plane vs. probabilistic model layer; the 5-stage long-horizon lifecycle (Admit ➔ Scope ➔ Authorize ➔ Observe ➔ Record); 10-point control evidence matrix.
  - *Hands-On Lab:* Run `python -m harnesslab.cli run ch01 --json`. Inspect denied operations and evidence hashing.
  - *Failure Injection Challenge:* Propose uncontracted vault queries and verify rejection.
- **Chapter 2: Autonomy: Graduated Control and Human Oversight**
  - *Core Concepts:* Autonomy ladders (L1 Read-Only to L3 Privileged Execution); capability budgets; execution rollbacks.
  - *Hands-On Lab:* Run `python -m harnesslab.cli run ch02 --json`. Trace capability budgets and approval requests.
  - *Failure Injection Challenge:* Exceed tool execution limits and verify deterministic budget exhaustion denials.
- **Chapter 3: Identity: Per-Agent Identity and Delegation Chains**
  - *Core Concepts:* Cryptographic delegation chains; audience-scoped credentials; short-lived tokens; immediate subject revocation.
  - *Hands-On Lab:* Run `python -m harnesslab.cli run ch03 --json`. Verify audience matching and token verification.
  - *Failure Injection Challenge:* Attempt to reuse a read-scoped token against a deployment tool and verify audience mismatch rejection.

### Module 2: Safety & State Defenses (Chapters 4–6)
- **Chapter 4: Intent: Contracts, Drift Detection, and Authorization by Purpose**
  - *Core Concepts:* Authorization by purpose vs. authorization by name; intent contracts; semantic drift detection; transparent parameter rewriting.
  - *Hands-On Lab:* Run `python -m harnesslab.cli run ch04 --json`. Observe parameter rewriting and goal hashing.
  - *Failure Injection Challenge:* Diverge tool arguments from declared contract purpose to trigger drift warnings.
- **Chapter 5: Context: Trust Tiers, Provenance, and Context-Poisoning Containment**
  - *Core Concepts:* 6-tier trust taxonomy (`system`, `tenant`, `trusted_tool`, `user`, `external`, `quarantined`); indirect prompt injection defense; the Lethal Trifecta (private data + tool execution + external sink).
  - *Hands-On Lab:* Run `python -m harnesslab.cli run ch05 --json`. Inspect quarantine ledger and egress halts.
  - *Failure Injection Challenge:* Submit untrusted web inputs containing injection patterns; confirm automatic quarantine admission.
- **Chapter 6: Memory: State Firewall, Ledger, and Forgetting**
  - *Core Concepts:* Memory poisoning defenses; immutable ledgers; point-in-time state rollback; cryptographic tombstones.
  - *Hands-On Lab:* Run `python -m harnesslab.cli run ch06 --json`. Inspect memory state snapshots and tombstones.
  - *Failure Injection Challenge:* Inject persistent behavioral directives into memory and verify memory firewall rejection.

### Module 3: Production Reliability & Operations (Chapters 7–8)
- **Chapter 7: Observability, Evals, and Hill-Climbing Evidence**
  - *Core Concepts:* OpenTelemetry spans with evidence envelopes; tamper-evident cryptographic hashes; deterministic replay bundles; regression hill-climbing gates.
  - *Hands-On Lab:* Run `python -m harnesslab.cli run ch07 --json`. Verify sealed evidence envelope SHA-256 digests.
  - *Failure Injection Challenge:* Propose candidate code optimizations that regress safety spans; confirm rejection at benchmark gate.
- **Chapter 8: Runtime Steering: Intervention, Policy Injection, and Safe Rollback**
  - *Core Concepts:* The 7-step runtime intervention lifecycle (`observe` ➔ `warn` ➔ `pause` ➔ `block` ➔ `kill` ➔ `quarantine` ➔ `recover`); temporary policy overlays; compensation sagas.
  - *Hands-On Lab:* Run `python -m harnesslab.cli run ch08 --json`. Trace dynamic policy overlay lifecycles.
  - *Failure Injection Challenge:* Inject time-to-live expired policy overlays; verify fallback to default enforcement.

### Module 4: Enterprise Scale & Governance (Chapters 9–10 + Capstone)
- **Chapter 9: Scalability: Fleet Coordination Without Cascading Failure**
  - *Core Concepts:* Tenant concurrency bulkheads; idempotency deduplication; rate-limiting backpressure; distributed deadlock prevention.
  - *Hands-On Lab:* Run `python -m harnesslab.cli run ch09 --json`. Verify tenant isolation under load.
  - *Failure Injection Challenge:* Send duplicate tasks with identical idempotency keys; verify duplicate drop without side effects.
- **Chapter 10: Data Governance: Classification-Aware Tools, Egress, and Compliance**
  - *Core Concepts:* 6-class data taxonomy; classification-aware tool routing; cross-border data residency boundaries; dual-layer GDPR erasure across memory and traces.
  - *Hands-On Lab:* Run `python -m harnesslab.cli run ch10 --json`. Trace data residency enforcement and proof of erasure.
  - *Failure Injection Challenge:* Attempt egress of regulated records across regional boundaries; verify deterministic block.
- **Enterprise Capstone Project: Autonomous Security Remediation Fleet**
  - Build, verify, and defend a 3-agent fleet (Triage, Patch, Deploy) passing all 5 Production Readiness Gates.

---

## 4. The 5-Step Teaching Protocol

Instructors should apply this structured loop for each chapter module:

```
Step 1: Execute Baseline Scenario
        └── Run scenario via CLI and confirm baseline score (Score >= 0.98).

Step 2: Inspect Forensic Artifacts
        └── Examine result.json, decisions ledger, and evidence hashes.

Step 3: Inject Adversarial Failure
        └── Modify inputs or parameters to violate a core invariant.

Step 4: Verify Deterministic Invariant
        └── Confirm the control plane rejects, quenches, or rewrites the operation.

Step 5: Map to Enterprise Production Stack
        └── Map Python laboratory primitive to SPIFFE, OPA, Kafka, OpenTelemetry, etc.
```

---

## 5. Socratic Cold-Call & Discussion Prompts

Use these targeted questions to test student comprehension during live sessions:

1. **On Control Plane Decoupling (Ch 01):** *"If an LLM has an alignment prompt telling it never to delete files, why do we still require a deterministic Policy Gateway in code?"*
   - *Expected Insight:* Prompt instructions can be bypassed via prompt injection, token manipulation, or context window overflow. The code gateway executes outside the model's context and cannot be overridden by text tokens.
2. **On Audience Binding (Ch 03):** *"Why is a valid cryptographic signature insufficient if the token audience is unrestricted?"*
   - *Expected Insight:* An agent possessing a valid token meant for a low-privilege service (e.g. read repo) could forward that token to invoke a privileged service (e.g. production deploy). Audience binding confines execution scope to the intended recipient.
3. **On Context vs. Memory (Ch 05 vs. Ch 06):** *"What is the architectural difference between a context-poisoning attack and a memory-poisoning attack?"*
   - *Expected Insight:* Context poisoning is ephemeral and attacks the current inference step; memory poisoning persists malicious directives across sessions, infecting all future tasks that read the ledger.
4. **On Observability Evidence (Ch 07):** *"Why do we hash the evidence envelope with SHA-256 instead of just storing logs in Elasticsearch?"*
   - *Expected Insight:* Log indices can be modified or truncated retroactively. A sealed evidence envelope cryptographically binds inputs, policies, spans, and artifact digests, guaranteeing non-repudiation during post-incident audits.

---

## 6. Student Grading & Certification Rubric

For accredited or certificate-granting courses, evaluation is weighted as follows:

| Component | Weight | Assessment Method |
|---|---|---|
| **1. Lab Invariant Verifications** | 30% | Automated verification via `python -m harnesslab.cli verify` (all 10 chapters passing). |
| **2. Failure Injection Exercises** | 20% | Submission of documented `WORKBOOK.md` exercises detailing how injected violations were caught. |
| **3. Architecture Decision Record (ADR)** | 20% | A formal 2-page ADR defending a security boundary choice using `adr/TEMPLATE.md`. |
| **4. Capstone Fleet Defense** | 30% | Implementation and test execution of the 3-Agent Remediation Fleet satisfying all 5 Readiness Gates. |

Students achieving ≥ 85% total score receive the **Production Harness Engineering Readiness Certificate**.
