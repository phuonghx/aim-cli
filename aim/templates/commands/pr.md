---
description: Clean up code, stage changes, and prepare a pull request
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(npm test:*), Bash(npm run lint:*)
---

# Pull Request Preparation Checklist

Before creating a PR, execute these steps:

1. Run formatting and linting as configured in the project.
2. Run test suite: `git diff HEAD` to see what changed, and run tests.
3. Review git diff: `git diff HEAD`.
4. Stage changes: `git add .`.
5. Suggest or create commit message following conventional commits format.
6. Generate a comprehensive PR description containing:
   - **Summary**: What changed and why.
   - **Technical Details**: Brief summary of the implementation approach.
   - **Verification**: Tests run and verification results (e.g. build logs, command outputs).
   - **Impact**: Potential side effects or dependencies.
