"""Core conversion and OCR helpers for SH-file-helper."""

from .conversion import ConversionError, ConversionMode, ConversionRequest, convert
from .glossary import GlossaryEntry, GlossaryError, GlossaryRequest, GlossaryResult, generate_glossary
from .ocr import OcrError, OcrRequest, OcrResult, ocr_image, ocr_pdf
from .ppt_extract import PptExtractError, PptExtractRequest, PptExtractResult, extract_ppt_text
from .service import GlossaryJobInput, OcrJobInput, PptExtractJobInput, ServiceLayer
from .task_queue import TaskQueue, TaskRecord, TaskStatus
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
    "GlossaryJobInput",
    "OcrJobInput",
    "PptExtractJobInput",
    "ServiceLayer",
    "TaskQueue",
    "TaskRecord",
    "TaskStatus",
    "TextExtractError",
    "TextExtractRequest",
    "extract_text",
]