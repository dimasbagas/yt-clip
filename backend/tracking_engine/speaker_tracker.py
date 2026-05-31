import logging
from collections import deque

logger = logging.getLogger(__name__)

SPEAKER_HISTORY = deque(maxlen=15)


def track_active_speaker(segments: list[dict], current_time: float) -> int | None:
    for seg in segments:
        if seg["start_sec"] <= current_time <= seg["end_sec"]:
            return seg.get("speaker", 0)
    return None


def determine_focus_side(faces: list[dict], active_speaker: int | None) -> str:
    if not faces:
        return "center"

    if active_speaker is not None and active_speaker < len(faces):
        cx = faces[active_speaker]["cx"]
        return "left" if cx < 0.5 else "right"

    cx = faces[0]["cx"]
    return "left" if cx < 0.5 else "right"


def smooth_transition(current: str, target: str, alpha: float = 0.3) -> str:
    SPEAKER_HISTORY.append(target)
    if len(SPEAKER_HISTORY) < 3:
        return target

    counts = {}
    for d in SPEAKER_HISTORY:
        counts[d] = counts.get(d, 0) + 1
    smoothed = max(counts, key=counts.get)
    return smoothed
