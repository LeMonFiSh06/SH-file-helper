from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from conversion import ConversionMode, ConversionRequest, convert
from glossary import GlossaryRequest, generate_glossary
from ocr import OcrRequest, ocr_image, ocr_pdf
from ppt_extract import PptExtractRequest, extract_ppt_text
from task_queue import TaskQueue, TaskRecord
from text_extract import TextExtractRequest, extract_text


@dataclass(frozen=True)
class GlossaryJobInput:
    input_paths: Sequence[Path]
    output_path: Path
    top_k: int = 30
    window_size: int = 4
    min_term_length: int = 2
    language: str = "eng"
    dpi: int = 300
    output_format: str = "txt"


@dataclass(frozen=True)
class OcrJobInput:
    input_path: Path
    output_path: Path
    language: str = "eng"
    dpi: int = 300


@dataclass(frozen=True)
class PptExtractJobInput:
    input_path: Path
    output_path: Path
    language: str = "eng"


class ServiceLayer:
    def __init__(self) -> None:
        self.queue = TaskQueue()

    def submit_conversion(self, request: ConversionRequest) -> TaskRecord:
        return self.queue.enqueue(
            description=f"Convert {request.mode}",
            handler=lambda: convert(request),
        )

    def submit_ocr_image(self, request: OcrJobInput) -> TaskRecord:
        return self.queue.enqueue(
            description=f"OCR image {request.input_path.name}",
            handler=lambda: _run_ocr_image(request),
        )

    def submit_ocr_pdf(self, request: OcrJobInput) -> TaskRecord:
        return self.queue.enqueue(
            description=f"OCR PDF {request.input_path.name}",
            handler=lambda: _run_ocr_pdf(request),
        )

    def submit_glossary(self, request: GlossaryJobInput) -> TaskRecord:
        return self.queue.enqueue(
            description="Generate glossary",
            handler=lambda: _run_glossary(request),
        )

    def submit_ppt_extract(self, request: PptExtractJobInput) -> TaskRecord:
        return self.queue.enqueue(
            description=f"Extract PPT {request.input_path.name}",
            handler=lambda: _run_ppt_extract(request),
        )


def _run_ocr_image(request: OcrJobInput) -> Path:
    result = ocr_image(OcrRequest(request.input_path, request.language))
    request.output_path.parent.mkdir(parents=True, exist_ok=True)
    request.output_path.write_text(result.text, encoding="utf-8")
    return request.output_path


def _run_ocr_pdf(request: OcrJobInput) -> Path:
    result = ocr_pdf(OcrRequest(request.input_path, request.language, request.dpi))
    request.output_path.parent.mkdir(parents=True, exist_ok=True)
    request.output_path.write_text(result.text, encoding="utf-8")
    return request.output_path


def _run_glossary(request: GlossaryJobInput) -> Path:
    texts = [
        extract_text(
            TextExtractRequest(
                input_path=path,
                language=request.language,
                dpi=request.dpi,
            )
        )
        for path in request.input_paths
    ]
    result = generate_glossary(
        GlossaryRequest(
            texts=texts,
            top_k=request.top_k,
            window_size=request.window_size,
            min_term_length=request.min_term_length,
        )
    )

    request.output_path.parent.mkdir(parents=True, exist_ok=True)
    if request.output_format == "json":
        payload = [entry.__dict__ for entry in result.entries]
        request.output_path.write_text(_to_json(payload), encoding="utf-8")
    else:
        lines = [f"{entry.term}\t{entry.score:.4f}" for entry in result.entries]
        request.output_path.write_text("\n".join(lines), encoding="utf-8")
    return request.output_path


def _run_ppt_extract(request: PptExtractJobInput) -> Path:
    result = extract_ppt_text(
        PptExtractRequest(
            input_path=request.input_path,
            language=request.language,
        )
    )
    request.output_path.parent.mkdir(parents=True, exist_ok=True)
    request.output_path.write_text(result.to_text(), encoding="utf-8")
    return request.output_path


def _to_json(payload: List[dict[str, object]]) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2)