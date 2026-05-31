@echo off
REM ClipOS — One-Click Installer
REM User hanya perlu double-click file ini

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║           ClipOS — AI Terminal Video Clipper               ║
echo ║                   One-Click Installer                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if dist\clipos exists
if not exist "dist\clipos\clipos.exe" (
    echo  ✗ ERROR: clipos.exe not found!
    echo  ✗ Make sure you extracted the ZIP file completely.
    echo.
    pause
    exit /b 1
)

REM Run PowerShell installer
echo  ⚙ Starting installation...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference = 'Stop'; ^
   $InstallDir = \"$env:USERPROFILE\AppData\Local\Programs\ClipOS\"; ^
   if (Test-Path $InstallDir) { Remove-Item $InstallDir -Recurse -Force }; ^
   New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null; ^
   Copy-Item -Path \"dist\clipos\*\" -Destination $InstallDir -Recurse -Force; ^
   New-Item -ItemType Directory -Path \"$InstallDir\exports\" -Force | Out-Null; ^
   New-Item -ItemType Directory -Path \"$InstallDir\temp\" -Force | Out-Null; ^
   $UserPath = [Environment]::GetEnvironmentVariable('Path', 'User'); ^
   if ($UserPath -notlike '*ClipOS*') { ^
     [Environment]::SetEnvironmentVariable('Path', \"$UserPath;$InstallDir\", 'User'); ^
   }; ^
   try { ^
     $WshShell = New-Object -ComObject WScript.Shell; ^
     $Shortcut = $WshShell.CreateShortcut(\"$env:USERPROFILE\Desktop\ClipOS.lnk\"); ^
     $Shortcut.TargetPath = \"$InstallDir\clipos.exe\"; ^
     $Shortcut.Arguments = 'interactive'; ^
     $Shortcut.WorkingDirectory = $InstallDir; ^
     $Shortcut.IconLocation = \"$InstallDir\clipos.exe,0\"; ^
     $Shortcut.Save(); ^
   } catch {}; ^
   Write-Host ''; ^
   Write-Host '╔════════════════════════════════════════════════════════════╗' -ForegroundColor Green; ^
   Write-Host '║             ✓ INSTALLATION COMPLETED!                      ║' -ForegroundColor Green; ^
   Write-Host '╚════════════════════════════════════════════════════════════╝' -ForegroundColor Green; ^
   Write-Host ''; ^
   Write-Host '  🚀 You can now use ClipOS!' -ForegroundColor Green; ^
   Write-Host ''; ^
   Write-Host '  Option 1: Open a new PowerShell and type:' -ForegroundColor Cyan; ^
   Write-Host '     clipos interactive' -ForegroundColor Gray; ^
   Write-Host ''; ^
   Write-Host '  Option 2: Double-click ClipOS shortcut on Desktop' -ForegroundColor Cyan; ^
   Write-Host ''; ^
   Write-Host '  Option 3: Use command line:' -ForegroundColor Cyan; ^
   Write-Host '     clipos --help' -ForegroundColor Gray; ^
   Write-Host ''; ^
   Read-Host '  Press Enter to exit';"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ✗ Installation failed!
    echo.
    pause
    exit /b 1
)

echo.
echo  ✓ Installation successful!
echo.
pause
