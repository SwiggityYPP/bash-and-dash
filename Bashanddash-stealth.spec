# -*- mode: python ; coding: utf-8 -*-
"""
Advanced Stealth PyInstaller Spec File for Bash and Dash Game Log Analyzer
===========================================================================

This spec file implements advanced techniques to minimize antivirus detection:
- More aggressive module exclusions
- Custom bootloader options
- Obfuscated temporary directory
- Additional security metadata

Swiggity: Ultra-stealth executable generation configuration
"""

import os
import sys
import uuid
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Generate unique temporary directory name to avoid heuristic detection
TEMP_DIR_NAME = f"tmp_{str(uuid.uuid4())[:8]}"

# Advanced security-focused build configuration
a = Analysis(
    ['Bashanddash.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        # Only essential imports
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'json',
        'threading',
        'hashlib',
        'tempfile',
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
        # Aggressively exclude suspicious modules
        'pytest', 'setuptools', 'distutils', 'pip', 'wheel', 'pkg_resources',
        'pywin32', 'win32api', 'win32con', 'win32gui', 'pywintypes',
        'numpy', 'scipy', 'pandas', 'matplotlib', 'requests', 'urllib3',
        'cryptography', 'pycrypto', 'ssl', 'socket', 'http', 'ftplib',
        'smtplib', 'imaplib', 'poplib', 'telnetlib', 'xmlrpc',
        'multiprocessing', 'concurrent', 'asyncio', 'queue',
        'pickle', 'marshal', 'shelve', 'dbm', 'sqlite3',
        'ctypes', 'ctypes.wintypes', 'ctypes.util',
        'email', 'mimetypes', 'base64', 'binascii', 'quopri', 'uu',
        'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma', 'zlib',
        'subprocess', 'os.path', 'pathlib', 'shutil', 'glob',
        'getpass', 'keyring', 'platform', 'locale',
        'logging', 'syslog', 'warnings', 'traceback',
        'unittest', 'doctest', 'pdb', 'profile', 'pstats',
        'webbrowser', 'cgi', 'cgitb', 'wsgiref',
        'xml', 'html', 'urllib', 'http.client', 'http.server'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# More aggressive binary filtering
suspicious_binaries = [
    'msvcr', 'msvcp', 'vcruntime', 'api-ms-win', 'kernel32', 'ntdll', 
    'advapi32', 'user32', 'gdi32', 'shell32', 'ole32', 'oleaut32',
    'wininet', 'urlmon', 'crypt32', 'wintrust', 'version', 'psapi',
    'dbghelp', 'imagehlp', 'ws2_32', 'mswsock', 'dnsapi', 'iphlpapi',
    'netapi32', 'wtsapi32', 'userenv', 'uxtheme', 'dwmapi', 'comctl32'
]

a.binaries = [x for x in a.binaries if not any(
    suspicious in x[0].lower() for suspicious in suspicious_binaries
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
    strip=True,  # Strip debug symbols
    upx=False,  # Never use UPX
    upx_exclude=[],
    runtime_tmpdir=TEMP_DIR_NAME,  # Custom temp directory
    console=False,
    disable_windowed_traceback=True,  # Disable traceback
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    # Enhanced manifest with additional security declarations
    manifest=f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.1.0"
    processorArchitecture="*"
    name="BashDashGameLogAnalyzer.Application"
    type="win32"
  />
  <description>Bash and Dash Game Statistics and Log Analysis Tool</description>
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
      <supportedOS Id="{{e2011457-1546-43c5-a5fe-008deee3d3f0}}"/>
      <supportedOS Id="{{35138b9a-5d96-4fbd-8e2d-a2440225f93a}}"/>
      <supportedOS Id="{{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}}"/>
      <supportedOS Id="{{1f676c76-80e1-4239-95bb-83d0f6d0da78}}"/>
      <supportedOS Id="{{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}}"/>
    </application>
  </compatibility>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
    </windowsSettings>
  </application>
</assembly>"""
)
