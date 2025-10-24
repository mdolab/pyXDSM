"""
Command-line interface for pyXDSM.

Allows running pyXDSM from the command line:
    python -m pyxdsm input.json -o output.pdf
"""

import argparse
import sys
from pathlib import Path

from .XDSM import XDSM


def main():
    """Main entry point for the pyxdsm CLI."""
    parser = argparse.ArgumentParser(
        description="Generate XDSM diagrams from JSON specification files", prog="python -m pyxdsm"
    )

    parser.add_argument("input", type=str, help="Input JSON specification file")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        default=None,
        help="Output file path (e.g., output.pdf or output.tikz). If not provided, defaults to input filename with .pdf extension",
    )

    parser.add_argument(
        "-c",
        "--cleanup",
        action="store_true",
        default=True,
        help="Clean up auxiliary files after PDF build (default: True)",
    )

    parser.add_argument("-q", "--quiet", action="store_true", default=False, help="Suppress pdflatex output")

    args = parser.parse_args()

    # Load XDSM from JSON
    try:
        xdsm = XDSM.from_json(args.input)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output is None:
        input_path = Path(args.input)
        output_path = input_path.with_suffix(".pdf")
    else:
        output_path = Path(args.output)

    outdir = str(output_path.parent) if output_path.parent != Path(".") else "."
    file_name = output_path.stem
    extension = output_path.suffix.lower()

    if extension.lower() == ".json":
        xdsm.to_json(output_path)
        print(f"Successfully generated {output_path}")
    else:
        if extension.lower() not in (".pdf", ".tikz"):
            print(f"Warning: Unknown output extension '{extension}'. Defaulting to PDF build.", file=sys.stderr)
            extension = ".pdf"
        xdsm.write(
            file_name=file_name,
            build=extension.lower() == ".pdf",
            cleanup=args.cleanup,
            quiet=args.quiet,
            outdir=outdir,
        )
        print(f"Successfully generated {args.output}")


if __name__ == "__main__":
    main()
