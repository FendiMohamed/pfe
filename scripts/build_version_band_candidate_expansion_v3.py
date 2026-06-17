from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.version_band_candidate_expansion_v3 import (  # noqa: E402
    DEFAULT_APK_ONLY_JSON,
    DEFAULT_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON,
    DEFAULT_SOURCE_KNOWN_JSON,
    build_payload,
    write_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the version-band candidate expansion v3 promotion-gate report.",
    )
    parser.add_argument(
        "--source-known-json",
        default=str(DEFAULT_SOURCE_KNOWN_JSON),
        help="Source-known version-band rerank experiment JSON.",
    )
    parser.add_argument(
        "--apk-only-json",
        default=str(DEFAULT_APK_ONLY_JSON),
        help="APK-only version-band reranker v2 JSON.",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Output promotion-gate JSON.",
    )
    parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_OUTPUT_DOC),
        help="Output promotion-gate Markdown report.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        source_known_json=args.source_known_json,
        apk_only_json=args.apk_only_json,
    )
    result = write_outputs(
        payload,
        output_json=args.output_json,
        output_doc=args.output_doc,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
