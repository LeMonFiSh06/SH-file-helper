from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from typing import Iterable, List

from pdf2image import convert_from_path
from PIL import Image
import pytesseract

from runtime_paths import get_app_root


@dataclass(frozen=True)
class OcrRequest:
    input_path: Path
    language: str = "eng"
    dpi: int = 300


@dataclass(frozen=True)
class OcrPageResult:
    page_number: int
    text: str


@dataclass(frozen=True)
class OcrResult:
    text: str
    pages: List[OcrPageResult]


class OcrError(RuntimeError):
    pass


_TESSERACT_READY = False


def ocr_image(request: OcrRequest) -> OcrResult:
    setup_tesseract()
    if not request.input_path.exists():
        raise OcrError(f"Input image not found: {request.input_path}")

    with Image.open(request.input_path) as image:
        text = pytesseract.image_to_string(image, lang=request.language)

    return OcrResult(text=text, pages=[OcrPageResult(page_number=1, text=text)])


def ocr_pdf(request: OcrRequest) -> OcrResult:
    setup_tesseract()
    if not request.input_path.exists():
        raise OcrError(f"Input PDF not found: {request.input_path}")

    try:
        images = convert_from_path(str(request.input_path), dpi=request.dpi)
    except Exception as exc:  # noqa: BLE001
        raise OcrError(
            "Failed to render PDF pages. Ensure Poppler is installed and in PATH."
        ) from exc

    pages = _ocr_images(images, request.language)
    text = "\n\n".join(page.text for page in pages)
    return OcrResult(text=text, pages=pages)


def _ocr_images(images: Iterable[Image.Image], language: str) -> List[OcrPageResult]:
    results: List[OcrPageResult] = []
    for index, image in enumerate(images, start=1):
        text = pytesseract.image_to_string(image, lang=language)
        results.append(OcrPageResult(page_number=index, text=text))
    return results


def setup_tesseract() -> None:
    """Configure pytesseract to use bundled binaries when available."""
    global _TESSERACT_READY
    if _TESSERACT_READY:
        return
    _TESSERACT_READY = True

    if os.environ.get("TESSERACT_CMD"):
        pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]
        return

    app_root = get_app_root()
    tesseract_exe = app_root / "tesseract" / "tesseract.exe"
    if tesseract_exe.exists():
        pytesseract.pytesseract.tesseract_cmd = str(tesseract_exe)
        os.environ.setdefault("TESSDATA_PREFIX", str(app_root / "tesseract"))
        return