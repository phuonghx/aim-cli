---
name: geo-fundamentals
description: Tactics for getting content surfaced and cited by generative answer engines such as Perplexity, ChatGPT, Gemini, and other LLM-driven assistants. Covers how retrieval pipelines pick sources, which on-page signals raise citation odds, entity reputation, crawler access, and ways to track mentions. Use it when shaping pages so AI assistants quote them, or when auditing existing content for citation readiness.
---

# Generative Engine Optimization (GEO)

The goal here is narrow: get a page quoted inside an AI-generated answer, not just ranked on a results page. This file explains the levers that move that needle.

---

## How GEO differs from classic SEO

Search optimization tries to win a position in a ranked list a human scrolls through. GEO tries to become the passage a language model pulls into its synthesized reply. The overlap is real, but the targets diverge:

- **Outcome that matters** -- a citation or named mention, not a click-through rank.
- **Where it happens** -- inside answer engines (Perplexity, ChatGPT browsing, Gemini, Copilot), not the ten blue links.
- **What you tune for** -- extractable facts, named entities, and trust markers rather than keyword density alone.
- **How you measure** -- how often the brand is referenced in answers, versus rank tracking and CTR.

---

## The answer-engine field

Each assistant cites a little differently, which changes where the easy wins are.

- **Perplexity** -- attaches inline numbered references; tends to cite generously, so it is the friendliest starting target.
- **ChatGPT** -- mixes inline mentions and footnote-style links when browsing; custom GPTs open extra surface area.
- **Gemini** -- leans on a sources block and inherits a lot from Google's index, so SEO work carries over.
- **Reasoning-first engines** -- favor thorough, well-structured long-form material when reasoning over a topic.

---

## What the retrieval layer rewards

Answer engines run a retrieval-augmented pipeline: they pull candidate passages, rank them, then write over the top results. Rough influence of each signal:

| Signal | Approximate pull |
|--------|------------------|
| Meaning match to the query (embeddings) | strongest |
| Source authority and reputation | strong |
| Topical / keyword overlap | moderate |
| Spread across independent sources | moderate |
| Recency of the page | smaller but real |

Takeaway: write the passage that *most precisely answers* the likely question, from a source the model already trusts.

---

## Passages that tend to get quoted

Models lift self-contained chunks that read as a complete answer on their own.

- **Numbers you produced** -- proprietary figures and survey results are uniquely quotable.
- **Named-source statements** -- a quote with a real person and title transfers credibility.
- **Tight definitions** -- one or two sentences that fully define a term.
- **Ordered procedures** -- numbered how-to steps are easy to extract verbatim.
- **Side-by-side tables** -- structured comparisons map cleanly into answers.
- **Question-and-answer blocks** -- a heading phrased as the user's question, answered right below.

---

## On-page readiness review

### Editorial layer
- [ ] Headings written as the questions readers actually ask
- [ ] A short answer or summary near the very top of the page
- [ ] First-party data, with the source named
- [ ] Quotes attributed to a real name and role
- [ ] A handful of question/answer pairs
- [ ] Plain, lift-ready definitions of key terms
- [ ] A visible "updated on" date
- [ ] A bylined author with stated credentials

### Markup layer
- [ ] Article structured data carrying publish and update dates
- [ ] Author represented with Person structured data
- [ ] Q&A content marked up as FAQPage
- [ ] Quick render and stable layout (LCP comfortably under ~2.5s)
- [ ] Semantic, uncluttered HTML

---

## Establishing the entity

Models trust sources they can resolve to a known entity. Strengthen that resolution by:

- Earning a Google Knowledge Panel so the brand is a recognized thing.
- Securing a Wikipedia entry where genuine notability exists.
- Keeping name, role, and descriptions identical everywhere they appear.
- Collecting references from recognized publications in the field.

---

## Letting the AI crawlers in

If citations are the goal, the relevant bots have to be able to fetch the pages.

| User-agent | Belongs to |
|------------|-----------|
| `GPTBot` | OpenAI / ChatGPT |
| `ClaudeBot` | Claude |
| `PerplexityBot` | Perplexity |
| `Googlebot` | Google, shared with Gemini |

Pick a posture in `robots.txt`:

- **Open everything** when maximum citation reach is the priority.
- **Block a specific bot** to opt out of one vendor's training while allowing others.
- **Mix it** -- permit the engines you care about, exclude the rest.

---

## Tracking whether it works

There is no clean dashboard yet, so combine proxies:

- Pose target questions to the assistants and watch for brand references.
- Search inside the tools for "according to [brand]" style phrasing.
- Run the same prompts for rivals and compare who gets cited.
- Tag any outbound links the answers expose with UTM parameters to catch referral traffic.

---

## Habits to drop

- Shipping undated pages -> stamp publish and update dates.
- Hand-wavy "studies show" claims -> name the study or source.
- Anonymous content -> attach a credentialed author.
- Shallow coverage -> answer the question completely.

---

> Bottom line: assistants quote the clearest, best-sourced, easiest-to-lift answer on a topic. Write that answer.

---

## Script

| Script | What it does | How to run |
|--------|--------------|------------|
| `scripts/geo_checker.py` | Audits public pages for AI-citation readiness | `python scripts/geo_checker.py <project_path>` |
