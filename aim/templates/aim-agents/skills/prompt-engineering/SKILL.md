---
name: prompt-engineering
description: Designs production prompts for LLM-powered features — clear instructions, role/system prompts, few-shot examples, structured output schemas, delimiter structuring, and reasoning strategy. Use when building or debugging an LLM feature (extraction, classification, generation, agents), when output is inconsistent or off-format, or when authoring a reusable prompt template. Not for casual chat tricks.
---

# Prompt Engineering

> Treat prompts as code: explicit, structured, versioned, and tested.

## Core principles

- **Be explicit, not clever.** State the task, constraints, and output format directly. The model cannot read intent you did not write.
- **Show the shape of success.** A correct example beats a paragraph of description.
- **Separate the stable from the variable.** Put fixed rules in the system prompt; inject per-request data in the user turn.
- **Constrain the output.** Define the exact format you will parse. Unconstrained prose is unparseable.
- **One job per prompt.** If a prompt does extraction *and* summarization *and* routing, split it.

## Anatomy of a production prompt

| Section | Purpose | Goes in |
|---|---|---|
| Role / persona | Set domain + tone | System |
| Task instruction | What to do, imperatively | System |
| Rules / constraints | Hard limits, do/don't | System |
| Output schema | Exact format to return | System |
| Few-shot examples | Demonstrate edge cases | System |
| Input data | The thing to process | User |

## Clear instructions checklist

- [ ] Task stated as an imperative ("Extract...", "Classify...", not "Can you...").
- [ ] Audience and tone specified if it matters.
- [ ] Edge cases named: empty input, ambiguous input, no valid answer.
- [ ] An explicit escape hatch: what to output when the model cannot comply (e.g. `{"error": "insufficient_context"}`).
- [ ] Ordering matters — put the most important constraint first and last (models weight both ends).

## Role / system prompts

Set durable behavior once, not per request.

```
You are a support-ticket triage engine for a B2B SaaS product.
You classify tickets and never address the customer directly.
You only ever return JSON matching the schema. No prose, no apologies.
```

Keep the role functional ("triage engine") over theatrical ("world-class expert"). Function drives behavior; flattery does not.

## Delimiter / XML structuring

Wrap distinct parts in named tags so the model never confuses instructions with data. This also blunts prompt injection from user content.

```
<instructions>
Summarize the review in one sentence. Output only the sentence.
</instructions>

<review>
{{user_review}}
</review>
```

Use tags (`<document>`, `<example>`, `<context>`) or fenced blocks. Pick one convention and keep it consistent across your templates.

## Few-shot examples

- 2–5 examples usually suffice; add examples for the cases that fail, not the easy ones.
- Cover the boundaries: the tricky class, the null case, the "do not answer" case.
- Match the exact output format you want — the model mimics structure precisely.
- Keep label balance realistic; do not stack all examples of one class together.

```
<example>
input: "App crashes every time I export a PDF"
output: {"category": "bug", "severity": "high"}
</example>
<example>
input: "How do I change my billing email?"
output: {"category": "how_to", "severity": "low"}
</example>
```

## Structured output

Prefer schema-enforced output (JSON mode / function-calling / constrained decoding) over "please return JSON". When you must rely on the prompt:

- Give the literal schema, with types and which fields are required.
- Specify enum values explicitly: `"severity": one of ["low","medium","high"]`.
- Forbid extra keys and surrounding prose.
- Always parse defensively: validate against the schema; on failure, repair-prompt or retry rather than trusting the string.

## Reasoning: chain-of-thought vs direct

| Use direct (no CoT) | Use step-by-step reasoning |
|---|---|
| Classification, extraction, lookup | Multi-step math, logic, planning |
| Latency/cost sensitive | Accuracy matters more than speed |
| Output is a fixed schema | Decision needs justification |

When you need reasoning but a clean output, keep the thinking out of the parsed payload — e.g. put it in a `reasoning` field you ignore, or a separate `<scratchpad>` you strip. Do not let free-form reasoning leak into the field you parse.

## Decomposition

When a single prompt is unreliable, break the task into a chain where each step has one job and a checkable output:

```
1. extract  → pull raw fields from the document   → JSON
2. validate → check fields against business rules  → JSON + errors[]
3. format   → render the final user-facing message → text
```

Each stage is independently testable and swappable. Prefer this over one mega-prompt that tries to do everything.

## Prompt templates and versioning

- Store prompts as files/constants, never inline string-concatenation scattered in code.
- Use named placeholders (`{{ticket_body}}`), not positional `%s`.
- Version every prompt (`triage.v3`) and log which version produced each output.
- Pin the model id alongside the prompt version — prompt behavior is model-specific.
- Changing a prompt is a code change: review it, and re-run your eval set (see the `llm-evaluation` skill) before shipping.

## Common failure modes and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Output drifts in/out of JSON | Format not enforced | Use schema/JSON mode; add output example |
| Model invents fields/values | No closed vocabulary | List allowed enums; forbid extra keys |
| Ignores a rule | Buried mid-prompt | Move rule to start AND end; make it its own line |
| Hallucinates when unsure | No escape hatch | Add explicit "if unknown, return X" |
| Verbose preamble ("Sure! Here…") | No output constraint | "Output only the JSON. No other text." |
| User text overrides instructions | Injection | Wrap user data in delimiters; restate the rule after it |
| Inconsistent across runs | Ambiguous task / high temperature | Tighten wording; lower temperature; add few-shot |

## Before / after

**Before** (vague, unparseable, no guardrails):

```
Tell me what this customer email is about and how urgent it is.

{{email}}
```

**After** (scoped role, delimited input, closed schema, escape hatch):

```
You are a triage engine. Classify the email below.
Return ONLY JSON: {"category": <one of ["bug","billing","how_to","other"]>,
"urgency": <one of ["low","medium","high"]>}.
If the email is empty or unintelligible, return {"category":"other","urgency":"low"}.

<email>
{{email}}
</email>
```

The "after" version is deterministic to parse, resists injection, handles the empty case, and can be regression-tested.
