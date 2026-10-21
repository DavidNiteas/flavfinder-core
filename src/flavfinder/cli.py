"""Command-line entry point for flavfinder-core."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from flavfinder import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flavfinder",
        description=(
            "Independent, code-only port of the flavfinder MS/MS flavonoid "
            "classifier. Training and prediction commands are being ported."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--describe",
        action="store_true",
        help="describe this port and its scope",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.describe:
        print(
            "flavfinder-core is an independent, code-only port of "
            "https://github.com/Ficere/flavfinder.\n"
            "It does not include training data, real example spectra, or "
            "pretrained models."
        )
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
