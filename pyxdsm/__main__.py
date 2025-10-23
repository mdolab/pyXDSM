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
    """Main entry point for the pyXDSM CLI."""
    parser = argparse.ArgumentParser(
        description="Generate XDSM diagrams from JSON specification files",
        prog="python -m pyxdsm"
    )

    parser.add_argument(
        "input",
        type=str,
        help="Input JSON specification file"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Output file path (e.g., output.pdf or output.tikz)"
    )

    parser.add_argument(
        "--cleanup",
        action="store_true",
        default=True,
        help="Clean up auxiliary files after PDF build (default: True)"
    )

    parser.add_argument(
        "--no-cleanup",
        action="store_false",
        dest="cleanup",
        help="Keep auxiliary files after PDF build"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress pdflatex output"
    )

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

    # Parse output path
    output_path = Path(args.output)
    outdir = str(output_path.parent) if output_path.parent != Path(".") else "."
    file_name = output_path.stem
    extension = output_path.suffix.lower()

    # Determine build flag based on output extension
    if extension == ".pdf":
        build = True
    elif extension == ".tikz":
        build = False
    else:
        print(f"Warning: Unknown extension '{extension}'. Defaulting to PDF build.",
              file=sys.stderr)
        build = True

    # Build the diagram
    try:
        xdsm.write(
            file_name=file_name,
            build=build,
            cleanup=args.cleanup,
            quiet=args.quiet,
            outdir=outdir
        )
        print(f"Successfully generated {args.output}")
    except Exception as e:
        print(f"Error generating output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
