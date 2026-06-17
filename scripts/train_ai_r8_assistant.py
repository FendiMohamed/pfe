from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.ai_r8_assistant import (
    DEFAULT_METRICS_JSON,
    DEFAULT_MODEL_PATH,
    DEFAULT_TRAINING_DATASET_JSON,
    train_ai_r8_assistant,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train the report-only AI R8 assistant RandomForest model.",
    )
    parser.add_argument(
        "--dataset-json",
        default=str(DEFAULT_TRAINING_DATASET_JSON),
        help="Training dataset JSON.",
    )
    parser.add_argument(
        "--model-output",
        default=str(DEFAULT_MODEL_PATH),
        help="Output joblib model path.",
    )
    parser.add_argument(
        "--metrics-output",
        default=str(DEFAULT_METRICS_JSON),
        help="Output metrics JSON path.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    metrics = train_ai_r8_assistant(
        dataset_json=args.dataset_json,
        model_path=args.model_output,
        metrics_json=args.metrics_output,
    )
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
