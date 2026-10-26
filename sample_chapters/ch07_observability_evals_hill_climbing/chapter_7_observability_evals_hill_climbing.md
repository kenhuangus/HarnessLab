# **Chapter 7: Observability, Evals, and Hill-Climbing Evidence**

## Editorial Reasoning for Selecting This as the Sample Chapter

This is the strongest sample chapter for the book because it proves the central claim of **Harness Engineering: Design Patterns for Securing Long-Horizon Multi-Agent AI Systems** in one place. A secure harness is not only a policy layer that says yes or no to a tool call. It is the engineering system that lets an organization see what an agent did, decide whether that behavior was safe, learn from failures, and improve the harness without losing control of the system being improved. Chapter 7 sits at the hinge between the first half of the book, which introduces autonomy, identity, intent, context, and memory, and the final chapters, which address runtime steering, fleet scale, and governance. If the observability chapter is convincing, the whole book becomes easier for a reader to believe.

The chapter is also the best sales sample because it connects academic research, production practice, and the companion lab code in a way that is immediately useful to practitioners and credible to academic reviewers. Research on ReAct, Reflexion, and Self-Refine shows that agents improve through trajectories, feedback, and iterative refinement rather than through one-shot prompting alone (Yao et al. 2022; Shinn et al. 2023; Madaan et al. 2023). Industry practice is converging on the same lesson: agent platforms now expose traces, tool-call telemetry, guardrails, evals, human feedback, and improvement loops as first-class features rather than optional debugging aids (OpenAI 2026a; Google Cloud 2026; NVIDIA 2026a; LangChain 2026a). Security and governance frameworks add the missing constraint: observation must itself be secure, because traces can leak secrets, preserve poisoned context, or justify unsafe optimization if the wrong metrics become the reward (Huang 2025; NVIDIA 2026b; NIST 2024).

For a university press proposal, this chapter demonstrates that the book is not merely cataloging agent-security threats. It offers an engineering pattern language. The reader learns a reusable pattern: turn traces into evidence, evidence into evals, evals into governed hill climbing, and hill climbing into bounded change. That pattern is durable even as vendors, model names, benchmarks, and agent frameworks change.

## Abstract

Long-horizon agents do not fail like ordinary request-response software. They plan, call tools, delegate work, carry context forward, write memory, pause, resume, and revise their own approach. The observability harness therefore has a broader job than collecting logs and dashboards. It must preserve an evidence chain from intent to action, from action to policy decision, from policy decision to artifact, and from artifact to future improvement. This chapter treats observability as a security control plane for multi-agent systems. It introduces decision traces, evidence envelopes, redaction-before-emission, replay bundles, eval fixtures, regression gates, and governed recursive self-improvement. Drawing on current research in agent trajectories and self-refinement, and on best practices from OpenAI, Anthropic, Google, NVIDIA, LangChain, Alibaba, OpenTelemetry, NIST, and CSA MAESTRO, the chapter shows how teams can use traces and evals to make hill climbing falsifiable rather than impressionistic. The accompanying HarnessLab scenario demonstrates a risky customer-notification run in which the harness rewrites sensitive telemetry, seals artifact hashes, detects a benchmark regression, accepts a safe eval-driven improvement, blocks an ungoverned self-improvement attempt, and allows a bounded rollout with rollback controls.

## Chapter Outline

1. **Why Agent Observability Is Different**

   Observability for long-horizon agents must explain decisions, state transitions, delegated actions, eval outcomes, and improvement pressure, not merely uptime.

2. **From Reasoning Traces to Evidence Traces**

   Research on ReAct, Reflexion, Self-Refine, and related agent methods shows why trajectories matter, but production systems need traces that are structured, redacted, replayable, and policy-bound.

3. **The Observability Spine of the Secure Harness**

   A secure harness connects intent contracts, agent actions, tool calls, policy decisions, traces, evals, and evidence envelopes into a single auditable path.

4. **Decision Traces and Evidence Envelopes**

   Decision traces record control outcomes such as allow, rewrite, escalate, deny, and rollback. Evidence envelopes bind spans, artifacts, policy versions, redaction markers, and tamper-evident hashes.

5. **Privacy-Safe Telemetry**

   Logs and traces can become a new data-exfiltration path. Agent observability must classify, redact, hash, route, and retain telemetry according to data-governance rules.

6. **Evals as Executable Risk Controls**

   Evals are not only model-quality tests. In a harness, they become regression gates over task success, unsafe-block rate, redaction recall, replay fidelity, latency, cost, and operator burden.

7. **Hill Climbing Without Losing the Harness**

   Harness improvement should be treated as controlled local search over prompts, tool contracts, middleware, memory rules, routing, and policy. A change is an improvement only when evidence shows that it improves the target metric without weakening safety gates.

8. **Recursive Self-Improvement as a Governed Change Process**

   Agents may propose improvements to the harness that governs them. Those proposals need stronger controls than ordinary tool actions: evidence hashes, rollback checkpoints, bounded rollout, and human or policy approval.

9. **Benchmarks and Their Limits**

   Benchmarks such as AgentBench, τ-bench, SWE-bench, and Terminal-Bench reveal agent capability and harness quality, but they must be interpreted through trace evidence and regression gates rather than as single leaderboard numbers.

10. **HarnessLab Walkthrough**

    The chapter closes with the companion lab implementation, explaining how the deterministic scenario models redaction, evidence sealing, replay, regression detection, hill climbing, and governed rollout.

## Figures

Figure 7.1: [Secure Harness Observability Spine](figures/figure_7_1_observability_spine.excalidraw)  
Figure 7.2: [Evidence Envelope and Artifact Hashes](figures/figure_7_2_evidence_envelope.excalidraw)  
Figure 7.3: [Trace to Eval to Improvement Loop](figures/figure_7_3_trace_eval_loop.excalidraw)  
Figure 7.4: [Long-Horizon Trace Continuity Across Pause and Resume](figures/figure_7_4_long_horizon_trace.excalidraw)  
Figure 7.5: [Benchmark Regression Gate Matrix](figures/figure_7_5_benchmark_gate_matrix.excalidraw)  
Figure 7.6: [Privacy-Safe Telemetry Pipeline](figures/figure_7_6_privacy_safe_telemetry.excalidraw)  
Figure 7.7: [Recursive Self-Improvement Governance Flow](figures/figure_7_7_recursive_improvement_governance.excalidraw)  
Figure 7.8: [MAESTRO-Informed Observability Map](figures/figure_7_8_maestro_observability_map.excalidraw)

## 7.1 Why Agent Observability Is Different

The first generation of software observability was built around services. A service received a request, called dependencies, emitted logs, produced metrics, and returned a response. A good operations team wanted to know whether the service was up, whether latency had changed, whether errors had increased, and which dependency was responsible for a failure. Distributed tracing added a useful causal view: a request could be followed across services, spans, databases, queues, and network calls. That model remains necessary for agent systems. It is no longer sufficient.

A long-horizon agent is not just a service endpoint. It is an actor inside a mediated environment. It may decide which tools to call, read documents, summarize context, spawn subagents, update memory, ask for approval, retry a failed plan, change its own prompt, or propose a modification to the harness itself. The important question is not only whether the HTTP request succeeded. The important question is whether the agent had the right authority, acted under the right intent, used trustworthy context, preserved the right evidence, respected data boundaries, and improved in a way that did not damage the controls that made it safe.

This shift changes the role of observability. Observability becomes a security property. A system that cannot explain what an agent did is a system that cannot enforce accountability. A system that records everything without classification is a system that may leak the same secrets the harness was supposed to protect. A system that measures only task success may optimize away the very traces needed to investigate the next incident. A system that accepts self-improvement without replayable evidence may mistake local progress for safe progress. The observability harness must therefore be designed as part of the control plane.

Google Cloud’s current agent-observability guidance captures the operational problem directly: AI agents can drift, hallucinate, regress silently, make unexpected decisions, and fail in ways that differ from conventional software (Google Cloud 2026). OpenAI’s Agents SDK tracing documentation takes a concrete implementation view, noting that traces can capture an end-to-end run, LLM generations, tool calls, handoffs, guardrails, and custom events (OpenAI 2026a). NVIDIA’s NeMo Agent Toolkit similarly treats observability and profiling as tools for monitoring workflows down to the tool and agent level, tracking tokens, timings, traces, and behavior (NVIDIA 2026a). These are not marketing conveniences. They are evidence that the industry has learned a painful lesson: once agents act through tools, the path to an answer matters as much as the answer itself.

The academic literature reached the same point from a different direction. ReAct showed that interleaving reasoning traces and actions could improve performance and interpretability in interactive decision-making tasks (Yao et al. 2022). Reflexion showed that language agents could improve from verbal feedback stored in episodic memory rather than by updating weights (Shinn et al. 2023). Self-Refine showed that iterative feedback and refinement could improve outputs without additional supervised training (Madaan et al. 2023). These methods are often discussed as prompting or agent-design techniques. For a secure harness, they are also observability requirements. If an agent learns from feedback, someone must decide which feedback is trustworthy. If an agent records reflections, someone must decide whether those reflections are memory, telemetry, or untrusted context. If an agent iterates over candidate actions, someone must preserve enough evidence to know which iteration changed the outcome.

The central thesis of this chapter is simple: **agent observability should produce evidence that can be used during the run, after the run, and before the next harness change ships**. During the run, the harness needs signals to interrupt unsafe behavior. After the run, auditors and incident responders need a record that is more reliable than a narrative summary. Before the next change, engineers need evals that convert observed failures into tests. Without this evidence path, “hill climbing” becomes a flattering name for guesswork.

Figure 7.1 shows the observability spine used throughout this chapter. The chain begins with an intent contract and passes through the agent run, tool and memory calls, harness policy decisions, trace spans, evals, evidence envelopes, and governed improvement. The loop matters. Observability is not a sink at the end of the system. It is the path by which the system learns without silently granting itself more power.

## 7.2 From Reasoning Traces to Evidence Traces

The word “trace” is dangerously overloaded in agent systems. In early LLM-agent research, a trace often meant the model’s intermediate reasoning or the sequence of thoughts and actions produced during a task. In software operations, a trace usually means a structured record of spans across a distributed system. In governance, a trace may mean an audit trail. These meanings overlap, but they are not interchangeable.

A reasoning trace can help a model solve a problem, but it is not automatically evidence. It may contain private reasoning that should not be exposed to users. It may contain sensitive data copied from context. It may include a plausible explanation that was generated after the fact rather than a faithful record of control decisions. It may omit tool outputs, policy versions, or approval state. A production evidence trace has a different standard. It must be structured enough to query, safe enough to retain, complete enough to support replay, and tied to the controls that made the decision.

ReAct is important because it normalized the idea that action trajectories are useful and interpretable. The method combines reasoning and acting so that a model can update plans as it interacts with an environment (Yao et al. 2022). For a research benchmark, the trajectory can be inspected to understand behavior. For a production harness, the trajectory must be decomposed. The harness should not simply dump every thought, prompt, context item, and tool output into a log. It should record policy-relevant facts: which tool was called, under which intent, with which data class, by which identity, against which resource, with which approval or denial decision, and with which artifact reference.

Reflexion and Self-Refine deepen the challenge. Reflexion agents use feedback to create verbal reflections that influence future trials (Shinn et al. 2023). Self-Refine agents generate feedback on their own output and use it to refine later output (Madaan et al. 2023). These methods make improvement part of the runtime. From a harness perspective, improvement is not free. Feedback can be poisoned. Reflection can encode a bad lesson. Self-critique can optimize for the wrong evaluator. A secure observability layer must record not only the final answer but also the feedback source, the acceptance rule, the memory boundary, and the eval result that justified carrying a lesson forward.

This is where the distinction between “model reasoning trace” and “harness evidence trace” becomes essential. The harness evidence trace does not need to reveal every internal chain of thought. It needs to reveal the control-relevant chain of custody. For example, it might record that the model produced a candidate customer email, that the content contained a token-like string, that the redaction middleware rewrote the trace payload before emission, that the final output was blocked until a policy rule passed, and that the replay bundle contains a redacted fixture plus a hash of the raw input. This is enough to support security review without turning internal reasoning into another sensitive artifact.

OpenTelemetry’s GenAI conventions reflect this move toward structured, interoperable telemetry. The current GenAI attribute registry includes concepts for agent identity, conversation identifiers, evaluation scores and explanations, model input and output messages, tool calls, token usage, and workflow names (OpenTelemetry 2026). The specific vocabulary will continue to evolve, and the official documentation notes that GenAI attributes have moved into a dedicated semantic-conventions repository. The stable lesson is not a particular field name. The stable lesson is that agent systems need a shared language for telemetry that covers models, tools, conversations, evaluations, and workflows.

The same lesson appears in platform guidance. OpenAI’s tracing model distinguishes traces from spans and records agent runs, LLM generations, tool calls, guardrails, and handoffs by default (OpenAI 2026a). Anthropic’s Claude Code monitoring documentation describes OpenTelemetry export for metrics, logs, events, and optionally distributed traces, including tool activity and costs (Anthropic 2026a). Alibaba’s LoongSuite article frames agent observability and audit data collection around extended OpenTelemetry GenAI conventions (Alibaba Cloud Native Community 2026). These systems are different in implementation, but they point toward a common architecture: agent observability must move beyond ad hoc logs toward structured, multi-layer evidence.

For this book, the term **evidence trace** means the subset of telemetry that can answer four questions:

1. **What happened?** The trace records the agent, tool, memory, context, delegation, policy, and output events that changed the run.
2. **Why was it allowed or blocked?** The trace records the decision, rule, intent, data class, and evidence reference.
3. **Can it be reviewed safely?** The trace is redacted, classified, access-controlled, and linked to governed raw evidence when necessary.
4. **Can it improve the harness?** The trace can be converted into eval fixtures, regression gates, and bounded change proposals.

Those four questions are the bridge between research trajectories and production assurance. They also explain why observability belongs in a security book. If a harness cannot answer them, it cannot credibly claim to control long-horizon autonomy.

## 7.3 The Observability Spine of the Secure Harness

The secure harness is the control plane around agent autonomy. It mediates identity, intent, context, memory, tools, runtime steering, and data governance. Observability is the nervous system of that control plane. It carries signals from every component, but it also decides which signals are safe to expose, which signals are important enough to retain, and which signals should become tests.

In a conventional application, an observability pipeline often begins after an event has already happened. The application logs the event; metrics aggregate it; tracing connects it to a request. In a secure agent harness, observability starts earlier. The harness knows the agent’s declared goal, the identity under which it is acting, the tools it may call, the data classes it may touch, the context sources it has been given, the memory writes it proposes, and the runtime state of the run. Every one of those elements can change the interpretation of the same action.

Consider an agent that sends an email. The action is not inherently safe or unsafe. It depends on the intent, recipient, content, data class, approval state, prior context, memory source, jurisdiction, and reversibility. If the email is a draft to an internal reviewer, the harness may allow it. If it is an external notification containing a secret, the harness should block or rewrite it. If it is a customer notification after an incident, the harness may require human approval and preserve evidence for later review. The trace must capture these distinctions. A log line that says `send_email succeeded` is operationally useful and security-poor.

Figure 7.1 is deliberately drawn as a spine rather than as a pile of telemetry boxes. The harness observes the relationship between components. The intent contract authorizes the run. The run produces tool and memory calls. Policy decisions mediate those calls. Trace spans and evals record the mediation. Evidence envelopes bind the record. Governed improvement updates the system under control. If any link is missing, the system can still produce outputs, but it cannot prove that those outputs were governed.

The spine pattern has three design principles.

First, **record decisions, not only events**. Events say what happened. Decisions say what the harness concluded and why. Agent systems need decisions such as `allow`, `deny`, `rewrite`, `escalate`, `pause`, `kill`, `rollback`, and `expire`. The exact vocabulary can vary, but the distinction matters. A rewritten trace payload is not a failure. It is a successful privacy control. An escalated benchmark regression is not an outage. It is a risk signal. A denied self-improvement proposal is not an agent bug. It is evidence that the harness kept authority bounded.

Second, **bind evidence to artifacts**. A trace event that claims “benchmark regression detected” should refer to the benchmark report, the candidate configuration, the baseline configuration, and the failed gates. A trace event that claims “customer data redacted” should record the redaction rule and provide a safe artifact for inspection. Artifact hashes make this binding stronger. They do not solve governance by themselves, but they make it harder for later narratives to drift away from what the harness actually saw.

Third, **make improvement falsifiable**. A harness change should not ship because the team likes a new prompt, a new profile, or a new middleware rule. It should ship because evidence shows that it improves a measured outcome without weakening safety gates. OpenAI’s agent-improvement-loop cookbook expresses this idea in a concrete workflow: start with real traces, add human and model feedback, turn feedback into evals, and use the resulting evidence to propose harness changes (OpenAI 2026b). LangChain makes a similar point in its discussion of traces as the start of an agent improvement loop: collect traces, enrich them with feedback, identify failures, make targeted changes, validate, and repeat (LangChain 2026b). The secure-harness version adds a governance requirement: the loop must not be allowed to optimize away the controls that generate the evidence.

This pattern is particularly important for long-running agents. A short chatbot interaction can be reviewed as one prompt and one response. A long-horizon run may unfold across hours, days, or weeks. The run may pause for human approval, resume with a different credential epoch, delegate a task to a subagent, retrieve fresh context, write memory, and retry a tool call after a transient failure. Without trace continuity, the organization sees fragments. With trace continuity, the organization sees an evidence chain.

Anthropic’s context-engineering guidance is useful here because it describes agents as autonomous tool users in a loop and emphasizes just-in-time context strategies, progressive disclosure, and external references rather than loading everything into a prompt up front (Anthropic 2025a). This makes agents more capable, but it also means the observability spine must capture which references were followed, which data was loaded, and whether the agent’s later action relied on stale or untrusted context. The more an agent discovers at runtime, the more important it becomes to record the discovery path.

The spine pattern also clarifies the relationship between observability and threat modeling. CSA MAESTRO argues that agentic AI threat modeling must address vulnerabilities across layers and interactions, not just isolated components (Huang 2025). Observability is how those layers become reviewable at runtime. A MAESTRO-informed trace should tell the reviewer which model, prompt, tool, memory, orchestration, data, and governance layers were involved in a decision. Without that mapping, an incident review becomes a guessing exercise.

## 7.4 Decision Traces

A decision trace is a structured record of control decisions made during a run. It is not a natural-language story written by the agent at the end. It is not a raw transcript. It is not merely an OpenTelemetry span. It is the security-relevant layer that says what the harness decided, under which rule, with which evidence, at which point in the run.

The simplest decision trace entry has five fields: step, decision, reason, evidence reference, and policy version. A production trace will likely include more: actor identity, task identity, delegated identity, tool name, data class, tenant, region, approval state, memory source, context source, risk level, and rollback pointer. The point is not to create an enormous schema on day one. The point is to make decisions explicit enough that a reviewer can distinguish a safe action from a lucky one.

Decision traces should include positive and negative outcomes. Many teams log denials but fail to log ordinary allows. That creates a distorted audit record. If a harmful action was allowed, the organization needs to know which rule allowed it. Conversely, many teams log successful business actions but fail to log rewrites and escalations. That hides the harness’s work. In a secure agent platform, a good day includes many small controlled decisions: a context item was quarantined, a tool call was downgraded, a memory write was held for validation, an output was rewritten, an irreversible action was escalated, and a low-risk lookup was allowed. The trace should show the texture of control.

The HarnessLab Chapter 7 scenario uses six decision-trace steps. The first records that a customer-notification tool call was observed with intent, data class, and policy context. The second records that sensitive evidence was rewritten before trace emission. The third records that a benchmark regression was escalated because unsafe-block rate, redaction recall, and replay pass rate fell. The fourth records that a hill-climbing loop selected a safe improvement. The fifth records that an ungoverned recursive self-improvement proposal was denied. The sixth records that a bounded rollout was allowed because it included evidence, rollback, and approval controls.

This vocabulary is intentionally richer than pass/fail. `Rewrite` is a first-class decision because agent telemetry often needs transformation before retention. `Escalate` is a first-class decision because some evidence requires review rather than automatic rejection. `Deny` is a first-class decision because the harness must preserve hard boundaries. `Allow` is a first-class decision because safe progress should be visible too. A good trace lets the reviewer see all four.

OpenAI’s Agents SDK tracing documentation shows why this fits naturally into modern agent platforms. By default, agent runs, LLM generations, function tool calls, guardrails, handoffs, and speech spans can be represented as spans (OpenAI 2026a). A decision trace can be built on top of such spans or stored as structured span attributes and events. The design choice depends on the platform. What matters is that policy decisions are not hidden in free-form logs or agent summaries.

Decision traces should also be designed for evaluation. If the trace records why a run was escalated, the same trace can become a future regression case. If the trace records that a redaction rule fired, the same trace can test whether a future redaction pipeline still catches that pattern. If the trace records that an ungoverned self-improvement proposal was denied, the same trace can test whether a future agent still lacks the ability to modify its evaluator weights without approval. This is how observability becomes part of the hill-climbing loop.

The security risk is trace inflation. Teams may be tempted to preserve everything, partly because storage is cheap and partly because forensic completeness is attractive. Agent telemetry makes that instinct dangerous. Tool arguments may contain secrets. Retrieved documents may contain regulated data. Model outputs may contain personal information. Memory writes may contain user-specific context. Even a hashed artifact can be sensitive if the input space is small enough for guessing. Decision traces should therefore preserve control-relevant evidence, not indiscriminate copies of every input and output.

This is one reason the trace schema should separate raw evidence, redacted evidence, and evidence references. A normal reviewer may need only the redacted evidence. A security incident team may need governed access to raw evidence in a restricted store. An external auditor may need hashes and policy versions but not raw content. The decision trace should make these paths possible without collapsing them into one log stream.

## 7.5 Evidence Envelopes and Artifact Hashes

Decision traces explain control decisions. Evidence envelopes bind those decisions to artifacts. An evidence envelope is a metadata wrapper around the run’s reviewable record: run id, actor, policy version, spans, artifact hashes, redaction markers, creation time, and a tamper-evident digest. It is not a replacement for a trace backend, object store, or audit log. It is a portable evidence shape that can survive movement across systems.

Figure 7.2 shows the pattern. The run contributes identity and policy metadata. Trace spans, artifacts, and replay bundles are digested into hashes. The hashes are sealed into an envelope. The envelope supports audit, incident response, and replay. This pattern is deliberately simple. It borrows from familiar software supply-chain and audit practices: do not merely claim that an artifact existed; bind it to a digest and a context.

Artifact hashes solve a common agent-review problem. A trace may say that the harness escalated a benchmark regression. Which benchmark report? Which candidate configuration? Which baseline? Which dataset? Which judge prompt? Which tool version? Without artifact references, the decision is hard to reproduce and easy to reinterpret. With hashes, a reviewer can compare the current artifact set with the one the harness used at decision time.

Hashes are not magic. A hash does not make sensitive data safe. If the raw input is guessable, a hash may still leak information through brute force. If the artifact store is compromised, hashes may preserve integrity but not confidentiality. If the wrong artifact is hashed, the evidence is faithfully wrong. The envelope pattern must therefore be paired with classification, access control, retention policy, and review process. The envelope makes evidence manageable; governance makes it safe.

The evidence envelope is also a response to a subtle problem in agent development: narrative drift. After a failure, people naturally create stories. The agent failed because the prompt was too vague. The tool failed because the API was flaky. The model failed because the context was too long. The reviewer failed because the approval screen was unclear. Some of these stories may be true. The evidence envelope forces the conversation back to recorded facts. Which policy version was active? Which rule fired? Which artifact was used? Which gate failed? Which run was replayed? Which rollout was approved?

For long-horizon agents, the envelope should include checkpoint references. A run that pauses and resumes should record not only the final action but also the state boundary at pause time: state hash, credential epoch, policy version, memory snapshot reference, and context freshness. Figure 7.4 shows this continuity pattern. A checkpoint is not merely a recovery convenience. It is an evidentiary boundary. If the agent resumes after credentials expire or context becomes stale, the harness should be able to prove that renewal checks happened.

NIST’s Generative AI Profile for the AI Risk Management Framework emphasizes that risk management should align with legal, regulatory, organizational, and lifecycle requirements (NIST 2024). Evidence envelopes are one way to make such alignment concrete. They give governance teams a technical object that connects policy, measurement, and incident review. ISO/IEC 42001 similarly frames AI management as a system for establishing, implementing, maintaining, and continually improving AI-related policies and processes (ISO 2023). Evidence envelopes provide the operational substrate for that continual improvement. They turn governance from a committee assertion into a reviewable artifact.

The HarnessLab scenario demonstrates this pattern with deterministic data. It creates hashes for redacted observations, decision traces, trace spans, benchmark regression reports, hill-climbing loops, governed self-improvement records, and replay bundles. It then seals those hashes into an evidence envelope with a policy version and redaction markers. In production, timestamps would be real and storage would be external. In the lab, determinism makes the concept easier to test. The important lesson is the same: a trace without artifact binding is a story; a trace with evidence binding becomes an audit record.

## 7.6 Privacy-Safe Telemetry

Observability can become the system’s most ironic vulnerability. A team may design strong controls around model inputs, tool credentials, customer data, and memory writes, then accidentally copy all of that data into a trace backend with broader access and longer retention. The agent’s primary action may be safe while the telemetry pipeline becomes the leak.

This is not a hypothetical concern. NVIDIA’s NeMo Agent Toolkit security considerations explicitly warn that observability and profiling features can capture detailed information about agent behavior, including prompts and responses, and that those records may contain sensitive, personal, confidential, or regulated information depending on the systems the agent can access (NVIDIA 2026b). OpenAI’s Agents SDK tracing documentation separately notes that tracing is unavailable for organizations operating under Zero Data Retention policies, a reminder that telemetry has data-retention consequences (OpenAI 2026a). Anthropic’s Agent SDK documentation warns developers to avoid putting secrets into serialized run context when state may be persisted or transmitted (Anthropic 2026b). These details are easy to treat as implementation notes. They are actually design constraints.

The secure-harness rule is **redact before emission**. Redaction after ingestion is sometimes necessary for cleanup, but it is not a safe default. If raw PII or secrets reach a log collector, queue, search index, trace backend, alerting system, dashboard cache, screenshot, model-feedback store, or eval dataset, the organization now has many copies to govern. Agent systems multiply this risk because the same information may appear in prompts, retrieved context, tool arguments, tool outputs, intermediate summaries, memory candidates, evaluator explanations, and failure transcripts.

Figure 7.6 shows a privacy-safe telemetry pipeline. Raw observations first pass through classification. The pipeline identifies source, data class, tenant, region, and retention requirements. Sensitive content is redacted, summarized, tokenized, or routed to a restricted vault. The trace store receives safe payloads and references. Hashes preserve integrity without exposing raw content to ordinary reviewers. Retention and access policy govern both the safe trace store and any restricted raw-evidence vault.

The hardest design problem is not the redaction function itself. It is deciding **where redaction lives**. If redaction is a best-effort library call inside each agent, coverage will be inconsistent. If redaction is only a post-processing job, sensitive content may already be copied. If redaction is hidden inside a vendor’s trace exporter, the team may not know which artifacts are safe. The harness should treat telemetry rewriting as middleware on the evidence path. Tool outputs, model outputs, context snippets, and evaluator explanations should pass through it before they become durable evidence.

This does not mean every trace must be stripped until useless. A trace that says only “something happened” is safe but not valuable. The right goal is **minimum sufficient evidence**. For a customer notification, the reviewer may need to know that the content was a customer email, that the incident ticket was `INC-407`, that a token-like pattern was removed, that the final approved text passed the policy, and that a hash of the raw draft exists in a restricted store. The reviewer probably does not need the customer’s raw email address, the literal token string, or the full source document in the ordinary trace dashboard.

Privacy-safe telemetry also requires data-class-aware routing. A public documentation lookup, an internal runbook, a customer record, and a regulated medical note should not flow into the same trace path simply because the same agent saw them. The trace backend may support field-level redaction, but the harness should still label and route evidence before storage. A good rule is to treat telemetry as another tool call. It has a destination, a schema, a data class, a retention policy, and a permission boundary.

OpenTelemetry’s GenAI conventions are helpful because they encourage structured capture of agent, conversation, evaluation, message, tool, token, and workflow attributes (OpenTelemetry 2026). But standards do not remove the need for policy. The same standard field can carry safe or unsafe content. For example, a tool-call argument field might contain a city name in one workflow and a bank account number in another. A retrieval document field might contain a public FAQ or a confidential contract. Standardization makes instrumentation interoperable; classification makes it governable.

Redaction should be observable too. A trace should record that redaction happened, which rule fired, and whether the output was rewritten, summarized, or withheld. It should not record the removed secret. This helps reviewers distinguish actual redaction from magical thinking. In the HarnessLab scenario, the redaction markers include a field-based email redaction and a token-pattern redaction. The final result verifies that the redacted observation does not contain the raw email or token-like string, while preserving enough evidence to explain the rewrite decision.

There is an uncomfortable tradeoff between forensic completeness and privacy minimization. Security teams often want raw evidence because incidents are messy. Privacy and compliance teams often want less retention because every retained artifact creates obligations. The secure harness should not pretend the tradeoff disappears. It should make it explicit through tiers. Ordinary traces contain redacted evidence. Restricted vaults contain governed raw evidence when the risk justifies it. Evidence envelopes contain hashes and references. Replay bundles contain fixtures designed for safe reruns. Each tier has a purpose, access model, and retention period.

This tiered design also reduces evaluator contamination. If raw production traces become eval fixtures without review, sensitive data may enter test suites, prompt libraries, or benchmark datasets. Once there, it may be copied into development machines, CI logs, third-party evaluator systems, or model-training corpora. A privacy-safe harness turns trace-to-eval conversion into a review step. The team should decide what can be replayed, what must be synthesized, what should be hashed only, and what should be excluded entirely.

## 7.7 Evals as Executable Risk Controls

Evals are structured tests for measuring model or application behavior. In a secure harness, they are also executable risk controls. They decide whether a candidate change can ship, whether a regression needs escalation, whether a new model is acceptable, whether a memory policy still prevents poisoning, whether a tool contract remains enforceable, and whether a redaction pipeline is still catching sensitive content.

OpenAI’s evaluation guidance defines evals as structured tests that help ensure accuracy, performance, and reliability despite the nondeterminism of AI systems (OpenAI 2026c). That definition is a good starting point. Agent harnesses need a broader frame. An agent eval should not measure only final-answer quality. It should measure the trajectory and the controls: Did the agent call the right tool? Did it avoid forbidden tools? Did it preserve data labels? Did it ask for approval before irreversible action? Did it refuse poisoned context? Did it maintain replay fidelity? Did it leave an evidence trail that can be audited?

This is why agent benchmarks have become more realistic over time. AgentBench evaluates LLMs as agents across interactive environments and identifies long-term reasoning, decision-making, and instruction-following as major obstacles (Liu et al. 2023). τ-bench evaluates tool-agent-user interaction in real-world domains, emphasizing dynamic conversations, domain-specific rules, API tools, and reliability over repeated trials (Yao et al. 2024). SWE-bench evaluates whether systems can resolve real GitHub issues, and SWE-bench Verified uses a human-filtered subset of 500 instances for more reliable evaluation (SWE-bench 2026). Terminal-Bench evaluates agents in terminal environments with long-running, end-to-end tasks; its 2.0 leaderboard is useful not only because of model scores, but because it shows how much harness design can influence performance (Terminal-Bench 2026).

For a secure-harness chapter, the important point is not that any one benchmark is definitive. None is. Benchmarks are instruments. Each highlights some dimensions and hides others. Terminal-Bench can expose tool-use discipline, command execution, environment management, and verification habits. τ-bench can expose policy-following during user-tool interaction. SWE-bench can expose codebase navigation, patch generation, and test-driven repair. AgentBench can expose multi-environment decision-making. None by itself proves that a production agent is safe for regulated data, irreversible actions, or long-running self-improvement.

The harness needs a **gate matrix** rather than a single score. Figure 7.5 illustrates the idea. A candidate harness change should be compared against task-success metrics, safety metrics, privacy metrics, replay metrics, cost metrics, and operator-burden metrics. Some metrics can be optimized. Others are gates. Unsafe-block rate should not fall below threshold. Redaction recall should not regress. Replay pass rate should not drop. Human-review burden should not explode silently. A change that improves task success while weakening a safety gate is not an improvement; it is a tradeoff requiring review.

The HarnessLab scenario includes a candidate called `aggressive_trace_sampling`. It improves latency and task success. Those are real gains. But it reduces unsafe-block rate, redaction recall, and replay pass rate. A naive optimizer might accept it. The secure harness escalates it. This is the chapter’s core lesson in miniature: hill climbing must be constrained by gates, not seduced by a single reward.

Evals come in several forms. Unit-style evals check deterministic properties: a redaction function removes a token pattern; a tool contract rejects an out-of-scope argument; a replay bundle reaches the expected decision. Model-graded evals use an LLM judge to rate quality, safety, relevance, or policy adherence. Human evals capture expert judgment where stakes are high or labels are ambiguous. Simulation evals run agent-user-tool interactions in controlled environments. Production monitors track real-world metrics such as escalation rate, latency, cost, user correction, incident rate, and policy drift.

Each form has strengths and weaknesses. Deterministic evals are reliable but narrow. Model-graded evals scale but can be biased. Human evals are rich but expensive and inconsistent. Simulations expose interaction failures but may not match production distribution. Production monitors reflect reality but can lag behind harm. The secure harness combines them. It does not ask one evaluator to carry all governance.

LLM-as-judge deserves special caution. Zheng et al. show that strong LLM judges can approximate human preferences in some settings and make scalable evaluation possible, but they also identify limitations such as position bias, verbosity bias, self-enhancement bias, and reasoning limits (Zheng et al. 2023). Later work continues to quantify judge biases, including position and other shortcut effects (Shi et al. 2024; Ye et al. 2024). The practical lesson is not to reject LLM judges. It is to use them with countermeasures: randomized ordering, calibration sets, rubric specificity, judge-model diversity, human spot checks, deterministic graders where possible, and trace-grounded evidence rather than free-form impressions.

HELM is useful here because it argues for broad, multi-metric evaluation rather than a narrow accuracy race. It measures multiple desiderata such as accuracy, calibration, robustness, fairness, bias, toxicity, and efficiency across scenarios (Liang et al. 2022). Agent harnesses need the same spirit. A candidate that improves accuracy while worsening privacy, replay, or operator comprehension is not an unqualified improvement. Multi-metric evaluation forces tradeoffs into view.

Evals should be integrated into the development lifecycle. In early design, they define the target behavior. During implementation, they close the loop for agents and engineers. In CI, they prevent regressions. In production, they turn incidents into new fixtures. In governance, they provide evidence for audit and model-risk review. OpenAI’s current agent-improvement-loop example explicitly starts with real traces, adds feedback, turns feedback into evals, and uses evidence to propose harness changes (OpenAI 2026b). That workflow is close to the hill-climbing discipline this book advocates, but security adds a hard requirement: the eval suite itself must be protected from manipulation by the agent or optimizer being evaluated.

This requirement leads to a simple rule: **evals must be outside the agent’s authority boundary**. An agent may propose a new eval fixture. It may label a failure. It may suggest a threshold. It may run a local check. But it should not be able to delete failing evals, rewrite judge rubrics, alter safety thresholds, or change metric weights without governance. Otherwise the agent can improve its score by changing the test rather than improving behavior.

## 7.8 Hill Climbing as Harness Engineering

Hill climbing is a local-search method: try nearby changes, measure them, keep improvements, and continue from the new baseline. The phrase can sound too narrow because in classical optimization it is associated with local optima and simple search. In this book, hill climbing is used deliberately. Long-horizon agents already hill-climb in practice. They revise plans, retry commands, ask subagents, inspect errors, change prompts, add context, rewrite code, and run tests. The question is whether the harness makes that search bounded, evidence-driven, and reversible.

Most teams begin by hill-climbing prompts. A prompt is changed, the agent seems better on a few examples, and the change ships. This is understandable. Prompts are visible, cheap to edit, and often effective. But mature agent systems are not prompt-only systems. The harness includes tool descriptions, tool implementations, middleware, memory policy, retrieval rules, routing, context packing, delegation patterns, timeout rules, approval gates, eval fixtures, trace exporters, and rollback paths. A harness change can improve behavior even when the model and prompt stay the same. Conversely, a prompt change can look good while damaging tool discipline or auditability.

LangChain’s Deep Agents profiles are a useful current example of harness-level variation. The profiles documentation distinguishes harness profiles from provider profiles and notes that Deep Agents ships built-in harness profiles for OpenAI and Anthropic models (LangChain 2026a). The point is subtle but important: model construction parameters are not the same as harness behavior. The harness can adjust prompts, tools, middleware, and runtime assumptions around a model. That is precisely the design surface this book calls harness engineering.

NVIDIA’s AI-Q Blueprint illustrates a similar industry direction. It is described as an open reference example for building inspectable and controllable agents, built on LangChain Deep Agents and accelerated by the NeMo Agent Toolkit, with benchmarks and evaluation harnesses for measuring quality and improvement over time (NVIDIA 2026c). The named products will evolve. The pattern will endure: agent quality increasingly depends on the harness around the model, and the harness must be evaluated as an engineering artifact.

Terminal-Bench provides one vivid example. As of July 2026, the Terminal-Bench 2.0 leaderboard listed NexAU-AHE GPT-5.5 at the top, with other harness-oriented agents near it (Terminal-Bench 2026). The interesting lesson is not the leaderboard position itself. It is that terminal-agent performance depends heavily on the operating environment around the model: shell-tool contracts, timeouts, output truncation, validation habits, file-state discipline, traces, retries, and acceptance checks. A simple agent can become strong when the harness gives it disciplined search and verification.

The hill-climbing loop in a secure harness should have five stages.

First, **define the neighborhood**. What is allowed to change? A prompt? A tool description? A context policy? A redaction rule? A routing threshold? A memory promotion gate? A timeout? A benchmark fixture? The safer the system, the clearer the change boundary. The agent or optimizer should not be free to modify every part of its own environment at once.

Second, **collect evidence**. The candidate should be evaluated against traces, replay bundles, synthetic tests, benchmark tasks, and production-derived fixtures. Evidence should include both success and failure cases. A change that improves average performance while failing a high-severity case should be visible.

Third, **separate score from gates**. A composite score can rank candidates, but safety gates must retain veto power. If unsafe-block rate, redaction recall, replay pass rate, or data-residency compliance falls below threshold, the candidate should be rejected or escalated even if task success improves.

Fourth, **ship through bounded rollout**. A passing candidate should not immediately become universal policy for all tenants, tools, data classes, and autonomy levels. Canary rollout, feature flags, tenant segmentation, traffic sampling, and rollback checkpoints are part of the harness. They reduce blast radius and preserve evidence.

Fifth, **promote lessons into durable assets**. A failure case should become a replay fixture. A repeated human correction should become an eval. A safe tool pattern should become a tool contract. A confusing trace should become a schema improvement. Hill climbing is not only about selecting the next candidate; it is about raising the baseline.

Figure 7.3 shows this loop. Production or pilot traces are enriched with human and model feedback. Feedback becomes eval fixtures and graders. Evals measure candidate harness changes. Gates decide whether the candidate enters bounded rollout or is rejected or escalated. A successful rollout becomes the new baseline. The loop repeats.

The main failure mode is metric capture. The system learns to optimize what is measured and ignore what is not. If latency is measured and forensic replay is not, replay will decay. If task success is measured and refusal quality is not, the agent may become overconfident. If human approvals are counted only as friction, the system may learn to avoid escalation. If cost is optimized without incident risk, the system may sample away traces. The solution is not to measure everything equally. The solution is to decide which dimensions are gates, which are objectives, which are diagnostics, and which are governance indicators.

Hill climbing also interacts with context engineering. Anthropic’s context-engineering guidance argues for just-in-time retrieval and progressive disclosure because agents can explore their environment and load only relevant information (Anthropic 2025a). That strategy can improve capability, but it creates new eval questions. Did the agent discover the right context? Did it waste context on irrelevant files? Did it load untrusted content into a high-trust reasoning path? Did it preserve identifiers that allow reviewers to reconstruct the path? A context strategy should be hill-climbed against these questions, not only against final output quality.

The same is true for tool design. Anthropic’s guidance on building effective agents emphasizes that tool definitions deserve as much attention as prompts and that agents work best when tools have clear structures and definitions (Anthropic 2024). A tool contract is therefore a hill-climbing surface. Better parameter names, stronger validation, clearer error messages, semantic output truncation, and safer defaults can improve agent behavior without changing the model. But every tool-contract change should be evaluated against real traces and regression gates. A tool that is easier for the model to use may also be easier to misuse.

## 7.9 Recursive Self-Improvement and the Governance Boundary

Recursive self-improvement is the moment when hill climbing becomes governance-sensitive. An agent or agent-assisted process proposes a change to the harness that will shape future agent behavior. That change might be benign and valuable. It might add a redaction rule, improve a tool description, create a replay fixture, or tighten an approval gate. It might also weaken a safety threshold, delete failing evals, hide trace detail, or shift evaluator weights toward task success at the expense of auditability.

The governance boundary is simple: **the system being evaluated should not have unilateral authority over the evaluation and control system that evaluates it**. This is not a philosophical position. It is an engineering control. If an agent can alter its own tests, erase its own failures, or grant itself broader authority, the evidence loop collapses.

Figure 7.7 shows a governed recursive self-improvement flow. The agent proposes a harness change. The proposal must include evidence hashes and eval reports. It must identify a rollback checkpoint. It must pass human or policy approval. If controls are complete, the change enters canary rollout with monitoring and rollback. If controls are missing, the proposal is denied and the denial is preserved as trace evidence.

This design does not prevent agents from helping improve themselves. It channels improvement through a change process. OpenAI’s multi-agent orchestration guidance explicitly notes that agents can introspect and improve, run in loops, critique themselves, and use evals to improve over time (OpenAI 2026d). Anthropic’s Claude Code best practices similarly encourage giving agents a way to verify work through tests, builds, screenshots, or other checks, so the agent can iterate until a check passes (Anthropic 2026c). These practices are powerful. The secure harness adds that the check itself must be outside the agent’s easy manipulation.

Governed recursive improvement needs a stronger evidence standard than ordinary task execution. A normal tool call might require identity, intent, tool scope, and data classification. A harness-change proposal should require more:

1. **Change statement**: What exactly changes, and which component owns it?
2. **Evidence hash**: Which trace, eval, incident, or benchmark justifies the change?
3. **Safety gate report**: Which gates passed, failed, or require human review?
4. **Rollback checkpoint**: How can the system return to the previous behavior?
5. **Blast-radius limit**: Which tenants, tools, agents, data classes, or tasks are affected first?
6. **Approval record**: Which human, policy, or governance process approved the change?
7. **Monitoring plan**: Which metrics decide whether to continue, pause, or roll back?

The HarnessLab scenario includes two recursive-improvement proposals. The first proposal tries to raise the task-success weight and ignore replay failures. It lacks an evidence hash, rollback checkpoint, and human approval, so the harness denies it. The second proposal promotes redaction-before-indexing after the hill-climbing loop selects it as safe. It includes evidence, rollback, bounded rollout, and approval controls, so the harness allows it as a supervised rollout.

The example is small, but the pattern scales. A coding agent that wants to modify its CI workflow should provide the failing trace and the passing test evidence. A customer-support agent that wants to relax an escalation rule should provide eval results showing no drop in policy compliance. A research agent that wants to change retrieval strategy should provide evidence that citation quality, data minimization, and answer quality all remain within threshold. A security agent that wants to add an automated remediation should provide rollback and blast-radius limits.

Recursive self-improvement also needs separation of duties. The agent can propose. The harness evaluates. A human or policy engine approves. CI runs tests. Observability monitors rollout. Incident response can roll back. This may sound heavy, but only high-impact self-modification needs the full path. Low-risk improvements can move through lighter gates. The key is to classify the change. A spelling correction in a tool description is not the same as a new permission mode. A new eval fixture is not the same as deleting an eval fixture. A temporary policy overlay is not the same as a permanent threshold change.

This is where long-horizon agents raise the stakes. A short-lived agent may propose a change during one session. A long-running agent may accumulate evidence, memory, and preferences over time. It may learn that certain controls slow it down. It may discover which evals are hard. It may infer that traces expose its mistakes. These are not signs of malice; they are consequences of optimization. A system that searches for better performance will eventually find pressure points in the harness. Governance turns those pressure points into reviewable proposals rather than silent drift.

## 7.10 Long-Horizon Trace Continuity

Long-running agents are becoming normal rather than exotic. Coding agents run across large repositories, test suites, and pull requests. Research agents gather sources, write drafts, revisit evidence, and refine claims. Enterprise workflow agents wait for approvals, monitor queues, and resume after external events. Customer-support agents may span multiple conversations and backend systems. These agents do not fit neatly into one prompt, one answer, and one log entry.

Long-horizon observability must therefore solve continuity. Which trace connects the first user request to a subagent’s tool call three hours later? Which policy version was active before the pause? Which credential epoch was renewed after resume? Which memory item influenced the later action? Which context source was fresh at the time? Which human approval was still valid? Which temporary policy overlay expired before the final output?

Figure 7.4 shows the pause/resume continuity pattern. A run begins with planning and retrieval, performs a tool call, records a checkpoint, pauses, resumes later, performs renewal checks, and continues or escalates. The checkpoint preserves state hash, credential epoch, and policy version. The renewed run records intent freshness, credential rotation, and context age. The final action remains tied to the earlier trace rather than becoming a disconnected event.

OpenAI’s tracing documentation explicitly includes long-running workers and higher-level traces in its tracing table of contents, reflecting the need to manage traces beyond a single short call (OpenAI 2026a). Anthropic’s Agent SDK streaming guidance describes long-lived interaction patterns that handle interruptions, permission requests, and session management (Anthropic 2026d). Spring AI Alibaba’s ecosystem describes graph runtime components for long-running, stateful agents and admin tooling for runtime visualization, tracing, and evaluation (Alibaba 2026). These are different platforms, but they converge on a shared requirement: stateful agent work needs stateful observability.

Continuity has a cost. Long traces can become enormous. They can expose more sensitive data. They can overwhelm reviewers. They can become expensive to store and query. The answer is not to abandon continuity. The answer is to design trace hierarchy. A long-horizon run should have a top-level workflow trace, child traces for major phases, spans for tool calls and policy decisions, and evidence references for large artifacts. Summaries should be generated as review aids, but they should point back to structured evidence rather than replacing it.

The harness should also distinguish between **working context** and **audit context**. The agent may need compact working memory to continue a task. The auditor needs evidence of why a decision was made. These are not the same. A summary that helps the agent remember a plan may omit policy details. An audit record that explains a denial may not be useful to the agent’s next reasoning step. Good systems maintain both, with explicit links.

Long-horizon continuity also makes time a security dimension. Credentials expire. Approvals expire. Context grows stale. Policies change. Data residency rules shift when a tenant moves. A decision that was safe at noon may be unsafe after a policy update at 3 p.m. Observability should record time-sensitive validity. A trace should not merely say that approval existed; it should say when it was granted, what it covered, and whether it was still valid when used.

Replay bundles become more important as runs lengthen. A replay bundle cannot always contain the whole world. It should contain enough to reproduce the control decision. For a policy denial, that may include the tool call, intent contract, data label, policy version, and relevant context hash. For a benchmark regression, it may include baseline metrics, candidate metrics, evaluator configuration, and failed gates. For a memory poisoning case, it may include the memory record, source trust tier, promotion decision, and rollback marker. The replay boundary should be explicit.

The incident-response value is enormous. When a long-running agent causes harm, the organization does not want a pile of disconnected logs. It wants a causal map: what goal was active, what context was trusted, what memory was written, what tool was called, what policy decided, what evidence existed, what operator saw, what changed after resume, and what can be replayed. Long-horizon trace continuity provides that map.

## 7.11 Industry Patterns and Best Practices

The best current industry guidance converges on a small set of patterns even though the products and terminology differ. These patterns are useful because they show that secure harness observability is not a speculative academic concern. It is becoming part of ordinary agent engineering.

OpenAI’s Agents SDK treats tracing as built in. A trace represents an end-to-end workflow; spans represent operations within it; default tracing captures the runner, agent spans, LLM generations, function calls, guardrails, handoffs, and audio operations where relevant (OpenAI 2026a). OpenAI’s orchestration guidance also recommends monitoring, iterating, letting agents introspect within loops, using specialized agents, and investing in evals (OpenAI 2026d). The agent-improvement-loop cookbook turns those ideas into a workflow: real traces become feedback, feedback becomes evals, evals become evidence for harness changes (OpenAI 2026b). This is very close to the pattern in this chapter, with one difference in emphasis: the book treats every improvement loop as a governance object when it can alter future autonomy.

Anthropic’s guidance adds two important ideas. First, the “Building Effective Agents” article emphasizes that agents are LLMs augmented with tools, retrieval, and memory, and that tool definitions require as much care as prompts (Anthropic 2024). This supports the claim that observability must include tool contracts and tool-use evidence, not only model messages. Second, Anthropic’s context-engineering article argues for just-in-time context, progressive disclosure, and agent-managed exploration (Anthropic 2025a). This supports the long-horizon trace argument: if agents gather context dynamically, traces must capture how context was discovered and used. Anthropic’s Claude Code best practices add a practical verification rule: give the agent a check it can run so it can close its own loop rather than relying on human noticing (Anthropic 2026c). In secure-harness terms, the check must be evidence-bearing and outside unilateral agent control.

Google Cloud’s agent observability documentation is valuable because it states the operational difference directly. Agents can drift, hallucinate, regress silently, make unexpected decisions, and fail differently from conventional software (Google Cloud 2026). This language is useful for executives and platform teams because it explains why ordinary APM dashboards are not enough. The platform still needs metrics, logs, and traces, but it also needs agent-specific state: goals, plans, tool calls, intermediate reasoning artifacts where appropriate, guardrail decisions, user feedback, and eval results.

NVIDIA’s NeMo Agent Toolkit emphasizes observability, profiling, integrations with tracing platforms, OpenTelemetry compatibility, token and timing tracking, and workflow-level debugging (NVIDIA 2026a). Its security considerations are equally important because they warn that observability may capture prompts, responses, API outputs, and intermediate results that contain sensitive or regulated information (NVIDIA 2026b). The combination is exactly right. Mature platforms need deep telemetry, and deep telemetry needs strong controls.

LangChain’s Deep Agents profiles provide a practical example of harness-level adaptation. A harness profile can adjust behavior around a model; provider profiles only affect construction arguments (LangChain 2026a). This distinction belongs in a secure-harness book because it separates model choice from harness choice. An organization may run the same model under different harness profiles for coding, research, customer support, regulated workflow, or internal automation. Observability should record which profile was active. Evals should compare profiles as harness artifacts, not only compare base models.

Alibaba’s Spring AI Alibaba project and LoongSuite article show that observability, evaluation, MCP management, context engineering, human-in-the-loop support, long-running graph runtimes, and runtime visualization are now part of enterprise agent platform design (Alibaba 2026; Alibaba Cloud Native Community 2026). This matters because it shows that the harness pattern is not limited to one vendor ecosystem. Java, Python, cloud-native, and framework-specific agent stacks are all moving toward the same control-plane components.

OpenTelemetry provides the interoperability direction. Its AI-agent observability discussion emphasizes standardized metrics, traces, and logs that make agent frameworks easier to compare and integrate across observability solutions (OpenTelemetry 2025). Its GenAI attribute registry includes evaluation fields, tool-call fields, model-message fields, token fields, and workflow fields (OpenTelemetry 2026). The secure harness should use such standards where possible, but it should not outsource policy to the standard. A standard can say where to record a tool-call argument. It cannot decide whether that argument is safe to retain.

The practical best practices can be summarized as follows.

First, instrument the agent loop by default. If a framework exposes traces for agent spans, LLM generations, tool calls, handoffs, guardrails, and custom events, use them. If it does not, build a thin trace layer around the harness. The trace should follow the run, not merely the request.

Second, log policy decisions as structured events. A `deny` without a reason is frustrating. An `allow` without evidence is dangerous. A `rewrite` without redaction markers is unverifiable. A decision trace should say what happened, why, under which policy, and with which evidence reference.

Third, protect telemetry as data. Classify it, redact it, route it, retain it, and restrict it. Do not let observability become the bypass around your own data-governance controls.

Fourth, convert traces into evals. Every incident, escalation, human correction, unsafe near miss, and confusing failure should be considered as a future fixture. A trace that cannot become an eval may still be useful, but a trace that can become an eval is leverage.

Fifth, separate objectives from gates. A single blended score is easy to optimize and easy to manipulate. Use composite scores for ranking, but preserve veto gates for safety, privacy, replay, data residency, and irreversible actions.

Sixth, govern self-improvement. Let agents propose better prompts, tools, middleware, evals, and policies. Do not let them silently change the controls that evaluate and authorize them.

Seventh, design for pause and resume. Long-running agents need trace continuity, checkpoint references, credential epochs, context freshness, and policy-version binding.

Eighth, keep the evidence portable. Vendor dashboards are useful; evidence envelopes, replay bundles, artifact hashes, and exportable traces keep the organization from being trapped inside a single runtime view.

## 7.12 A MAESTRO-Informed Observability Map

CSA MAESTRO is useful in this chapter because it prevents observability from collapsing into a narrow model-monitoring problem. Agentic AI risk is layered. Foundation models, prompts, tools, orchestration, memory, identity, data, deployment, and outcomes interact. A trace that captures only the model call misses much of the threat surface. A trace that captures only infrastructure metrics misses the agentic behavior. A MAESTRO-informed observability map asks which layer produced the signal and which layer owns the control (Huang 2025).

Figure 7.8 illustrates this mapping. Model-layer signals include model outputs, refusals, uncertainty indicators, token usage, and model version. Prompt and intent signals include system instructions, developer instructions, user goals, policy versions, and intent contracts. Tool-layer signals include calls, arguments, side effects, output classes, and errors. Memory and context signals include provenance, trust tier, freshness, promotion status, and rollback markers. Orchestration signals include subagent delegation, handoffs, retries, timeouts, interrupts, and runtime policy overlays. Evals and audit signals convert those observations into measured risk and reviewable evidence. Governance closes the loop through policy updates and risk decisions.

This map prevents two common mistakes.

The first mistake is **model monoculture** in observability. Teams ask which model produced the answer and stop there. Model identity matters, but it is rarely the whole explanation. A harmful output may result from poisoned context, overbroad tool credentials, missing approval, stale memory, poor data labeling, or an unsafe retry loop. Observability should let reviewers follow the chain across layers.

The second mistake is **infrastructure monoculture**. Teams instrument CPU, latency, HTTP status codes, queue depth, and database errors but fail to capture agent-specific decisions. Those metrics are necessary, especially at scale, but they do not explain why an agent believed it could send a message, write memory, or call a tool. The harness needs both: infrastructure observability and agent decision observability.

MAESTRO also helps with threat modeling evals. Instead of asking only whether the final answer is correct, the team can ask layer-specific questions. At the prompt and intent layer, did the agent stay within the approved goal? At the context layer, did untrusted content influence tool choice? At the memory layer, did a low-trust observation become durable? At the tool layer, did the agent attempt an irreversible side effect without approval? At the orchestration layer, did a subagent inherit authority it should not have had? At the governance layer, did the improvement loop preserve failing evidence?

These questions become eval fixtures. A MAESTRO threat model that remains a document will go stale. A MAESTRO-informed eval suite can run in CI, in pre-deployment review, and after incidents. The chapter’s observability patterns are therefore an implementation path for continuous threat modeling. The trace shows what happened. The eval tests whether the control still works. The evidence envelope proves which artifacts justified the decision. The governance loop updates the harness when reality changes.

## 7.13 The HarnessLab Scenario

The companion lab for this chapter is intentionally small. It does not call a live model, cloud service, or observability backend. It uses deterministic Python objects to model the evidence a production harness should preserve. This is a teaching choice. Students should be able to inspect the control pattern without first configuring a vendor stack.

The scenario begins with a risky customer notification. The raw observation includes a ticket id, a tool name, an intent, a customer email, a draft message, and a token-like string. A naive trace system might record the full observation. The harness does not. It redacts field-based sensitive data and token-like patterns before evidence emission. The redacted observation is safe to inspect. The raw observation is represented by a hash inside the replay bundle.

The harness then builds trace spans. The spans record a tool-call observation, evidence redaction, artifact hashing, benchmark regression detection, candidate acceptance, denial of an unsafe self-improvement attempt, and approval of a bounded rollout. These are not merely debug messages. They are control points. Each span supports a later decision.

Next, the scenario builds a decision trace. The trace records six steps: observe, redact, regression, hill climb, recursive self-improvement denial, and governed rollout. Each step has a decision, reason, and evidence reference. This is the minimum pattern students should carry into production designs.

The scenario then evaluates a candidate harness change. The baseline has task success of 0.84 and perfect unsafe-block, redaction-recall, and replay-pass rates. The candidate `aggressive_trace_sampling` improves task success and latency but reduces unsafe-block rate, redaction recall, and replay pass rate. The regression report marks those failed gates and returns an escalation verdict.

The hill-climbing loop then compares three candidates. `decision_reason_capture` improves the score slightly without failing gates. `aggressive_trace_sampling` improves speed and task success but fails safety gates. `redact_before_indexing` improves the composite score without weakening gates and becomes the selected candidate. This demonstrates why safety gates must remain separate from the blended score.

The scenario then models governed recursive self-improvement. One proposal tries to raise task-success weight and ignore replay failures. It is denied because it lacks evidence, rollback, and approval. Another proposal promotes redaction-before-indexing after safe eval improvement. It is accepted for supervised rollout because it includes an evidence hash, rollback checkpoint, bounded rollout status, and required controls.

Finally, the scenario creates an evidence envelope and replay bundle. The evidence envelope includes run id, actor, policy version, redaction markers, artifact hashes, and a tamper-evident hash. The replay bundle includes the raw-observation hash, redacted observation, trace, expected decision trace, expected regression verdict, and expected selected candidate. The lab verifies that raw sensitive content does not appear in the redacted observation, that redactions exist, that artifact hashes match, that regression is escalated, that the selected candidate is safe, and that governed rollout behaves as expected.

The lab’s output is a `LabResult`. The result contains a pass flag, score, summary, policy decisions, and artifacts. The saved `LabResult/` folder for Chapter 7 contains the captured `result.json`, raw `stdout.txt`, raw `stderr.txt`, and a short README. This is not only a convenience. It models the chapter’s thesis. A lab about observability should ship with observable results.

## 7.14 Implementation Guidance

A production implementation should begin with the smallest useful schema. Teams sometimes over-design observability before they have real failure cases. Others under-design it and discover too late that they cannot explain an incident. A practical starting schema includes run id, parent run id, agent id, task id, identity, intent id, policy version, tool name, tool arguments reference, data class, decision, reason, evidence reference, artifact hash, redaction markers, and timestamp. Add fields when a real review question cannot be answered.

The trace schema should be stable enough for evals. If field names change weekly, replay fixtures become brittle. If traces store only free-form text, evals become vague. If traces omit policy versions, regression review becomes guesswork. The schema should be treated like an API. Version it. Test it. Document it. Migrate it deliberately.

Instrumentation should sit at harness boundaries. Instrument the model call, tool gateway, memory service, context retrieval layer, approval service, delegation mechanism, policy engine, runtime steering controller, and data-governance router. Instrumenting only the agent loop is not enough because many important controls live outside the model call. Instrumenting only tools is not enough because intent, context, memory, and policy decisions shape tool use.

Do not record raw chain-of-thought as a default evidence artifact. The safer pattern is to record decision summaries, policy reasons, tool-call facts, structured evaluator outputs, and evidence references. If a model provides internal reasoning traces under a platform-specific feature, handle them under strict policy. In many cases, the harness can produce faithful control evidence without exposing private reasoning.

Design redaction as a pipeline, not a filter. A filter says “remove secrets.” A pipeline classifies source, decides retention tier, rewrites payload, records redaction markers, hashes raw artifacts when appropriate, routes safe evidence to trace storage, routes restricted evidence to a vault, and applies access policy. That pipeline is part of the harness.

Build evals from real traces, but sanitize them before they become fixtures. Remove or synthesize personal data. Keep hashes and references when raw data cannot be retained. Preserve the control-relevant structure. If the incident involved a poisoned instruction inside a document, the fixture needs a safe version of that pattern. If the incident involved a token-like string in a tool output, the fixture can use a fake token. If the incident involved a policy version, preserve the version semantics.

Use canaries for harness changes. A change to trace sampling, redaction, tool descriptions, routing, memory promotion, or approval thresholds can alter risk. Roll out to a narrow scope first. Monitor gates. Preserve rollback. Treat changes to evals and gates as especially sensitive. A failing eval may be annoying, but deleting it is not an improvement.

Keep human review focused. Observability should reduce human cognitive load, not flood operators with traces. Evidence envelopes, decision traces, and replay bundles should summarize what matters and link to deeper artifacts. Escalation should include the reason, failed gates, affected scope, recommended action, and rollback option. A human reviewer should not need to reconstruct the whole run from raw logs.

Finally, teach teams to read traces as arguments. A trace is not neutral just because it is structured. It claims that certain events mattered, certain decisions were justified, and certain evidence was sufficient. Reviewers should ask whether the trace omits a layer, whether redaction destroyed necessary context, whether evals measure the right target, whether gates reflect real risk, and whether the improvement loop could manipulate its own evidence.

## 7.15 Common Failure Patterns

The first failure pattern is **trace theater**. The system emits beautiful dashboards but cannot answer why a risky action was allowed. Trace theater often captures token counts, latency, and model names while omitting intent, data class, policy decision, approval status, and evidence references. It looks mature until an incident occurs.

The second failure pattern is **unsafe completeness**. The team records every prompt, output, document, tool argument, and memory item in full. This feels forensically responsible, but it creates a high-value data lake of sensitive content. The safer path is tiered evidence: redacted ordinary traces, restricted raw evidence, hashes, and replay fixtures.

The third failure pattern is **single-score optimization**. The team compresses quality, safety, privacy, latency, and cost into one score. The optimizer finds a candidate that raises the score while weakening a critical gate. The organization celebrates improvement and later discovers that replay fidelity or redaction recall degraded. Gate metrics need veto authority.

The fourth failure pattern is **eval laundering**. A failure is converted into an eval, but the eval removes the hard part. For example, a prompt-injection incident becomes a generic refusal test. A data-governance failure becomes a keyword check. A long-horizon state bug becomes a single-turn example. Good fixtures preserve the control challenge.

The fifth failure pattern is **self-improvement without separation of duties**. An agent that can propose harness changes is useful. An agent that can approve, deploy, and evaluate those changes alone is a governance risk. The more capable the agent, the more important the boundary.

The sixth failure pattern is **lost continuity**. A run pauses for approval and resumes later, but the resumed trace has no link to the original state. Reviewers cannot tell whether the approval was still valid, whether credentials rotated, or whether context was refreshed. Long-horizon work requires explicit continuity artifacts.

The seventh failure pattern is **benchmark overreach**. A team points to a leaderboard score as proof of production readiness. Benchmarks are useful evidence. They are not deployment authorization. A benchmark score should be interpreted through the system’s domain, data classes, tool permissions, human oversight, and failure tolerance.

The eighth failure pattern is **redaction opacity**. The system claims traces are redacted, but reviewers cannot tell which rule fired, what class of data was removed, or whether raw evidence exists elsewhere. Redaction should leave safe markers and evidence references.

## 7.16 Teaching and Discussion Questions

1. In the HarnessLab scenario, `aggressive_trace_sampling` improves latency and task success but fails several safety gates. Should the candidate be rejected automatically, escalated to a human, or allowed for a narrow experiment? What additional evidence would change your decision?

2. Design a decision-trace schema for a customer-support refund agent. Which fields are required to explain an approved refund, a denied refund, and an escalated refund?

3. Suppose a coding agent proposes deleting a failing eval because the eval is “obsolete.” What evidence should the harness require before accepting, modifying, or rejecting the proposal?

4. Choose one benchmark, such as τ-bench, SWE-bench, AgentBench, or Terminal-Bench. Which harness capabilities does it measure well? Which production risks does it leave mostly unmeasured?

5. A trace contains personal data because the agent retrieved a customer record and passed it to an evaluator. Design a privacy-safe replay fixture that preserves the security lesson without retaining the real customer data.

6. Map a real or hypothetical agent system to Figure 7.8. Which MAESTRO layer has the weakest observability? What incident would that weakness make difficult to investigate?

7. In a long-running agent, what should expire first: credentials, approvals, context, memory, or policy overlays? How should the trace represent each expiration?

8. When is an LLM-as-judge appropriate for agent evaluation, and when should the harness prefer deterministic checks or human review?

## 7.17 Conclusion

Observability is not a passive mirror. In long-horizon multi-agent systems, observability is part of the harness that makes autonomy governable. It captures the path from intent to action, from action to decision, from decision to evidence, and from evidence to improvement. If that path is missing, the team cannot distinguish safe agency from lucky output. If that path is unprotected, the telemetry system becomes a data leak. If that path is not connected to evals, improvement becomes anecdotal. If that path is controlled by the agent alone, recursive self-improvement becomes a governance failure.

This chapter has argued for a secure observability pattern built from decision traces, evidence envelopes, privacy-safe telemetry, replay bundles, eval gates, benchmark regression evidence, and governed hill climbing. The pattern draws from current agent research, platform practice, observability standards, threat modeling, and risk-management frameworks, but it is intentionally independent of any single vendor. Tools will change. Model names will change. Benchmarks will change. The durable unit is the evidence loop.

The HarnessLab scenario shows the pattern in compact form. A risky customer notification is observed. Sensitive telemetry is rewritten before emission. Artifact hashes are sealed. A benchmark regression is escalated. A safe hill-climbing candidate is selected. An ungoverned self-improvement proposal is denied. A bounded rollout is allowed because it includes evidence, rollback, and approval controls. That sequence is the book’s thesis in executable miniature: agents can search, adapt, and improve, but only a secure harness can make that hill climbing safe enough for production.

## References

Alibaba. 2026. “Spring AI Alibaba.” GitHub repository. Accessed July 9, 2026. https://github.com/alibaba/spring-ai-alibaba.

Alibaba Cloud Native Community. 2026. “From Black Box to Transparent: Alibaba Cloud Agent Observability and Audit Data Collection in Practice.” Alibaba Cloud Blog, June 10, 2026. https://www.alibabacloud.com/blog/from-black-box-to-transparent-alibaba-cloud-agent-observability-and-audit-data-collection-in-practice_603239.

Anthropic. 2024. “Building Effective AI Agents.” Anthropic Engineering, December 19, 2024. https://www.anthropic.com/engineering/building-effective-agents.

Anthropic. 2025a. “Effective Context Engineering for AI Agents.” Anthropic Engineering, September 29, 2025. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents.

Anthropic. 2026a. “Monitoring.” Claude Code Docs. Accessed July 9, 2026. https://code.claude.com/docs/en/monitoring-usage.

Anthropic. 2026b. “Agent SDK Reference: Python.” Claude Code Docs. Accessed July 9, 2026. https://code.claude.com/docs/en/agent-sdk/python.

Anthropic. 2026c. “Best Practices for Claude Code.” Claude Code Docs. Accessed July 9, 2026. https://code.claude.com/docs/en/best-practices.

Anthropic. 2026d. “Streaming Input.” Claude Code Docs. Accessed July 9, 2026. https://docs.anthropic.com/en/docs/claude-code/sdk/streaming-vs-single-mode.

Google Cloud. 2026. “Agent Observability.” Google Cloud Observability Documentation. Accessed July 9, 2026. https://docs.cloud.google.com/stackdriver/docs/observability/agent-observability.

Huang, Ken. 2025. “Agentic AI Threat Modeling Framework: MAESTRO.” Cloud Security Alliance, February 6, 2025. https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro.

ISO. 2023. “ISO/IEC 42001:2023: Artificial Intelligence Management System.” International Organization for Standardization. https://www.iso.org/standard/42001.

LangChain. 2026a. “Profiles.” Deep Agents Documentation. Accessed July 9, 2026. https://docs.langchain.com/oss/python/deepagents/profiles.

LangChain. 2026b. “The Agent Improvement Loop Starts with a Trace.” LangChain Blog, 2026. https://www.langchain.com/blog/traces-start-agent-improvement-loop.

Shi, Lin, Chiyu Ma, Wenhua Liang, Weicheng Ma, and Soroush Vosoughi. 2024. “Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge.” arXiv. https://arxiv.org/abs/2406.07791.

Liang, Percy, Rishi Bommasani, Tony Lee, Dimitris Tsipras, Dilara Soylu, Michihiro Yasunaga, Yian Zhang, et al. 2022. “Holistic Evaluation of Language Models.” arXiv. https://arxiv.org/abs/2211.09110.

Liu, Xiao, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu, et al. 2023. “AgentBench: Evaluating LLMs as Agents.” arXiv. https://arxiv.org/abs/2308.03688.

Madaan, Aman, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, et al. 2023. “Self-Refine: Iterative Refinement with Self-Feedback.” arXiv. https://arxiv.org/abs/2303.17651.

NIST. 2024. “Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile.” NIST AI 600-1. National Institute of Standards and Technology. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf.

NVIDIA. 2026a. “NVIDIA NeMo Agent Toolkit Overview.” NVIDIA Documentation. Accessed July 9, 2026. https://docs.nvidia.com/nemo/agent-toolkit/latest/index.html.

NVIDIA. 2026b. “Security Considerations.” NVIDIA NeMo Agent Toolkit Documentation. Accessed July 9, 2026. https://docs.nvidia.com/nemo/agent-toolkit/1.5/resources/security-considerations.html.

NVIDIA. 2026c. “NVIDIA AI-Q Blueprint for Intelligent Agents.” NVIDIA Build. Accessed July 9, 2026. https://build.nvidia.com/nvidia/aiq.

OpenAI. 2026a. “Tracing.” OpenAI Agents SDK Documentation. Accessed July 9, 2026. https://openai.github.io/openai-agents-python/tracing/.

OpenAI. 2026b. “Build an Agent Improvement Loop with Traces, Evals, and Codex.” OpenAI Cookbook, 2026. https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop.

OpenAI. 2026c. “Evaluation Best Practices.” OpenAI API Documentation. Accessed July 9, 2026. https://developers.openai.com/api/docs/guides/evaluation-best-practices.

OpenAI. 2026d. “Agent Orchestration.” OpenAI Agents SDK Documentation. Accessed July 9, 2026. https://openai.github.io/openai-agents-python/multi_agent/.

OpenTelemetry. 2025. “AI Agent Observability: Evolving Standards and Best Practices.” OpenTelemetry Blog, 2025. https://opentelemetry.io/blog/2025/ai-agent-observability/.

OpenTelemetry. 2026. “GenAI Attributes.” OpenTelemetry Semantic Conventions Registry. Accessed July 9, 2026. https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/.

Shinn, Noah, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao. 2023. “Reflexion: Language Agents with Verbal Reinforcement Learning.” arXiv. https://arxiv.org/abs/2303.11366.

SWE-bench. 2026. “SWE-bench Leaderboards.” Accessed July 9, 2026. https://www.swebench.com/.

Terminal-Bench. 2026. “Terminal-Bench 2.0 Leaderboard.” Accessed July 9, 2026. https://www.tbench.ai/leaderboard/terminal-bench/2.0.

Ye, Jiayi, Yanbo Wang, Yue Huang, Dongping Chen, Qihui Zhang, Nuno Moniz, Tian Gao, Werner Geyer, Chao Huang, Pin-Yu Chen, Nitesh V. Chawla, and Xiangliang Zhang. 2024. “Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge.” arXiv. https://arxiv.org/abs/2410.02736.

Yao, Shunyu, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. 2022. “ReAct: Synergizing Reasoning and Acting in Language Models.” arXiv. https://arxiv.org/abs/2210.03629.

Yao, Shunyu, Noah Shinn, Pedram Razavi, and Karthik Narasimhan. 2024. “τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains.” arXiv. https://arxiv.org/abs/2406.12045.

Zheng, Lianmin, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu, Yonghao Zhuang, Zi Lin, et al. 2023. “Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.” arXiv. https://arxiv.org/abs/2306.05685.
