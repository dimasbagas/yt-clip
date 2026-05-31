<div align="center">

# 🎬 ClipOS — AI Terminal Video Clipper

**Ubah Video Panjang Jadi Klip Viral Secara Otomatis dengan Kekuatan AI Lokal.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![FFmpeg: 8.1.1](https://img.shields.io/badge/FFmpeg-8.1.1+-green.svg)](https://ffmpeg.org/)

[Fitur Utama](#-fitur-utama) • [Instalasi](#-instalasi-cepat) • [Cara Penggunaan](#-cara-penggunaan) • [Teknologi](#-tech-stack)

</div>

---

## 💡 Apa itu ClipOS?

**ClipOS** adalah alat terminal berbasis AI mutakhir yang dirancang untuk membantu kreator konten memotong, memformat, dan mengoptimalkan video panjang menjadi klip pendek (TikTok, Shorts, Reels) dalam hitungan detik. 

Berbeda dengan alat lain, ClipOS bekerja **100% secara lokal** di komputer Anda, menjaga privasi data Anda tetap aman tanpa memerlukan biaya API eksternal.

## ✨ Fitur Utama

*   🚀 **Smart-Tracking Camera:** AI secara otomatis melacak pergerakan wajah dan aktivitas mulut (*Mouth Motion Tracking*) untuk memastikan kamera selalu fokus pada pembicara aktif.
*   🎙️ **Whisper AI Subtitles:** Transkripsi suara ke teks yang sangat akurat menggunakan model *Faster-Whisper*.
*   💎 **Full HD 1080p Export:** Kualitas ekspor super tajam dengan interpolasi **Lanczos4**, memastikan video upscaling tetap terlihat premium.
*   🎞️ **Opsi Subtitle Fleksibel:** Pilih antara membakar subtitle langsung ke video, mengekspor file `.srt` terpisah untuk diedit, atau video bersih tanpa teks.
*   🔥 **Akselerasi GPU (NVENC):** Deteksi otomatis GPU NVIDIA untuk proses rendering kilat tanpa membebani CPU.
*   📺 **YouTube Downloader Terintegrasi:** Cukup masukkan URL, dan ClipOS akan mengambil versi resolusi tertinggi (1080p/2K/4K) secara otomatis.

---

## 🚀 Instalasi Cepat (Windows)

ClipOS didistribusikan sebagai aplikasi mandiri yang tidak memerlukan instalasi Python di komputer target. Pembeli cukup menjalankan satu perintah di bawah ini di terminal PowerShell untuk menginstal.

### ⚙️ Cara Install (1 Perintah)

Buka **PowerShell** dan jalankan perintah satu baris berikut:

```powershell
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/dimasbagas/yt-clip/master/install.ps1 | iex"
```

*Selesai! Perintah `clipos` sekarang tersedia secara global di komputer Anda.*

### 🗑️ Cara Uninstall
Jika ingin menghapus ClipOS sepenuhnya dari sistem:
1. Hapus folder program: `C:\Users\[Username]\AppData\Local\Programs\ClipOS`
2. Hapus shortcut "ClipOS" dari Desktop.

---

## 🛠 Cara Penggunaan

ClipOS dirancang untuk kemudahan penggunaan melalui terminal. Anda bisa memilih mode interaktif yang dipandu atau menggunakan perintah CLI langsung.

### 🎮 Mode Interaktif (Direkomendasikan)
Cukup ketik perintah berikut dan ikuti instruksi di layar:
```powershell
clipos interactive
```

### ⚡ Perintah Cepat
| Perintah | Deskripsi |
|----------|-----------|
| `clipos youtube <URL>` | Download video langsung dari YouTube |
| `clipos import <FILE>` | Impor video lokal ke dalam session |
| `clipos subtitles` | Generate subtitle menggunakan AI |
| `clipos render` | Jalankan pipeline render AI penuh |
| `clipos --help` | Lihat bantuan perintah lengkap |

---

## 🎨 Tampilan Premium
ClipOS menghadirkan interface terminal yang modern dengan:
- **Loading Spinners:** Animasi gelombang ASCII untuk proses latar belakang.
- **Real-time Progress Bar:** Pantau kemajuan rendering bingkai demi bingkai.
- **Premium Styling:** Skema warna harmonis dan simbol Unicode box-drawing yang elegan.

---

## 🏗 Tech Stack

*   **Core:** Python 3.11 + FastAPI
*   **Frontend:** React + TypeScript + Tauri v2
*   **AI Engine:** 
    *   `Faster-Whisper` (Speech-to-Text)
    *   `YOLOv8` (Face Detection)
    *   `OpenCV` (Dynamic Cropping & Motion Analysis)
*   **Video Engine:** `FFmpeg` (with NVENC Support) + `yt-dlp`

---

## 📜 Lisensi

Proyek ini dilisensikan di bawah **MIT License**. Silakan gunakan, modifikasi, dan distribusikan sesuai kebutuhan Anda.

<div align="center">
  <sub>Built with ❤️ by DImas Bagas Firmansyah Arifin for ClipOS Creators</sub>
</div>
