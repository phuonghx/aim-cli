---
name: receiving-code-review
description: Guides an engineer or agent through ingesting code-review feedback and revising well — triaging comments into must-fix, nit, and question, replying to each without defensiveness, grouping related changes, pushing back with evidence when warranted, and re-requesting review. Use when a pull request has review comments to address or changes were requested. Complements the authoring side of reviewing.
allowed-tools: Read, Glob, Grep, Edit, Bash
effort: low
---

# Receiving Code Review

> Feedback is data about the change, not a verdict on you. Triage it, act, reply.

---

## The Loop

```
Read all comments → Triage → Act (grouped) → Reply to each → Re-request review
        ↑                                                          │
        └──────────────── repeat until approved ───────────────────┘
```

Read **every** comment before touching code — later comments often reframe earlier ones.

---

## Triage Each Comment

| Bucket | Meaning | Action |
|--------|---------|--------|
| 🔴 **Must-fix** | Bug, security issue, broken contract, blocking concern | Fix before merge |
| 🟡 **Should-fix** | Real improvement, maintainability, clarity | Fix, or defer with a tracked follow-up |
| 🟢 **Nit** | Style/taste, non-blocking | Apply if cheap; it's polite to |
| ❓ **Question** | Reviewer is unsure, not (yet) asking for a change | Answer; a change may or may not follow |
| 💬 **Discussion** | Design disagreement | Resolve in thread before coding |

When a bucket is ambiguous, ask the reviewer rather than guessing.

---

## Respond to Every Comment

Leave **no comment unanswered** — silence reads as "ignored."

- Made the change → reply `Done` (link the commit if not auto-linked).
- Disagree → give a one-line rationale and propose an alternative.
- Need clarification → ask a specific question, not "what do you mean?"
- Out of scope → acknowledge and link the follow-up issue.

### Sample Reply Patterns

```text
✅ Agreeing:
   Good catch — fixed in a3f9c21. Added a test for the null case too.

🤔 Pushing back (with evidence, not ego):
   I left this synchronous on purpose: it runs once at startup and the async
   version complicated error handling (see benchmark in the thread). Open to
   changing if you still prefer async.

❓ Clarifying:
   Do you mean validate at the API boundary, or also in the service layer?
   I went with the boundary to keep the service pure.

📌 Deferring:
   Agreed this needs refactoring, but it's outside this PR's scope.
   Filed #482 and linked it.
```

---

## Group Your Changes

Don't push one commit per comment.

- **Batch by theme:** one commit for "address review: error handling", another
  for "address review: naming". Reviewers re-read faster.
- Keep revision commits **separate from** original commits so the diff-since-review
  is reviewable; squash on merge.
- Push once after a coherent batch, not after every edit (avoids notification spam
  and half-applied states).

---

## When to Push Back

Pushing back is part of good review — do it with rationale, not defensiveness.

✅ **Legitimate:**
- The suggestion introduces a bug or regresses performance (show the evidence)
- It contradicts an agreed design or another reviewer
- It's genuinely out of scope — offer a follow-up issue
- A factual misunderstanding — clarify, link the code

❌ **Not legitimate:**
- "It works on my machine" / "I've always done it this way"
- Defending taste as correctness
- Arguing to avoid the rework

If a thread goes 2–3 rounds without converging, escalate to a synchronous chat
and summarize the decision back in the thread.

---

## Avoiding Defensiveness

- Separate the code from yourself — "the function" not "my function."
- Assume good intent; a terse comment is usually brevity, not hostility.
- Thank reviewers for catches, especially the ones that sting.
- If a comment frustrates you, draft the reply, then re-read it before sending.

---

## Before Re-Requesting Review

- [ ] Every comment has a reply or resolution
- [ ] All 🔴 must-fixes addressed; deferrals are tracked with issue links
- [ ] Changes grouped into themed commits
- [ ] Tests added/updated for fixed bugs; full suite green locally
- [ ] No unrelated/scope-creep changes snuck in
- [ ] PR description updated if behavior changed
- [ ] Re-requested review (don't merge on stale approval after big changes)

---

## Pairs With

- **code-review-checklist** — the giving side; mirror its 🔴/🟡/🟢/❓ severities.
- **conventional-commits** — name revision commits, e.g. `fix(auth): handle null token`.
- **`/pr` flow** — push the grouped fixups, then re-request review on the same PR.

---

> **Remember:** the goal isn't to win the thread — it's a correct change and a
> reviewer who can confidently approve. Fast, gracious iteration beats a perfect
> first push.
