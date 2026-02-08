# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ChannelSmith standalone executable.

This configuration creates a single-file executable for Windows, macOS, and Linux.
Build commands:
  Windows: pyinstaller channelsmith.spec
  macOS:   pyinstaller channelsmith.spec
  Linux:   pyinstaller channelsmith.spec

Output:
  Windows: dist/ChannelSmith.exe (~50MB)
  macOS:   dist/ChannelSmith (~50MB)
  Linux:   dist/ChannelSmith (~50MB)
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get absolute path to project root
# Use SPECPATH (automatically set by PyInstaller) or current directory
project_root = SPECPATH if 'SPECPATH' in dir() else os.getcwd()

# Collect data files for Pillow and numpy
pillow_data = collect_data_files('PIL')
numpy_data = collect_data_files('numpy')

a = Analysis(
    [os.path.join(project_root, 'channelsmith', '__main__.py')],
    pathex=[project_root],
    binaries=[],
    datas=[
        # Frontend assets (HTML, CSS, JS, images)
        (os.path.join(project_root, 'channelsmith', 'frontend'), 'channelsmith/frontend'),
        # Template files (JSON configuration)
        (os.path.join(project_root, 'channelsmith', 'templates'), 'channelsmith/templates'),
        # Documentation (user guide)
        (os.path.join(project_root, 'cs_wiki.md'), '.'),
        # Pillow and numpy data
        *pillow_data,
        *numpy_data,
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'PIL',
        'PIL.Image',
        'numpy',
        'channelsmith.core',
        'channelsmith.api',
        'channelsmith.templates',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[
        'tkinter',  # Exclude legacy GUI to reduce size
        'matplotlib',
        'scipy',
        'pandas',
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
    name='ChannelSmith',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console for Flask logs
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
