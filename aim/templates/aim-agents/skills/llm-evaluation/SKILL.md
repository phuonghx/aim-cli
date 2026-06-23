---
name: llm-evaluation
description: Builds evaluation systems for LLM features and agents — golden datasets, metrics (exact match, rubric/LLM-as-judge, pass@k), offline and online evals, and regression on a fixed set. Use when a prompt or model change needs to be measured rather than guessed, when adding a new LLM feature, or when output quality is drifting. Establishes a measure-before-ship loop so changes are proven, not hoped.
---

# LLM Evaluation

> If you cannot measure it, you are tuning prompts in the dark. Build the eval before you tune.

## When to add evals

- Before tuning a prompt or swapping models — you need a baseline.
- When shipping any LLM feature that real users or systems depend on.
- After every production bug — turn the failing input into a permanent test case.
- When "it feels better" is the only evidence a change is an improvement.

Skip formal evals only for throwaway scripts. Anything that ships gets at least a small fixed set.

## Build a golden dataset

A golden set is a fixed collection of `(input, expected)` pairs that defines "correct" for your task.

- **Start small, start real.** 20–50 hand-curated cases beat 5,000 synthetic ones. Grow over time.
- **Cover the distribution:** common cases, edge cases, the null/empty case, and known past failures.
- **Freeze it.** The set must be stable so scores are comparable across runs. Version it (`eval/v2`).
- **Label deliberately.** Each `expected` should be defensible; ambiguous labels poison every metric.
- **Keep it in the repo**, reviewed like code.

## Avoid leakage

Leakage = your eval secretly rewards memorization or itself, inflating scores.

- Do not put eval examples into the prompt's few-shot block. Test and demonstration sets must be disjoint.
- Do not tune the prompt by staring at eval *answers* — tune on a separate dev split, report on a held-out split.
- Watch for train/test contamination when inputs come from public data the model may have seen.
- If you use an LLM judge, the judge should not be the same call that produced the answer.

## Metrics: pick by task

| Metric | Use for | How |
|---|---|---|
| Exact / normalized match | Classification, extraction, enums | Compare after normalizing case/whitespace |
| Field-level / JSON match | Structured output | Compare per key; report which fields fail |
| Rubric (LLM-as-judge) | Open-ended generation, summaries | Score against an explicit rubric, 1–5 |
| pass@k | Code / tasks with a verifier | Sample k; pass if any sample passes the check |
| Task success | Agents / tool use | Did it reach the goal state? (programmatic check) |
| Regression rate | Any fixed set | % of previously-passing cases now failing |

Prefer a programmatic check (exact match, schema validation, unit test) whenever the task allows — it is cheap, deterministic, and leak-proof. Reserve LLM-as-judge for genuinely open-ended output.

## LLM-as-judge, done safely

- Give the judge an explicit rubric and a scale; do not ask "is this good?".
- Force structured output from the judge (e.g. `{"score": 1-5, "reason": "..."}`) and log the reason.
- Calibrate the judge against human labels on a sample before trusting it at scale.
- Reduce position/verbosity bias: randomize order in pairwise comparisons; do not reward length.
- Pin the judge model + judge-prompt version; a judge change invalidates historical scores.

## Offline vs online

| | Offline | Online |
|---|---|---|
| Runs on | Fixed golden set, in CI | Real production traffic |
| Answers | "Did this change regress anything?" | "Does it work for real users?" |
| Signals | Pass rate, regression count | A/B metrics, thumbs up/down, task completion |
| Speed | Fast, deterministic, pre-merge | Slow, noisy, post-deploy |

Use both: offline to gate merges, online to validate real-world impact. Online comparisons track **with-feature vs baseline** (control), not feature-vs-nothing.

## Eval-driven development loop

```
1. Write/extend the golden set for the behavior you want.
2. Run the current prompt → record baseline score.
3. Change ONE thing (prompt, model, params).
4. Re-run the SAME set → compare to baseline.
5. Keep the change only if it wins overall AND regresses nothing critical.
6. Add any new failure you found as a permanent case. Go to 1.
```

Change one variable at a time, or you cannot attribute the delta.

## Minimal eval-loop example

```python
# golden set: fixed (input, expected) pairs
cases = [
    {"input": "App crashes on PDF export", "expected": "bug"},
    {"input": "How do I change billing email?", "expected": "how_to"},
    {"input": "",                               "expected": "other"},  # null case
]

def run(model_fn, prompt_version):
    results = []
    for c in cases:
        got = model_fn(c["input"])          # the LLM feature under test
        ok = got.strip().lower() == c["expected"]   # exact-match metric
        results.append({"input": c["input"], "got": got,
                        "expected": c["expected"], "pass": ok})
    score = sum(r["pass"] for r in results) / len(results)
    return score, results

base_score, _   = run(triage_v2, "v2")      # baseline
new_score, fails = run(triage_v3, "v3")     # candidate

print(f"v2={base_score:.2%}  v3={new_score:.2%}  delta={new_score-base_score:+.2%}")
regressions = [r for r in fails if not r["pass"]]   # inspect what broke
assert new_score >= base_score, "v3 regressed — do not ship"
```

The shape is always the same: **inputs → run → score → compare**. Swap the scorer (schema check, pass@k, judge) per task; keep the loop.

## Track over time

- Store every run: prompt version, model id, params, per-case results, aggregate score.
- Plot score per version so you can see drift and catch silent regressions.
- Gate merges on the eval in CI; fail the build on regression of critical cases.
- Re-run evals when the upstream model changes — provider updates can move scores with no code change.

## Checklist

- [ ] Golden set exists, versioned, covers edge + null + past-bug cases.
- [ ] Demonstration (few-shot) and eval sets are disjoint.
- [ ] Metric matches task; programmatic check used where possible.
- [ ] Baseline recorded before any change.
- [ ] One variable changed per experiment.
- [ ] New production failures become permanent cases.
- [ ] Eval runs in CI and gates merges.
