# ClipOS Installer Script — Production Distribution
# This script installs the pre-built ClipOS executable for end users
$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           ClipOS — AI Terminal Video Clipper               ║" -ForegroundColor Cyan
Write-Host "║                   Installer Script                         ║" -ForegroundColor Cyan
Write-Host "║                  Production Release v0.1.0                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$InstallDir = "$env:USERPROFILE\AppData\Local\Programs\ClipOS"
$SourceDir = "$PSScriptRoot\dist\clipos"

# Fallback paths for different distribution scenarios
if (-not (Test-Path $SourceDir)) {
    $SourceDir = "$PSScriptRoot\clipos"
}

if (-not (Test-Path "$SourceDir\clipos.exe")) {
    Write-Host "  ✗ ClipOS executable not found!" -ForegroundColor Red
    Write-Host "  ✗ Expected location: $SourceDir\clipos.exe" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Make sure you have the complete ClipOS distribution package." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit..."
    Exit 1
}

# 1. Create installation directory
Write-Host "  ⚙ Creating installation directory..." -ForegroundColor Cyan
Write-Host "    Location: $InstallDir" -ForegroundColor Gray
if (Test-Path $InstallDir) {
    Write-Host "    Removing existing installation..." -ForegroundColor Gray
    Remove-Item $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
Write-Host "    ✓ Directory created" -ForegroundColor Green

# 2. Copy executable and all dependencies
Write-Host "  ⚙ Copying application files..." -ForegroundColor Cyan
Write-Host "    This may take a moment..." -ForegroundColor Gray
Copy-Item -Path "$SourceDir\*" -Destination $InstallDir -Recurse -Force
Write-Host "    ✓ Files copied successfully" -ForegroundColor Green

# 3. Create working directories
Write-Host "  ⚙ Creating working directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "$InstallDir\exports" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\temp" -Force | Out-Null
Write-Host "    ✓ Directories created" -ForegroundColor Green

# 4. Add to User Environment PATH
Write-Host "  ⚙ Registering in Environment PATH..." -ForegroundColor Cyan
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*ClipOS*") {
    $NewPath = "$UserPath;$InstallDir"
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    Write-Host "    ✓ Added to PATH (restart terminal to use 'clipos' command)" -ForegroundColor Green
} else {
    Write-Host "    ✓ Already registered in PATH" -ForegroundColor Green
}

# 5. Create Desktop Shortcut
Write-Host "  ⚙ Creating Desktop Shortcut..." -ForegroundColor Cyan
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $ShortcutPath = "$env:USERPROFILE\Desktop\ClipOS.lnk"
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = "$InstallDir\clipos.exe"
    $Shortcut.Arguments = "interactive"
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.IconLocation = "$InstallDir\clipos.exe,0"
    $Shortcut.Save()
    Write-Host "    ✓ Desktop shortcut created" -ForegroundColor Green
} catch {
    Write-Host "    ⚠ Could not create shortcut: $_" -ForegroundColor Yellow
}

# 6. Verify installation
Write-Host "  ⚙ Verifying installation..." -ForegroundColor Cyan
if (Test-Path "$InstallDir\clipos.exe") {
    Write-Host "    ✓ Installation verified successfully" -ForegroundColor Green
} else {
    Write-Host "    ✗ Installation verification failed" -ForegroundColor Red
    Exit 1
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║             ✓ INSTALLATION COMPLETED!                      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  📍 Installation Location:" -ForegroundColor Cyan
Write-Host "     $InstallDir" -ForegroundColor Gray
Write-Host ""
Write-Host "  🚀 How to Use:" -ForegroundColor Cyan
Write-Host "     1. Open a new PowerShell or Command Prompt window" -ForegroundColor Gray
Write-Host "     2. Type: clipos interactive" -ForegroundColor Gray
Write-Host "     3. Or double-click 'ClipOS' shortcut on your Desktop" -ForegroundColor Gray
Write-Host ""
Write-Host "  📚 Available Commands:" -ForegroundColor Cyan
Write-Host "     clipos import <file>              - Import local video" -ForegroundColor Gray
Write-Host "     clipos youtube <url>              - Download from YouTube" -ForegroundColor Gray
Write-Host "     clipos interactive                - Interactive guided mode" -ForegroundColor Gray
Write-Host "     clipos --help                     - Show all commands" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit..."
