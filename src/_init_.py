"""Core conversion and OCR helpers for SH-file-helper."""

from .conversion import ConversionError, ConversionMode, ConversionRequest, convert
from .ocr import OcrError, OcrRequest, OcrResult, ocr_image, ocr_pdf

__all__ = [
    "ConversionError",
    "ConversionMode",
    "ConversionRequest",
    "convert",
    "OcrError",
    "OcrRequest",
    "OcrResult",
    "ocr_image",
    "ocr_pdf",
]