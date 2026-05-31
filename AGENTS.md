# ClipOS — AI Terminal Video Clipper

Proyek desktop app AI untuk mengubah video panjang jadi clip pendek otomatis.

## Tech Stack

- **Frontend:** React + TypeScript + Vite + TailwindCSS v4 + Tauri v2
- **Backend:** Python + FastAPI + uvicorn
- **AI:** Faster-Whisper + YOLOv8 + OpenCV
- **Video:** FFmpeg + NVENC + yt-dlp

## Struktur Proyek

```
yt-clip/
├── clipos.bat          # CLI entry (panggil dari mana aja)
├── dev.bat             # Start backend + frontend
├── frontend/           # React + Vite + Tauri
│   └── src-tauri/      # Rust shell (Tauri)
├── backend/            # Python FastAPI + CLI
│   ├── clipos.py       # CLI tool (argparse)
│   ├── main.py         # FastAPI server
│   ├── config.py
│   ├── subtitle_engine/
│   ├── render_engine/
│   ├── tracking_engine/
│   ├── youtube_import/
│   └── ai_processing/
├── models/             # Whisper + YOLO model weights
├── exports/            # Output renders
└── temp/               # Temporary files
```

## CLI Usage

```bash
clipos import <file>                    # Import video lokal
clipos youtube <url>                    # Import dari YouTube
clipos clip <start> <end>               # Set range clip
clipos subtitles <video>                # Generate subtitle via Whisper
clipos subtitles-export <srt|vtt>       # Export subtitle
clipos trim <video> <start> <end>       # Trim tanpa AI
clipos detect <video>                   # Face detection
clipos render                           # Pipeline full AI
clipos render --dry-run                 # Show pipeline steps
clipos status                           # Cek session
clipos reset                            # Hapus session
```

Contoh workflow:
```bash
clipos import video.mp4
clipos clip 00:12:30 00:14:20
clipos subtitles
clipos render --preset tiktok
```

## Commands

### Frontend

| Perintah | Keterangan |
|----------|------------|
| `cd frontend && npm run dev` | Start Vite dev server (port 5173) |
| `cd frontend && npm run build` | TypeScript check + Vite build |
| `cd frontend && npm run tauri:dev` | Start Tauri dev mode |
| `cd frontend && npm run tauri:build` | Build Tauri production installer |

### Backend

| Perintah | Keterangan |
|----------|------------|
| `cd backend && .venv/Scripts/python -m uvicorn main:app --host 127.0.0.1 --port 8899 --reload` | Start API server |
| `clipos import <file>` | CLI: import video |
| `clipos render --dry-run` | CLI: simulate pipeline |

### Testing

| Perintah | Keterangan |
|----------|------------|
| `cd frontend && npx tsc --noEmit` | TypeScript type check |
| `cd frontend && npx vite build` | Frontend production build |

## Environment

- Python: 3.11.15 (venv di `backend/.venv/`)
- Node: 22.14.0
- FFmpeg: 8.1.1 (NVENC support)
- Rust: 1.96.0 (butuh VS C++ Build Tools)
- OS: Windows

## API Endpoints (port 8899)

`GET /api/health` — Status server
`GET /api/system` — Info NVENC + model
`POST /api/upload` — Upload video file
`POST /api/clip/trim` — Trim video
`POST /api/subtitles/generate` — Generate subtitle via Whisper
`POST /api/subtitles/export` — Export SRT/VTT
`POST /api/tracking/detect` — Face detection per frame
`POST /api/render` — Full pipeline render

## Catatan Penting

- Tauri butuh **Visual Studio C++ Build Tools** (Desktop development with C++ workload)
- Whisper model akan auto-download saat pertama kali digunakan
- YOLO model auto-download via Ultralytics
- GPU NVENC auto-terdeteksi untuk encoding lebih cepat
