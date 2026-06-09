import os
import json
import sys

def find_project_root():
    # Look for .ai-context in current directory, then parent directory
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, ".ai-context", "config.json")):
        return cwd
    parent = os.path.dirname(cwd)
    if os.path.exists(os.path.join(parent, ".ai-context", "config.json")):
        return parent
    # Fallback to the directory of this script's parent if it exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_parent = os.path.dirname(script_dir)
    if os.path.exists(os.path.join(script_parent, ".ai-context", "config.json")):
        return script_parent
    return cwd

def load_config(root_dir):
    config_path = os.path.join(root_dir, ".ai-context", "config.json")
    if not os.path.exists(config_path):
        print(f"[-] Configuration file not found at {config_path}")
        print("[-] Please run setup.py first to initialize the configuration.")
        sys.exit(1)
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

SKILLS_INDEX_MD = """
## Modular Skills & Agent Personas (Load On-Demand to Save Tokens)
When working on specific tasks, read and load these modular rules to guide your implementation:
- **Memory & Cross-Referencing:** `.ai-context/skills/project-memory/SKILL.md` (Read when creating docs, referencing files, or managing tasks)
- **Agent Orchestration & Coordination:** `.ai-context/skills/agent-orchestration/SKILL.md` (Read when coordinating subagents, choosing specialist roles, or managing long conversation histories)
- **Token Optimization & Command Guidelines:** `.ai-context/skills/token-optimizer/SKILL.md` (Read when running shell commands, executing test suites, or doing search operations)

### Specialist Agent Suite & Workflows (.aim-agents/)
You have access to 20 specialized personas, 45 skills, and 13 workflows provided by AIM:
- **Specialist Personas:** `.aim-agents/agent/` (Includes `frontend-specialist.md`, `backend-specialist.md`, `database-architect.md`, `devops-engineer.md`, `security-auditor.md`, `debugger.md`, `orchestrator.md`, etc.)
- **Advanced Domain Skills:** `.aim-agents/skills/` (Includes `nextjs-react-expert/`, `web-design-guidelines/`, `api-patterns/`, `testing-patterns/`, `python-patterns/`, `database-design/`, `systematic-debugging/`, etc.)
- **Agentic Workflows:** `.aim-agents/workflows/` (Includes rules for `/brainstorm`, `/coordinate`, `/plan`, `/debug`, `/verify`, `/remember`, etc.)
"""

def generate_claude_md(config):
    tech_stack_str = "\n".join([f"- {item}" for item in config.get("techStack", [])])
    conventions_str = "\n".join([f"- {item}" for item in config.get("conventions", [])])
    constraints_str = "\n".join([f"- {item}" for item in config.get("constraints", [])])
    
    custom_rules = config.get("customRules", {}).get("claude", [])
    custom_rules_str = "\n".join([f"- {item}" for item in custom_rules]) if custom_rules else "- Follow standard programming practices."

    commands = config.get("commands", {})
    build_cmd = commands.get("build", "")
    test_cmd = commands.get("test", "")
    lint_cmd = commands.get("lint", "")
    format_cmd = commands.get("format", "")

    content = f"""# CLAUDE.md — Claude Code Project Guidelines

**Project Name:** {config.get("projectName", "My Project")}
**Description:** {config.get("projectDescription", "")}

## Technology Stack
{tech_stack_str}

## Core Commands
- **Build/Compile:** `{build_cmd}`
- **Run Tests:** `{test_cmd}`
- **Lint Code:** `{lint_cmd}`
- **Format Code:** `{format_cmd}`

## Coding Conventions
{conventions_str}

## Constraints & Safety Rules
{constraints_str}

## Claude-Specific Custom Instructions
{custom_rules_str}
{SKILLS_INDEX_MD}
---

## Token-Saving Command Optimization (RTK)
When running shell commands inside Claude Code, use the following rules to conserve token usage:
1. **Prefer targeted commands:** Avoid listing entire directories or reading massive files when specific tools or lines can be targeted.
2. **Compact Git:** Use `git status -s` or `git diff --stat` for initial context before pulling full diffs.
3. **Filter Test Output:** If tests fail, run only the failing tests rather than the entire suite if possible.
4. **Use CLI Output Wrappers:** When running commands with excessive verbose logs, pipe output or use filtering tools to return only errors or warnings.
"""
    return content

def generate_antigravity_md(config):
    tech_stack_str = "\n".join([f"- {item}" for item in config.get("techStack", [])])
    conventions_str = "\n".join([f"- {item}" for item in config.get("conventions", [])])
    constraints_str = "\n".join([f"- {item}" for item in config.get("constraints", [])])
    
    custom_rules = config.get("customRules", {}).get("antigravity", [])
    custom_rules_str = "\n".join([f"- {item}" for item in custom_rules]) if custom_rules else "- Follow standard programming practices."

    content = f"""# ANTIGRAVITY.md — Antigravity Agent Guidelines

This file governs the behavior of the Antigravity agent (Google DeepMind Advanced Agentic Coding assistant) in this repository.

## Planning & Execution Flow (Planning Mode)
1. **Research & Plan**: When given complex tasks, major architectural changes, or significant decision-making:
   - Create or update the `implementation_plan.md` in the brain conversation directory.
   - Do NOT make source code changes or run modifying commands during the research phase.
   - Outline the proposed changes, verification plan, and open questions.
   - Set `request_feedback = true` in the metadata, and wait for explicit user approval.
2. **Checklist (task.md)**: Once approved, create the `task.md` file to log and track your checklist items. Update it dynamically as you work (`[/]` for in-progress, `[x]` for completed).
3. **Verify**: Ensure the changes build and all test suites pass. Run automated validation commands.
4. **Walkthrough**: Update `walkthrough.md` to summarize all changes, testing performed, and validation results.

## Knowledge Items (KI) System Rules
- **Mandatory First Step**: Always check the provided KI summaries at the start of each conversation.
- **Reference KIs**: Read relevant KI artifacts in `<appDataDir>\\knowledge` BEFORE doing independent research or writing code.
- **Verify against active code**: Cross-reference KI patterns with current code to avoid using stale patterns or APIs.

## Coding Conventions
{conventions_str}

## Constraints & Safety Rules
{constraints_str}

## Antigravity-Specific Rules
{custom_rules_str}
{SKILLS_INDEX_MD}
"""
    return content

def generate_cursorrules(config):
    tech_stack_str = "\n".join([f"- {item}" for item in config.get("techStack", [])])
    conventions_str = "\n".join([f"- {item}" for item in config.get("conventions", [])])
    constraints_str = "\n".join([f"- {item}" for item in config.get("constraints", [])])
    
    custom_rules = config.get("customRules", {}).get("codex", [])
    custom_rules_str = "\n".join([f"- {item}" for item in custom_rules]) if custom_rules else "- Follow standard programming practices."

    content = f"""# Cursor Rules & Coding Standards

**Project Name:** {config.get("projectName", "My Project")}

## Tech Stack
{tech_stack_str}

## Coding Conventions
{conventions_str}

## Project Constraints
{constraints_str}

## Codex/Cursor Custom Rules
{custom_rules_str}

## UI & Design Rules (if building UI)
- **Rich Aesthetics**: Avoid browser default components. Use sleek modern palettes, clear typography (Inter, Outfit, Roboto), and rounded corners.
- **No Placeholders**: Never leave empty placeholders or TODOs in visual layouts. Use actual working logic or assets.
- **Micro-animations**: Implement smooth transitions and hover micro-animations to enhance user experience.
- **Responsive Layout**: Always verify that the layout adapts elegantly to different viewport sizes.
{SKILLS_INDEX_MD}
"""
    return content

def generate_copilot_instructions(config):
    tech_stack_str = ", ".join(config.get("techStack", []))
    conventions_str = "\n".join([f"- {item}" for item in config.get("conventions", [])])
    constraints_str = "\n".join([f"- {item}" for item in config.get("constraints", [])])

    content = f"""# GitHub Copilot Instructions

## Project Context
This is the '{config.get("projectName", "My Project")}' project.
Description: {config.get("projectDescription", "")}
Technology Stack: {tech_stack_str}

## Coding Conventions
{conventions_str}

## Constraints & Requirements
{constraints_str}
{SKILLS_INDEX_MD}
"""
    return content

def main():
    root_dir = find_project_root()
    print(f"[*] Detected project root: {root_dir}")
    
    config = load_config(root_dir)
    print("[*] Loaded configuration file successfully.")
    
    # 1. Generate CLAUDE.md
    claude_content = generate_claude_md(config)
    claude_path = os.path.join(root_dir, "CLAUDE.md")
    with open(claude_path, "w", encoding="utf-8") as f:
        f.write(claude_content)
    print(f"[+] Synchronized {claude_path}")

    # 2. Generate ANTIGRAVITY.md
    anti_content = generate_antigravity_md(config)
    anti_path = os.path.join(root_dir, "ANTIGRAVITY.md")
    with open(anti_path, "w", encoding="utf-8") as f:
        f.write(anti_content)
    print(f"[+] Synchronized {anti_path}")

    # 3. Generate .cursorrules and .windsurfrules
    cursor_content = generate_cursorrules(config)
    cursor_path = os.path.join(root_dir, ".cursorrules")
    with open(cursor_path, "w", encoding="utf-8") as f:
        f.write(cursor_content)
    print(f"[+] Synchronized {cursor_path}")

    windsurf_path = os.path.join(root_dir, ".windsurfrules")
    with open(windsurf_path, "w", encoding="utf-8") as f:
        f.write(cursor_content)
    print(f"[+] Synchronized {windsurf_path}")

    # 4. Generate .github/copilot-instructions.md
    copilot_dir = os.path.join(root_dir, ".github")
    if not os.path.exists(copilot_dir):
        os.makedirs(copilot_dir)
    copilot_content = generate_copilot_instructions(config)
    copilot_path = os.path.join(copilot_dir, "copilot-instructions.md")
    with open(copilot_path, "w", encoding="utf-8") as f:
        f.write(copilot_content)
    print(f"[+] Synchronized {copilot_path}")

    print("[+] Synchronization completed successfully!")

if __name__ == "__main__":
    main()
