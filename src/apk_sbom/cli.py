from __future__ import annotations

import argparse
import sys

from apk_sbom.apk_extractor import inspect_apk
from apk_sbom.dex_analyzer import analyze_apk_dex


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apk-sbom",
        description="MVP utilities for recovering SBOM evidence from compiled Android APKs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser(
        "inspect-apk",
        help="Inspect an APK archive and output a JSON extraction summary.",
    )
    inspect_parser.add_argument("apk_path", help="Path to the APK file.")

    analyze_parser = subparsers.add_parser(
        "analyze-dex",
        help="Parse APK DEX files and output class/package/opcode feature counts.",
    )
    analyze_parser.add_argument("apk_path", help="Path to the APK file.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "inspect-apk":
        try:
            inspection = inspect_apk(args.apk_path)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(inspection.to_json())
        return 0

    if args.command == "analyze-dex":
        try:
            analysis = analyze_apk_dex(args.apk_path)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(analysis.to_json())
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
