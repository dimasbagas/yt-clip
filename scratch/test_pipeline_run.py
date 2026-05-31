import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from ai_processing.pipeline import Pipeline
from render_engine.ffmpeg_client import FFmpegClient

def main():
    print("Testing full Pipeline render with 1080p source and Lanczos4 upscaling...")
    video_path = "temp/youtube/Obrolan Setelah Marapthon.mp4"
    
    pipeline = Pipeline()
    print("1. Running pipeline for a 5-second clip...")
    import time
    start_time = time.time()
    
    result = pipeline.run(
        video_path=video_path,
        clip_start="00:00:00",
        clip_end="00:00:05",
        aspect_ratio="9:16",
        tracking_mode="podcast",
        generate_subtitles=True,
        burn_subtitles=True
    )
    
    elapsed = time.time() - start_time
    output_path = Path(result["output_path"])
    print(f"\n2. Render complete in {elapsed:.2f} seconds!")
    print(f"   Output path: {output_path}")
    print(f"   Steps executed: {result['steps']}")
    
    print("\n3. Probing output video...")
    ff = FFmpegClient()
    probe = ff.probe(str(output_path))
    stream = next((s for s in probe.get("streams", []) if s["codec_type"] == "video"), {})
    w = stream.get("width")
    h = stream.get("height")
    print(f"   Output resolution: {w}x{h}")
    
    if w == 1080 and h == 1920:
        print("   [SUCCESS] Output is exactly Full HD portrait 1080x1920!")
    else:
        print("   [FAIL] Output resolution is incorrect!")

if __name__ == "__main__":
    main()
