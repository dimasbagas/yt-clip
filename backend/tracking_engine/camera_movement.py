import logging
from typing import Literal

logger = logging.getLogger(__name__)

CameraMode = Literal["podcast", "interview", "gaming", "streamer", "cinematic"]


class CameraMovement:

    def __init__(self, mode: CameraMode = "podcast"):
        self.mode = mode
        self.prev_focus = "center"
        self.transition_frames = 0
        self.max_transition = self._get_transition_frames()

    def _get_transition_frames(self) -> int:
        return {
            "podcast": 15,
            "interview": 20,
            "gaming": 10,
            "streamer": 5,
            "cinematic": 30,
        }.get(self.mode, 15)

    def update(self, focus_side: str) -> dict:
        if focus_side != self.prev_focus:
            self.transition_frames = self.max_transition
            self.prev_focus = focus_side

        progress = 1.0
        if self.transition_frames > 0:
            progress = 1.0 - (self.transition_frames / self.max_transition)
            self.transition_frames -= 1

        return {
            "focus": focus_side,
            "progress": round(progress, 3),
            "smoothing": "ease-in-out" if progress < 1 else "none",
        }

    def get_crop_offset(
        self, focus_side: str, frame_width: int, frame_height: int,
        target_width: int = 1080, target_height: int = 1920,
    ) -> dict:
        if focus_side == "left":
            x = 0
        elif focus_side == "right":
            x = frame_width - target_width
        else:
            x = (frame_width - target_width) // 2

        y = (frame_height - target_height) // 2

        return {"x": max(0, x), "y": max(0, y), "width": target_width, "height": target_height}
