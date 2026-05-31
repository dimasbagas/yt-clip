import logging
from pathlib import Path

from subtitle_engine.whisper_client import WhisperClient
from subtitle_engine.subtitle_formatter import format_subtitles
from render_engine.ffmpeg_client import FFmpegClient
from render_engine.crop_processor import build_crop_filter, get_aspect_dimensions
from render_engine.encoder import check_nvenc
from tracking_engine.yolo_detector import YOLODetector
from tracking_engine.camera_movement import CameraMovement
from youtube_import.downloader import YouTubeDownloader

from config import TEMP_DIR, NVENC_AVAILABLE

logger = logging.getLogger(__name__)


import sys
import time
import threading

class TerminalSpinner:
    def __init__(self, message="Processing"):
        self.message = message
        self.active = False
        self.thread = None

    def _spin(self):
        frames = [
            "[=         ]",
            "[==        ]",
            "[===       ]",
            "[====      ]",
            "[ =====    ]",
            "[  =====   ]",
            "[   =====  ]",
            "[    ===== ]",
            "[     ==== ]",
            "[      ====]",
            "[       ===]",
            "[        ==]",
            "[         =]",
            "[          ]"
        ]
        idx = 0
        dots = ["   ", ".  ", ".. ", "..."]
        dots_idx = 0
        last_time = time.time()
        while self.active:
            if time.time() - last_time > 0.36:
                dots_idx = (dots_idx + 1) % len(dots)
                last_time = time.time()
                
            msg = f"{self.message}{dots[dots_idx]}"
            sys.stdout.write(f"\r  \033[96m[..]\033[0m {msg:<40} {frames[idx]} ")
            sys.stdout.flush()
            idx = (idx + 1) % len(frames)
            time.sleep(0.12)

    def __enter__(self):
        self.active = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.active = False
        if self.thread:
            self.thread.join(timeout=1.0)
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()
        if exc_type is None:
            sys.stdout.write(f"  \033[92m[OK]\033[0m {self.message} - Selesai!\n")
        else:
            sys.stdout.write(f"  \033[91m[XX]\033[0m {self.message} - Gagal!\n")
        sys.stdout.flush()


def print_progress(message, current, total):
    percent = int(100 * current / total)
    bar_length = 20
    filled_length = int(bar_length * current // total)
    bar = "=" * filled_length + " " * (bar_length - filled_length)
    sys.stdout.write(f"\r  \033[96m[..]\033[0m {message:<40} [{bar}] {percent}% ({current}/{total} frame)")
    sys.stdout.flush()

def clear_progress(message, success=True):
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()
    if success:
        sys.stdout.write(f"  \033[92m[OK]\033[0m {message} - Selesai!\n")
    else:
        sys.stdout.write(f"  \033[91m[XX]\033[0m {message} - Gagal!\n")
    sys.stdout.flush()


class Pipeline:

    def __init__(self):
        FFmpegClient()
        check_nvenc()
        self.temp = TEMP_DIR
        self.temp.mkdir(exist_ok=True)

    def run(self, video_path: str, clip_start: str, clip_end: str,
            aspect_ratio: str = "9:16", tracking_mode: str = "podcast",
            generate_subtitles: bool = True, burn_subtitles: bool = True,
            export_srt: bool = False) -> dict:
        steps = []
        ffmpeg = FFmpegClient()
        segments = []

        # 1. Trim clip first
        trimmed_path = self.temp / "trimmed.mp4"
        with TerminalSpinner("Memotong klip video (Trimming)"):
            ffmpeg.trim(video_path, trimmed_path, clip_start, clip_end)
        steps.append("clip_trimmed")

        # 2. Extract audio from trimmed clip for Whisper
        if generate_subtitles:
            audio_path = self.temp / "audio.wav"
            with TerminalSpinner("Mengekstrak audio klip untuk Whisper"):
                ffmpeg.extract_audio(trimmed_path, audio_path)
            steps.append("audio_extracted")

            # 3. Transcribe
            with TerminalSpinner("Mentranskripsi percakapan (Whisper AI)"):
                whisper = WhisperClient.get_instance()
                result = whisper.transcribe(str(audio_path))
                segments = result["segments"]
                srt_content = format_subtitles(segments, "srt")
                srt_path = self.temp / "subtitles.srt"
                srt_path.write_text(srt_content, encoding="utf-8")
            steps.append("subtitles_generated")
        else:
            srt_path = None
            steps.append("subtitles_skipped")

        # 4. Dynamic Crop
        import cv2
        import numpy as np
        from tracking_engine.speaker_tracker import track_active_speaker, determine_focus_side, smooth_transition
        
        logger.info(f"Starting Smart Crop with mode: {tracking_mode}, aspect: {aspect_ratio}")
        
        cap = cv2.VideoCapture(str(trimmed_path))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        # Target dimension calculations
        out_width, out_height = get_aspect_dimensions(aspect_ratio)
        
        # Calculate intermediate crop box width & height based on aspect ratio
        target_height = height
        target_width = int(height * (out_width / out_height)) // 2 * 2
        if target_width > width:
            target_width = width
            target_height = int(width * (out_height / out_width)) // 2 * 2
            
        logger.info(f"Source size: {width}x{height}, Target size: {out_width}x{out_height}, Crop box: {target_width}x{target_height}")

        # Run face detection on sampled frames (1 sample per second)
        detections = {}
        sample_rate = int(fps) if fps > 0 else 25
        
        if tracking_mode != "center" and target_width < width:
            logger.info("Running YOLO/Haar face detection and mouth motion analysis...")
            yolo = YOLODetector.get_instance()
            yolo.load()
            
            cap = cv2.VideoCapture(str(trimmed_path))
            frame_idx = 0
            prev_frame_gray = None
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                print_progress("Melacak subjek & gerakan mulut aktif", frame_idx + 1, frame_count)
                
                if frame_idx % sample_rate == 0:
                    faces = yolo.detect_faces(frame)
                    
                    # Calculate mouth movement difference if we have a previous frame
                    if prev_frame_gray is not None and faces:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        for face in faces:
                            bbox = face["bbox"]
                            fx1, fy1, fx2, fy2 = bbox
                            
                            # Estimate lower 30% of face for mouth region
                            my1 = fy1 + int((fy2 - fy1) * 0.65)
                            my2 = fy1 + int((fy2 - fy1) * 0.95)
                            mx1 = fx1 + int((fx2 - fx1) * 0.25)
                            mx2 = fx1 + int((fx2 - fx1) * 0.75)
                            
                            my1, my2 = max(0, min(height, my1)), max(0, min(height, my2))
                            mx1, mx2 = max(0, min(width, mx1)), max(0, min(width, mx2))
                            
                            if my2 > my1 and mx2 > mx1:
                                mouth_curr = gray[my1:my2, mx1:mx2]
                                mouth_prev = prev_frame_gray[my1:my2, mx1:mx2]
                                
                                # Absolute frame difference for mouth activity
                                diff = cv2.absdiff(mouth_curr, mouth_prev)
                                motion = float(np.mean(diff))
                                face["mouth_motion"] = motion
                            else:
                                face["mouth_motion"] = 0.0
                    else:
                        for face in faces:
                            face["mouth_motion"] = 0.0
                            
                    detections[frame_idx] = faces
                
                prev_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_idx += 1
            cap.release()
            clear_progress("Melacak subjek & gerakan mulut aktif")
            
        # Calculate raw X coordinates frame-by-frame (centering on most active mouth / face)
        raw_x = []
        prev_cx = 0.5
        for i in range(frame_count):
            sampled_frame = (i // sample_rate) * sample_rate
            faces = detections.get(sampled_frame, [])
            if not faces and detections:
                closest = min(detections.keys(), key=lambda k: abs(k - i))
                faces = detections.get(closest, [])
                
            if faces:
                # Find the face with the highest mouth motion
                active_face = max(faces, key=lambda f: f.get("mouth_motion", 0.0))
                # Only switch if mouth motion is above a noise threshold (1.5)
                if active_face.get("mouth_motion", 0.0) > 1.5:
                    target_cx = active_face["cx"]
                else:
                    target_cx = prev_cx
            else:
                target_cx = prev_cx
                
            prev_cx = target_cx
            
            # Center the crop box on target_cx and clamp
            tx = int(target_cx * width) - target_width // 2
            tx = max(0, min(width - target_width, tx))
            raw_x.append(tx)
            
        # Smooth coordinates using a moving average window (30 frames = ~1 sec)
        smooth_x = []
        window_size = 30
        for idx in range(frame_count):
            start_win = max(0, idx - window_size // 2)
            end_win = min(frame_count, idx + window_size // 2 + 1)
            sub_segment = raw_x[start_win:end_win]
            avg_x = int(sum(sub_segment) / len(sub_segment))
            smooth_x.append(avg_x)
            
        # Generate cropped video without audio using OpenCV
        temp_cropped_no_audio = self.temp / "cropped_no_audio.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out_video = cv2.VideoWriter(
            str(temp_cropped_no_audio),
            fourcc,
            fps,
            (out_width, out_height)
        )
        
        cap = cv2.VideoCapture(str(trimmed_path))
        for i in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break
            
            print_progress("Memotong & meresize aspek rasio (Smart Crop)", i + 1, frame_count)
            
            cx = smooth_x[i] if i < len(smooth_x) else (width - target_width) // 2
            # Clamp crop box to video bounds
            cx = max(0, min(width - target_width, cx))
            cy = max(0, (height - target_height) // 2)
            
            cropped_frame = frame[cy : cy + target_height, cx : cx + target_width]
            resized_frame = cv2.resize(cropped_frame, (out_width, out_height), interpolation=cv2.INTER_LANCZOS4)
            out_video.write(resized_frame)
            
        cap.release()
        out_video.release()
        clear_progress("Memotong & meresize aspek rasio (Smart Crop)")
        
        # Merge with audio from trimmed_path and encode via FFmpeg
        cropped_path = self.temp / "cropped.mp4"
        with TerminalSpinner("Menggabungkan audio & mengompres video"):
            ffmpeg.encode(
                temp_cropped_no_audio,
                cropped_path,
                width=None,
                height=None,
                audio_src=trimmed_path
            )
        
        # Cleanup temporary cropped file
        if temp_cropped_no_audio.exists():
            temp_cropped_no_audio.unlink()
            
        steps.append("cropped")

        # 5. Burn subtitles
        if burn_subtitles and srt_path:
            final_path = self.temp / "output.mp4"
            with TerminalSpinner("Menempelkan subtitle ke dalam video (Burning)"):
                ffmpeg.burn_subtitles(cropped_path, final_path, srt_path)
            steps.append("subtitles_burned")
        else:
            final_path = cropped_path

        steps.append("complete")

        return {
            "output_path": str(final_path),
            "srt_path": str(srt_path) if (export_srt and srt_path) else None,
            "steps": steps,
        }
