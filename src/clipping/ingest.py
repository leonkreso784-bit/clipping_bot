"""Ulaz: izvor iz kampanje (yt-dlp samo za poveznice s dopuštenog kanala) i zapis prava (ADR-004).

Poveznica prolazi samo ako je video s kanala iz `izvori.dopusteni_kanali`; to se gleda po handleu
`@...` u URL-u ili po `uploader_url`/`channel_url` iz metapodataka. Bez `--izvor` alat uzme
najnoviji video kanala koji još nije u tablici `izvor`.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from clipping.profile import CampaignProfile

#: Format: do 1080p, H.264 ako postoji (FFmpeg ga brže dekodira od VP9/AV1).
FORMAT_SORT = "res:1080,vcodec:h264"
_CHANNEL_TAILS = ("/videos", "/streams", "/shorts", "/featured", "/live")
_HANDLE = re.compile(r"/(@[A-Za-z0-9_.\-]+)")
_SHA_CHUNK = 8 * 1024 * 1024
_YOUTUBE_HOSTS = frozenset({"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"})


class IngestError(RuntimeError):
    """Izvor se ne može dohvatiti ili nije s dopuštenog kanala."""


@dataclass(frozen=True)
class VideoMeta:
    id: str
    url: str
    title: str
    upload_date: str = ""
    duration_s: float | None = None
    channel_urls: tuple[str, ...] = ()


@dataclass(frozen=True)
class Downloaded:
    path: Path
    sha256: str
    url: str


def _run_ytdlp(args: list[str]) -> str:
    """Pokreni pinani yt-dlp iz istog okruženja i vrati stdout (zamjenjuje se u testovima)."""
    proc = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--no-warnings", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise IngestError(f"yt-dlp je pao ({proc.returncode}):\n{proc.stderr[-800:]}")
    return proc.stdout


def normalize_channel(url: str) -> str:
    """Usporediv oblik adrese kanala: https, www, mala slova, bez repa `/videos` i kose crte."""
    text = url.strip().lower()
    text = re.sub(r"^http://", "https://", text)
    text = re.sub(r"^https://(m\.)?youtube\.com", "https://www.youtube.com", text)
    text = text.split("?", 1)[0].rstrip("/")
    for tail in _CHANNEL_TAILS:
        if text.endswith(tail):
            text = text[: -len(tail)]
    return text


def canonical_video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def _meta_from_json(data: dict[str, Any]) -> VideoMeta:
    video_id = str(data["id"])
    channels = tuple(
        normalize_channel(str(data[key]))
        for key in ("uploader_url", "channel_url")
        if data.get(key)
    )
    duration = data.get("duration")
    return VideoMeta(
        id=video_id,
        url=canonical_video_url(video_id),
        title=str(data.get("title") or ""),
        upload_date=str(data.get("upload_date") or ""),
        duration_s=float(duration) if duration is not None else None,
        channel_urls=channels,
    )


def fetch_meta(url: str) -> VideoMeta:
    return _meta_from_json(json.loads(_run_ytdlp(["-J", "--skip-download", url])))


def is_allowed_source(url: str, profile: CampaignProfile, *, meta: VideoMeta | None = None) -> bool:
    """Je li poveznica s kanala iz briefa.

    Odlučuju metapodaci videa (`uploader_url`/`channel_url`), nikad sam URL: `@handle` u putanji
    služi samo za brzo odbijanje, jer yt-dlp prihvaća i oblike poput `/@dopusten#/watch?v=TUDJI`.
    """
    return check_source(url, profile, meta=meta) is not None


def check_source(
    url: str, profile: CampaignProfile, *, meta: VideoMeta | None = None
) -> VideoMeta | None:
    """Metapodaci videa ako je s dopuštenog kanala, inače `None` (vidi `is_allowed_source`)."""
    allowed = {normalize_channel(c) for c in profile.izvori.dopusteni_kanali}
    allowed_handles = {
        m.group(1).lower() for c in profile.izvori.dopusteni_kanali if (m := _HANDLE.search(c))
    }
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or parsed.netloc.lower() not in _YOUTUBE_HOSTS:
        return None
    handle = _HANDLE.search(parsed.path)
    if handle is not None and handle.group(1).lower() not in allowed_handles:
        return None
    found = meta if meta is not None else fetch_meta(url)
    return found if any(channel in allowed for channel in found.channel_urls) else None


def list_channel_videos(channel_url: str, *, limit: int = 20) -> list[VideoMeta]:
    """Najnoviji videi kanala (samo metapodaci, bez skidanja), od najnovijeg."""
    base = normalize_channel(channel_url)
    data = json.loads(
        _run_ytdlp(["--flat-playlist", "-J", "--playlist-end", str(limit), f"{base}/videos"])
    )
    channels = tuple(
        normalize_channel(str(data[key]))
        for key in ("uploader_url", "channel_url")
        if data.get(key)
    )
    videos: list[VideoMeta] = []
    for entry in data.get("entries") or []:
        if not entry or not entry.get("id"):
            continue
        meta = _meta_from_json(entry)
        videos.append(
            VideoMeta(meta.id, meta.url, meta.title, meta.upload_date, meta.duration_s, channels)
        )
    return videos


def pick_new_video(profile: CampaignProfile, known_urls: set[str]) -> VideoMeta | None:
    """Najnoviji video s dopuštenih kanala koji još nije obrađen."""
    for channel in profile.izvori.dopusteni_kanali:
        for video in list_channel_videos(channel):
            if video.url not in known_urls:
                return video
    return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(_SHA_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, sources_dir: Path, *, meta: VideoMeta | None = None) -> Downloaded:
    """Skini video u `sources_dir/<id>/source.mp4`; postojeća datoteka se ne skida ponovno."""
    found = meta if meta is not None else fetch_meta(url)
    destination = sources_dir / found.id / "source.mp4"
    if not destination.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_name("source.part.mp4")
        _run_ytdlp(
            ["-S", FORMAT_SORT, "--merge-output-format", "mp4", "-o", str(partial), found.url]
        )
        if not partial.is_file():
            raise IngestError(f"yt-dlp je završio, ali {partial} ne postoji")
        partial.replace(destination)
    return Downloaded(path=destination, sha256=sha256_file(destination), url=found.url)
