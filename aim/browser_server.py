import os
import json
import http.server
import socketserver
import webbrowser
import urllib.parse
import sys
import re
import time
import secrets
import datetime

# Import helpers
try:
    from aim.aim_cli import parse_task_file, write_task_file, create_task_file, next_task_id, \
        detect_parent_cycle, ensure_directories, get_project_root, configure_utf8_output, \
        load_json, save_json, _is_within
    from aim.aim_cli import TASKS_DIR, DOCS_DIR, load_users, save_users
except ImportError:
    from aim_cli import parse_task_file, write_task_file, create_task_file, next_task_id, \
        detect_parent_cycle, ensure_directories, get_project_root, configure_utf8_output, \
        load_json, save_json, _is_within
    from aim_cli import TASKS_DIR, DOCS_DIR, load_users, save_users

try:
    from aim import core
except ImportError:
    import core

# Per-launch session token. It is embedded into the served HTML and required
# on every /api request, so no other website (or DNS-rebound host) can read
# or mutate workspace data through this server.
SESSION_TOKEN = secrets.token_hex(16)

def safe_task_path(task_id):
    """Build the path for a task id, rejecting anything that is not a plain
    integer (blocks ../ path traversal through the id field)."""
    tid = str(task_id).strip()
    if not tid.isdigit():
        return None
    return os.path.join(TASKS_DIR, f"task-{int(tid)}.md")

# The dashboard SPA lives in dashboard.html next to this module
# (kept out of the Python source; shipped via package_data).
_DASHBOARD_HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.html")
with open(_DASHBOARD_HTML_PATH, "r", encoding="utf-8") as _f:
    HTML_CONTENT = _f.read()

class AIMBrowserHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress stdout logs to keep terminal output clean
        pass

    def send_json(self, data, status=200):
        # NOTE: deliberately no CORS headers. The dashboard SPA is served
        # same-origin from this server; emitting Access-Control-Allow-Origin
        # would let any website the user visits read/mutate workspace data.
        try:
            content = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error writing response: {e}")

    def is_request_allowed(self):
        """Reject DNS-rebinding (foreign Host header) and any caller that
        does not present the per-launch session token."""
        host = self.headers.get("Host", "").split(":")[0].lower()
        if host not in ("localhost", "127.0.0.1", "[::1]", "::1"):
            return False
        token = self.headers.get("X-AIM-Token", "")
        return secrets.compare_digest(token, SESSION_TOKEN)

    def reject_unauthorized(self):
        self.send_json({"error": "Unauthorized"}, 403)

    def do_OPTIONS(self):
        # Same-origin requests never need a CORS preflight; respond without
        # any Access-Control-* headers so cross-origin callers stay blocked.
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        ensure_directories()
        parsed_url = urllib.parse.urlparse(self.path)

        # 1. Serves SPA Frontend
        if parsed_url.path == "/" or parsed_url.path == "/index.html":
            host = self.headers.get("Host", "").split(":")[0].lower()
            if host not in ("localhost", "127.0.0.1", "[::1]", "::1"):
                self.send_error(403, "Forbidden")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.replace("__AIM_SESSION_TOKEN__", SESSION_TOKEN).encode("utf-8"))
            return

        if parsed_url.path.startswith("/api/") and not self.is_request_allowed():
            self.reject_unauthorized()
            return
            
        # 2. API Root
        elif parsed_url.path == "/api/root":
            self.send_json({"root": get_project_root()})
            return

        # 2.5. API Status (Overview metrics and system health)
        elif parsed_url.path == "/api/status":
            try:
                from aim.aim_cli import format_duration
            except ImportError:
                from aim_cli import format_duration

            status = core.collect_status()
            counts = status["statusCounts"]
            memories = status["memories"]
            logs = status["timeLogs"]

            active_timer = status["activeTimer"]
            if active_timer:
                active_timer = dict(active_timer)
                active_timer["formattedElapsed"] = format_duration(active_timer["elapsed"])

            errors = len(core.validate_references())

            status_payload = {
                "projectName": status["projectName"],
                "techStack": status["techStack"],
                "projectRoot": status["projectRoot"],
                "tasks": {
                    "total": len(status["tasks"]),
                    "todo": counts.get("todo", 0),
                    "inProgress": counts.get("in-progress", 0),
                    "inReview": counts.get("in-review", 0),
                    "done": counts.get("done", 0)
                },
                "docsCount": status["docsCount"],
                "memoriesCount": len(memories),
                "totalTimeSpent": status["totalTimeSpent"],
                "formattedTotalTime": format_duration(status["totalTimeSpent"]),
                "activeTimer": active_timer,
                "sync": {
                    "allSynced": status["allSynced"],
                    "files": status["syncStatuses"]
                },
                "health": {
                    "errors": errors,
                    "isHealthy": errors == 0
                },
                "recentLogs": logs[-5:] if logs else [],
                "recentMemories": memories[-5:] if memories else []
            }
            self.send_json(status_payload)
            return

        # 3. List Tasks API
        elif parsed_url.path == "/api/tasks":
            tasks, parse_errors = core.load_tasks()
            for err in parse_errors:
                print(f"[-] Error parsing task file {err}")
            self.send_json(tasks)
            return

        # 4. List Docs API
        elif parsed_url.path == "/api/docs":
            self.send_json(core.load_docs())
            return

        # 5. List Memories API
        elif parsed_url.path == "/api/memories":
            self.send_json(core.load_memories())
            return

        # 5.05. Doctor API (context-drift findings)
        elif parsed_url.path == "/api/doctor":
            self.send_json(core.run_diagnostics())
            return

        # 5.1. List Users API
        elif parsed_url.path == "/api/users":
            self.send_json(load_users())
            return
        elif parsed_url.path == "/api/search":
            query_params = urllib.parse.parse_qs(parsed_url.query)
            query = query_params.get("q", [""])[0].lower().strip()
            self.send_json(core.search_workspace(query, context=40))
            return

        # 5.15. App Builder Templates API
        elif parsed_url.path == "/api/app-builder/templates":
            templates = []
            try:
                base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "aim-agents", "skills", "app-builder", "templates")
                if os.path.exists(base_dir):
                    for name in sorted(os.listdir(base_dir)):
                        t_dir = os.path.join(base_dir, name)
                        if os.path.isdir(t_dir):
                            tpl_file = os.path.join(t_dir, "TEMPLATE.md")
                            if os.path.exists(tpl_file):
                                with open(tpl_file, "r", encoding="utf-8") as f:
                                    content = f.read()
                                meta = {"name": name, "description": f"Template for {name}", "content": content}
                                if content.startswith("---"):
                                    parts = content.split("---", 2)
                                    if len(parts) >= 3:
                                        for line in parts[1].strip().splitlines():
                                            if ":" in line:
                                                k, _, v = line.partition(":")
                                                meta[k.strip()] = v.strip().strip('"').strip("'")
                                templates.append(meta)
            except Exception as e:
                print(f"[-] Error loading app builder templates: {e}")
            self.send_json(templates)
            return

        # 5.5. Graph API
        elif parsed_url.path == "/api/graph":
            nodes = []
            links = []
            
            existing_tasks = set()
            existing_docs = set()
            
            # Scan Tasks
            tasks_data = []
            if os.path.exists(TASKS_DIR):
                for filename in os.listdir(TASKS_DIR):
                    if filename.startswith("task-") and filename.endswith(".md"):
                        try:
                            t = parse_task_file(os.path.join(TASKS_DIR, filename))
                            node_id = f"task-{t['id']}"
                            existing_tasks.add(t['id'])
                            nodes.append({
                                "id": node_id,
                                "label": f"TASK-{t['id']}: {t['title'][:25]}...",
                                "type": "task",
                                "status": t.get("status", "todo"),
                                "rawId": t['id']
                            })
                            with open(os.path.join(TASKS_DIR, filename), "r", encoding="utf-8") as f:
                                tasks_data.append((node_id, f.read()))
                        except Exception:
                            pass
                            
            # Scan Docs
            docs_data = []
            if os.path.exists(DOCS_DIR):
                for root, dirs, files in os.walk(DOCS_DIR):
                    for file in files:
                        if file.endswith(".md"):
                            full_path = os.path.join(root, file)
                            rel = os.path.relpath(full_path, DOCS_DIR).replace("\\", "/")
                            existing_docs.add(rel)
                            try:
                                with open(full_path, "r", encoding="utf-8") as f:
                                    content = f.read()
                                title = file.replace(".md", "").replace("-", " ").title()
                                for line in content.split("\n"):
                                    if line.startswith("# "):
                                        title = line.replace("# ", "").strip()
                                        break
                                node_id = f"doc-{rel}"
                                nodes.append({
                                    "id": node_id,
                                    "label": title[:30],
                                    "type": "doc",
                                    "path": rel
                                })
                                docs_data.append((node_id, content))
                            except Exception:
                                pass
                                
            # Add links from Tasks
            for node_id, content in tasks_data:
                task_refs = re.findall(r"@task-(\d+)", content)
                for ref in task_refs:
                    ref_id = int(ref)
                    if ref_id in existing_tasks:
                        links.append({"source": node_id, "target": f"task-{ref_id}"})
                doc_refs = re.findall(r"@doc/([\w\-/]+(?:\.md)?)", content)
                for ref in doc_refs:
                    clean_ref = ref.strip()
                    if not clean_ref.endswith(".md"):
                        clean_ref += ".md"
                    if clean_ref in existing_docs:
                        links.append({"source": node_id, "target": f"doc-{clean_ref}"})
                        
            # Add links from Docs
            for node_id, content in docs_data:
                task_refs = re.findall(r"@task-(\d+)", content)
                for ref in task_refs:
                    ref_id = int(ref)
                    if ref_id in existing_tasks:
                        links.append({"source": node_id, "target": f"task-{ref_id}"})
                doc_refs = re.findall(r"@doc/([\w\-/]+(?:\.md)?)", content)
                for ref in doc_refs:
                    clean_ref = ref.strip()
                    if not clean_ref.endswith(".md"):
                        clean_ref += ".md"
                    if clean_ref in existing_docs:
                        links.append({"source": node_id, "target": f"doc-{clean_ref}"})
                        
            # Deduplicate links
            unique_links = []
            seen_links = set()
            for l in links:
                pair = (l["source"], l["target"])
                if pair not in seen_links:
                    seen_links.add(pair)
                    unique_links.append(l)
                    
            self.send_json({"nodes": nodes, "links": unique_links})
            return

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        ensure_directories()
        if not self.is_request_allowed():
            self.reject_unauthorized()
            return
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type.lower():
            self.send_json({"error": "Content-Type must be application/json"}, 415)
            return
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            payload = json.loads(body) if body else {}
        except Exception as e:
            self.send_error(400, f"Malformed JSON: {e}")
            return

        try:
            from aim.aim_cli import TIMER_STATE_PATH, TIME_LOG_PATH
        except ImportError:
            from aim_cli import TIMER_STATE_PATH, TIME_LOG_PATH

        # 1. Edit Task Status / AC / Metadata
        if self.path == "/api/tasks/edit":
            task_id = payload.get("id")
            if not task_id:
                self.send_json({"error": "Missing task ID"}, 400)
                return

            task_path = safe_task_path(task_id)
            if task_path is None:
                self.send_json({"error": "Invalid task ID"}, 400)
                return
            if not os.path.exists(task_path):
                self.send_json({"error": "Task not found"}, 404)
                return
                
            try:
                meta = parse_task_file(task_path)
                
                # Check if updating status
                if "status" in payload:
                    meta["status"] = payload["status"]
                    
                # Check if updating priority
                if "priority" in payload:
                    meta["priority"] = payload["priority"].strip().lower()
                    
                # Check if updating assignee
                if "assignee" in payload:
                    assignee = payload["assignee"].strip().lower()
                    users = load_users()
                    if assignee not in users:
                        users.append(assignee)
                        save_users(users)
                    meta["assignee"] = assignee
                    
                # New updates
                if "title" in payload:
                    meta["title"] = payload["title"].strip()
                if "description" in payload:
                    meta["description"] = payload["description"].strip()
                if "parent" in payload:
                    new_parent = int(payload["parent"]) if payload["parent"] else None
                    if detect_parent_cycle(meta["id"], new_parent):
                        self.send_json({"error": "Setting this parent would create a cycle"}, 400)
                        return
                    meta["parent"] = new_parent
                if "spec" in payload:
                    meta["spec"] = payload["spec"].strip()
                if "plan" in payload:
                    meta["plan"] = payload["plan"].strip()
                if "labels" in payload:
                    meta["labels"] = [l.strip().lower() for l in payload["labels"] if l.strip()]
                    
                # Check if checking off AC
                if "ac_index" in payload and "checked" in payload:
                    ac_idx = int(payload["ac_index"]) - 1
                    if 0 <= ac_idx < len(meta["ac"]):
                        meta["ac"][ac_idx]["checked"] = payload["checked"]
                        
                # Check if adding AC
                if "add_ac" in payload:
                    meta["ac"].append({"index": len(meta["ac"]) + 1, "checked": False, "text": payload["add_ac"].strip()})
                        
                write_task_file(meta)
                self.send_json({"success": True, "task": meta})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        # 1.5. Create Task
        elif self.path == "/api/tasks/create":
            title = payload.get("title", "").strip()
            if not title:
                self.send_json({"error": "Missing title"}, 400)
                return

            meta = {
                "id": next_task_id(),
                "title": title,
                "status": payload.get("status", "todo"),
                "priority": payload.get("priority", "medium"),
                "assignee": payload.get("assignee", "unassigned"),
                "parent": int(payload["parent"]) if payload.get("parent") else None,
                "labels": payload.get("labels", []),
                "spec": payload.get("spec", ""),
                "plan": payload.get("plan", ""),
                "description": payload.get("description", ""),
                "ac": [{"index": i + 1, "checked": False, "text": ac} for i, ac in enumerate(payload.get("ac", []))]
            }
            try:
                create_task_file(meta)
                self.send_json({"success": True, "task": meta})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        # 1.6. Delete Task
        elif self.path == "/api/tasks/delete":
            task_id = payload.get("id")
            if not task_id:
                self.send_json({"error": "Missing task ID"}, 400)
                return

            task_path = safe_task_path(task_id)
            if task_path is None:
                self.send_json({"error": "Invalid task ID"}, 400)
                return
            if not os.path.exists(task_path):
                self.send_json({"error": "Task not found"}, 404)
                return
                
            try:
                os.remove(task_path)
                # Orphan children tasks
                if os.path.exists(TASKS_DIR):
                    for filename in os.listdir(TASKS_DIR):
                        if filename.startswith("task-") and filename.endswith(".md"):
                            child_path = os.path.join(TASKS_DIR, filename)
                            try:
                                child_meta = parse_task_file(child_path)
                                if child_meta.get("parent") == int(task_id):
                                    child_meta["parent"] = None
                                    write_task_file(child_meta)
                            except Exception:
                                pass
                self.send_json({"success": True})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        # 1.7. Create Subtask
        elif self.path == "/api/tasks/create_subtask":
            parent_id = payload.get("parent_id")
            title = payload.get("title", "").strip()
            if not parent_id or not title:
                self.send_json({"error": "Missing parent ID or title"}, 400)
                return
            if safe_task_path(parent_id) is None:
                self.send_json({"error": "Invalid parent ID"}, 400)
                return

            meta = {
                "id": next_task_id(),
                "title": title,
                "status": "todo",
                "priority": "medium",
                "assignee": "unassigned",
                "parent": int(parent_id),
                "labels": [],
                "spec": "",
                "plan": "",
                "description": "",
                "ac": []
            }
            try:
                create_task_file(meta)
                self.send_json({"success": True, "task": meta})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        # 2. Add Memory
        elif self.path == "/api/memories/add":
            content = payload.get("content")
            if not content:
                self.send_json({"error": "Missing content"}, 400)
                return

            try:
                _new_mem, memories = core.add_memory(
                    content,
                    payload.get("category", "general"),
                    payload.get("layer", "project"))
                self.send_json({"success": True, "memories": memories})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        # 3. Start Timer
        elif self.path == "/api/time/start":
            task_id = payload.get("id")
            if not task_id:
                self.send_json({"error": "Missing task ID"}, 400)
                return

            task_path = safe_task_path(task_id)
            if task_path is None:
                self.send_json({"error": "Invalid task ID"}, 400)
                return
            if not os.path.exists(task_path):
                self.send_json({"error": "Task not found"}, 404)
                return

            try:
                task = parse_task_file(task_path)
                timer_state = {
                    "taskId": int(str(task_id)),
                    "title": task["title"],
                    "startedAt": time.time()
                }
                save_json(TIMER_STATE_PATH, timer_state)
                self.send_json({"success": True, "timer": timer_state})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        # 4. Stop Timer
        elif self.path == "/api/time/stop":
            if not os.path.exists(TIMER_STATE_PATH):
                self.send_json({"error": "No active timer"}, 400)
                return

            try:
                with open(TIMER_STATE_PATH, "r", encoding="utf-8") as f:
                    timer_state = json.load(f)

                task_id = timer_state["taskId"]
                duration = max(0, int(time.time() - timer_state["startedAt"]))

                # Persist results before deleting the timer state so a failure
                # cannot lose the tracked session.
                task_path = safe_task_path(task_id)
                if task_path and os.path.exists(task_path):
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
                    "note": payload.get("note", "Stopped from Web UI")
                }
                logs.append(entry)
                save_json(TIME_LOG_PATH, logs)

                if os.path.exists(TIMER_STATE_PATH):
                    os.remove(TIMER_STATE_PATH)

                self.send_json({"success": True, "duration": duration})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        # 5. Run Sync
        elif self.path == "/api/sync":
            try:
                try:
                    from aim.sync import main as run_sync
                except ImportError:
                    from sync import main as run_sync
                run_sync()
                self.send_json({"success": True})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        # 6. Run Validate
        elif self.path == "/api/validate":
            try:
                errors = len(core.validate_references())
                self.send_json({"success": True, "errors": errors, "isHealthy": errors == 0})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        # 7. Add User
        elif self.path == "/api/users/add":
            username = payload.get("username", "").strip().lower()
            if not username:
                self.send_json({"error": "Invalid username"}, 400)
                return
            users = load_users()
            if username in users:
                self.send_json({"error": "User already exists"}, 400)
                return
            users.append(username)
            save_users(users)
            self.send_json({"success": True, "users": users})

        # 8. Remove User
        elif self.path == "/api/users/remove":
            username = payload.get("username", "").strip().lower()
            if not username:
                self.send_json({"error": "Invalid username"}, 400)
                return
            if username in ["developer", "unassigned"]:
                self.send_json({"error": "Cannot remove default users"}, 400)
                return
            users = load_users()
            if username not in users:
                self.send_json({"error": "User not found"}, 404)
                return
            users.remove(username)
            save_users(users)
            self.send_json({"success": True, "users": users})

        # 8.5. Edit (Rename) User
        elif self.path == "/api/users/edit":
            old_username = payload.get("old_username", "").strip().lower()
            new_username = payload.get("new_username", "").strip().lower()
            if not old_username or not new_username:
                self.send_json({"error": "Invalid usernames"}, 400)
                return
            if old_username in ["developer", "unassigned"]:
                self.send_json({"error": "Cannot rename default users"}, 400)
                return
            users = load_users()
            if old_username not in users:
                self.send_json({"error": "User not found"}, 404)
                return
            if new_username in users:
                self.send_json({"error": "New username already exists"}, 400)
                return
            
            idx = users.index(old_username)
            users[idx] = new_username
            save_users(users)

            # Propagate changes to task files
            _updated, errors = core.rename_user_propagate(old_username, new_username)
            for err in errors:
                print(f"[-] Error propagating rename in server for {err}")

            self.send_json({"success": True, "users": users})

        # 9. Run App Builder Scaffolding API
        elif self.path == "/api/app-builder/run":
            template_name = payload.get("template_name", "").strip().lower()
            project_name = payload.get("project_name", "").strip()
            description = payload.get("description", "").strip()
            destination = payload.get("destination", "").strip()
            
            if not template_name or not project_name:
                self.send_json({"error": "Missing template_name or project_name"}, 400)
                return
                
            try:
                root_dir = get_project_root()
                if destination:
                    dest_path = os.path.normpath(os.path.join(root_dir, destination))
                else:
                    dest_path = os.path.normpath(os.path.join(root_dir, project_name))
                    
                if not _is_within(root_dir, dest_path):
                    self.send_json({"error": "Refusing to write outside workspace directory"}, 400)
                    return
                    
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                    
                base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "aim-agents", "skills", "app-builder", "templates")
                tpl_file = os.path.join(base_dir, template_name, "TEMPLATE.md")
                template_content = ""
                if os.path.exists(tpl_file):
                    with open(tpl_file, "r", encoding="utf-8") as f:
                        template_content = f.read()
                        
                task_title = f"Scaffold project: {project_name} ({template_name})"
                task_desc = f"Use template `{template_name}` to scaffold and implement project `{project_name}` at `{os.path.relpath(dest_path, root_dir)}`.\n\n### Specifications & Guidelines:\n\n{template_content}"
                
                from aim.aim_cli import next_task_id, create_task_file
                task_id = next_task_id()
                task_meta = {
                    "id": task_id,
                    "title": task_title,
                    "status": "todo",
                    "priority": "high",
                    "assignee": "unassigned",
                    "parent": None,
                    "dependsOn": [],
                    "labels": ["scaffolding", template_name],
                    "spec": "",
                    "plan": "",
                    "description": task_desc,
                    "ac": [
                        {"index": 1, "checked": False, "text": f"Scaffold folder structure at {os.path.relpath(dest_path, root_dir)}"},
                        {"index": 2, "checked": False, "text": "Configure dev server and start preview"},
                        {"index": 3, "checked": False, "text": "Implement core UI components and styling"},
                        {"index": 4, "checked": False, "text": "Run verification tests and verify build"}
                    ]
                }
                create_task_file(task_meta)
                
                readme_path = os.path.join(dest_path, "README.md")
                if not os.path.exists(readme_path):
                    with open(readme_path, "w", encoding="utf-8") as f:
                        f.write(f"# {project_name}\n\n{description}\n\nGenerated using AIM App Builder template: `{template_name}`.\n\nRefer to task `@task-{task_id}` for checklist and progress.\n")
                
                self.send_json({"success": True, "taskId": task_id, "task": task_meta})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        else:
            self.send_error(404, "Not Found")

class _ThreadingTCPServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = False


def start_server(port=6420, open_browser=True):
    configure_utf8_output()
    attempts = 10
    httpd = None

    for offset in range(attempts):
        current_port = port + offset
        try:
            server_address = ('127.0.0.1', current_port)
            httpd = _ThreadingTCPServer(server_address, AIMBrowserHandler)
            port = current_port
            break
        except OSError:
            print(f"[-] Port {current_port} is busy, trying next...")
            
    if httpd is None:
        print(f"[-] Error: Could not bind server to any port in range {port}-{port+attempts-1}")
        sys.exit(1)
        
    url = f"http://localhost:{port}"
    print("=========================================")
    print("         AIM Control Hub Dashboard       ")
    print("=========================================")
    print(f"[+] Server running at: {url}")
    print(f"[+] Project workspace: {get_project_root()}")
    print("[*] Press Ctrl+C to terminate the server.\n")

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"[-] Failed to open default browser: {e}")
            
    try:
        httpd.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print("\n[*] Shutting down AIM Web UI server...")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    start_server()
