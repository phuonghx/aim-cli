import json

from aim import aim_cli, core, mcp_server


# ---------- dependsOn round-trip ----------

def test_dependson_roundtrip(workspace):
    core.create_task("a")                                  # id 1
    core.create_task("b")                                  # id 2
    t = core.create_task("c", depends_on=[1, 2])           # id 3
    assert t["dependsOn"] == [1, 2]
    reread = core.get_task(3)
    assert reread["dependsOn"] == [1, 2]
    # the metadata line is present in the file
    with open(f"{aim_cli.TASKS_DIR}/task-3.md", encoding="utf-8") as f:
        assert "**Depends On:** 1, 2" in f.read()


def test_dependency_cycle_detection(workspace):
    core.create_task("a")                                  # 1
    core.create_task("b", depends_on=[1])                  # 2 depends on 1
    assert aim_cli.detect_dependency_cycle(1, [2]) is True   # 1->2->1 loop
    assert aim_cli.detect_dependency_cycle(1, [1]) is True   # self
    assert aim_cli.detect_dependency_cycle(2, [1]) is False  # already so, no loop
    core.create_task("c")                                  # 3
    assert aim_cli.detect_dependency_cycle(3, [1]) is False


# ---------- next_task ----------

def test_next_task_respects_dependencies_and_priority(workspace):
    core.create_task("low prio ready", priority="low")            # 1, ready
    core.create_task("dep", priority="medium")                   # 2 (dep, todo)
    core.create_task("urgent waiting", priority="urgent", depends_on=[2])  # 3 waiting on 2

    # Nothing done yet: candidates = t1 (low, ready), t2 (medium, ready); t3 waits on t2.
    nxt = core.next_task()
    assert nxt["id"] == 2  # medium > low, both ready

    # finish t2 -> t3 becomes actionable and is urgent
    _set_status(2, "done")
    nxt = core.next_task()
    assert nxt["id"] == 3  # now unblocked + urgent


def _set_status(task_id, status):
    full = core.get_task(task_id)
    full["status"] = status
    aim_cli.write_task_file(full)


def test_next_task_skips_blocked_and_done(workspace):
    a = core.create_task("done one")
    _set_status(a["id"], "done")
    b = core.create_task("blocked one")
    _set_status(b["id"], "blocked")
    assert core.next_task() is None


# ---------- batch create with within-batch keys ----------

def test_create_tasks_resolves_batch_keys(workspace):
    created = core.create_tasks([
        {"title": "schema", "key": "db", "priority": "high"},
        {"title": "api", "key": "api", "dependsOn": ["db"]},
        {"title": "ui", "dependsOn": ["api", "db"]},
    ])
    assert [c["id"] for c in created] == [1, 2, 3]
    assert core.get_task(2)["dependsOn"] == [1]          # api -> schema
    assert core.get_task(3)["dependsOn"] == [2, 1]       # ui -> api, schema


def test_create_tasks_accepts_existing_int_ids(workspace):
    core.create_task("existing")                          # 1
    created = core.create_tasks([{"title": "new", "dependsOn": [1]}])
    assert created[0]["dependsOn"] == [1]


# ---------- MCP surface ----------

def test_mcp_next_task_and_prompts(workspace):
    core.create_task("only task")
    resp = mcp_server.handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                      "params": {"name": "next_task", "arguments": {}}})
    payload = json.loads(resp["result"]["content"][0]["text"])
    assert payload["id"] == 1

    # initialize advertises prompts capability
    init = mcp_server.handle_message({"jsonrpc": "2.0", "id": 2, "method": "initialize",
                                      "params": {"protocolVersion": "2024-11-05", "capabilities": {}}})
    assert "prompts" in init["result"]["capabilities"]

    # prompts/list + prompts/get
    listed = mcp_server.handle_message({"jsonrpc": "2.0", "id": 3, "method": "prompts/list"})
    assert any(p["name"] == "decompose_prd" for p in listed["result"]["prompts"])
    got = mcp_server.handle_message({"jsonrpc": "2.0", "id": 4, "method": "prompts/get",
                                     "params": {"name": "decompose_prd", "arguments": {"prd": "Build login"}}})
    text = got["result"]["messages"][0]["content"]["text"]
    assert "Build login" in text
    assert "create_tasks" in text


def test_mcp_create_tasks(workspace):
    resp = mcp_server.handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                      "params": {"name": "create_tasks", "arguments": {
                                          "tasks": [{"title": "x", "key": "x"},
                                                    {"title": "y", "dependsOn": ["x"]}]}}})
    created = json.loads(resp["result"]["content"][0]["text"])["created"]
    assert created[1]["dependsOn"] == [created[0]["id"]]
