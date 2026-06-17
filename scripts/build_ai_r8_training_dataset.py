from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.ai_r8_assistant import (
    DEFAULT_MATCHER_RECALL_DIAGNOSTICS,
    DEFAULT_PHASE5_DIAGNOSTICS,
    DEFAULT_R8_OBFUSCATION_DIAGNOSTICS,
    DEFAULT_TRAINING_DATASET_CSV,
    DEFAULT_TRAINING_DATASET_JSON,
    DEFAULT_TRANSPARENCY_EXPORT,
    build_training_dataset,
    write_training_dataset,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the report-only AI R8 assistant training dataset.",
    )
    parser.add_argument(
        "--matcher-recall-json",
        default=str(DEFAULT_MATCHER_RECALL_DIAGNOSTICS),
        help="Matcher-recall diagnostics JSON.",
    )
    parser.add_argument(
        "--transparency-json",
        default=str(DEFAULT_TRANSPARENCY_EXPORT),
        help="Final transparency export JSON.",
    )
    parser.add_argument(
        "--phase5-json",
        default=str(DEFAULT_PHASE5_DIAGNOSTICS),
        help="Phase 5 scoped trigger diagnostics JSON.",
    )
    parser.add_argument(
        "--r8-obfuscation-json",
        default=str(DEFAULT_R8_OBFUSCATION_DIAGNOSTICS),
        help="R8 obfuscation diagnostics JSON.",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_TRAINING_DATASET_JSON),
        help="Output training dataset JSON.",
    )
    parser.add_argument(
        "--output-csv",
        default=str(DEFAULT_TRAINING_DATASET_CSV),
        help="Output training dataset CSV.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    payload = build_training_dataset(
        matcher_recall_json=args.matcher_recall_json,
        transparency_json=args.transparency_json,
        phase5_json=args.phase5_json,
        r8_obfuscation_json=args.r8_obfuscation_json,
    )
    result = write_training_dataset(
        payload,
        json_path=args.output_json,
        csv_path=args.output_csv,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
