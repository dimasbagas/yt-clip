from faster_whisper import WhisperModel
from pathlib import Path
import logging

from config import WHISPER_MODEL, WHISPER_MODEL_DIR, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE

logger = logging.getLogger(__name__)


class WhisperClient:
    _instance = None

    def __init__(self):
        self.model = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self):
        if self.model is not None:
            return
        logger.info(f"Loading Whisper model: {WHISPER_MODEL}")
        device, compute_type = self._resolve_device()
        self.model = WhisperModel(
            WHISPER_MODEL,
            device=device,
            compute_type=compute_type,
            download_root=str(WHISPER_MODEL_DIR),
        )
        logger.info("Whisper model loaded")

    def _resolve_device(self):
        if WHISPER_DEVICE == "auto":
            import torch
            return ("cuda", "float16") if torch.cuda.is_available() else ("cpu", "int8")
        return (WHISPER_DEVICE, WHISPER_COMPUTE_TYPE)

    def transcribe(self, audio_path: str | Path, language: str | None = None):
        if self.model is None:
            self.load()

        segments, info = self.model.transcribe(
            str(audio_path),
            language=language,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                threshold=0.5,
            ),
        )

        return {
            "language": info.language,
            "duration": info.duration,
            "segments": [
                {
                    "id": seg.id,
                    "start": self._fmt_time(seg.start),
                    "end": self._fmt_time(seg.end),
                    "start_sec": round(seg.start, 3),
                    "end_sec": round(seg.end, 3),
                    "text": seg.text.strip(),
                }
                for seg in segments
            ],
        }

    @staticmethod
    def _fmt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}"
