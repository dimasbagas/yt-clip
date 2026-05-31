import subprocess
import logging
from pathlib import Path

from config import FFMPEG_BIN, FFPROBE_BIN, NVENC_AVAILABLE

logger = logging.getLogger(__name__)


class FFmpegClient:

    def probe(self, video_path: str | Path) -> dict:
        cmd = [
            FFPROBE_BIN,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ]
        import json
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        return json.loads(result.stdout)

    def trim(self, input_path: str | Path, output_path: str | Path,
             start: str, end: str) -> Path:
        output_path = Path(output_path)

        def to_sec(t_str: str) -> float:
            parts = t_str.split(":")
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return int(parts[0]) * 60 + float(parts[1])
            return float(t_str)

        duration = max(0.1, to_sec(end) - to_sec(start))
        cmd = [
            FFMPEG_BIN, "-y",
            "-ss", start,
            "-i", str(input_path),
            "-t", f"{duration:.3f}",
            "-c", "copy",
            str(output_path),
        ]
        logger.info(f"Trimming: {start} → {end} (Duration: {duration:.3f}s)")
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def burn_subtitles(self, input_path: str | Path, output_path: str | Path,
                       subtitle_path: str | Path) -> Path:
        output_path = Path(output_path)

        try:
            # Convert to relative path relative to CWD to avoid Windows drive colons
            sub_path = str(Path(subtitle_path).relative_to(Path.cwd())).replace("\\", "/")
        except ValueError:
            # Fallback if not under CWD
            sub_path = str(Path(subtitle_path).resolve()).replace("\\", "/")
            if ":" in sub_path:
                sub_path = sub_path.replace(":", "\\:")

        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(input_path),
            "-vf", f"subtitles={sub_path}",
            "-c:a", "aac",
            str(output_path),
        ]
        logger.info(f"Burning subtitles using path: {sub_path}")
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def encode(self, input_path: str | Path, output_path: str | Path,
               preset: str = "tiktok", width: int = 1080, height: int = 1920,
               filter_str: str | None = None, audio_src: str | Path | None = None) -> Path:
        output_path = Path(output_path)

        if NVENC_AVAILABLE:
            vcodec = "h264_nvenc"
            enc_args = ["-preset", "p7", "-cq", "23"]
        else:
            vcodec = "libx264"
            enc_args = ["-preset", "medium", "-crf", "18"]

        inputs = ["-i", str(input_path)]
        maps = []

        if audio_src:
            inputs.extend(["-i", str(audio_src)])
            maps.extend(["-map", "0:v:0", "-map", "1:a:0"])

        vf_arg = []
        if filter_str:
            vf_arg = ["-vf", filter_str]
        elif width and height:
            scale = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
            vf_arg = ["-vf", scale]

        cmd = [
            FFMPEG_BIN, "-y",
            *inputs,
            *vf_arg,
            *maps,
            "-c:v", vcodec, *enc_args,
            "-c:a", "aac", "-b:a", "128k",
            "-r", "30",
            str(output_path),
        ]

        logger.info(f"Encoding with {'NVENC' if NVENC_AVAILABLE else 'CPU'}: {width}x{height}")
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def extract_audio(self, input_path: str | Path, output_path: str | Path) -> Path:
        output_path = Path(output_path)
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(input_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            str(output_path),
        ]
        logger.info("Extracting audio...")
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
