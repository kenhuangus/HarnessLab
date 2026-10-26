# Architecture Decision Record (ADR) Template: Agent Harness Systems

**Title:** [ADR-XXXX: Descriptive Title of Decision]  
**Status:** [Proposed | Accepted | Superseded | Deprecated]  
**Author:** [Engineer / Student Name]  
**Date:** [YYYY-MM-DD]  
**Target Chapter / Harness Subsystem:** [e.g., Ch 02 Autonomy, Ch 05 Context, Ch 06 Memory]

---

## 1. Context & Problem Statement
*Describe the technical context, the multi-agent failure mode, and the risk. What specific threat or failure occurs if this decision is not implemented?*

- **Agent Workflow:**
- **Failure Mode / Attack Vector:**
- **Business / Operational Impact:**

---

## 2. Decision Drivers
*What constraints and requirements govern this architecture?*
- Requirement 1 (e.g., Latency overhead < 5ms per tool call)
- Requirement 2 (e.g., Non-bypassable by model prompt injection)
- Requirement 3 (e.g., Complete auditability under regulatory scrutiny)

---

## 3. Considered Architectural Options
*Compare at least two competing approaches.*

### Option A: [e.g., LLM-Based Prompt Judge / System Prompt Directive]
- **Description:**
- **Pros:** Easy to modify; natural language understanding.
- **Cons:** Probabilistic; vulnerable to jailbreaks; high latency and token cost; non-deterministic.

### Option B: [e.g., Deterministic Code Gateway / Policy-as-Code Engine] (Chosen)
- **Description:**
- **Pros:** Deterministic execution; sub-millisecond evaluation; mathematically verifiable boundary; non-bypassable.
- **Cons:** Requires explicit schema definition and tool specification.

---

## 4. Decision Outcome
*State the chosen option clearly and specify the invariants it enforces.*

- **Chosen Architecture:**
- **Invariants Enforced:**
  1. *Invariant 1:*
  2. *Invariant 2:*

---

## 5. Enterprise Implementation & Platform Mapping
*How does this pattern translate to production enterprise infrastructure?*
- **Laboratory Primitive:** [e.g., Python `PolicyGateway` or `ContextFirewall`]
- **Enterprise Equivalent:** [e.g., Open Policy Agent (OPA), AWS Bedrock Guardrails, Envoy Filter]
- **Operational Rollout:**

---

## 6. Verification & Test Evidence
*What tests prove this invariant cannot be violated?*
- **Test Command:** `python -m harnesslab.cli verify --ch [chapter]`
- **Expected Outcome:** Policy denial or escalation recorded in evidence ledger.
