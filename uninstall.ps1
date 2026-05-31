# ClipOS Uninstaller Script
$ErrorActionPreference = "Continue"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║           ClipOS — AI Terminal Video Clipper               ║" -ForegroundColor Red
Write-Host "║                  Uninstaller Script                        ║" -ForegroundColor Red
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Red
Write-Host ""

$InstallDir = "$env:USERPROFILE\AppData\Local\Programs\ClipOS"
$ShortcutPath = "$env:USERPROFILE\Desktop\ClipOS.lnk"

# 1. Remove Desktop Shortcut
if (Test-Path $ShortcutPath) {
    Write-Host "  ⚙ Removing Desktop Shortcut..." -ForegroundColor Cyan
    Remove-Item $ShortcutPath -Force
    Write-Host "    ✓ Shortcut removed." -ForegroundColor Green
}

# 2. Remove from User Environment PATH
Write-Host "  ⚙ Cleaning up Environment PATH..." -ForegroundColor Cyan
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -like "*ClipOS*") {
    # Split path, filter out ClipOS, and join back
    $Paths = $UserPath -split ";" | Where-Object { $_ -ne $InstallDir -and $_ -ne "$InstallDir\" -and $_ -notlike "*AppData\Local\Programs\ClipOS*" }
    $NewPath = $Paths -join ";"
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    Write-Host "    ✓ ClipOS removed from PATH." -ForegroundColor Green
} else {
    Write-Host "    ✓ ClipOS was not found in PATH." -ForegroundColor Gray
}

# 3. Remove Installation Directory
if (Test-Path $InstallDir) {
    Write-Host "  ⚙ Deleting application files at:" -ForegroundColor Cyan
    Write-Host "    $InstallDir" -ForegroundColor Gray
    try {
        Remove-Item $InstallDir -Recurse -Force
        Write-Host "    ✓ All files deleted." -ForegroundColor Green
    } catch {
        Write-Host "    ⚠ Could not delete some files. Make sure no ClipOS process is running." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║             ✓ UNINSTALLATION COMPLETED!                    ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
Write-Host "  ClipOS has been successfully removed from your system." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit..."
