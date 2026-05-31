import logging
import json
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import HOST, PORT, TEMP_DIR, EXPORTS_DIR, YOLO_MODEL, WHISPER_MODEL
from render_engine.encoder import check_nvenc
from subtitle_engine.whisper_client import WhisperClient
from subtitle_engine.subtitle_formatter import format_subtitles
from render_engine.ffmpeg_client import FFmpegClient
from render_engine.crop_processor import get_aspect_dimensions
from tracking_engine.camera_movement import CameraMovement
from tracking_engine.yolo_detector import YOLODetector
from youtube_import.downloader import YouTubeDownloader

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("clipos")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ClipOS backend starting...")
    logger.info(f"NVENC: {'available' if check_nvenc() else 'not available'}")
    logger.info("Models will load on first use")
    logger.info("ClipOS backend ready")
    yield
    logger.info("ClipOS backend shutting down")


app = FastAPI(title="ClipOS API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ffmpeg = FFmpegClient()
downloader = YouTubeDownloader()


# ─── Models ───

class YouTubeInfoRequest(BaseModel):
    url: str


class YouTubeDownloadRequest(BaseModel):
    url: str
    quality: str = "best"


class ClipRequest(BaseModel):
    video_path: str
    start: str
    end: str


class SubtitleRequest(BaseModel):
    video_path: str
    language: str | None = None


class RenderRequest(BaseModel):
    video_path: str
    start: str
    end: str
    aspect_ratio: str = "9:16"
    tracking_mode: str = "podcast"
    format: str = "mp4"
    burn_subtitles: bool = True


# ─── Routes ───

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/system")
def system_info():
    return {
        "nvenc": check_nvenc(),
        "models": {
            "whisper": WHISPER_MODEL,
            "yolo": YOLO_MODEL,
        },
    }


# ─── YouTube ───

@app.post("/api/youtube/info")
def youtube_info(req: YouTubeInfoRequest):
    try:
        info = downloader.extract_info(req.url)
        return info
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/youtube/download")
def youtube_download(req: YouTubeDownloadRequest):
    try:
        result = downloader.download(req.url, req.quality)
        return result
    except Exception as e:
        raise HTTPException(400, str(e))


# ─── Upload ───

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix if file.filename else ".mp4"
    if ext.lower() not in {".mp4", ".mov", ".mkv", ".avi"}:
        raise HTTPException(400, "Unsupported format")

    dest = TEMP_DIR / f"input{ext}"
    content = await file.read()
    dest.write_bytes(content)

    probe = ffmpeg.probe(str(dest))
    stream = next((s for s in probe.get("streams", []) if s["codec_type"] == "video"), {})

    return {
        "path": str(dest),
        "filename": file.filename,
        "duration": float(probe.get("format", {}).get("duration", 0)),
        "width": stream.get("width", 0),
        "height": stream.get("height", 0),
        "fps": eval(stream.get("r_frame_rate", "0/1")) if stream.get("r_frame_rate") else 0,
    }


# ─── Clip ───

@app.post("/api/clip/trim")
def trim_video(req: ClipRequest):
    output = TEMP_DIR / "trimmed.mp4"
    ffmpeg.trim(req.video_path, output, req.start, req.end)
    return {"path": str(output)}


# ─── Subtitles ───

@app.post("/api/subtitles/generate")
def generate_subtitles(req: SubtitleRequest):
    try:
        audio_path = TEMP_DIR / "audio.wav"
        ffmpeg.extract_audio(req.video_path, audio_path)

        whisper = WhisperClient.get_instance()
        result = whisper.transcribe(str(audio_path), language=req.language)

        srt = format_subtitles(result["segments"], "srt")
        vtt = format_subtitles(result["segments"], "vtt")

        srt_path = TEMP_DIR / "subtitles.srt"
        vtt_path = TEMP_DIR / "subtitles.vtt"
        srt_path.write_text(srt, encoding="utf-8")
        vtt_path.write_text(vtt, encoding="utf-8")

        return {
            "segments": result["segments"],
            "language": result["language"],
            "duration": result["duration"],
            "srt_path": str(srt_path),
            "vtt_path": str(vtt_path),
        }
    except Exception as e:
        raise HTTPException(500, f"Subtitle generation failed: {e}")


@app.post("/api/subtitles/export")
def export_subtitles(video_path: str = Form(...), fmt: str = Form("srt")):
    audio_path = TEMP_DIR / "audio.wav"
    ffmpeg.extract_audio(video_path, audio_path)
    whisper = WhisperClient.get_instance()
    result = whisper.transcribe(str(audio_path))
    content = format_subtitles(result["segments"], fmt)
    ext = fmt
    out_path = EXPORTS_DIR / f"subtitles.{ext}"
    out_path.write_text(content, encoding="utf-8")
    return FileResponse(str(out_path), filename=f"subtitles.{ext}")


# ─── Render ───

@app.post("/api/render")
def render_video(req: RenderRequest):
    try:
        from ai_processing.pipeline import Pipeline
        pipeline = Pipeline()
        result = pipeline.run(
            video_path=req.video_path,
            clip_start=req.start,
            clip_end=req.end,
            aspect_ratio=req.aspect_ratio,
            tracking_mode=req.tracking_mode,
            burn_subtitles=req.burn_subtitles,
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"Render failed: {e}")


# ─── Track Faces ───

@app.post("/api/tracking/detect")
def detect_faces(video_path: str = Form(...)):
    import cv2
    cap = cv2.VideoCapture(video_path)
    frames = []
    count = 0

    yolo = YOLODetector.get_instance()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count % 30 == 0:
            faces = yolo.detect_faces(frame)
            if faces:
                frames.append({
                    "frame": count,
                    "faces": faces,
                })
        count += 1

    cap.release()
    return {"total_frames": count, "detections": frames}


# ─── Entry ───

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
