from __future__ import annotations

import argparse
from pathlib import Path

from conversion import ConversionMode, ConversionRequest, convert
from ocr import OcrRequest, ocr_image, ocr_pdf


OCR_MODES = {"ocr_image", "ocr_pdf"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline file conversion helper")
    parser.add_argument(
        "--mode",
        required=True,
        choices=[mode.value for mode in ConversionMode] + sorted(OCR_MODES),
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode in OCR_MODES:
        output = _run_ocr(args)
        print(f"OCR saved to: {output}")
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


if __name__ == "__main__":
    main()
