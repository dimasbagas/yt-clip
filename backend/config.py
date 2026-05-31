from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
EXPORTS_DIR = BASE_DIR / "exports"
TEMP_DIR = BASE_DIR / "temp"
MODELS_DIR = BASE_DIR / "models"

EXPORTS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Whisper
WHISPER_MODEL = "base"  # tiny, base, small, medium, large-v3
WHISPER_MODEL_DIR = MODELS_DIR / "whisper"
WHISPER_DEVICE = "auto"  # auto, cpu, cuda
WHISPER_COMPUTE_TYPE = "auto"  # auto, float16, int8

# YOLO
YOLO_MODEL = "yolov8n.pt"
YOLO_MODEL_DIR = MODELS_DIR / "yolo"
YOLO_CONFIDENCE = 0.5

# FFmpeg
FFMPEG_BIN = "ffmpeg"
FFPROBE_BIN = "ffprobe"
NVENC_ENABLED = True

def _check_nvenc() -> bool:
    import subprocess
    if not NVENC_ENABLED:
        return False
    try:
        # Jalankan encoding dummy 0.1 detik dengan h264_nvenc untuk memverifikasi kompatibilitas driver secara riil
        result = subprocess.run(
            [FFMPEG_BIN, "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64:d=1", "-c:v", "h264_nvenc", "-t", "0.1", "-f", "null", "-"],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False

NVENC_AVAILABLE = _check_nvenc()


# Render
RENDER_QUALITY = "high"  # low, medium, high
RENDER_FPS = 30
RENDER_CRF = 18
RENDER_BITRATE = "8M"

# Server
HOST = "127.0.0.1"
PORT = 8899
