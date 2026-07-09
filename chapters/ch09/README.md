# **Chapter 9: Scalability: Fleet Coordination Without Cascading Failure**

Chapter 9 teaches the part of agent safety that becomes visible only when a system is busy for a long time. A single agent can look safe in a short demo because the demo has one user, one task, one tool call, and one happy path. A production fleet has many tenants, many workers, many queues, many retries, shifting rate limits, and partial failures that arrive while useful work is already in flight. In that setting, a secure harness is not just a prompt wrapper. It is a control plane that decides which work may start, which work must wait, which worker is allowed to hold a lease, which retries are safe, which capacity is already committed, and which evidence must survive a pause or incident review.

The executable scenario in this chapter is intentionally deterministic and dependency-free. It does not simulate cloud infrastructure, but it does model the control-plane shapes that students should recognize when they later work with queues, worker pools, model gateways, workflow engines, and policy services. The lab creates a small fleet for two tenants. It admits work into tenant-specific bulkheads, applies a global active-work limit, queues work under back-pressure, enforces capacity quotas, delays tool use when a rate window is exhausted, records idempotency keys before side effects, quarantines a compromised worker, retries the interrupted task without duplicating side effects, and pauses long-running work across governance epochs.

Run the lab from the HarnessLab project root with:

```bash
python -m chapters.ch09.run
```

The command prints a JSON `LabResult`. The public contract is the same as the other HarnessLab chapters: `scenario.py` exposes `run()` returning `harnesslab.core.LabResult`, and `run.py` prints `run().to_json()`. The interesting fields are `decisions` and `artifacts`. The decisions show every allow, warn, deny, or escalate outcome. The artifacts show the final fleet state, idempotency ledger, rate-limit windows, capacity-governance state, required controls, and unsafe paths that were contained.

## Why Fleet Coordination Is A Security Control

Fleet coordination is often described as a reliability concern, but in long-horizon agent systems it is also a security concern. A worker that is allowed to run forever can accumulate stale context, stale credentials, stale policy assumptions, and unreviewed side effects. A queue that accepts unlimited work can turn a minor incident into a denial-of-service condition. A retry loop that repeats non-idempotent tool calls can send duplicate emails, duplicate patches, duplicate payments, or duplicate production changes. A shared worker pool without tenant bulkheads can let one tenant's runaway workload consume capacity needed by another tenant. A compromised worker that is not isolated quickly can keep operating under a valid lease while the rest of the system assumes the fleet is healthy.

The core idea is that useful agency has to be bounded by explicit operational gates. The harness should not merely ask whether a proposed action sounds safe. It should also ask whether the fleet has capacity, whether the tenant has quota, whether the tool has rate headroom, whether the retry can be proven idempotent, whether the worker is still trustworthy, and whether the task has a checkpoint that allows it to stop and resume cleanly. These questions are security questions because they determine how far a mistake or compromise can propagate.

In this chapter, the fleet control plane treats each work item as a lease-bound operation. A work item has a tenant, operation, idempotency key, payload, capacity cost, expected duration, and tool list. That is a small model, but it is enough to teach production reasoning. The tenant and operation support bulkheads and quotas. The idempotency key and payload hash support retry safety. The capacity cost and expected duration support long-running governance. The tools support rate limiting. The worker lease supports containment.

## The Scenario Flow

The scenario begins by admitting two Acme tasks into the Acme bulkhead. One task is a short triage operation. The other is a longer patch-preparation operation that needs a checkpoint because it is expected to run longer than the chapter's checkpoint threshold. The capacity governor reserves capacity for both. When the longer patch task does not fit in the current governance epoch, the governor records a rollover and resumes the task in the next epoch. This models a real long-running agent that cannot assume yesterday's capacity budget, policy window, or operator shift is still valid.

Next, a Globex triage task arrives while the global active-work limit is already full. The task is accepted into the queue instead of being started. That warning is not a failure. It is the desired back-pressure behavior. In production, the equivalent action might be returning a retry-after response, placing the task in a durable queue, reducing planner parallelism, or asking an operator to approve more capacity. The important point is that the harness does not hide saturation. It records a decision that reviewers can see later.

The scenario then submits an Acme follow-up patch while both Acme workers are already busy. This exercises a different form of back-pressure: the tenant bulkhead is full. Even if another tenant has an idle worker, the Acme work should not automatically spill into that tenant's worker pool. Bulkheads preserve isolation. They prevent one tenant's incident, workload spike, or compromised worker from consuming every clean worker in the fleet. In a real deployment, the bulkhead might map to separate queues, separate service accounts, separate Kubernetes namespaces, separate model-gateway pools, or separate workflow-engine partitions.

The lab also submits a larger Acme analysis task after the tenant has already reserved its capacity quota. That task escalates instead of starting. Escalation is the correct behavior because quota exhaustion is not always a hard deny. Sometimes an operator can approve a temporary increase, lower the task's priority, move it to a different schedule, or ask the planner to produce a cheaper plan. The scenario records this as a capacity and quota escalation so students can distinguish bounded human review from silent overcommitment.

The compromised-worker path is the unsafe path. The Acme patch worker is marked compromised after it emits a tool request containing a policy-disabling instruction. The harness quarantines the worker, revokes the active lease, and returns the interrupted task to the queue. This is containment. The task is not discarded, because useful work should continue when it can do so safely. It is not allowed to continue on the compromised worker, because the lease no longer has trustworthy execution context. When a clean Acme worker becomes available, the queued task is promoted and retried.

That retry is safe because the idempotency ledger recorded the original key and payload hash before tool execution. When the task restarts with the same key and same payload, the ledger warns that this is a retry after lease loss and suppresses duplicate side effects. Later, the lab attempts a poisoned retry that reuses the same idempotency key with a different payload. The ledger denies it. This is the core production lesson: retry safety is not a boolean label on a function. It is a ledgered contract between key, payload, attempt count, status, and side-effect boundary.

The rate limiter is exercised when too many tool calls hit the same tool in one window. The lab delays a `read_ticket` call and a `patch_repo` call into later windows. This is not about pretending that rate limits are a complete safety solution. It is about showing that rate limits belong in the same evidence stream as policy decisions. If a queue grows because the patch tool is rate-limited, a reviewer should be able to see that cause directly. Otherwise teams may misdiagnose rate exhaustion as model slowness, worker failure, or tenant abuse.

## Reading The JSON

The `decisions` array should be read as the control narrative. Look for an `allow` when a task is admitted to a clean worker. Look for a `warn` when work is queued, delayed, checkpointed, or retried. Look for an `escalate` when tenant capacity is exhausted. Look for a `deny` when a compromised worker is quarantined or a poisoned retry is blocked. The lab is successful because these decisions are explicit and because they map to named controls.

The `artifacts.fleet` object shows the operational result. It includes active tasks, completed tasks, queued tasks, quarantined workers, tenant capacity reservations, and queue promotions. In a production system, this information would be spread across queue metadata, worker leases, orchestration logs, and scheduler state. HarnessLab keeps it together so students can inspect the whole story.

The `artifacts.idempotency_ledger` object shows the retry state. Each key has the original task id, payload hash, attempt count, and status. This is one of the most important artifacts in the chapter. Without it, the harness could not prove that the resumed patch task used the same payload, and it could not block the poisoned retry that reused a trusted key for changed work.

The `artifacts.rate_limits` object shows per-tool windows and delayed calls. The values are small because the lab is small, but the production shape is familiar: a model gateway, tool gateway, or workflow engine needs a durable record of rate-limit pressure. Rate-limit pressure should feed planning decisions. A planner that knows the patch tool is saturated can batch, reorder, or ask for approval instead of blindly spawning more workers.

The `artifacts.capacity_governance` object shows the current governance epoch, remaining capacity, checkpoints, and epoch rollovers. The word "epoch" is deliberately generic. In a real organization it might mean a budget window, maintenance window, shift boundary, policy release, human approval window, or scheduled capacity interval. Long-running agents need an explicit unit like this because they do not complete inside one neat request-response envelope.

The `artifacts.unsafe_paths` object gives a compact pass/fail summary for the unsafe behaviors. The chapter should not pass unless the compromised worker was contained, the poisoned retry was blocked, and the quota-overrun path escalated. This makes the lab more than a success-path demo. It teaches students to preserve useful work while proving that unsafe paths are bounded.

## Design Lessons

First, admission control should happen before execution. The fleet must know whether a tenant has quota and whether a clean worker is available before a task begins spending capacity or calling tools. In the lab, a task may be accepted into the queue without being executed. That distinction is important. A queue entry is not permission to perform side effects. It is a promise that the scheduler will reconsider the task under current policy when capacity becomes available.

Second, a bulkhead is useful only if it fails closed. The Acme follow-up patch cannot borrow a Globex worker just because Globex has an idle worker. That can feel inefficient in a toy example, but it is exactly the point. Production systems often trade a small amount of utilization for a large amount of containment. The right answer is not always strict separation, but the harness should force the design decision to be explicit.

Third, back-pressure must be visible to the planner. If the planner keeps producing tasks while every downstream queue is saturated, the harness becomes a buffer for unsafe ambition. A good harness feeds pressure signals back into planning, prioritization, and human review. In a more advanced version of this chapter, students can add planner behavior that reduces fan-out when queue depth or rate-limit delay crosses a threshold.

Fourth, retries need identity. A retry should answer three questions: is this the same logical operation, is this the same payload, and has this operation already committed side effects? The lab answers those questions with an idempotency key, payload hash, attempt count, and status. In production, the ledger might also include actor identity, policy version, tool version, request hash, response hash, and evidence envelope hash.

Fifth, compromised-worker containment is a runtime control, not a postmortem note. Once a worker is suspected, the harness must revoke its lease, quarantine it from new assignments, preserve evidence, and decide what to do with the interrupted task. The lab returns the task to the queue because the idempotency ledger can make the retry safe. A task without idempotency evidence should escalate instead.

Sixth, capacity governance is not only about cost. Capacity represents the right to keep consuming attention, tool calls, model calls, review bandwidth, and operational risk over time. Long-running tasks should checkpoint before they cross meaningful boundaries. They should resume under current policy, not under assumptions captured at the moment they began.

## Exercises

One exercise is to add priority classes. Give incident response tasks higher priority than retrospective analysis, but preserve tenant quotas so one urgent tenant cannot starve every other tenant. The teaching question is whether priority changes scheduling only, or whether it also changes quota and rate-limit policy.

Another exercise is to add a non-idempotent tool, such as `send_customer_email`. The expected behavior is that a retry after lease loss should escalate unless the harness has evidence that the email was not sent or has a safe deduplication key accepted by the downstream system. This helps students see that idempotency is end-to-end. It cannot be invented by the orchestrator after a side effect leaves the system.

A third exercise is to add aging to queued work. If a queued task waits too long, should it be promoted, canceled, compacted, or revalidated? Long queues can carry stale context. A task that was safe when submitted may no longer be safe after policy, data, or business state changes. The harness should make that revalidation explicit.

A fourth exercise is to add worker attestation. Before a worker receives a lease, it might need to prove its version, policy bundle, tenant binding, and last health check. If attestation fails, the worker should not receive new work, and any active task should be checkpointed or escalated. This connects fleet coordination to supply-chain and runtime-integrity controls.

## Production Review Checklist

When reviewing a real agent fleet, ask whether every tenant has a quota and whether quota decisions are logged. Ask whether queues have hard limits and whether queue pressure changes planner behavior. Ask whether workers are isolated by tenant, data class, tool risk, or some other meaningful boundary. Ask whether a compromised worker can be quarantined without losing the evidence needed to retry or investigate. Ask whether retries carry idempotency keys accepted by downstream tools. Ask whether rate limits are enforced in the tool gateway, the model gateway, or both. Ask whether long-running work checkpoints before policy windows, credential lifetimes, and operator shifts expire.

Also ask who owns each control. Fleet coordination touches platform engineering, security engineering, application teams, model platform teams, and operations. A policy that no one owns will drift. A queue that no one watches will become an incident waiting room. A retry ledger that no downstream tool honors will give a false sense of safety. A capacity budget that only finance understands will miss operational risk. Chapter 9's miniature scenario is meant to make those ownership boundaries discussable.

The goal is not to make agents timid. The goal is to make them reliable enough to do consequential work. A production-ready harness lets agents continue after failures, but only through paths that are scoped, evidenced, rate-aware, quota-aware, checkpointed, and reversible where reversal is required. That is the difference between a demo that survives one run and a fleet that can operate through real incidents without cascading failure.
