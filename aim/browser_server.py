import os
import json
import http.server
import socketserver
import webbrowser
import urllib.parse
import sys
import re
import time

# Import helpers
try:
    from aim.aim_cli import parse_task_file, write_task_file, ensure_directories, get_project_root
    from aim.aim_cli import TASKS_DIR, DOCS_DIR, MEMORIES_PATH, load_users, save_users, USERS_PATH
except ImportError:
    from aim_cli import parse_task_file, write_task_file, ensure_directories, get_project_root
    from aim_cli import TASKS_DIR, DOCS_DIR, MEMORIES_PATH, load_users, save_users, USERS_PATH

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIM Control Panel</title>
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <!-- Marked for Markdown rendering -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg: #06050b;
            --bg-gradient: radial-gradient(circle at 50% 0%, #15112e 0%, #06050b 80%);
            --surface: rgba(18, 16, 32, 0.65);
            --surface-solid: #0e0d1a;
            --surface-hover: rgba(30, 26, 54, 0.8);
            --border: rgba(255, 255, 255, 0.07);
            --border-hover: rgba(99, 102, 241, 0.3);
            
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.15);
            --primary-glow-strong: rgba(99, 102, 241, 0.35);
            
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.15);
            --warning: #f59e0b;
            --warning-glow: rgba(245, 158, 11, 0.15);
            --danger: #ef4444;
            --danger-glow: rgba(239, 68, 68, 0.15);
            
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
            background: var(--bg);
            background-image: var(--bg-gradient);
            background-attachment: fixed;
            color: var(--text);
            line-height: 1.5;
            overflow-x: hidden;
            min-height: 100vh;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(99, 102, 241, 0.4);
        }

        header {
            background: rgba(10, 8, 20, 0.6);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border);
            padding: 1.25rem 2.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo-area {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-area h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.7rem;
            font-weight: 700;
            background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }

        .badge {
            background-color: var(--primary-glow);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            padding: 0.2rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 0 10px rgba(99, 102, 241, 0.1);
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .project-path {
            font-size: 0.85rem;
            color: var(--text-muted);
            font-family: monospace;
            background-color: rgba(0, 0, 0, 0.35);
            padding: 0.4rem 0.9rem;
            border-radius: 8px;
            border: 1px solid var(--border);
            max-width: 450px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .tabs {
            display: flex;
            gap: 0.35rem;
            padding: 0.75rem 2.5rem;
            background-color: rgba(6, 5, 11, 0.4);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 73px;
            z-index: 90;
            backdrop-filter: blur(12px);
            flex-wrap: wrap;
        }

        .tab-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            font-family: inherit;
            font-size: 0.95rem;
            font-weight: 600;
            padding: 0.55rem 1.1rem;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .tab-btn:hover {
            color: var(--text);
            background-color: rgba(255, 255, 255, 0.03);
        }

        .tab-btn.active {
            color: #ffffff;
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35);
        }

        main {
            padding: 2.5rem;
            max-width: 1500px;
            margin: 0 auto;
            min-height: calc(100vh - 180px);
        }

        .tab-content {
            display: none;
            animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* 🔮 GENERAL PREMIUM GLASS CARD */
        .glass-panel {
            background: var(--surface);
            backdrop-filter: blur(16px) saturate(180%);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.5rem;
            box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.05), 0 8px 32px 0 rgba(0, 0, 0, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glass-panel:hover {
            border-color: rgba(255, 255, 255, 0.12);
        }

        /* 🔮 DASHBOARD LANDING */
        .hero-panel {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.05) 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 14px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.05);
        }

        .hero-left h2 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 0.35rem;
            background: linear-gradient(to right, #ffffff, #c7d2fe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-left p {
            color: var(--text-muted);
            font-size: 0.95rem;
        }

        .tech-stack-container {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
        }

        .stack-tag {
            background-color: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.2);
            color: #c7d2fe;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .metric-card {
            background: var(--surface);
            backdrop-filter: blur(12px) saturate(180%);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 180px;
            box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.05), 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .metric-card:hover {
            transform: translateY(-4px);
            border-color: var(--border-hover);
            box-shadow: 0 12px 30px rgba(99, 102, 241, 0.12);
        }

        .metric-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-muted);
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-icon {
            font-size: 1.2rem;
            opacity: 0.8;
        }

        .metric-body {
            margin: 1rem 0;
        }

        .metric-value-huge {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.1;
        }

        .metric-subtext {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }

        /* Custom widgets for metric cards */
        .progress-circle-wrap {
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .progress-bar-container {
            background: rgba(255, 255, 255, 0.05);
            height: 6px;
            width: 100%;
            border-radius: 99px;
            overflow: hidden;
        }

        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(to right, #6366f1, #10b981);
            box-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
            border-radius: 99px;
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .tracker-active-block {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .tracker-status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--text-muted);
            display: inline-block;
            transition: background-color 0.3s ease;
        }

        .tracker-status-dot.active {
            background-color: var(--danger);
            box-shadow: 0 0 8px var(--danger);
            animation: pulse 1.5s infinite alternate;
        }

        @keyframes pulse {
            from { opacity: 0.4; }
            to { opacity: 1; }
        }

        .tracker-live-counter {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--danger);
            text-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
            margin-top: 0.25rem;
        }

        .kb-metrics {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }

        .kb-metric-item {
            display: flex;
            flex-direction: column;
        }

        .kb-num {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff;
        }

        .kb-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
        }

        .kb-separator {
            width: 1px;
            height: 35px;
            background-color: var(--border);
        }

        .health-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            margin-bottom: 0.35rem;
        }

        .health-label {
            color: var(--text-muted);
        }

        .health-val-badge {
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-success {
            background-color: var(--success-glow);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }

        .badge-warning {
            background-color: var(--warning-glow);
            color: var(--warning);
            border: 1px solid rgba(245, 158, 11, 0.2);
        }

        .badge-danger {
            background-color: var(--danger-glow);
            color: var(--danger);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .dashboard-details-grid {
            display: grid;
            grid-template-columns: 1.8fr 1.2fr;
            gap: 1.5rem;
        }

        .details-panel {
            background: var(--surface);
            backdrop-filter: blur(16px) saturate(180%);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.75rem;
            box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.05), 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        }

        .panel-header {
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.75rem;
            margin-bottom: 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .panel-header h3 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.15rem;
            font-weight: 600;
            letter-spacing: -0.2px;
        }

        /* 📋 TIMELINE & LOGS */
        .timeline {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-height: 350px;
            overflow-y: auto;
            padding-right: 0.5rem;
        }

        .timeline-item {
            position: relative;
            padding-left: 1.5rem;
            border-left: 2px solid rgba(99, 102, 241, 0.25);
            padding-bottom: 0.5rem;
        }

        .timeline-item::before {
            content: '';
            position: absolute;
            left: -5px;
            top: 5px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--primary);
            box-shadow: 0 0 8px var(--primary);
        }

        .timeline-header {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-bottom: 0.15rem;
        }

        .timeline-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #ffffff;
        }

        .timeline-body {
            font-size: 0.85rem;
            color: #c7d2fe;
            background-color: rgba(0, 0, 0, 0.15);
            padding: 0.4rem 0.65rem;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.02);
            margin-top: 0.25rem;
        }

        /* SYNC FILE LIST */
        .sync-files-list {
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
        }

        .sync-file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.55rem 0.75rem;
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 0.85rem;
            transition: all 0.2s ease;
        }

        .sync-file-item:hover {
            border-color: rgba(255, 255, 255, 0.12);
            background-color: rgba(255, 255, 255, 0.04);
        }

        .sync-filename {
            font-family: monospace;
            font-weight: 500;
        }

        /* RECENT MEMORIES LIST */
        .recent-memories-list {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            max-height: 280px;
            overflow-y: auto;
            padding-right: 0.5rem;
        }

        .recent-memory-item {
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 0.85rem;
            border-left: 3px solid var(--warning);
        }

        .recent-memory-meta {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
            text-transform: uppercase;
        }

        /* 📋 KANBAN BOARD */
        .kanban-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            align-items: start;
        }

        .kanban-col {
            background-color: rgba(18, 16, 32, 0.5);
            backdrop-filter: blur(12px);
            border-radius: 14px;
            border: 1px solid var(--border);
            padding: 1.25rem;
            min-height: 600px;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            transition: all 0.2s ease;
        }

        .kanban-col.drag-over {
            background-color: rgba(99, 102, 241, 0.05);
            border: 1px dashed rgba(99, 102, 241, 0.4);
        }

        .task-card.dragging {
            opacity: 0.4;
            border: 1px dashed var(--primary);
            transform: scale(0.98);
        }

        .col-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.75rem;
            margin-bottom: 0.25rem;
        }

        .col-title {
            font-weight: 600;
            font-size: 1.05rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: 'Space Grotesk', sans-serif;
        }

        .col-count {
            background-color: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.25);
            padding: 0.15rem 0.55rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: bold;
        }

        .task-card {
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 1.1rem;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
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
            border-color: rgba(99, 102, 241, 0.3);
            background-color: var(--surface-hover);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .task-card:hover::before {
            opacity: 1;
        }

        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
        }

        .task-id {
            font-family: monospace;
            font-size: 0.8rem;
            color: #a5b4fc;
            font-weight: bold;
            background-color: rgba(99, 102, 241, 0.1);
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
        }

        .task-priority {
            font-size: 0.65rem;
            text-transform: uppercase;
            font-weight: 800;
            padding: 0.1rem 0.45rem;
            border-radius: 4px;
            letter-spacing: 0.5px;
        }

        .pri-urgent { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35); }
        .pri-high { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.35); }
        .pri-medium { background-color: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.35); }
        .pri-low { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); }

        .task-title {
            font-weight: 600;
            font-size: 0.95rem;
            color: #ffffff;
            line-height: 1.4;
        }

        .task-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-muted);
            border-top: 1px solid rgba(255, 255, 255, 0.03);
            padding-top: 0.6rem;
            margin-top: 0.25rem;
        }

        .task-progress {
            background-color: rgba(255, 255, 255, 0.05);
            height: 4px;
            width: 70px;
            border-radius: 99px;
            overflow: hidden;
            position: relative;
        }

        .task-progress-bar {
            height: 100%;
            background-color: var(--success);
            border-radius: 99px;
        }

        /* 📚 DOCUMENT LIBRARY */
        .doc-layout {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 2rem;
            background-color: var(--surface);
            backdrop-filter: blur(16px);
            border-radius: 14px;
            border: 1px solid var(--border);
            min-height: 650px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            overflow: hidden;
        }

        .doc-sidebar {
            border-right: 1px solid var(--border);
            padding: 1.75rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            background-color: rgba(0,0,0,0.15);
        }

        .doc-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            overflow-y: auto;
            max-height: 520px;
            padding-right: 0.25rem;
        }

        .doc-item {
            padding: 0.75rem 1rem;
            background-color: rgba(255, 255, 255, 0.01);
            border: 1px solid var(--border);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 0.88rem;
            font-weight: 500;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .doc-item:hover, .doc-item.active {
            background-color: var(--primary-glow);
            border-color: var(--primary);
            color: #ffffff;
            box-shadow: 0 4px 10px rgba(99, 102, 241, 0.15);
        }

        .doc-content {
            padding: 3rem;
            overflow-y: auto;
            max-height: 650px;
            background-color: rgba(0, 0, 0, 0.05);
        }

        /* Markdown styling inside doc viewer */
        .markdown-body {
            color: #d1d5db;
        }
        .markdown-body h1 { 
            font-size: 2rem; 
            margin-bottom: 1.5rem; 
            font-family: 'Space Grotesk', sans-serif; 
            border-bottom: 1px solid var(--border); 
            padding-bottom: 0.5rem; 
            color: #ffffff;
        }
        .markdown-body h2 { 
            font-size: 1.4rem; 
            margin-top: 2rem; 
            margin-bottom: 1rem; 
            border-bottom: 1px solid var(--border); 
            padding-bottom: 0.25rem; 
            color: #ffffff;
        }
        .markdown-body h3 { font-size: 1.15rem; margin-top: 1.5rem; margin-bottom: 0.75rem; color: #ffffff; }
        .markdown-body p { margin-bottom: 1.15rem; line-height: 1.6; }
        .markdown-body ul, .markdown-body ol { margin-bottom: 1.15rem; padding-left: 1.75rem; }
        .markdown-body li { margin-bottom: 0.35rem; }
        .markdown-body pre { 
            background-color: rgba(0,0,0,0.45); 
            padding: 1.25rem; 
            border-radius: 8px; 
            border: 1px solid var(--border); 
            overflow-x: auto; 
            margin-bottom: 1.25rem; 
            font-family: monospace; 
        }
        .markdown-body code { font-family: monospace; background-color: rgba(255,255,255,0.07); padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.9em; color: #a5b4fc; }
        .markdown-body pre code { background: none; padding: 0; color: inherit; font-size: inherit; }
        .markdown-body blockquote { border-left: 4px solid var(--primary); padding-left: 1.25rem; margin-bottom: 1.25rem; font-style: italic; color: var(--text-muted); }

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
            gap: 1.5rem;
        }

        .memory-card {
            background-color: var(--surface);
            backdrop-filter: blur(12px);
            border-radius: 12px;
            border: 1px solid var(--border);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            border-left: 4px solid var(--primary);
        }

        .memory-card:hover {
            transform: translateY(-2px);
            border-color: var(--primary);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
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
            letter-spacing: 0.5px;
        }

        .mem-layer {
            background-color: rgba(255,255,255,0.05);
            padding: 0.15rem 0.55rem;
            border-radius: 4px;
            color: var(--text-muted);
        }

        .mem-content {
            font-size: 0.92rem;
            color: #d1d5db;
            line-height: 1.45;
            word-break: break-word;
        }

        /* FORMS & INPUTS */
        .form-panel {
            background-color: var(--surface);
            backdrop-filter: blur(16px);
            border-radius: 14px;
            border: 1px solid var(--border);
            padding: 1.75rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
        }

        .form-title {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            font-size: 1.15rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.5rem;
            margin-bottom: 0.25rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .form-group label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-control {
            background-color: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.65rem 0.9rem;
            color: var(--text);
            font-family: inherit;
            font-size: 0.92rem;
            transition: border-color 0.2s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 10px rgba(99, 102, 241, 0.15);
        }

        .btn {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.7rem 1.4rem;
            font-weight: 600;
            font-family: inherit;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
            font-size: 0.9rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn:hover {
            opacity: 0.95;
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        }

        .btn-sync {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.1) 100%);
            border: 1px solid rgba(99, 102, 241, 0.35);
            color: #c7d2fe;
            box-shadow: none;
            padding: 0.45rem 1rem;
            font-size: 0.8rem;
        }
        .btn-sync:hover {
            background: rgba(99, 102, 241, 0.3);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: #ffffff;
            box-shadow: none;
        }
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255,255,255,0.2);
            box-shadow: none;
        }

        .btn-danger {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
        }
        .btn-danger:hover {
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
        }

        .btn-sm {
            padding: 0.35rem 0.75rem;
            font-size: 0.78rem;
            border-radius: 6px;
        }

        /* MODAL */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(3, 3, 7, 0.8);
            backdrop-filter: blur(8px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .modal {
            background-color: var(--surface-solid);
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            width: 90%;
            max-width: 650px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            animation: modalSlide 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        }

        @keyframes modalSlide {
            from { transform: translateY(30px); opacity: 0; }
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
            font-size: 1.6rem;
            cursor: pointer;
            line-height: 1;
        }

        .modal-close:hover {
            color: var(--text);
        }

        .modal-body {
            padding: 1.75rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .modal-section-title {
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }

        .ac-list {
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            margin-top: 0.5rem;
        }

        .ac-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            background-color: rgba(255, 255, 255, 0.01);
            padding: 0.6rem 0.85rem;
            border-radius: 8px;
            border: 1px solid var(--border);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .ac-item:hover {
            background-color: rgba(255, 255, 255, 0.03);
            border-color: rgba(255, 255, 255, 0.12);
        }

        .ac-item input[type="checkbox"] {
            width: 1.15rem;
            height: 1.15rem;
            accent-color: var(--success);
            cursor: pointer;
        }

        .ac-text {
            font-size: 0.9rem;
            color: #d1d5db;
            transition: all 0.2s ease;
        }

        .ac-text.checked {
            text-decoration: line-through;
            color: var(--text-muted);
        }

        /* Time Tracking Action Inside Modal */
        .modal-timer-banner {
            background: rgba(99, 102, 241, 0.08);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 10px;
            padding: 0.9rem 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .timer-active-badge {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
            font-size: 0.88rem;
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <h1>AIM Control Hub</h1>
            <span class="badge">v0.2.0</span>
        </div>
        <div class="header-right">
            <div class="project-path" id="projectRootDisplay">Loading project root...</div>
            <button class="btn btn-secondary" onclick="openSearchModal()" style="display:flex; align-items:center; gap:0.5rem; background:rgba(255,255,255,0.04); border:1px solid var(--border); box-shadow:none; padding: 0.45rem 0.9rem;"><span style="font-size:0.9rem; margin-top:-2px;">🔍</span> Search... <kbd style="font-size:0.75rem; background:rgba(255,255,255,0.1); padding:0.1rem 0.35rem; border-radius:4px; font-family:inherit; color:var(--text-muted);">Ctrl+K</kbd></button>
            <button class="btn btn-sync" onclick="triggerSync()">Sync Rules</button>
        </div>
    </header>

    <nav class="tabs">
        <button class="tab-btn active" id="tab-dashboard" onclick="switchTab('dashboard')">🔮 Dashboard</button>
        <button class="tab-btn" id="tab-tasks" onclick="switchTab('tasks')">📋 Task Board</button>
        <button class="tab-btn" id="tab-docs" onclick="switchTab('docs')">📚 Document Library</button>
        <button class="tab-btn" id="tab-memory" onclick="switchTab('memory')">🧠 Memory Storage</button>
        <button class="tab-btn" id="tab-users" onclick="switchTab('users')">👥 Users</button>
        <button class="tab-btn" id="tab-graph" onclick="switchTab('graph')">🕸️ Knowledge Graph</button>
    </nav>

    <main>
        <!-- 🔮 DASHBOARD CONTENT -->
        <div id="dashboardContent" class="tab-content active">
            <!-- Hero Panel -->
            <div class="hero-panel">
                <div class="hero-left">
                    <h2>Welcome to your Project Mind</h2>
                    <p>AIM (AI Memory/Mind) engine is tracking and maintaining repository context.</p>
                </div>
                <div class="hero-right">
                    <div class="tech-stack-container" id="techStackContainer">
                        <!-- Filled by JS -->
                    </div>
                </div>
            </div>

            <!-- Metrics Grid -->
            <div class="metrics-grid">
                <!-- Task Progress Card -->
                <div class="metric-card">
                    <div class="metric-header">
                        <span>Task Completion</span>
                        <span class="metric-icon">📋</span>
                    </div>
                    <div class="metric-body">
                        <div class="metric-value-huge" id="taskCompletionPct">0%</div>
                        <div class="metric-subtext" id="taskCompletionRatio">0 of 0 tasks done</div>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" id="taskProgressBar" style="width: 0%"></div>
                    </div>
                </div>

                <!-- Time Spent / Live Timer Card -->
                <div class="metric-card" id="trackerMetricCard">
                    <div class="metric-header">
                        <span>Time Tracked</span>
                        <span class="tracker-status-dot" id="trackerStatusDot"></span>
                    </div>
                    <div class="metric-body">
                        <div class="metric-value-huge" id="totalTimeSpentText">0h 0m</div>
                        <div class="metric-subtext" id="activeTaskText">No active timer running</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; min-height: 30px;">
                        <span class="tracker-live-counter" id="trackerLiveTimerText" style="display: none;">00:00:00</span>
                        <button class="btn btn-danger btn-sm" id="btnStopTimer" style="display: none;" onclick="stopTimerFromDashboard()">Stop Tracking</button>
                    </div>
                </div>

                <!-- Knowledge Base Metrics Card -->
                <div class="metric-card">
                    <div class="metric-header">
                        <span>Knowledge Base</span>
                        <span class="metric-icon">📚</span>
                    </div>
                    <div class="metric-body">
                        <div class="kb-metrics">
                            <div class="kb-metric-item">
                                <span class="kb-num" id="docsCountText">0</span>
                                <span class="kb-label">Documents</span>
                            </div>
                            <div class="kb-separator"></div>
                            <div class="kb-metric-item">
                                <span class="kb-num" id="memoriesCountText">0</span>
                                <span class="kb-label">Memories</span>
                            </div>
                        </div>
                    </div>
                    <div class="metric-subtext">Captured project guides & rules</div>
                </div>

                <!-- System Health Status Card -->
                <div class="metric-card">
                    <div class="metric-header">
                        <span>System Health</span>
                        <span class="metric-icon">🛡️</span>
                    </div>
                    <div class="metric-body">
                        <div class="health-item">
                            <span class="health-label">Configs:</span>
                            <span class="health-val-badge badge-success" id="syncStatusBadge">Synced</span>
                        </div>
                        <div class="health-item" style="margin-top: 0.35rem;">
                            <span class="health-label">Links Health:</span>
                            <span class="health-val-badge badge-success" id="refHealthBadge">Healthy</span>
                        </div>
                    </div>
                    <button class="btn btn-secondary btn-sm" onclick="runValidation()">Validate Links</button>
                </div>
            </div>

            <!-- Details Dashboard Row -->
            <div class="dashboard-details-grid">
                <!-- Left panel: Recent activity logs -->
                <div class="details-panel">
                    <div class="panel-header">
                        <h3>Session Activity Log</h3>
                    </div>
                    <div class="timeline" id="recentTimeLogsContainer">
                        <!-- Filled by JS -->
                    </div>
                </div>

                <!-- Right panel: Sync files coverage and quick memories list -->
                <div class="details-panel">
                    <div class="panel-header">
                        <h3>Shim Synchronized Files</h3>
                    </div>
                    <div class="sync-files-list" id="syncFilesContainer">
                        <!-- Filled by JS -->
                    </div>

                    <div class="panel-header" style="margin-top: 1.5rem; margin-bottom: 0.75rem; border-top: 1px solid var(--border); padding-top: 1.25rem;">
                        <h3>Recent Decisions & Notes</h3>
                    </div>
                    <div class="recent-memories-list" id="recentMemoriesContainer">
                        <!-- Filled by JS -->
                    </div>
                </div>
            </div>
        </div>

        <!-- 📋 KANBAN CONTENT -->
        <div id="tasksContent" class="tab-content">
            <div style="display:flex; justify-content:flex-end; margin-bottom:1.25rem;">
                <button class="btn btn-sync" onclick="openCreateTaskModal()">+ New Task</button>
            </div>
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
                    <h2 style="font-size:1.1rem; font-weight:600; font-family:'Space Grotesk', sans-serif;">Documents</h2>
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

        <!-- 👥 USERS CONTENT -->
        <div id="usersContent" class="tab-content">
            <div class="memory-layout" style="grid-template-columns: 1fr 380px;">
                <div class="glass-panel" style="display: flex; flex-direction: column; gap: 1rem; min-height: 500px;">
                    <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; color: #ffffff; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; margin-bottom: 0.5rem;">Project Team Members</h2>
                    <div id="usersListContainer" style="display: flex; flex-direction: column; gap: 0.75rem;">
                        <!-- Filled by JS -->
                    </div>
                </div>
                <div class="form-panel">
                    <h3 class="form-title">Register New User</h3>
                    <div class="form-group">
                        <label for="newUsernameInput">Username</label>
                        <input type="text" id="newUsernameInput" class="form-control" placeholder="e.g. alice, bob">
                    </div>
                    <button class="btn" onclick="addNewUser()">Add User</button>
                </div>
            </div>
        </div>

        <!-- 🕸️ KNOWLEDGE GRAPH CONTENT -->
        <div id="graphContent" class="tab-content">
            <div class="glass-panel" style="display: flex; flex-direction: column; gap: 1rem; min-height: 700px; position: relative;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem; flex-wrap: wrap; gap: 1rem;">
                    <div>
                        <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; color: #ffffff;">Interactive Context Graph</h2>
                        <p style="font-size: 0.85rem; color: var(--text-muted);">Visualizing cross-references between Tasks and Documents. Drag nodes to explore, double-click to view details.</p>
                    </div>
                    <div style="display: flex; gap: 1.5rem; font-size: 0.85rem; align-items: center;">
                        <span style="display: flex; align-items: center; gap: 0.35rem;"><span style="width: 10px; height: 10px; border-radius: 50%; background: #6366f1; box-shadow: 0 0 6px #6366f1; display: inline-block;"></span> Tasks</span>
                        <span style="display: flex; align-items: center; gap: 0.35rem;"><span style="width: 10px; height: 10px; border-radius: 50%; background: #10b981; box-shadow: 0 0 6px #10b981; display: inline-block;"></span> Documents</span>
                        <button class="btn btn-secondary btn-sm" onclick="fetchGraphData()">Reset Layout</button>
                    </div>
                </div>
                
                <div style="position: relative; flex: 1; background: rgba(0,0,0,0.25); border-radius: 10px; overflow: hidden; min-height: 550px; border: 1px solid var(--border);">
                    <canvas id="graphCanvas" style="display: block; width: 100%; height: 100%; min-height: 550px; cursor: grab;"></canvas>
                    <div id="graphTooltip" style="position: absolute; display: none; background: rgba(10, 8, 20, 0.95); border: 1px solid var(--primary); border-radius: 6px; padding: 0.5rem 0.75rem; font-size: 0.82rem; pointer-events: none; z-index: 10; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5); color: #ffffff; line-height: 1.4;"></div>
                </div>
            </div>
        </div>
    </main>

    <!-- SEARCH MODAL (COMMAND PALETTE STYLE) -->
    <div class="modal-overlay" id="searchModalOverlay" onclick="closeSearchModal(event)">
        <div class="modal" onclick="event.stopPropagation()" style="max-width: 650px; margin-top: 10vh; align-self: flex-start; border-color: rgba(99, 102, 241, 0.45); box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7), 0 0 30px rgba(99, 102, 241, 0.15);">
            <div style="padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border); display: flex; gap: 1rem; align-items: center;">
                <span style="font-size: 1.25rem;">🔍</span>
                <input type="text" id="modalSearchInput" style="flex: 1; background: none; border: none; color: #ffffff; font-size: 1.1rem; outline: none; font-family: inherit;" placeholder="Search tasks, docs, memories... (Esc to exit)" onkeyup="handleModalSearchKeyup(event)">
                <button class="modal-close" onclick="closeSearchModal(null)">&times;</button>
            </div>
            <div class="modal-body" id="modalSearchResults" style="max-height: 400px; padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 0.75rem; overflow-y: auto;">
                <div style="color: var(--text-muted); text-align: center; padding: 2rem 0;">Type a keyword to start searching...</div>
            </div>
            <div style="padding: 0.6rem 1.5rem; border-top: 1px solid var(--border); font-size: 0.75rem; color: var(--text-muted); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.15); border-bottom-left-radius: 14px; border-bottom-right-radius: 14px;">
                <span>Use keyboard to navigate results</span>
                <span>Esc to close</span>
            </div>
        </div>
    </div>

    <!-- CREATE TASK MODAL -->
    <div class="modal-overlay" id="createTaskModalOverlay" onclick="closeCreateTaskModal(event)">
        <div class="modal" onclick="event.stopPropagation()" style="max-width: 600px;">
            <div class="modal-header">
                <h3 style="margin:0; font-family:'Space Grotesk',sans-serif; font-weight:600;">Create New Task</h3>
                <button class="modal-close" onclick="closeCreateTaskModal(null)">&times;</button>
            </div>
            <div class="modal-body" style="display:flex; flex-direction:column; gap:1rem; padding:1.5rem;">
                <div style="display:flex; flex-direction:column; gap:0.35rem;">
                    <label style="font-weight:600; font-size:0.82rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">Title *</label>
                    <input type="text" id="createTaskTitleInput" class="form-control" placeholder="e.g. Implement user dashboard styling" required style="background:rgba(0,0,0,0.3); border:1px solid var(--border); border-radius:6px; color:#ffffff; padding:0.45rem 0.75rem; font-family:inherit; outline:none;">
                </div>
                <div style="display:flex; flex-direction:column; gap:0.35rem;">
                    <label style="font-weight:600; font-size:0.82rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">Description</label>
                    <textarea id="createTaskDescInput" class="form-control" style="min-height:80px; font-family:inherit; background:rgba(0,0,0,0.3); border:1px solid var(--border); border-radius:6px; color:#ffffff; padding:0.45rem 0.75rem; outline:none; resize:vertical;" placeholder="Detailed description of the task..."></textarea>
                </div>
                <div style="display:flex; gap:1.5rem;">
                    <div style="flex:1; display:flex; flex-direction:column; gap:0.35rem;">
                        <label style="font-weight:600; font-size:0.82rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">Status</label>
                        <select id="createTaskStatusSelect" class="form-control" style="background:rgba(0,0,0,0.3); border:1px solid var(--border); border-radius:6px; color:#ffffff; padding:0.45rem 0.75rem; font-family:inherit; outline:none;">
                            <option value="todo">Todo</option>
                            <option value="in-progress">In Progress</option>
                            <option value="in-review">In Review</option>
                            <option value="done">Done</option>
                        </select>
                    </div>
                    <div style="flex:1; display:flex; flex-direction:column; gap:0.35rem;">
                        <label style="font-weight:600; font-size:0.82rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">Priority</label>
                        <select id="createTaskPrioritySelect" class="form-control" style="background:rgba(0,0,0,0.3); border:1px solid var(--border); border-radius:6px; color:#ffffff; padding:0.45rem 0.75rem; font-family:inherit; outline:none;">
                            <option value="low">Low</option>
                            <option value="medium" selected>Medium</option>
                            <option value="high">High</option>
                            <option value="urgent">Urgent</option>
                        </select>
                    </div>
                </div>
                <div style="display:flex; gap:1.5rem;">
                    <div style="flex:1; display:flex; flex-direction:column; gap:0.35rem;">
                        <label style="font-weight:600; font-size:0.82rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">Assignee</label>
                        <select id="createTaskAssigneeSelect" class="form-control" style="background:rgba(0,0,0,0.3); border:1px solid var(--border); border-radius:6px; color:#ffffff; padding:0.45rem 0.75rem; font-family:inherit; outline:none;"></select>
                    </div>
                    <div style="flex:1; display:flex; flex-direction:column; gap:0.35rem;">
                        <label style="font-weight:600; font-size:0.82rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">Labels (comma separated)</label>
                        <input type="text" id="createTaskLabelsInput" class="form-control" placeholder="e.g. bug, frontend" style="background:rgba(0,0,0,0.3); border:1px solid var(--border); border-radius:6px; color:#ffffff; padding:0.45rem 0.75rem; font-family:inherit; outline:none;">
                    </div>
                </div>
                <div style="display:flex; justify-content:flex-end; gap:0.75rem; margin-top:0.75rem;">
                    <button class="btn btn-secondary" onclick="closeCreateTaskModal(null)">Cancel</button>
                    <button class="btn btn-sync" onclick="submitCreateTask()">Create Task</button>
                </div>
            </div>
        </div>
    </div>

    <!-- TASK DETAILS MODAL -->
    <div class="modal-overlay" id="taskModalOverlay" onclick="closeTaskModal(event)">
        <div class="modal" onclick="event.stopPropagation()" style="max-width: 750px; max-height: 90vh;">
            <div class="modal-header">
                <div style="flex: 1;">
                    <span class="task-id" id="modalTaskId">TASK-1</span>
                    <div style="display:flex; align-items:center; gap:0.5rem; width:100%; margin-top:0.35rem;">
                        <input type="text" id="modalTaskTitleInput" style="flex:1; background:none; border:none; border-bottom:1px solid transparent; color:#ffffff; font-size: 1.35rem; font-weight: 600; font-family: 'Space Grotesk', sans-serif; outline:none;" onchange="updateTaskTitle()" onfocus="this.style.borderBottomColor='var(--primary)'" onblur="this.style.borderBottomColor='transparent'">
                    </div>
                </div>
                <button class="btn btn-secondary btn-sm" onclick="deleteActiveTask()" style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.35); color:#f87171; margin-right:1rem; padding:0.25rem 0.65rem; font-size:0.82rem;">Delete Task</button>
                <button class="modal-close" onclick="closeTaskModal(null)">&times;</button>
            </div>
            <div class="modal-body" style="overflow-y: auto; padding-right: 0.5rem;">
                <!-- Timer Action Row -->
                <div id="modalTaskTimerContainer">
                    <!-- Filled dynamically -->
                </div>

                <div style="display: flex; flex-direction: column; gap: 0.35rem;">
                    <h3 class="modal-section-title">Description</h3>
                    <textarea id="modalTaskDescInput" class="form-control" style="width: 100%; min-height: 80px; font-family: inherit; font-size: 0.9rem; line-height: 1.4; resize: vertical; background: rgba(0,0,0,0.3);" onchange="updateTaskDescription()" placeholder="Add a description..."></textarea>
                </div>
                
                <div style="display: flex; gap: 2rem; margin-top: 1rem;">
                    <div style="flex: 1; display:flex; flex-direction:column; gap:0.5rem;">
                        <h3 class="modal-section-title">Status</h3>
                        <select id="modalTaskStatusSelect" class="form-control" style="width: 100%;" onchange="updateTaskStatus()">
                            <option value="todo">Todo</option>
                            <option value="in-progress">In Progress</option>
                            <option value="in-review">In Review</option>
                            <option value="done">Done</option>
                        </select>
                    </div>
                    <div style="flex: 1; display:flex; flex-direction:column; gap:0.5rem;">
                        <h3 class="modal-section-title">Priority & Assignee</h3>
                        <div style="font-size: 0.9rem; display: flex; flex-direction: column; gap: 0.5rem;">
                             <div style="display: flex; align-items: center; gap: 0.35rem; color: var(--text-muted); margin-bottom: 0.25rem;">
                                <span>Priority:</span>
                                <select id="modalTaskPrioritySelect" class="form-control" style="padding: 0.25rem 0.5rem; font-size: 0.82rem; background: rgba(0,0,0,0.3); border:1px solid var(--border); border-radius:6px; color:#ffffff; font-family:inherit; outline:none;" onchange="updateTaskPriority()">
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                    <option value="urgent">Urgent</option>
                                </select>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.35rem; color: var(--text-muted);">
                                <span>Assignee:</span>
                                <select id="modalTaskAssigneeSelect" class="form-control" style="padding: 0.25rem 0.5rem; font-size: 0.82rem; background: rgba(0,0,0,0.3); border:1px solid var(--border); border-radius:6px; color:#ffffff; font-family:inherit; outline:none;" onchange="updateTaskAssignee()"></select>
                            </div>
                        </div>
                    </div>
                </div>

                <div style="display: flex; gap: 2rem; margin-top: 1.25rem;">
                    <div style="flex: 1; display: flex; flex-direction: column; gap: 0.5rem;">
                        <h3 class="modal-section-title">Labels</h3>
                        <div id="modalTaskLabelsContainer" style="display: flex; flex-wrap: wrap; gap: 0.35rem; align-items: center; min-height: 28px;"></div>
                        <div style="display: flex; gap: 0.35rem; margin-top: 0.2rem;">
                            <input type="text" id="modalTaskNewLabelInput" class="form-control" style="padding: 0.25rem 0.5rem; font-size: 0.82rem; flex: 1; background: rgba(0,0,0,0.2);" placeholder="e.g. bug, feature">
                            <button class="btn btn-secondary btn-sm" style="padding: 0.25rem 0.65rem; font-size: 0.82rem; background: rgba(255,255,255,0.06); border: 1px solid var(--border);" onclick="addTaskLabel()">Add</button>
                        </div>
                    </div>
                    <div style="flex: 1; display: flex; flex-direction: column; gap: 0.5rem;">
                        <h3 class="modal-section-title">Cross-References</h3>
                        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                            <div style="display: flex; align-items: center; gap: 0.35rem; font-size: 0.85rem; color: var(--text-muted);">
                                <span style="width: 45px;">Spec:</span>
                                <input type="text" id="modalTaskSpecInput" class="form-control" style="padding: 0.2rem 0.5rem; font-size: 0.82rem; flex: 1; background: rgba(0,0,0,0.2);" placeholder="e.g. @doc/sdd/auth.md" onchange="updateTaskSpec()">
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.35rem; font-size: 0.85rem; color: var(--text-muted);">
                                <span style="width: 45px;">Plan:</span>
                                <input type="text" id="modalTaskPlanInput" class="form-control" style="padding: 0.2rem 0.5rem; font-size: 0.82rem; flex: 1; background: rgba(0,0,0,0.2);" placeholder="e.g. @doc/plan.md" onchange="updateTaskPlan()">
                            </div>
                        </div>
                    </div>
                </div>

                <div style="display: flex; gap: 2rem; margin-top: 1.25rem; border-top: 1px solid var(--border); padding-top: 1.25rem;">
                    <div style="flex: 1; display: flex; flex-direction: column; gap: 0.5rem;">
                        <h3 class="modal-section-title">Acceptance Criteria</h3>
                        <div class="ac-list" id="modalTaskAcContainer">
                            <!-- Filled by JS -->
                        </div>
                        <div style="display: flex; gap: 0.35rem; margin-top: 0.25rem;">
                            <input type="text" id="modalTaskNewAcInput" class="form-control" style="padding: 0.25rem 0.5rem; font-size: 0.82rem; flex: 1; background: rgba(0,0,0,0.2);" placeholder="Add criteria...">
                            <button class="btn btn-secondary btn-sm" style="padding: 0.25rem 0.65rem; font-size: 0.82rem; background: rgba(255,255,255,0.06); border: 1px solid var(--border);" onclick="addTaskAc()">Add</button>
                        </div>
                    </div>
                    <div style="flex: 1; display: flex; flex-direction: column; gap: 0.5rem;">
                        <h3 class="modal-section-title">Hierarchy (Subtasks)</h3>
                        <div style="display: flex; align-items: center; gap: 0.35rem; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.25rem;">
                            <span>Parent:</span>
                            <select id="modalTaskParentSelect" class="form-control" style="padding: 0.2rem 0.5rem; font-size: 0.82rem; flex: 1; background: rgba(0,0,0,0.2); outline: none; border-radius:6px; color:#ffffff;" onchange="updateTaskParent()"></select>
                        </div>
                        <div id="modalTaskSubtasksContainer" style="display: flex; flex-direction: column; gap: 0.35rem; max-height: 120px; overflow-y: auto;">
                            <!-- Filled by JS -->
                        </div>
                        <div style="display: flex; gap: 0.35rem; margin-top: 0.25rem;">
                            <input type="text" id="modalTaskNewSubtaskInput" class="form-control" style="padding: 0.25rem 0.5rem; font-size: 0.82rem; flex: 1; background: rgba(0,0,0,0.2);" placeholder="Quick add subtask...">
                            <button class="btn btn-secondary btn-sm" style="padding: 0.25rem 0.65rem; font-size: 0.82rem; background: rgba(255,255,255,0.06); border: 1px solid var(--border);" onclick="quickAddSubtask()">Add</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentTasks = [];
        let currentDocs = [];
        let currentMemories = [];
        let currentUsers = [];
        let currentStatus = null;
        let activeTaskId = null;
        
        let localTimerInterval = null;
        let localTimerStartEpoch = null;

        // Force-directed graph simulation variables
        let graphNodes = [];
        let graphLinks = [];
        let hoveredNode = null;
        let draggedNode = null;
        let isDragging = false;
        let canvas = null;
        let ctx = null;
        let animationFrameId = null;

        // Physics coefficients
        const REPULSION = 1200; // force pushing nodes apart
        const TENSION = 0.05;  // force pulling linked nodes together
        const CENTER_ATTRACTION = 0.012; // force pulling nodes to center
        const DAMPING = 0.82;  // friction
        const NODE_RADIUS = 16;

        function switchTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            const btn = document.getElementById('tab-' + tabName);
            if (btn) btn.classList.add('active');
            
            const content = document.getElementById(tabName + 'Content');
            if (content) content.classList.add('active');
            
            // Cancel any running graph animation if leaving graph tab
            if (tabName !== 'graph' && animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                animationFrameId = null;
            }
            
            if (tabName === 'dashboard') fetchStatus();
            if (tabName === 'tasks') fetchTasks();
            if (tabName === 'docs') fetchDocs();
            if (tabName === 'memory') fetchMemories();
            if (tabName === 'users') fetchUsers();
            if (tabName === 'graph') fetchGraphData();
        }

        // --- SEARCH COMMAND PALETTE MODAL ---
        window.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                openSearchModal();
            }
            if (e.key === 'Escape') {
                closeSearchModal(null);
            }
        });

        function openSearchModal() {
            const overlay = document.getElementById('searchModalOverlay');
            if (overlay) {
                overlay.style.display = 'flex';
                const input = document.getElementById('modalSearchInput');
                if (input) {
                    input.value = '';
                    input.focus();
                }
                const resultsContainer = document.getElementById('modalSearchResults');
                if (resultsContainer) {
                    resultsContainer.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 2rem 0;">Type a keyword to start searching...</div>';
                }
            }
        }

        function closeSearchModal(e) {
            const overlay = document.getElementById('searchModalOverlay');
            if (overlay) {
                if (e === null || e.target === overlay || e.target.classList.contains('modal-close')) {
                    overlay.style.display = 'none';
                }
            }
        }

        function handleModalSearchKeyup(e) {
            if (e.key === 'Escape') {
                closeSearchModal(null);
                return;
            }
            executeModalSearch();
        }

        async function executeModalSearch() {
            const input = document.getElementById('modalSearchInput');
            const container = document.getElementById('modalSearchResults');
            if (!input || !container) return;
            
            const query = input.value.trim();
            if (!query) {
                container.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 2rem 0;">Type a keyword to start searching...</div>';
                return;
            }
            
            try {
                let res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                let results = await res.json();
                
                container.innerHTML = '';
                if (results.length === 0) {
                    container.innerHTML = `<div style="color: var(--text-muted); text-align: center; padding: 2rem 0;">No matches found for "${query}".</div>`;
                    return;
                }
                
                results.forEach(res => {
                    const card = document.createElement('div');
                    card.className = 'task-card';
                    card.style.cursor = 'pointer';
                    card.style.padding = '0.75rem 1rem';
                    card.style.display = 'flex';
                    card.style.flexDirection = 'column';
                    card.style.gap = '0.25rem';
                    
                    let icon = '🏷️';
                    let badge = '';
                    let action = '';
                    
                    if (res.type === 'task') {
                        icon = '📋';
                        badge = `<span class="task-id">TASK-${res.id}</span>`;
                        action = `onclick="closeSearchModal(null); switchTab('tasks'); openTaskModal(${res.id});"`;
                    } else if (res.type === 'doc') {
                        icon = '📚';
                        badge = `<span class="badge" style="background:var(--success-glow); color:var(--success); border-color:rgba(16,185,129,0.2); font-size:0.65rem;">DOC</span>`;
                        action = `onclick="closeSearchModal(null); navigateToDoc('${res.path}')"`;
                    } else if (res.type === 'memory') {
                        icon = '🧠';
                        badge = `<span class="badge" style="background:var(--warning-glow); color:var(--warning); border-color:rgba(245,158,11,0.2); font-size:0.65rem;">MEMORY</span>`;
                        action = `onclick="closeSearchModal(null); switchTab('memory');"`;
                    }
                    
                    card.innerHTML = `
                        <div class="task-header" ${action} style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="display:flex; align-items:center; gap:0.5rem;">
                                <span style="font-size:1.1rem;">${icon}</span>
                                <strong style="color:#ffffff; font-size:0.95rem;">${res.title}</strong>
                            </div>
                            ${badge}
                        </div>
                        <div class="mem-content" style="font-size:0.8rem; color:var(--text-muted); font-family:monospace; line-height:1.3; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" ${action}>
                            ${res.snippet}
                        </div>
                    `;
                    container.appendChild(card);
                });
            } catch (err) {
                console.error("Search failed:", err);
                container.innerHTML = '<div style="color: var(--danger); text-align: center; padding: 2rem 0;">Error running search query.</div>';
            }
        }

        function navigateToDoc(docPath) {
            switchTab('docs');
            const docIdx = currentDocs.findIndex(d => d.path === docPath);
            if (docIdx !== -1) {
                setTimeout(() => {
                    const docItems = document.querySelectorAll('.doc-item');
                    if (docItems[docIdx]) {
                        docItems[docIdx].click();
                    }
                }, 100);
            }
        }

        // --- USER MANAGEMENT LOGIC ---
        async function fetchUsers() {
            try {
                let res = await fetch('/api/users');
                currentUsers = await res.json();
                renderUsers();
            } catch (err) {
                console.error("Failed to fetch users:", err);
            }
        }

        function renderUsers() {
            const container = document.getElementById('usersListContainer');
            if (!container) return;
            
            container.innerHTML = '';
            if (currentUsers.length === 0) {
                container.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 2rem 0;">No users found.</div>';
                return;
            }
            
            currentUsers.forEach(u => {
                const item = document.createElement('div');
                item.className = 'sync-file-item';
                item.style.padding = '0.75rem 1rem';
                
                const isDefault = u === 'developer' || u === 'unassigned';
                const actions = isDefault ? '' : `
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-secondary btn-sm" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; background: rgba(255,255,255,0.04); border: 1px solid var(--border);" onclick="renameUserPrompt('${u}')">Edit</button>
                        <button class="btn btn-danger btn-sm" onclick="removeUser('${u}')">Delete</button>
                    </div>
                `;
                
                item.innerHTML = `
                    <span style="font-weight:600; font-size:0.95rem; color:#ffffff;">👤 ${u} ${isDefault ? '<span class="badge" style="margin-left:0.5rem; font-size:0.6rem; background:rgba(255,255,255,0.06); border-color:var(--border);">SYSTEM</span>' : ''}</span>
                    ${actions}
                `;
                container.appendChild(item);
            });
        }

        async function renameUserPrompt(oldUsername) {
            const newUsername = prompt(`Enter new username for '${oldUsername}':`, oldUsername);
            if (newUsername === null) return;
            const cleanNewName = newUsername.trim().toLowerCase();
            if (!cleanNewName) {
                alert('Username cannot be empty!');
                return;
            }
            if (cleanNewName === oldUsername) return;
            
            try {
                let res = await fetch('/api/users/edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ old_username: oldUsername, new_username: cleanNewName })
                });
                if (res.ok) {
                    await fetchUsers();
                    if (typeof fetchTasks === 'function') fetchTasks();
                } else {
                    let err = await res.json();
                    alert('Failed to rename user: ' + err.error);
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function addNewUser() {
            const input = document.getElementById('newUsernameInput');
            if (!input) return;
            
            const username = input.value.trim().toLowerCase();
            if (!username) {
                alert('Please enter a username!');
                return;
            }
            
            try {
                let res = await fetch('/api/users/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username })
                });
                if (res.ok) {
                    input.value = '';
                    await fetchUsers();
                } else {
                    let err = await res.json();
                    alert('Failed to add user: ' + err.error);
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function removeUser(username) {
            if (!confirm(`Are you sure you want to delete user '${username}'?`)) return;
            
            try {
                let res = await fetch('/api/users/remove', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username })
                });
                if (res.ok) {
                    await fetchUsers();
                } else {
                    let err = await res.json();
                    alert('Failed to delete user: ' + err.error);
                }
            } catch (err) {
                console.error(err);
            }
        }

        // --- TASK ASSIGNMENT OPTIONS IN MODAL ---
        async function fetchUsersDropdownList() {
            try {
                let res = await fetch('/api/users');
                currentUsers = await res.json();
                
                const select = document.getElementById('modalTaskAssigneeSelect');
                if (select) {
                    select.innerHTML = '';
                    currentUsers.forEach(u => {
                        const opt = document.createElement('option');
                        opt.value = u;
                        opt.textContent = u;
                        select.appendChild(opt);
                    });
                }
                const createSelect = document.getElementById('createTaskAssigneeSelect');
                if (createSelect) {
                    createSelect.innerHTML = '';
                    currentUsers.forEach(u => {
                        const opt = document.createElement('option');
                        opt.value = u;
                        opt.textContent = u;
                        createSelect.appendChild(opt);
                    });
                    createSelect.value = 'unassigned';
                }
            } catch (err) {
                console.error("Failed to load users for dropdown:", err);
            }
        }

        async function updateTaskAssignee() {
            const select = document.getElementById('modalTaskAssigneeSelect');
            if (!select || !activeTaskId) return;
            
            const assignee = select.value;
            try {
                let res = await fetch('/api/tasks/edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: activeTaskId,
                        assignee: assignee
                    })
                });
                if (res.ok) {
                    await fetchTasks();
                }
            } catch (err) {
                console.error("Failed to update task assignee:", err);
            }
        }

        // --- KNOWLEDGE GRAPH RENDERER ---
        async function fetchGraphData() {
            try {
                let res = await fetch('/api/graph');
                let data = await res.json();
                
                canvas = document.getElementById('graphCanvas');
                if (!canvas) return;
                ctx = canvas.getContext('2d');
                
                // Adjust layout to fit container bounds
                const rect = canvas.parentNode.getBoundingClientRect();
                canvas.width = rect.width;
                canvas.height = 550; // force fixed rendering height
                
                const centerX = canvas.width / 2;
                const centerY = canvas.height / 2;
                
                // Position nodes
                graphNodes = data.nodes.map(n => {
                    const existing = graphNodes.find(ex => ex.id === n.id);
                    return {
                        ...n,
                        x: existing ? existing.x : centerX + (Math.random() - 0.5) * 350,
                        y: existing ? existing.y : centerY + (Math.random() - 0.5) * 250,
                        vx: 0,
                        vy: 0,
                        radius: n.type === 'task' ? NODE_RADIUS : NODE_RADIUS - 2
                    };
                });
                
                // Resolve links
                graphLinks = data.links.map(l => {
                    const source = graphNodes.find(n => n.id === l.source);
                    const target = graphNodes.find(n => n.id === l.target);
                    return { source, target };
                }).filter(l => l.source && l.target);
                
                if (!canvas.hasListeners) {
                    setupCanvasListeners();
                    canvas.hasListeners = true;
                }
                
                if (animationFrameId) cancelAnimationFrame(animationFrameId);
                animationFrameId = requestAnimationFrame(updatePhysicsLoop);
            } catch (err) {
                console.error("Error loading graph:", err);
            }
        }

        function setupCanvasListeners() {
            canvas.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                const mx = e.clientX - rect.left;
                const my = e.clientY - rect.top;
                
                if (isDragging && draggedNode) {
                    draggedNode.x = mx;
                    draggedNode.y = my;
                    return;
                }
                
                let foundHover = null;
                for (let n of graphNodes) {
                    const dist = Math.hypot(n.x - mx, n.y - my);
                    if (dist < n.radius + 6) {
                        foundHover = n;
                        break;
                    }
                }
                
                hoveredNode = foundHover;
                
                const tooltip = document.getElementById('graphTooltip');
                if (hoveredNode) {
                    canvas.style.cursor = isDragging ? 'grabbing' : 'grab';
                    tooltip.style.display = 'block';
                    tooltip.style.left = (mx + 15) + 'px';
                    tooltip.style.top = (my + 15) + 'px';
                    if (hoveredNode.type === 'task') {
                        tooltip.innerHTML = `<strong>TASK-${hoveredNode.rawId}</strong> (${hoveredNode.status.toUpperCase()})<br>${hoveredNode.label}`;
                    } else {
                        tooltip.innerHTML = `<strong>Doc:</strong> ${hoveredNode.label}<br>Path: @doc/${hoveredNode.path}`;
                    }
                } else {
                    canvas.style.cursor = 'default';
                    tooltip.style.display = 'none';
                }
            });
            
            canvas.addEventListener('mousedown', (e) => {
                if (hoveredNode) {
                    draggedNode = hoveredNode;
                    isDragging = true;
                    canvas.style.cursor = 'grabbing';
                }
            });
            
            window.addEventListener('mouseup', () => {
                isDragging = false;
                draggedNode = null;
                if (canvas) canvas.style.cursor = hoveredNode ? 'grab' : 'default';
            });
            
            canvas.addEventListener('dblclick', () => {
                if (hoveredNode) {
                    if (hoveredNode.type === 'task') {
                        switchTab('tasks');
                        openTaskModal(hoveredNode.rawId);
                    } else if (hoveredNode.type === 'doc') {
                        navigateToDoc(hoveredNode.path);
                    }
                }
            });
        }

        function updatePhysicsLoop() {
            if (!canvas || !ctx) return;
            
            const width = canvas.width;
            const height = canvas.height;
            const centerX = width / 2;
            const centerY = height / 2;
            
            // 1. Repel nodes
            for (let i = 0; i < graphNodes.length; i++) {
                const n1 = graphNodes[i];
                for (let j = i + 1; j < graphNodes.length; j++) {
                    const n2 = graphNodes[j];
                    const dx = n2.x - n1.x;
                    const dy = n2.y - n1.y;
                    const dist = Math.hypot(dx, dy) || 1;
                    
                    const force = REPULSION / (dist * dist);
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    
                    if (n1 !== draggedNode) {
                        n1.vx -= fx;
                        n1.vy -= fy;
                    }
                    if (n2 !== draggedNode) {
                        n2.vx += fx;
                        n2.vy += fy;
                    }
                }
            }
            
            // 2. Link attraction
            for (let link of graphLinks) {
                const n1 = link.source;
                const n2 = link.target;
                const dx = n2.x - n1.x;
                const dy = n2.y - n1.y;
                const dist = Math.hypot(dx, dy) || 1;
                
                const force = (dist - 120) * TENSION;
                const fx = (dx / dist) * force;
                const fy = (dy / dist) * force;
                
                if (n1 !== draggedNode) {
                    n1.vx += fx;
                    n1.vy += fy;
                }
                if (n2 !== draggedNode) {
                    n2.vx -= fx;
                    n2.vy -= fy;
                }
            }
            
            // 3. Center gravity & boundary checks
            for (let n of graphNodes) {
                if (n === draggedNode) continue;
                
                n.vx += (centerX - n.x) * CENTER_ATTRACTION;
                n.vy += (centerY - n.y) * CENTER_ATTRACTION;
                
                n.vx *= DAMPING;
                n.vy *= DAMPING;
                n.x += n.vx;
                n.y += n.vy;
                
                n.x = Math.max(n.radius + 15, Math.min(width - n.radius - 15, n.x));
                n.y = Math.max(n.radius + 15, Math.min(height - n.radius - 15, n.y));
            }
            
            // 4. Render
            ctx.clearRect(0, 0, width, height);
            
            // Draw connections
            ctx.lineWidth = 1.5;
            for (let link of graphLinks) {
                const isHighlighted = hoveredNode && (link.source === hoveredNode || link.target === hoveredNode);
                ctx.strokeStyle = isHighlighted ? 'rgba(99, 102, 241, 0.8)' : 'rgba(255, 255, 255, 0.08)';
                ctx.beginPath();
                ctx.moveTo(link.source.x, link.source.y);
                ctx.lineTo(link.target.x, link.target.y);
                ctx.stroke();
            }
            
            // Draw circles
            for (let n of graphNodes) {
                const isHovered = n === hoveredNode;
                const isLinked = hoveredNode && graphLinks.some(l => 
                    (l.source === n && l.target === hoveredNode) || (l.target === n && l.source === hoveredNode)
                );
                
                ctx.shadowBlur = (isHovered || isLinked) ? 15 : 0;
                
                if (n.type === 'task') {
                    ctx.fillStyle = '#6366f1';
                    ctx.shadowColor = '#6366f1';
                } else {
                    ctx.fillStyle = '#10b981';
                    ctx.shadowColor = '#10b981';
                }
                
                ctx.beginPath();
                ctx.arc(n.x, n.y, n.radius + (isHovered ? 2 : 0), 0, Math.PI * 2);
                ctx.fill();
                
                ctx.strokeStyle = isHovered ? '#ffffff' : 'rgba(255, 255, 255, 0.2)';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Labels
                ctx.shadowBlur = 0;
                ctx.fillStyle = (isHovered || isLinked) ? '#ffffff' : 'rgba(255, 255, 255, 0.7)';
                ctx.font = isHovered ? 'bold 11px Outfit, sans-serif' : '10px Outfit, sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                
                const text = n.type === 'task' ? `TASK-${n.rawId}` : n.label;
                ctx.fillText(text, n.x, n.y + n.radius + 6);
            }
            
            animationFrameId = requestAnimationFrame(updatePhysicsLoop);
        }

        // --- FETCHERS ---
        async function fetchStatus() {
            try {
                let res = await fetch('/api/status');
                currentStatus = await res.json();
                renderDashboard();
            } catch (err) {
                console.error("Error fetching project status:", err);
            }
        }

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

        // --- ACTIONS ---
        async function triggerSync() {
            try {
                let res = await fetch('/api/sync', { method: 'POST' });
                if (res.ok) {
                    alert('Sync completed successfully!');
                    fetchStatus();
                } else {
                    let err = await res.json();
                    alert('Sync failed: ' + err.error);
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function runValidation() {
            try {
                let res = await fetch('/api/validate', { method: 'POST' });
                let data = await res.json();
                if (data.isHealthy) {
                    alert('All references and links are perfectly healthy!');
                } else {
                    alert(`Found ${data.errors} broken link reference(s). Inspect files using CLI 'aim validate'.`);
                }
                fetchStatus();
            } catch (err) {
                console.error(err);
            }
        }

        async function startTimerFromModal(taskId) {
            try {
                let res = await fetch('/api/time/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: taskId })
                });
                if (res.ok) {
                    await fetchStatus();
                    await fetchTasks();
                    openTaskModal(taskId); // refresh modal
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function stopTimerFromModal(taskId) {
            try {
                let res = await fetch('/api/time/stop', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ note: 'Stopped from browser modal' })
                });
                if (res.ok) {
                    await fetchStatus();
                    await fetchTasks();
                    openTaskModal(taskId); // refresh modal
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function stopTimerFromDashboard() {
            try {
                let res = await fetch('/api/time/stop', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ note: 'Stopped from dashboard widget' })
                });
                if (res.ok) {
                    fetchStatus();
                }
            } catch (err) {
                console.error(err);
            }
        }

        // --- RENDERERS ---
        function renderDashboard() {
            if (!currentStatus) return;

            // 1. Project info
            document.getElementById('projectRootDisplay').textContent = currentStatus.projectRoot;
            
            // Render tech stack tags
            const stackContainer = document.getElementById('techStackContainer');
            stackContainer.innerHTML = '';
            if (currentStatus.techStack && currentStatus.techStack.length > 0) {
                currentStatus.techStack.forEach(st => {
                    const span = document.createElement('span');
                    span.className = 'stack-tag';
                    span.textContent = st;
                    stackContainer.appendChild(span);
                });
            } else {
                stackContainer.innerHTML = '<span class="stack-tag">Standard Project</span>';
            }

            // 2. Task metrics
            const t = currentStatus.tasks;
            const completionPct = t.total > 0 ? Math.round((t.done / t.total) * 100) : 0;
            document.getElementById('taskCompletionPct').textContent = completionPct + '%';
            document.getElementById('taskCompletionRatio').textContent = `${t.done} of ${t.total} tasks completed`;
            document.getElementById('taskProgressBar').style.width = completionPct + '%';

            // 3. Time tracker & active timer
            document.getElementById('totalTimeSpentText').textContent = currentStatus.formattedTotalTime;
            
            const dotEl = document.getElementById('trackerStatusDot');
            const activeTextEl = document.getElementById('activeTaskText');
            const liveCounterEl = document.getElementById('trackerLiveTimerText');
            const stopBtn = document.getElementById('btnStopTimer');

            if (currentStatus.activeTimer) {
                dotEl.className = 'tracker-status-dot active';
                activeTextEl.textContent = `Tracking: TASK-${currentStatus.activeTimer.taskId} - ${currentStatus.activeTimer.title}`;
                liveCounterEl.style.display = 'block';
                stopBtn.style.display = 'block';
                
                // Start local ticking
                localTimerStartEpoch = currentStatus.activeTimer.startedAt;
                if (localTimerInterval) clearInterval(localTimerInterval);
                updateLiveCounter();
                localTimerInterval = setInterval(updateLiveCounter, 1000);
            } else {
                dotEl.className = 'tracker-status-dot';
                activeTextEl.textContent = 'No active timer running';
                liveCounterEl.style.display = 'none';
                stopBtn.style.display = 'none';
                if (localTimerInterval) {
                    clearInterval(localTimerInterval);
                    localTimerInterval = null;
                }
            }

            // 4. Counts
            document.getElementById('docsCountText').textContent = currentStatus.docsCount;
            document.getElementById('memoriesCountText').textContent = currentStatus.memoriesCount;

            // 5. System Health Badges
            const syncBadge = document.getElementById('syncStatusBadge');
            if (currentStatus.sync.allSynced) {
                syncBadge.textContent = 'Synced';
                syncBadge.className = 'health-val-badge badge-success';
            } else {
                syncBadge.textContent = 'Dirty / Out of Sync';
                syncBadge.className = 'health-val-badge badge-warning';
            }

            const healthBadge = document.getElementById('refHealthBadge');
            if (currentStatus.health.isHealthy) {
                healthBadge.textContent = 'Healthy (0 broken links)';
                healthBadge.className = 'health-val-badge badge-success';
            } else {
                healthBadge.textContent = `${currentStatus.health.errors} Broken Link(s)`;
                healthBadge.className = 'health-val-badge badge-danger';
            }

            // 6. Recent Logs
            const logsContainer = document.getElementById('recentTimeLogsContainer');
            logsContainer.innerHTML = '';
            if (currentStatus.recentLogs && currentStatus.recentLogs.length > 0) {
                const logsCopy = [...currentStatus.recentLogs].reverse();
                logsCopy.forEach(log => {
                    const item = document.createElement('div');
                    item.className = 'timeline-item';
                    
                    const timeFormatted = formatSeconds(log.duration);
                    const endedDate = new Date(log.endedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' ' + new Date(log.endedAt).toLocaleDateString();
                    
                    item.innerHTML = `
                        <div class="timeline-header">
                            <span class="timeline-title">TASK-${log.taskId} duration: ${timeFormatted}</span>
                            <span>${endedDate}</span>
                        </div>
                        <div class="timeline-body">${log.note || 'No note provided'}</div>
                    `;
                    logsContainer.appendChild(item);
                });
            } else {
                logsContainer.innerHTML = '<div style="color:var(--text-muted);font-size:0.88rem;text-align:center;padding:1.5rem 0;">No time logs captured yet.</div>';
            }

            // 7. Sync files checklist
            const syncFilesContainer = document.getElementById('syncFilesContainer');
            syncFilesContainer.innerHTML = '';
            if (currentStatus.sync.files) {
                Object.keys(currentStatus.sync.files).forEach(filename => {
                    const statusVal = currentStatus.sync.files[filename];
                    const item = document.createElement('div');
                    item.className = 'sync-file-item';
                    
                    const badgeClass = statusVal === 'OK' ? 'badge-success' : 'badge-warning';
                    item.innerHTML = `
                        <span class="sync-filename">${filename}</span>
                        <span class="health-val-badge ${badgeClass}">${statusVal}</span>
                    `;
                    syncFilesContainer.appendChild(item);
                });
            }

            // 8. Recent Memories
            const recentMemsContainer = document.getElementById('recentMemoriesContainer');
            recentMemsContainer.innerHTML = '';
            if (currentStatus.recentMemories && currentStatus.recentMemories.length > 0) {
                const memsCopy = [...currentStatus.recentMemories].reverse();
                memsCopy.forEach(mem => {
                    const div = document.createElement('div');
                    div.className = 'recent-memory-item';
                    div.innerHTML = `
                        <div class="recent-memory-meta">
                            <span>${mem.category}</span>
                            <span>${mem.layer}</span>
                        </div>
                        <div style="color:#ffffff;">${mem.content}</div>
                    `;
                    recentMemsContainer.appendChild(div);
                });
            } else {
                recentMemsContainer.innerHTML = '<div style="color:var(--text-muted);font-size:0.88rem;text-align:center;padding:1.5rem 0;">No decisions recorded yet.</div>';
            }
        }

        function updateLiveCounter() {
            if (!localTimerStartEpoch) return;
            const elapsed = Math.floor(Date.now() / 1000 - localTimerStartEpoch);
            const hrs = Math.floor(elapsed / 3600);
            const mins = Math.floor((elapsed % 3600) / 60);
            const secs = elapsed % 60;
            
            const displayStr = [
                hrs.toString().padStart(2, '0'),
                mins.toString().padStart(2, '0'),
                secs.toString().padStart(2, '0')
            ].join(':');
            
            document.getElementById('trackerLiveTimerText').textContent = displayStr;
        }

        function formatSeconds(totalSeconds) {
            const hrs = Math.floor(totalSeconds / 3600);
            const mins = Math.floor((totalSeconds % 3600) / 60);
            const secs = totalSeconds % 60;
            
            if (hrs > 0) return `${hrs}h ${mins}m ${secs}s`;
            if (mins > 0) return `${mins}m ${secs}s`;
            return `${secs}s`;
        }

        function renderKanban() {
            const cols = ['todo', 'in-progress', 'in-review', 'done'];
            cols.forEach(col => {
                const container = document.getElementById('col-' + col);
                container.querySelectorAll('.task-card').forEach(card => card.remove());
                document.getElementById('count-' + col).textContent = '0';
            });

            const counts = {todo: 0, 'in-progress': 0, 'in-review': 0, done: 0};

            currentTasks.forEach(task => {
                let status = task.status.toLowerCase();
                if (!cols.includes(status)) status = 'todo';
                
                counts[status]++;
                
                const card = document.createElement('div');
                card.className = 'task-card';
                card.setAttribute('draggable', 'true');
                card.onclick = () => openTaskModal(task.id);
                card.ondragstart = (e) => {
                    e.dataTransfer.setData('text/plain', task.id);
                    card.classList.add('dragging');
                };
                card.ondragend = () => {
                    card.classList.remove('dragging');
                };
                
                const checkedCount = task.ac.filter(item => item.checked).length;
                const progressPct = task.ac.length ? Math.round((checkedCount / task.ac.length) * 100) : 0;
                const priClass = 'pri-' + (task.priority || 'medium').toLowerCase();
                
                let labelsHtml = '';
                if (task.labels && task.labels.length > 0) {
                    labelsHtml = `<div style="display:flex; flex-wrap:wrap; gap:0.25rem; margin-top:0.25rem;">` + 
                        task.labels.map(l => `<span style="font-size:0.68rem; padding:0.05rem 0.35rem; background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.18); color:#a5b4fc; border-radius:4px;">${l}</span>`).join('') +
                        `</div>`;
                }

                let parentHtml = task.parent ? `<div style="font-size:0.72rem; color:var(--text-muted); margin-bottom:0.2rem; display:flex; align-items:center; gap:0.2rem;"><span>↱</span> <span style="font-family:monospace; font-weight:bold; color:#a5b4fc;">TASK-${task.parent}</span></div>` : '';
                
                const subtasks = currentTasks.filter(t => t.parent === task.id);
                const doneSubtasks = subtasks.filter(t => t.status.toLowerCase() === 'done').length;
                let subtaskCountHtml = subtasks.length > 0 ? `<div style="font-size:0.72rem; color:var(--text-muted); margin-top:0.2rem; display:flex; align-items:center; gap:0.25rem;"><span>↳ Subtasks:</span> <span style="font-weight:bold; color:#10b981;">${doneSubtasks}/${subtasks.length}</span></div>` : '';

                card.innerHTML = `
                    ${parentHtml}
                    <div class="task-header">
                        <span class="task-id">TASK-${task.id}</span>
                        <span class="task-priority ${priClass}">${task.priority}</span>
                    </div>
                    <div class="task-title">${task.title}</div>
                    ${labelsHtml}
                    ${subtaskCountHtml}
                    <div class="task-meta">
                        <span>👤 ${task.assignee || 'unassigned'}</span>
                        <div style="display:flex; align-items:center; gap:0.35rem;">
                            <span style="font-size:0.75rem;">${progressPct}%</span>
                            <div class="task-progress">
                                <div class="task-progress-bar" style="width: ${progressPct}%"></div>
                            </div>
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
                container.innerHTML = '<div style="color:var(--text-muted); padding:2rem 0;">No memories recorded yet. Add one on the right!</div>';
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
        async function openTaskModal(taskId) {
            let task = currentTasks.find(t => t.id === taskId);
            if (!task) {
                await fetchTasks();
                task = currentTasks.find(t => t.id === taskId);
            }
            if (!task) return;
            
            activeTaskId = taskId;
            document.getElementById('modalTaskId').textContent = `TASK-${task.id}`;
            document.getElementById('modalTaskTitleInput').value = task.title;
            document.getElementById('modalTaskDescInput').value = task.description || '';
            document.getElementById('modalTaskStatusSelect').value = task.status;
            
            // Spec & Plan inputs
            document.getElementById('modalTaskSpecInput').value = task.spec || '';
            document.getElementById('modalTaskPlanInput').value = task.plan || '';
            
            const priSelect = document.getElementById('modalTaskPrioritySelect');
            if (priSelect) {
                priSelect.value = (task.priority || 'medium').toLowerCase();
            }
            
            await fetchUsersDropdownList();
            document.getElementById('modalTaskAssigneeSelect').value = task.assignee || 'unassigned';

            // Fill Parent Selector
            const parentSelect = document.getElementById('modalTaskParentSelect');
            if (parentSelect) {
                parentSelect.innerHTML = '<option value="">None (Root Task)</option>';
                currentTasks.forEach(t => {
                    if (t.id !== taskId) {
                        const opt = document.createElement('option');
                        opt.value = t.id;
                        opt.textContent = `TASK-${t.id}: ${t.title}`;
                        parentSelect.appendChild(opt);
                    }
                });
                parentSelect.value = task.parent || '';
            }

            // Fill Subtasks list
            const subtasksContainer = document.getElementById('modalTaskSubtasksContainer');
            if (subtasksContainer) {
                subtasksContainer.innerHTML = '';
                const subtasks = currentTasks.filter(t => t.parent === taskId);
                if (subtasks.length === 0) {
                    subtasksContainer.innerHTML = '<div style="color:var(--text-muted); font-size:0.8rem; padding: 0.25rem 0;">No subtasks.</div>';
                } else {
                    subtasks.forEach(sub => {
                        const subDiv = document.createElement('div');
                        subDiv.className = 'sync-file-item';
                        subDiv.style.padding = '0.35rem 0.65rem';
                        subDiv.style.cursor = 'pointer';
                        subDiv.style.fontSize = '0.82rem';
                        
                        const statusBadge = `<span class="health-val-badge ${sub.status === 'done' ? 'badge-success' : 'badge-warning'}" style="font-size:0.7rem; padding:0.05rem 0.35rem;">${sub.status}</span>`;
                        
                        subDiv.innerHTML = `
                            <span style="font-weight:600; color:#a5b4fc;">TASK-${sub.id}</span>
                            <span style="flex:1; margin-left:0.5rem; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">${sub.title}</span>
                            ${statusBadge}
                        `;
                        subDiv.onclick = () => {
                            openTaskModal(sub.id);
                        };
                        subtasksContainer.appendChild(subDiv);
                    });
                }
            }

            // Fill Labels tags
            const labelsContainer = document.getElementById('modalTaskLabelsContainer');
            if (labelsContainer) {
                labelsContainer.innerHTML = '';
                const labels = task.labels || [];
                if (labels.length === 0) {
                    labelsContainer.innerHTML = '<span style="color:var(--text-muted); font-size:0.82rem; font-style:italic;">No labels.</span>';
                } else {
                    labels.forEach(l => {
                        const badge = document.createElement('span');
                        badge.className = 'badge';
                        badge.style.display = 'flex';
                        badge.style.alignItems = 'center';
                        badge.style.gap = '0.25rem';
                        badge.style.fontSize = '0.75rem';
                        badge.style.padding = '0.15rem 0.45rem';
                        badge.style.background = 'rgba(99, 102, 241, 0.12)';
                        badge.style.borderColor = 'rgba(99, 102, 241, 0.25)';
                        badge.style.color = '#c7d2fe';
                        
                        badge.innerHTML = `
                            <span>${l}</span>
                            <span style="cursor:pointer; opacity:0.6; font-weight:bold; font-size:0.75rem;" onclick="event.stopPropagation(); removeTaskLabel('${l}')">&times;</span>
                        `;
                        labelsContainer.appendChild(badge);
                    });
                }
            }

            // Active Timer Banner Inside Modal
            const timerContainer = document.getElementById('modalTaskTimerContainer');
            timerContainer.innerHTML = '';
            
            const activeTimer = currentStatus ? currentStatus.activeTimer : null;
            if (activeTimer && activeTimer.taskId === taskId) {
                timerContainer.innerHTML = `
                    <div class="modal-timer-banner" style="border-color:var(--danger); background:rgba(239,68,68,0.08); margin-bottom: 1rem;">
                        <div class="timer-active-badge" style="color:var(--danger);">
                            <span class="tracker-status-dot active"></span>
                            <span>Tracking this task in progress...</span>
                        </div>
                        <button class="btn btn-danger btn-sm" onclick="stopTimerFromModal(${task.id})">Stop Timer</button>
                    </div>
                `;
            } else if (activeTimer) {
                timerContainer.innerHTML = `
                    <div class="modal-timer-banner" style="border-color:var(--warning); background:rgba(245,158,11,0.08); margin-bottom: 1rem;">
                        <div class="timer-active-badge" style="color:var(--warning);">
                            <span>Timer is running on TASK-${activeTimer.taskId}</span>
                        </div>
                    </div>
                `;
            } else {
                timerContainer.innerHTML = `
                    <div class="modal-timer-banner" style="margin-bottom: 1rem;">
                        <div class="timer-active-badge">
                            <span>No time tracking active</span>
                        </div>
                        <button class="btn btn-primary btn-sm" onclick="startTimerFromModal(${task.id})">Start Timer</button>
                    </div>
                `;
            }
            
            const acContainer = document.getElementById('modalTaskAcContainer');
            acContainer.innerHTML = '';
            
            if (task.ac.length === 0) {
                acContainer.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem;">No acceptance criteria configured.</div>';
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

        async function saveTaskEdit(extraPayload) {
            if (!activeTaskId) return;
            try {
                let res = await fetch('/api/tasks/edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: activeTaskId,
                        ...extraPayload
                    })
                });
                if (res.ok) {
                    await fetchTasks();
                    openTaskModal(activeTaskId);
                }
            } catch (err) {
                console.error("Failed to save task edit:", err);
            }
        }

        async function deleteActiveTask() {
            if (!activeTaskId) return;
            if (!confirm(`Are you sure you want to delete TASK-${activeTaskId}?`)) return;
            try {
                let res = await fetch('/api/tasks/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: activeTaskId })
                });
                if (res.ok) {
                    closeTaskModal(null);
                    await fetchTasks();
                    await fetchStatus();
                } else {
                    const data = await res.json();
                    alert("Error: " + (data.error || "Failed to delete task"));
                }
            } catch (err) {
                console.error("Failed to delete task:", err);
                alert("Failed to delete task.");
            }
        }

        async function updateTaskPriority() {
            if (!activeTaskId) return;
            const pri = document.getElementById('modalTaskPrioritySelect').value;
            await saveTaskEdit({ priority: pri });
        }

        function openCreateTaskModal() {
            document.getElementById('createTaskTitleInput').value = '';
            document.getElementById('createTaskDescInput').value = '';
            document.getElementById('createTaskStatusSelect').value = 'todo';
            document.getElementById('createTaskPrioritySelect').value = 'medium';
            document.getElementById('createTaskLabelsInput').value = '';
            
            fetchUsersDropdownList();
            document.getElementById('createTaskModalOverlay').style.display = 'flex';
        }

        function closeCreateTaskModal(e) {
            const overlay = document.getElementById('createTaskModalOverlay');
            if (overlay) {
                if (e === null || e.target === overlay || e.target.classList.contains('modal-close') || e.target.textContent === 'Cancel') {
                    overlay.style.display = 'none';
                }
            }
        }

        async function submitCreateTask() {
            const title = document.getElementById('createTaskTitleInput').value.trim();
            if (!title) {
                alert("Task Title is required!");
                return;
            }
            const desc = document.getElementById('createTaskDescInput').value.trim();
            const status = document.getElementById('createTaskStatusSelect').value;
            const priority = document.getElementById('createTaskPrioritySelect').value;
            const assignee = document.getElementById('createTaskAssigneeSelect').value;
            const labelsStr = document.getElementById('createTaskLabelsInput').value.trim();
            const labels = labelsStr ? labelsStr.split(',').map(l => l.trim().toLowerCase()).filter(l => l) : [];

            try {
                let res = await fetch('/api/tasks/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title,
                        description: desc,
                        status,
                        priority,
                        assignee,
                        labels
                    })
                });
                if (res.ok) {
                    document.getElementById('createTaskModalOverlay').style.display = 'none';
                    await fetchTasks();
                    await fetchStatus();
                } else {
                    const data = await res.json();
                    alert("Error: " + (data.error || "Failed to create task"));
                }
            } catch (err) {
                console.error("Failed to create task:", err);
                alert("Failed to create task.");
            }
        }

        async function updateTaskTitle() {
            const newTitle = document.getElementById('modalTaskTitleInput').value.trim();
            if (!newTitle) return;
            await saveTaskEdit({ title: newTitle });
        }

        async function updateTaskDescription() {
            const newDesc = document.getElementById('modalTaskDescInput').value.trim();
            await saveTaskEdit({ description: newDesc });
        }

        async function updateTaskStatus() {
            const newStatus = document.getElementById('modalTaskStatusSelect').value;
            await saveTaskEdit({ status: newStatus });
        }

        async function updateTaskSpec() {
            const spec = document.getElementById('modalTaskSpecInput').value.trim();
            await saveTaskEdit({ spec: spec });
        }

        async function updateTaskPlan() {
            const plan = document.getElementById('modalTaskPlanInput').value.trim();
            await saveTaskEdit({ plan: plan });
        }

        async function updateTaskParent() {
            const parent = document.getElementById('modalTaskParentSelect').value;
            await saveTaskEdit({ parent: parent ? parseInt(parent) : null });
        }

        async function addTaskLabel() {
            const input = document.getElementById('modalTaskNewLabelInput');
            const label = input.value.trim().toLowerCase();
            if (!label) return;
            
            const task = currentTasks.find(t => t.id === activeTaskId);
            if (!task) return;
            
            const labels = [...(task.labels || [])];
            if (!labels.includes(label)) {
                labels.push(label);
                await saveTaskEdit({ labels });
                input.value = '';
            }
        }

        async function removeTaskLabel(label) {
            const task = currentTasks.find(t => t.id === activeTaskId);
            if (!task) return;
            
            const labels = (task.labels || []).filter(l => l !== label);
            await saveTaskEdit({ labels });
        }

        async function addTaskAc() {
            const input = document.getElementById('modalTaskNewAcInput');
            const text = input.value.trim();
            if (!text) return;
            
            try {
                let res = await fetch('/api/tasks/edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: activeTaskId,
                        add_ac: text
                    })
                });
                if (res.ok) {
                    input.value = '';
                    await fetchTasks();
                    openTaskModal(activeTaskId);
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function quickAddSubtask() {
            const input = document.getElementById('modalTaskNewSubtaskInput');
            const title = input.value.trim();
            if (!title) return;
            
            try {
                let res = await fetch('/api/tasks/create_subtask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        parent_id: activeTaskId,
                        title: title
                    })
                });
                if (res.ok) {
                    input.value = '';
                    await fetchTasks();
                    openTaskModal(activeTaskId);
                } else {
                    let err = await res.json();
                    alert('Failed to add subtask: ' + err.error);
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
        window.onload = async () => {
            await fetchProjectRoot();
            await fetchStatus();
            // Pre-load tasks in background
            await fetchTasks();

            // Set up Kanban Column drag & drop listeners
            const cols = ['todo', 'in-progress', 'in-review', 'done'];
            cols.forEach(col => {
                const container = document.getElementById('col-' + col);
                if (container) {
                    container.ondragover = (e) => {
                        e.preventDefault();
                        container.classList.add('drag-over');
                    };
                    container.ondragleave = () => {
                        container.classList.remove('drag-over');
                    };
                    container.ondrop = async (e) => {
                        e.preventDefault();
                        container.classList.remove('drag-over');
                        const taskId = e.dataTransfer.getData('text/plain');
                        if (taskId) {
                            const task = currentTasks.find(t => t.id == taskId);
                            if (task && task.status.toLowerCase() !== col) {
                                // Optimistically update and render
                                task.status = col;
                                renderKanban();
                                try {
                                    await fetch('/api/tasks/edit', {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'application/json' },
                                        body: JSON.stringify({ id: parseInt(taskId), status: col })
                                    });
                                    await fetchTasks();
                                    await fetchStatus();
                                } catch (err) {
                                    console.error("Failed to update status via drag-drop:", err);
                                }
                            }
                        }
                    };
                }
            });
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
        parsed_url = urllib.parse.urlparse(self.path)
        
        # 1. Serves SPA Frontend
        if parsed_url.path == "/" or parsed_url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
            return
            
        # 2. API Root
        elif parsed_url.path == "/api/root":
            self.send_json({"root": get_project_root()})
            return

        # 2.5. API Status (Overview metrics and system health)
        elif parsed_url.path == "/api/status":
            try:
                from aim.aim_cli import CONFIG_PATH, TIMER_STATE_PATH, TIME_LOG_PATH, format_duration
            except ImportError:
                from aim_cli import CONFIG_PATH, TIMER_STATE_PATH, TIME_LOG_PATH, format_duration
            
            project_root = get_project_root()
            
            # Project info
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
            
            # Task stats
            tasks = []
            if os.path.exists(TASKS_DIR):
                for filename in os.listdir(TASKS_DIR):
                    if filename.startswith("task-") and filename.endswith(".md"):
                        try:
                            t = parse_task_file(os.path.join(TASKS_DIR, filename))
                            tasks.append(t)
                        except:
                            pass
            
            counts = {"todo": 0, "in-progress": 0, "in-review": 0, "done": 0}
            for t in tasks:
                st = t.get("status", "todo").lower()
                if st in counts:
                    counts[st] += 1
                else:
                    counts[st] = counts.get(st, 0) + 1
            
            # Docs count
            doc_count = 0
            if os.path.exists(DOCS_DIR):
                for root, dirs, files in os.walk(DOCS_DIR):
                    for file in files:
                        if file.endswith(".md"):
                            doc_count += 1
            
            # Memories
            memories = []
            if os.path.exists(MEMORIES_PATH):
                try:
                    with open(MEMORIES_PATH, "r", encoding="utf-8") as f:
                        memories = json.load(f)
                except:
                    pass
            
            # Time tracking & active timer
            total_duration = 0
            logs = []
            if os.path.exists(TIME_LOG_PATH):
                try:
                    with open(TIME_LOG_PATH, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                        total_duration = sum(l.get("duration", 0) for l in logs)
                except:
                    pass
            
            active_timer = None
            if os.path.exists(TIMER_STATE_PATH):
                try:
                    with open(TIMER_STATE_PATH, "r", encoding="utf-8") as f:
                        timer_state = json.load(f)
                        elapsed = int(time.time() - timer_state["startedAt"])
                        active_timer = {
                            "taskId": timer_state["taskId"],
                            "title": timer_state["title"],
                            "startedAt": timer_state["startedAt"],
                            "elapsed": elapsed,
                            "formattedElapsed": format_duration(elapsed)
                        }
                except:
                    pass
            
            # Sync status
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
                full_p = os.path.join(project_root, rel_path)
                exists = os.path.exists(full_p)
                sync_statuses[label] = "OK" if exists else "Missing"
                if not exists:
                    all_synced = False
            
            # Check reference health
            errors = 0
            task_ids = {t["id"] for t in tasks}
            doc_paths = set()
            if os.path.exists(DOCS_DIR):
                for root, dirs, files in os.walk(DOCS_DIR):
                    for file in files:
                        if file.endswith(".md"):
                            rel = os.path.relpath(os.path.join(root, file), DOCS_DIR).replace("\\", "/")
                            doc_paths.add(rel)
            
            def check_content(content):
                nonlocal errors
                for ref in re.findall(r"@task-(\d+)", content):
                    if int(ref) not in task_ids:
                        errors += 1
                for ref in re.findall(r"@doc/([\w\-/]+\.md|[\w\-/\s]+)", content):
                    clean_ref = ref.strip()
                    if not clean_ref.endswith(".md"):
                        clean_ref += ".md"
                    if clean_ref not in doc_paths:
                        errors += 1
            
            if os.path.exists(TASKS_DIR):
                for filename in os.listdir(TASKS_DIR):
                    if filename.endswith(".md"):
                        try:
                            with open(os.path.join(TASKS_DIR, filename), "r", encoding="utf-8") as f:
                                check_content(f.read())
                        except:
                            pass
            if os.path.exists(DOCS_DIR):
                for root, dirs, files in os.walk(DOCS_DIR):
                    for file in files:
                        if file.endswith(".md"):
                            try:
                                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                                    check_content(f.read())
                            except:
                                pass
            
            status_payload = {
                "projectName": project_name,
                "techStack": tech_stack,
                "projectRoot": project_root,
                "tasks": {
                    "total": len(tasks),
                    "todo": counts["todo"],
                    "inProgress": counts["in-progress"],
                    "inReview": counts["in-review"],
                    "done": counts["done"]
                },
                "docsCount": doc_count,
                "memoriesCount": len(memories),
                "totalTimeSpent": total_duration,
                "formattedTotalTime": format_duration(total_duration),
                "activeTimer": active_timer,
                "sync": {
                    "allSynced": all_synced,
                    "files": sync_statuses
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
        elif parsed_url.path == "/api/docs":
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
        elif parsed_url.path == "/api/memories":
            memories = []
            if os.path.exists(MEMORIES_PATH):
                try:
                    with open(MEMORIES_PATH, "r", encoding="utf-8") as f:
                        memories = json.load(f)
                except Exception as e:
                    print(f"[-] Error reading memories file: {e}")
            self.send_json(memories)
            return

        # 5.1. List Users API
        elif parsed_url.path == "/api/users":
            self.send_json(load_users())
            return
        elif parsed_url.path == "/api/search":
            query_params = urllib.parse.parse_qs(parsed_url.query)
            query = query_params.get("q", [""])[0].lower().strip()
            
            results = []
            if not query:
                self.send_json(results)
                return
                
            # Search Tasks
            if os.path.exists(TASKS_DIR):
                for filename in os.listdir(TASKS_DIR):
                    if filename.endswith(".md"):
                        path = os.path.join(TASKS_DIR, filename)
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                content = f.read()
                            if query in content.lower():
                                meta = parse_task_file(path)
                                matches = re.findall(f"(?i).{{0,40}}{re.escape(query)}.{{0,40}}", content)
                                snippet = " | ".join(matches[:2])
                                results.append({
                                    "type": "task",
                                    "id": meta["id"],
                                    "ref": f"@task-{meta['id']}",
                                    "title": meta["title"],
                                    "snippet": snippet
                                })
                        except Exception as e:
                            import traceback
                            traceback.print_exc()
                            
            # Search Docs
            if os.path.exists(DOCS_DIR):
                for root, dirs, files in os.walk(DOCS_DIR):
                    for file in files:
                        if file.endswith(".md"):
                            path = os.path.join(root, file)
                            rel = os.path.relpath(path, DOCS_DIR).replace("\\", "/")
                            try:
                                with open(path, "r", encoding="utf-8") as f:
                                    content = f.read()
                                if query in content.lower():
                                    title = file.replace(".md", "").replace("-", " ").title()
                                    for line in content.split("\n"):
                                        if line.startswith("# "):
                                            title = line.replace("# ", "").strip()
                                            break
                                    matches = re.findall(f"(?i).{{0,40}}{re.escape(query)}.{{0,40}}", content)
                                    snippet = " | ".join(matches[:2])
                                    results.append({
                                        "type": "doc",
                                        "path": rel,
                                        "ref": f"@doc/{rel}",
                                        "title": title,
                                        "snippet": snippet
                                    })
                            except Exception as e:
                                import traceback
                                traceback.print_exc()
                                
            # Search Memories
            if os.path.exists(MEMORIES_PATH):
                try:
                    with open(MEMORIES_PATH, "r", encoding="utf-8") as f:
                        mems = json.load(f)
                        for m in mems:
                            if query in m["content"].lower():
                                results.append({
                                    "type": "memory",
                                    "id": m["id"],
                                    "ref": f"Memory #{m['id']}",
                                    "title": f"Memory ({m['category']})",
                                    "snippet": m["content"]
                                })
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    
            self.send_json(results)
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
                        except:
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
                            except:
                                pass
                                
            # Add links from Tasks
            for node_id, content in tasks_data:
                task_refs = re.findall(r"@task-(\d+)", content)
                for ref in task_refs:
                    ref_id = int(ref)
                    if ref_id in existing_tasks:
                        links.append({"source": node_id, "target": f"task-{ref_id}"})
                doc_refs = re.findall(r"@doc/([\w\-/]+\.md|[\w\-/\s]+)", content)
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
                doc_refs = re.findall(r"@doc/([\w\-/]+\.md|[\w\-/\s]+)", content)
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
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            payload = json.loads(body) if body else {}
        except Exception as e:
            self.send_error(400, f"Malformed JSON: {e}")
            return

        try:
            from aim.aim_cli import CONFIG_PATH, TIMER_STATE_PATH, TIME_LOG_PATH
        except ImportError:
            from aim_cli import CONFIG_PATH, TIMER_STATE_PATH, TIME_LOG_PATH

        # 1. Edit Task Status / AC / Metadata
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
                    meta["parent"] = int(payload["parent"]) if payload["parent"] else None
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
                
            # Determine next ID
            existing_ids = []
            if os.path.exists(TASKS_DIR):
                for filename in os.listdir(TASKS_DIR):
                    m = re.match(r"task-(\d+)\.md", filename)
                    if m:
                        existing_ids.append(int(m.group(1)))
            next_id = max(existing_ids) + 1 if existing_ids else 1
            
            meta = {
                "id": next_id,
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
                write_task_file(meta)
                self.send_json({"success": True, "task": meta})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        # 1.6. Delete Task
        elif self.path == "/api/tasks/delete":
            task_id = payload.get("id")
            if not task_id:
                self.send_json({"error": "Missing task ID"}, 400)
                return
                
            task_path = os.path.join(TASKS_DIR, f"task-{task_id}.md")
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
                            except:
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
                
            # Determine next ID
            existing_ids = []
            if os.path.exists(TASKS_DIR):
                for filename in os.listdir(TASKS_DIR):
                    m = re.match(r"task-(\d+)\.md", filename)
                    if m:
                        existing_ids.append(int(m.group(1)))
            next_id = max(existing_ids) + 1 if existing_ids else 1
            
            meta = {
                "id": next_id,
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

        # 3. Start Timer
        elif self.path == "/api/time/start":
            task_id = payload.get("id")
            if not task_id:
                self.send_json({"error": "Missing task ID"}, 400)
                return
            
            task_path = os.path.join(TASKS_DIR, f"task-{task_id}.md")
            if not os.path.exists(task_path):
                self.send_json({"error": "Task not found"}, 404)
                return
            
            import time
            try:
                task = parse_task_file(task_path)
                timer_state = {
                    "taskId": task_id,
                    "title": task["title"],
                    "startedAt": time.time()
                }
                with open(TIMER_STATE_PATH, "w", encoding="utf-8") as f:
                    json.dump(timer_state, f)
                self.send_json({"success": True, "timer": timer_state})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        # 4. Stop Timer
        elif self.path == "/api/time/stop":
            import time
            if not os.path.exists(TIMER_STATE_PATH):
                self.send_json({"error": "No active timer"}, 400)
                return
            
            try:
                with open(TIMER_STATE_PATH, "r", encoding="utf-8") as f:
                    timer_state = json.load(f)
                
                task_id = timer_state["taskId"]
                duration = int(time.time() - timer_state["startedAt"])
                
                if os.path.exists(TIMER_STATE_PATH):
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
                
                import datetime
                entry = {
                    "id": f"te-{int(time.time()*1000)}",
                    "taskId": task_id,
                    "startedAt": datetime.datetime.fromtimestamp(timer_state["startedAt"]).isoformat(),
                    "endedAt": datetime.datetime.now().isoformat(),
                    "duration": duration,
                    "note": payload.get("note", "Stopped from Web UI")
                }
                logs.append(entry)
                with open(TIME_LOG_PATH, "w", encoding="utf-8") as f:
                    json.dump(logs, f, indent=2)
                
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
                tasks = []
                if os.path.exists(TASKS_DIR):
                    for filename in os.listdir(TASKS_DIR):
                        if filename.startswith("task-") and filename.endswith(".md"):
                            try:
                                tasks.append(parse_task_file(os.path.join(TASKS_DIR, filename)))
                            except:
                                pass
                task_ids = {t["id"] for t in tasks}
                doc_paths = set()
                if os.path.exists(DOCS_DIR):
                    for root, dirs, files in os.walk(DOCS_DIR):
                        for file in files:
                            if file.endswith(".md"):
                                rel = os.path.relpath(os.path.join(root, file), DOCS_DIR).replace("\\", "/")
                                doc_paths.add(rel)
                
                errors = 0
                def check_content(content):
                    nonlocal errors
                    for ref in re.findall(r"@task-(\d+)", content):
                        if int(ref) not in task_ids:
                            errors += 1
                    for ref in re.findall(r"@doc/([\w\-/]+\.md|[\w\-/\s]+)", content):
                        clean_ref = ref.strip()
                        if not clean_ref.endswith(".md"):
                            clean_ref += ".md"
                        if clean_ref not in doc_paths:
                            errors += 1
                
                if os.path.exists(TASKS_DIR):
                    for filename in os.listdir(TASKS_DIR):
                        if filename.endswith(".md"):
                            try:
                                with open(os.path.join(TASKS_DIR, filename), "r", encoding="utf-8") as f:
                                    check_content(f.read())
                            except:
                                pass
                if os.path.exists(DOCS_DIR):
                    for root, dirs, files in os.walk(DOCS_DIR):
                        for file in files:
                            if file.endswith(".md"):
                                try:
                                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                                        check_content(f.read())
                                except:
                                    pass
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
            if os.path.exists(TASKS_DIR):
                for filename in os.listdir(TASKS_DIR):
                    if filename.startswith("task-") and filename.endswith(".md"):
                        path = os.path.join(TASKS_DIR, filename)
                        try:
                            meta = parse_task_file(path)
                            if meta.get("assignee", "").strip().lower() == old_username:
                                meta["assignee"] = new_username
                                write_task_file(meta)
                        except Exception as e:
                            print(f"[-] Error propagating rename in server for {filename}: {e}")
                            
            self.send_json({"success": True, "users": users})

        else:
            self.send_error(404, "Not Found")

def start_server(port=6420, open_browser=True):
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
