# SH-file-helper
github.com/lemonfish06/SH-file-helper
## How to test

1. Install Python dependencies:
   ```bash
   python -m pip install pillow pytesseract pdf2image python-docx python-pptx pdf2docx pyside6
   ```
2. Ensure system dependencies are available:
   - LibreOffice (`soffice`) for Office/PDF conversions.
   - Tesseract OCR and Poppler for OCR.
3. Run a sample OCR command:
   ```bash
   python src/main.py --mode ocr_image --input input/sample.png --output output/sample.txt
   ```
4. OCR parameters:
   - `--lang`: Tesseract language(s), supports multi-language like `chi_sim+eng`.
   - `--dpi`: Render DPI for PDF OCR (higher is slower but improves accuracy).
   Example:
   ```bash
   python src/main.py --mode ocr_pdf --input input/sample.pdf --output output/sample.txt --lang chi_sim+eng --dpi 300
   ```
5. Run a sample glossary command:
   ```bash
   python src/main.py --mode glossary --input input/sample.txt --output output/glossary.txt
   ```
6. Glossary parameters:
   - `--top-k`: number of terms returned.
   - `--window-size`: co-occurrence window size (larger captures broader context).
   - `--min-term-length`: minimum term length in characters.
   - `--glossary-format`: `txt` or `json`.
   - `--lang`/`--dpi`: used when inputs require OCR (e.g. PDFs).
   Example:
   ```bash
   python src/main.py --mode glossary --input input/sample.pdf --output output/glossary.txt --top-k 50 --window-size 5 --min-term-length 2 --lang chi_sim+eng --dpi 300
   ```
7. Run a glossary command with Office files:
   ```bash
   python src/main.py --mode glossary --input input/sample.docx input/sample.pptx --output output/glossary.txt
   ```
8. Run a PPT text extraction snippet:
   ```bash
   python -c "from pathlib import Path; from src.ppt_extract import PptExtractRequest, extract_ppt_text; result = extract_ppt_text(PptExtractRequest(Path('input/sample.pptx'), language='eng')); Path('output/ppt_text.txt').write_text(result.to_text(), encoding='utf-8')"
   ```
9. Run a service layer task queue snippet:
   ```bash
   python -c "from pathlib import Path; from src.service import ServiceLayer, OcrJobInput; service = ServiceLayer(); task = service.submit_ocr_image(OcrJobInput(input_path=Path('input/sample.png'), output_path=Path('output/ocr.txt'))); service.queue.run_all(); print(task.status)"
   ```
10. Run the conversion UI:
   ```bash
   python src/ui_conversion.py
   ```

## Packaging (Windows)

### Requirements
- PyInstaller (onedir)
- Inno Setup
- Bundled Tesseract binaries

### 1) Prepare Tesseract bundle
1. Download the Windows Tesseract release (tesseract.exe + tessdata).
2. Place it under `third_party/tesseract/` with the layout:
   ```
   third_party/tesseract/
     tesseract.exe
     tessdata/
   ```

### 2) Build onedir package with PyInstaller
```bash
pyinstaller packaging/pyinstaller.spec
```
This produces `dist/SHFileHelper/` containing `SHFileHelper.exe` and bundled assets.

### 3) Build the installer with Inno Setup
Open `installer/SHFileHelper.iss` in Inno Setup and click **Build**.
The installer will be created under `dist-installer/`.

### Updating
For new releases: update code → rerun PyInstaller → rebuild the Inno Setup installer.
