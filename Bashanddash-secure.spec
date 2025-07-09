# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for Bash and Dash Game Log Analyzer
=========================================================

This spec file is configured to minimize antivirus false positives
by using secure compilation options and proper metadata.

Swiggity: Custom spec file for secure executable generation
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Security-focused build configuration
a = Analysis(
    ['Bashanddash.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'urllib.request',
        'urllib.parse',
        'json',
        'threading',
        'hashlib',
        'tempfile',
        'shutil',
        'subprocess',
        're',
        'collections',
        'datetime',
        'os',
        'sys',
        'time'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude potentially suspicious modules
        'pytest',
        'setuptools',
        'distutils',
        'pip',
        'wheel',
        'pkg_resources',
        'pywin32',
        'win32api',
        'win32con',
        'win32gui',
        'pywintypes'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove potentially suspicious libraries
a.binaries = [x for x in a.binaries if not any(
    suspicious in x[0].lower() for suspicious in [
        'msvcr', 'msvcp', 'vcruntime', 'api-ms-win',
        'kernel32', 'ntdll', 'advapi32'
    ]
)]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Bashanddash',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression as it often triggers AV
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Security and identification metadata
    version='version_info.txt',
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    # Manifest for Windows compatibility
    manifest="""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.1.0"
    processorArchitecture="*"
    name="Bash.and.Dash.Game.Log.Analyzer"
    type="win32"
  />
  <description>Bash and Dash Game Log Analyzer - Legitimate game statistics tool</description>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <supportedOS Id="{e2011457-1546-43c5-a5fe-008deee3d3f0}"/>
      <supportedOS Id="{35138b9a-5d96-4fbd-8e2d-a2440225f93a}"/>
      <supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"/>
      <supportedOS Id="{1f676c76-80e1-4239-95bb-83d0f6d0da78}"/>
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
    </application>
  </compatibility>
</assembly>"""
)
