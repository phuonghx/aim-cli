#!/usr/bin/env python3
"""Drive a headless browser over a URL and report basic health.

A small Playwright harness. The default mode loads the page, records its
title/status, runs a handful of sanity checks (does it have an H1, links,
images?), grabs rough load-timing numbers, and counts interactive
elements. Two extra modes are available:

    --screenshot   also save a full-page PNG to the OS temp directory
    --a11y         run a quick accessibility-oriented element count instead

Usage:
    python playwright_runner.py <url> [--screenshot] [--a11y]

Setup:
    pip install playwright && playwright install chromium

Screenshots land in a temp folder that the OS cleans up on its own.
"""

import json
import os
import sys
import tempfile
from datetime import datetime

# Unicode-safe console on legacy Windows terminals.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

# Playwright is optional; degrade gracefully when it isn't installed.
try:
    from playwright.sync_api import sync_playwright
    HAVE_PLAYWRIGHT = True
except ImportError:
    HAVE_PLAYWRIGHT = False

NAV_TIMEOUT_MS = 30000
VIEWPORT = {"width": 1280, "height": 720}
DESKTOP_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
SCREENSHOT_FOLDER = "webapp_testing_shots"


def _missing_playwright(with_fix: bool = True) -> dict:
    payload = {"error": "Playwright not installed"}
    if with_fix:
        payload["fix"] = "pip install playwright && playwright install chromium"
    return payload


def _timing(page, end_field: str) -> int:
    """Read a navigation-timing delta (ms) relative to navigationStart."""
    expr = (
        f"window.performance.timing.{end_field} "
        "- window.performance.timing.navigationStart"
    )
    return page.evaluate(expr)


def _save_screenshot(page) -> str:
    """Write a full-page screenshot into a temp folder and return its path."""
    folder = os.path.join(tempfile.gettempdir(), SCREENSHOT_FOLDER)
    os.makedirs(folder, exist_ok=True)
    filename = f"shot_{datetime.now():%Y%m%d_%H%M%S}.png"
    destination = os.path.join(folder, filename)
    page.screenshot(path=destination, full_page=True)
    return destination


def inspect_page(url: str, capture: bool = False) -> dict:
    """Load `url`, run health checks, and return a report dict."""
    if not HAVE_PLAYWRIGHT:
        return _missing_playwright()

    report = {"url": url, "timestamp": datetime.now().isoformat(), "status": "pending"}

    try:
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch(headless=True)
            context = browser.new_context(viewport=VIEWPORT, user_agent=DESKTOP_UA)
            page = context.new_page()

            response = page.goto(url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
            title = page.title()

            report["page"] = {
                "title": title,
                "url": page.url,
                "status_code": response.status if response else None,
            }

            loaded = bool(response and response.ok)
            report["health"] = {
                "loaded": loaded,
                "has_title": bool(title),
                "has_h1": page.locator("h1").count() > 0,
                "has_links": page.locator("a").count() > 0,
                "has_images": page.locator("img").count() > 0,
            }

            report["performance"] = {
                "dom_content_loaded": _timing(page, "domContentLoadedEventEnd"),
                "load_complete": _timing(page, "loadEventEnd"),
            }

            if capture:
                report["screenshot"] = _save_screenshot(page)
                report["screenshot_note"] = "Saved to temp directory (auto-cleaned by OS)"

            report["elements"] = {
                "links": page.locator("a").count(),
                "buttons": page.locator("button").count(),
                "inputs": page.locator("input").count(),
                "images": page.locator("img").count(),
                "forms": page.locator("form").count(),
            }

            browser.close()

            report["status"] = "success" if loaded else "failed"
            report["summary"] = (
                "[OK] Page loaded successfully" if loaded else "[X] Page failed to load"
            )

    except Exception as err:  # noqa: BLE001 - surface any browser failure verbatim
        report["status"] = "error"
        report["error"] = str(err)
        report["summary"] = f"[X] Error: {str(err)[:100]}"

    return report


def inspect_accessibility(url: str) -> dict:
    """Load `url` and count accessibility-relevant elements."""
    if not HAVE_PLAYWRIGHT:
        return _missing_playwright(with_fix=False)

    report = {"url": url, "accessibility": {}}

    try:
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)

            report["accessibility"] = {
                "images_with_alt": page.locator("img[alt]").count(),
                "images_without_alt": page.locator("img:not([alt])").count(),
                "buttons_with_label": page.locator("button[aria-label], button:has-text('')").count(),
                "links_with_text": page.locator("a:has-text('')").count(),
                "form_labels": page.locator("label").count(),
                "headings": {
                    "h1": page.locator("h1").count(),
                    "h2": page.locator("h2").count(),
                    "h3": page.locator("h3").count(),
                },
            }

            browser.close()
            report["status"] = "success"

    except Exception as err:  # noqa: BLE001
        report["status"] = "error"
        report["error"] = str(err)

    return report


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python playwright_runner.py <url> [--screenshot] [--a11y]",
            "examples": [
                "python playwright_runner.py https://example.com",
                "python playwright_runner.py https://example.com --screenshot",
                "python playwright_runner.py https://example.com --a11y",
            ],
        }, indent=2))
        sys.exit(1)

    url = sys.argv[1]
    flags = set(sys.argv[2:])

    if "--a11y" in flags:
        report = inspect_accessibility(url)
    else:
        report = inspect_page(url, capture="--screenshot" in flags)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
