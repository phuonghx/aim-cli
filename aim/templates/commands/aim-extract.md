---
description: Extract reusable project decisions, rules, schemas, or patterns into memory or docs
---

# Extract Project Memory & Patterns

Analyze the current session, recent modifications, or code files, and extract reusable rules, schemas, decisions, or architectural patterns into AIM's persistent context.

Instructions:
1. Examine recently modified files (e.g. using `git status -s` or reviewing diffs) and chat history to identify reusable decisions, coding rules, patterns, schemas, or constraints.
2. For micro-rules, decisions, or conventions, add them to AIM memories using `aim memory add`:
   - Project-specific rule: `aim memory add "Rule/Decision description" -c [decision|syntax|pattern] -l project --importance [1-10]`
   - Global user preference: `aim memory add "Preference description" -c [decision|syntax|pattern] -l global`
3. For comprehensive guides, APIs, or architectural designs, create a doc file:
   - `aim doc create "Title" -d "Summary description" -f [folder]`
4. Run `aim sync` to compile the new context into active rules.
