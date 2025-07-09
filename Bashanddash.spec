# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Bashanddash.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyw = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyw,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Bashanddash',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
