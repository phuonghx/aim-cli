#!/usr/bin/env python3
import os
import sys
import json
import shutil
import re
import datetime
import argparse

try:
    from aim import __version__
except ImportError:
    __version__ = "unknown"

# Determine directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


def _core():
    """Late import of the shared service layer (avoids a circular import
    at module load: core resolves paths from this module at call time)."""
    try:
        from aim import core
    except ImportError:
        import core
    return core


def configure_utf8_output():
    """Force UTF-8 stdout/stderr so piped output (the way AI agents invoke
    this CLI) does not crash with UnicodeEncodeError on Windows."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


# Helper: Find project root dynamically
def get_project_root():
    cwd = os.getcwd()
    # `aim init` always initializes the current directory; only treat it as
    # the subcommand when it is actually in the subcommand position.
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        return cwd
    # Walk up the directory tree looking for an existing workspace.
    current = cwd
    while True:
        if os.path.exists(os.path.join(current, ".ai-context")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return cwd
        current = parent

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
# Global memory store — shared across every project on this machine.
GLOBAL_AIM_DIR = os.path.join(os.path.expanduser("~"), ".aim")
GLOBAL_MEMORIES_PATH = os.path.join(GLOBAL_AIM_DIR, "memories.json")

def load_json(path, default):
    """Read a JSON store. A corrupt file is backed up (never silently
    clobbered later by a save) and the default is returned."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        backup_path = f"{path}.corrupt-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        try:
            shutil.copy2(path, backup_path)
            print(f"[-] Warning: {os.path.basename(path)} is unreadable ({e}). "
                  f"Backed it up to {os.path.basename(backup_path)} and continuing with defaults.")
        except OSError:
            print(f"[-] Warning: {os.path.basename(path)} is unreadable ({e}).")
        return default

def save_json(path, data):
    """Atomically write a JSON store (temp file + os.replace) so a crash or
    concurrent reader never observes a truncated file."""
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent)
    tmp_path = f"{path}.{os.getpid()}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)

def load_users():
    default_users = ["developer", "unassigned"]
    if not os.path.exists(USERS_PATH):
        try:
            save_json(USERS_PATH, default_users)
        except OSError:
            pass
        return default_users
    return load_json(USERS_PATH, default_users)

def save_users(users):
    try:
        save_json(USERS_PATH, users)
    except OSError as e:
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
                if "next" in deps:
                    detected["techStack"].append("React/Next.js")
                    detected["commands"]["build"] = "next build"
                elif "react" in deps:
                    detected["techStack"].append("React")
                elif "vue" in deps:
                    detected["techStack"].append("Vue.js")
            except Exception:
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
            print("[+] Created config.json based on auto-detection.")
        else:
            print("[-] Warning: config.json template not found.")
    else:
        print("[*] config.json already exists. Skipping recreation.")
        
    force = bool(getattr(args, "force", False))

    def install_tree(src_dir, dest_dir, label):
        """Copy a template tree. Never silently destroys an existing
        (possibly user-customized) install: requires --force, and even then
        moves the old directory to a timestamped .bak first."""
        if not os.path.exists(src_dir):
            return False
        if os.path.exists(dest_dir):
            if not force:
                print(f"[*] {label} already exists at {dest_dir}. "
                      f"Use 'aim init --force' to reinstall (a .bak backup will be kept).")
                return False
            backup_dir = f"{dest_dir}.bak-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.move(dest_dir, backup_dir)
            print(f"[*] Backed up existing {label} to: {backup_dir}")
        shutil.copytree(src_dir, dest_dir)
        print(f"[+] Installed {label} to: {dest_dir}")
        return True

    # Copy skills
    install_tree(os.path.join(SCRIPT_DIR, "skills"),
                 os.path.join(AI_CONTEXT_DIR, "skills"),
                 "modular skills")

    # Copy AIM Specialist Agent Suite (agents, workflows, scripts, rules)
    src_ag_kit = os.path.join(SCRIPT_DIR, "templates", "aim-agents")
    if os.path.exists(src_ag_kit):
        install_tree(src_ag_kit, os.path.join(ROOT_DIR, ".aim-agents"),
                     "AIM Specialist Agent Suite")
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
    except SystemExit:
        raise
    except Exception as e:
        print(f"[-] Sync failed: {e}")
        sys.exit(1)

# ==========================================
# 3. TASK COMMANDS
# ==========================================
# Sections the task parser understands. Anything else found in a task file
# is preserved verbatim through every edit (see extraSections below).
_KNOWN_TASK_SECTIONS = ("description", "acceptance criteria", "notes")

def _split_task_sections(content):
    """Split a task file into (preamble, ordered list of (header, body))."""
    parts = re.split(r"^## (.+)$", content, flags=re.MULTILINE)
    preamble = parts[0]
    sections = []
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        sections.append((header, body.strip("\n")))
    return preamble, sections

def parse_task_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    meta = {
        "id": "", "title": "", "status": "todo", "priority": "medium",
        "assignee": "unassigned", "timeSpent": 0,
        "parent": None, "dependsOn": [], "labels": [], "spec": "", "plan": "",
        "githubIssue": None,
        "description": "", "ac": [], "notes": "", "extraSections": []
    }

    # Parse title
    title_match = re.search(r"^# Task (\d+):\s*(.+)$", content, re.MULTILINE)
    if not title_match:
        raise ValueError(f"Not a valid task file (missing '# Task <id>:' header): {path}")
    meta["id"] = int(title_match.group(1))
    meta["title"] = title_match.group(2).strip()

    preamble, sections = _split_task_sections(content)

    # Parse front metadata (only the preamble, never section bodies)
    for line in preamble.split("\n"):
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
            except ValueError:
                meta["timeSpent"] = 0
        elif line.startswith("**Parent Task:**"):
            val = line.replace("**Parent Task:**", "").strip()
            meta["parent"] = int(val) if val.isdigit() else None
        elif line.startswith("**Depends On:**"):
            val = line.replace("**Depends On:**", "").strip()
            meta["dependsOn"] = [int(x) for x in re.findall(r"\d+", val)] if val and val != "none" else []
        elif line.startswith("**Labels:**"):
            val = line.replace("**Labels:**", "").strip()
            meta["labels"] = [x.strip() for x in val.split(",")] if val and val != "none" else []
        elif line.startswith("**Spec:**"):
            val = line.replace("**Spec:**", "").strip()
            meta["spec"] = val if val and val != "none" else ""
        elif line.startswith("**Plan:**"):
            val = line.replace("**Plan:**", "").strip()
            meta["plan"] = val if val and val != "none" else ""
        elif line.startswith("**GitHub Issue:**"):
            val = line.replace("**GitHub Issue:**", "").replace("#", "").strip()
            meta["githubIssue"] = int(val) if val.isdigit() else None

    for header, body in sections:
        key = header.strip().lower()
        if key == "description":
            meta["description"] = body.strip()
        elif key == "acceptance criteria":
            # Checkboxes are only harvested from this section, so checklists
            # living in Description (or anywhere else) never migrate into ACs.
            for index, (state, ac_text) in enumerate(re.findall(r"-\s*\[([ x/])\]\s*(.+)", body)):
                meta["ac"].append({
                    "index": index + 1,
                    "checked": state == "x",
                    "state": state,
                    "text": ac_text.strip()
                })
        elif key == "notes":
            meta["notes"] = body.strip()
        else:
            meta["extraSections"].append({"header": header, "body": body.strip()})

    return meta

def render_task_content(meta):
    ac_lines = []
    for ac in meta["ac"]:
        if ac.get("checked"):
            chk = "x"
        elif ac.get("state") == "/":
            chk = "/"
        else:
            chk = " "
        ac_lines.append(f"- [{chk}] {ac['text']}")

    ac_str = "\n".join(ac_lines)
    time_spent = meta.get("timeSpent", 0)

    parent_str = f"**Parent Task:** {meta['parent']}" if meta.get("parent") else "**Parent Task:** none"
    depends_str = (f"**Depends On:** {', '.join(str(d) for d in meta['dependsOn'])}"
                   if meta.get("dependsOn") else "**Depends On:** none")
    labels_str = f"**Labels:** {', '.join(meta['labels'])}" if meta.get("labels") else "**Labels:** none"
    spec_str = f"**Spec:** {meta['spec']}" if meta.get("spec") else "**Spec:** none"
    plan_str = f"**Plan:** {meta['plan']}" if meta.get("plan") else "**Plan:** none"
    gh_str = f"**GitHub Issue:** #{meta['githubIssue']}" if meta.get("githubIssue") else "**GitHub Issue:** none"

    # Preserve user notes; only the "Last updated" stamp line is managed.
    notes = meta.get("notes", "")
    if isinstance(notes, list):  # tolerate legacy callers
        notes = "\n".join(notes)
    notes_lines = [l for l in notes.split("\n") if not l.strip().startswith("- Last updated:")]
    notes_lines = [l for l in notes_lines if l.strip()]
    notes_lines.append(f"- Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    notes_str = "\n".join(notes_lines)

    extra_str = ""
    for section in meta.get("extraSections", []):
        extra_str += f"\n## {section['header']}\n{section['body']}\n"

    content = f"""# Task {meta['id']}: {meta['title']}

**Status:** {meta['status']}
**Priority:** {meta['priority']}
**Assignee:** {meta['assignee']}
**Time Spent:** {time_spent} seconds
{parent_str}
{depends_str}
{labels_str}
{spec_str}
{plan_str}
{gh_str}

## Description
{meta['description']}

## Acceptance Criteria
{ac_str}
{extra_str}
## Notes
{notes_str}
"""
    return content

def write_task_file(meta):
    """Atomically overwrite an existing task file."""
    path = os.path.join(TASKS_DIR, f"task-{meta['id']}.md")
    tmp_path = f"{path}.{os.getpid()}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(render_task_content(meta))
    os.replace(tmp_path, path)

def create_task_file(meta):
    """Create a new task file with a race-safe ID: exclusive create, and on
    collision (concurrent CLI/dashboard create) retry with the next ID."""
    next_id = meta["id"]
    for _ in range(1000):
        path = os.path.join(TASKS_DIR, f"task-{next_id}.md")
        meta["id"] = next_id
        try:
            with open(path, "x", encoding="utf-8") as f:
                f.write(render_task_content(meta))
            return next_id
        except FileExistsError:
            next_id += 1
    raise RuntimeError("Could not allocate a free task ID after 1000 attempts.")

def next_task_id():
    existing_ids = []
    if os.path.exists(TASKS_DIR):
        for filename in os.listdir(TASKS_DIR):
            m = re.match(r"task-(\d+)\.md", filename)
            if m:
                existing_ids.append(int(m.group(1)))
    return max(existing_ids) + 1 if existing_ids else 1

def detect_parent_cycle(task_id, new_parent_id):
    """Return True if assigning new_parent_id to task_id would create a
    self-parent or ancestor cycle (which makes tasks vanish from the tree)."""
    if new_parent_id is None:
        return False
    if new_parent_id == task_id:
        return True
    seen = set()
    current = new_parent_id
    while current is not None and current not in seen:
        seen.add(current)
        path = os.path.join(TASKS_DIR, f"task-{current}.md")
        if not os.path.exists(path):
            return False
        try:
            current = parse_task_file(path).get("parent")
        except (ValueError, OSError):
            return False
        if current == task_id:
            return True
    return current is not None  # pre-existing cycle among ancestors


def detect_dependency_cycle(task_id, new_deps):
    """Return True if making task_id depend on new_deps would create a cycle
    in the dependency graph (task_id reachable from any new dependency)."""
    if not new_deps:
        return False
    if task_id in new_deps:
        return True
    seen = set()
    stack = list(new_deps)
    while stack:
        cur = stack.pop()
        if cur == task_id:
            return True
        if cur in seen:
            continue
        seen.add(cur)
        path = os.path.join(TASKS_DIR, f"task-{cur}.md")
        if os.path.exists(path):
            try:
                stack.extend(parse_task_file(path).get("dependsOn", []))
            except (ValueError, OSError):
                pass
    return False

def cmd_task(args):
    ensure_directories()
    if args.task_action == "create":
        next_id = next_task_id()

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
        depends_on = args.depends_on if hasattr(args, "depends_on") and args.depends_on else []

        if parent and not os.path.exists(os.path.join(TASKS_DIR, f"task-{parent}.md")):
            print(f"[-] Error: parent task {parent} does not exist.")
            sys.exit(1)
        for dep in depends_on:
            if not os.path.exists(os.path.join(TASKS_DIR, f"task-{dep}.md")):
                print(f"[-] Error: dependency task {dep} does not exist.")
                sys.exit(1)

        meta = {
            "id": next_id,
            "title": args.title,
            "status": "todo",
            "priority": args.priority or "medium",
            "assignee": assignee,
            "parent": parent,
            "dependsOn": depends_on,
            "labels": labels,
            "spec": spec,
            "plan": plan,
            "description": args.desc or "",
            "ac": [{"index": i+1, "checked": False, "text": ac} for i, ac in enumerate(args.ac or [])]
        }
        next_id = create_task_file(meta)
        print(f"[+] Task created successfully: task-{next_id} (Title: {args.title})")

    elif args.task_action == "next":
        t = _core().next_task()
        if not t:
            print("[*] No actionable task (all done/blocked, or waiting on dependencies).")
            return
        print(f"[+] Next: TASK-{t['id']} [{t['priority']}] {t['title']}")
        if t.get("dependsOn"):
            print(f"    dependencies (all done): {', '.join('task-' + str(d) for d in t['dependsOn'])}")

    elif args.task_action == "list":
        tasks, parse_errors = _core().load_tasks()
        for err in parse_errors:
            print(f"[-] Warning: skipping malformed task file {err}")
        
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
            new_parent = args.parent if args.parent > 0 else None
            if detect_parent_cycle(meta["id"], new_parent):
                print(f"[-] Error: setting parent {new_parent} would create a cycle "
                      f"(task {meta['id']} would become its own ancestor).")
                sys.exit(1)
            meta["parent"] = new_parent
        if hasattr(args, "add_dep") and args.add_dep:
            for dep in args.add_dep:
                if not os.path.exists(os.path.join(TASKS_DIR, f"task-{dep}.md")):
                    print(f"[-] Error: dependency task {dep} does not exist.")
                    sys.exit(1)
                if detect_dependency_cycle(meta["id"], [dep]):
                    print(f"[-] Error: depending on {dep} would create a dependency cycle.")
                    sys.exit(1)
                if dep not in meta["dependsOn"]:
                    meta["dependsOn"].append(dep)
        if hasattr(args, "remove_dep") and args.remove_dep:
            for dep in args.remove_dep:
                if dep in meta["dependsOn"]:
                    meta["dependsOn"].remove(dep)
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
        
        if os.path.exists(doc_file_path):
            rel_existing = os.path.relpath(doc_file_path, DOCS_DIR).replace("\\", "/")
            print(f"[-] Error: a document already exists at @doc/{rel_existing}. "
                  f"Choose a different title or folder.")
            sys.exit(1)

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
    core = _core()

    if args.mem_action == "add":
        new_mem, _memories = core.add_memory(args.content, args.category, args.layer)
        print(f"[+] Memory added successfully under category '{new_mem['category']}'.")

    elif args.mem_action == "list":
        memories = core.load_memories()
        if not memories:
            print("[*] No memories recorded.")
            return
        print(f"{'ID':<4} {'Category':<12} {'Layer':<8} {'Author':<14} {'Content':<40}")
        print("-" * 84)
        for m in memories:
            author = (m.get("author") or "-")[:12]
            print(f"{m['id']:<4} {m['category']:<12} {m['layer']:<8} {author:<14} {m['content'][:38]:<40}")

    elif args.mem_action == "edit":
        updated = core.update_memory(args.id, content=args.content,
                                     category=args.category, layer=args.layer)
        if updated is None:
            print(f"[-] Memory #{args.id} not found.")
            sys.exit(1)
        print(f"[+] Memory #{args.id} updated.")

    elif args.mem_action == "rm":
        if core.delete_memory(args.id):
            print(f"[+] Memory #{args.id} deleted.")
        else:
            print(f"[-] Memory #{args.id} not found.")
            sys.exit(1)

    elif args.mem_action == "review":
        reviewed = core.review_memory(args.id)
        if reviewed is None:
            print(f"[-] Memory #{args.id} not found.")
            sys.exit(1)
        print(f"[+] Memory #{args.id} marked as reviewed (staleness clock reset).")

# ==========================================
# 5.4. INGEST COMMAND (reverse-sync)
# ==========================================
def cmd_ingest(args):
    ensure_directories()
    core = _core()

    if getattr(args, "emit", False):
        # LLM-inversion: hand the raw content to the connected agent to
        # restructure into config.json. AIM stays zero-dependency.
        payload = core.ingest_emit_payload()
        if not payload["sources"]:
            print("[*] No hand-written rule files found to ingest.")
            return
        print(payload["instruction"])
        print()
        for s in payload["sources"]:
            print(f"===== {s['source']} ({s['lines']} lines) =====")
            print(s["content"])
            print()
        return

    sources = core.ingest_sources()
    if not sources:
        print("[*] No hand-written rule files found to ingest "
              "(nothing outside AIM markers in known rule files).")
        return

    print("[*] Found hand-written rules in:")
    for s in sources:
        print(f"  - {s['source']}  ({s['lines']} lines)")

    if getattr(args, "dry_run", False):
        print("\n[*] Dry run - nothing written. Re-run without --dry-run to import.")
        return

    written = core.apply_ingest(sources)
    print("\n[+] Imported into:")
    for w in written:
        print(f"  - {w}")
    print("\n[*] Next steps:")
    print("    1. Review the files under .ai-context/imported/")
    print("    2. Run `aim sync` to re-emit them into every client file")
    print("    3. Remove the now-redundant original rules from the source files")
    print("       (they live inside the AIM markers after sync).")

# ==========================================
# 5.5. DOCTOR COMMAND (context health)
# ==========================================
def cmd_doctor(args):
    ensure_directories()
    author = None
    if getattr(args, "mine", False):
        author = _core().current_author()
        print(f"[*] Showing context-health findings for: {author}\n")

    findings = _core().run_diagnostics(author=author)

    icons = {"high": "HIGH  ", "medium": "MEDIUM", "low": "LOW   ", "info": "INFO  "}
    print("=========================================")
    print("        AIM Context Health Report        ")
    print("=========================================")
    if not findings:
        print("[+] No context-drift issues found. Your context layer is healthy.")
        return

    counts = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
        line = f"{icons.get(f['severity'], f['severity'])}  {f['message']}"
        print(line)
        if f.get("fix"):
            print(f"        -> fix: {f['fix']}")

    summary = ", ".join(f"{counts[s]} {s}" for s in ("high", "medium", "low", "info") if s in counts)
    print("-" * 41)
    print(f"Summary: {summary}")

    # Exit non-zero on actionable findings so `aim doctor` works as a CI gate.
    if any(f["severity"] in ("high", "medium") for f in findings):
        sys.exit(1)

# ==========================================
# 6. LOCAL SEARCH COMMAND
# ==========================================
def cmd_search(args):
    ensure_directories()
    query = args.query.lower()
    print(f"[*] Searching for '{query}' across tasks, docs, and memory...\n")

    results = _core().search_workspace(query, context=30)

    if not results:
        print("[*] No matches found.")
        return

    print(f"{'Type':<8} {'Reference':<30} {'Match Snippet'}")
    print("-" * 88)
    for r in results:
        if r["type"] == "memory":
            ref = f"Memory #{r['id']} ({r['category']})"
        else:
            ref = r["ref"]
        print(f"{r['type']:<8} {ref:<30} {r['snippet']}")

# ==========================================
# 7. VALIDATE REFERENCES COMMAND
# ==========================================
def cmd_validate(args):
    ensure_directories()
    core = _core()
    print("[*] Validating project memory layer references...")

    errors = core.validate_references()
    for err in errors:
        if err["kind"] == "task":
            print(f"[-] Broken task link in {err['source']}: @task-{err['ref']} does not exist.")
        else:
            print(f"[-] Broken doc link in {err['source']}: @doc/{err['ref']} does not exist.")

    missing_spec = []
    if getattr(args, "require_spec", False):
        missing_spec = core.tasks_without_spec()
        for tid in missing_spec:
            print(f"[-] Task {tid} has no linked spec (--require-spec).")

    total = len(errors) + len(missing_spec)
    if total == 0:
        print("[+] All references are healthy!")
    else:
        print(f"[-] Found {total} issue(s).")
        sys.exit(1)

# ==========================================
# 7.6. GITHUB SYNC COMMANDS
# ==========================================
def cmd_github(args):
    ensure_directories()
    core = _core()
    if not core.github_available():
        print("[-] GitHub CLI (gh) not found or not authenticated.")
        print("    Install gh (https://cli.github.com) and run `gh auth login`.")
        sys.exit(1)

    if args.github_action == "create-project":
        try:
            data = core.create_project(args.title)
        except RuntimeError as e:
            print(f"[-] {e}")
            sys.exit(1)
        print(f"[+] Created project #{data.get('number')}: {data.get('url')}")
        print(f"[*] Push tasks into it with: aim github push --all --project {data.get('number')}")

    elif args.github_action == "push":
        try:
            if args.id:
                results = [core.push_task(args.id, project=args.project)]
            else:
                results = core.push_all(project=args.project)
        except RuntimeError as e:
            print(f"[-] {e}")
            sys.exit(1)
        if not results:
            print("[*] No tasks to push.")
            return
        for r in results:
            print(f"[+] TASK-{r['taskId']} -> issue #{r['issue']} ({r['action']}, status={r['status']})")
        if args.project:
            print(f"[+] Linked issues to project #{args.project}.")

    elif args.github_action == "status":
        rows = core.github_status()
        if not rows:
            print("[*] No tasks found.")
            return
        print(f"{'Task':<6} {'Issue':<8} {'Status':<12} {'Title'}")
        print("-" * 70)
        for r in rows:
            issue = f"#{r['issue']}" if r["issue"] else "-"
            print(f"{r['taskId']:<6} {issue:<8} {r['status']:<12} {r['title'][:40]}")

# ==========================================
# 7.5. SPEC COMMANDS (spec-driven development)
# ==========================================
def cmd_spec(args):
    ensure_directories()
    core = _core()

    if args.spec_action == "import":
        try:
            result = core.import_spec(args.dir, name=args.name)
        except ValueError as e:
            print(f"[-] {e}")
            sys.exit(1)
        print(f"[+] Imported spec '{result['name']}':")
        print(f"  - spec doc:  @doc/{result['specDoc']}")
        if result.get("planDoc"):
            print(f"  - plan doc:  @doc/{result['planDoc']}")
        print(f"  - umbrella task: TASK-{result['taskId']}")
        print("[*] Expand it into subtasks with the MCP `decompose_prd` prompt, "
              "or `aim task create ... --depends-on`.")

    elif args.spec_action == "coverage":
        cov = core.spec_coverage()
        print("Spec coverage:")
        print(f"  {cov['withSpec']}/{cov['total']} tasks have a linked spec.")
        if cov["withoutSpec"]:
            print(f"  Missing: {', '.join('task-' + str(t) for t in cov['withoutSpec'])}")

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
    tasks, _parse_errors = _core().load_tasks()

    statuses = ["todo", "in-progress", "in-review", "blocked", "done"]
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
    seconds = max(0, int(seconds))
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
        save_json(TIMER_STATE_PATH, timer_state)

        print(f"[+] Timer started for task {task_id} ({task['title']})")
        
    elif args.time_action == "stop":
        if not os.path.exists(TIMER_STATE_PATH):
            print("[-] No active timer.")
            sys.exit(1)

        with open(TIMER_STATE_PATH, "r", encoding="utf-8") as f:
            timer_state = json.load(f)

        task_id = timer_state["taskId"]
        # Clamp so a backwards clock adjustment never produces negative time.
        duration = max(0, int(time.time() - timer_state["startedAt"]))

        # Persist results FIRST; only delete the timer state once the session
        # has been recorded, so a failure cannot lose the tracked time.
        task_path = os.path.join(TASKS_DIR, f"task-{task_id}.md")
        if os.path.exists(task_path):
            task = parse_task_file(task_path)
            task["timeSpent"] = task.get("timeSpent", 0) + duration
            write_task_file(task)

        logs = load_json(TIME_LOG_PATH, [])
        entry = {
            "id": f"te-{int(time.time()*1000)}",
            "taskId": task_id,
            "startedAt": datetime.datetime.fromtimestamp(timer_state["startedAt"]).isoformat(),
            "endedAt": datetime.datetime.now().isoformat(),
            "duration": duration,
            "note": args.note or ""
        }
        logs.append(entry)
        save_json(TIME_LOG_PATH, logs)

        os.remove(TIMER_STATE_PATH)

        print(f"[+] Timer stopped for task {task_id}. Elapsed: {format_duration(duration)}")
        
    elif args.time_action == "status":
        if not os.path.exists(TIMER_STATE_PATH):
            print("[*] No active timer.")
            return
            
        with open(TIMER_STATE_PATH, "r", encoding="utf-8") as f:
            timer_state = json.load(f)
            
        elapsed = int(time.time() - timer_state["startedAt"])
        print("[*] Active Timer:")
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

        updated_tasks, errors = _core().rename_user_propagate(old_username, new_username)
        for err in errors:
            print(f"[-] Error updating task {err}")

        print(f"[+] User '{old_username}' renamed to '{new_username}' successfully.")
        if updated_tasks > 0:
            print(f"[+] Propagated changes to {updated_tasks} task(s).")

# ==========================================
# 11. STATUS COMMAND
# ==========================================
def cmd_status(args):
    ensure_directories()
    status = _core().collect_status()

    status_breakdown = ", ".join([f"{k}: {v}" for k, v in status["statusCounts"].items()])
    tech_stack = status["techStack"]

    active_timer_str = "None"
    if status["activeTimer"]:
        timer = status["activeTimer"]
        active_timer_str = (f"Task {timer['taskId']} ({timer['title']}) - "
                            f"active for {format_duration(timer['elapsed'])}")

    # Print status report
    print("=========================================")
    print("         AIM Project Status Summary      ")
    print("=========================================")
    print(f"Project Name:  {status['projectName']}")
    print(f"Tech Stack:    {', '.join(tech_stack) if tech_stack else 'Not configured'}")
    print(f"Workspace:     {status['projectRoot']}")
    print()
    print("Memory Layer Statistics:")
    print(f"  Tasks:       {len(status['tasks'])} total ({status_breakdown})")
    print(f"  Docs:        {status['docsCount']} files (@doc/)")
    print(f"  Memories:    {len(status['memories'])} entries recorded")
    print()
    print("Time Tracking:")
    print(f"  Total Spent: {format_duration(status['totalTimeSpent'])}")
    print(f"  Active:      {active_timer_str}")
    print()
    print("Agent Config Sync Status:")
    for label, sync_status in status["syncStatuses"].items():
        print(f"  {label:<30} [{sync_status}]")
    print(f"  Sync Health: {'Healthy & Synchronized' if status['allSynced'] else 'Out of sync / Run `aim sync` to update'}")
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

def _strip_yaml_comment(line):
    """Strip a trailing # comment, but only when the # is outside quotes and
    preceded by whitespace (so values like 'color: #fff' survive)."""
    in_single = in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if i == 0 or line[i - 1] in " \t":
                return line[:i]
    return line

def parse_yaml(content):
    data = {}
    lines = content.splitlines()
    current_key = None
    current_list = None

    for line in lines:
        line_clean = _strip_yaml_comment(line).rstrip()
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
                    # Every "- key: value" line starts a NEW list entry;
                    # continuation lines (no leading dash) extend the last one.
                    current_list.append({k: v})
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
# 12.5. MCP SERVER COMMAND
# ==========================================
def cmd_mcp(args):
    try:
        from aim.mcp_server import run_stdio_server
    except ImportError:
        from mcp_server import run_stdio_server
    run_stdio_server()

# ==========================================
# 13. DEMO GENERATOR COMMAND
# ==========================================
def cmd_generator_demo(args):
    ensure_directories()
    print("[*] Generating AeroMap Google Maps alternative demo workspace...")
    
    # 1. Users
    demo_users = ["alice", "bob", "charlotte", "developer", "unassigned"]
    save_users(demo_users)
    print("  [+] Configured users.json")
    
    # 2. Docs
    docs_to_create = {
        "architecture/system-design.md": """# AeroMap: High-Level System Architecture 🗺️

This document outlines the high-level architecture of **AeroMap**, an open-source, high-performance alternative to Google Maps. The project is designed with modular microservices to optimize data ingestion, map rendering, and routing calculation.

---

## 🏗️ Architecture Component Overview

```mermaid
graph TD
    User([Web / Mobile Client]) --> CDN[Cloudflare CDN]
    CDN --> WebApp[Frontend App: MapLibre GL JS / React]
    WebApp -->|Tile Requests| TileServer[Tegola Vector Tile Server]
    WebApp -->|Routing Requests| RoutingAPI[Valhalla API Service]
    WebApp -->|Search / Geocode| Geocoder[Photon / Nominatim API]
    
    TileServer --> PostGIS[(PostgreSQL + PostGIS DB)]
    RoutingAPI --> OSMData[OSM Graph Binary Files]
    Geocoder --> NominatimDB[(Nominatim Database)]
```

### 1. Vector Tile Server (Tegola)
We utilize **Tegola** to serve vector tiles (MVT format) dynamically computed from spatial datasets.
- Tegola connects directly to our Postgres/PostGIS instance.
- Map tiles are cached on CDN edges to reduce db queries.

### 2. Frontend Map Rendering (MapLibre GL JS)
Clients render map visuals dynamically using WebGL.
- **Client library**: MapLibre GL JS (stable, high performance).
- **Styling**: OpenMapTiles schema with tailored custom themes.

### 3. Spatial Database (PostgreSQL + PostGIS)
All spatial coordinates and geography details are stored here:
- Coordinate system: EPSG:4326 (WGS 84).
- Indexes: GIST spatial indexes on geometry columns.

### 4. Routing Engine (Valhalla)
Calculates path-finding, multi-modal routing, and navigation steps.
- Compiles OpenStreetMap (OSM) data into custom routing graphs.
- Supports offline mobile database integration.
""",
        "api/routing-api.md": """# AeroMap: Routing API Specification 🚗

This document details the interface and specifications for the AeroMap pathfinding service.

---

## 🚀 Directions / Route Endpoint

Calculates the optimal route between coordinates for various modes of transportation.

- **URL:** `/api/v1/route`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`

### 1. Request Body Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `locations` | array | Yes | List of coordinate pairs `[lng, lat]`. Must contain at least 2 locations. |
| `costing` | string | No | Mode of transport: `auto`, `bicycle`, `pedestrian`, `transit`. Default: `auto`. |
| `language` | string | No | Language tag for navigation instructions. Default: `en-US`. |

#### Example Payload:
```json
{
  "locations": [
    {"lon": 105.8544, "lat": 21.0285},
    {"lon": 105.7801, "lat": 21.0381}
  ],
  "costing": "auto",
  "language": "vi-VN"
}
```

### 2. Response Structure

Returns a JSON object representing the route path, duration, distance, and navigation maneuvers.

#### Example Success Response (200 OK):
```json
{
  "status": "success",
  "trip": {
    "summary": {
      "time_seconds": 920.5,
      "distance_km": 8.35
    },
    "legs": [
      {
        "maneuvers": [
          {
            "instruction": "Đi thẳng về hướng Tây trên phố Tràng Thi.",
            "distance_meters": 450,
            "time_seconds": 60
          },
          {
            "instruction": "Rẽ phải vào Điện Biên Phủ.",
            "distance_meters": 1200,
            "time_seconds": 150
          }
        ],
        "shape": "g~`hE_gse@sBmAcCiD..."
      }
    ]
  }
}
```
""",
        "guides/offline-sync.md": """# AeroMap: Offline Tile Synchronization Guide 📶

This guide outlines the synchronization mechanisms and local storage models to support offline map capabilities in AeroMap web and mobile applications.

---

## 💾 Local Storage Strategy

Offline maps require caching vector tiles (Protobuf `.pbf` format) locally on the client.

```
+-------------------------------------------------------------+
|                     Client Map Engine                       |
+-------------------------------------------------------------+
                               |
               (Request Tile z/x/y)
                               v
+-------------------------------------------------------------+
|                  Service Worker / Cache                     |
+-------------------------------------------------------------+
         |                                           |
    (Cache hit)                                 (Cache miss)
         v                                           v
+------------------+                       +------------------+
|    IndexedDB     |                       |    Fetch URL     |
+------------------+                       +------------------+
                                                     |
                                                (Saves PBF)
                                                     v
                                           +------------------+
                                           |    IndexedDB     |
                                           +------------------+
```

### 1. Web Clients (IndexedDB)
- **Library**: `localForage` or vanilla IndexedDB wrapper.
- **Store Name**: `aeromap_tiles_cache`.
- **Key Schema**: `style_id/z/x/y`.
- **Value**: Binary ArrayBuffer of the vector tile PBF data, with a timestamp metadata attribute.

### 2. Native Mobile Clients (SQLite)
- For native Android/iOS clients, we packages MBTiles databases.
- Tiles are queried using standard `SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?` statements.

---

## 🔄 Synchronization Pipeline

1. **Pre-download Region**: User selects a bounding box (BBOX) on the map and chooses a maximum zoom level (up to z15).
2. **Download Queue**: Client queue fetches tiles in batches of 10 concurrent requests.
3. **Storage**: Each tile is saved with an expiration date (default: 30 days).
4. **Purging**: When memory usage exceeds the browser quota, the application drops tiles based on a Least Recently Used (LRU) algorithm.
"""
    }
    for rel_path, doc_content in docs_to_create.items():
        full_path = os.path.join(DOCS_DIR, os.path.normpath(rel_path))
        parent_dir = os.path.dirname(full_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(doc_content)
        print(f"  [+] Created doc: @doc/{rel_path}")
        
    # 3. Tasks
    tasks_to_create = {
        "task-1.md": """# Task 1: Setup AeroMap High-Level System Architecture

**Status:** done
**Priority:** high
**Assignee:** alice
**Time Spent:** 3600 seconds
**Parent Task:** none
**Labels:** architecture, documentation
**Spec:** @doc/architecture/system-design.md
**Plan:** none

## Description
Research and document the system design, components, databases, and microservices needed for AeroMap.

## Acceptance Criteria
- [x] Draft high-level component diagrams using Mermaid
- [x] Detail technical specifications for the Vector Tile Server
- [x] Select client-side map rendering library (MapLibre GL JS)
- [x] Document physical data model and database choices (PostGIS)

## Notes
- Last updated: 2026-06-10 16:40:00
""",
        "task-2.md": """# Task 2: Implement Vector Tile Rendering Engine

**Status:** in-progress
**Priority:** high
**Assignee:** charlotte
**Time Spent:** 1800 seconds
**Parent Task:** 1
**Labels:** frontend, map-rendering
**Spec:** @doc/architecture/system-design.md
**Plan:** none

## Description
Set up MapLibre GL JS / Leaflet on the client interface to request and render vector tiles from the Tegola server.

## Acceptance Criteria
- [x] Install MapLibre GL JS library
- [ ] Render basic world map with OpenMapTiles style
- [ ] Connect tiles source to Tegola mock endpoints
- [ ] Add controls for zooming, panning, and toggling custom layer styles

## Notes
- Last updated: 2026-06-10 16:42:00
""",
        "task-3.md": """# Task 3: Develop Routing API Service

**Status:** todo
**Priority:** high
**Assignee:** bob
**Time Spent:** 0 seconds
**Parent Task:** none
**Labels:** backend, routing
**Spec:** @doc/api/routing-api.md
**Plan:** none

## Description
Deploy the Valhalla pathfinding engine in a Docker container and set up our API gateway to route requests to it.

## Acceptance Criteria
- [ ] Configure Valhalla Docker container with OSM data for Vietnam region
- [ ] Implement proxy controller `/api/v1/route` that forwards payloads to Valhalla
- [ ] Parse Valhalla JSON responses and return them in standard AeroMap routing format

## Notes
- Last updated: 2026-06-10 16:45:00
""",
        "task-4.md": """# Task 4: Optimize Route Search Algorithm

**Status:** todo
**Priority:** medium
**Assignee:** bob
**Time Spent:** 0 seconds
**Parent Task:** 3
**Labels:** backend, performance
**Spec:** none
**Plan:** none

## Description
Pre-compile contraction hierarchies for the OSM graph of the target region to reduce route calculation latency.

## Acceptance Criteria
- [ ] Write shell script to automate OSM data graph compilation
- [ ] Measure routing calculation response times (must be under 50ms for typical city routes)
- [ ] Enable multithreaded cost estimation queries in Valhalla config

## Notes
- Last updated: 2026-06-10 16:47:00
""",
        "task-5.md": """# Task 5: Implement Multi-Modal Routing (Transit & Walking)

**Status:** todo
**Priority:** medium
**Assignee:** unassigned
**Time Spent:** 0 seconds
**Parent Task:** 3
**Labels:** backend, routing
**Spec:** @doc/api/routing-api.md
**Plan:** none

## Description
Integrate public transit schedules (GTFS feeds) and pedestrian walking trails into the Valhalla graph compiler.

## Acceptance Criteria
- [ ] Import city GTFS feed into routing database
- [ ] Implement query costing calculations for pedestrian paths and sidewalks
- [ ] Allow combining walk-to-station, transit ride, and walk-to-destination paths in a single trip object

## Notes
- Last updated: 2026-06-10 16:50:00
""",
        "task-6.md": """# Task 6: Implement Offline Map Tile Caching

**Status:** in-review
**Priority:** medium
**Assignee:** charlotte
**Time Spent:** 2400 seconds
**Parent Task:** none
**Labels:** mobile, offline
**Spec:** @doc/guides/offline-sync.md
**Plan:** none

## Description
Develop a caching policy that allows offline vector map tiles request intercepts via service workers, storing tiles inside local IndexedDB.

## Acceptance Criteria
- [x] Configure service worker to intercept tile URLs (`/tile/{z}/{x}/{y}.pbf`)
- [x] Integrate localForage for asynchronous IndexedDB caching
- [x] Write LRU cache eviction policy for offline database storage
- [ ] Implement UI indicators showing offline sync progress and bounding box selections

## Notes
- Last updated: 2026-06-10 16:53:00
"""
    }
    for filename, task_content in tasks_to_create.items():
        full_path = os.path.join(TASKS_DIR, filename)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(task_content)
        print(f"  [+] Created task: {filename}")
        
    # 4. Memories
    demo_memories = [
      {
        "id": 1,
        "content": "Use MapLibre GL for client-side vector tile rendering due to styling flexibility and performance.",
        "category": "decision",
        "layer": "project",
        "createdAt": datetime.datetime.now().isoformat()
      },
      {
        "id": 2,
        "content": "Store spatial coordinates in PostGIS (EPSG:4326) and index them using GIST indexes.",
        "category": "convention",
        "layer": "project",
        "createdAt": datetime.datetime.now().isoformat()
      },
      {
        "id": 3,
        "content": "Cache Valhalla routing query responses in Redis using a 1-hour TTL.",
        "category": "optimization",
        "layer": "project",
        "createdAt": datetime.datetime.now().isoformat()
      }
    ]
    with open(MEMORIES_PATH, "w", encoding="utf-8") as f:
        json.dump(demo_memories, f, indent=2)
    print("  [+] Created memories.json")
    
    # 5. Templates
    tpl_dir = os.path.join(TEMPLATES_DIR, "map-component")
    if not os.path.exists(tpl_dir):
        os.makedirs(tpl_dir)
        
    tpl_yaml = """name: map-component
description: Generates a reusable React MapLibre Component
version: 1.0.0
destination: src
prompts:
  - name: name
    type: text
    message: Enter component name
    validate: required
actions:
  - type: add
    template: component.hbs
    path: components/{{pascalCase name}}.tsx
"""
    with open(os.path.join(tpl_dir, "_template.yaml"), "w", encoding="utf-8") as f:
        f.write(tpl_yaml)
        
    tpl_hbs = """import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

interface {{pascalCase name}}Props {
  center?: [number, number]; // [lng, lat]
  zoom?: number;
  styleUrl?: string;
}

export const {{pascalCase name}}: React.FC<{{pascalCase name}}Props> = ({
  center = [105.8544, 21.0285], // default: Hanoi
  zoom = 12,
  styleUrl = 'https://tiles.basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: styleUrl,
      center: center,
      zoom: zoom
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [center, zoom, styleUrl]);

  return (
    <div className="map-wrapper relative w-full h-full min-h-[400px]">
      <div ref={mapContainer} className="absolute inset-0 w-full h-full rounded-lg shadow-lg" />
    </div>
  );
};

export default {{pascalCase name}};
"""
    with open(os.path.join(tpl_dir, "component.hbs"), "w", encoding="utf-8") as f:
        f.write(tpl_hbs)
    print("  [+] Created map-component template")
    print("[+] AeroMap Google Maps demo workspace generated successfully.")

# ==========================================
# MAIN DISPATCHER
# ==========================================
def main():
    configure_utf8_output()
    parser = argparse.ArgumentParser(
        description="AIM (AI Memory/Mind) CLI - Centralized Project Context & Memory Engine",
        prog="aim"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    init_parser = subparsers.add_parser("init", help="Initialize AIM in the project root")
    init_parser.add_argument("--force", action="store_true",
                             help="Reinstall skills/agents even if they already exist (keeps a .bak backup)")
    
    # sync
    subparsers.add_parser("sync", help="Synchronize active config and compile shims")
    
    # task
    task_parser = subparsers.add_parser("task", help="Manage project tasks")
    task_sub = task_parser.add_subparsers(dest="task_action", required=True)
    
    task_sub.add_parser("list", help="List all tasks")

    task_sub.add_parser("next", help="Show the next actionable task (deps satisfied, by priority)")

    create_task = task_sub.add_parser("create", help="Create a new task")
    create_task.add_argument("title", help="Task title")
    create_task.add_argument("-d", "--desc", help="Task description")
    create_task.add_argument("--ac", action="append", help="Acceptance criteria item")
    create_task.add_argument("-p", "--priority", choices=["low", "medium", "high", "urgent"], help="Task priority")
    create_task.add_argument("-a", "--assignee", help="Task assignee")
    create_task.add_argument("--parent", type=int, help="Parent task ID")
    create_task.add_argument("--depends-on", action="append", type=int, help="Prerequisite task ID (repeatable)")
    create_task.add_argument("-l", "--label", action="append", help="Label tag (repeatable)")
    create_task.add_argument("--spec", help="Linked spec document path")
    create_task.add_argument("--plan", help="Linked plan document path")

    view_task = task_sub.add_parser("view", help="View a specific task")
    view_task.add_argument("id", type=int, help="Task ID")
    
    edit_task = task_sub.add_parser("edit", help="Edit a task's status or assignee")
    edit_task.add_argument("id", type=int, help="Task ID")
    edit_task.add_argument("-s", "--status", choices=["todo", "in-progress", "in-review", "blocked", "done"],
                           help="Update status")
    edit_task.add_argument("-a", "--assignee", help="Assignee user")
    edit_task.add_argument("--add-ac", help="Add acceptance criteria item")
    edit_task.add_argument("--check-ac", type=int, help="Mark AC index as completed (1-based)")
    edit_task.add_argument("--parent", type=int, help="Update parent task ID")
    edit_task.add_argument("--add-dep", action="append", type=int, help="Add a prerequisite task ID (repeatable)")
    edit_task.add_argument("--remove-dep", action="append", type=int, help="Remove a prerequisite task ID (repeatable)")
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

    edit_mem = mem_sub.add_parser("edit", help="Edit a memory")
    edit_mem.add_argument("id", type=int, help="Memory ID")
    edit_mem.add_argument("content", nargs="?", help="New memory statement")
    edit_mem.add_argument("-c", "--category", help="Update category")
    edit_mem.add_argument("-l", "--layer", choices=["project", "global"], help="Move to storage layer")

    rm_mem = mem_sub.add_parser("rm", help="Delete a memory")
    rm_mem.add_argument("id", type=int, help="Memory ID")

    review_mem = mem_sub.add_parser("review", help="Mark a memory as verified (reset staleness clock)")
    review_mem.add_argument("id", type=int, help="Memory ID")

    # search
    search_parser = subparsers.add_parser("search", help="Search across tasks, docs, and memory")
    search_parser.add_argument("query", help="Search query string")

    # validate
    validate_parser = subparsers.add_parser("validate", help="Validate links and references health")
    validate_parser.add_argument("--require-spec", action="store_true", help="Also flag tasks that have no linked spec")

    # spec
    spec_parser = subparsers.add_parser("spec", help="Spec-driven development helpers")
    spec_sub = spec_parser.add_subparsers(dest="spec_action", required=True)
    import_spec_p = spec_sub.add_parser("import", help="Import a spec-kit directory (spec.md/plan.md) into AIM docs + an umbrella task")
    import_spec_p.add_argument("dir", help="Path to the spec-kit feature directory")
    import_spec_p.add_argument("--name", help="Override the spec name (default: directory name)")
    spec_sub.add_parser("coverage", help="Show spec-link coverage across tasks")

    # github
    github_parser = subparsers.add_parser("github", help="Sync tasks to GitHub Issues / Projects (via the gh CLI)")
    github_sub = github_parser.add_subparsers(dest="github_action", required=True)
    gh_push = github_sub.add_parser("push", help="Create/update a GitHub issue per task (idempotent)")
    gh_push.add_argument("id", type=int, nargs="?", help="Task ID (omit, or use --all, to push every task)")
    gh_push.add_argument("--all", action="store_true", help="Push every task (default when no ID is given)")
    gh_push.add_argument("--project", type=int, help="Also add issues to this Project (v2) number")
    github_sub.add_parser("status", help="Show task <-> GitHub issue linkage")
    gh_proj = github_sub.add_parser("create-project", help="Create a GitHub Project (v2) for this repo")
    gh_proj.add_argument("title", help="Project title")

    # ingest
    ingest_parser = subparsers.add_parser("ingest", help="Import existing hand-written rule files (CLAUDE.md, .cursorrules, ...) into AIM")
    ingest_parser.add_argument("--dry-run", action="store_true", help="Preview what would be imported without writing")
    ingest_parser.add_argument("--emit", action="store_true", help="Print raw content + an instruction for the connected agent to restructure into config (zero-dependency LLM inversion)")

    # doctor
    doctor_parser = subparsers.add_parser("doctor", help="Diagnose context drift (stale memory, broken refs, id clashes)")
    doctor_parser.add_argument("--mine", action="store_true", help="Only show findings for memories you authored")

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
    
    # mcp
    subparsers.add_parser("mcp", help="Run the AIM MCP server over stdio (for Claude Code / Cursor integration)")

    # generator / demo
    generator_parser = subparsers.add_parser("generator", help="Generate demo workspaces and templates")
    generator_sub = generator_parser.add_subparsers(dest="generator_action", required=True)
    generator_sub.add_parser("demo", help="Generate the interactive AeroMap Google Maps demo workspace")
    
    # top-level demo command alias
    subparsers.add_parser("demo", help="Generate the interactive AeroMap Google Maps demo workspace")
    
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
    elif args.command == "spec":
        cmd_spec(args)
    elif args.command == "github":
        cmd_github(args)
    elif args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "doctor":
        cmd_doctor(args)
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
    elif args.command == "mcp":
        cmd_mcp(args)
    elif args.command == "generator":
        if args.generator_action == "demo":
            cmd_generator_demo(args)
    elif args.command == "demo":
        cmd_generator_demo(args)

if __name__ == "__main__":
    main()
