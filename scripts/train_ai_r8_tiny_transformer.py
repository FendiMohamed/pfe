from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


DEFAULT_CORPUS_JSON = Path(
    "data/results/experiments/ai-r8-dl-prototype/token-corpus.json"
)
DEFAULT_METRICS_JSON = Path(
    "data/results/experiments/ai-r8-dl-prototype/metrics.json"
)
DEFAULT_DOC = Path("docs/evaluation/AI_R8_DL_PROTOTYPE.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Train the isolated Phase 6B tiny Transformer prototype when torch is "
            "available. This is not wired into production reports."
        ),
    )
    parser.add_argument(
        "--corpus-json",
        default=str(DEFAULT_CORPUS_JSON),
        help="Token corpus manifest JSON.",
    )
    parser.add_argument(
        "--metrics-output",
        default=str(DEFAULT_METRICS_JSON),
        help="Output metrics JSON.",
    )
    parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_DOC),
        help="Output prototype Markdown report.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    metrics_output = Path(args.metrics_output)
    doc_output = Path(args.output_doc)
    metrics_output.parent.mkdir(parents=True, exist_ok=True)
    doc_output.parent.mkdir(parents=True, exist_ok=True)

    torch_available = importlib.util.find_spec("torch") is not None
    payload = {
        "schema_version": "ai-r8-dl-prototype-metrics-v1",
        "status": "skipped-missing-optional-dependency"
        if not torch_available
        else "ready-for-training-data",
        "model_type": "torch.nn.TransformerEncoder",
        "report_only": True,
        "production_wiring": "disabled",
        "corpus_json": str(args.corpus_json),
        "missing_optional_dependencies": [] if torch_available else ["torch"],
        "task": "binary/multiclass identity-risk classification, not exact version authority",
    }
    metrics_output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc_output.write_text(
        "\n".join(
            [
                "# AI R8 DL Prototype",
                "",
                "This is the isolated Phase 6B LibAttention-inspired prototype scaffold.",
                "",
                f"- Status: `{payload['status']}`",
                "- Model family: `torch.nn.TransformerEncoder`",
                "- Production report wiring: `disabled`",
                "- Authority: identity-risk research only, not exact SBOM versioning or CVE labeling.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "metrics_json": str(metrics_output),
                "diagnostics_doc": str(doc_output),
                "status": payload["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

