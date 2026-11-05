from pathlib import Path

import pytest

from clipping.reframe import Strategy, build_crop_path, wide_segment
from clipping.reframe.croppath import CropKeyframe, CropSegment, segment_crop_filter
from clipping.reframe.faces import FaceObservation
from clipping.reframe.tracker import FaceTrack

GOLDEN = Path("data/izvori/JvLklMRThYs/source.mp4")


def test_no_face_centre_crop(synthetic_video: Path) -> None:
    path = build_crop_path(synthetic_video, start_s=0.0, end_s=8.0)
    assert path.source_width == 1280 and path.source_height == 720
    assert path.segments[0].start_s == 0.0 and path.segments[-1].end_s == pytest.approx(8.0)
    assert all(s.strategy is Strategy.GENERAL for s in path.segments)
    assert {(s.width, s.height) for s in path.segments} == {(404, 720)}


def test_crop_filter_static_expression() -> None:
    seg = CropSegment(0.0, 8.0, 404, 720, [CropKeyframe(0.0, 438.0, 0.0)], Strategy.GENERAL)
    assert segment_crop_filter(seg) == "crop=w=404:h=720:x='438.0':y='0.0'"


def test_crop_filter_pans_between_keyframes() -> None:
    seg = CropSegment(
        2.0, 4.0, 404, 720, [CropKeyframe(2.0, 100.0, 0.0), CropKeyframe(4.0, 300.0, 0.0)]
    )
    f = segment_crop_filter(seg)
    assert f.startswith("crop=w=404:h=720:x='if(lt(t") and "100.0+100.0*(t-0.0)" in f


def _obs(t: float, cx: float) -> FaceObservation:
    return FaceObservation(t=t, cx=cx, cy=300.0, width=120.0, height=160.0, eye_y=280.0, mar=0.1)


def test_wide_spread_uses_fit() -> None:
    left = FaceTrack(0, [_obs(0.0, 64.0), _obs(0.5, 64.0)])
    right = FaceTrack(1, [_obs(0.0, 1216.0), _obs(0.5, 1216.0)])
    seg = wide_segment(
        [left, right], start_s=0.0, end_s=1.0, source_w=1280, source_h=720, crop_w=404, crop_h=720
    )
    assert seg.fit is True and seg.strategy is Strategy.WIDE


def test_wide_close_faces_lock_on_centroid() -> None:
    a = FaceTrack(0, [_obs(0.0, 600.0), _obs(0.5, 600.0)])
    b = FaceTrack(1, [_obs(0.0, 700.0), _obs(0.5, 700.0)])
    seg = wide_segment(
        [a, b], start_s=0.0, end_s=1.0, source_w=1280, source_h=720, crop_w=404, crop_h=720
    )
    assert seg.fit is False and seg.keyframes[0].x == pytest.approx(650 - 202)


def test_segments_tile_without_gaps(synthetic_video: Path) -> None:
    path = build_crop_path(synthetic_video, start_s=1.0, end_s=5.0)
    assert path.segments[0].start_s == 0.0 and path.segments[-1].end_s == pytest.approx(4.0)
    for a, b in zip(path.segments, path.segments[1:], strict=False):
        assert a.end_s == pytest.approx(b.start_s)


@pytest.mark.golden
def test_golden_clip_tracks_a_face() -> None:
    if not GOLDEN.exists():
        pytest.skip("nema zlatnog videa")
    path = build_crop_path(GOLDEN, start_s=1155.8, end_s=1209.7)
    assert len(path.segments) >= 2
    assert any(s.strategy is Strategy.TRACK for s in path.segments)
    for s in path.segments:
        for k in s.keyframes:
            assert 0 <= k.x <= path.source_width - s.width + 1e-6


def test_single_wide_face_uses_fit() -> None:
    from clipping.reframe import track_segment

    big = [
        FaceObservation(
            t=t * 0.2, cx=640.0, cy=360.0, width=500.0, height=600.0, eye_y=300.0, mar=0.1
        )
        for t in range(10)
    ]
    seg = track_segment(
        FaceTrack(0, big),
        start_s=0.0,
        end_s=2.0,
        source_w=1280,
        source_h=720,
        crop_w=404,
        crop_h=720,
    )
    assert seg.fit is True
