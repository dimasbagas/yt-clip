# ClipOS Installer Script
$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           ClipOS — AI Terminal Video Clipper               ║" -ForegroundColor Cyan
Write-Host "║                   Installer Script                         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$InstallDir = "$env:USERPROFILE\AppData\Local\Programs\ClipOS"
$SourceDir = "$PSScriptRoot\dist\clipos"

if (-not (Test-Path $SourceDir)) {
    # Fallback if run directly from extracted root folder
    $SourceDir = "$PSScriptRoot\clipos"
}

if (-not (Test-Path $SourceDir)) {
    Write-Host "  ✗ Source files not found! Make sure you run this script from the ClipOS folder." -ForegroundColor Red
    Exit 1
}

# 1. Create installation directory
Write-Host "  ⚙ Creating installation directory at:" -ForegroundColor Cyan
Write-Host "    $InstallDir" -ForegroundColor Gray
if (Test-Path $InstallDir) {
    Remove-Item $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

# 2. Copy compiled executable and library files
Write-Host "  ⚙ Copying application files..." -ForegroundColor Cyan
Copy-Item -Path "$SourceDir\*" -Destination $InstallDir -Recurse -Force

# Create exports and temp folder in installation directory
New-Item -ItemType Directory -Path "$InstallDir\exports" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\temp" -Force | Out-Null

# 3. Add to User Environment PATH
Write-Host "  ⚙ Adding ClipOS to Environment PATH..." -ForegroundColor Cyan
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*ClipOS*") {
    $NewPath = "$UserPath;$InstallDir"
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    Write-Host "    ✓ Registered globally in Environment PATH!" -ForegroundColor Green
} else {
    Write-Host "    ✓ ClipOS is already in Environment PATH." -ForegroundColor Green
}

# 4. Create Desktop Shortcut
Write-Host "  ⚙ Creating Desktop Shortcut..." -ForegroundColor Cyan
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $ShortcutPath = "$env:USERPROFILE\Desktop\ClipOS.lnk"
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = "$InstallDir\clipos.exe"
    $Shortcut.Arguments = "interactive"
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.Save()
    Write-Host "    ✓ Shortcut 'ClipOS' created on Desktop!" -ForegroundColor Green
} catch {
    Write-Host "    ⚠ Failed to create shortcut: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║             ✓ INSTALLATION COMPLETED!                      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host "  ➜ You can now type 'clipos' in any terminal or powershell!" -ForegroundColor Green
Write-Host "  ➜ Or double-click the 'ClipOS' shortcut on your Desktop!" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit..."
