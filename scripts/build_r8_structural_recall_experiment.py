from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.r8_structural_recall_experiment import (  # noqa: E402
    DEFAULT_AI_SUGGESTIONS_JSON,
    DEFAULT_LARGE_ANALYSIS_JSON,
    DEFAULT_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON,
    DEFAULT_ROUTER_JSON,
    build_payload,
    write_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the report-only R8 structural recall experiment from the "
            "Hybrid Matcher Router queue and current real-APK evaluation artifacts."
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
        help="Large combined real-APK analysis JSON with normal baseline controls.",
    )
    parser.add_argument(
        "--ai-suggestions-json",
        default=str(DEFAULT_AI_SUGGESTIONS_JSON),
        help="AI R8 suggestions JSON.",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Output experiment JSON.",
    )
    parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_OUTPUT_DOC),
        help="Output experiment Markdown report.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        router_json=args.router_json,
        large_analysis_json=args.large_analysis_json,
        ai_suggestions_json=args.ai_suggestions_json,
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
