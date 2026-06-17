from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.ai_r8_final_evaluation import (  # noqa: E402
    DEFAULT_AI_METRICS_JSON,
    DEFAULT_AI_SUMMARY_JSON,
    DEFAULT_DL_METRICS_JSON,
    DEFAULT_INDEPENDENT_CORPUS_JSON,
    DEFAULT_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON,
    DEFAULT_RAW_OPCODE_CORPUS_JSON,
    DEFAULT_REPORT_ONLY_DEMO_JSON,
    build_final_evaluation,
    build_markdown,
    write_final_evaluation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the final thesis/demo evidence package for the Phase 6 "
            "AI-assisted R8 ML/DL layer."
        )
    )
    parser.add_argument("--ai-summary-json", default=str(DEFAULT_AI_SUMMARY_JSON))
    parser.add_argument("--ai-metrics-json", default=str(DEFAULT_AI_METRICS_JSON))
    parser.add_argument("--dl-metrics-json", default=str(DEFAULT_DL_METRICS_JSON))
    parser.add_argument(
        "--report-only-demo-json",
        default=str(DEFAULT_REPORT_ONLY_DEMO_JSON),
    )
    parser.add_argument(
        "--independent-corpus-json",
        default=str(DEFAULT_INDEPENDENT_CORPUS_JSON),
    )
    parser.add_argument(
        "--raw-opcode-corpus-json",
        default=str(DEFAULT_RAW_OPCODE_CORPUS_JSON),
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = write_final_evaluation(
        ai_summary_json=args.ai_summary_json,
        ai_metrics_json=args.ai_metrics_json,
        dl_metrics_json=args.dl_metrics_json,
        report_only_demo_json=args.report_only_demo_json,
        independent_corpus_json=args.independent_corpus_json,
        raw_opcode_corpus_json=args.raw_opcode_corpus_json,
        output_json=args.output_json,
        output_doc=args.output_doc,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
