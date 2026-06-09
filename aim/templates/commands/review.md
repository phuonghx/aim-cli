---
description: Perform a comprehensive code review focusing on style, bugs, and security
---

# Code Review Checklist

Perform a code review of the target files or staged changes. Focus on:

1. **Correctness & Logic**: Are there logic errors, boundary conditions missed, or off-by-one issues?
2. **Security & Vulnerabilities**: Are there hardcoded secrets, injection vectors, unvalidated inputs, or authorization gaps?
3. **Readability & Code Style**: Does the code match the project conventions? Is naming clear and descriptive? Are there too many nested blocks?
4. **Error Handling**: Are errors caught and handled gracefully? Are resources closed in finalizers/try-catch?
5. **Testing**: Are there associated unit tests for the new changes? Are the tests thorough?

Present your feedback in a structured format:
- **Files/Lines Reviewed**
- **Issues Found** (categorized by severity: Security, Bug, Style, Enhancement)
- **Suggested Improvements** with code snippets.
