# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['backend/clipos.py'],
    pathex=['backend'],
    binaries=[],
    datas=[
        ('backend/config.py', '.'),
        ('backend/subtitle_engine', 'subtitle_engine'),
        ('backend/render_engine', 'render_engine'),
        ('backend/tracking_engine', 'tracking_engine'),
        ('backend/youtube_import', 'youtube_import'),
        ('backend/ai_processing', 'ai_processing'),
        ('models', 'models'),
    ],
    hiddenimports=[
        'faster_whisper',
        'ultralytics',
        'cv2',
        'yt_dlp',
        'numpy',
        'torch',
        'pydantic',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='clipos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='clipos',
)
