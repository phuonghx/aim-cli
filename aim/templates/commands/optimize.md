---
description: Analyze code for performance issues and suggest optimizations
---

# Code Optimization

Review the provided code or workspace changes for the following issues in order of priority:

1. **Performance Bottlenecks** - Identify O(n²) or inefficient loops, redundant operations, and heavy computations.
2. **Memory & Resource Efficiency** - Find potential leaks, unreleased resources, circular references, or heavy memory consumption.
3. **Data Structure & Algorithms** - Suggest more optimal structures or algorithms.
4. **Caching & Memoization** - Highlight repeated computations that could benefit from caching.
5. **Concurrency & Async** - Point out race conditions, blocking calls, or unoptimized asynchronous operations.

Format your response with:
- **Issue Severity** (Critical / High / Medium / Low)
- **Location in Code** (File and line range)
- **Problem Statement**: Brief explanation of the bottleneck.
- **Recommended Solution**: Recommended code refactoring with explanation.
