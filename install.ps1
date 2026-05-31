# ClipOS Production Web Installer & Local Installer
$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           ClipOS — AI Terminal Video Clipper               ║" -ForegroundColor Cyan
Write-Host "║                   Installer Script                         ║" -ForegroundColor Cyan
Write-Host "║                  Production Release v0.1.0                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$InstallDir = "$env:USERPROFILE\AppData\Local\Programs\ClipOS"
$ReleaseZipUrl = "https://github.com/dimasbagas/yt-clip/releases/download/v0.1.0/ClipOS-v0.1.0-Windows.zip"

# 1. Determine Source (Local directory vs. Remote Web download)
$LocalSourceDir = "$PSScriptRoot\dist\clipos"
if (-not (Test-Path $LocalSourceDir)) {
    $LocalSourceDir = "$PSScriptRoot\clipos"
}

$IsWebInstall = $true
$TempZip = "$env:TEMP\ClipOS_Download.zip"
$TempExtract = "$env:TEMP\ClipOS_Extract"

if ((Test-Path "$LocalSourceDir\clipos.exe") -and ($PSScriptRoot -ne "")) {
    $IsWebInstall = $false
    Write-Host "  ⚙ Local source detected. Installing from: $LocalSourceDir" -ForegroundColor Yellow
} else {
    Write-Host "  ⚙ Remote installation detected. Downloading from GitHub..." -ForegroundColor Cyan
}

# 2. Prepare installation directory
Write-Host "  ⚙ Preparing installation directory..." -ForegroundColor Cyan
Write-Host "    Location: $InstallDir" -ForegroundColor Gray
if (Test-Path $InstallDir) {
    Write-Host "    Removing existing installation..." -ForegroundColor Gray
    Remove-Item $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
Write-Host "    ✓ Directory ready" -ForegroundColor Green

# 3. Get the files (Download from Web or Copy from Local)
if ($IsWebInstall) {
    Write-Host "  ⚙ Downloading ClipOS production bundle..." -ForegroundColor Cyan
    Write-Host "    URL: $ReleaseZipUrl" -ForegroundColor Gray
    
    # Download the release ZIP in background
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $ReleaseZipUrl -OutFile $TempZip -UseBasicParsing
        Write-Host "    ✓ Download complete!" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to download release ZIP from GitHub!" -ForegroundColor Red
        Write-Host "  ✗ Please make sure the release is uploaded to: $ReleaseZipUrl" -ForegroundColor Red
        Write-Host "  ✗ Details: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit..."
        Exit 1
    }
    
    Write-Host "  ⚙ Extracting bundle..." -ForegroundColor Cyan
    if (Test-Path $TempExtract) { Remove-Item $TempExtract -Recurse -Force -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Path $TempExtract -Force | Out-Null
    
    # Extract ZIP
    Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force
    
    # Locate the compiled files in the extracted zip
    $ExtractedSource = "$TempExtract\dist\clipos"
    if (-not (Test-Path $ExtractedSource)) {
        $ExtractedSource = "$TempExtract\clipos"
    }
    if (-not (Test-Path $ExtractedSource)) {
        # Fallback to search for clipos.exe inside extracted structure
        $FoundExe = Get-ChildItem -Path $TempExtract -Filter "clipos.exe" -Recurse | Select-Object -First 1
        if ($FoundExe) {
            $ExtractedSource = $FoundExe.Directory.FullName
        }
    }
    
    if (-not (Test-Path "$ExtractedSource\clipos.exe")) {
        Write-Host "  ✗ Could not find clipos.exe in downloaded archive!" -ForegroundColor Red
        Read-Host "Press Enter to exit..."
        Exit 1
    }
    
    Write-Host "  ⚙ Copying executable to program folder..." -ForegroundColor Cyan
    Copy-Item -Path "$ExtractedSource\*" -Destination $InstallDir -Recurse -Force
    Write-Host "    ✓ Copied successfully" -ForegroundColor Green
    
    # Cleanup temp download files
    Remove-Item $TempZip -Force -ErrorAction SilentlyContinue
    Remove-Item $TempExtract -Recurse -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "  ⚙ Copying local application files..." -ForegroundColor Cyan
    Copy-Item -Path "$LocalSourceDir\*" -Destination $InstallDir -Recurse -Force
    Write-Host "    ✓ Copied successfully" -ForegroundColor Green
}

# 4. Create working directories
Write-Host "  ⚙ Creating program working directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "$InstallDir\exports" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\temp" -Force | Out-Null
Write-Host "    ✓ Working directories ready" -ForegroundColor Green

# 5. Add to User Environment PATH
Write-Host "  ⚙ Registering in User PATH environment..." -ForegroundColor Cyan
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*ClipOS*") {
    $NewPath = "$UserPath;$InstallDir"
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    Write-Host "    ✓ Added to Environment PATH!" -ForegroundColor Green
    Write-Host "    ℹ Please RESTART your PowerShell terminal to load 'clipos' command." -ForegroundColor Yellow
} else {
    Write-Host "    ✓ Already registered in PATH" -ForegroundColor Green
}

# 6. Create Desktop Shortcut
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

# 7. Verification
Write-Host "  ⚙ Verifying installation..." -ForegroundColor Cyan
if (Test-Path "$InstallDir\clipos.exe") {
    Write-Host "    ✓ Installation verified successfully!" -ForegroundColor Green
} else {
    Write-Host "    ✗ Verification failed! clipos.exe not found." -ForegroundColor Red
    Exit 1
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║             ✓ INSTALLATION COMPLETED!                      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  📍 Program Location:" -ForegroundColor Cyan
Write-Host "     $InstallDir" -ForegroundColor Gray
Write-Host ""
Write-Host "  🚀 How to Launch:" -ForegroundColor Cyan
Write-Host "     1. Close this window and open a NEW PowerShell or Command Prompt" -ForegroundColor Gray
Write-Host "     2. Type: clipos interactive" -ForegroundColor Gray
Write-Host "     3. Or double-click the 'ClipOS' icon on your Desktop!" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit..."
