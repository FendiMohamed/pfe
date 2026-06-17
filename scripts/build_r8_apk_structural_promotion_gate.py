from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.r8_apk_structural_promotion_gate import (  # noqa: E402
    DEFAULT_AI_SUGGESTIONS_JSON,
    DEFAULT_LARGE_ANALYSIS_JSON,
    DEFAULT_MAX_NAME_SCORE,
    DEFAULT_MIN_DEPENDENCY_SCORE,
    DEFAULT_MIN_IDENTITY_CONFIDENCE,
    DEFAULT_MIN_LITERAL_SCORE,
    DEFAULT_MIN_OPCODE_SCORE,
    DEFAULT_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON,
    DEFAULT_ROUTER_JSON,
    build_payload,
    write_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the APK-only structural promotion gate for the R8 structural "
            "recall lane. The artifact is report-only and does not change matcher "
            "or SBOM behavior."
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
        help="Large combined real-APK analysis JSON with emitted controls.",
    )
    parser.add_argument(
        "--ai-suggestions-json",
        default=str(DEFAULT_AI_SUGGESTIONS_JSON),
        help="AI R8 suggestions JSON.",
    )
    parser.add_argument(
        "--min-opcode-score",
        type=float,
        default=DEFAULT_MIN_OPCODE_SCORE,
        help="Minimum opcode score required to pass the APK-only gate.",
    )
    parser.add_argument(
        "--min-literal-score",
        type=float,
        default=DEFAULT_MIN_LITERAL_SCORE,
        help="Minimum literal score required to pass the APK-only gate.",
    )
    parser.add_argument(
        "--min-dependency-score",
        type=float,
        default=DEFAULT_MIN_DEPENDENCY_SCORE,
        help="Minimum dependency score required to pass the APK-only gate.",
    )
    parser.add_argument(
        "--max-name-score",
        type=float,
        default=DEFAULT_MAX_NAME_SCORE,
        help="Maximum class/method name score for the R8 structural profile.",
    )
    parser.add_argument(
        "--min-identity-confidence",
        type=float,
        default=DEFAULT_MIN_IDENTITY_CONFIDENCE,
        help="Minimum identity confidence floor for the APK-only gate.",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Output promotion gate JSON.",
    )
    parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_OUTPUT_DOC),
        help="Output promotion gate Markdown report.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        router_json=args.router_json,
        large_analysis_json=args.large_analysis_json,
        ai_suggestions_json=args.ai_suggestions_json,
        min_opcode_score=args.min_opcode_score,
        min_literal_score=args.min_literal_score,
        min_dependency_score=args.min_dependency_score,
        max_name_score=args.max_name_score,
        min_identity_confidence=args.min_identity_confidence,
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
