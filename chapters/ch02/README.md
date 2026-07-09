# **Chapter 2: Autonomy: Graduated Control and Human Oversight**

Autonomy is not a single switch. A secure long-horizon agent should not move
from "human typed every instruction" directly to "agent can do anything until it
is stopped." Production systems need a ladder of autonomy levels, each tied to
the actual risk of the next action. Chapter 2 teaches that ladder through a
runnable scenario: a simulated autonomy controller triages an incident, reads a
ticket, proposes a reversible patch, attempts to exceed its budget, queues a
customer communication for review, blocks an irreversible customer-data action,
rejects a secret-access waiver, renews an expired long-running lease, and then
executes a rollback hook.

The point is not that these exact tools are special. The point is that every
agent action has a control-plane shape. A read is not the same as a reversible
write. A reversible write is not the same as a customer email. A customer email
is not the same as deleting a customer record. A privileged deployment is not
the same as querying a vault. When those actions are treated as equivalent, the
system either becomes too permissive or too frustrating to use. If everything is
allowed, the agent can make costly mistakes. If everything requires a meeting,
people route around the harness. The better pattern is graduated autonomy:
automatic for low-risk work, bounded for reversible work, supervised for
externally visible work, and blocked for controls that no reviewer may waive.

## Running the Lab

From the HarnessLab project root, run:

```bash
python -m chapters.ch02.run
```

You can also run it through the shared CLI:

```bash
python -m harnesslab.cli run ch02
```

The scenario returns a `LabResult`. Its `decisions` list shows each policy
decision made by the harness. Its `artifacts` field records the autonomy gates,
the action timeline, the approval queue, budget spend, rollback hooks, lease
events, and final control checks. The lab is deterministic and uses only the
Python standard library plus the shared `harnesslab.core` primitives.

## What Autonomy Means Here

In this chapter, autonomy means "how far the agent may proceed before another
control must participate." That control might be a hard policy denial, a
capability budget, a human approval queue, a short-lived lease, a rollback hook,
or a non-waivable boundary. The agent is still useful because the harness lets
it do work. The agent is still constrained because each step is checked against
the action's risk.

The lab uses five risk classes from the shared core:

- `read`: observe state without changing it.
- `reversible_write`: change state in a way that can be rolled back.
- `external_communication`: send information outside the immediate system.
- `irreversible_write`: make a change that cannot be cleanly undone.
- `privileged_operation`: exercise elevated authority, such as a deployment or
  vault access.

Those labels are intentionally plain. They keep the design conversation focused
on consequences. The harness does not ask whether an action "feels agentic" or
whether the model sounds confident. It asks what will happen if the action is
wrong, stale, maliciously influenced, or executed at the wrong time. That is the
right unit for autonomy design.

## The Autonomy Ladder

The scenario maps each risk class to an autonomy gate. Reads use the `observe`
gate and can run automatically when the tool, data class, and intent contract
match. The agent reads a training incident ticket because reading internal
ticket metadata does not create a side effect. This is the lowest-friction level
of autonomy. It is still policy-checked, but it does not consume scarce human
attention.

Reversible writes use the `bounded-write` gate. In the scenario, the agent
creates a repository patch that changes a bounded retry limit. The write is
allowed only because it stays inside the intent contract, uses internal data,
fits within the tool gateway registration, and has remaining capability budget.
The scenario also creates a checkpoint and registers a rollback hook. This is a
central lesson: the permission to perform reversible work should be coupled to
the ability to reverse it. If the system cannot name the rollback, it should not
pretend the action is low risk.

External communication uses the `supervised-communication` gate. The agent can
prepare a customer update, but it cannot send the message just because the model
generated confident prose. The action enters an approval queue with required
evidence: the ticket, a message preview, and owner acknowledgement. The approval
queue grants the action only after that evidence is present. This pattern lets
agents accelerate the work around a human decision without silently becoming the
decision maker for externally visible communication.

Irreversible writes use the `irreversible-change` gate. The scenario attempts to
delete a customer record. Even though the local tool is registered and the
intent contract names the action, the approval queue denies the request because
it lacks the complete evidence set: retention ticket, two-person review, and
export receipt. This demonstrates an important distinction. Some actions are not
made safe by a single click. They require a stronger approval ceremony because
they erase options. Good autonomy design preserves options wherever possible.

Privileged operations use the `privileged-operation` gate. The deployment step
is also subject to expiry and renewal because long-running agents can outlive
the context in which their authority was granted. The first deployment attempt
uses an expired contract and is denied. The renewed contract has the same scope,
requires the same evidence, and still enters an approval queue. Renewal is not a
magic expansion of power. It is a fresh check that the old authorization still
matches the current task.

## Capability Budgets

Capability budgets answer a simple operational question: even if an action is
allowed in principle, how many times should this agent be allowed to perform it
within this run? Without budgets, a small loop can become a large incident. A
coding agent might keep patching the same file. A support agent might send too
many messages. A remediation agent might repeatedly deploy a service while
trying to chase a flaky test. The mistake is not always dramatic. Sometimes the
danger is repetition.

The lab sets a budget of one `patch_repo` call and one reversible write. The
first patch is allowed. The second patch is denied with a capability-budget
decision. That denial is not a model critique. The model might have a plausible
reason for the second patch. The harness is saying that this run has consumed
the amount of mutation it was granted. If more mutation is needed, the run must
be re-scoped, renewed, or reviewed.

Budgets work best when they are close to the capability. A generic token budget
does not tell you how many customer emails were sent. A wall-clock timeout does
not tell you whether the agent deployed three times. Capability budgets should
track the actual tools and risk categories that matter for the system. The
Chapter 2 artifact includes both configured limits and spent counts so students
can inspect how the control reached its decision.

## Approval Queues

Approval queues are often implemented as a button in a product, but the button
is the least interesting part. The queue needs a request identity, a tool call,
the action risk, required evidence, reviewer identity, status, and a reason. A
good queue also distinguishes "pending" from "denied" and "approved." Pending
means the action may still become safe. Denied means the action failed a
control. Approved means the required review happened and the evidence was
present at the time of review.

The Chapter 2 queue is deliberately small, but it models that structure. The
customer email is approved because the ticket, message preview, and owner
acknowledgement are present. The customer-record deletion is denied because the
evidence is incomplete. Both actions pass through the same queue object, yet
they receive different outcomes. That is the behavior we want from a harness.
The agent should not learn that "ask a human" always means "eventually allowed."
Human review is a control, not a rubber stamp.

Approval queues also create audit material. The lab records each request in the
`approval_queue` artifact with a deterministic request id, tool name, risk,
required evidence, waiver flag, status, reviewer, and reason. In a production
system, this record would feed audit logs, incident reconstruction, and
post-deployment review. In a classroom lab, it gives students something concrete
to inspect rather than a vague claim that review happened.

## Non-Waivable Controls

Some controls must not be bypassable by an ordinary approval. If a system lets a
reviewer waive every boundary, then the real policy is "whoever finds the button
can do anything." That is not graduated autonomy. That is hidden root access.

The scenario demonstrates this with a vault query. The agent requests a
production secret and marks the request as if it wants a waiver. The harness
blocks the action with a non-waivable secret-boundary decision. The point is not
that secrets can never be read by any system. The point is that this chapter's
autonomy controller and approval queue are not the right authority for that
operation. A vault control might require a break-glass workflow, separate
identity, just-in-time access, hardware-backed approval, or an incident command
record. The Chapter 2 queue cannot simply wave it through.

Non-waivable controls should be rare and explicit. If every rule is
non-waivable, operators lose the ability to respond to real-world complexity. If
no rule is non-waivable, the harness has no spine. Good candidates include
secret exfiltration boundaries, regulated data residency, tenant isolation,
destructive production operations, and actions that would violate law or
contract. The key is to name which controls are non-waivable and to make the
denial visible in the decision record.

## Reversible and Irreversible Actions

Reversibility is one of the most useful design levers in agent systems. If a
write can be reversed quickly and reliably, the harness can grant more autonomy
without accepting the same level of permanent risk. If a write cannot be
reversed, the harness should demand stronger evidence, stronger approval, or a
different plan.

In the lab, `patch_repo` is a reversible write. The harness creates a checkpoint
before spending the budget, then registers a rollback hook. Later, the scenario
executes that hook and records the execution in artifacts. This does not mean
every repository patch is harmless. A patch can still be dangerous. It means the
system has a concrete path back to the previous state, so it can treat the
action differently from deletion or external disclosure.

The customer-record deletion is different. It is modeled as an irreversible
write over PII. The queue requires a retention ticket, two-person review, and an
export receipt. The simulated request only supplies a retention ticket, so the
queue denies it. That denial teaches the agent and the operator the same lesson:
if the system cannot recover the previous state, the preconditions must be
stronger.

Reversibility should be tested, not assumed. A rollback hook that nobody can
execute is documentation, not a control. A checkpoint that omits the important
state is a false comfort. A database restore that takes six hours may be
insufficient for a high-speed agent loop. This chapter's hook is simple because
the lab is small, but the pattern scales: register the rollback when the action
is allowed, keep its identity in the run artifact, and exercise it when the
scenario calls for recovery.

## Expiry and Renewal

Long-running agents create a special autonomy problem. The user may approve a
task at 9:00, but by 11:00 the repository, incident, customer state, or policy
may have changed. A credential may still be technically valid while the reason
for using it is no longer valid. A harness should treat time as part of
authorization.

The lab models this through an expired intent contract. The first deployment
attempt is denied because the contract has expired. The scenario then creates a
renewed contract with the same tool, data, risk, and evidence scope. The
deployment still does not run automatically. It goes through the privileged
operation gate and receives approval only after test log, change ticket, and
lease renewal evidence are present.

This is an important nuance. Renewal is not escalation. Renewal should normally
preserve or narrow scope. If the agent needs more authority than it had before,
that is not a renewal; it is a new authorization. Keeping this distinction clear
helps prevent long-running agents from accumulating power as they encounter
friction. A good renewal flow asks: is the actor the same, is the task still the
same, is the data class still allowed, has the risk changed, what evidence is
fresh, and when will this renewed lease expire?

## Reading the Result

The `LabResult` contains several useful artifacts:

- `autonomy_gates` shows how risk maps to autonomy mode.
- `timeline` shows the scenario steps and outcomes.
- `approval_queue` shows requests, reviewers, evidence requirements, and
  statuses.
- `capability_budgets` shows limits and spend.
- `rollback_hooks` shows the registered hook and whether it executed.
- `lease_events` explains the expired and renewed long-running run.
- `control_checks` summarizes whether each teaching objective passed.

The decisions list is also worth reading. It includes allow, deny, and escalate
decisions. A secure harness should not treat denials as failures of the lab. In
this scenario, denials are expected outcomes. The budget denial, irreversible
delete denial, secret-boundary denial, and expired-lease denial are all signs
that the controls are working. The lab passes because the right actions are
allowed and the unsafe or under-evidenced actions are blocked or escalated.

## Design Questions for Students

When adapting this pattern to a real system, ask practical questions before
arguing about model behavior. Which tools are read-only? Which writes are truly
reversible? What rollback evidence is required? Which actions expose customers,
tenants, regulators, or production infrastructure? How many times can the agent
use each capability before review? Who can approve each risk class? Which
controls cannot be waived by that approver? How long does a run keep its
authority? What happens when the run expires mid-task? Where is the evidence
stored?

These questions produce implementable controls. They also make autonomy less
mysterious. Instead of debating whether an AI system is "autonomous," the team
can describe what it may do at each risk level. That description becomes a
contract between product, engineering, security, legal, and operations.

## Production Takeaways

Graduated autonomy is a design pattern for preserving agency without preserving
chaos. Let agents do the parts they are good at: gather context, prepare
changes, assemble evidence, draft communications, and propose actions. Then use
the harness to decide how far each action may proceed. Keep low-risk work fast.
Keep reversible work bounded. Keep external and privileged work supervised. Keep
irreversible work evidence-heavy. Keep non-waivable boundaries explicit. Keep
long-running authority short-lived and renewable only through fresh checks.

The Chapter 2 scenario is intentionally small, but it captures the core
production posture: autonomy is granted in slices, measured through budgets,
paused at approval queues, constrained by hard controls, refreshed by lease
renewal, and made safer by rollback hooks. That is the foundation needed before
later chapters add identity, intent, context, memory, observability, runtime
steering, fleet controls, and governance.
