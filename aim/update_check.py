"""\"A new release is available\" check for AIM.

Design goals (matches AIM's zero-dependency, agent-first philosophy):
- **Zero dependency**: uses only urllib from the stdlib.
- **Interactive only**: the check runs solely when stdout is a TTY, so pipes,
  CI, the MCP server, and agent invocations stay completely silent.
- **Throttled & cheap**: an interactive run hits the network at most once per
  day (short timeout); every other run reads the local cache instantly. The
  fetch is synchronous on purpose — a background thread gets killed when a fast
  command exits before it finishes, so the cache would never populate.
- **Never fails the command**: every network/parse/IO error is swallowed.
- **ASCII-only notice** on stderr, so it can't raise an encoding error.
- **Opt-out**: set AIM_NO_UPDATE_CHECK=1.

The comparison source is the GitHub Releases API (AIM publishes a release per
`v*` tag), so it works even though AIM is installed via `pip install git+...`.
"""
import json
import os
import sys
import time
import urllib.request

REPO = "phuonghx/aim-cli"
RELEASES_API = "https://api.github.com/repos/%s/releases/latest" % REPO
UPGRADE_CMD = "pip install --upgrade git+https://github.com/%s.git" % REPO
CHECK_INTERVAL = 24 * 3600  # only hit the network once per day
HTTP_TIMEOUT = 2.0


def _cache_path():
    return os.path.join(os.path.expanduser("~"), ".aim", "update_check.json")


def _read_cache():
    try:
        with open(_cache_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _write_cache(data):
    try:
        os.makedirs(os.path.dirname(_cache_path()), exist_ok=True)
        with open(_cache_path(), "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError:
        pass


def _parse_version(v):
    """'v1.9.0' / '1.9.0-rc1' -> (1, 9, 0). Stops at the first non-numeric
    chunk so pre-release suffixes don't break the comparison."""
    v = (v or "").strip().lstrip("vV")
    parts = []
    for chunk in v.split("."):
        num = ""
        for ch in chunk:
            if ch.isdigit():
                num += ch
            else:
                break
        if not num:
            break
        parts.append(int(num))
    return tuple(parts)


def release_is_newer(latest, current):
    """True when `latest` is a strictly higher version than `current`."""
    lp = _parse_version(latest)
    return bool(lp) and lp > _parse_version(current)


def format_notice(current_version, latest):
    """Return the upgrade notice string, or None when no update is warranted."""
    if not latest or not release_is_newer(latest, current_version):
        return None
    clean = latest.lstrip("vV")
    return (
        "\n[update] AIM %s is available (you have %s).\n"
        "         Update:  %s\n"
        "         or run:  aim upgrade\n"
        % (clean, current_version, UPGRADE_CMD)
    )


def _fetch_latest_tag():
    req = urllib.request.Request(
        RELEASES_API,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "aim-cli"},
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        data = json.load(resp)
    return data.get("tag_name") or data.get("name")


def _cache_is_stale(cache, now=None):
    now = time.time() if now is None else now
    last = cache.get("last_checked")
    return not last or (now - last) >= CHECK_INTERVAL


def get_latest_known(current_version=None, force=False):
    """Return the latest known release tag, refreshing the cache from the
    network when it is stale. Swallows all errors; returns None if unknown."""
    cache = _read_cache()
    if not force and not _cache_is_stale(cache):
        return cache.get("latest_known")
    latest = cache.get("latest_known")  # keep prior knowledge if the fetch fails
    try:
        fetched = _fetch_latest_tag()
        if fetched:
            latest = fetched
    except Exception:
        pass
    cache["last_checked"] = time.time()
    if latest:
        cache["latest_known"] = latest
    _write_cache(cache)
    return latest


def maybe_notify(current_version, command=None, stream=None):
    """Print a one-line upgrade notice to stderr when a newer release exists.
    Interactive terminals only; the network check is throttled to at most once
    per day. Never raises."""
    stream = stream or sys.stderr
    try:
        if os.environ.get("AIM_NO_UPDATE_CHECK"):
            return
        # No point nagging during these: mcp speaks a protocol on stdout,
        # upgrade just ran pip, and a bare invocation showed --help/usage.
        if command in (None, "mcp", "upgrade"):
            return
        if not sys.stdout.isatty():
            return
        # Synchronous + throttled (one network call per day max). Synchronous so
        # the cache reliably populates: a daemon thread would be killed when a
        # fast command exits before the fetch finished, so the notice would
        # never appear. Non-interactive runs never reach here (TTY gate above).
        notice = format_notice(current_version, get_latest_known(current_version))
        if notice:
            stream.write(notice)
    except Exception:
        pass
