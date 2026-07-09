# **Chapter 5: Context: Trust Tiers, Provenance, and Poisoning Containment**

Context is the part of an agent system that feels deceptively harmless. It is
"just information" until it changes what the agent believes, which tools it
uses, which records it carries forward, and which external destination receives
the result. Chapter 5 teaches that context needs its own control plane. The
right question is not only "what text should the model see?" The better
question is "which classified, provenance-bound, freshness-checked context is
safe to release into this step of this run?"

This lab is a small, deterministic version of that control plane. It does not
call a model, a browser, a vector database, or a network service. Instead it
models the security decisions that must happen before any of those systems feed
an agent. The executable scenario creates a set of candidate context items from
system policy, tenant configuration, a user ticket, trusted tools, prior memory,
and untrusted browser content. The chapter then chooses a governed context
profile, inspects every item, releases only the fresh trusted subset, isolates
external content, persists quarantine evidence, blocks a lethal-trifecta egress
attempt, and checkpoints the long-running agent before continuing.

Run it with:

```bash
python -m chapters.ch05.run
python -m harnesslab.cli run ch05 --json
```

The result is a `LabResult`, so the same scenario works through the direct
chapter module and through the public HarnessLab CLI.

## The Problem This Chapter Teaches

Long-horizon agents do not operate on one prompt. They accumulate context over
time. A support agent might start with system instructions, tenant policy, a
ticket body, a CRM profile, runbook snippets, browser research, trace results,
messages from subagents, and memory from earlier shifts. Each piece may be
useful, but each piece has a different authority. A system policy is not the
same kind of input as a customer comment. A trusted SIEM query is not the same
as a pasted web page. A previous run's memory is not the same as a freshly
approved tenant profile.

Without a context control plane, the agent tends to flatten all of this into
one text window. Flattening destroys the security boundary. Once untrusted text
sits beside trusted instructions, a model may treat both as equally important
language. Once stale memory sits beside fresh evidence, a model may keep using
the old rule because it is convenient and familiar. Once a malicious external
page is summarized into memory, the attack can survive the original page and
return later as "what the agent remembers."

The lab focuses on seven controls that prevent that collapse: trust tiers,
provenance, untrusted-content isolation, lethal-trifecta defense, context
compaction, freshness checks, quarantine persistence, and governed profile
choice. These controls are intentionally boring in the best way. They are
ordinary engineering gates, not magic prompts. The agent does not need to be
asked nicely to ignore hostile content. The harness decides whether the content
is eligible for release.

## Trust Tiers

A trust tier is an authority label. In this repository the core framework
defines tiers such as `system`, `tenant`, `trusted_tool`, `user`, `external`,
and `quarantined`. The tier does not claim that a piece of text is true. It
answers a narrower question: who or what is allowed to influence the agent at
this point?

In the scenario, system policy and tenant policy are high-authority inputs.
Trusted tool output from an approved SIEM query is useful operational evidence.
The user's support ticket is important, but it is not allowed to rewrite policy.
Browser pages and uploads are external. They may be informative, but they are
not allowed to sit in the same lane as system, tenant, or trusted tool context
for a customer-impacting PII workflow.

The point is not to distrust users or the web as a blanket rule. The point is
to preserve the difference between "this is data the agent should consider" and
"this is instruction authority." Production systems often lose that distinction
when they perform retrieval, summarization, or memory writes. Chapter 5 keeps
the distinction explicit in the artifact: every context item has a declared
tier, an effective tier after inspection, a data class, and a provenance string.

## Provenance

Provenance is the evidence trail for context. A context item without provenance
is hard to debug and hard to govern. If an agent recommends the wrong action,
the team needs to know whether the bad input came from a tenant profile, a
stale memory record, a browser page, or a trusted tool. If a quarantine event is
reviewed later, the security team needs enough metadata to identify the source
without rereleasing the unsafe text.

The scenario gives every item a provenance string such as
`tenant:acme/security-profile/v3`, `crm:ticket/INC-4242#comment-1`, or
`web:paste.example/comment-77#untrusted`. Released context keeps this
provenance. Quarantined context stores provenance plus a hash of the unsafe
text. The hash lets the harness prove that the same content was seen again
without copying the hostile instructions back into the live prompt or artifact.

Good provenance also makes compaction safer. When the context window is too
large, the harness can drop lower-priority items while keeping a summary that
names the released context IDs and their sources. That is different from asking
a model to create a loose narrative summary. A model summary can accidentally
launder external instructions into trusted memory. A harness summary should
preserve metadata and avoid promoting untrusted text.

## Untrusted-Content Isolation

Isolation is the difference between "not released" and "forgotten." The lab
includes a clean public browser page and a hostile public browser page. The
clean page is external, so the high-assurance profile isolates it even though
the content itself does not trigger injection findings. The hostile page is
quarantined because it contains direct instruction-injection markers and a
lethal-trifecta pattern.

Both outcomes matter. Clean external content may be useful in a different
profile, such as low-risk public research, but it should not influence a PII
support workflow unless a policy explicitly permits that flow. Hostile external
content should be retained for evidence and later review, but it should not be
released into the agent's live context.

This is a practical pattern for browser-enabled agents. Browser content should
arrive in an untrusted lane. The harness may summarize, cite, or transform it
under strict rules, but the raw page should not gain authority merely because a
tool fetched it. If the page says "ignore previous instructions," that phrase
is data about the page, not an instruction to the agent.

## Lethal-Trifecta Defense

The lethal trifecta is the combination of private data, tool capability, and an
external sink. Any one of these can be legitimate. A support agent may need
private ticket data. It may need a tool. It may need to communicate externally.
The danger appears when untrusted context steers the agent to combine all three
in one unsafe move.

The scenario includes an external page that tells the agent to use a tool to
send private ticket material to an external webhook. The core `ContextFirewall`
detects the pattern because the text combines private data, a tool, and an
external destination. The item is moved to the quarantined tier and persisted in
the quarantine ledger. The scenario then models a tool call to
`send_customer_email`. The tool gateway recognizes that the tool is registered
for external communication with PII, so the gateway alone does not save the
system. The data governance route blocks the destination because
`personal-webhook` is not on the egress allowlist.

That layered result is important. Tool registration, context inspection, and
data governance are separate controls. A production harness should not assume
that one gate catches every misuse. The context firewall catches hostile
instructions before release. The tool gateway checks that a declared tool call
matches its registered risk. The data governance engine checks destination and
residency rules at egress time. Defense in depth is what turns a clever prompt
attack into a denied route.

## Context Compaction For Long-Running Agents

Long-running agents need compaction because the working set grows. The wrong
kind of compaction is dangerous. If the agent asks the model to "summarize
everything so far," untrusted content, stale memory, and trusted evidence can
be blended into a single paragraph. That paragraph may then be stored as memory
with a higher apparent authority than the original source.

The lab handles compaction as a deterministic admission step. First, each item
is inspected and classified. Next, stale items are excluded. Then the remaining
fresh candidates are ranked by the selected profile's tier priority and
recency. The high-assurance profile has a live context budget of four items.
The scenario has five fresh trusted candidates, so the older trusted runbook is
compacted out. The released window keeps system policy, tenant profile, the
user ticket, and the recent trusted trace.

The compaction artifact does not invent a new policy. It records the released
IDs, the compacted-out IDs, and a compact summary that retains provenance. This
teaches a useful rule: compaction should reduce working-set size without
changing authority. Dropping a lower-priority item is acceptable when the
policy says so. Promoting an external page into trusted memory because it was
mentioned in a summary is not acceptable.

## Freshness

Freshness is a context property, not a model preference. The scenario includes
a stale memory item from a previous agent shift that says the tenant allowed
webhook export. The current tenant profile says personal webhooks are
forbidden. The stale item is from a trusted tool tier, but trust tier alone is
not enough. It falls outside the selected profile's freshness window and is
excluded with a warning decision.

This matters for long-running work. Agents may pause overnight, resume after a
policy update, or inherit state from another worker. The context that was safe
at 9:00 may be wrong at 17:00. A production harness should make continuation a
checkpointed event: revalidate policy, check freshness, and only then resume.
The chapter uses `RuntimeController` to checkpoint the released context and
quarantine record IDs, pause the run after stale context is found, and resume
from the checkpointed state. The checkpoint does not mean "the model remembers
everything." It means the harness has a controlled state boundary.

## Quarantine Persistence

Quarantine should persist because unsafe content is evidence. If the system
simply drops hostile input, defenders lose the ability to understand repeated
attacks, tune detectors, or explain why an agent refused a path. If the system
stores the hostile text directly in live memory, the attack may return later.
The safe middle path is a quarantine ledger.

The scenario's ledger stores record ID, context ID, source, provenance,
declared tier, effective tier, data class, disposition, reason, findings, and a
text hash. It does not release the raw hostile content into the live context
artifact. It also writes a `context_quarantine_index` memory record from the
system tier, containing only the quarantine record IDs. A separate poisoned
memory write from an external source is denied. That contrast is the lesson:
persist evidence under harness authority, but do not let untrusted content
write future behavior.

Quarantine persistence is also useful for audit. In a classroom, students can
inspect the `quarantine_ledger` artifact and see exactly which control fired.
In production, the same shape can feed security review, incident response, or
policy tuning. The record is not just "blocked." It explains what was blocked,
where it came from, and which findings justified the decision.

## Governed Profile Choices

Different tasks need different context profiles. A public research agent might
be allowed to read external web pages. A customer-support agent handling PII
should be stricter. A code-repair agent might accept repository files and CI
logs but isolate chat messages from unknown users. Profile choice is itself a
governance decision.

This scenario defines two profiles. `fast_research_context` allows external
public context and has a larger freshness window. It is useful for low-risk
research. `high_assurance_context` excludes external tiers, permits PII under
trusted workflow rules, uses a shorter freshness window, and has a smaller live
context budget. Because the candidate set includes both sensitive PII and
external content, the fast profile is denied and the high-assurance profile is
selected.

The important design point is that the agent does not choose the looser profile
because it wants more information. The harness chooses the profile based on the
task's data classes, trust tiers, and egress shape. A production system can add
more profiles, but the selection rule should remain explicit and auditable.

## Reading The Result

The JSON result contains several high-signal sections. `profile` shows the
selected profile and the rejected alternative. `inspected_context` shows each
candidate item's declared tier, effective tier, data class, age, admission
result, and findings. `released_context` shows the small set that reached the
agent. `compaction` shows the live context budget, the released IDs, the
compacted-out IDs, and a provenance-preserving summary. `quarantine_ledger`
shows isolated and quarantined records with hashes. `memory` shows that the
quarantine index was stored but the poisoned profile write was denied.
`lethal_trifecta` shows the layered defense: the gateway accepted the registered
tool shape, but data governance denied the unapproved destination. `runtime`
shows the checkpoint and pause/resume behavior used for the long-running agent.

The scenario passes only if all expected controls fire: high-assurance profile
selection, release of exactly the intended fresh trusted context, exclusion of
stale memory, compaction of the older trusted runbook, quarantine of the hostile
external page, isolation of the clean external page, persistence of quarantine
records, denial of poisoned memory, denial of unapproved egress, and
checkpointed runtime continuation.

## Applying The Pattern

Use this chapter as a template for real systems that retrieve or accumulate
context. Put every context item in a typed envelope before the model sees it.
Track source, provenance, data class, trust tier, and creation time. Choose a
profile based on the task, not on the agent's preference. Inspect untrusted
content before release. Keep external text in an isolated lane unless a policy
explicitly allows it. Treat compaction as a policy operation, not a free-form
summary request. Recheck freshness whenever a long-running agent resumes. Store
quarantine evidence in a ledger, but never let hostile content become trusted
memory.

The deeper lesson is simple: context is not neutral. It is part of the control
surface of a long-horizon agent. Secure systems do not merely ask models to be
careful with context. They govern context before it can govern the model.
