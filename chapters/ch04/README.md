# **Chapter 4: Intent: Contracts, Drift Detection, and Authorization by Purpose**

Chapter 4 teaches the control plane that sits between an agent's stated goal and the tools it wants to use. A long-running agent can hold a useful instruction at the start of a run, then slowly drift as it reads more context, follows subgoals, resumes from checkpoints, or receives a new request from a human. The harness cannot treat "the user asked me to help" as a permanent all-access pass. It needs a concrete intent contract that says what purpose is approved, who may act on it, what tools are in scope, what data may be touched, how much risk is acceptable, what evidence must exist, and when a new authorization is required.

This chapter is intentionally small and dependency-free, but it models a real production pattern. The scenario starts with a remediation agent that has approval to fix a vulnerable dependency in a billing service. That purpose allows it to read the security ticket, create a repository patch, and emit internal evidence. It does not allow it to deploy to production, send customer email, read secrets, or opportunistically improve an unrelated feature. Those blocked actions are not bad in every context. They are bad under this context. That distinction is the point of intent security: the decision is made against purpose, not against a vague global idea of whether a tool is safe.

## What The Scenario Runs

Run the chapter from the HarnessLab project root:

```bash
python -m chapters.ch04.run
python -m harnesslab.cli run ch04 --json
```

Both paths return a `LabResult`. The result includes policy decisions and artifacts that instructors can inspect without any network calls, secrets, API keys, or vendor accounts. The chapter uses only Python's standard library plus shared primitives from `harnesslab.core`.

The main executable behavior is in `scenario.py`. It builds an `IntentContract` for a remediation goal:

```text
remediate vulnerable dependency in billing-api
```

The contract binds that goal to a `remediation_agent` role. It allows `read_ticket`, `patch_repo`, and `emit_trace`. It permits public and internal data. It caps risk at reversible writes. It requires a ticket and a test log as evidence. It also marks external communication and privileged operations as actions that require escalation. These fields make the contract more than a prompt. The harness can compare tool calls against a structured object and produce deterministic allow, deny, warn, rewrite, or escalate decisions.

The run then walks through several situations that long-horizon systems encounter:

1. The agent reads a ticket and prepares a repository patch that match the contract.
2. The agent proposes an unrelated patch while the repository is already open.
3. The agent tries to deploy the service under a remediation-only contract.
4. The agent tries to send a customer email before a communication purpose exists.
5. The harness rewrites that external email into an internal trace artifact.
6. The run resumes from a checkpoint after the active human goal has changed.
7. A reauthorization request with the wrong purpose is rejected.
8. A new customer-notice contract is issued for the new purpose.
9. The customer email succeeds only under the new purpose-bound contract.

Those steps are meant to feel familiar. Real agent deployments often fail at the boundary between "I am continuing the task" and "I am now doing something materially different." The difference may be subtle. Updating a dependency is one purpose. Deploying the service is another. Notifying affected customers is another. Reading secrets for rotation is another. A well-designed harness treats these as separate authority envelopes, even when the same conversation, run ID, or agent process connects them.

## Intent Contracts

An intent contract is a short-lived authorization envelope. It should be specific enough that a tool gateway can enforce it and a human reviewer can understand it. In HarnessLab, the shared `IntentContract` contains:

- `intent_id`: a stable label for the approval.
- `goal`: the human-approved purpose.
- `actor_role`: the role expected to act under the contract.
- `allowed_tools`: the tools that may be called for this purpose.
- `allowed_data`: the data classes that may be accessed.
- `max_risk`: the highest action risk allowed without separate approval.
- `evidence_required`: proof that must be present before work proceeds.
- `expires_at`: the time boundary for the authorization.
- `escalation_required_for`: risk categories that need human review even if other fields look acceptable.

The executable scenario uses these fields directly. The remediation contract allows a ticket read and a repository patch because those actions are necessary for the approved purpose. The same contract denies a deployment because deployment is a privileged operation and is not one of the allowed tools. It denies a customer email because external communication with PII is not part of dependency remediation. The email is not condemned forever. It simply needs its own communication purpose.

This is different from a static allowlist. A static allowlist might say that the agent role can call `send_customer_email`. An intent contract says the role can call that tool only when the current approved purpose, evidence, data class, risk, and timing line up. That is the security property we want in a long-running agent. The agent may need broad capabilities across its life, but it should have narrow authority at any particular moment.

## Drift Detection

Drift is what happens when the agent's next action no longer matches the purpose that originally authorized the work. The scenario demonstrates drift with a patch call that uses an approved tool and an approved data class, but declares a different intent:

```text
optimize recommendation ranking while the repo is open
```

That action uses `patch_repo`, which is normally in scope for the remediation contract. The risk is also within the reversible-write maximum. A simple tool allowlist would approve it. The intent verifier warns because the declared purpose has moved away from the contract goal. That warning matters. In a real harness, a warning can pause a plan, ask the agent to restate its goal, request human review, or require a new contract before the action is executed.

Drift detection does not need to mean perfect natural language understanding. Production systems can combine several signals: goal fingerprints, ticket IDs, plan-step references, task metadata, embeddings, reviewer approval text, and simple lexical checks. This lab uses a deliberately transparent check so students can see the shape of the control. The important design point is that drift is evaluated before the action, and that the result becomes evidence. The harness records that the action was allowed, denied, warned, rewritten, or escalated for a named reason.

Long-running systems need this because time changes context. An agent may start by patching a dependency, then discover a test failure, then notice adjacent code, then decide to improve a feature. The improvement might be useful, but it was not approved. The correct harness response is not to erase initiative. It is to channel initiative into a new approval boundary.

## Authorization By Purpose

Authorization by purpose means the harness evaluates "may this actor do this action for this reason right now?" rather than "may this actor ever use this tool?" The scenario shows this twice.

First, `deploy_service` is denied under the remediation contract. Deployment may be the right next operational step after testing, but it is not a reversible repository change. It changes production. The contract therefore denies the proposed action before the tool gateway even needs to decide whether the tool exists.

Second, `send_customer_email` is denied under the remediation contract. The call carries PII and has an external communication side effect. The shared tool registry knows that `send_customer_email` can handle PII, so a pure tool compatibility check would not block it. The intent layer blocks it because customer communication is a different purpose from dependency remediation.

This separation is crucial. Tool gateways answer whether a tool call is structurally valid for a registered tool. Intent contracts answer whether that structurally valid call belongs to the currently approved purpose. Both checks matter. If either layer is missing, an agent can accumulate too much ambient authority.

## Tool-Call Rewriting And Escalation

The scenario includes a local helper that rewrites an unsafe external email into a safer internal trace event. The proposed email is not executed. Instead, the harness creates an `emit_trace` call that records a redacted draft event:

```text
customer_notice_draft_blocked
```

The rewrite preserves useful evidence while removing customer identifiers and preventing external communication. It lets the agent keep making progress without crossing the purpose boundary. The rewritten call is then checked against the same remediation contract and the shared tool gateway. It passes because internal evidence emission is allowed.

Rewriting is not always possible. Some calls should simply escalate or fail closed. A request to query a vault, delete production data, or deploy to a regulated environment usually cannot be made safe by changing the tool name. In those cases the harness should return an escalation decision with enough context for a human or higher-trust controller to decide the next contract. This lab includes escalation for stale resume state and for actions that cannot be safely transformed under the active purpose.

The broader lesson is that a harness should have more than two answers. Allow and deny are necessary, but long-horizon agents benefit from warn, rewrite, and escalate outcomes. Warn catches possible drift. Rewrite keeps safe evidence flowing. Escalate preserves momentum while moving risk to a stronger approval path. These richer decisions make the system safer without forcing every uncertainty into a hard stop.

## Stale Goals On Resume

Resume is a dangerous moment for agents. A checkpoint can preserve plan state, tool outputs, memory references, and partially completed work. But it may not preserve the authority that made those steps valid. A user might return the next day and ask for a different outcome. A policy might change. The original approval might expire. A delegated agent might be replaced. If the harness blindly resumes, the agent can continue under stale assumptions.

Chapter 4 stores a checkpoint with the original remediation intent ID and a digest of the remediation goal. When the run resumes, the active goal is now:

```text
notify affected customers about patched vulnerability
```

That is related to the incident, but it is not the same purpose. The chapter compares the checkpoint's stored goal digest and intent ID with the active purpose. They do not match, so the harness escalates:

```text
resume checkpoint goal no longer matches the active purpose; reauthorization required
```

This check is intentionally simple and deterministic. A production implementation might include richer state, such as the approving user, policy version, ticket status, evidence hash, and delegation chain. The principle is the same: a resumed process must prove that its old authority still matches the current purpose. If it cannot prove that, it must pause for reauthorization.

This is especially important for agents that operate over hours or days. The longer the run, the more chances there are for the world to change around it. Stale-goal detection turns resume from a blind continuation into a policy decision.

## Purpose-Bound Reauthorization

After stale-goal detection fires, the chapter demonstrates reauthorization. The first reauthorization request is intentionally wrong. It includes an approval ticket, but the approval is bound to:

```text
deploy billing-api to production
```

The active requested goal is customer notification. The harness denies that approval because approval for one purpose cannot be spent on another. This is the same idea as audience binding for credentials. A credential minted for a repository should not work against a vault. An intent approval minted for deployment should not authorize customer email.

The second reauthorization request matches the active goal and includes the required evidence: an approval ticket and a message template. The harness issues a new contract for `customer_comms_agent`. That contract allows `send_customer_email` and `emit_trace`, permits public, internal, and PII data, and caps risk at external communication. The customer email then passes the intent verifier and the tool gateway.

This final step is important because it shows that the harness is not anti-action. It does not permanently block the user from sending notices. It asks for the right authority envelope and then allows the action. Good security controls should shape work, not merely obstruct it.

## How To Read The Result

The `LabResult` contains deterministic decisions and artifacts. The decisions list is the audit trail. You should see allows for evidence, ticket read, patch preparation, rewritten trace emission, valid reauthorization, and the final customer email under the new contract. You should see a warning for drift. You should see denies for actions outside the approved purpose. You should see an escalation for stale resume state. You should see a rewrite decision that points from `send_customer_email` to `emit_trace`.

The artifacts summarize the two contracts, decision counts, drift detection, purpose denials, rewrite details, resume state, and reauthorization outcome. These artifacts are deliberately plain dictionaries so they can be rendered in a classroom, checked in CI, or inspected by a reader without special tooling.

The `passed` flag requires all core behaviors to occur. It is not enough for the happy path to work. The scenario must also show a warning, a denial, an escalation, a rewrite, stale-goal detection, rejected wrong-purpose approval, and successful purpose-bound reauthorization. The score is calculated from shared HarnessLab decision scoring.

## Production Lessons

Use intent contracts where an agent crosses a meaningful authority boundary. That includes external communication, writes to repositories, production deployments, memory persistence, regulated data access, vault reads, financial actions, and any tool that can create durable side effects. Keep contracts short-lived. Bind them to a purpose, actor role, evidence, data classes, and tool set. Store the contract ID and goal fingerprint in traces and checkpoints.

Do not rely on prompts alone. A prompt can ask the agent to stay on task, but the harness must enforce the boundary. The enforcement should happen before tool execution and should produce evidence. If the agent asks for a tool outside purpose, the system should produce a named decision, not a vague failure.

Treat resume as a new authorization event. A checkpoint is not proof that old authority still applies. Compare the stored intent to the active goal. Check expiry. Check policy version. Check whether the approving human or delegated role still has authority. If any of those do not match, escalate.

Prefer narrow reauthorization over broad unlocks. When the user approves customer communication, issue a customer-communication contract. Do not expand the remediation contract until it can do everything. Narrow contracts are easier to reason about, easier to revoke, and easier to audit.

Finally, build graceful alternatives. Rewriting an unsafe call into safe evidence is often better than stopping the agent with no output. The agent learns what evidence is missing, the human gets a trace of what was attempted, and the system avoids crossing a boundary prematurely. That is the hill-climbing pattern in this chapter: preserve progress, but make every increase in authority explicit, bounded, and reviewable.
