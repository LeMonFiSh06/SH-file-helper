# SH-file-helper

## How to test

1. Install Python dependencies:
   ```bash
   python -m pip install pillow pytesseract pdf2image python-docx python-pptx
   ```
2. Ensure system dependencies are available:
   - LibreOffice (`soffice`) for Office/PDF conversions.
   - Tesseract OCR and Poppler for OCR.
3. Run a sample OCR command:
   ```bash
   python src/main.py --mode ocr_image --input input/sample.png --output output/sample.txt
   ```
4. Run a sample glossary command:
   ```bash
   python src/main.py --mode glossary --input input/sample.txt --output output/glossary.txt
   ```
5. Run a glossary command with Office files:
   ```bash
   python src/main.py --mode glossary --input input/sample.docx input/sample.pptx --output output/glossary.txt
   ```
6. Run a PPT text extraction snippet:
   ```bash
   python -c "from pathlib import Path; from src.ppt_extract import PptExtractRequest, extract_ppt_text; result = extract_ppt_text(PptExtractRequest(Path('input/sample.pptx'), language='eng')); Path('output/ppt_text.txt').write_text(result.to_text(), encoding='utf-8')"
   ```
7. Run a service layer task queue snippet:
   ```bash
   python -c "from pathlib import Path; from src.service import ServiceLayer, OcrJobInput; service = ServiceLayer(); task = service.submit_ocr_image(OcrJobInput(input_path=Path('input/sample.png'), output_path=Path('output/ocr.txt'))); service.queue.run_all(); print(task.status)"
   ```