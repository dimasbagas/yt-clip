# 📦 ClipOS — Distribution & Installation Guide

## For End Users (Pembeli)

### ✅ System Requirements

- **OS:** Windows 10 / Windows 11
- **RAM:** Minimum 4GB (8GB recommended for AI processing)
- **Disk Space:** 2GB free space (for models and temporary files)
- **GPU:** Optional - NVIDIA GPU with CUDA support for faster rendering

### 🚀 Installation Steps

#### Step 1: Extract the Package
1. Download the ClipOS distribution package
2. Extract the ZIP file to any location (e.g., `C:\ClipOS`)

#### Step 2: Run the Installer
1. Open **PowerShell** as Administrator
2. Navigate to the extracted folder:
   ```powershell
   cd C:\ClipOS
   ```
3. Run the installer:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   .\install.ps1
   ```
4. Wait for installation to complete

#### Step 3: Verify Installation
1. Open a **new** PowerShell or Command Prompt window
2. Type:
   ```powershell
   clipos --help
   ```
3. You should see the help menu with all available commands

### 📚 Quick Start

#### Interactive Mode (Recommended for Beginners)
```powershell
clipos interactive
```
This will guide you through the entire process step-by-step.

#### Command Line Mode (For Advanced Users)

**Import a local video:**
```powershell
clipos import C:\Videos\myvideo.mp4
```

**Download from YouTube:**
```powershell
clipos youtube https://www.youtube.com/watch?v=...
```

**Set clip range:**
```powershell
clipos clip 00:01:30 00:02:45
```

**Generate subtitles:**
```powershell
clipos subtitles
```

**Full AI rendering pipeline:**
```powershell
clipos render --aspect-ratio 9:16 --tracking-mode podcast
```

**See all commands:**
```powershell
clipos --help
```

### 📁 Installation Location

By default, ClipOS is installed to:
```
C:\Users\[YourUsername]\AppData\Local\Programs\ClipOS
```

### 🎯 Output Files

Rendered videos are saved to:
```
C:\Users\[YourUsername]\AppData\Local\Programs\ClipOS\exports
```

### ⚙️ Uninstallation

To uninstall ClipOS:
1. Delete the folder: `C:\Users\[YourUsername]\AppData\Local\Programs\ClipOS`
2. Remove from PATH (optional):
   - Open Environment Variables
   - Remove the ClipOS path entry
3. Delete Desktop shortcut (if created)

---

## For Developers / Resellers

### 📦 Package Contents

```
ClipOS-v0.1.0/
├── dist/
│   └── clipos/
│       ├── clipos.exe              # Main executable (61.5 MB)
│       ├── _internal/              # All dependencies bundled
│       ├── exports/                # Output directory
│       └── temp/                   # Temporary files
├── install.ps1                     # Installation script
├── README.md                       # User documentation
└── DISTRIBUTION.md                 # This file
```

### 🔧 Building from Source

If you need to rebuild the executable:

```bash
# 1. Setup Python environment
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Build with PyInstaller
pyinstaller ..\clipos.spec

# 3. Copy to dist folder
Copy-Item -Path "dist\clipos" -Destination "..\dist\clipos" -Recurse -Force
```

### 📝 Customization

To customize the installer for your brand:

1. Edit `install.ps1`:
   - Change company name in header
   - Modify installation path
   - Add custom shortcuts

2. Edit `README.md`:
   - Add your company branding
   - Include support contact information
   - Add license terms

### 🔐 License & Distribution

- **License:** MIT License
- **Distribution:** Free to distribute and modify
- **Attribution:** Please include original author credit

---

## 🐛 Troubleshooting

### Issue: "clipos is not recognized as a command"

**Solution:**
1. Close and reopen PowerShell/Command Prompt
2. Verify installation: `dir "%USERPROFILE%\AppData\Local\Programs\ClipOS"`
3. Manually add to PATH if needed

### Issue: "FFmpeg not found"

**Solution:**
- ClipOS includes FFmpeg internally
- If error persists, reinstall ClipOS

### Issue: "YOLO model download fails"

**Solution:**
- First run requires downloading AI models (~500MB)
- Ensure stable internet connection
- Models are cached after first download

### Issue: "Out of memory" during rendering

**Solution:**
- Close other applications
- Reduce video resolution or clip length
- Increase system RAM if possible

---

## 📞 Support

For issues or feature requests:
- GitHub: [dimasbagas/yt-clip](https://github.com/dimasbagas/yt-clip)
- Issues: [GitHub Issues](https://github.com/dimasbagas/yt-clip/issues)

---

**Version:** 0.1.0  
**Last Updated:** May 31, 2026  
**Built with:** Python + FastAPI + React + Tauri
