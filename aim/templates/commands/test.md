---
description: Target untested branches and edge cases to expand unit test coverage
---

# Expand Unit Tests

Expand the unit test suite for the specified file or module:

1. **Analyze Coverage**: Identify untested branches, functions, and error cases in the target file.
2. **Determine Testing Framework**: Use the project's configured test runner and libraries (e.g. Jest, Vitest, pytest, Go test).
3. **Write Tests**:
   - Focus on edge cases (null inputs, empty strings, boundary values, max/min limits).
   - Target error handling paths and exceptions.
   - Verify asynchronous flows and mock external API dependencies.
4. **Consistency**: Maintain existing test file patterns (e.g., `*.test.ts`, `*_test.go`, `test_*.py`) and coding style.

Output the new test code blocks with a brief explanation of what scenarios they cover.
