@echo off
REM ClipOS Distribution Packager
REM Creates a ready-to-distribute ZIP file

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║        ClipOS — Distribution Package Creator               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

set VERSION=0.1.0
set PACKAGE_NAME=ClipOS-v%VERSION%-Windows
set OUTPUT_DIR=%cd%\releases
set TEMP_PACKAGE=%OUTPUT_DIR%\%PACKAGE_NAME%

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo [1/4] Preparing package directory...
if exist "%TEMP_PACKAGE%" rmdir /s /q "%TEMP_PACKAGE%"
mkdir "%TEMP_PACKAGE%"

echo [2/4] Copying distribution files...
xcopy /E /I /Y "dist\clipos" "%TEMP_PACKAGE%\dist\clipos" >nul
copy /Y "INSTALL.bat" "%TEMP_PACKAGE%\" >nul
copy /Y "install.ps1" "%TEMP_PACKAGE%\" >nul
copy /Y "README.md" "%TEMP_PACKAGE%\" >nul
copy /Y "DISTRIBUTION.md" "%TEMP_PACKAGE%\" >nul
copy /Y "LICENSE" "%TEMP_PACKAGE%\" >nul 2>nul

echo [3/4] Creating ZIP archive...
cd /d "%OUTPUT_DIR%"
powershell -Command "Compress-Archive -Path '%PACKAGE_NAME%' -DestinationPath '%PACKAGE_NAME%.zip' -Force"
cd /d "%cd%"

echo [4/4] Cleaning up temporary files...
rmdir /s /q "%TEMP_PACKAGE%"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║           ✓ PACKAGE CREATED SUCCESSFULLY!                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Package Location: %OUTPUT_DIR%\%PACKAGE_NAME%.zip
echo.
echo Ready to distribute! You can now:
echo   1. Upload to your website
echo   2. Share via cloud storage (Google Drive, OneDrive, etc.)
echo   3. Distribute to customers
echo.
pause
