from typing import Any


def _srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def _vtt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def to_srt(segments: list[dict[str, Any]]) -> str:
    lines = []
    for i, seg in enumerate(segments, 1):
        start = _srt_time(seg["start_sec"])
        end = _srt_time(seg["end_sec"])
        lines.append(f"{i}")
        lines.append(f"{start} --> {end}")
        lines.append(seg["text"].strip())
        lines.append("")
    return "\n".join(lines)


def to_vtt(segments: list[dict[str, Any]]) -> str:
    lines = ["WEBVTT", ""]
    for seg in segments:
        start = _vtt_time(seg["start_sec"])
        end = _vtt_time(seg["end_sec"])
        lines.append(f"{start} --> {end}")
        lines.append(seg["text"].strip())
        lines.append("")
    return "\n".join(lines)


def format_subtitles(segments: list[dict[str, Any]], fmt: str = "srt") -> str:
    if fmt == "srt":
        return to_srt(segments)
    elif fmt == "vtt":
        return to_vtt(segments)
    raise ValueError(f"Unsupported format: {fmt}")
