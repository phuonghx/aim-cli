"""Zero-dependency MCP (Model Context Protocol) server for AIM.

Serves the workspace (tasks, docs, memories) over the MCP stdio transport
so AI assistants (Claude Code, Cursor, Windsurf, ...) can query and mutate
project context directly instead of reading static files.

Implementation notes:
- Pure stdlib: JSON-RPC 2.0 messages, newline-delimited, over stdin/stdout
  (per the MCP stdio transport spec). No external packages required.
- All logging goes to stderr; stdout carries protocol messages only.

Register in Claude Code:   claude mcp add aim -- aim mcp
Register in Cursor (.cursor/mcp.json):
  {"mcpServers": {"aim": {"command": "aim", "args": ["mcp"]}}}
"""
import json
import sys

try:
    from aim import core, __version__
except ImportError:
    import core
    __version__ = "unknown"


def _cli():
    try:
        from aim import aim_cli
    except ImportError:
        import aim_cli
    return aim_cli


PROTOCOL_VERSION = "2024-11-05"

TOOLS = [
    {
        "name": "list_tasks",
        "description": "List every task in the AIM workspace (id, title, status, priority, assignee, parent, labels, description, acceptance criteria).",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "get_task",
        "description": "Get the full details of one task by its numeric ID.",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "integer", "description": "Task ID"}},
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "create_task",
        "description": "Create a new task in the AIM workspace. Returns the created task including its allocated ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                "assignee": {"type": "string"},
                "parent": {"type": "integer", "description": "Parent task ID (subtask)"},
                "dependsOn": {"type": "array", "items": {"type": "integer"}, "description": "Prerequisite task IDs"},
                "labels": {"type": "array", "items": {"type": "string"}},
                "ac": {"type": "array", "items": {"type": "string"}, "description": "Acceptance criteria items"},
            },
            "required": ["title"],
            "additionalProperties": False,
        },
    },
    {
        "name": "create_tasks",
        "description": "Batch-create tasks (e.g. from a decomposed PRD). Each item: {title, description?, priority?, ac?, labels?, key?, dependsOn?}. dependsOn entries may be existing task IDs (int) or a `key` of an earlier task in the same batch (string), so dependency chains can be created in one call.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                            "ac": {"type": "array", "items": {"type": "string"}},
                            "labels": {"type": "array", "items": {"type": "string"}},
                            "key": {"type": "string", "description": "Local handle for within-batch dependsOn references"},
                            "dependsOn": {"type": "array", "description": "Existing task IDs (int) or batch keys (str)"},
                        },
                        "required": ["title"],
                    },
                },
            },
            "required": ["tasks"],
            "additionalProperties": False,
        },
    },
    {
        "name": "next_task",
        "description": "Return the next actionable task: highest priority (then lowest id) among not-done, not-blocked tasks whose dependencies are all done. Call this to decide what to work on next.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "search",
        "description": "Search tasks, docs, and memories for a keyword. Returns typed results with snippets.",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_memory_context",
        "description": "Recall the most relevant project memories for the current work as a compact markdown block to inject as working memory. Ranked by relevance, importance and recency. Call this at the start of a task before making changes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What you're working on (optional; omit to get the highest-priority memories overall)"},
                "limit": {"type": "integer", "description": "Max memories to include (default 8)"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "add_memory",
        "description": "Persist a reusable decision, pattern, or rule into the AIM memory store so it can be recalled in future sessions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "category": {"type": "string", "description": "e.g. decision, syntax, pattern"},
                "layer": {"type": "string", "enum": ["project", "global"]},
                "importance": {"type": "integer", "minimum": 1, "maximum": 10, "description": "1-10; biases recall ranking (default 5)"},
            },
            "required": ["content"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_memories",
        "description": "List every persistent memory entry (id, content, category, layer, author, createdAt, reviewedAt, refs).",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "record_correction",
        "description": "Capture a mid-session correction so the lesson survives across sessions and tools. Call this whenever the user corrects your approach.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "what_was_wrong": {"type": "string", "description": "The mistaken approach"},
                "correct_approach": {"type": "string", "description": "What to do instead"},
                "refs": {"type": "array", "items": {"type": "string"}, "description": "Related file paths"},
            },
            "required": ["what_was_wrong", "correct_approach"],
            "additionalProperties": False,
        },
    },
    {
        "name": "review_memory",
        "description": "Mark a memory as freshly verified (resets its staleness clock).",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "doctor",
        "description": "Diagnose context drift: stale memories (vs git history), broken references, duplicate task IDs, spec drift. Returns findings with severity.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]


DECOMPOSE_PRD_INSTRUCTION = (
    "Decompose the following PRD into a set of small, independently verifiable "
    "AIM tasks. For each task provide: title, a short description, acceptance "
    "criteria (ac), a priority, and dependsOn (prerequisite tasks). Give each "
    "task a short `key` and reference those keys in later tasks' dependsOn so "
    "the dependency chain is explicit. Then call the `create_tasks` tool with "
    "the full list in dependency order."
)

PROMPTS = [
    {
        "name": "decompose_prd",
        "description": "Break a PRD / feature description into AIM tasks with dependencies, then create them via create_tasks.",
        "arguments": [
            {"name": "prd", "description": "The PRD or feature description text", "required": True},
        ],
    },
]


def _get_prompt(name, arguments):
    if name != "decompose_prd":
        raise ValueError(f"Unknown prompt: {name}")
    prd = (arguments or {}).get("prd", "")
    text = f"{DECOMPOSE_PRD_INSTRUCTION}\n\nPRD:\n{prd}"
    return {
        "description": "Decompose a PRD into AIM tasks",
        "messages": [{"role": "user", "content": {"type": "text", "text": text}}],
    }


def _call_tool(name, arguments):
    """Execute a tool. Returns a JSON-serializable result, or raises ValueError."""
    if name == "list_tasks":
        tasks, errors = core.load_tasks()
        return {"tasks": tasks, "parseErrors": errors}

    if name == "get_task":
        task = core.get_task(arguments.get("id"))
        if task is None:
            raise ValueError(f"Task {arguments.get('id')} not found.")
        return task

    if name == "create_task":
        title = (arguments.get("title") or "").strip()
        if not title:
            raise ValueError("title is required.")
        return core.create_task(
            title,
            description=arguments.get("description", ""),
            priority=arguments.get("priority", "medium"),
            assignee=(arguments.get("assignee") or "unassigned").strip().lower(),
            parent=arguments.get("parent"),
            labels=arguments.get("labels"),
            ac=arguments.get("ac"),
            depends_on=arguments.get("dependsOn"),
        )

    if name == "create_tasks":
        specs = arguments.get("tasks") or []
        if not specs:
            raise ValueError("tasks (a non-empty list) is required.")
        return {"created": core.create_tasks(specs)}

    if name == "next_task":
        t = core.next_task()
        return t if t is not None else {"message": "No actionable task."}

    if name == "search":
        query = (arguments.get("query") or "").strip()
        if not query:
            raise ValueError("query is required.")
        return {"results": core.search_workspace(query)}

    if name == "add_memory":
        content = (arguments.get("content") or "").strip()
        if not content:
            raise ValueError("content is required.")
        new_mem, _memories = core.add_memory(
            content, arguments.get("category"), arguments.get("layer"),
            importance=arguments.get("importance"))
        return new_mem

    if name == "get_memory_context":
        return {"context": core.get_memory_context(
            query=(arguments.get("query") or None),
            limit=arguments.get("limit") or 8)}

    if name == "list_memories":
        return {"memories": core.load_memories()}

    if name == "record_correction":
        wrong = (arguments.get("what_was_wrong") or "").strip()
        right = (arguments.get("correct_approach") or "").strip()
        if not wrong or not right:
            raise ValueError("what_was_wrong and correct_approach are required.")
        new_mem, _memories = core.record_correction(wrong, right, arguments.get("refs"))
        return new_mem

    if name == "review_memory":
        reviewed = core.review_memory(arguments.get("id"))
        if reviewed is None:
            raise ValueError(f"Memory {arguments.get('id')} not found.")
        return reviewed

    if name == "doctor":
        return {"findings": core.run_diagnostics()}

    raise ValueError(f"Unknown tool: {name}")


def _result(msg_id, result):
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id, code, message):
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def handle_message(msg):
    """Handle one JSON-RPC message. Returns the response dict, or None for
    notifications (which must not be answered)."""
    method = msg.get("method", "")
    msg_id = msg.get("id")
    params = msg.get("params") or {}
    is_notification = "id" not in msg

    if method == "initialize":
        client_version = params.get("protocolVersion") or PROTOCOL_VERSION
        return _result(msg_id, {
            "protocolVersion": client_version,
            "capabilities": {"tools": {}, "prompts": {}},
            "serverInfo": {"name": "aim-cli", "version": __version__},
        })

    if method.startswith("notifications/"):
        return None

    if method == "ping":
        return _result(msg_id, {})

    if method == "tools/list":
        return _result(msg_id, {"tools": TOOLS})

    if method == "prompts/list":
        return _result(msg_id, {"prompts": PROMPTS})

    if method == "prompts/get":
        try:
            return _result(msg_id, _get_prompt(params.get("name", ""), params.get("arguments")))
        except ValueError as e:
            return _error(msg_id, -32602, str(e))

    if method == "tools/call":
        name = params.get("name", "")
        arguments = params.get("arguments") or {}
        try:
            result = _call_tool(name, arguments)
            return _result(msg_id, {
                "content": [{"type": "text",
                             "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                "isError": False,
            })
        except ValueError as e:
            return _result(msg_id, {
                "content": [{"type": "text", "text": f"Error: {e}"}],
                "isError": True,
            })
        except Exception as e:
            return _result(msg_id, {
                "content": [{"type": "text", "text": f"Error: {type(e).__name__}: {e}"}],
                "isError": True,
            })

    if is_notification:
        return None
    return _error(msg_id, -32601, f"Method not found: {method}")


def run_stdio_server():
    """Blocking loop: read newline-delimited JSON-RPC from stdin, write
    responses to stdout. stderr is used for human-facing logs."""
    cli = _cli()
    cli.configure_utf8_output()
    cli.ensure_directories()
    print(f"[*] AIM MCP server (stdio) ready - workspace: {cli.ROOT_DIR}", file=sys.stderr)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            response = _error(None, -32700, f"Parse error: {e}")
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
            continue

        response = handle_message(msg)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
