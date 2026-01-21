"""Core conversion and OCR helpers for SH-file-helper."""

from .conversion import ConversionError, ConversionMode, ConversionRequest, convert
from .glossary import GlossaryEntry, GlossaryError, GlossaryRequest, GlossaryResult, generate_glossary
from .ocr import OcrError, OcrRequest, OcrResult, ocr_image, ocr_pdf
from .ppt_extract import PptExtractError, PptExtractRequest, PptExtractResult, extract_ppt_text
from .text_extract import TextExtractError, TextExtractRequest, extract_text

__all__ = [
    "ConversionError",
    "ConversionMode",
    "ConversionRequest",
    "convert",
    "GlossaryEntry",
    "GlossaryError",
    "GlossaryRequest",
    "GlossaryResult",
    "generate_glossary",
    "OcrError",
    "OcrRequest",
    "OcrResult",
    "ocr_image",
    "ocr_pdf",
    "PptExtractError",
    "PptExtractRequest",
    "PptExtractResult",
    "extract_ppt_text",
    "TextExtractError",
    "TextExtractRequest",
    "extract_text",
]
