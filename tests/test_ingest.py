import json
from pathlib import Path

import pytest

from clipping import ingest
from clipping.ingest import is_allowed_source, normalize_channel, pick_new_video
from clipping.profile import load_profile

PROFILE = load_profile(Path(__file__).parent / "fixtures" / "kampanja_test.yaml")
OWN = "https://www.youtube.com/@test"


def _fake(monkeypatch: pytest.MonkeyPatch, payload: dict[str, object]) -> list[list[str]]:
    calls: list[list[str]] = []

    def run(args: list[str]) -> str:
        calls.append(args)
        return json.dumps(payload)

    monkeypatch.setattr(ingest, "_run_ytdlp", run)
    return calls


def test_normalize_channel() -> None:
    assert normalize_channel("http://youtube.com/@Test/videos/") == "https://www.youtube.com/@test"


def test_foreign_handle_rejected_without_network(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _fake(monkeypatch, {})
    assert not is_allowed_source("https://www.youtube.com/@drugi/videos", PROFILE)
    assert calls == []  # tuđi handle se odbija bez mreže


def test_allowed_handle_still_checks_video_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pregled C3: yt-dlp prihvaća `/@dopusten#/watch?v=TUDJI`; handle u URL-u nije dokaz."""
    _fake(monkeypatch, {"id": "TUDJI", "uploader_url": "https://www.youtube.com/@drugi"})
    assert not is_allowed_source("https://www.youtube.com/@test#/watch?v=TUDJI", PROFILE)


def test_rejects_lookalike_host_and_missing_scheme(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _fake(monkeypatch, {"id": "abc", "uploader_url": OWN})
    assert not is_allowed_source("https://notyoutube.com/watch?v=abc", PROFILE)
    assert not is_allowed_source("evil.com/@test", PROFILE)
    assert not is_allowed_source("www.youtube.com/watch?v=abc", PROFILE)
    assert calls == []


def test_allowed_source_by_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake(monkeypatch, {"id": "abc", "uploader_url": OWN, "channel_url": "https://x/channel/1"})
    assert is_allowed_source("https://www.youtube.com/watch?v=abc", PROFILE)


def test_rejects_foreign_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake(monkeypatch, {"id": "abc", "uploader_url": "https://www.youtube.com/@drugi"})
    assert not is_allowed_source("https://www.youtube.com/watch?v=abc", PROFILE)
    assert not is_allowed_source("https://www.youtube.com/@drugi", PROFILE)
    assert not is_allowed_source("https://vimeo.com/123", PROFILE)


def test_pick_new_skips_known(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _fake(
        monkeypatch,
        {
            "uploader_url": OWN,
            "entries": [{"id": "new1", "title": "a"}, {"id": "new2", "title": "b"}],
        },
    )
    picked = pick_new_video(PROFILE, {"https://www.youtube.com/watch?v=new1"})
    assert picked is not None and picked.id == "new2"
    assert calls[0][-1] == "https://www.youtube.com/@test/videos"
    assert (
        pick_new_video(PROFILE, {f"https://www.youtube.com/watch?v=new{i}" for i in (1, 2)}) is None
    )


def test_download_skips_existing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    existing = tmp_path / "abc" / "source.mp4"
    existing.parent.mkdir()
    existing.write_bytes(b"video")
    calls = _fake(monkeypatch, {"id": "abc", "uploader_url": OWN})
    got = ingest.download("https://www.youtube.com/watch?v=abc", tmp_path)
    assert got.path == existing and len(got.sha256) == 64
    assert all("-S" not in c for c in calls)
