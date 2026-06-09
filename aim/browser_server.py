import os
import json
import http.server
import socketserver
import webbrowser
import urllib.parse
import sys

# Import helpers
try:
    from aim.aim_cli import parse_task_file, write_task_file, ensure_directories, get_project_root
    from aim.aim_cli import TASKS_DIR, DOCS_DIR, MEMORIES_PATH
except ImportError:
    from aim_cli import parse_task_file, write_task_file, ensure_directories, get_project_root
    from aim_cli import TASKS_DIR, DOCS_DIR, MEMORIES_PATH

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIM Control Panel 🎯</title>
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;600&display=swap" rel="stylesheet">
    <!-- Marked for Markdown rendering -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg: #090a0f;
            --surface: #121420;
            --surface-hover: #1b1e30;
            --border: rgba(255, 255, 255, 0.08);
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.15);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text: #f3f4f6;
            --text-muted: #9ca3af;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.5;
            overflow-x: hidden;
        }

        header {
            background: linear-gradient(135deg, #181b2d 0%, #090a0f 100%);
            border-bottom: 1px solid var(--border);
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo-area {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-area h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.8rem;
            font-weight: 800;
            background: linear-gradient(to right, #818cf8, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .badge {
            background-color: var(--primary-glow);
            border: 1px solid var(--primary);
            color: #a5b4fc;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .project-path {
            font-size: 0.875rem;
            color: var(--text-muted);
            font-family: monospace;
            background-color: rgba(255, 255, 255, 0.03);
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            border: 1px solid var(--border);
        }

        .tabs {
            display: flex;
            gap: 1rem;
            padding: 1rem 2rem;
            background-color: rgba(255, 255, 255, 0.01);
            border-bottom: 1px solid var(--border);
        }

        .tab-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            font-family: inherit;
            font-size: 1rem;
            font-weight: 600;
            padding: 0.5rem 1rem;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .tab-btn:hover {
            color: var(--text);
            background-color: rgba(255, 255, 255, 0.03);
        }

        .tab-btn.active {
            color: var(--text);
            background-color: var(--primary);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }

        main {
            padding: 2rem;
            max-width: 1600px;
            margin: 0 auto;
            min-height: calc(100vh - 180px);
        }

        .tab-content {
            display: none;
            animation: fadeIn 0.3s ease-in-out;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* 📋 KANBAN BOARD */
        .kanban-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            align-items: start;
        }

        .kanban-col {
            background-color: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--border);
            padding: 1.25rem;
            min-height: 500px;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .col-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.75rem;
            margin-bottom: 0.5rem;
        }

        .col-title {
            font-weight: 600;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .col-count {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }

        .task-card {
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }

        .task-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background-color: var(--primary);
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        .task-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.15);
            background-color: var(--surface-hover);
        }

        .task-card:hover::before {
            opacity: 1;
        }

        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 0.5rem;
        }

        .task-id {
            font-family: monospace;
            font-size: 0.8rem;
            color: var(--primary);
            font-weight: bold;
        }

        .task-priority {
            font-size: 0.7rem;
            text-transform: uppercase;
            font-weight: 800;
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
        }

        .pri-high { background-color: rgba(239, 68, 68, 0.1); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.2); }
        .pri-medium { background-color: rgba(245, 158, 11, 0.1); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.2); }
        .pri-low { background-color: rgba(16, 185, 129, 0.1); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.2); }

        .task-title {
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 0.75rem;
        }

        .task-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        .task-progress {
            background-color: rgba(255, 255, 255, 0.05);
            height: 4px;
            width: 60px;
            border-radius: 99px;
            overflow: hidden;
        }

        .task-progress-bar {
            height: 100%;
            background-color: var(--success);
        }

        /* 📚 DOCUMENT LIBRARY */
        .doc-layout {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 2rem;
            background-color: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--border);
            min-height: 600px;
        }

        .doc-sidebar {
            border-right: 1px solid var(--border);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .doc-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            overflow-y: auto;
            max-height: 500px;
        }

        .doc-item {
            padding: 0.75rem 1rem;
            background-color: rgba(255, 255, 255, 0.01);
            border: 1px solid var(--border);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.9rem;
            font-weight: 600;
        }

        .doc-item:hover, .doc-item.active {
            background-color: var(--primary-glow);
            border-color: var(--primary);
            color: #a5b4fc;
        }

        .doc-content {
            padding: 2.5rem;
            overflow-y: auto;
            max-height: 600px;
        }

        /* Markdown styling inside doc viewer */
        .markdown-body h1 { font-size: 2rem; margin-bottom: 1rem; font-family: 'Space Grotesk', sans-serif; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
        .markdown-body h2 { font-size: 1.5rem; margin-top: 1.5rem; margin-bottom: 0.75rem; border-bottom: 1px solid var(--border); padding-bottom: 0.25rem; }
        .markdown-body h3 { font-size: 1.2rem; margin-top: 1.25rem; margin-bottom: 0.5rem; }
        .markdown-body p { margin-bottom: 1rem; color: #d1d5db; }
        .markdown-body ul, .markdown-body ol { margin-bottom: 1rem; padding-left: 1.5rem; }
        .markdown-body li { margin-bottom: 0.25rem; }
        .markdown-body pre { background-color: rgba(0,0,0,0.3); padding: 1rem; border-radius: 6px; border: 1px solid var(--border); overflow-x: auto; margin-bottom: 1rem; font-family: monospace; }
        .markdown-body code { font-family: monospace; background-color: rgba(255,255,255,0.06); padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.9em; }
        .markdown-body blockquote { border-left: 4px solid var(--primary); padding-left: 1rem; margin-bottom: 1rem; font-style: italic; color: var(--text-muted); }

        /* 🧠 MEMORY GRID */
        .memory-layout {
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 2rem;
            align-items: start;
        }

        .memory-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.25rem;
        }

        .memory-card {
            background-color: var(--surface);
            border-radius: 10px;
            border: 1px solid var(--border);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            transition: border-color 0.2s ease;
        }

        .memory-card:hover {
            border-color: var(--primary);
        }

        .mem-header {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            font-weight: bold;
        }

        .mem-cat {
            color: var(--warning);
            text-transform: uppercase;
        }

        .mem-layer {
            background-color: rgba(255,255,255,0.05);
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            color: var(--text-muted);
        }

        .mem-content {
            font-size: 0.9rem;
            color: #d1d5db;
            word-break: break-word;
        }

        /* FORMS & INPUTS */
        .form-panel {
            background-color: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--border);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .form-title {
            font-weight: 600;
            font-size: 1.1rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }

        .form-group label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
        }

        .form-control {
            background-color: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.6rem 0.8rem;
            color: var(--text);
            font-family: inherit;
            font-size: 0.9rem;
            transition: border-color 0.2s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary);
        }

        .btn {
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.65rem 1.2rem;
            font-weight: 600;
            font-family: inherit;
            cursor: pointer;
            transition: opacity 0.2s ease;
        }

        .btn:hover {
            opacity: 0.9;
        }

        /* MODAL */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(4px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .modal {
            background-color: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--border);
            width: 90%;
            max-width: 700px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            animation: modalSlide 0.25s ease-out;
        }

        @keyframes modalSlide {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .modal-header {
            padding: 1.5rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: start;
        }

        .modal-close {
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 1.5rem;
            cursor: pointer;
        }

        .modal-close:hover {
            color: var(--text);
        }

        .modal-body {
            padding: 1.5rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .ac-list {
            display: flex;
            flex-direction: column;
            gap: 0.50rem;
            margin-top: 0.5rem;
        }

        .ac-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            background-color: rgba(255,255,255,0.01);
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            border: 1px solid var(--border);
            cursor: pointer;
        }

        .ac-item input[type="checkbox"] {
            width: 1.1rem;
            height: 1.1rem;
            accent-color: var(--success);
            cursor: pointer;
        }

        .ac-text.checked {
            text-decoration: line-through;
            color: var(--text-muted);
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <h1>AIM Mind Control Panel</h1>
            <span class="badge">v0.1.1</span>
        </div>
        <div class="project-path" id="projectRootDisplay">Loading project root...</div>
    </header>

    <nav class="tabs">
        <button class="tab-btn active" onclick="switchTab('tasks')">📋 Task Board</button>
        <button class="tab-btn" onclick="switchTab('docs')">📚 Document Library</button>
        <button class="tab-btn" onclick="switchTab('memory')">🧠 Memory Storage</button>
    </nav>

    <main>
        <!-- 📋 KANBAN CONTENT -->
        <div id="tasksContent" class="tab-content active">
            <div class="kanban-grid">
                <div class="kanban-col" id="col-todo">
                    <div class="col-header">
                        <span class="col-title">Todo 📝</span>
                        <span class="col-count" id="count-todo">0</span>
                    </div>
                </div>
                <div class="kanban-col" id="col-in-progress">
                    <div class="col-header">
                        <span class="col-title">In Progress ⚙️</span>
                        <span class="col-count" id="count-in-progress">0</span>
                    </div>
                </div>
                <div class="kanban-col" id="col-in-review">
                    <div class="col-header">
                        <span class="col-title">In Review 🔍</span>
                        <span class="col-count" id="count-in-review">0</span>
                    </div>
                </div>
                <div class="kanban-col" id="col-done">
                    <div class="col-header">
                        <span class="col-title">Done ✅</span>
                        <span class="col-count" id="count-done">0</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 📚 DOCS CONTENT -->
        <div id="docsContent" class="tab-content">
            <div class="doc-layout">
                <div class="doc-sidebar">
                    <h2 style="font-size:1.1rem; font-weight:600; margin-bottom:0.5rem;">Documents</h2>
                    <div class="doc-list" id="docListContainer">
                        <!-- Filled by JS -->
                    </div>
                </div>
                <div class="doc-content markdown-body" id="docViewerContainer">
                    Select a document from the sidebar to preview.
                </div>
            </div>
        </div>

        <!-- 🧠 MEMORY CONTENT -->
        <div id="memoryContent" class="tab-content">
            <div class="memory-layout">
                <div class="memory-grid" id="memoryGridContainer">
                    <!-- Filled by JS -->
                </div>
                <div class="form-panel">
                    <h3 class="form-title">Record Decision / Pattern</h3>
                    <div class="form-group">
                        <label for="memContentInput">Memory Statement</label>
                        <textarea id="memContentInput" class="form-control" rows="4" placeholder="e.g. We use Repository pattern for Database access."></textarea>
                    </div>
                    <div class="form-group">
                        <label for="memCatInput">Category</label>
                        <select id="memCatInput" class="form-control">
                            <option value="decision">Decision ⚖️</option>
                            <option value="pattern">Pattern 🧩</option>
                            <option value="syntax">Syntax 📋</option>
                            <option value="general">General 🏷️</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="memLayerInput">Storage Layer</label>
                        <select id="memLayerInput" class="form-control">
                            <option value="project">Project Root 📁</option>
                            <option value="global">Global Settings 🌍</option>
                        </select>
                    </div>
                    <button class="btn" onclick="saveMemory()">Save Memory</button>
                </div>
            </div>
        </div>
    </main>

    <!-- TASK DETAILS MODAL -->
    <div class="modal-overlay" id="taskModalOverlay" onclick="closeTaskModal(event)">
        <div class="modal" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div>
                    <span class="task-id" id="modalTaskId">TASK-1</span>
                    <h2 id="modalTaskTitle" style="font-size: 1.4rem; font-weight: 600; margin-top: 0.25rem;">Task Title</h2>
                </div>
                <button class="modal-close" onclick="closeTaskModal(null)">&times;</button>
            </div>
            <div class="modal-body">
                <div>
                    <h3 style="font-size: 0.9rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase;">Description</h3>
                    <p id="modalTaskDesc" style="margin-top: 0.35rem; font-size: 0.95rem;"></p>
                </div>
                <div>
                    <h3 style="font-size: 0.9rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase;">Status</h3>
                    <select id="modalTaskStatusSelect" class="form-control" style="margin-top: 0.35rem; width: 200px;" onchange="updateTaskStatus()">
                        <option value="todo">Todo</option>
                        <option value="in-progress">In Progress</option>
                        <option value="in-review">In Review</option>
                        <option value="done">Done</option>
                    </select>
                </div>
                <div>
                    <h3 style="font-size: 0.9rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase;">Acceptance Criteria</h3>
                    <div class="ac-list" id="modalTaskAcContainer">
                        <!-- Filled by JS -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentTasks = [];
        let currentDocs = [];
        let currentMemories = [];
        let activeTaskId = null;

        function switchTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName + 'Content').classList.add('active');
            
            if (tabName === 'tasks') fetchTasks();
            if (tabName === 'docs') fetchDocs();
            if (tabName === 'memory') fetchMemories();
        }

        // --- FETCHERS ---
        async function fetchProjectRoot() {
            try {
                let res = await fetch('/api/root');
                let data = await res.json();
                document.getElementById('projectRootDisplay').textContent = data.root;
            } catch (err) {
                console.error(err);
            }
        }

        async function fetchTasks() {
            try {
                let res = await fetch('/api/tasks');
                currentTasks = await res.json();
                renderKanban();
            } catch (err) {
                console.error(err);
            }
        }

        async function fetchDocs() {
            try {
                let res = await fetch('/api/docs');
                currentDocs = await res.json();
                renderDocsList();
            } catch (err) {
                console.error(err);
            }
        }

        async function fetchMemories() {
            try {
                let res = await fetch('/api/memories');
                currentMemories = await res.json();
                renderMemories();
            } catch (err) {
                console.error(err);
            }
        }

        // --- RENDERERS ---
        function renderKanban() {
            // Clear columns
            const cols = ['todo', 'in-progress', 'in-review', 'done'];
            cols.forEach(col => {
                const container = document.getElementById('col-' + col);
                container.querySelectorAll('.task-card').forEach(card => card.remove());
                document.getElementById('count-' + col).textContent = '0';
            });

            const counts = {todo: 0, 'in-progress': 0, 'in-review': 0, done: 0};

            currentTasks.forEach(task => {
                let status = task.status.toLowerCase();
                if (!cols.includes(status)) status = 'todo'; // fallback
                
                counts[status]++;
                
                const card = document.createElement('div');
                card.className = 'task-card';
                card.onclick = () => openTaskModal(task.id);
                
                // Calculate progress
                const checkedCount = task.ac.filter(item => item.checked).length;
                const progressPct = task.ac.length ? Math.round((checkedCount / task.ac.length) * 100) : 0;
                
                card.innerHTML = `
                    <div class="task-header">
                        <span class="task-id">TASK-${task.id}</span>
                        <span class="task-priority pri-${task.priority.toLowerCase()}">${task.priority}</span>
                    </div>
                    <div class="task-title">${task.title}</div>
                    <div class="task-meta">
                        <span>👤 ${task.assignee}</span>
                        <div class="task-progress">
                            <div class="task-progress-bar" style="width: ${progressPct}%"></div>
                        </div>
                    </div>
                `;
                document.getElementById('col-' + status).appendChild(card);
            });

            cols.forEach(col => {
                document.getElementById('count-' + col).textContent = counts[col];
            });
        }

        function renderDocsList() {
            const container = document.getElementById('docListContainer');
            container.innerHTML = '';
            
            if (currentDocs.length === 0) {
                container.innerHTML = '<div style="color:var(--text-muted);font-size:0.875rem;">No documents found.</div>';
                return;
            }

            currentDocs.forEach((doc, idx) => {
                const item = document.createElement('div');
                item.className = 'doc-item';
                item.textContent = doc.title || doc.path;
                item.onclick = () => selectDoc(idx, item);
                container.appendChild(item);
            });
        }

        function selectDoc(index, element) {
            document.querySelectorAll('.doc-item').forEach(el => el.classList.remove('active'));
            element.classList.add('active');
            
            const doc = currentDocs[index];
            const viewer = document.getElementById('docViewerContainer');
            viewer.innerHTML = marked.parse(doc.content);
        }

        function renderMemories() {
            const container = document.getElementById('memoryGridContainer');
            container.innerHTML = '';

            if (currentMemories.length === 0) {
                container.innerHTML = '<div style="color:var(--text-muted)">No memories recorded yet. Add one on the right!</div>';
                return;
            }

            currentMemories.forEach(mem => {
                const card = document.createElement('div');
                card.className = 'memory-card';
                card.innerHTML = `
                    <div class="mem-header">
                        <span class="mem-cat">${mem.category}</span>
                        <span class="mem-layer">${mem.layer}</span>
                    </div>
                    <div class="mem-content">${mem.content}</div>
                `;
                container.appendChild(card);
            });
        }

        // --- TASK MODAL & ACTIONS ---
        function openTaskModal(taskId) {
            const task = currentTasks.find(t => t.id === taskId);
            if (!task) return;
            
            activeTaskId = taskId;
            document.getElementById('modalTaskId').textContent = `TASK-${task.id}`;
            document.getElementById('modalTaskTitle').textContent = task.title;
            document.getElementById('modalTaskDesc').textContent = task.description || 'No description provided.';
            document.getElementById('modalTaskStatusSelect').value = task.status;
            
            const acContainer = document.getElementById('modalTaskAcContainer');
            acContainer.innerHTML = '';
            
            if (task.ac.length === 0) {
                acContainer.innerHTML = '<div style="color:var(--text-muted)">No acceptance criteria configured.</div>';
            } else {
                task.ac.forEach(item => {
                    const acDiv = document.createElement('div');
                    acDiv.className = 'ac-item';
                    acDiv.onclick = () => toggleTaskAc(item.index);
                    acDiv.innerHTML = `
                        <input type="checkbox" ${item.checked ? 'checked' : ''} onclick="event.stopPropagation(); toggleTaskAc(${item.index})">
                        <span class="ac-text ${item.checked ? 'checked' : ''}">${item.text}</span>
                    `;
                    acContainer.appendChild(acDiv);
                });
            }
            
            document.getElementById('taskModalOverlay').style.display = 'flex';
        }

        function closeTaskModal(e) {
            if (e === null || e.target === document.getElementById('taskModalOverlay')) {
                document.getElementById('taskModalOverlay').style.display = 'none';
                activeTaskId = null;
            }
        }

        async function updateTaskStatus() {
            const newStatus = document.getElementById('modalTaskStatusSelect').value;
            try {
                let res = await fetch('/api/tasks/edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: activeTaskId,
                        status: newStatus
                    })
                });
                if (res.ok) {
                    await fetchTasks();
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function toggleTaskAc(acIndex) {
            const task = currentTasks.find(t => t.id === activeTaskId);
            if (!task) return;
            
            const acItem = task.ac.find(item => item.index === acIndex);
            if (!acItem) return;

            try {
                let res = await fetch('/api/tasks/edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: activeTaskId,
                        ac_index: acIndex,
                        checked: !acItem.checked
                    })
                });
                if (res.ok) {
                    await fetchTasks();
                    // Refresh modal UI
                    openTaskModal(activeTaskId);
                }
            } catch (err) {
                console.error(err);
            }
        }

        // --- MEMORY ACTIONS ---
        async function saveMemory() {
            const content = document.getElementById('memContentInput').value.trim();
            const category = document.getElementById('memCatInput').value;
            const layer = document.getElementById('memLayerInput').value;
            
            if (!content) {
                alert('Please enter a memory statement!');
                return;
            }

            try {
                let res = await fetch('/api/memories/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content, category, layer })
                });
                if (res.ok) {
                    document.getElementById('memContentInput').value = '';
                    await fetchMemories();
                }
            } catch (err) {
                console.error(err);
            }
        }

        // --- INIT ---
        window.onload = () => {
            fetchProjectRoot();
            fetchTasks();
        };
    </script>
</body>
</html>
"""

class AIMBrowserHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress stdout logs to keep terminal output clean
        pass

    def send_json(self, data, status=200):
        try:
            content = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error writing response: {e}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        ensure_directories()
        
        # 1. Serves SPA Frontend
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
            return
            
        # 2. API Root
        elif self.path == "/api/root":
            self.send_json({"root": get_project_root()})
            return
            
        # 3. List Tasks API
        elif self.path == "/api/tasks":
            tasks = []
            if os.path.exists(TASKS_DIR):
                for filename in os.listdir(TASKS_DIR):
                    if filename.startswith("task-") and filename.endswith(".md"):
                        try:
                            t = parse_task_file(os.path.join(TASKS_DIR, filename))
                            tasks.append(t)
                        except Exception as e:
                            print(f"[-] Error parsing task file {filename}: {e}")
            tasks.sort(key=lambda x: x["id"])
            self.send_json(tasks)
            return

        # 4. List Docs API
        elif self.path == "/api/docs":
            docs = []
            if os.path.exists(DOCS_DIR):
                for root, dirs, files in os.walk(DOCS_DIR):
                    for file in files:
                        if file.endswith(".md"):
                            full_path = os.path.join(root, file)
                            rel = os.path.relpath(full_path, DOCS_DIR).replace("\\", "/")
                            try:
                                with open(full_path, "r", encoding="utf-8") as f:
                                    content = f.read()
                                # Extract title from first H1 if possible
                                title = file.replace(".md", "").replace("-", " ").title()
                                for line in content.split("\n"):
                                    if line.startswith("# "):
                                        title = line.replace("# ", "").strip()
                                        break
                                docs.append({
                                    "path": rel,
                                    "title": title,
                                    "content": content
                                })
                            except Exception as e:
                                print(f"[-] Error reading doc {file}: {e}")
            self.send_json(docs)
            return

        # 5. List Memories API
        elif self.path == "/api/memories":
            memories = []
            if os.path.exists(MEMORIES_PATH):
                try:
                    with open(MEMORIES_PATH, "r", encoding="utf-8") as f:
                        memories = json.load(f)
                except Exception as e:
                    print(f"[-] Error reading memories file: {e}")
            self.send_json(memories)
            return

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        ensure_directories()
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            payload = json.loads(body) if body else {}
        except Exception as e:
            self.send_error(400, f"Malformed JSON: {e}")
            return

        # 1. Edit Task Status / AC
        if self.path == "/api/tasks/edit":
            task_id = payload.get("id")
            if not task_id:
                self.send_json({"error": "Missing task ID"}, 400)
                return
                
            task_path = os.path.join(TASKS_DIR, f"task-{task_id}.md")
            if not os.path.exists(task_path):
                self.send_json({"error": "Task not found"}, 404)
                return
                
            try:
                meta = parse_task_file(task_path)
                
                # Check if updating status
                if "status" in payload:
                    meta["status"] = payload["status"]
                    
                # Check if checking off AC
                if "ac_index" in payload and "checked" in payload:
                    ac_idx = int(payload["ac_index"]) - 1
                    if 0 <= ac_idx < len(meta["ac"]):
                        meta["ac"][ac_idx]["checked"] = payload["checked"]
                        
                write_task_file(meta)
                self.send_json({"success": True, "task": meta})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        # 2. Add Memory
        elif self.path == "/api/memories/add":
            content = payload.get("content")
            if not content:
                self.send_json({"error": "Missing content"}, 400)
                return
                
            memories = []
            if os.path.exists(MEMORIES_PATH):
                try:
                    with open(MEMORIES_PATH, "r", encoding="utf-8") as f:
                        memories = json.load(f)
                except:
                    pass
                    
            new_mem = {
                "id": len(memories) + 1,
                "content": content,
                "category": payload.get("category", "general"),
                "layer": payload.get("layer", "project"),
                "createdAt": "just now"
            }
            memories.append(new_mem)
            
            try:
                with open(MEMORIES_PATH, "w", encoding="utf-8") as f:
                    json.dump(memories, f, indent=2)
                self.send_json({"success": True, "memories": memories})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        else:
            self.send_error(404, "Not Found")

def start_server(port=6420, open_browser=True):
    # Bind to first available port starting from port
    attempts = 10
    server_address = ('127.0.0.1', port)
    httpd = None
    
    for offset in range(attempts):
        current_port = port + offset
        try:
            server_address = ('127.0.0.1', current_port)
            httpd = socketserver.TCPServer(server_address, AIMBrowserHandler)
            port = current_port
            break
        except OSError:
            print(f"[-] Port {current_port} is busy, trying next...")
            
    if httpd is None:
        print(f"[-] Error: Could not bind server to any port in range {port}-{port+attempts-1}")
        sys.exit(1)
        
    url = f"http://localhost:{port}"
    print("=========================================")
    print("         AIM Mind Control Panel 🎯        ")
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
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down AIM Web UI server...")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    start_server()
