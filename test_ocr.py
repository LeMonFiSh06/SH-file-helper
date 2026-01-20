from pathlib import Path
from src.ocr import OcrRequest, ocr_image, ocr_pdf

# 图片 OCR
#img_result = ocr_image(OcrRequest(input_path=Path("input/sample.png"), language="eng"))
#Path("output/image_ocr.txt").write_text(img_result.text, encoding="utf-8")

# PDF OCR
pdf_result = ocr_pdf(OcrRequest(input_path=Path("input/demo.pdf"), language="eng"))
Path("output/pdf_ocr.txt").write_text(pdf_result.text, encoding="utf-8")
