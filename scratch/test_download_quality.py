import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from youtube_import.downloader import YouTubeDownloader
from render_engine.ffmpeg_client import FFmpegClient

def main():
    print("Testing YouTube downloader quality...")
    url = "https://youtu.be/3x9dcDQ61o4?si=QfXYJjoCznyZVbek" # 'Obrolan Setelah Marapthon'
    
    dl = YouTubeDownloader()
    print("1. Extracting info...")
    info = dl.extract_info(url)
    print(f"   Title: {info['title']}")
    print(f"   Duration: {info['duration']}s")
    
    print("\n2. Downloading video...")
    res = dl.download(url, quality="best")
    video_path = Path(res["path"])
    print(f"   Downloaded path: {video_path}")
    print(f"   Size: {video_path.stat().st_size / (1024*1024):.2f} MB")
    
    print("\n3. Probing downloaded video resolution...")
    ff = FFmpegClient()
    probe = ff.probe(str(video_path))
    stream = next((s for s in probe.get("streams", []) if s["codec_type"] == "video"), {})
    w = stream.get("width")
    h = stream.get("height")
    print(f"   Resolution: {w}x{h}")
    
    if w > 640 or h > 360:
        print("   [SUCCESS] Quality is higher than 360p fallback!")
    else:
        print("   [FAIL] Quality is still 360p fallback!")

if __name__ == "__main__":
    main()
