---
description: Manage and rewrite project documentation. Use this to list, view, create, or rewrite documentation under .ai-context/docs/.
---

# /aim-docs - Documentation Management

Create, update, view, or rewrite high-quality documentation files under the `.ai-context/docs/` directory to maintain a clear and up-to-date project context.

---

## 🔴 CRITICAL RULES

1. **Hierarchy Integrity** - Use exactly one `<h1>` per page. Ensure clean heading levels (`##`, `###`).
2. **No Placeholders** - Documentation must be complete. Write real descriptions, parameters, and code examples without placeholders or TODO comments.
3. **Cross-Referencing** - Link to tasks using `@task-N`, and reference other docs using `@doc/<path>`.
4. **Accuracy** - Ensure that documentation matches the current codebase exactly. Do not describe outdated features or APIs.

---

## Task

Manage documentation based on the user's request:

1. **Discover Docs**:
   - Run `aim doc list` to see all current documentation files.
2. **Read/Analyze**:
   - Use `aim doc view <path>` (e.g. `aim doc view architecture/auth`) to read existing content.
3. **Create or Rewrite**:
   - To create a new doc: Run `aim doc create "<title>" -d "<desc>" -f [folder]` to initialize the template, then fill it.
   - To rewrite/update an existing doc: Read the file, make the necessary modifications using file edit tools, and ensure proper metadata is retained.
4. **Verify References**:
   - Run `aim validate` to ensure all links and references in the documentation are healthy and pointing to valid targets.

---

## Expected Output

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Documentation File | `.ai-context/docs/{folder}/{slug}.md` | Complete, well-structured markdown file with description metadata, overview, details, and code examples. |
| References Check | `aim validate` output | Clean report with no broken `@doc` or `@task` links. |

---

## Usage

```bash
/aim-docs list
/aim-docs view architecture/auth
/aim-docs create "Authentication Guide" -d "Details how Cognito and JWT auth is configured"
```
