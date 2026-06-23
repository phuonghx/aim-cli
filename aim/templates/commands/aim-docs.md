---
description: Create, read, update, list, or rewrite project-level documentation
---

# Documentation Management

Manage documentation files under the `.ai-context/docs/` directory to maintain a clear and up-to-date project context.

Instructions:
1. If listing docs is requested, run `aim doc list` to see all current documentation files.
2. If viewing a doc is requested, run `aim doc view <path>` (e.g. `aim doc view architecture/auth`) to read it.
3. If creating or rewriting a doc is requested:
   - To create: Run `aim doc create "<title>" -d "<desc>" -f [folder]` to initialize the document template.
   - To rewrite: Use file editing tools to update the markdown file under `.ai-context/docs/` (retaining proper metadata at the top).
   - Ensure the rewrite contains clear structure (single H1, metadata block, overview), practical code examples (no placeholders), and cross-references (`@task-N` or `@doc/<path>`).
4. Run `aim validate` to ensure all links and references in the documentation are healthy and pointing to valid targets.
