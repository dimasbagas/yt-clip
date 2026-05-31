import logging

logger = logging.getLogger(__name__)

RATIO_MAP = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
}


def get_aspect_dimensions(ratio: str) -> tuple[int, int]:
    return RATIO_MAP.get(ratio, (1080, 1920))


def build_crop_filter(
    track_data: list[dict] | None = None,
    ratio: str = "9:16",
    mode: str = "center",
) -> str:
    width, height = get_aspect_dimensions(ratio)

    if mode == "center":
        return (
            f"crop={width}:{height}:"
            f"(iw-{width})/2:(ih-{height})/2"
        )

    if mode == "tracking" and track_data:
        return _build_tracking_filter(width, height, track_data)

    return f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"


def _build_tracking_filter(width: int, height: int, track_data: list[dict]) -> str:
    # Simplified: first frame face position determines crop offset
    if not track_data:
        return f"crop={width}:{height}:0:0"

    cx, cy = track_data[0].get("cx", 0.5), track_data[0].get("cy", 0.5)
    x = max(0, int(cx * 1920 - width // 2))
    y = max(0, int(cy * 1080 - height // 2))

    return f"crop={width}:{height}:{x}:{y}"
