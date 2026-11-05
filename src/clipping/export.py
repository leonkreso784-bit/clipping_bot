"""Izvoz isječka: putanja kadra + žig + titlovi + glasnoća → MP4 u jednom FFmpeg prolazu.

Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), `pipeline/export.py`. Segmenti kadra se izrežu
(`trim`), neovisno kropaju, skaliraju na isti izlaz i spoje (`concat`); zatim žig (`overlay`) i na
kraju titlovi (`ass`), da titl bude iznad žiga. Enkoder je libx264 (računalo nema NVENC-a).
Titlovi i fontovi se stavljaju u radnu mapu i navode golim imenom, pa nema bijega znakova.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from clipping import captions as captions_module
from clipping import ffmpeg
from clipping.captions import CaptionStyle
from clipping.profile import Watermark, WatermarkPosition
from clipping.reframe.croppath import CropPath, segment_crop_filter
from clipping.transcript import Word

OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920
OUTPUT_FPS = 30
#: Glasnoća: -14 LUFS integrirano je ono prema čemu platforme normaliziraju (dizajn §6).
LOUDNESS_LUFS = -14.0
LOUDNESS_TRUE_PEAK = -1.5
LOUDNESS_RANGE = 11.0
AUDIO_BITRATE = "192k"
AUDIO_SAMPLE_RATE = 48_000
CRF = 20
#: Žig se nikad ne povećava, a najviše zauzima ovaj udio širine izlaza.
WATERMARK_MAX_WIDTH_RATIO = 0.3
WATERMARK_MARGIN_PX = 40

_POSITIONS: dict[WatermarkPosition, str] = {
    "centar": "(W-w)/2:(H-h)/2",
    "gore_lijevo": f"{WATERMARK_MARGIN_PX}:{WATERMARK_MARGIN_PX}",
    "gore_desno": f"W-w-{WATERMARK_MARGIN_PX}:{WATERMARK_MARGIN_PX}",
    "dolje_lijevo": f"{WATERMARK_MARGIN_PX}:H-h-{WATERMARK_MARGIN_PX}",
    "dolje_desno": f"W-w-{WATERMARK_MARGIN_PX}:H-h-{WATERMARK_MARGIN_PX}",
}


class ExportError(RuntimeError):
    """Izvoz isječka nije uspio."""


@dataclass
class ExportRequest:
    source: Path
    destination: Path
    start_s: float
    end_s: float
    crop_path: CropPath
    words: list[Word]
    style: CaptionStyle
    watermark: Watermark | None = None
    top_text: str | None = None
    mask_profanity: bool = True

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s


def watermark_position(polozaj: WatermarkPosition) -> str:
    """`overlay=x:y` izraz za položaj žiga iz profila (`W,H` izlaz; `w,h` žig)."""
    return _POSITIONS[polozaj]


def watermark_render_size(image_w: int, image_h: int, out_w: int = OUTPUT_WIDTH) -> tuple[int, int]:
    """Veličina žiga u izlazu: nikad veći od izvorne slike, najviše 30 % širine izlaza, parno."""
    max_w = int(out_w * WATERMARK_MAX_WIDTH_RATIO)
    if image_w <= max_w:
        w, h = image_w, image_h
    else:
        w = max_w
        h = round(image_h * max_w / image_w)
    return w - (w % 2), max(2, h - (h % 2))


def build_filtergraph(
    request: ExportRequest,
    *,
    subtitle_name: str | None,
    fonts_name: str,
    watermark_input_index: int | None,
) -> str:
    """`-filter_complex` za jedan isječak; izlazna oznaka je `[vout]`."""
    segments = request.crop_path.segments
    if not segments:
        raise ExportError("putanja kadra nema segmenata")
    out_w, out_h = OUTPUT_WIDTH, OUTPUT_HEIGHT
    parts: list[str] = []
    labels: list[str] = []
    for index, segment in enumerate(segments):
        label = f"[v{index}]"
        labels.append(label)
        if len(segments) == 1:
            source_label = "[0:v]"
        else:
            source_label = f"[s{index}]"
            parts.append(
                f"[0:v]trim=start={segment.start_s:.4f}:end={segment.end_s:.4f},"
                f"setpts=PTS-STARTPTS{source_label}"
            )
        if segment.fit:
            parts.extend(_fit_chain(source_label, index, out_w, out_h))
            continue
        chain = [
            segment_crop_filter(segment),
            f"scale={out_w}:{out_h}:flags=lanczos",
            "setsar=1,format=yuv420p",
        ]
        parts.append(f"{source_label}{','.join(chain)}{label}")

    current = "[v0]"
    if len(segments) > 1:
        parts.append(f"{''.join(labels)}concat=n={len(segments)}:v=1:a=0[vcat]")
        current = "[vcat]"

    if request.watermark is not None and watermark_input_index is not None:
        opacity = request.watermark.neprozirnost
        pos = watermark_position(request.watermark.polozaj)
        parts.append(f"[{watermark_input_index}:v]format=rgba,colorchannelmixer=aa={opacity:g}[wm]")
        parts.append(f"{current}[wm]overlay={pos}:format=auto[vwm]")
        current = "[vwm]"

    tail = f"fps={OUTPUT_FPS}"
    if subtitle_name is not None:
        tail += f",ass=filename={subtitle_name}:fontsdir={fonts_name}"
    parts.append(f"{current}{tail}[vout]")
    return ";".join(parts)


def _fit_chain(source_label: str, index: int, out_w: int, out_h: int) -> list[str]:
    """Cijeli kadar na zamućenoj kopiji samoga sebe (lica preširoka za rez)."""
    return [
        f"{source_label}split=2[fitbg{index}][fitfg{index}]",
        (
            f"[fitbg{index}]scale={out_w}:{out_h}:force_original_aspect_ratio=increase,"
            f"crop={out_w}:{out_h},boxblur=24:2[bg{index}]"
        ),
        (
            f"[fitfg{index}]scale={out_w}:{out_h}:force_original_aspect_ratio=decrease:"
            f"flags=lanczos[fg{index}]"
        ),
        f"[bg{index}][fg{index}]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[v{index}]",
    ]


def audio_filter() -> str:
    return f"loudnorm=I={LOUDNESS_LUFS:g}:TP={LOUDNESS_TRUE_PEAK:g}:LRA={LOUDNESS_RANGE:g}"


def stage_workspace(workspace: Path, request: ExportRequest) -> tuple[str, str]:
    """Zapiši `captions.ass` i kopiraj fontove u radnu mapu; vrati gola imena za filtergraf."""
    workspace.mkdir(parents=True, exist_ok=True)
    captions_module.write_ass(
        workspace / "captions.ass",
        request.words,
        request.style,
        width=OUTPUT_WIDTH,
        height=OUTPUT_HEIGHT,
        time_offset_s=request.start_s,
        mask_profanity=request.mask_profanity,
        top_text=request.top_text,
    )
    fonts = workspace / "fonts"
    fonts.mkdir(exist_ok=True)
    for font in captions_module.FONT_DIR.iterdir():
        if font.suffix.lower() in (".ttf", ".otf") and not (fonts / font.name).exists():
            shutil.copyfile(font, fonts / font.name)
    return "captions.ass", "fonts"


def export_clip(request: ExportRequest, *, work_dir: Path) -> Path:
    """Izreži jedan isječak u MP4 (1080×1920, 30 fps, H.264, AAC, -14 LUFS) i vrati putanju."""
    workspace = work_dir / request.destination.stem
    subtitle_name, fonts_name = stage_workspace(workspace, request)

    inputs = [
        "-ss",
        f"{request.start_s:.4f}",
        "-t",
        f"{request.duration_s:.4f}",
        "-i",
        str(request.source),
    ]
    watermark_index: int | None = None
    if request.watermark is not None:
        if not request.watermark.path.is_file():
            raise ExportError(f"žig ne postoji: {request.watermark.path}")
        inputs += ["-i", str(request.watermark.path)]
        watermark_index = 1

    graph = build_filtergraph(
        request,
        subtitle_name=subtitle_name,
        fonts_name=fonts_name,
        watermark_input_index=watermark_index,
    )
    request.destination.parent.mkdir(parents=True, exist_ok=True)
    args = [
        *inputs,
        "-filter_complex", graph,
        "-map", "[vout]",
        "-map", "0:a?",
        "-af", audio_filter(),
        "-c:v", "libx264", "-preset", "medium", "-crf", str(CRF), "-profile:v", "high",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", str(AUDIO_SAMPLE_RATE),
        "-movflags", "+faststart",
        str(request.destination),
    ]  # fmt: skip
    try:
        ffmpeg.run(args, cwd=workspace)
    except ffmpeg.FFmpegError as exc:
        raise ExportError(f"izvoz {request.destination.name} nije uspio:\n{exc}") from exc
    if not request.destination.is_file() or request.destination.stat().st_size == 0:
        raise ExportError(f"ffmpeg je završio, ali {request.destination.name} je prazan")
    return request.destination
