from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.version_band_apk_reranker import (  # noqa: E402
    DEFAULT_LARGE_ANALYSIS_JSON,
    DEFAULT_MAX_SCORE_DROP,
    DEFAULT_MIN_SIBLING_ERA_ANCHORS,
    DEFAULT_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON,
    DEFAULT_ROUTER_JSON,
    build_payload,
    write_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the report-only APK-only version-band reranker v2 diagnostic."
        )
    )
    parser.add_argument(
        "--router-json",
        default=str(DEFAULT_ROUTER_JSON),
        help="Hybrid matcher router JSON.",
    )
    parser.add_argument(
        "--large-analysis-json",
        default=str(DEFAULT_LARGE_ANALYSIS_JSON),
        help="Large combined real-APK analysis JSON with baseline APK-only reports.",
    )
    parser.add_argument(
        "--max-score-drop",
        type=float,
        default=DEFAULT_MAX_SCORE_DROP,
        help="Maximum allowed score drop from selected version to alternative.",
    )
    parser.add_argument(
        "--min-sibling-era-anchors",
        type=int,
        default=DEFAULT_MIN_SIBLING_ERA_ANCHORS,
        help="Minimum same-family sibling selected-version era anchors.",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Output diagnostic JSON.",
    )
    parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_OUTPUT_DOC),
        help="Output diagnostic Markdown report.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        router_json=args.router_json,
        large_analysis_json=args.large_analysis_json,
        max_score_drop=args.max_score_drop,
        min_sibling_era_anchors=args.min_sibling_era_anchors,
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
