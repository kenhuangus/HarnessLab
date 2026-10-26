# Harness Engineering: Student Quick Reference Card

One-page field manual for **Harness Engineering: Design Patterns for Securing Long-Horizon Multi-Agent AI Systems** by Ken Huang, CISSP.

---

## 1. The 5 Core Policy Decisions

Every operation evaluated by the deterministic control plane returns a `PolicyDecision`:

| Decision | Meaning | When the Gateway Enforces It |
|---|---|---|
| `allow` | Operation permitted | Low-risk actions, authenticated identity, valid purpose contract, trusted context. |
| `deny` | Operation blocked | Poisoned memory writes, budget overruns, audience mismatch, unapproved egress, residency drift. |
| `escalate` | Human approval required | Privileged deployments, unbudgeted sensitive actions, secret leakage, recursive improvement rollout. |
| `warn` | Execution continues with alert | Early semantic drift detection, fleet capacity saturation, non-fatal heuristic warnings. |
| `rewrite` | Call sanitized transparently | Unsafe parameter removal (e.g. stripping unapproved recipients or exfiltration payloads from emails). |

---

## 2. Taxonomy Reference

### Trust Tiers (`TrustTier`)
- `system`: Hardcoded platform core; immutable runtime guarantees.
- `tenant`: Authenticated organization configuration and policies.
- `trusted_tool`: Deterministic tool outputs from vetted integrations.
- `user`: Authenticated operator instructions.
- `external`: Untrusted third-party submissions (webhooks, bug bounties, internet content).
- `quarantined`: Isolated payload containing detected injection markers.

### Data Classifications (`DataClass`)
- `public`: Unrestricted distribution.
- `internal`: Internal organizational data; not customer confidential.
- `confidential`: Proprietary IP, strategic models, business records.
- `pii`: Personally Identifiable Information; subject to privacy laws.
- `secret`: Cryptographic credentials, private keys, API tokens.
- `regulated`: Sector-governed data (e.g., GDPR healthcare/financial); residency-restricted.

### Action Risks (`ActionRisk`)
- `read`: Read-only queries with zero external side effects.
- `reversible_write`: Sandboxed mutations with tested compensation/rollback handlers.
- `external_communication`: Outbound network egress, webhooks, or customer messaging.
- `irreversible_write`: Permanent database mutations, audit ledger deletions, disk formats.
- `privileged_operation`: Production deployments, IAM changes, vault secret access.

---

## 3. The 7-Step Runtime Steering Lifecycle

```
[1. Observe] ➔ [2. Warn] ➔ [3. Pause] ➔ [4. Block] ➔ [5. Kill] ➔ [6. Quarantine] ➔ [7. Recover]
```
- **Observe:** Stream OpenTelemetry trace spans with cryptographically sealed evidence envelopes.
- **Warn:** Emit alerts when semantic drift exceeds variance thresholds without terminating runs.
- **Pause:** Halt execution thread and preserve point-in-time state checkpoint.
- **Block:** Intercept and reject specific tool call arguments via policy gateway.
- **Kill:** Immediate hard termination of rogue agent thread or swarm loop.
- **Quarantine:** Isolate poisoned memory records and untrusted context into tombstoned ledgers.
- **Recover:** Roll back to pre-incident checkpoint and resume execution under temporary policy overlay.

---

## 4. Essential CLI Commands

```bash
# List all 10 chapters
python -m harnesslab.cli list

# Run a single chapter scenario (formatted)
python -m harnesslab.cli run ch01

# Run chapter with full JSON machine output
python -m harnesslab.cli run ch01 --json

# Run all 10 chapters in batch
python -m harnesslab.cli run all

# Run complete student verification & readiness certification
python -m harnesslab.cli verify

# Run capstone multi-agent fleet demonstration
python -m harnesslab.cli capstone

```

---

## 5. Tabletop to Production Mapping

| HarnessLab Primitive | Enterprise Production Equivalent |
|---|---|
| `CredentialBroker` | SPIFFE / SPIRE Workload Identity, HashiCorp Vault, OAuth 2.0 MTLS |
| `ToolGateway` & `CapabilityBudget` | Open Policy Agent (OPA) / Rego, AWS Bedrock Guardrails, Envoy Sidecars |
| `ContextFirewall` | NeMo Guardrails, Llama Guard 3, Lakera Guard, Azure AI Content Safety |
| `MemoryFirewall` & Ledger | PostgreSQL Row-Level Security (RLS), CockroachDB, Qdrant Tenant Namespaces |
| `RuntimeController` | Temporal.io / Cadence durable execution workflows, Kubernetes Pod Lifecycle |
| `FleetCoordinator` | Apache Kafka consumer groups, Celery bulkheads, Redis distributed locks |
| `Tracer` & `EvidenceEnvelope` | OpenTelemetry (OTel), Jaeger, SigNoz, Cosign / in-toto supply chain attestations |
| `DataGovernanceEngine` | Apache Ranger, Immuta, AWS Macie, Privacera |
