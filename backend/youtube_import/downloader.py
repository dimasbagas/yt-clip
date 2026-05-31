import yt_dlp
import logging
from pathlib import Path

from config import TEMP_DIR

logger = logging.getLogger(__name__)


class YouTubeDownloader:

    def __init__(self):
        self.temp_dir = TEMP_DIR / "youtube"
        self.temp_dir.mkdir(exist_ok=True)

    def download(self, url: str, quality: str = "best") -> dict:
        logger.info(f"Downloading: {url}")

        output_template = self.temp_dir / "%(title)s.%(ext)s"

        import shutil
        ffmpeg_location = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
        ffmpeg_dir = str(Path(ffmpeg_location).parent) if ffmpeg_location else None

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": str(output_template),
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }
        if ffmpeg_dir:
            ydl_opts["ffmpeg_location"] = ffmpeg_dir

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            # fix extension
            file_path = str(Path(file_path).with_suffix(".mp4"))

            return {
                "title": info.get("title", "unknown"),
                "duration": info.get("duration", 0),
                "path": file_path,
                "filesize": info.get("filesize", 0),
            }

    def extract_info(self, url: str) -> dict:
        """Analyze video without downloading."""
        logger.info(f"Analyzing: {url}")
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", "unknown"),
                "duration": info.get("duration", 0),
                "filesize_approx": info.get("filesize_approx", 0),
                "thumbnail": info.get("thumbnail", ""),
                "formats": [
                    {
                        "format_id": f.get("format_id"),
                        "ext": f.get("ext"),
                        "resolution": f.get("resolution"),
                        "filesize": f.get("filesize", 0),
                    }
                    for f in (info.get("formats") or [])
                    if f.get("ext") == "mp4"
                ][:10],
            }
