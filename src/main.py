from __future__ import annotations

import argparse
from pathlib import Path

from conversion import ConversionMode, ConversionRequest, convert


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline file conversion helper")
    parser.add_argument(
        "--mode",
        required=True,
        choices=[mode.value for mode in ConversionMode],
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request = ConversionRequest(
        mode=ConversionMode(args.mode),
        input_paths=args.input,
        output_path=args.output,
    )
    output = convert(request)
    print(f"Converted to: {output}")


if __name__ == "__main__":
    main()