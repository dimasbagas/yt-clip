#!/usr/bin/env python3
"""
ClipOS — AI Terminal Video Clipper
CLI tool for AI-powered video clipping from the terminal.

Usage:
  clipos import <file>              Import local video
  clipos import youtube <url>       Import video from YouTube
  clipos clip <start> <end>         Set clip range (00:00:00 format)
  clipos subtitles <video>          Generate subtitles with Whisper AI
  clipos subtitles export <fmt>     Export subtitles as srt/vtt
  clipos trim <video> <start> <end> Trim video without AI processing
  clipos detect <video>             Run face detection on video
  clipos render                     Full AI pipeline: trim + subs + crop
  clipos status                     Show current session info
  clipos reset                      Clear current session
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Ensure backend modules are importable
BACKEND_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BACKEND_DIR))

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SESSION_DIR = Path.home() / ".clipos"
SESSION_FILE = SESSION_DIR / "session.json"


# ─── Terminal Styling ───

class Style:
    # ANSI Color Codes
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Bright Colors (Premium Look)
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    
    RESET = "\033[0m"

    @staticmethod
    def ok(msg):
        return f"  {Style.GREEN}✓{Style.RESET} {msg}"

    @staticmethod
    def info(msg):
        return f"  {Style.CYAN}⚙{Style.RESET} {msg}"

    @staticmethod
    def warn(msg):
        return f"  {Style.YELLOW}⚠{Style.RESET} {msg}"

    @staticmethod
    def err(msg):
        return f"  {Style.RED}✗{Style.RESET} {msg}"

    @staticmethod
    def header(msg):
        border = "═" * (len(msg) + 4)
        return f"\n{Style.BOLD}{Style.CYAN}╔{border}╗{Style.RESET}\n{Style.BOLD}{Style.CYAN}║  {msg}  ║{Style.RESET}\n{Style.BOLD}{Style.CYAN}╚{border}╝{Style.RESET}"

    @staticmethod
    def section(msg):
        return f"\n{Style.BOLD}{Style.MAGENTA}▸ {msg}{Style.RESET}"

    @staticmethod
    def footer():
        return f"{Style.GRAY}{'─' * 60}{Style.RESET}"

    @staticmethod
    def title(msg):
        return f"{Style.BOLD}{Style.CYAN}{msg}{Style.RESET}"

    @staticmethod
    def subtitle(msg):
        return f"{Style.MAGENTA}{msg}{Style.RESET}"


def log(msg):
    print(f"{msg}")


# ─── Session Management ───

def load_session() -> dict:
    if SESSION_FILE.exists():
        return json.loads(SESSION_FILE.read_text())
    return {"video": None, "clip_start": None, "clip_end": None}


def save_session(session: dict):
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(session, indent=2))


def reset_session():
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
    log(Style.ok("Session cleared"))


# ─── Subcommands ───

def cmd_import(args):
    from render_engine.ffmpeg_client import FFmpegClient

    path = Path(args.path)
    if not path.exists():
        log(Style.err(f"File not found: {path}"))
        sys.exit(1)

    log(Style.info(f"Importing: {path.name}"))
    ff = FFmpegClient()
    probe = ff.probe(str(path))
    stream = next((s for s in probe.get("streams", []) if s["codec_type"] == "video"), {})
    duration = float(probe.get("format", {}).get("duration", 0))

    session = load_session()
    session["video"] = str(path.resolve())
    save_session(session)

    log(Style.ok(f"Imported: {path.name}"))
    log(f"  Duration: {duration:.1f}s")
    log(f"  Resolution: {stream.get('width', '?')}x{stream.get('height', '?')}")
    log(f"  Path: {path.resolve()}")


def cmd_import_youtube(args):
    from youtube_import.downloader import YouTubeDownloader

    url = args.url
    log(Style.info(f"Fetching: {url}"))
    dl = YouTubeDownloader()

    info = dl.extract_info(url)
    log(Style.ok(f"Found: {info['title']} ({info['duration']}s)"))

    if not args.analyze_only:
        log(Style.info("Downloading..."))
        result = dl.download(url, args.quality)
        session = load_session()
        session["video"] = result["path"]
        save_session(session)
        log(Style.ok(f"Downloaded: {result['title']}"))
        log(f"  Path: {result['path']}")
    else:
        log(Style.info("Analysis complete (--analyze-only)"))


def cmd_clip(args):
    session = load_session()
    if not session.get("video"):
        log(Style.err("No video imported. Run 'clipos import <file>' first"))
        sys.exit(1)

    session["clip_start"] = args.start
    session["clip_end"] = args.end
    save_session(session)

    log(Style.ok(f"Clip set: {args.start} -> {args.end}"))
    log(f"  Duration: {args.end}")


def cmd_subtitles(args):
    from render_engine.ffmpeg_client import FFmpegClient
    from subtitle_engine.whisper_client import WhisperClient
    from subtitle_engine.subtitle_formatter import format_subtitles

    video = args.video
    if not video:
        session = load_session()
        video = session.get("video")
    if not video or not Path(video).exists():
        log(Style.err("No video file. Specify path or import first"))
        sys.exit(1)

    log(Style.info("Extracting audio..."))
    ff = FFmpegClient()
    audio_path = Path(video).parent / ".clipos_audio.wav"
    ff.extract_audio(video, audio_path)

    log(Style.info("Running Whisper AI speech recognition..."))
    whisper = WhisperClient.get_instance()
    whisper.load()
    result = whisper.transcribe(str(audio_path), language=args.language)

    segs = result["segments"]
    log(Style.ok(f"Transcribed: {len(segs)} segments"))
    log(f"  Language: {result['language']}")

    # Save to files
    base = Path(video).with_suffix("")
    srt_path = base.with_suffix(".srt")
    vtt_path = base.with_suffix(".vtt")

    srt_path.write_text(format_subtitles(segs, "srt"), encoding="utf-8")
    vtt_path.write_text(format_subtitles(segs, "vtt"), encoding="utf-8")

    log(Style.ok(f"SRT: {srt_path}"))
    log(Style.ok(f"VTT: {vtt_path}"))

    # Print preview
    print()
    for seg in segs[:5]:
        print(f"  {Style.DIM}{seg['start']} -> {seg['end']}{Style.RESET}  {seg['text']}")
    if len(segs) > 5:
        print(f"  {Style.DIM}... and {len(segs) - 5} more segments{Style.RESET}")

    # Cleanup
    audio_path.unlink(missing_ok=True)


def cmd_subtitles_export(args):
    from subtitle_engine.subtitle_formatter import format_subtitles

    srt_path = Path(args.file) if args.file else Path.cwd() / "subtitles.srt"
    if not srt_path.exists():
        log(Style.err(f"Subtitles not found at {srt_path}"))
        log(Style.info("Generate subtitles first: clipos subtitles <video>"))
        sys.exit(1)

    import re
    segs = []
    for block in srt_path.read_text(encoding="utf-8").strip().split("\n\n"):
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            time_match = re.match(r"(\d+:\d+:\d+[.,]\d+)\s*-->\s*(\d+:\d+:\d+[.,]\d+)", lines[1])
            if time_match:
                segs.append({"start": time_match.group(1), "end": time_match.group(2), "text": "\n".join(lines[2:])})

    fmt = args.format
    content = format_subtitles(segs, fmt)
    out = Path.cwd() / f"subtitles.{fmt}"
    out.write_text(content, encoding="utf-8")
    log(Style.ok(f"Exported: {out}"))


def cmd_trim(args):
    from render_engine.ffmpeg_client import FFmpegClient

    video = args.video
    if not video:
        session = load_session()
        video = session.get("video")
    if not video or not Path(video).exists():
        log(Style.err("No video file"))
        sys.exit(1)

    out = args.output or Path(video).with_name(f"{Path(video).stem}_trimmed{Path(video).suffix}")

    log(Style.info(f"Trimming: {args.start} -> {args.end}"))
    ff = FFmpegClient()
    ff.trim(video, out, args.start, args.end)
    log(Style.ok(f"Trimmed: {out}"))


def cmd_detect(args):
    import cv2
    from tracking_engine.yolo_detector import YOLODetector

    video = args.video
    if not video:
        session = load_session()
        video = session.get("video")
    if not video or not Path(video).exists():
        log(Style.err("No video file"))
        sys.exit(1)

    log(Style.info("Running face detection..."))
    yolo = YOLODetector.get_instance()
    yolo.load()

    cap = cv2.VideoCapture(video)
    total = 0
    faces_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if total % args.every == 0:
            faces = yolo.detect_faces(frame)
            if faces:
                faces_count += len(faces)
                log(f"  Frame {total}: {len(faces)} face(s)")
        total += 1

    cap.release()
    log(Style.ok(f"Detection done: {total} frames, {faces_count} faces detected"))


def cmd_render(args):
    session = load_session()
    video = args.video or session.get("video")
    if not video or not Path(video).exists():
        log(Style.err("No video. Import first or specify --video"))
        sys.exit(1)

    start = args.start or session.get("clip_start") or "00:00:00"
    end = args.end or session.get("clip_end") or "00:00:10"
    ratio = args.aspect_ratio
    mode = args.tracking_mode
    subtitle = not args.no_subtitles

    log(Style.header("RENDER PIPELINE"))
    log(f"  Video:    {Path(video).name}")
    log(f"  Clip:     {start} -> {end}")
    log(f"  Ratio:    {ratio}")
    log(f"  Tracking: {mode}")
    log(f"  Subs:     {'yes' if subtitle else 'no'}")
    print()

    from ai_processing.pipeline import Pipeline
    pipeline = Pipeline()

    steps = [
        ("Audio Extraction", 5),
        ("Whisper Transcription", 30),
        ("Clip Trimming", 10),
        ("Auto Crop & Scale", 15),
        ("Final Encoding", 40),
    ]

    for i, (step_name, weight) in enumerate(steps):
        if step_name == "Whisper Transcription" and not subtitle:
            log(Style.info(f"[{i+1}/{len(steps)}] {step_name} -- skipped"))
            continue
        log(Style.info(f"[{i+1}/{len(steps)}] {step_name}..."))
        time.sleep(0.5 if args.dry_run else 0.1)

    if args.dry_run:
        log(Style.ok("Dry run complete"))
        return

    result = pipeline.run(
        video_path=video,
        clip_start=start,
        clip_end=end,
        aspect_ratio=ratio,
        tracking_mode=mode,
        generate_subtitles=subtitle,
        burn_subtitles=subtitle,
    )

    print()
    log(Style.ok("Render complete!"))
    log(f"  Output: {result['output_path']}")


def cmd_status(_args):
    session = load_session()
    video = session.get("video")
    print(f"{Style.BOLD}{Style.GREEN}>>> CLIPOS SESSION <<<{Style.RESET}")
    if video and Path(video).exists():
        from render_engine.ffmpeg_client import FFmpegClient
        ff = FFmpegClient()
        probe = ff.probe(video)
        dur = float(probe.get("format", {}).get("duration", 0))
        print(f"  Video:     {Style.GREEN}{Path(video).name}{Style.RESET}")
        print(f"  Duration:  {dur:.1f}s")
    else:
        print(f"  Video:     {Style.DIM}none{Style.RESET}")

    print(f"  Clip:      {session.get('clip_start', '-')} -> {session.get('clip_end', '-')}")
    print(f"{Style.DIM}---{Style.RESET}")


def cmd_interactive(args):
    print()
    print(f"{Style.BOLD}{Style.CYAN}╔════════════════════════════════════════════════════════════╗{Style.RESET}")
    print(f"{Style.BOLD}{Style.CYAN}║{Style.RESET}  {Style.BOLD}ClipOS — AI Terminal Video Clipper{Style.RESET}")
    print(f"{Style.BOLD}{Style.CYAN}║{Style.RESET}  {Style.CYAN}Interactive Guided Mode{Style.RESET}")
    print(f"{Style.BOLD}{Style.CYAN}╚════════════════════════════════════════════════════════════╝{Style.RESET}")
    print(f"{Style.CYAN}This wizard will guide you through the process step-by-step.{Style.RESET}")
    print()

    # 1. Video Input
    video_path = None
    while not video_path:
        source = input("  ❯ Enter YouTube URL or local video file path: ").strip()
        if not source:
            print(Style.warn("Input cannot be empty. Please try again."))
            continue

        if source.startswith("http://") or source.startswith("https://") or "youtube.com" in source or "youtu.be" in source:
            from youtube_import.downloader import YouTubeDownloader
            print(Style.info(f"Connecting to YouTube and analyzing: {source}..."))
            dl = YouTubeDownloader()
            try:
                info = dl.extract_info(source)
                print(Style.ok(f"Found: {info['title']} ({info['duration']}s)"))
                confirm = input("    Download this video? (y/n) [y]: ").strip().lower()
                if confirm not in ("", "y", "yes"):
                    print(Style.warn("Cancelled download."))
                    continue
                print(Style.info("Downloading from YouTube... This might take a moment..."))
                result = dl.download(source, "best")
                video_path = result["path"]
                print(Style.ok(f"Downloaded and saved to: {video_path}"))
            except Exception as e:
                print(Style.err(f"YouTube error: {e}"))
                continue
        else:
            path = Path(source)
            if not path.exists() or not path.is_file():
                print(Style.err(f"Local file not found: {source}. Please verify the path."))
                continue
            video_path = str(path.resolve())
            print(Style.ok(f"Selected local video: {path.name}"))

    # 2. Aspect Ratio Selection
    print()
    print(f"{Style.MAGENTA}▸ Select Aspect Ratio / Format:{Style.RESET}")
    print(f"  {Style.CYAN}1.{Style.RESET} Portrait  (9:16 - TikTok / Shorts / Reels) {Style.GREEN}[Default]{Style.RESET}")
    print(f"  {Style.CYAN}2.{Style.RESET} Landscape (16:9 - YouTube / Standard)")
    print(f"  {Style.CYAN}3.{Style.RESET} Square    (1:1  - Instagram)")
    ratio_choice = input(f"  {Style.CYAN}Choice (1-3) [1]:{Style.RESET} ").strip()
    if ratio_choice == "2":
        ratio = "16:9"
    elif ratio_choice == "3":
        ratio = "1:1"
    else:
        ratio = "9:16"
    print(Style.ok(f"Aspect ratio set to: {Style.BOLD}{ratio}{Style.RESET}"))

    # 3. Clip timestamps
    print()
    print(f"{Style.MAGENTA}▸ Set Clip Timestamps:{Style.RESET}")
    from render_engine.ffmpeg_client import FFmpegClient
    ff = FFmpegClient()
    probe = ff.probe(video_path)
    dur = float(probe.get("format", {}).get("duration", 0))
    print(f"  {Style.CYAN}Source Video Duration:{Style.RESET} {Style.BOLD}{dur:.2f}s{Style.RESET}")
    print(f"  {Style.CYAN}You can enter multiple timestamp ranges in a single line!{Style.RESET}")
    print(f"  {Style.GRAY}Examples: 00:01:00-00:01:10, 00:03:00-00:03:20{Style.RESET}")
    print(f"  {Style.GRAY}          [00:01:00] [00:01:10] [00:03:00] [00:03:20]{Style.RESET}")
    print(f"  {Style.GRAY}          00:10-00:20 01:00-01:30{Style.RESET}")
    
    ts_input = input(f"  {Style.CYAN}Enter timestamps [00:00:00-00:00:10]:{Style.RESET} ").strip()
    if not ts_input:
        ts_input = "00:00:00-00:00:10"
        
    # Parser to extract all start and end ranges
    import re
    # Clean brackets and spacing
    cleaned = ts_input.replace("[", "").replace("]", " ")
    
    # Split ranges by comma, semicolon, tab, or newline
    parts = re.split(r'[,;\n\t]+', cleaned)
    if len(parts) == 1 and "-" not in parts[0] and "to" not in parts[0]:
        # They might have typed: [00:00] [03:04] [05:04] [11:54]
        # which becomes "00:00   03:04   05:04   11:54"
        # Let's group them into pairs of start and end!
        subparts = [p.strip() for p in re.split(r'\s+', cleaned) if p.strip()]
        clips = []
        for j in range(0, len(subparts) - 1, 2):
            clips.append((subparts[j], subparts[j+1]))
    else:
        if len(parts) == 1:
            # Maybe separated by space, e.g. "00:00-03:04 05:04-11:54"
            parts = [p.strip() for p in re.split(r'\s+', cleaned) if p.strip()]
            
        clips = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            subparts = re.split(r'[-\s/]+|to', part)
            subparts = [p.strip() for p in subparts if p.strip()]
            if len(subparts) >= 2:
                clips.append((subparts[0], subparts[1]))
                
    if not clips:
        # Fallback
        clips = [("00:00:00", "00:00:10")]
        
    print()
    print(Style.ok(f"Detected {len(clips)} clip range(s) to process:"))
    for idx, (st, et) in enumerate(clips, 1):
        print(f"  {Style.CYAN}Clip #{idx}:{Style.RESET} {Style.BOLD}{st}{Style.RESET} → {Style.BOLD}{et}{Style.RESET}")

    # 4. Tracking Mode Selection
    tracking_mode = "podcast"
    if ratio != "16:9":
        print()
        print(f"{Style.MAGENTA}▸ Select AI Smart Camera Tracking Mode:{Style.RESET}")
        print(f"  {Style.CYAN}1.{Style.RESET} Podcast   (Dual speakers, smooth switching) {Style.GREEN}[Default]{Style.RESET}")
        print(f"  {Style.CYAN}2.{Style.RESET} Interview (Q&A style, focus on active speaker)")
        print(f"  {Style.CYAN}3.{Style.RESET} Gaming    (Facecam tracking, stable crop)")
        print(f"  {Style.CYAN}4.{Style.RESET} Streamer  (Single speaker, center-locked)")
        print(f"  {Style.CYAN}5.{Style.RESET} Cinematic (Slow pans, wide-to-tight)")
        print(f"  {Style.CYAN}6.{Style.RESET} Center    (Static crop, no face tracking)")
        track_choice = input(f"  {Style.CYAN}Choice (1-6) [1]:{Style.RESET} ").strip()
        if track_choice == "2":
            tracking_mode = "interview"
        elif track_choice == "3":
            tracking_mode = "gaming"
        elif track_choice == "4":
            tracking_mode = "streamer"
        elif track_choice == "5":
            tracking_mode = "cinematic"
        elif track_choice == "6":
            tracking_mode = "center"
        else:
            tracking_mode = "podcast"
    else:
        tracking_mode = "center"
        
    print(Style.ok(f"Camera tracking mode: {Style.BOLD}{tracking_mode}{Style.RESET}"))

    # 4.5 Export Subtitle Option
    print()
    print(f"{Style.MAGENTA}▸ Subtitle Export Options:{Style.RESET}")
    print(f"  {Style.CYAN}1.{Style.RESET} Burn subtitle into video (default)")
    print(f"  {Style.CYAN}2.{Style.RESET} Export video + separate .srt file (no burn)")
    print(f"  {Style.CYAN}3.{Style.RESET} Video only (no subtitle)")
    subtitle_choice = input(f"  {Style.CYAN}Choice (1-3) [1]:{Style.RESET} ").strip()
    
    if subtitle_choice == "2":
        burn_subtitles = False
        export_srt = True
        subtitle_mode = "Export .srt only"
    elif subtitle_choice == "3":
        burn_subtitles = False
        export_srt = False
        subtitle_mode = "No subtitle"
    else:
        burn_subtitles = True
        export_srt = False
        subtitle_mode = "Burn into video"
    
    print(Style.ok(f"Subtitle mode: {Style.BOLD}{subtitle_mode}{Style.RESET}"))

    # 5. Export Directory Selection
    print()
    print(f"{Style.MAGENTA}▸ Export Directory:{Style.RESET}")
    default_export = Path(__file__).parent.parent.resolve() / "exports"
    export_dir_str = input(f"  {Style.CYAN}Enter path [{default_export}]:{Style.RESET} ").strip()
    if export_dir_str:
        export_dir = Path(export_dir_str)
    else:
        export_dir = default_export
        
    export_dir.mkdir(parents=True, exist_ok=True)
    print(Style.ok(f"Export directory set to: {Style.BOLD}{export_dir}{Style.RESET}"))

    # 6. Run the Render Pipeline
    print()
    print(f"{Style.BOLD}{Style.CYAN}╔════════════════════════════════════════════════════════════╗{Style.RESET}")
    print(f"{Style.BOLD}{Style.CYAN}║{Style.RESET}  {Style.BOLD}{Style.GREEN}▶ RUNNING PIPELINE{Style.RESET}")
    print(f"{Style.BOLD}{Style.CYAN}╚════════════════════════════════════════════════════════════╝{Style.RESET}")
    from ai_processing.pipeline import Pipeline
    pipeline = Pipeline()
    
    import shutil
    from config import TEMP_DIR
    video_filename = Path(video_path).stem
    
    # Use TEMP_DIR from config which is already set correctly
    temp_dir = TEMP_DIR
        
    for idx, (st, et) in enumerate(clips, 1):
        print()
        print(f"{Style.BOLD}{Style.MAGENTA}╔════════════════════════════════════════════════════════════╗{Style.RESET}")
        print(f"{Style.BOLD}{Style.MAGENTA}║{Style.RESET}  {Style.BOLD}{Style.YELLOW}⏳ PROCESSING CLIP #{idx}{Style.RESET}  {Style.GRAY}({st} → {et}){Style.RESET}")
        print(f"{Style.BOLD}{Style.MAGENTA}╚════════════════════════════════════════════════════════════╝{Style.RESET}")
        
        # Clean temp directory to prevent any subtitle/video leftovers
        import glob
        for temp_f in glob.glob(str(temp_dir / "*.mp4")) + glob.glob(str(temp_dir / "*.wav")) + glob.glob(str(temp_dir / "*.srt")) + glob.glob(str(temp_dir / "*.vtt")):
            try:
                os.remove(temp_f)
            except Exception:
                pass
                
        try:
            result = pipeline.run(
                video_path=video_path,
                clip_start=st,
                clip_end=et,
                aspect_ratio=ratio,
                tracking_mode=tracking_mode,
                generate_subtitles=True,
                burn_subtitles=burn_subtitles,
                export_srt=export_srt
            )
            
            # Format filename with safe timestamps: e.g. sample_00_10_00_to_00_10_05.mp4
            safe_st = st.replace(":", "_")
            safe_et = et.replace(":", "_")
            
            dest_video = export_dir / f"{video_filename}_{safe_st}_to_{safe_et}.mp4"
            src_video = Path(result["output_path"])
            
            if src_video.exists():
                shutil.copy2(src_video, dest_video)
                
            # Copy subtitles only if export_srt is True
            sub_copied = False
            if export_srt:
                print(f"  {Style.CYAN}[DEBUG] export_srt=True, attempting to copy .srt files...{Style.RESET}")
                for ext in ("srt", "vtt"):
                    temp_sub = temp_dir / f"subtitles.{ext}"
                    print(f"  {Style.CYAN}[DEBUG] Checking {temp_sub}...{Style.RESET}")
                    if temp_sub.exists():
                        dest_sub = export_dir / f"{video_filename}_{safe_st}_to_{safe_et}.{ext}"
                        try:
                            shutil.copy2(temp_sub, dest_sub)
                            print(f"  {Style.CYAN}[DEBUG] Copied {ext} to {dest_sub}{Style.RESET}")
                            sub_copied = True
                        except Exception as copy_err:
                            print(f"  {Style.RED}[DEBUG] Error copying {ext}: {copy_err}{Style.RESET}")
                    else:
                        print(f"  {Style.CYAN}[DEBUG] File not found: {temp_sub}{Style.RESET}")
            else:
                print(f"  {Style.CYAN}[DEBUG] export_srt=False, skipping .srt copy{Style.RESET}")
                    
            print()
            print(Style.ok(f"Clip #{idx} completed successfully!"))
            print(f"  {Style.CYAN}Video:{Style.RESET}     {Style.BOLD}{dest_video.resolve()}{Style.RESET}")
            if sub_copied:
                srt_file = export_dir / f"{video_filename}_{safe_st}_to_{safe_et}.srt"
                if srt_file.exists():
                    print(f"  {Style.CYAN}Subtitles:{Style.RESET} {Style.BOLD}{srt_file.resolve()}{Style.RESET}")
                
        except Exception as e:
            print()
            print(Style.err(f"Failed to process Clip #{idx} ({st} -> {et}): {e}"))
            import traceback
            traceback.print_exc()
            
    print()
    print(f"{Style.BOLD}{Style.GREEN}╔════════════════════════════════════════════════════════════╗{Style.RESET}")
    print(f"{Style.BOLD}{Style.GREEN}║{Style.RESET}  {Style.BOLD}{Style.GREEN}✓ SUCCESS — ALL CLIPS PROCESSED!{Style.RESET}")
    print(f"{Style.BOLD}{Style.GREEN}╚════════════════════════════════════════════════════════════╝{Style.RESET}")
    print(Style.ok(f"Check your export directory: {Style.BOLD}{export_dir.resolve()}{Style.RESET}"))
    print()


# ─── Main Parser ───

def main():
    parser = argparse.ArgumentParser(
        prog="clipos",
        description="ClipOS — AI Terminal Video Clipper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clipos import video.mp4
  clipos import youtube https://youtube.com/watch?v=...
  clipos clip 00:12:30 00:14:20
  clipos subtitles video.mp4
  clipos render --preset tiktok
  clipos trim video.mp4 00:01:00 00:01:30 -o clip.mp4
  clipos detect video.mp4
  clipos status
        """,
    )

    sub = parser.add_subparsers(dest="command")

    # import
    p_import = sub.add_parser("import", help="Import a local video")
    p_import.add_argument("path", help="Path to video file")

    # import youtube
    p_yt = sub.add_parser("youtube", help="Import from YouTube")
    p_yt.add_argument("url", help="YouTube URL")
    p_yt.add_argument("--quality", default="best", help="Video quality")
    p_yt.add_argument("--analyze-only", action="store_true", help="Don't download, only show info")

    # clip
    p_clip = sub.add_parser("clip", help="Set clip in/out points")
    p_clip.add_argument("start", help="Start time (00:00:00)")
    p_clip.add_argument("end", help="End time (00:00:00)")

    # subtitles
    p_sub = sub.add_parser("subtitles", help="Generate subtitles with Whisper AI")
    p_sub.add_argument("video", nargs="?", help="Video file path (uses session if omitted)")
    p_sub.add_argument("--language", "-l", default=None, help="Language code (auto-detect if omitted)")

    # subtitles export
    p_sub_e = sub.add_parser("subtitles-export", help="Export subtitles to different format")
    p_sub_e.add_argument("format", choices=["srt", "vtt"], help="Output format")
    p_sub_e.add_argument("--file", "-f", help="Input subtitle file")

    # trim
    p_trim = sub.add_parser("trim", help="Trim video without AI processing")
    p_trim.add_argument("video", nargs="?", help="Video file path")
    p_trim.add_argument("start", help="Start time")
    p_trim.add_argument("end", help="End time")
    p_trim.add_argument("--output", "-o", help="Output file path")

    # detect
    p_detect = sub.add_parser("detect", help="Run face detection on video")
    p_detect.add_argument("video", nargs="?", help="Video file path")
    p_detect.add_argument("--every", type=int, default=30, help="Check every N frames")

    # render
    p_render = sub.add_parser("render", help="Full AI rendering pipeline")
    p_render.add_argument("video", nargs="?", help="Video file path")
    p_render.add_argument("--start", help="Clip start time")
    p_render.add_argument("--end", help="Clip end time")
    p_render.add_argument("--aspect-ratio", choices=["9:16", "16:9", "1:1"], default="9:16")
    p_render.add_argument("--tracking-mode", choices=["podcast", "interview", "gaming", "streamer", "cinematic", "center"], default="podcast")
    p_render.add_argument("--no-subtitles", action="store_true", help="Skip subtitle generation")
    p_render.add_argument("--dry-run", action="store_true", help="Show pipeline steps without running")
    p_render.add_argument("--preset", help="Shortcut: tiktok, shorts, reels, landscape")

    # status
    sub.add_parser("status", help="Show current session info")

    # reset
    sub.add_parser("reset", help="Clear current session")

    # interactive
    sub.add_parser("interactive", help="Run interactive guided clipper")

    args = parser.parse_args()

    if not args.command:
        print()
        print(f"{Style.BOLD}{Style.CYAN}╔════════════════════════════════════════════════════════════╗{Style.RESET}")
        print(f"{Style.BOLD}{Style.CYAN}║{Style.RESET}  {Style.BOLD}{Style.CYAN}ClipOS — AI Terminal Video Clipper{Style.RESET}")
        print(f"{Style.BOLD}{Style.CYAN}╚════════════════════════════════════════════════════════════╝{Style.RESET}")
        choice = input(f"{Style.CYAN}Start interactive guided mode? (y/n) [y]:{Style.RESET} ").strip().lower()
        if choice in ("", "y", "yes"):
            cmd_interactive(None)
            sys.exit(0)
        else:
            parser.print_help()
            sys.exit(1)

    # ─── Dispatch ───

    if args.command == "import":
        cmd_import(args)
    elif args.command == "youtube":
        cmd_import_youtube(args)
    elif args.command == "clip":
        cmd_clip(args)
    elif args.command == "subtitles":
        cmd_subtitles(args)
    elif args.command == "subtitles-export":
        cmd_subtitles_export(args)
    elif args.command == "trim":
        cmd_trim(args)
    elif args.command == "detect":
        cmd_detect(args)
    elif args.command == "render":
        cmd_render(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "reset":
        reset_session()
    elif args.command == "interactive":
        cmd_interactive(args)


if __name__ == "__main__":
    main()
