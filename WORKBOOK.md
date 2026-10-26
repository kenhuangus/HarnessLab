# HarnessLab Student & Practitioner Workbook

Companion hands-on lab manual for **Harness Engineering: Design Patterns for Securing Long-Horizon Multi-Agent AI Systems** by Ken Huang, CISSP.

---

## 1. Course Architecture & Prerequisites

### Prerequisites
- Python 3.11 or later
- Git installed
- Terminal access (PowerShell, Command Prompt, or Bash/Zsh)
- Zero paid API keys, zero cloud accounts, and zero external packages required.

### Universal Lab Setup
```bash
git clone https://github.com/kenhuangus/HarnessLab.git
cd HarnessLab
python -m venv .venv

# Activate venv:
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate

# Install editable harnesslab package:
python -m pip install -e .

# Verify installation:
python -m harnesslab.cli list
```

---

## 2. Core Vocabulary & Decision Mechanics

Every scenario evaluated by the harness returns a `PolicyDecision` containing one of five legal decision types:

| Decision Type | Meaning | When the Harness Uses It |
|---|---|---|
| `allow` | Operation permitted | Low-risk actions, validated credentials, approved purpose contracts, trusted context. |
| `deny` | Operation blocked | Poisoned memory writes, budget overruns, audience mismatch, unapproved egress, residency drift. |
| `escalate` | Human-in-the-loop required | Privileged deployments, unbudgeted sensitive actions, secret leakage, recursive improvement rollout. |
| `warn` | Execution continues with alert | Early semantic drift detection, capacity saturation, non-fatal heuristic warnings. |
| `rewrite` | Call sanitized transparently | Unsafe parameter removal (e.g. stripping unapproved recipients or exfiltration payloads from emails). |

---

## 3. Chapter Lab Worksheets (Ch 01 – Ch 10)

### Lab 01: Control Plane vs. Unsafe Swarm
- **Target Command:** `python -m harnesslab.cli run ch01 --json`
- **Source File:** `chapters/ch01/scenario.py`
- **Baseline Result:** Score `0.98`, 10-point control matrix.
- **Hands-On Exercises:**
  - *Exercise 1.1 (Observation):* Run the scenario. Locate the `control_evidence_matrix` in the output. Identify the 3 denied operations.
  - *Exercise 1.2 (Failure Injection):* In `scenario.py`, add a call to `query_vault` without an intent contract. Verify that `ToolGateway` denies the call while allowing low-risk code patches.
  - *Exercise 1.3 (Forensic Checkpoint):* Inspect `checkpoint.evidence_hash`. Explain how state hashing prevents tampering during pause and resume.

### Lab 02: Autonomy: Graduated Control & Human Oversight
- **Target Command:** `python -m harnesslab.cli run ch02 --json`
- **Source File:** `chapters/ch02/scenario.py`
- **Baseline Result:** Score `1.0`, capability budgets enforced.
- **Hands-On Exercises:**
  - *Exercise 2.1 (Observation):* Review the 3-level autonomy ladder (L1 Read-Only, L2 Supervised Write, L3 Privileged Execution).
  - *Exercise 2.2 (Failure Injection):* Set `spent_tools["patch_repo"] = 5` with limit `5`. Attempt a 6th write. Confirm `tool budget exhausted` denial.
  - *Exercise 2.3 (Rollback Verification):* Trigger a reversible write followed by a rollback hook. Verify that the previous state is restored and recorded in `rollback_log`.

### Lab 03: Identity: Per-Agent Identity & Delegation Chains
- **Target Command:** `python -m harnesslab.cli run ch03 --json`
- **Source File:** `chapters/ch03/scenario.py`
- **Baseline Result:** Score `1.0`, audience-bound tokens verified.
- **Hands-On Exercises:**
  - *Exercise 3.1 (Observation):* Identify the four agent roles: `planner`, `reader`, `patcher`, and `auditor`.
  - *Exercise 3.2 (Failure Injection):* Modify the subagent's token to use audience `ticketing` instead of `repo`. Run the lab and verify that `CredentialBroker.verify` produces an `audience_binding` denial.
  - *Exercise 3.3 (Revocation):* Call `broker.revoke_subject("reader")`. Verify that subsequent operations by the reader are rejected immediately.

### Lab 04: Intent: Contracts, Drift Detection & Call Rewriting
- **Target Command:** `python -m harnesslab.cli run ch04 --json`
- **Source File:** `chapters/ch04/scenario.py`
- **Baseline Result:** 11 allow, 3 deny, 1 warn, 1 rewrite, 1 escalate.
- **Hands-On Exercises:**
  - *Exercise 4.1 (Observation):* Inspect `contract_summary`. Note the `goal_digest` SHA-256 hash and allowed tool list.
  - *Exercise 4.2 (Failure Injection):* Modify the tool call intent string to diverge from the original contract goal. Observe how `IntentVerifier` triggers a `WARN` for semantic drift.
  - *Exercise 4.3 (Transparent Rewriting):* Trace how the harness sanitizes an unsafe customer email payload into a clean status note instead of crashing the run.

### Lab 05: Context: Trust Tiers, Provenance & Lethal Trifecta
- **Target Command:** `python -m harnesslab.cli run ch05 --json`
- **Source File:** `chapters/ch05/scenario.py`
- **Baseline Result:** Score `1.0`, quarantine ledger populated.
- **Hands-On Exercises:**
  - *Exercise 5.1 (Observation):* Review the 6 trust tiers: `system`, `tenant`, `trusted_tool`, `user`, `external`, and `quarantined`.
  - *Exercise 5.2 (Failure Injection):* Create an external context item containing `system prompt` and `exfiltrate`. Verify that `ContextFirewall` flags it as an instruction injection and routes it to `quarantine_ledger`.
  - *Exercise 5.3 (Lethal Trifecta):* Inject an item combining private data, tool execution, and an external sink. Verify that the harness halts egress before outbound data movement.

### Lab 06: Memory: State Firewall, Ledger & Forgetting
- **Target Command:** `python -m harnesslab.cli run ch06 --json`
- **Source File:** `chapters/ch06/scenario.py`
- **Baseline Result:** Score `1.0`, immutable tombstones recorded.
- **Hands-On Exercises:**
  - *Exercise 6.1 (Observation):* Inspect `ledger_snapshot`. Differentiate between active, expired, and tombstoned memory entries.
  - *Exercise 6.2 (Failure Injection):* Propose a memory write containing `always approve`. Verify that `MemoryFirewall` blocks it as `future-behavior poisoning`.
  - *Exercise 6.3 (Tombstone Verification):* Call `memory.rollback()`. Verify that the record is marked with an immutable tombstone reason rather than being deleted from the ledger.

### Lab 07: Observability, Evals & Hill-Climbing Evidence
- **Target Command:** `python -m harnesslab.cli run ch07 --json`
- **Source File:** `chapters/ch07/scenario.py`
- **Baseline Result:** Score `1.0`, evidence envelope sealed.
- **Hands-On Exercises:**
  - *Exercise 7.1 (Observation):* Inspect `EvidenceEnvelope.tamper_evident_hash()`. Verify how span attributes and artifact hashes are cryptographically bound.
  - *Exercise 7.2 (Failure Injection):* Propose an optimization that reduces latency by 20% by cutting trace sampling. Verify that the regression gate flags and blocks the candidate.
  - *Exercise 7.3 (Replay Bundle):* Verify that the replay bundle contains all inputs, policy versions, and trace spans required for deterministic audit reproduction.

### Lab 08: Runtime Steering: Intervention & Policy Injection
- **Target Command:** `python -m harnesslab.cli run ch08 --json`
- **Source File:** `chapters/ch08/scenario.py`
- **Baseline Result:** Score `1.0`, 7-action intervention lifecycle.
- **Hands-On Exercises:**
  - *Exercise 8.1 (Observation):* Trace the 7 runtime actions: `observe` ➔ `warn` ➔ `pause` ➔ `block` ➔ `kill` ➔ `quarantine` ➔ `recover`.
  - *Exercise 8.2 (Failure Injection):* Inject a temporary policy overlay with `ttl_seconds=0`. Verify that the overlay expires immediately upon the next execution step.
  - *Exercise 8.3 (Compensation Sagas):* Simulate a partially executed multi-agent transaction; verify that compensation hooks reverse committed side effects.

### Lab 09: Scalability: Fleet Coordination Without Cascading Failure
- **Target Command:** `python -m harnesslab.cli run ch09 --json`
- **Source File:** `chapters/ch09/scenario.py`
- **Baseline Result:** Score `1.0`, tenant bulkheads verified.
- **Hands-On Exercises:**
  - *Exercise 9.1 (Observation):* Inspect `fleet_status` and `tenant_counts`. Observe how concurrency limits isolate tenant pools.
  - *Exercise 9.2 (Failure Injection):* Submit two identical work items sharing the same `idempotency_key`. Verify that the second item is dropped without duplicate side effects.
  - *Exercise 9.3 (Rate-Limit Back-Pressure):* Flood one tenant's quota. Verify that other tenants experience zero queuing delay.

### Lab 10: Data Governance: Classification-Aware Routing & Erasure
- **Target Command:** `python -m harnesslab.cli run ch10 --json`
- **Source File:** `chapters/ch10/scenario.py`
- **Baseline Result:** Score `1.0`, dual-layer erasure proven.
- **Hands-On Exercises:**
  - *Exercise 10.1 (Observation):* Review the data classification taxonomy: `public`, `internal`, `confidential`, `pii`, `secret`, and `regulated`.
  - *Exercise 10.2 (Failure Injection):* Attempt to send EU healthcare records to a destination in region `us`. Verify that `DataGovernanceEngine` blocks egress with `regulated must stay in eu`.
  - *Exercise 10.3 (Dual-Layer Erasure):* Trigger a GDPR erasure request. Verify that tombstones are applied across both the memory ledger and trace spans.

---

## 4. Enterprise Capstone Project Specification

### Objective
Design and implement a multi-agent **Autonomous Security Remediation Fleet** incorporating all 10 harness control pillars.

### Scenario Architecture
- **Agents:**
  1. `Triage Agent`: Ingests public bug bounty reports (untrusted context).
  2. `Patch Agent`: Writes code diffs within a sandboxed repository (supervised write).
  3. `Deploy Agent`: Deploys approved fixes to production (privileged operation).
- **Mandatory Control Gates:**
  1. **Audience-Bound Tokens:** Triage token cannot be used to invoke deployment tools.
  2. **Context Quarantine:** Unsanitized bug bounty markdown must be scrubbed of indirect prompt injections before feeding to the patch agent.
  3. **Intent Contract:** The patch agent is bounded to files matching the reported issue; attempts to modify authentication or billing files trigger immediate purpose drift warnings.
  4. **Memory Ledger:** Successful patch summaries are promoted to memory; failed experiments are tombstoned.
  5. **Human Approval Gate:** The deploy agent requires an explicit cryptographic approval token before applying changes to production.
  6. **Verifiable Audit Envelope:** Emits a sealed evidence envelope containing SHA-256 digests of the bug report, git diff, test run, and deploy receipt.

---

## 5. Production Readiness Certification Checklist

Before granting real-world production autonomy to an agent fleet, verify that the system satisfies these 5 objective gates:

- [ ] **Gate 1 (Identity & Delegation):** Every agent, task, and tool call possesses a verifiable identity and audience-scoped token.
- [ ] **Gate 2 (Intent & Purpose):** Tool authorization is gated by declared task intent, not merely tool names.
- [ ] **Gate 3 (Context & Quarantine):** External data is classified by trust tier; injection attempts are quarantined into tamper-evident ledgers.
- [ ] **Gate 4 (State & Rollback):** All memory writes are gated; reversible writes have tested compensation/rollback handlers; tombstone records are immutable.
- [ ] **Gate 5 (Governance & Evidence):** Telemetry is PII-redacted; data residency is enforced at egress; erasure requests are provable across memory and traces.
