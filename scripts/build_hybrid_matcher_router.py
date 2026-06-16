from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.hybrid_matcher_router import (  # noqa: E402
    DEFAULT_AI_SUGGESTIONS_JSON,
    DEFAULT_MATCHER_RECALL_JSON,
    DEFAULT_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON,
    DEFAULT_SOURCE_GAP_JSON,
    DEFAULT_TRANSPARENCY_JSON,
    DEFAULT_WRONG_VERSION_JSON,
    build_payload,
    write_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the report-only Hybrid Matcher Router V1 artifact from the "
            "current matcher-recall, source-gap, wrong-version, and AI "
            "diagnostic outputs."
        )
    )
    parser.add_argument(
        "--matcher-recall-json",
        default=str(DEFAULT_MATCHER_RECALL_JSON),
        help="Matcher-recall diagnostics JSON.",
    )
    parser.add_argument(
        "--transparency-json",
        default=str(DEFAULT_TRANSPARENCY_JSON),
        help="Final transparency export JSON.",
    )
    parser.add_argument(
        "--source-gap-json",
        default=str(DEFAULT_SOURCE_GAP_JSON),
        help="Final source-gap triage JSON.",
    )
    parser.add_argument(
        "--wrong-version-json",
        default=str(DEFAULT_WRONG_VERSION_JSON),
        help="Wrong-version optimization dashboard JSON.",
    )
    parser.add_argument(
        "--ai-suggestions-json",
        default=str(DEFAULT_AI_SUGGESTIONS_JSON),
        help="AI R8 suggestions JSON used as report-only triage evidence.",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Output hybrid matcher router JSON.",
    )
    parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_OUTPUT_DOC),
        help="Output hybrid matcher router Markdown report.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        matcher_recall_json=args.matcher_recall_json,
        transparency_json=args.transparency_json,
        source_gap_json=args.source_gap_json,
        wrong_version_json=args.wrong_version_json,
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
