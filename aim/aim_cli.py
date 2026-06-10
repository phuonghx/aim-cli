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
TIMER_STATE_PATH = os.path.join(AI_CONTEXT_DIR, "timer_state.json")
TIME_LOG_PATH = os.path.join(AI_CONTEXT_DIR, "time_log.json")
USERS_PATH = os.path.join(AI_CONTEXT_DIR, "users.json")
TEMPLATES_DIR = os.path.join(AI_CONTEXT_DIR, "templates")

def load_users():
    if not os.path.exists(USERS_PATH):
        default_users = ["developer", "unassigned"]
        try:
            if not os.path.exists(AI_CONTEXT_DIR):
                os.makedirs(AI_CONTEXT_DIR)
            with open(USERS_PATH, "w", encoding="utf-8") as f:
                json.dump(default_users, f, indent=2)
        except:
            pass
        return default_users
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return ["developer", "unassigned"]

def save_users(users):
    try:
        if not os.path.exists(AI_CONTEXT_DIR):
            os.makedirs(AI_CONTEXT_DIR)
        with open(USERS_PATH, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"[-] Error saving users: {e}")

# Ensure base directories exist
def ensure_directories():
    if not os.path.exists(AI_CONTEXT_DIR):
        os.makedirs(AI_CONTEXT_DIR)
    if not os.path.exists(TASKS_DIR):
        os.makedirs(TASKS_DIR)
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)
    load_users()

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
        "assignee": "unassigned", "timeSpent": 0, 
        "parent": None, "labels": [], "spec": "", "plan": "",
        "description": "", "ac": [], "notes": []
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
        elif line.startswith("**Time Spent:**"):
            try:
                t_str = line.replace("**Time Spent:**", "").replace("seconds", "").strip()
                meta["timeSpent"] = int(t_str)
            except:
                meta["timeSpent"] = 0
        elif line.startswith("**Parent Task:**"):
            val = line.replace("**Parent Task:**", "").strip()
            meta["parent"] = int(val) if val.isdigit() else None
        elif line.startswith("**Labels:**"):
            val = line.replace("**Labels:**", "").strip()
            meta["labels"] = [x.strip() for x in val.split(",")] if val and val != "none" else []
        elif line.startswith("**Spec:**"):
            val = line.replace("**Spec:**", "").strip()
            meta["spec"] = val if val and val != "none" else ""
        elif line.startswith("**Plan:**"):
            val = line.replace("**Plan:**", "").strip()
            meta["plan"] = val if val and val != "none" else ""
            
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
    time_spent = meta.get("timeSpent", 0)
    
    parent_str = f"**Parent Task:** {meta['parent']}" if meta.get("parent") else "**Parent Task:** none"
    labels_str = f"**Labels:** {', '.join(meta['labels'])}" if meta.get("labels") else "**Labels:** none"
    spec_str = f"**Spec:** {meta['spec']}" if meta.get("spec") else "**Spec:** none"
    plan_str = f"**Plan:** {meta['plan']}" if meta.get("plan") else "**Plan:** none"
    
    content = f"""# Task {meta['id']}: {meta['title']}

**Status:** {meta['status']}
**Priority:** {meta['priority']}
**Assignee:** {meta['assignee']}
**Time Spent:** {time_spent} seconds
{parent_str}
{labels_str}
{spec_str}
{plan_str}

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
        
        assignee = args.assignee.strip().lower() if args.assignee else "unassigned"
        users = load_users()
        if assignee not in users:
            print(f"[*] Registering new user '{assignee}' in the database...")
            users.append(assignee)
            save_users(users)
            
        parent = args.parent if hasattr(args, "parent") and args.parent else None
        labels = args.label if hasattr(args, "label") and args.label else []
        spec = args.spec if hasattr(args, "spec") and args.spec else ""
        plan = args.plan if hasattr(args, "plan") and args.plan else ""
        
        meta = {
            "id": next_id,
            "title": args.title,
            "status": "todo",
            "priority": args.priority or "medium",
            "assignee": assignee,
            "parent": parent,
            "labels": labels,
            "spec": spec,
            "plan": plan,
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
            
        # Build tree of tasks
        task_dict = {t["id"]: t for t in tasks}
        children = {t["id"]: [] for t in tasks}
        root_tasks = []
        
        for t in tasks:
            p_id = t.get("parent")
            if p_id and p_id in task_dict:
                children[p_id].append(t)
            else:
                root_tasks.append(t)
                
        print(f"{'ID':<6} {'Title':<40} {'Status':<12} {'Priority':<10} {'Assignee':<15}")
        print("-" * 88)
        
        def print_task(t, indent=""):
            title_text = indent + t['title']
            if t.get("labels"):
                labels_str = f" [{','.join(t['labels'])}]"
                title_text += labels_str
            print(f"{t['id']:<6} {title_text[:38]:<40} {t['status']:<12} {t['priority']:<10} {t['assignee']:<15}")
            for child in children[t["id"]]:
                print_task(child, indent + "  ")
                
        for t in root_tasks:
            print_task(t)
            
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
        
        if hasattr(args, "status") and args.status:
            meta["status"] = args.status
        if hasattr(args, "assignee") and args.assignee:
            assignee = args.assignee.strip().lower()
            users = load_users()
            if assignee not in users:
                print(f"[*] Registering new user '{assignee}' in the database...")
                users.append(assignee)
                save_users(users)
            meta["assignee"] = assignee
        if hasattr(args, "parent") and args.parent is not None:
            meta["parent"] = args.parent if args.parent > 0 else None
        if hasattr(args, "add_label") and args.add_label:
            if "labels" not in meta or not meta["labels"]:
                meta["labels"] = []
            if args.add_label not in meta["labels"]:
                meta["labels"].append(args.add_label)
        if hasattr(args, "remove_label") and args.remove_label:
            if "labels" in meta and args.remove_label in meta["labels"]:
                meta["labels"].remove(args.remove_label)
        if hasattr(args, "spec") and args.spec is not None:
            meta["spec"] = args.spec
        if hasattr(args, "plan") and args.plan is not None:
            meta["plan"] = args.plan
        if hasattr(args, "desc") and args.desc is not None:
            meta["description"] = args.desc
            
        if hasattr(args, "add_ac") and args.add_ac:
            meta["ac"].append({"index": len(meta["ac"]) + 1, "checked": False, "text": args.add_ac})
        if hasattr(args, "check_ac") and args.check_ac is not None:
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
# 9. BOARD COMMAND
# ==========================================
def cmd_board(args):
    ensure_directories()
    tasks = []
    if os.path.exists(TASKS_DIR):
        for filename in os.listdir(TASKS_DIR):
            if filename.startswith("task-") and filename.endswith(".md"):
                try:
                    tasks.append(parse_task_file(os.path.join(TASKS_DIR, filename)))
                except:
                    pass
    
    tasks.sort(key=lambda x: x["id"])
    
    statuses = ["todo", "in-progress", "in-review", "done"]
    columns = {s: [] for s in statuses}
    for t in tasks:
        status = t["status"].lower()
        if status in columns:
            columns[status].append(t)
        else:
            columns["todo"].append(t)
            
    col_width = 30
    
    header_line = ""
    for s in statuses:
        label = f"{s.upper()} ({len(columns[s])})"
        header_line += f"{label:<{col_width}}  "
    print(header_line)
    
    sep_line = ""
    for s in statuses:
        sep_line += f"{'-'*col_width}  "
    print(sep_line)
    
    max_rows = max(len(columns[s]) for s in statuses) if tasks else 0
    
    for row in range(max_rows):
        row_line = ""
        for s in statuses:
            col = columns[s]
            if row < len(col):
                t = col[row]
                card = f"[{t['id']}] {t['title']}"
                if len(card) > col_width:
                    card = card[:col_width-3] + "..."
                row_line += f"{card:<{col_width}}  "
            else:
                row_line += f"{'':<{col_width}}  "
        print(row_line)
        
    print(f"\nTotal: {len(tasks)} tasks across {len(statuses)} columns.")

# ==========================================
# 10. TIME COMMAND
# ==========================================
def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"

def cmd_time(args):
    import time
    ensure_directories()
    
    if args.time_action == "start":
        task_id = args.id
        task_path = os.path.join(TASKS_DIR, f"task-{task_id}.md")
        if not os.path.exists(task_path):
            print(f"[-] Task-{task_id} not found.")
            sys.exit(1)
            
        task = parse_task_file(task_path)
        
        timer_state = {
            "taskId": task_id,
            "title": task["title"],
            "startedAt": time.time()
        }
        with open(TIMER_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(timer_state, f)
            
        print(f"[+] Timer started for task {task_id} ({task['title']})")
        
    elif args.time_action == "stop":
        if not os.path.exists(TIMER_STATE_PATH):
            print("[-] No active timer.")
            sys.exit(1)
            
        with open(TIMER_STATE_PATH, "r", encoding="utf-8") as f:
            timer_state = json.load(f)
            
        task_id = timer_state["taskId"]
        duration = int(time.time() - timer_state["startedAt"])
        
        os.remove(TIMER_STATE_PATH)
        
        task_path = os.path.join(TASKS_DIR, f"task-{task_id}.md")
        if os.path.exists(task_path):
            task = parse_task_file(task_path)
            task["timeSpent"] = task.get("timeSpent", 0) + duration
            write_task_file(task)
            
        logs = []
        if os.path.exists(TIME_LOG_PATH):
            try:
                with open(TIME_LOG_PATH, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except:
                pass
        
        entry = {
            "id": f"te-{int(time.time()*1000)}",
            "taskId": task_id,
            "startedAt": datetime.datetime.fromtimestamp(timer_state["startedAt"]).isoformat(),
            "endedAt": datetime.datetime.now().isoformat(),
            "duration": duration,
            "note": args.note or ""
        }
        logs.append(entry)
        with open(TIME_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
            
        print(f"[+] Timer stopped for task {task_id}. Elapsed: {format_duration(duration)}")
        
    elif args.time_action == "status":
        if not os.path.exists(TIMER_STATE_PATH):
            print("[*] No active timer.")
            return
            
        with open(TIMER_STATE_PATH, "r", encoding="utf-8") as f:
            timer_state = json.load(f)
            
        elapsed = int(time.time() - timer_state["startedAt"])
        print(f"[*] Active Timer:")
        print(f"  Task:      {timer_state['taskId']}")
        print(f"  Title:     {timer_state['title']}")
        print(f"  Elapsed:   {format_duration(elapsed)}")
        
    elif args.time_action == "log":
        task_id = args.id
        if not os.path.exists(TIME_LOG_PATH):
            print("[*] No time logs found.")
            return
            
        with open(TIME_LOG_PATH, "r", encoding="utf-8") as f:
            logs = json.load(f)
            
        task_logs = [l for l in logs if l["taskId"] == task_id]
        if not task_logs:
            print(f"[*] No time logs found for task {task_id}.")
            return
            
        total_secs = sum(l["duration"] for l in task_logs)
        print(f"Time Log for Task {task_id} (Total: {format_duration(total_secs)}):")
        print("-" * 65)
        for l in task_logs:
            print(f"  Started: {l['startedAt']} | Duration: {format_duration(l['duration'])} | Note: {l['note']}")
            
    elif args.time_action == "report":
        if not os.path.exists(TIME_LOG_PATH):
            print("[*] No time logs found.")
            return
            
        with open(TIME_LOG_PATH, "r", encoding="utf-8") as f:
            logs = json.load(f)
            
        totals = {}
        for l in logs:
            tid = l["taskId"]
            totals[tid] = totals.get(tid, 0) + l["duration"]
            
        print("Time spent per task:")
        print("-" * 40)
        for tid, secs in totals.items():
            print(f"  Task {tid:<5}: {format_duration(secs)}")

# ==========================================
# 10.5. USER MANAGEMENT COMMAND
# ==========================================
def cmd_user(args):
    ensure_directories()
    users = load_users()
    
    if args.user_action == "list":
        if not users:
            print("[*] No users found.")
            return
        print("Project Users:")
        print("-" * 25)
        for u in users:
            print(f"  - {u}")
            
    elif args.user_action == "add":
        username = args.username.strip().lower()
        if not username:
            print("[-] Invalid username.")
            sys.exit(1)
        if username in users:
            print(f"[-] User '{username}' already exists.")
            sys.exit(1)
        users.append(username)
        save_users(users)
        print(f"[+] User '{username}' added successfully.")
        
    elif args.user_action == "remove":
        username = args.username.strip().lower()
        if username not in users:
            print(f"[-] User '{username}' not found.")
            sys.exit(1)
        if username in ["developer", "unassigned"]:
            print(f"[-] Cannot remove default user '{username}'.")
            sys.exit(1)
        users.remove(username)
        save_users(users)
        print(f"[+] User '{username}' removed successfully.")

    elif args.user_action == "rename":
        old_username = args.old_username.strip().lower()
        new_username = args.new_username.strip().lower()
        if not old_username or not new_username:
            print("[-] Invalid username.")
            sys.exit(1)
        if old_username not in users:
            print(f"[-] User '{old_username}' not found.")
            sys.exit(1)
        if old_username in ["developer", "unassigned"]:
            print(f"[-] Cannot rename default user '{old_username}'.")
            sys.exit(1)
        if new_username in users:
            print(f"[-] User '{new_username}' already exists.")
            sys.exit(1)
        
        idx = users.index(old_username)
        users[idx] = new_username
        save_users(users)
        
        updated_tasks = 0
        if os.path.exists(TASKS_DIR):
            for filename in os.listdir(TASKS_DIR):
                if filename.startswith("task-") and filename.endswith(".md"):
                    path = os.path.join(TASKS_DIR, filename)
                    try:
                        meta = parse_task_file(path)
                        if meta.get("assignee", "").strip().lower() == old_username:
                            meta["assignee"] = new_username
                            write_task_file(meta)
                            updated_tasks += 1
                    except Exception as e:
                        print(f"[-] Error updating task {filename}: {e}")
                        
        print(f"[+] User '{old_username}' renamed to '{new_username}' successfully.")
        if updated_tasks > 0:
            print(f"[+] Propagated changes to {updated_tasks} task(s).")

# ==========================================
# 11. STATUS COMMAND
# ==========================================
def cmd_status(args):
    ensure_directories()
    import time
    
    # 1. Project Info
    project_name = "My Project"
    tech_stack = []
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                project_name = cfg.get("projectName", project_name)
                tech_stack = cfg.get("techStack", [])
        except:
            pass
            
    # 2. Tasks Stats
    tasks = []
    if os.path.exists(TASKS_DIR):
        for filename in os.listdir(TASKS_DIR):
            if filename.startswith("task-") and filename.endswith(".md"):
                try:
                    t = parse_task_file(os.path.join(TASKS_DIR, filename))
                    tasks.append(t)
                except:
                    pass
                    
    status_counts = {"todo": 0, "in-progress": 0, "in-review": 0, "done": 0}
    for t in tasks:
        st = t.get("status", "todo").lower()
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts[st] = status_counts.get(st, 0) + 1
            
    status_breakdown = ", ".join([f"{k}: {v}" for k, v in status_counts.items()])
    
    # 3. Docs Count
    doc_count = 0
    if os.path.exists(DOCS_DIR):
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if file.endswith(".md"):
                    doc_count += 1
                    
    # 4. Memories Count
    memories = []
    if os.path.exists(MEMORIES_PATH):
        try:
            with open(MEMORIES_PATH, "r", encoding="utf-8") as f:
                memories = json.load(f)
        except:
            pass
    mem_count = len(memories)
    
    # 5. Time Tracked
    total_duration = 0
    if os.path.exists(TIME_LOG_PATH):
        try:
            with open(TIME_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
                total_duration = sum(l.get("duration", 0) for l in logs)
        except:
            pass
            
    active_timer_str = "None"
    if os.path.exists(TIMER_STATE_PATH):
        try:
            with open(TIMER_STATE_PATH, "r", encoding="utf-8") as f:
                timer_state = json.load(f)
                elapsed = int(time.time() - timer_state["startedAt"])
                active_timer_str = f"Task {timer_state['taskId']} ({timer_state['title']}) - active for {format_duration(elapsed)}"
        except:
            pass
            
    # 6. Sync status
    sync_files = {
        "CLAUDE.md": "CLAUDE.md",
        "ANTIGRAVITY.md": "ANTIGRAVITY.md",
        ".cursorrules": ".cursorrules",
        ".windsurfrules": ".windsurfrules",
        "copilot-instructions.md": ".github/copilot-instructions.md"
    }
    
    sync_statuses = {}
    all_synced = True
    for label, rel_path in sync_files.items():
        full_p = os.path.join(ROOT_DIR, rel_path)
        exists = os.path.exists(full_p)
        sync_statuses[label] = "OK" if exists else "Missing"
        if not exists:
            all_synced = False
            
    # Print status report
    print("=========================================")
    print("         AIM Project Status Summary      ")
    print("=========================================")
    print(f"Project Name:  {project_name}")
    print(f"Tech Stack:    {', '.join(tech_stack) if tech_stack else 'Not configured'}")
    print(f"Workspace:     {ROOT_DIR}")
    print()
    print("Memory Layer Statistics:")
    print(f"  Tasks:       {len(tasks)} total ({status_breakdown})")
    print(f"  Docs:        {doc_count} files (@doc/)")
    print(f"  Memories:    {mem_count} entries recorded")
    print()
    print("Time Tracking:")
    print(f"  Total Spent: {format_duration(total_duration)}")
    print(f"  Active:      {active_timer_str}")
    print()
    print("Agent Config Sync Status:")
    for label, status in sync_statuses.items():
        print(f"  {label:<30} [{status}]")
    print(f"  Sync Health: {'Healthy & Synchronized' if all_synced else 'Out of sync / Run `aim sync` to update'}")
    print("=========================================")

# ==========================================
# 12. TEMPLATE COMMANDS & UTILS
# ==========================================
def to_words(s):
    import re
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', s)
    return re.findall(r'[a-zA-Z0-9]+', s)

def kebab_case(s):
    return "-".join(w.lower() for w in to_words(s))

def camel_case(s):
    words = to_words(s)
    if not words:
        return ""
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])

def pascal_case(s):
    return "".join(w.capitalize() for w in to_words(s))

def snake_case(s):
    return "_".join(w.lower() for w in to_words(s))

def render_template_string(template_str, variables):
    import re
    def replacer(match):
        content = match.group(1).strip()
        parts = content.split()
        if len(parts) == 2:
            helper, var_name = parts[0], parts[1]
            val = variables.get(var_name, "")
            if helper == "kebabCase":
                return kebab_case(val)
            elif helper == "camelCase":
                return camel_case(val)
            elif helper == "pascalCase":
                return pascal_case(val)
            elif helper == "snakeCase":
                return snake_case(val)
            elif helper == "lowerCase":
                return val.lower()
            elif helper == "upperCase":
                return val.upper()
            return val
        else:
            return str(variables.get(content, ""))
            
    return re.sub(r'\{\{\s*([^{}]+)\s*\}\}', replacer, template_str)

def parse_yaml(content):
    import re
    data = {}
    lines = content.splitlines()
    current_key = None
    current_list = None
    
    for line in lines:
        line_clean = re.sub(r'#.*$', '', line).rstrip()
        if not line_clean.strip():
            continue
            
        indent = len(line) - len(line.lstrip())
        
        # If it's a list item
        if line_clean.strip().startswith("-"):
            if current_list is not None:
                item_str = line_clean.strip()[1:].strip()
                if ":" in item_str:
                    parts = item_str.split(":", 1)
                    k = parts[0].strip()
                    v = parts[1].strip()
                    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                        v = v[1:-1]
                    if not current_list or not isinstance(current_list[-1], dict):
                        current_list.append({})
                    current_list[-1][k] = v
                else:
                    if (item_str.startswith('"') and item_str.endswith('"')) or (item_str.startswith("'") and item_str.endswith("'")):
                        item_str = item_str[1:-1]
                    current_list.append(item_str)
            continue
            
        if ":" in line_clean:
            parts = line_clean.split(":", 1)
            k = parts[0].strip()
            v = parts[1].strip()
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            
            if indent == 0:
                if v == "":
                    if k in ["prompts", "actions"]:
                        data[k] = []
                        current_list = data[k]
                    else:
                        data[k] = {}
                        current_list = None
                    current_key = k
                else:
                    data[k] = v
                    current_list = None
                    current_key = k
            else:
                if current_key and isinstance(data[current_key], dict):
                    data[current_key][k] = v
                elif current_key and isinstance(data[current_key], list):
                    if not data[current_key] or not isinstance(data[current_key][-1], dict):
                        data[current_key].append({})
                    data[current_key][-1][k] = v
                    
    return data

def cmd_template(args):
    ensure_directories()
    if args.template_action == "create":
        name = args.name.strip().lower()
        if not name:
            print("[-] Invalid template name.")
            sys.exit(1)
            
        t_dir = os.path.join(TEMPLATES_DIR, name)
        if os.path.exists(t_dir):
            print(f"[-] Template '{name}' already exists.")
            sys.exit(1)
            
        os.makedirs(t_dir)
        
        # Default config
        config_content = f"""# Template: {name}
name: {name}
description: Create a {name}
version: 1.0.0
destination: src
prompts:
  - name: name
    type: text
    message: "Name?"
    validate: required
actions:
  - type: add
    template: "main.hbs"
    path: "{{{{kebabCase name}}}}.ts"
    skipIfExists: true
messages:
  success: "Created: {{{{name}}}}"
"""
        with open(os.path.join(t_dir, "_template.yaml"), "w", encoding="utf-8") as f:
            f.write(config_content)
            
        # Default main.hbs
        main_content = f"""// Generated: {{{{name}}}}
// Created by AIM template: {name}
"""
        with open(os.path.join(t_dir, "main.hbs"), "w", encoding="utf-8") as f:
            f.write(main_content)
            
        print(f"[+] Created template: {name}")
        print(f"[*] Edit the template config at: .ai-context/templates/{name}/_template.yaml")
        
    elif args.template_action == "list":
        if not os.path.exists(TEMPLATES_DIR):
            print("[*] No templates found.")
            return
            
        templates = []
        for d in os.listdir(TEMPLATES_DIR):
            t_path = os.path.join(TEMPLATES_DIR, d)
            if os.path.isdir(t_path) and os.path.exists(os.path.join(t_path, "_template.yaml")):
                try:
                    with open(os.path.join(t_path, "_template.yaml"), "r", encoding="utf-8") as f:
                        cfg = parse_yaml(f.read())
                    templates.append(cfg)
                except Exception as e:
                    print(f"[-] Warning: Failed to parse template {d}: {e}")
                    
        if not templates:
            print("[*] No templates found.")
            return
            
        print(f"{'Name':<15} {'Description':<50}")
        print("-" * 65)
        for t in templates:
            name = t.get("name", "unknown")
            desc = t.get("description", "")
            print(f"{name:<15} {desc:<50}")
            
    elif args.template_action == "view":
        name = args.name.strip().lower()
        t_path = os.path.join(TEMPLATES_DIR, name, "_template.yaml")
        if not os.path.exists(t_path):
            print(f"[-] Template '{name}' not found.")
            sys.exit(1)
            
        with open(t_path, "r", encoding="utf-8") as f:
            print(f.read())
            
    elif args.template_action == "run":
        name = args.name.strip().lower()
        t_dir = os.path.join(TEMPLATES_DIR, name)
        t_path = os.path.join(t_dir, "_template.yaml")
        if not os.path.exists(t_path):
            print(f"[-] Template '{name}' not found.")
            sys.exit(1)
            
        with open(t_path, "r", encoding="utf-8") as f:
            cfg = parse_yaml(f.read())
            
        variables = {}
        for var in args.var or []:
            if "=" in var:
                k, v = var.split("=", 1)
                variables[k.strip()] = v.strip()
                
        prompts = cfg.get("prompts", [])
        for prompt in prompts:
            p_name = prompt.get("name")
            if p_name and p_name not in variables:
                msg = prompt.get("message", f"{p_name}?")
                default = prompt.get("default", "")
                prompt_msg = f"{msg} "
                if default:
                    prompt_msg += f"({default}) "
                val = input(prompt_msg).strip()
                if not val and default:
                    val = default
                if not val and prompt.get("validate") == "required":
                    print(f"[-] {p_name} is required.")
                    sys.exit(1)
                variables[p_name] = val
                
        actions = cfg.get("actions", [])
        dest_base = cfg.get("destination", "")
        dest_root = os.path.join(ROOT_DIR, dest_base) if dest_base else ROOT_DIR
        
        dry_run = args.dry_run
        if dry_run:
            print("[*] Dry-run mode: Preview of files that would be generated:")
            print("-" * 65)
            
        success_files = []
        for action in actions:
            a_type = action.get("type", "add")
            if a_type == "add":
                tpl_file = action.get("template")
                dest_file_pattern = action.get("path")
                
                if not tpl_file or not dest_file_pattern:
                    print("[-] Error: action missing template or path.")
                    continue
                    
                tpl_path = os.path.join(t_dir, tpl_file)
                if not os.path.exists(tpl_path):
                    print(f"[-] Error: template source file '{tpl_file}' not found.")
                    continue
                    
                with open(tpl_path, "r", encoding="utf-8") as f:
                    tpl_content = f.read()
                    
                rendered_content = render_template_string(tpl_content, variables)
                rendered_path = render_template_string(dest_file_pattern, variables)
                
                final_dest_path = os.path.normpath(os.path.join(dest_root, rendered_path))
                
                if dry_run:
                    print(f"Target Path: {os.path.relpath(final_dest_path, ROOT_DIR)}")
                    print("Content Preview:")
                    print(rendered_content)
                    print("-" * 65)
                else:
                    if action.get("skipIfExists") == "true" and os.path.exists(final_dest_path):
                        print(f"[*] Skipped: File already exists at {final_dest_path}")
                        continue
                        
                    parent_dir = os.path.dirname(final_dest_path)
                    if not os.path.exists(parent_dir):
                        os.makedirs(parent_dir)
                        
                    with open(final_dest_path, "w", encoding="utf-8") as f:
                        f.write(rendered_content)
                    print(f"[+] Created: {os.path.relpath(final_dest_path, ROOT_DIR)}")
                    success_files.append(final_dest_path)
                    
        if not dry_run:
            success_msg_pattern = cfg.get("messages", {}).get("success", "") if isinstance(cfg.get("messages"), dict) else ""
            if success_msg_pattern:
                print(render_template_string(success_msg_pattern, variables))
            else:
                print(f"[+] Template '{name}' run successfully.")

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
    create_task.add_argument("--parent", type=int, help="Parent task ID")
    create_task.add_argument("-l", "--label", action="append", help="Label tag (repeatable)")
    create_task.add_argument("--spec", help="Linked spec document path")
    create_task.add_argument("--plan", help="Linked plan document path")
    
    view_task = task_sub.add_parser("view", help="View a specific task")
    view_task.add_argument("id", type=int, help="Task ID")
    
    edit_task = task_sub.add_parser("edit", help="Edit a task's status or assignee")
    edit_task.add_argument("id", type=int, help="Task ID")
    edit_task.add_argument("-s", "--status", help="Update status (todo/in-progress/in-review/done/blocked)")
    edit_task.add_argument("-a", "--assignee", help="Assignee user")
    edit_task.add_argument("--add-ac", help="Add acceptance criteria item")
    edit_task.add_argument("--check-ac", type=int, help="Mark AC index as completed (1-based)")
    edit_task.add_argument("--parent", type=int, help="Update parent task ID")
    edit_task.add_argument("--add-label", help="Add label tag")
    edit_task.add_argument("--remove-label", help="Remove label tag")
    edit_task.add_argument("--spec", help="Update spec document path")
    edit_task.add_argument("--plan", help="Update plan document path")
    edit_task.add_argument("-d", "--desc", help="Update task description")
    
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
    
    # status
    subparsers.add_parser("status", help="Show project readiness summary")
    
    # browser
    browser_parser = subparsers.add_parser("browser", help="Launch the AIM Web UI in your browser")
    browser_parser.add_argument("-p", "--port", type=int, default=6420, help="Port to run the server on")
    browser_parser.add_argument("--no-open", action="store_true", help="Start the server without opening the browser automatically")
    
    # board
    subparsers.add_parser("board", help="Show the ASCII Kanban board")
    
    # time
    time_parser = subparsers.add_parser("time", help="Track time spent on tasks")
    time_sub = time_parser.add_subparsers(dest="time_action", required=True)
    
    time_start = time_sub.add_parser("start", help="Start timer for a task")
    time_start.add_argument("id", type=int, help="Task ID")
    
    time_stop = time_sub.add_parser("stop", help="Stop the active timer")
    time_stop.add_argument("-n", "--note", help="Add a note to this time entry")
    
    time_sub.add_parser("status", help="Show current timer status")
    
    time_log = time_sub.add_parser("log", help="Show time logs for a task")
    time_log.add_argument("id", type=int, help="Task ID")
    
    time_sub.add_parser("report", help="Generate a time tracking report")
    
    # user
    user_parser = subparsers.add_parser("user", help="Manage project users & assignees")
    user_sub = user_parser.add_subparsers(dest="user_action", required=True)
    
    user_sub.add_parser("list", help="List all registered users")
    
    add_user = user_sub.add_parser("add", help="Add a new user")
    add_user.add_argument("username", help="Username to add")
    
    remove_user = user_sub.add_parser("remove", help="Remove a user")
    remove_user.add_argument("username", help="Username to remove")
    
    rename_user = user_sub.add_parser("rename", help="Rename a user")
    rename_user.add_argument("old_username", help="Old username to rename")
    rename_user.add_argument("new_username", help="New username to set")
    
    # template
    template_parser = subparsers.add_parser("template", help="Manage code generation templates")
    template_sub = template_parser.add_subparsers(dest="template_action", required=True)
    
    template_sub.add_parser("list", help="List all templates")
    
    create_template = template_sub.add_parser("create", help="Create a new template scaffold")
    create_template.add_argument("name", help="Template name")
    
    view_template = template_sub.add_parser("view", help="View template details")
    view_template.add_argument("name", help="Template name")
    
    run_template = template_sub.add_parser("run", help="Run a code generation template")
    run_template.add_argument("name", help="Template name")
    run_template.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    run_template.add_argument("-v", "--var", action="append", help="Template variable (key=value, repeatable)")
    
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
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "browser":
        cmd_browser(args)
    elif args.command == "board":
        cmd_board(args)
    elif args.command == "time":
        cmd_time(args)
    elif args.command == "user":
        cmd_user(args)
    elif args.command == "template":
        cmd_template(args)

if __name__ == "__main__":
    main()
