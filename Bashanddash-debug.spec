# -*- mode: python ; coding: utf-8 -*-

# Bash and Dash Game Log Analyzer - Debug Build Configuration
# This version enables error tracebacks for debugging issues

import sys
import os

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath('Bashanddash-stealth.py'))

a = Analysis(
    ['Bashanddash-stealth.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.filedialog',
        'tkinter.scrolledtext', 
        'tkinter.messagebox',
        'urllib.request',
        'urllib.parse',
        'collections',
        'json',
        'threading',
        'hashlib',
        'tempfile',
        'shutil',
        're',
        'datetime',
        'time'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Remove these exclusions for debugging
        # 'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'cv2'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Bashanddash-debug',
    debug=True,  # Enable debug mode
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Enable console for error messages
    disable_windowed_traceback=False,  # Enable tracebacks
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon=None
)
