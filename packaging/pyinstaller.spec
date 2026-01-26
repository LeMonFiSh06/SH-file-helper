# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path.cwd()
app_name = "SHFileHelper"
entry_script = project_root / "src" / "UI.py"

# Bundle Tesseract binaries and tessdata. Place them under third_party/tesseract.
# Expected layout:
# third_party/tesseract/tesseract.exe
# third_party/tesseract/tessdata/

tesseract_dir = project_root / "third_party" / "tesseract"

a = Analysis(
    [str(entry_script)],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=[(str(tesseract_dir), "tesseract")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name=app_name,
)