from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.ai_r8_mvp_integration_gate import (  # noqa: E402
    DEFAULT_AI_METRICS_JSON,
    DEFAULT_AI_SUGGESTIONS_JSON,
    DEFAULT_FINAL_SMOKE_JSON,
    DEFAULT_HYBRID_PRODUCTION_JSON,
    DEFAULT_INDEPENDENT_CORPUS_JSON,
    DEFAULT_MVP_SAFE_DL_METRICS_JSON,
    DEFAULT_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON,
    DEFAULT_RAW_OPCODE_DL_METRICS_JSON,
    DEFAULT_STRICT_GATE_MATRIX_JSON,
    DEFAULT_STRUCTURED_DL_METRICS_JSON,
    write_integration_gate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the AI/R8 MVP integration gate after ML/DL training. The gate "
            "decides what can be integrated as report-only assistance and what "
            "remains blocked from matcher/SBOM/CVE authority."
        )
    )
    parser.add_argument("--ai-metrics-json", default=str(DEFAULT_AI_METRICS_JSON))
    parser.add_argument("--ai-suggestions-json", default=str(DEFAULT_AI_SUGGESTIONS_JSON))
    parser.add_argument(
        "--structured-dl-metrics-json",
        default=str(DEFAULT_STRUCTURED_DL_METRICS_JSON),
    )
    parser.add_argument(
        "--mvp-safe-dl-metrics-json",
        default=str(DEFAULT_MVP_SAFE_DL_METRICS_JSON),
    )
    parser.add_argument(
        "--raw-opcode-dl-metrics-json",
        default=str(DEFAULT_RAW_OPCODE_DL_METRICS_JSON),
    )
    parser.add_argument(
        "--independent-corpus-json",
        default=str(DEFAULT_INDEPENDENT_CORPUS_JSON),
    )
    parser.add_argument(
        "--hybrid-production-json",
        default=str(DEFAULT_HYBRID_PRODUCTION_JSON),
    )
    parser.add_argument("--final-smoke-json", default=str(DEFAULT_FINAL_SMOKE_JSON))
    parser.add_argument(
        "--strict-gate-matrix-json",
        default=str(DEFAULT_STRICT_GATE_MATRIX_JSON),
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = write_integration_gate(
        ai_metrics_json=args.ai_metrics_json,
        ai_suggestions_json=args.ai_suggestions_json,
        structured_dl_metrics_json=args.structured_dl_metrics_json,
        mvp_safe_dl_metrics_json=args.mvp_safe_dl_metrics_json,
        raw_opcode_dl_metrics_json=args.raw_opcode_dl_metrics_json,
        independent_corpus_json=args.independent_corpus_json,
        hybrid_production_json=args.hybrid_production_json,
        final_smoke_json=args.final_smoke_json,
        strict_gate_matrix_json=args.strict_gate_matrix_json,
        output_json=args.output_json,
        output_doc=args.output_doc,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
