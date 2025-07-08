# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the base directory of the application
base_dir = os.path.abspath('.')

# Add application data files
datas = [
    # Include the config directory
    ('config', 'config'),
    # The database file will remain external
    # Include the variables file
    ('variablesCodProd.json', '.')
]

# Add PySide6 plugins path
pyside6_plugins_path = os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'PySide6', 'plugins')
if os.path.exists(pyside6_plugins_path):
    datas.append((pyside6_plugins_path, 'PySide6/plugins'))

# Add PySide6 translations
pyside6_translations_path = os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'PySide6', 'translations')
if os.path.exists(pyside6_translations_path):
    datas.append((pyside6_translations_path, 'PySide6/translations'))

a = Analysis(
    ['main.py'],
    pathex=[base_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'PySide6.QtSvg',
        'sqlite3',
        'json',
        'os',
        'sys',
        'datetime',
        're'
    ],
    hookspath=[],
    hooksconfig={
        'PySide6': {
            'includes': ['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtNetwork', 'PySide6.QtSvg'],
        }
    },
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

# Version info
version_info_file = 'version_info.txt'
version_info = None
if os.path.exists(version_info_file):
    version_info = version_info_file

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GestProdAdmin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon=os.path.join('ui', 'app_icon.ico') if os.path.exists(os.path.join('ui', 'app_icon.ico')) else None,
    version=version_info,
    codesign_identity=None,
    entitlements_file=None,
)
