from __future__ import annotations

import argparse
from pathlib import Path

from conversion import ConversionMode, ConversionRequest, convert
from glossary import GlossaryRequest, generate_glossary
from ocr import OcrRequest, ocr_image, ocr_pdf
from text_extract import TextExtractRequest, extract_text


OCR_MODES = {"ocr_image", "ocr_pdf"}
GLOSSARY_MODE = "glossary"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline file conversion helper")
    parser.add_argument(
        "--mode",
        required=True,
        choices=[mode.value for mode in ConversionMode] + sorted(OCR_MODES) + [GLOSSARY_MODE],
        help="Conversion mode.",
    )
    parser.add_argument(
        "--input",
        required=True,
        nargs="+",
        type=Path,
        help="Input file(s).",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output file path.",
    )
    parser.add_argument(
        "--lang",
        default="eng",
        help="OCR language(s), e.g. eng or chi_sim+eng.",
    )
    parser.add_argument(
        "--dpi",
        default=300,
        type=int,
        help="DPI used when rendering PDF pages for OCR.",
    )
    parser.add_argument(
        "--top-k",
        default=30,
        type=int,
        help="Number of glossary entries to return.",
    )
    parser.add_argument(
        "--window-size",
        default=4,
        type=int,
        help="Co-occurrence window size for glossary extraction.",
    )
    parser.add_argument(
        "--min-term-length",
        default=2,
        type=int,
        help="Minimum length for glossary terms.",
    )
    parser.add_argument(
        "--glossary-format",
        choices=["txt", "json"],
        default="txt",
        help="Glossary output format.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode in OCR_MODES:
        output = _run_ocr(args)
        print(f"OCR saved to: {output}")
        return
    if args.mode == GLOSSARY_MODE:
        output = _run_glossary(args)
        print(f"Glossary saved to: {output}")
        return

    request = ConversionRequest(
        mode=ConversionMode(args.mode),
        input_paths=args.input,
        output_path=args.output,
    )
    output = convert(request)
    print(f"Converted to: {output}")


def _run_ocr(args: argparse.Namespace) -> Path:
    if len(args.input) != 1:
        raise ValueError("OCR requires exactly one input file.")

    request = OcrRequest(
        input_path=args.input[0],
        language=args.lang,
        dpi=args.dpi,
    )
    if args.mode == "ocr_image":
        result = ocr_image(request)
    else:
        result = ocr_pdf(request)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.text, encoding="utf-8")
    return args.output


def _run_glossary(args: argparse.Namespace) -> Path:
    if not args.input:
        raise ValueError("Glossary generation requires at least one input file.")

    texts = [
        extract_text(
            TextExtractRequest(
                input_path=path,
                language=args.lang,
                dpi=args.dpi,
            )
        )
        for path in args.input
    ]
    request = GlossaryRequest(
        texts=texts,
        top_k=args.top_k,
        window_size=args.window_size,
        min_term_length=args.min_term_length,
    )
    result = generate_glossary(request)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.glossary_format == "json":
        payload = [entry.__dict__ for entry in result.entries]
        args.output.write_text(_to_json(payload), encoding="utf-8")
    else:
        lines = [f"{entry.term}\t{entry.score:.4f}" for entry in result.entries]
        args.output.write_text("\n".join(lines), encoding="utf-8")
    return args.output


def _to_json(payload: list[dict[str, object]]) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()