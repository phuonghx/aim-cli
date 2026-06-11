import json

from aim import mcp_server


def rpc(method, params=None, msg_id=1):
    msg = {"jsonrpc": "2.0", "method": method, "id": msg_id}
    if params is not None:
        msg["params"] = params
    return mcp_server.handle_message(msg)


def call_tool(name, arguments=None):
    resp = rpc("tools/call", {"name": name, "arguments": arguments or {}})
    assert resp["id"] == 1
    result = resp["result"]
    payload = result["content"][0]["text"]
    return result["isError"], payload


def test_initialize_handshake():
    resp = rpc("initialize", {"protocolVersion": "2024-11-05",
                              "capabilities": {}, "clientInfo": {"name": "test"}})
    result = resp["result"]
    assert result["protocolVersion"] == "2024-11-05"
    assert "tools" in result["capabilities"]
    assert result["serverInfo"]["name"] == "aim-cli"


def test_initialized_notification_gets_no_response():
    assert mcp_server.handle_message(
        {"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_unknown_method_errors():
    resp = rpc("resources/list")
    assert resp["error"]["code"] == -32601


def test_tools_list_shapes():
    resp = rpc("tools/list")
    tools = resp["result"]["tools"]
    names = {t["name"] for t in tools}
    assert names == {"list_tasks", "get_task", "create_task", "create_tasks",
                     "next_task", "search", "add_memory", "list_memories",
                     "record_correction", "review_memory", "doctor"}
    for t in tools:
        assert "description" in t
        assert t["inputSchema"]["type"] == "object"


def test_tool_roundtrip_create_get_search(workspace):
    is_err, payload = call_tool("create_task", {
        "title": "Nhiệm vụ MCP", "description": "tạo từ MCP server",
        "priority": "high", "ac": ["AC một", "AC hai"]})
    assert not is_err
    task = json.loads(payload)
    assert task["id"] == 1
    assert task["priority"] == "high"

    is_err, payload = call_tool("get_task", {"id": 1})
    assert not is_err
    assert json.loads(payload)["title"] == "Nhiệm vụ MCP"
    assert len(json.loads(payload)["ac"]) == 2

    is_err, payload = call_tool("list_tasks")
    assert not is_err
    assert len(json.loads(payload)["tasks"]) == 1

    is_err, payload = call_tool("search", {"query": "mcp"})
    assert not is_err
    results = json.loads(payload)["results"]
    assert any(r["type"] == "task" and r["id"] == 1 for r in results)


def test_tool_memory_roundtrip(workspace):
    is_err, payload = call_tool("add_memory", {
        "content": "Dùng repository pattern", "category": "decision"})
    assert not is_err
    mem = json.loads(payload)
    assert mem["id"] == 1
    assert mem["category"] == "decision"

    is_err, payload = call_tool("list_memories")
    assert not is_err
    assert len(json.loads(payload)["memories"]) == 1


def test_tool_errors_are_soft(workspace):
    is_err, payload = call_tool("get_task", {"id": 999})
    assert is_err
    assert "not found" in payload

    is_err, payload = call_tool("create_task", {"title": "   "})
    assert is_err

    is_err, payload = call_tool("nonexistent_tool")
    assert is_err
    assert "Unknown tool" in payload
