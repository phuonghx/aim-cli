"""Tests for the non-blocking release-update check."""
import pytest

from aim import update_check as uc


@pytest.fixture
def cache_file(tmp_path, monkeypatch):
    path = tmp_path / "update_check.json"
    monkeypatch.setattr(uc, "_cache_path", lambda: str(path))
    return path


def test_parse_version():
    assert uc._parse_version("v1.9.0") == (1, 9, 0)
    assert uc._parse_version("1.10.2") == (1, 10, 2)
    assert uc._parse_version("v2.0.0-rc1") == (2, 0, 0)
    assert uc._parse_version("") == ()


def test_release_is_newer():
    assert uc.release_is_newer("v1.10.0", "1.9.0")
    assert uc.release_is_newer("2.0.0", "1.9.9")
    assert not uc.release_is_newer("1.9.0", "1.9.0")     # equal
    assert not uc.release_is_newer("1.8.0", "1.9.0")     # older
    assert not uc.release_is_newer("", "1.9.0")          # unknown


def test_format_notice():
    notice = uc.format_notice("1.9.0", "v1.10.0")
    assert notice is not None
    assert "1.10.0" in notice and "1.9.0" in notice
    assert "aim upgrade" in notice
    assert uc.format_notice("1.9.0", "1.9.0") is None    # not newer -> no notice
    assert uc.format_notice("1.9.0", None) is None


def test_get_latest_known_fetches_and_caches(cache_file, monkeypatch):
    calls = {"n": 0}

    def fake_fetch():
        calls["n"] += 1
        return "v1.10.0"

    monkeypatch.setattr(uc, "_fetch_latest_tag", fake_fetch)

    assert uc.get_latest_known("1.9.0") == "v1.10.0"
    assert calls["n"] == 1
    # Within the interval, a second call serves from cache (no new fetch).
    assert uc.get_latest_known("1.9.0") == "v1.10.0"
    assert calls["n"] == 1
    # force=True bypasses the interval.
    assert uc.get_latest_known("1.9.0", force=True) == "v1.10.0"
    assert calls["n"] == 2


def test_get_latest_known_keeps_prior_on_network_failure(cache_file, monkeypatch):
    monkeypatch.setattr(uc, "_fetch_latest_tag", lambda: "v1.10.0")
    assert uc.get_latest_known("1.9.0") == "v1.10.0"

    def boom():
        raise OSError("network down")

    monkeypatch.setattr(uc, "_fetch_latest_tag", boom)
    # force a refresh that fails -> prior knowledge is retained, no raise
    assert uc.get_latest_known("1.9.0", force=True) == "v1.10.0"


def test_maybe_notify_silent_when_not_a_tty(cache_file, monkeypatch, capsys):
    cache_file.write_text('{"last_checked": 9999999999, "latest_known": "v9.9.9"}')
    monkeypatch.setattr(uc.sys.stdout, "isatty", lambda: False)
    uc.maybe_notify("1.9.0", command="status")
    assert capsys.readouterr().err == ""


def test_maybe_notify_respects_optout(cache_file, monkeypatch, capsys):
    cache_file.write_text('{"last_checked": 9999999999, "latest_known": "v9.9.9"}')
    monkeypatch.setattr(uc.sys.stdout, "isatty", lambda: True)
    monkeypatch.setenv("AIM_NO_UPDATE_CHECK", "1")
    uc.maybe_notify("1.9.0", command="status")
    assert capsys.readouterr().err == ""


def test_maybe_notify_prints_when_interactive(cache_file, monkeypatch, capsys):
    cache_file.write_text('{"last_checked": 9999999999, "latest_known": "v9.9.9"}')
    monkeypatch.setattr(uc.sys.stdout, "isatty", lambda: True)
    monkeypatch.delenv("AIM_NO_UPDATE_CHECK", raising=False)
    uc.maybe_notify("1.9.0", command="status")
    err = capsys.readouterr().err
    assert "9.9.9" in err


def test_maybe_notify_fetches_synchronously_when_stale(cache_file, monkeypatch, capsys):
    """Cold/stale cache + interactive: must fetch synchronously, populate the
    cache, and print — regression test for the daemon-thread-never-finishes bug."""
    import json
    monkeypatch.setattr(uc, "_fetch_latest_tag", lambda: "v2.0.0")
    monkeypatch.setattr(uc.sys.stdout, "isatty", lambda: True)
    monkeypatch.delenv("AIM_NO_UPDATE_CHECK", raising=False)
    assert not cache_file.exists()              # cold start
    uc.maybe_notify("1.0.0", command="status")
    assert "2.0.0" in capsys.readouterr().err
    assert json.loads(cache_file.read_text())["latest_known"] == "v2.0.0"   # cache populated


def test_format_notice_is_ascii_safe():
    """The notice must be pure ASCII so writing it can't raise on a non-UTF-8
    stderr (the whole feature swallows errors, so a notice that raises vanishes)."""
    uc.format_notice("1.9.0", "v1.10.0").encode("ascii")  # must not raise
