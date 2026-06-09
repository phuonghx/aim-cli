#!/usr/bin/env python3
import os
import sys
import json
import shutil
import re
import datetime
import argparse
import subprocess

# Determine directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Helper: Find project root dynamically
def get_project_root():
    cwd = os.getcwd()
    if "init" in sys.argv:
        return cwd
    if os.path.exists(os.path.join(cwd, ".ai-context")):
        return cwd
    parent = os.path.dirname(cwd)
    if os.path.exists(os.path.join(parent, ".ai-context")):
        return parent
    return cwd

ROOT_DIR = get_project_root()
AI_CONTEXT_DIR = os.path.join(ROOT_DIR, ".ai-context")
TASKS_DIR = os.path.join(AI_CONTEXT_DIR, "tasks")
DOCS_DIR = os.path.join(AI_CONTEXT_DIR, "docs")
MEMORIES_PATH = os.path.join(AI_CONTEXT_DIR, "memories.json")
CONFIG_PATH = os.path.join(AI_CONTEXT_DIR, "config.json")

# Ensure base directories exist
def ensure_directories():
    if not os.path.exists(AI_CONTEXT_DIR):
        os.makedirs(AI_CONTEXT_DIR)
    if not os.path.exists(TASKS_DIR):
        os.makedirs(TASKS_DIR)
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)

def auto_detect_project(root_dir):
    detected = {
        "projectName": os.path.basename(root_dir) or "My Project",
        "techStack": [],
        "commands": {
            "build": "",
            "test": "",
            "lint": "",
            "format": ""
        }
    }
    
    # 1. Node / JS / TS
    if os.path.exists(os.path.join(root_dir, "package.json")):
        detected["techStack"].append("JavaScript/TypeScript")
        detected["commands"]["build"] = "npm run build"
        detected["commands"]["test"] = "npm test"
        detected["commands"]["lint"] = "npm run lint"
        detected["commands"]["format"] = "npx prettier --write ."
        
        # Check if tsconfig exists
        if os.path.exists(os.path.join(root_dir, "tsconfig.json")):
            detected["techStack"].append("TypeScript")
            
        # Check frameworks
        with open(os.path.join(root_dir, "package.json"), "r", encoding="utf-8") as f:
            try:
                pkg = json.load(f)
                deps = pkg.get("dependencies", {})
                dev_deps = pkg.get("devDependencies", {})
                if "next" in deps:
                    detected["techStack"].append("React/Next.js")
                    detected["commands"]["build"] = "next build"
                elif "react" in deps:
                    detected["techStack"].append("React")
                elif "vue" in deps:
                    detected["techStack"].append("Vue.js")
            except:
                pass
                
    # 2. Rust
    elif os.path.exists(os.path.join(root_dir, "Cargo.toml")):
        detected["techStack"].append("Rust")
        detected["commands"]["build"] = "cargo build"
        detected["commands"]["test"] = "cargo test"
        detected["commands"]["lint"] = "cargo clippy"
        detected["commands"]["format"] = "cargo fmt"
        
    # 3. Python
    elif any(os.path.exists(os.path.join(root_dir, f)) for f in ["requirements.txt", "pyproject.toml", "setup.py"]):
        detected["techStack"].append("Python")
        detected["commands"]["build"] = "# Python projects typically do not compile"
        detected["commands"]["test"] = "pytest"
        detected["commands"]["lint"] = "flake8 . or black --check ."
        detected["commands"]["format"] = "black ."
        
    # 4. Go
    elif os.path.exists(os.path.join(root_dir, "go.mod")):
        detected["techStack"].append("Go")
        detected["commands"]["build"] = "go build ./"
        detected["commands"]["test"] = "go test ./..."
        detected["commands"]["lint"] = "golangci-lint run"
        detected["commands"]["format"] = "go fmt ./..."
        
    # Fallback default stack
    if not detected["techStack"]:
        detected["techStack"] = ["Web Application (HTML/JS/CSS)"]
        detected["commands"]["build"] = "echo 'No build command needed'"
        detected["commands"]["test"] = "echo 'No tests configured'"
        detected["commands"]["lint"] = "echo 'No lint configured'"
        detected["commands"]["format"] = "echo 'No format configured'"
        
    return detected

# ==========================================
# 1. SETUP / INIT COMMAND
# ==========================================
def cmd_init(args):
    print("=========================================")
    print("         AIM - AI Agent Toolkit          ")
    print("=========================================\n")
    print(f"[*] Initializing in: {ROOT_DIR}")
    
    ensure_directories()
    
    # Auto-detect project characteristics
    detected = auto_detect_project(ROOT_DIR)
    print(f"[+] Detected project name: {detected['projectName']}")
    print(f"[+] Detected tech stack: {', '.join(detected['techStack'])}")
    
    # Create config.json
    if not os.path.exists(CONFIG_PATH):
        template_path = os.path.join(SCRIPT_DIR, "templates", "config.json.template")
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            config_data["projectName"] = detected["projectName"]
            config_data["techStack"] = detected["techStack"]
            config_data["commands"] = detected["commands"]
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            print(f"[+] Created config.json based on auto-detection.")
        else:
            print("[-] Warning: config.json template not found.")
    else:
        print("[*] config.json already exists. Skipping recreation.")
        
    # Copy skills
    dest_skills_dir = os.path.join(AI_CONTEXT_DIR, "skills")
    if os.path.exists(dest_skills_dir):
        shutil.rmtree(dest_skills_dir)
    src_skills_dir = os.path.join(SCRIPT_DIR, "skills")
    if os.path.exists(src_skills_dir):
        shutil.copytree(src_skills_dir, dest_skills_dir)
        print(f"[+] Installed modular skills to: {dest_skills_dir}")
        
    # Copy AIM Specialist Agent Suite (agents, workflows, scripts, rules)
    dest_ag_kit_dir = os.path.join(ROOT_DIR, ".aim-agents")
    if os.path.exists(dest_ag_kit_dir):
        shutil.rmtree(dest_ag_kit_dir)
    src_ag_kit = os.path.join(SCRIPT_DIR, "templates", "aim-agents")
    if os.path.exists(src_ag_kit):
        shutil.copytree(src_ag_kit, dest_ag_kit_dir)
        print(f"[+] Installed AIM Specialist Agent Suite to: {dest_ag_kit_dir}")
    else:
        print("[-] Warning: AIM Agent templates not found in source directory.")
        
    # Copy Claude slash commands
    claude_commands_dir = os.path.join(ROOT_DIR, ".claude", "commands")
    if not os.path.exists(claude_commands_dir):
        os.makedirs(claude_commands_dir)
    src_commands_dir = os.path.join(SCRIPT_DIR, "templates", "commands")
    if os.path.exists(src_commands_dir):
        for cmd_file in os.listdir(src_commands_dir):
            shutil.copy2(os.path.join(src_commands_dir, cmd_file), os.path.join(claude_commands_dir, cmd_file))
            print(f"  [+] Installed slash command: {cmd_file}")
            
    # Trigger sync
    cmd_sync(None)

# ==========================================
# 2. SYNC COMMAND
# ==========================================
def cmd_sync(args):
    print("[*] Synchronizing rules & agent guidelines...")
    try:
        from aim.sync import main as run_sync
    except ImportError:
        from sync import main as run_sync
    try:
        run_sync()
    except Exception as e:
        print(f"[-] Sync failed: {e}")

# ==========================================
# 3. TASK COMMANDS
# ==========================================
def parse_task_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    meta = {
        "id": "", "title": "", "status": "todo", "priority": "medium", 
        "assignee": "unassigned", "description": "", "ac": [], "notes": []
    }
    
    # Parse title
    title_match = re.search(r"^# Task (\d+):\s*(.+)$", content, re.MULTILINE)
    if title_match:
        meta["id"] = int(title_match.group(1))
        meta["title"] = title_match.group(2).strip()
        
    # Parse front metadata
    for line in content.split("\n"):
        if line.startswith("**Status:**"):
            meta["status"] = line.replace("**Status:**", "").strip()
        elif line.startswith("**Priority:**"):
            meta["priority"] = line.replace("**Priority:**", "").strip()
        elif line.startswith("**Assignee:**"):
            meta["assignee"] = line.replace("**Assignee:**", "").strip()
            
    # Parse description
    desc_section = re.search(r"## Description\n(.*?)\n##", content, re.DOTALL | re.MULTILINE)
    if desc_section:
        meta["description"] = desc_section.group(1).strip()
        
    # Parse ACs
    ac_matches = re.findall(r"-\s*\[([ x/])\]\s*(.+)", content)
    for index, (checked, ac_text) in enumerate(ac_matches):
        meta["ac"].append({
            "index": index + 1,
            "checked": checked.strip() == "x",
            "text": ac_text.strip()
        })
        
    return meta

def write_task_file(meta):
    ac_lines = []
    for ac in meta["ac"]:
        chk = "x" if ac["checked"] else " "
        ac_lines.append(f"- [{chk}] {ac['text']}")
        
    ac_str = "\n".join(ac_lines)
    
    content = f"""# Task {meta['id']}: {meta['title']}

**Status:** {meta['status']}
**Priority:** {meta['priority']}
**Assignee:** {meta['assignee']}

## Description
{meta['description']}

## Acceptance Criteria
{ac_str}

## Notes
- Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    path = os.path.join(TASKS_DIR, f"task-{meta['id']}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def cmd_task(args):
    ensure_directories()
    if args.task_action == "create":
        # Determine next ID
        existing_ids = []
        for filename in os.listdir(TASKS_DIR):
            m = re.match(r"task-(\d+)\.md", filename)
            if m:
                existing_ids.append(int(m.group(1)))
        next_id = max(existing_ids) + 1 if existing_ids else 1
        
        meta = {
            "id": next_id,
            "title": args.title,
            "status": "todo",
            "priority": args.priority or "medium",
            "assignee": args.assignee or "unassigned",
            "description": args.desc or "",
            "ac": [{"index": i+1, "checked": False, "text": ac} for i, ac in enumerate(args.ac or [])]
        }
        write_task_file(meta)
        print(f"[+] Task created successfully: task-{next_id} (Title: {args.title})")
        
    elif args.task_action == "list":
        tasks = []
        for filename in os.listdir(TASKS_DIR):
            if filename.startswith("task-") and filename.endswith(".md"):
                tasks.append(parse_task_file(os.path.join(TASKS_DIR, filename)))
        
        if not tasks:
            print("[*] No tasks found.")
            return
            
        tasks.sort(key=lambda x: x["id"])
        print(f"{'ID':<6} {'Title':<40} {'Status':<12} {'Priority':<10} {'Assignee':<15}")
        print("-" * 88)
        for t in tasks:
            print(f"{t['id']:<6} {t['title'][:38]:<40} {t['status']:<12} {t['priority']:<10} {t['assignee']:<15}")
            
    elif args.task_action == "view":
        path = os.path.join(TASKS_DIR, f"task-{args.id}.md")
        if not os.path.exists(path):
            print(f"[-] Task-{args.id} not found.")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            print(f.read())
            
    elif args.task_action == "edit":
        path = os.path.join(TASKS_DIR, f"task-{args.id}.md")
        if not os.path.exists(path):
            print(f"[-] Task-{args.id} not found.")
            sys.exit(1)
            
        meta = parse_task_file(path)
        
        if args.status:
            meta["status"] = args.status
        if args.assignee:
            meta["assignee"] = args.assignee
        if args.add_ac:
            meta["ac"].append({"index": len(meta["ac"]) + 1, "checked": False, "text": args.add_ac})
        if args.check_ac is not None:
            ac_idx = args.check_ac - 1
            if 0 <= ac_idx < len(meta["ac"]):
                meta["ac"][ac_idx]["checked"] = True
                print(f"[+] Marked AC #{args.check_ac} as completed.")
            else:
                print(f"[-] Error: AC index {args.check_ac} out of range.")
                
        write_task_file(meta)
        print(f"[+] Task-{args.id} updated successfully.")

# ==========================================
# 4. DOC COMMANDS
# ==========================================
def cmd_doc(args):
    ensure_directories()
    if args.doc_action == "create":
        # Create folders if needed
        folder_path = os.path.join(DOCS_DIR, args.folder) if args.folder else DOCS_DIR
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        slug = re.sub(r"[^\w\s-]", "", args.title.lower()).strip().replace(" ", "-")
        filename = f"{slug}.md"
        doc_file_path = os.path.join(folder_path, filename)
        
        content = f"""# {args.title}

**Description:** {args.desc or ""}
**Created:** {datetime.datetime.now().strftime('%Y-%m-%d')}

## Overview

[Write your documentation content here]
"""
        with open(doc_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        relative_path = os.path.relpath(doc_file_path, DOCS_DIR).replace("\\", "/")
        print(f"[+] Documentation file created: @doc/{relative_path}")
        
    elif args.doc_action == "list":
        print("[*] Documentation Files:")
        print("-" * 60)
        found = False
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    rel = os.path.relpath(full_path, DOCS_DIR).replace("\\", "/")
                    print(f"- @doc/{rel}")
                    found = True
        if not found:
            print("[*] No documents found.")
            
    elif args.doc_action == "view":
        # Support both raw name (e.g. architecture/auth) or path
        clean_path = args.path.replace("@doc/", "")
        if not clean_path.endswith(".md"):
            clean_path += ".md"
            
        doc_file_path = os.path.join(DOCS_DIR, clean_path)
        if not os.path.exists(doc_file_path):
            print(f"[-] Doc '{args.path}' not found at {doc_file_path}")
            sys.exit(1)
            
        with open(doc_file_path, "r", encoding="utf-8") as f:
            print(f.read())

# ==========================================
# 5. MEMORY COMMANDS
# ==========================================
def cmd_memory(args):
    ensure_directories()
    memories = []
    if os.path.exists(MEMORIES_PATH):
        with open(MEMORIES_PATH, "r", encoding="utf-8") as f:
            try:
                memories = json.load(f)
            except:
                pass
                
    if args.mem_action == "add":
        new_mem = {
            "id": len(memories) + 1,
            "content": args.content,
            "category": args.category or "general",
            "layer": args.layer or "project",
            "createdAt": datetime.datetime.now().isoformat()
        }
        memories.append(new_mem)
        with open(MEMORIES_PATH, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2)
        print(f"[+] Memory added successfully under category '{new_mem['category']}'.")
        
    elif args.mem_action == "list":
        if not memories:
            print("[*] No memories recorded.")
            return
        print(f"{'ID':<4} {'Category':<12} {'Layer':<10} {'Content':<50}")
        print("-" * 80)
        for m in memories:
            print(f"{m['id']:<4} {m['category']:<12} {m['layer']:<10} {m['content'][:48]:<50}")

# ==========================================
# 6. LOCAL SEARCH COMMAND
# ==========================================
def cmd_search(args):
    ensure_directories()
    query = args.query.lower()
    print(f"[*] Searching for '{query}' across tasks, docs, and memory...\n")
    
    results = []
    
    # 1. Search Tasks
    for filename in os.listdir(TASKS_DIR):
        if filename.endswith(".md"):
            path = os.path.join(TASKS_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if query in content.lower():
                matches = re.findall(f"(?i).{{0,30}}{re.escape(query)}.{{0,30}}", content)
                snippet = " | ".join(matches[:2])
                results.append({"type": "task", "ref": f"@task-{filename.replace('task-', '').replace('.md', '')}", "snippet": snippet})
                
    # 2. Search Docs
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                path = os.path.join(root, file)
                rel = os.path.relpath(path, DOCS_DIR).replace("\\", "/")
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if query in content.lower():
                    matches = re.findall(f"(?i).{{0,30}}{re.escape(query)}.{{0,30}}", content)
                    snippet = " | ".join(matches[:2])
                    results.append({"type": "doc", "ref": f"@doc/{rel}", "snippet": snippet})
                    
    # 3. Search Memory
    if os.path.exists(MEMORIES_PATH):
        with open(MEMORIES_PATH, "r", encoding="utf-8") as f:
            try:
                memories = json.load(f)
                for mem in memories:
                    if query in mem["content"].lower():
                        results.append({"type": "memory", "ref": f"Memory #{mem['id']} ({mem['category']})", "snippet": mem["content"]})
            except:
                pass
                
    if not results:
        print("[*] No matches found.")
        return
        
    print(f"{'Type':<8} {'Reference':<30} {'Match Snippet'}")
    print("-" * 88)
    for r in results:
        print(f"{r['type']:<8} {r['ref']:<30} {r['snippet']}")

# ==========================================
# 7. VALIDATE REFERENCES COMMAND
# ==========================================
def cmd_validate(args):
    ensure_directories()
    print("[*] Validating project memory layer references...")
    errors = 0
    
    # Get lists of tasks & docs
    tasks = set()
    for filename in os.listdir(TASKS_DIR):
        m = re.match(r"task-(\d+)\.md", filename)
        if m:
            tasks.add(int(m.group(1)))
            
    docs = set()
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                rel = os.path.relpath(os.path.join(root, file), DOCS_DIR).replace("\\", "/")
                docs.add(rel)
                
    # Function to check file contents
    def check_references(content, file_desc):
        nonlocal errors
        # Check task mentions
        task_refs = re.findall(r"@task-(\d+)", content)
        for ref in task_refs:
            if int(ref) not in tasks:
                print(f"[-] Broken task link in {file_desc}: @task-{ref} does not exist.")
                errors += 1
        # Check doc mentions
        doc_refs = re.findall(r"@doc/([\w\-/]+\.md|[\w\-/\s]+)", content)
        for ref in doc_refs:
            clean_ref = ref.strip()
            if not clean_ref.endswith(".md"):
                clean_ref += ".md"
            if clean_ref not in docs:
                print(f"[-] Broken doc link in {file_desc}: @doc/{ref} does not exist.")
                errors += 1

    # Validate Tasks
    for filename in os.listdir(TASKS_DIR):
        if filename.endswith(".md"):
            path = os.path.join(TASKS_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            check_references(content, f"task file {filename}")
            
    # Validate Docs
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                path = os.path.join(root, file)
                rel = os.path.relpath(path, DOCS_DIR).replace("\\", "/")
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                check_references(content, f"doc @doc/{rel}")
                
    if errors == 0:
        print("[+] All references are healthy!")
    else:
        print(f"[-] Found {errors} broken reference link(s).")
        sys.exit(1)

# ==========================================
# 8. BROWSER COMMAND
# ==========================================
def cmd_browser(args):
    try:
        from aim.browser_server import start_server
    except ImportError:
        from browser_server import start_server
    start_server(port=args.port, open_browser=not args.no_open)

# ==========================================
# MAIN DISPATCHER
# ==========================================
def main():
    parser = argparse.ArgumentParser(
        description="AIM (AI Memory/Mind) CLI - Centralized Project Context & Memory Engine",
        prog="aim"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # init
    subparsers.add_parser("init", help="Initialize AIM in the project root")
    
    # sync
    subparsers.add_parser("sync", help="Synchronize active config and compile shims")
    
    # task
    task_parser = subparsers.add_parser("task", help="Manage project tasks")
    task_sub = task_parser.add_subparsers(dest="task_action", required=True)
    
    task_sub.add_parser("list", help="List all tasks")
    
    create_task = task_sub.add_parser("create", help="Create a new task")
    create_task.add_argument("title", help="Task title")
    create_task.add_argument("-d", "--desc", help="Task description")
    create_task.add_argument("--ac", action="append", help="Acceptance criteria item")
    create_task.add_argument("-p", "--priority", choices=["low", "medium", "high", "urgent"], help="Task priority")
    create_task.add_argument("-a", "--assignee", help="Task assignee")
    
    view_task = task_sub.add_parser("view", help="View a specific task")
    view_task.add_argument("id", type=int, help="Task ID")
    
    edit_task = task_sub.add_parser("edit", help="Edit a task's status or assignee")
    edit_task.add_argument("id", type=int, help="Task ID")
    edit_task.add_argument("-s", "--status", help="Update status (todo/in-progress/in-review/done/blocked)")
    edit_task.add_argument("-a", "--assignee", help="Assignee user")
    edit_task.add_argument("--add-ac", help="Add acceptance criteria item")
    edit_task.add_argument("--check-ac", type=int, help="Mark AC index as completed (1-based)")
    
    # doc
    doc_parser = subparsers.add_parser("doc", help="Manage documentation")
    doc_sub = doc_parser.add_subparsers(dest="doc_action", required=True)
    
    doc_sub.add_parser("list", help="List all documentation files")
    
    create_doc = doc_sub.add_parser("create", help="Create a new document")
    create_doc.add_argument("title", help="Document title")
    create_doc.add_argument("-f", "--folder", help="Subfolder path inside docs")
    create_doc.add_argument("-d", "--desc", help="Document description summary")
    
    view_doc = doc_sub.add_parser("view", help="View a document")
    view_doc.add_argument("path", help="Document reference path (e.g. architecture/auth)")
    
    # memory
    mem_parser = subparsers.add_parser("memory", help="Manage persistent session memory")
    mem_sub = mem_parser.add_subparsers(dest="mem_action", required=True)
    
    mem_sub.add_parser("list", help="List memories")
    
    add_mem = mem_sub.add_parser("add", help="Add a persistent memory item")
    add_mem.add_argument("content", help="Memory statement")
    add_mem.add_argument("-c", "--category", help="Category (e.g. decision, syntax, pattern)")
    add_mem.add_argument("-l", "--layer", choices=["project", "global"], help="Storage layer")
    
    # search
    search_parser = subparsers.add_parser("search", help="Search across tasks, docs, and memory")
    search_parser.add_argument("query", help="Search query string")
    
    # validate
    subparsers.add_parser("validate", help="Validate links and references health")
    
    # browser
    browser_parser = subparsers.add_parser("browser", help="Launch the AIM Web UI in your browser")
    browser_parser.add_argument("-p", "--port", type=int, default=6420, help="Port to run the server on")
    browser_parser.add_argument("--no-open", action="store_true", help="Start the server without opening the browser automatically")
    
    args = parser.parse_args()
    
    # Command Dispatcher
    if args.command == "init":
        cmd_init(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "task":
        cmd_task(args)
    elif args.command == "doc":
        cmd_doc(args)
    elif args.command == "memory":
        cmd_memory(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "browser":
        cmd_browser(args)

if __name__ == "__main__":
    main()
