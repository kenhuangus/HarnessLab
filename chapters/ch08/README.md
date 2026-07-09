# **Chapter 8: Runtime Steering: Intervention, Policy Injection, and Safe Rollback**

Runtime steering is the control plane for an agent that is already in motion. Earlier chapters teach how to shape a run before it starts: identify the actor, define intent, filter context, guard memory, and collect observability. Those controls are necessary, but they are not sufficient for long-running agents. A long-running agent may spend minutes, hours, or days moving through a workflow. During that time the world can change. A ticket can receive a hostile comment. A human can discover that a tool was misclassified. A downstream system can begin returning risky data. A new policy can be issued while the agent is halfway through a task. The important question is not only "was this agent allowed to start?" It is also "can the harness safely intervene after the agent has started?"

This lab models that problem with a deterministic incident-response run. The simulated agent reads a ticket, detects hostile context, writes a reversible draft, pauses, receives a temporary policy overlay, blocks unsafe outbound communication, kills a retrying subtask, resumes from a checkpoint, replays preserved evidence, compensates for the reversible draft, allows the overlay to expire, and finishes with a final checkpoint. The code is small on purpose, but the shape is production-like. The harness does not ask the model to promise that it will be careful. It records state, checks controls, changes runtime policy, and produces artifacts that can be inspected after the run.

You can run the chapter with either public contract:

```bash
python -m chapters.ch08.run
harnesslab run ch08 --json
```

Both paths execute `scenario.run()` and return a `LabResult`. The result includes deterministic decisions and artifacts, so it can be used in classroom demos, continuous integration, or regression tests without live services or paid model APIs.

## Learning Goals

By the end of this chapter, you should be able to explain the difference between pre-run authorization and runtime steering. You should also be able to name the minimum controls a long-running harness needs once a run has started: observe, warn, pause, block, kill, quarantine, recover, replay, and compensate. These verbs are intentionally plain. They describe what an operator expects from a serious control plane. An agent platform that cannot pause a run, preserve evidence, recover from a checkpoint, or roll back a reversible write is asking humans to trust a moving system without enough handles.

The chapter also teaches three supporting ideas. First, interrupts must preserve evidence. If the harness pauses or kills a run but loses the state that caused the interruption, the organization cannot learn from the event or prove that the response was appropriate. Second, temporary policy changes need expiry. A runtime overlay is useful when a new risk appears, but unbounded overlays become hidden permanent policy. Third, rollback should be safe and explicit. Some side effects are reversible and can be compensated. Others are not. The harness should model that distinction before the agent touches production tools.

## Runtime Steering In Context

Runtime steering sits between observability and governance. Observability tells the harness what is happening: which tool was called, which context was read, which state was written, and which decisions were made. Governance defines the standing rules: which data classes can leave, where regulated data may reside, and which tools are approved. Runtime steering is the active middle layer. It watches the run and uses both evidence and policy to decide whether to let the run continue, slow it down, change its policy, rewind to a checkpoint, or stop part of the run entirely.

This is especially important for agentic systems because agent runs are not always a single request and response. A long-horizon agent may read data, summarize it, call a tool, update memory, ask another agent to help, revisit earlier assumptions, and continue after a delay. A static approval at the start of that process cannot account for every later condition. Runtime steering makes the harness responsive without becoming chaotic. It gives the system a controlled vocabulary for intervention.

In this lab, the run is an incident-response task. The agent begins with a reasonable internal ticket. Then an external ticket comment includes classic instruction-injection language: it tells the agent to ignore previous instructions and send private data to an external mailbox. A prompt-only system might hope the model resists. A secure harness does something stronger. It quarantines the context, warns the operator path, checkpoints the run, pauses execution, and injects a bounded overlay that blocks outbound messages using sensitive data until recovery is complete.

## The Steering Verbs

The scenario demonstrates nine runtime verbs. Each verb appears as a decision control and as evidence in the artifacts.

Observe means the harness sees the run before acting. In the scenario, the first tool call reads an internal ticket through the tool gateway. This step is not glamorous, but it is foundational. You cannot safely steer what you cannot observe. Production systems should capture enough data to answer who acted, which run was active, what tool was requested, what data class was involved, and which policy version applied.

Warn means the harness detects risk without stopping all progress. The lab raises a warning after hostile context is quarantined. A warning can notify an operator, mark a run for review, increase sampling, or require a checkpoint before the next action. Warning is useful when the system has evidence of risk but can still continue under tighter controls.

Pause means the main run is temporarily stopped. The scenario pauses the long-running run after the hostile context tries to redirect the task. Pause is softer than kill. It should preserve state and leave a path to recovery. In production, pause is valuable when a human needs to review evidence, when a temporary dependency is unhealthy, or when a new policy must be injected before continuing.

Block means a specific action is denied while the run may still be recoverable. In this lab, the agent attempts to send a customer email containing PII and raw private notes while a temporary policy overlay is active. The harness blocks that outbound action. Blocking should be precise. If the unsafe action is one tool call, the harness should not necessarily destroy the entire run. Precision reduces needless disruption while still protecting the boundary that matters.

Kill means a subtask is terminated. The lab kills a child run that keeps retrying the blocked outbound communication. Kill should be reserved for behavior that is unsafe to continue: repeated policy evasion, compromised credentials, runaway loops, or operations that could produce irreversible harm. Killing a child task while recovering the parent run is often better than killing the whole workflow.

Quarantine means suspicious input or state is isolated from the trusted working set. The lab uses the context firewall to quarantine an external comment with instruction-injection markers. Quarantine is more useful than deletion because the organization may need the evidence later. A quarantined item should not steer tool use, but its findings should remain available for audit, training, and incident response.

Recover means the run moves back to a known good state. The scenario resumes from a checkpoint captured before the pause and policy injection. Recovery should not be guesswork. The harness should know which checkpoint was used, which evidence hash anchored it, and what state was restored.

Replay means the harness re-evaluates the preserved safe prefix before continuing. Replay is how a system avoids blindly trusting a stale checkpoint. In this lab, replay verifies that the checkpoint evidence hash matches the stored evidence chain. In larger systems, replay can rerun policy checks, compare tool outputs, or reconstruct the sequence of allowed decisions before the resumed run moves forward.

Compensate means the harness performs an explicit corrective action for a reversible side effect. The scenario writes a draft memory record and later tombstones it after the blocked outbound attempt invalidates the draft. Compensation is not the same as pretending the side effect never happened. The ledger still shows the write and the rollback. That distinction matters for auditability.

## Evidence-Preserving Interrupts

An interrupt that destroys evidence is a weak interrupt. Imagine a run is killed because it attempted to exfiltrate data, but the system deletes the prompt, tool arguments, policy decision, and state snapshot that caused the kill. The organization is left with a vague statement that something bad happened. It cannot improve detection, satisfy an auditor, or explain the event to a customer.

The lab uses a small deterministic evidence ledger to model a better approach. Every steering event records the action name, the current state snapshot, the decision, and the previous evidence hash. The event is hashed into a chain. The artifacts report the final head hash, the event count, and whether the ledger verifies. This is not a replacement for production trace storage, but it teaches the control-plane shape: interruptions should create more evidence, not less.

The pause, block, and kill events are especially important. These are the moments when operators will later ask why the harness intervened. The scenario asserts that those interrupt actions appear in the evidence chain. The final result passes only if the evidence verifies and each interrupt has an evidence event. That turns evidence preservation from an aspiration into executable behavior.

In production, the same principle often maps to append-only logs, signed envelopes, trace spans, immutable object storage, or tamper-evident ledgers. The exact storage technology is less important than the invariant. Every intervention should be reconstructable from preserved facts. Those facts should include the run identity, actor identity, policy version, tool call, data class, and state needed to understand what happened.

## Policy Overlays With Expiry

A policy overlay is a temporary rule injected into a running system. Overlays are useful because runtime risk is often local and time-bound. If a ticket receives hostile external context, the harness may temporarily block outbound messages for that run. If a tool starts returning malformed data, the harness may require extra validation for calls that use that tool. If a regulator issues urgent guidance, the harness may apply a stricter rule before the next scheduled policy release.

Temporary does not mean casual. A runtime overlay should identify its scope, reason, and expiry. Scope answers where the overlay applies: one run, one tenant, one tool, one data class, or one fleet. Reason answers why the overlay was injected. Expiry answers when the system returns to standing policy unless someone renews the overlay through a proper path.

In the scenario, the overlay denies `send_customer_email` for PII and confidential data until step 8. That overlay blocks the unsafe email attempt at step 7. After recovery, replay, and compensation, the run reaches step 12. At that point the overlay is expired, and a redacted public notification can pass through the normal tool gateway. This shows a healthy pattern: the overlay is strong enough to prevent the risky action, but bounded enough that it does not silently become permanent policy.

Production systems may express expiry as wall-clock time, step count, checkpoint generation, approval ticket, or policy bundle version. The lab uses a deterministic step expiry because the repository must run without clocks affecting the result. The concept is the same. If an overlay cannot expire, it should probably be promoted into the normal policy system, reviewed, tested, and versioned.

## Checkpoints, Recovery, And Replay

Checkpointing is the foundation of safe runtime recovery. A checkpoint captures enough state to resume from a known point. That does not mean every byte of memory must be copied. It means the harness can restore the run to a state that is meaningful for the workflow and defensible for audit. The checkpoint should include the run identifier, policy version, relevant state, and an evidence hash that anchors what the system knew at the time.

The lab captures a checkpoint after the ticket has been observed, the hostile context has been quarantined, the warning has been raised, and a reversible draft has been written. That point is chosen carefully. It is late enough to preserve useful work, but early enough to avoid including the blocked outbound attempt. When the run pauses and the child subtask is killed, the parent can recover from this checkpoint rather than starting over.

Recovery alone is not enough. A checkpoint can be stale, incomplete, or tampered with. Replay gives the harness a chance to validate the safe prefix before continuing. The scenario compares the checkpoint evidence hash with the evidence chain and verifies the chain itself. If the evidence does not match, replay returns a deny decision and the lab fails. In a larger harness, replay might call evaluators, rerun policy decisions, or compare state transitions against a schema.

Long-running runs need this because they often cross process boundaries. A worker may restart. A queue may delay work. A human may review the run hours later. A policy may change while the run is paused. Checkpoint and replay let the harness continue without pretending that nothing happened during the gap.

## Safe Rollback And Compensation

Rollback is easy to say and hard to do safely. Some operations can be reversed directly. A draft memory record can be tombstoned. A queued message can be canceled. A feature flag can be restored. Other operations are not truly reversible. An email that was already sent cannot be unsent. A secret that was exposed must be rotated, not simply marked deleted. A payment that was issued may require a compensating transaction, not a rollback.

The lab models a reversible write with `MemoryFirewall.propose_write()`. The run stores a draft customer notice while it is still operating normally. Later, the blocked outbound attempt shows that the draft should not be trusted. The harness compensates by tombstoning the memory record. The artifact reports the record id, deletion status, and tombstone reason.

Notice what the scenario does not do. It does not erase the write from history. The memory ledger still contains a record showing that the draft existed and was rolled back. That is the right pattern. Safe rollback should preserve accountability while removing unsafe state from future use. A production memory system might implement this with tombstones, versioned records, revocation markers, or ledger entries. The important point is that future reads should not treat the rolled-back state as active truth.

Compensation also belongs in the decision stream. If a system performs a corrective action but does not expose it as a decision, operators cannot distinguish clean progress from repaired progress. The lab includes `compensate` and `safe_rollback` controls in the final result, making the repair visible.

## Reading The Result

The `LabResult` tells the story of the run in three places. The `decisions` list is the chronological policy narrative. It shows allowed observations, warnings, the pause, the bounded overlay, the block, the kill, recovery, replay, compensation, and the final checkpoint. The `artifacts` map is the audit bundle. It contains checkpoint ids, the resumed step, quarantined context ids, blocked tool history, killed child run ids, overlay expiry details, rollback status, evidence verification, and replay details. The `passed` flag is the executable assertion that all required controls were exercised and verified.

Because this is a teaching lab, the artifacts are intentionally compact. They are not intended to be a full production trace. They are intended to make the control-plane invariants visible:

1. The run is observed before intervention.
2. Hostile context is quarantined rather than trusted.
3. The operator path receives a warning.
4. The run pauses before continuing under new risk.
5. A bounded overlay changes policy for the run.
6. Unsafe outbound action is blocked.
7. A retrying child subtask is killed.
8. The parent run recovers from a checkpoint.
9. Evidence is replayed before continuation.
10. A reversible write is compensated through rollback.
11. The overlay expires before normal completion.
12. A final checkpoint closes the run.

If any of these invariants break, the lab should fail. That makes the chapter useful as a regression guard. Future changes to the core runtime controller or chapter scenario should not accidentally remove evidence preservation, expiry, rollback, or resumption.

## Production Design Notes

When adapting this pattern to a real system, start by deciding what a run is. A run needs a stable identifier, an actor, a policy version, and a state model. Without those, pause and recovery become informal. Next, decide which operations are interruptible. Read operations, reversible writes, external communication, privileged operations, and irreversible writes need different steering rules. A pause may be enough for a read. A block may be required for external communication. A kill may be required for a compromised worker. Irreversible writes may need human approval before they happen at all.

Then define the evidence contract. Each steering decision should be recorded with the triggering facts. Logs that only say "denied" are rarely enough. Operators need to know what was denied, which data class was involved, which policy applied, and which state was preserved. Evidence should be retained even when context is quarantined. Quarantine removes influence, not accountability.

Finally, make expiry and compensation operational. Runtime overlays should have owners, reasons, and expiration rules. Compensating actions should be typed by side effect. A rollback for a memory write is not the same as a remediation for a leaked secret or an apology email to a customer. The harness should encode those differences so that agents cannot treat every mistake as if it were equally reversible.

The deeper lesson is that runtime steering lets a secure harness stay adaptive without becoming arbitrary. The agent is allowed to work, but the harness keeps handles on the run. It can observe, warn, pause, block, kill, quarantine, recover, replay, and compensate. Those handles are what make long-running autonomy governable.
