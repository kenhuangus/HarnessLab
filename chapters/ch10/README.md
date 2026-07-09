# **Chapter 10: Data Governance: Classification-Aware Tools, Egress, and Compliance**

Chapter 10 teaches how a long-running agent harness can make data governance an executable control instead of a policy document that people hope the agent remembers. The lab focuses on a common production problem: an agent needs to work across tickets, memory, traces, model calls, tool calls, and compliance evidence, but each piece of data carries different handling requirements. Some information is public. Some is internal. Some is PII. Some is a secret. Some is regulated by geography. The agent's usefulness depends on moving the right data to the right tool at the right time, but the organization's safety depends on proving that unsafe routes were blocked, sensitive values were redacted or escalated, residency was respected, and deletion requests reached every place the data was stored.

The scenario is dependency-free and deterministic so it can run in a classroom, a workshop, or CI without cloud accounts or paid model APIs. It is not a vendor tutorial. It is a small executable model of a production design pattern. The production version might be spread across a model gateway, tool gateway, policy decision point, data loss prevention service, memory service, trace backend, workflow engine, and evidence store. HarnessLab compresses those responsibilities into one readable chapter so learners can study the control shape before mapping it to their own platform.

The public contract remains simple. `scenario.py` exposes `run()` and returns a `harnesslab.core.LabResult`. `run.py` prints that result as JSON. The important work is inside the result: a list of policy decisions and a set of artifacts that explain what happened. Students should read the JSON first, then read the code, then come back to the JSON and ask whether a reviewer could reconstruct the governance story from the evidence.

## How to Run

From the HarnessLab project root, run:

```bash
python -m chapters.ch10.run
```

The output is JSON. The main fields are:

- `passed`: whether the scenario observed the expected allow, deny, escalation, lineage, persistence, and deletion outcomes.
- `score`: a deterministic score derived from the policy decisions.
- `summary`: a short explanation of the chapter result.
- `decisions`: every meaningful allow, deny, escalation, rewrite, or warning returned by the harness.
- `artifacts`: sanitized evidence, including labels, checkpoint metadata, lineage entries, memory tombstones, trace tombstones, and a compliance evidence hash.

The chapter can also be run through the HarnessLab command-line interface when installed:

```bash
harnesslab run ch10 --json
```

The direct module command is useful while editing the chapter. The public CLI command is useful for CI or for checking that the registry path still works.

## The Production Problem

Long-running agents do not simply answer one prompt. They gather context, call tools, store memory, emit traces, delegate work, pause, resume, retry, and create evidence. Over time, the agent's state becomes a mix of user instructions, tool results, model summaries, old decisions, partial conclusions, and operational metadata. That state can become dangerous if data labels disappear.

Imagine an investigation agent reading a customer-impacting security ticket. The ticket contains an email address and incident details. The agent wants to summarize the ticket, check whether a secret rotation is needed, write useful memory, and emit compliance evidence. Each step can be reasonable in isolation. The failure appears when one step strips the data label and the next step treats the same data as ordinary internal text. Once that happens, the agent might send PII to an external model, store a secret-like payload in memory, emit a trace with raw personal data, or resume a paused task without remembering that the original context had a residency requirement.

Production governance is about maintaining those boundaries even when the workflow is long, boring, and partially automated. The harness should not rely on the model to remember policy. It should attach labels to data, route based on those labels, and record evidence when it allows or blocks an action.

## What the Scenario Demonstrates

The scenario models seven governance responsibilities.

First, it demonstrates classification-aware model and tool routing. A `DataLabel` records the data class, residency region, subject reference, policy version, and lineage parent. A `ModelProfile` records the destination, region, allowed data classes, and evidence mode for a candidate model or processing endpoint. Before a tool call is allowed to leave the harness, the chapter checks the registered tool, the persisted label, the model profile, and the data governance route. This means the model choice is not just an optimization decision. It is a policy decision.

Second, it demonstrates PII handling. The scenario starts with a ticket that includes a customer email address, but the evidence artifacts do not need to reveal the raw address. The chapter creates a deterministic `subject_ref` and uses that reference in memory, traces, and deletion evidence. The redaction decision shows how a harness can rewrite a payload into a subject reference while preserving enough context for audit and recovery.

Third, it demonstrates secret handling. A vault query containing an `api_key`-shaped field triggers an escalation through the data governance engine's DLP check. A second vault query uses a credential reference instead of an inline secret value and is allowed through an approved security route. The point is not that a string check is sufficient for production DLP. The point is that the harness records the boundary: inline secret-like payloads do not silently flow into outbound calls.

Fourth, it demonstrates egress allowlists. A consumer-style external model profile is considered as a destination for PII, but it is not on the approved egress list and is not approved for PII. The chapter blocks that path. This is an important production lesson because many agent incidents are not caused by a strange new capability. They are caused by normal data moving to a normal service that was never approved for that data.

Fifth, it demonstrates residency. The same PII ticket label is deliberately paired with a mismatched region to show that a label must carry location constraints, not just sensitivity. The regulated case is allowed in an EU profile and denied when routed to the wrong region. In production, residency checks may depend on country, tenant, contract, cloud region, encryption boundary, and support staffing model. This lab keeps the rule small so the learner can see the policy shape.

Sixth, it demonstrates lineage and compliance evidence. Allowed governance routes append lineage entries that identify the tool, data class, destination, and region. The scenario then builds a sanitized compliance payload and a deterministic evidence hash. The hash is not meant to replace a real evidence store. It teaches the habit of producing a compact, reviewable statement of what the harness observed.

Seventh, it demonstrates deletion across memory and traces. A subject deletion request is not complete if it only removes one memory record while leaving raw data in trace events. The chapter writes a PII memory record, appends trace events linked to the same subject reference, then tombstones both the memory record and the trace events. The final artifact reports memory tombstones and trace tombstones using identifiers rather than raw PII.

## Labels Are Runtime State

A label is more than metadata. In a long-running system, the label is part of the agent's runtime authority. The data class tells the harness which destinations, tools, and stores are eligible. The residency region tells the harness where processing may occur. The subject reference tells the harness what must be found again during deletion. The policy version tells the harness which rule set produced the label. The lineage parent tells the reviewer where the data came from.

If any of those fields are dropped, the agent may still appear to work. That is the dangerous part. A model can summarize text after a label is lost. A memory store can persist text after a label is lost. A trace backend can record text after a label is lost. The user may even see a useful answer. The failure is invisible until an audit, breach, discovery request, or data subject request asks where the data went and why.

The chapter includes a deliberate label-loss case. A resumed call tries to declare the ticket as internal data even though the checkpointed label says it is PII. The router denies the call because the persisted label and declared data class do not match. This is one of the most important habits in secure agent design: do not allow the caller to simply restate a less sensitive classification. The harness needs a source of truth for the label.

## Routing Is a Multi-Step Decision

The scenario uses a layered route check:

1. The tool gateway checks that the requested tool is registered for the declared risk and data class.
2. The model profile check verifies that the model or processing endpoint is approved for the persisted label.
3. The residency check verifies that the processing region matches the label.
4. The training exclusion check verifies that sensitive data will not be retained in a provider default training mode.
5. The egress check verifies that the destination is on the allowlist.
6. The DLP check escalates if the payload looks like it contains an inline secret.
7. The lineage ledger records allowed routes.

This layered shape matters because no single control knows everything. The tool gateway knows tool registration. The model profile knows processing constraints. The governance engine knows egress and residency. The DLP check knows payload risk. The lineage ledger knows what needs to be reviewed later. A production system might implement these layers in separate services, but the decision needs to feel like one coherent gate to the developer.

This also helps avoid false confidence. A tool may be registered, but the destination may still be wrong. A destination may be approved for public summaries, but not for PII. A model may be allowed in one region, but not another. A payload may have the right destination and still contain an inline secret. Secure routing is a composition problem.

## PII and Subject References

The scenario uses a deterministic `subject_ref` instead of exposing the raw email address in evidence artifacts. That mirrors a common production pattern: compliance and operations teams need to correlate activity for a person or account, but not every trace viewer needs direct access to raw PII.

This does not mean hashing alone solves privacy. A stable subject reference can still be sensitive if it is linkable across systems. In production, teams should define who can reverse or join subject references, how long the references live, how they are salted or keyed, and whether they are tenant scoped. The lab uses a simple stable identifier because the educational focus is on carrying the subject link into memory, traces, and deletion evidence.

The redaction decision is represented as an allowed decision with a rewritten call. The rewritten call preserves the tool, intent, and context reference, but replaces direct payload content with a subject reference and an evidence identifier. A real system might do this in a DLP proxy or tool gateway. The important behavior is that redaction is visible. Silent mutation is difficult to audit. A reviewer should know that the harness changed the payload before allowing it to continue.

## Secret Handling and Escalation

Secrets require different handling from PII. PII may be processed under strict rules, consent, contract, or legal basis. Secrets should usually not be copied into model prompts, memory, or general traces at all. The chapter models this by escalating a vault query that includes an `api_key` field in the outbound payload. Even though the destination is an approved security system, the payload shape is still unsafe.

The safer path uses a reference. The agent can ask for a rotation status using a vault reference without carrying the secret value itself. This is a production pattern worth practicing. Agents should often operate on handles, references, scoped credentials, or brokered capabilities rather than raw secrets. If the agent does not need the secret value to complete the task, the harness should not provide it.

Escalation is not failure. It is a controlled pause for a decision that exceeds the agent's ordinary authority. A strong harness distinguishes between deny and escalate. Deny means the action is outside policy. Escalate means the action may be legitimate, but it requires a human, a stronger identity, a break-glass workflow, or additional evidence.

## Residency and Egress

Egress and residency are related but not identical. Egress asks whether data may leave toward a destination. Residency asks where the data may be processed or stored. A destination can be allowlisted and still be wrong for a data class in a specific region. A region can be correct and still route to a destination that is not approved.

The chapter shows both failures. The consumer model is rejected because it is not approved for PII and is not on the egress allowlist. The regulated trace is accepted through an EU profile and denied when the same data is sent to the wrong region. A production governance review should ask for both controls. "We use an approved vendor" is not the same as "this data stayed in the approved region." "We used the right region" is not the same as "this destination was approved for this data class."

The allowlist in the lab is intentionally explicit. It includes internal ticketing, an approved SIEM route, a training console for public evidence, and an EU regulated model endpoint. Learners should notice that adding a destination to the allowlist is a governance change. It should be reviewed, tested, and tied to evidence.

## Long-Running Label Persistence

Long-running agents create a special governance problem because their state crosses time. They pause, resume, compact context, and retry. During that movement, labels must survive. A checkpoint that stores only text and tool state is not enough. It must store the classification label, subject reference, residency requirement, policy version, and any memory or trace references required for later deletion.

The chapter creates a checkpoint with an active label snapshot, memory keys, and a trace subject reference. On resume, the scenario checks that the label ID and data class survived. The passing path proves that the run can continue with the same governance state. The failing path shows what happens if a call tries to downgrade PII to internal data after resume.

In production, this becomes even more important when agents hand off work to subagents. A subagent should not receive declassified context just because the parent summarized it. If the summary is derived from PII, the summary may still need a PII label or a derived-data label. If a memory record was created under one policy version, a resumed run under a new policy version may need revalidation. The chapter's policy version field is a small hook for that larger design.

## Deletion Across Memory and Traces

Deletion is where many demos stop being production designs. It is easy to delete a user-facing memory entry and forget the trace event that captured the same content. It is easy to delete a trace field and forget an embedding, checkpoint, cache, or evaluation artifact. A real data subject request or incident response task requires a map of every durable place the data went.

The scenario keeps the map small. It writes one PII memory record and two subject-linked trace events. Then it processes a subject erasure request by tombstoning the memory record and tombstoning the trace events. The final artifact reports identifiers for both sets of tombstones. It also keeps sanitized evidence that the deletion happened.

This is an important nuance: deletion does not always mean destroying all evidence that an action occurred. Many compliance regimes require proof that the deletion workflow ran. The evidence should not preserve the sensitive payload, but it may need to preserve a tombstone identifier, reason, timestamp in a real system, approver, policy version, and artifact hash. The lab keeps the evidence deterministic, so it avoids wall-clock timestamps in the JSON, but the production concept is the same.

## Compliance Evidence

The compliance payload is a sanitized bundle. It includes the run ID, policy version, checkpoint ID, allowed lineage entries, memory summary, trace summary, control list, and evidence hash. This gives the reviewer a compact answer to several questions:

- What run produced this evidence?
- What policy version was applied?
- Which labels existed?
- Which routes were allowed?
- Which sensitive stores were tombstoned?
- Which controls were exercised?
- Can the evidence be compared deterministically in a test?

The hash is computed over sanitized evidence, not raw PII or secret values. That distinction matters. Evidence should be useful for audit without becoming a new leak. A production version might sign this evidence, store it in an append-only ledger, or export it to a GRC workflow. The lab only needs a deterministic hash to teach the habit.

## Reading the JSON

When reviewing the output, do not look only at `passed: true`. Read the decisions. You should see allowed paths for approved PII, redacted secret references, regulated EU evidence, public trace evidence, memory write, checkpoint resume, memory erasure, and trace erasure. You should also see denied paths for an external model, a residency mismatch, a lost label, an untrusted PII memory write, and a regulated region violation. You should see at least one escalation for an inline secret-like payload.

Then inspect the artifacts. The `labels` section shows the governing metadata. The `checkpoint` section shows that long-running state carried a label ID. The `lineage` section shows only allowed routes. The `memory` section shows the PII memory record as deleted. The `trace` section shows subject-linked trace events as deleted and field names reduced to safe metadata. The `deletion_evidence` section ties memory and trace tombstones to the same subject reference. The `compliance_evidence` section gathers the review bundle.

That review process is the heart of the chapter. A secure harness is not just a set of blocks. It is an explanation machine. It lets an engineer, auditor, incident responder, or instructor reconstruct why the agent could do some things and not others.

## Exercises

One useful exercise is to add a new model profile that is allowed for internal data but not PII. Route the ticket through it and confirm that the label prevents the downgrade. Then add a public summary derived from the ticket and decide whether it should remain PII, become confidential, or become public after redaction. There is no universal answer. The point is to force an explicit policy decision.

Another exercise is to add a second tenant. Make sure memory reads and deletion requests remain tenant scoped. A subject reference that is stable across all tenants may be unacceptable in some systems. A tenant-scoped subject reference may be safer, but it can complicate global deletion workflows. That tradeoff should be visible in the artifacts.

Another exercise is to add an approval override for the secret escalation. The override should not simply turn the decision into allow. It should record who approved it, what evidence they reviewed, how long the approval lasts, and whether the approval applies to one call or a class of calls. This is how break-glass workflows stay accountable.

Another exercise is to make the policy version change between checkpoint and resume. The resumed run should either deny, escalate, or revalidate labels before continuing. Long-running systems cannot assume that yesterday's policy is still valid today.

Finally, extend deletion to a derived public summary and decide what should happen. If the summary contains no personal data, maybe it can remain. If it can still be linked to a subject, maybe it needs a tombstone. The production lesson is that deletion decisions depend on derivation, linkability, retention obligations, and policy.

## What Good Looks Like

A production-ready answer to this chapter is not "the model promised not to leak data." A production-ready answer is a set of enforceable routes, labels, stores, and evidence flows. The harness should know which data class is present, which destinations are allowed, which regions are required, which payloads need redaction, which actions require escalation, which memory and trace records exist, and how to prove deletion later.

The agent remains useful. It can read a ticket, use a safe model profile, query a vault by reference, emit sanitized evidence, remember governed state, resume a long task, and produce compliance artifacts. The harness does not solve safety by forbidding agency. It makes agency bounded, reviewable, and recoverable.

That is the core lesson of Chapter 10. Governance for long-horizon agent systems must be carried by runtime state and enforced by the harness. If the label disappears, the safety case disappears with it. If the evidence is not produced, the organization cannot prove the control worked. If deletion only touches one store, the erasure story is incomplete. A secure system treats classification, routing, lineage, and deletion as ordinary executable behavior, not as an afterthought.
