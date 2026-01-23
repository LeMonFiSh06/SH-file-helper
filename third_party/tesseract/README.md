# Bundled Tesseract

Place the Windows Tesseract distribution here before building.

Expected layout:
```
third_party/tesseract/
  tesseract.exe
  tessdata/
```

The PyInstaller spec bundles this folder into the app under `tesseract/` so the
OCR runtime can locate it without system installation.
