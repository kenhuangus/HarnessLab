# Chapter 7: Observability

Observability is the part of the secure harness that lets people understand
what a long-running agent did, why it did it, what evidence supported the
decision, and whether a later change made the system safer or less safe. In a
normal application, observability often means logs, metrics, traces, and
dashboards. Those tools still matter for agentic systems, but they are not
enough by themselves. A long-horizon agent can call tools, delegate work, read
memory, update state, summarize its own behavior, retry failed plans, and propose
changes to the harness that governs it. If the harness only records generic
request logs, the important security question is lost: did the system preserve a
verifiable chain from intent to action to evidence to outcome?

This lab teaches observability as a control plane, not as an afterthought. The
scenario is intentionally small and dependency-free, but it models a production
shape. A risky customer notification is observed. The evidence stream contains
PII and a token-like string, so the harness rewrites the evidence before it can
enter the trace store. The lab then seals a tamper-evident evidence envelope,
computes artifact hashes, builds a replay bundle, detects a benchmark
regression, runs a hill-climbing evaluation loop, and blocks an ungoverned
recursive self-improvement proposal while allowing a bounded governed rollout.
Each step returns deterministic data so students can run the chapter repeatedly
and compare output without chasing timing differences.

## Running the Lab

From the HarnessLab project root, run:

```bash
python -m chapters.ch07.run
```

You can also run the chapter through the shared CLI:

```bash
python -m harnesslab.cli run ch07 --json
```

The public scenario entry point is:

```python
from chapters.ch07.scenario import run

result = run()
assert result.passed
print(result.to_json())
```

The returned `LabResult` contains policy decisions and artifacts. The decisions
show the control outcomes: allow, rewrite, escalate, deny, and allow again for a
bounded rollout. The artifacts show the evidence that explains those outcomes:
redacted observations, decision traces, serialized spans, benchmark regression
evidence, a hill-climbing loop, a governed recursive self-improvement record, a
replay bundle, artifact hashes, and an evidence envelope.

## The Core Idea

The core idea of Chapter 7 is that an agent harness needs evidence that is
useful both during the run and after the run. During the run, the harness needs
enough signal to interrupt unsafe behavior, spot drift, and keep the operator
orchestrating from facts instead of vibes. After the run, the harness needs an
audit record that can answer harder questions: which policy decided this, which
input caused it, which artifact was reviewed, which regression gate failed, and
whether the same outcome can be replayed later.

This is different from asking the agent to write a narrative explanation at the
end. End-of-run summaries are useful, but they are not a security boundary. A
summary can omit the exact decision that mattered, can be influenced by later
context, can contain sensitive data, and can fail to identify which benchmark
changed. The harness needs structured evidence at the time decisions happen.
That evidence should be scoped, redacted, hashed, and replayable.

In this lab, the action being observed is a customer notification. The raw
observation includes a customer email and a token-like string in the draft. A
naive trace system might record both values. That would create a new data leak:
the tool call might have been safe, but the logging pipeline would now contain
PII and possible secret material. The lab demonstrates a safer pattern. Evidence
is rewritten before emission. The returned artifacts include a redacted
observation and a hash of the raw observation, but they do not expose the raw
email or the raw token string.

## Decision Traces

A decision trace is a structured record of the important control decisions made
during a run. It is not merely a list of log messages. Each entry should identify
the step, the decision, the reason, and the evidence that supports the decision.
For agent systems, this is especially important because the same external action
can be safe or unsafe depending on the intent, data class, tool, autonomy level,
and state of the run.

The Chapter 7 decision trace includes six steps. First, the harness observes the
tool call and records the fact that a customer notification was attempted.
Second, it rewrites evidence because sensitive fields were present. Third, it
escalates benchmark regression evidence because one candidate reduced safety and
replay metrics. Fourth, it allows a safe hill-climbing improvement. Fifth, it
denies an ungoverned recursive self-improvement attempt. Sixth, it allows a
bounded rollout because the second proposal includes evidence, rollback, and
approval controls.

The important teaching point is that these decisions do not all have the same
shape. A secure harness should not treat every non-allow as a failure. `REWRITE`
is the correct outcome when the system can make an artifact safe without
changing the user's core goal. `ESCALATE` is the correct outcome when evidence
shows a meaningful risk that a reviewer should examine. `DENY` is the correct
outcome when a proposed action would change the harness without the controls
required for self-improvement. Observability should make these distinctions
clear instead of flattening everything into "success" or "error."

## Evidence Envelopes

An evidence envelope is a bundle of metadata that makes a run easier to audit.
In this lab, the envelope contains the run id, actor, policy version, trace
spans, artifact hashes, redaction markers, and a deterministic creation time.
The envelope can produce a tamper-evident hash. In a production system, the same
idea could be backed by an append-only log, object storage with retention
controls, a transparency log, or a signed audit store. The exact backing system
can vary. The shape of the evidence should not.

The envelope answers several questions at once. Which policy version was active?
Which actor emitted the trace? Which artifacts were part of the run? Were any
redactions applied? Can the current artifact set be compared with the recorded
hashes? If a later report claims that the run selected a different candidate,
the envelope and replay bundle give reviewers a concrete way to compare claims
against recorded evidence.

The lab deliberately uses stable data so the evidence hash remains predictable.
Real systems usually include real timestamps. That is appropriate in production,
but it makes classroom tests noisy. HarnessLab keeps the teaching artifact
deterministic so learners can focus on the control design.

## Artifact Hashes

Artifact hashes are the glue between a trace and the evidence it describes. A
trace event might say "benchmark regression detected," but without a hash or
reference to the benchmark report, a reviewer cannot know which report was
actually used. The lab computes SHA-256 hashes for the redacted observation,
decision trace, trace spans, benchmark regression report, hill-climbing loop,
governed self-improvement record, and replay bundle.

Hashes do not replace access control or retention policy. A hash of sensitive
data can still reveal information if the input is guessable, and storing raw
artifacts requires careful classification. In this lab, the raw observation is
not returned. The replay bundle stores a hash of the raw observation and the
redacted observation that is safe to inspect. This pattern lets the harness
prove that it saw a specific input without turning the lab output into another
copy of sensitive data.

Production systems should connect artifact hashes to storage policy. Public or
internal artifacts might be stored in ordinary trace infrastructure. PII,
regulated data, and secrets should move through stricter pipelines. Some
artifacts should expire quickly. Some should be retained for audit. Some should
be represented only by a digest and a reference to a governed storage location.
The chapter keeps the implementation small, but the artifact list is meant to
train that instinct.

## Redaction

Redaction in this lab happens before evidence emission. The scenario detects
sensitive fields by key, such as `customer_email`, and token-like strings by
pattern. It replaces those values with placeholders and records which redaction
rules fired. That record matters. If a trace says it was redacted but never says
how, reviewers cannot distinguish effective redaction from wishful thinking.

The redaction model is intentionally conservative. It does not claim to solve
data loss prevention. It demonstrates the control point: evidence pipelines need
classification-aware rewriting before logs, traces, eval stores, and replay
bundles receive data. Agent systems create many tempting places to store
observations. The model may want to remember a detail. The evaluator may want to
index a failure case. The orchestrator may want to attach the tool arguments to
a trace. Each of those moves can accidentally duplicate sensitive data. A secure
harness makes redaction a first-class step.

The lab's success condition verifies that the redacted artifact does not contain
the example email or token-like string. It also verifies that redactions were
recorded and that artifact hashes still match after the rewrite.

## Replay Bundles

A replay bundle is a compact package that lets a reviewer or test runner repeat
the important parts of a run. In this lab, the replay bundle contains a schema
name, run id, policy version, the hash of the raw input, the redacted input, the
trace, the expected decision trace, the expected regression verdict, and the
expected selected candidate. The bundle is not a full simulator. It is the
minimum evidence needed to ask, "If we load this case again, do we reach the
same policy conclusions?"

Replay is essential for long-running agents because failures often depend on
state. A single prompt or tool call may not reproduce the issue. The harness
needs to preserve enough information to rebuild the relevant state without
capturing everything the agent ever saw. The right replay boundary depends on
the system. For some teams, it may include tool fixtures and memory snapshots.
For others, it may include policy versions, eval data ids, and artifact hashes.
The lesson is to design replay as an explicit artifact, not as an emergency
forensics project after a failure.

Replay bundles also support regression tests. Once a risky case has been found,
it should become a fixture. A future harness change should prove that it still
handles the case safely. If an optimization breaks replay coverage or changes a
decision from deny to allow, the benchmark should make that visible before the
change ships.

## Benchmark Regression Evidence

The scenario includes a candidate called `aggressive_trace_sampling`. It lowers
latency and increases task success, which looks attractive if the harness is
optimized only for throughput. But the candidate also reduces unsafe-block rate,
redaction recall, and replay pass rate. Those are safety and audit metrics, so
the lab marks the candidate as a regression and escalates it.

This is a key lesson for hill-climbing systems. Optimization pressure is not
neutral. If the reward function only values speed or short-term task success,
the system will eventually find changes that make the harness less observable.
It may sample away the traces needed to diagnose incidents. It may skip
redaction checks to reduce latency. It may weaken replay fidelity because replay
does not matter to the immediate task. Those changes can look like improvements
until the organization needs to investigate a failure.

Good benchmark evidence names the baseline, names the candidate, lists the
deltas, and identifies failed gates. The lab returns that shape directly. A
reviewer can see not only that escalation happened, but why it happened. The
decision is tied to evidence rather than taste.

## Hill-Climbing Eval Loops

Hill climbing is the process of trying bounded changes, measuring them, keeping
the improvements, and rejecting regressions. Agent harnesses need hill climbing
because static controls decay. New tools appear, new workflows become common,
attackers adapt, and operators learn where the harness is too strict or too
loose. The question is not whether the system should improve. The question is
whether improvement is governed by evidence.

The lab models a small loop with three candidate changes. One candidate adds
decision-reason capture to each trace. One candidate samples traces aggressively
to reduce latency. One candidate redacts before indexing evidence. Each
candidate receives metrics and a composite score. The loop only accepts a
candidate if it improves the score and does not fail safety gates. This means
the fast but unsafe sampling change is rejected even though it improves latency
and task success. The selected candidate is `redact_before_indexing`, because it
improves the composite score without reducing unsafe-block rate, redaction
recall, or replay pass rate.

In production, the metric set should be broader. Teams might track escalation
precision, false-deny rate, human review burden, incident investigation time,
cost per run, policy drift, memory rollback success, and data residency
violations. The exact metric set should reflect the system's risk. The invariant
is that safety gates must be gates, not soft preferences hidden inside a single
score.

## Governed Recursive Self-Improvement

Recursive self-improvement means the agent or harness proposes changes to the
system that will affect future agent behavior. This can be valuable. An agent
may discover that a redaction rule should fire earlier, that an eval fixture
should be added, or that a policy needs a clearer threshold. But recursive
self-improvement is also dangerous. If an optimizer can change its own
evaluation weights, suppress failing replay cases, or weaken evidence capture,
the harness can appear to improve while losing the controls that made it safe.

The lab includes two proposals. The first tries to raise the task-success weight
and ignore replay failures. It lacks an evidence hash, rollback checkpoint, and
human approval, so the harness denies it. The second promotes
redaction-before-indexing after the safe hill-climbing loop. It includes an
evidence hash, rollback checkpoint, bounded rollout status, and approval
controls, so the harness allows it as a supervised rollout.

The point is not that every improvement needs a heavyweight committee. The point
is that self-modification requires a higher evidence standard than ordinary task
execution. At minimum, a governed proposal should state the change, attach the
eval evidence, identify failed and passed gates, define a rollback path, limit
the blast radius, and create a human-readable approval trail.

## Long-Running Agent Considerations

Long-running agents make observability harder because their important behavior
is distributed over time. A risk may begin as a harmless memory write, become a
tool choice several steps later, and only become visible after an external
communication. A trace that captures only the final tool call will miss the
chain. A trace that captures everything may leak data or become impossible to
review. The harness has to balance completeness, privacy, and cost.

For long-running systems, observability should include checkpoint references,
policy versions, memory and context provenance, tool-call decisions, eval
fixtures created from incidents, and explicit links between interventions and
outcomes. If a run is paused or resumed, the evidence should say where the state
came from. If an operator injects a temporary policy overlay, traces should show
the overlay and its expiration. If a sub-agent performs work, traces should
connect the delegated action back to the parent intent and actor.

The Chapter 7 scenario does not run for hours, but it models these long-running
needs. The replay bundle preserves the state needed to re-check the case. The
evidence envelope binds artifacts to a policy version. The governed improvement
record includes rollback. The benchmark regression report makes optimization
tradeoffs visible before they silently reshape future runs.

## What to Look For

When you inspect the JSON output, look for a few things. The `decisions` array
should include a rewrite for redaction, an escalation for benchmark regression,
a denial for ungoverned recursive self-improvement, and an allow for the bounded
rollout. The `artifacts.redacted_observation` object should not contain the raw
email or token-like string. The `artifacts.artifact_hashes` object should include
hashes for every major evidence artifact. The `artifacts.evidence_envelope`
should include the same artifact hashes and a tamper-evident hash. The
`artifacts.replay_bundle` should contain enough structured data to reproduce the
expected decisions. The `artifacts.hill_climb.selected.candidate` should be
`redact_before_indexing`.

This is the mindset to carry into production designs. Observability is not just
what the system prints. It is the governed evidence path that lets teams
understand, replay, compare, improve, and constrain autonomous behavior over
time.

