from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.ai_r8_assistant import (
    DEFAULT_DIAGNOSTICS_DOC,
    DEFAULT_METRICS_JSON,
    DEFAULT_SUGGESTIONS_JSON,
    DEFAULT_TRAINING_DATASET_JSON,
    build_ai_r8_suggestions,
    write_ai_r8_diagnostics,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build report-only AI R8 assistant suggestions and diagnostics.",
    )
    parser.add_argument(
        "--dataset-json",
        default=str(DEFAULT_TRAINING_DATASET_JSON),
        help="Training dataset JSON.",
    )
    parser.add_argument(
        "--metrics-json",
        default=str(DEFAULT_METRICS_JSON),
        help="Metrics JSON produced by train_ai_r8_assistant.py.",
    )
    parser.add_argument(
        "--suggestions-json",
        default=str(DEFAULT_SUGGESTIONS_JSON),
        help="Output suggestions JSON.",
    )
    parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_DIAGNOSTICS_DOC),
        help="Output diagnostics Markdown.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    build_ai_r8_suggestions(
        dataset_json=args.dataset_json,
        metrics_json=args.metrics_json,
        output_json=args.suggestions_json,
    )
    result = write_ai_r8_diagnostics(
        dataset_json=args.dataset_json,
        metrics_json=args.metrics_json,
        suggestions_json=args.suggestions_json,
        output_doc=args.output_doc,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
