from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path


DEFAULT_CORPUS_JSON = Path(
    "data/results/experiments/ai-r8-dl-prototype/token-corpus.json"
)
DEFAULT_METRICS_JSON = Path(
    "data/results/experiments/ai-r8-dl-prototype/metrics.json"
)
DEFAULT_MODEL_PATH = Path(
    "data/results/experiments/ai-r8-dl-prototype/tiny-transformer.pt"
)
DEFAULT_DOC = Path("docs/evaluation/AI_R8_DL_PROTOTYPE.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Train the isolated Phase 6B tiny Transformer prototype. It can be "
            "surfaced as status-only report evidence, but production decision "
            "wiring remains disabled."
        ),
    )
    parser.add_argument(
        "--corpus-json",
        default=str(DEFAULT_CORPUS_JSON),
        help="Token corpus JSON.",
    )
    parser.add_argument(
        "--metrics-output",
        default=str(DEFAULT_METRICS_JSON),
        help="Output metrics JSON.",
    )
    parser.add_argument(
        "--model-output",
        default=str(DEFAULT_MODEL_PATH),
        help="Output torch model state path.",
    )
    parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_DOC),
        help="Output prototype Markdown report.",
    )
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--d-model", type=int, default=64)
    parser.add_argument("--nhead", type=int, default=4)
    parser.add_argument("--layers", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    metrics_output = Path(args.metrics_output)
    doc_output = Path(args.output_doc)
    model_output = Path(args.model_output)
    metrics_output.parent.mkdir(parents=True, exist_ok=True)
    doc_output.parent.mkdir(parents=True, exist_ok=True)
    model_output.parent.mkdir(parents=True, exist_ok=True)

    if importlib.util.find_spec("torch") is None:
        payload = _missing_torch_payload(args)
        _write_outputs(payload, metrics_output, doc_output)
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

    import torch
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
    from torch import nn

    torch.manual_seed(42)
    corpus = json.loads(Path(args.corpus_json).read_text(encoding="utf-8"))
    label_set = corpus["label_set"]
    label_to_id = {label: index for index, label in enumerate(label_set)}
    rows = corpus["rows"]
    split_rows = {
        "train": [row for row in rows if row["split"] == "train"],
        "validation": [row for row in rows if row["split"] == "validation"],
        "test": [row for row in rows if row["split"] == "test"],
    }

    train_loader = _loader(split_rows["train"], label_to_id, args.batch_size, shuffle=True)
    validation_loader = _loader(split_rows["validation"], label_to_id, args.batch_size)
    test_loader = _loader(split_rows["test"], label_to_id, args.batch_size)

    model = TinyTransformerClassifier(
        vocab_size=len(corpus["vocabulary"]),
        labels=len(label_set),
        max_length=corpus["max_sequence_length"],
        d_model=args.d_model,
        nhead=args.nhead,
        layers=args.layers,
        pad_id=corpus["vocabulary"]["<pad>"],
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    class_weights = _class_weights(split_rows["train"], label_to_id, torch)
    loss_fn = nn.CrossEntropyLoss(weight=class_weights)

    history = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        batches = 0
        for token_ids, labels in train_loader:
            optimizer.zero_grad()
            logits = model(token_ids)
            loss = loss_fn(logits, labels)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item())
            batches += 1
        validation = _evaluate(
            model,
            validation_loader,
            label_set,
            classification_report,
            confusion_matrix,
            f1_score,
            accuracy_score,
        )
        history.append(
            {
                "epoch": epoch,
                "train_loss": total_loss / max(1, batches),
                "validation_macro_f1": validation["macro_f1"],
                "validation_accuracy": validation["accuracy"],
            }
        )

    test = _evaluate(
        model,
        test_loader,
        label_set,
        classification_report,
        confusion_matrix,
        f1_score,
        accuracy_score,
    )
    validation = _evaluate(
        model,
        validation_loader,
        label_set,
        classification_report,
        confusion_matrix,
        f1_score,
        accuracy_score,
    )

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "label_set": label_set,
            "vocabulary_size": len(corpus["vocabulary"]),
            "max_sequence_length": corpus["max_sequence_length"],
            "parameters": {
                "d_model": args.d_model,
                "nhead": args.nhead,
                "layers": args.layers,
            },
        },
        model_output,
    )

    payload = {
        "schema_version": "ai-r8-dl-prototype-metrics-v2",
        "status": "trained",
        "model_type": "torch.nn.TransformerEncoder",
        "report_only": True,
        "production_wiring": "disabled",
        "corpus_json": str(args.corpus_json),
        "model_path": str(model_output),
        "task": "multiclass identity-risk classification, not exact version authority",
        "parameters": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "d_model": args.d_model,
            "nhead": args.nhead,
            "layers": args.layers,
            "learning_rate": args.learning_rate,
            "random_state": 42,
        },
        "dataset": corpus["summary"],
        "history": history,
        "validation": validation,
        "test": test,
        "limits": [
            "This prototype uses structured project-evidence tokens, not large-scale smali pretraining.",
            "It demonstrates a DL workflow for PhD-readiness; reports may surface its status only.",
            "It cannot change selected versions, SBOM components, vulnerability labels, or source-validation metrics.",
        ],
    }
    _write_outputs(payload, metrics_output, doc_output)
    print(
        json.dumps(
            {
                "metrics_json": str(metrics_output),
                "diagnostics_doc": str(doc_output),
                "model_path": str(model_output),
                "status": payload["status"],
                "test_macro_f1": test["macro_f1"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


class TinyTransformerClassifier:
    def __new__(cls, *args, **kwargs):
        import torch
        from torch import nn

        class _Model(nn.Module):
            def __init__(
                self,
                *,
                vocab_size: int,
                labels: int,
                max_length: int,
                d_model: int,
                nhead: int,
                layers: int,
                pad_id: int,
            ) -> None:
                super().__init__()
                self.pad_id = pad_id
                self.embedding = nn.Embedding(
                    vocab_size,
                    d_model,
                    padding_idx=pad_id,
                )
                self.position = nn.Parameter(torch.zeros(1, max_length, d_model))
                encoder_layer = nn.TransformerEncoderLayer(
                    d_model=d_model,
                    nhead=nhead,
                    dim_feedforward=d_model * 2,
                    dropout=0.1,
                    batch_first=True,
                    activation="gelu",
                )
                self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=layers)
                self.classifier = nn.Sequential(
                    nn.LayerNorm(d_model),
                    nn.Linear(d_model, labels),
                )

            def forward(self, token_ids):
                mask = token_ids.eq(self.pad_id)
                embedded = self.embedding(token_ids) + self.position[:, : token_ids.size(1), :]
                encoded = self.encoder(embedded, src_key_padding_mask=mask)
                valid = (~mask).unsqueeze(-1).float()
                pooled = (encoded * valid).sum(dim=1) / valid.sum(dim=1).clamp_min(1.0)
                return self.classifier(pooled)

        return _Model(*args, **kwargs)


def _loader(rows: list[dict], label_to_id: dict[str, int], batch_size: int, shuffle: bool = False):
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    token_tensor = torch.tensor([row["token_ids"] for row in rows], dtype=torch.long)
    label_tensor = torch.tensor([label_to_id[row["label"]] for row in rows], dtype=torch.long)
    return DataLoader(
        TensorDataset(token_tensor, label_tensor),
        batch_size=batch_size,
        shuffle=shuffle,
    )


def _class_weights(rows: list[dict], label_to_id: dict[str, int], torch):
    counts = Counter(row["label"] for row in rows)
    weights = []
    total = sum(counts.values())
    for label in label_to_id:
        weights.append(total / max(1, counts.get(label, 0)))
    tensor = torch.tensor(weights, dtype=torch.float)
    return tensor / tensor.mean().clamp_min(1e-6)


def _evaluate(
    model,
    loader,
    label_set: list[str],
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
) -> dict:
    import torch

    model.eval()
    true_ids = []
    pred_ids = []
    with torch.no_grad():
        for token_ids, labels in loader:
            logits = model(token_ids)
            predictions = logits.argmax(dim=1)
            true_ids.extend(labels.tolist())
            pred_ids.extend(predictions.tolist())
    if not true_ids:
        return {"macro_f1": None, "accuracy": None, "per_class": {}, "confusion_matrix": []}
    report = classification_report(
        true_ids,
        pred_ids,
        labels=list(range(len(label_set))),
        target_names=label_set,
        output_dict=True,
        zero_division=0,
    )
    return {
        "macro_f1": f1_score(
            true_ids,
            pred_ids,
            labels=list(range(len(label_set))),
            average="macro",
            zero_division=0,
        ),
        "accuracy": accuracy_score(true_ids, pred_ids),
        "per_class": {
            label: {
                "precision": report.get(label, {}).get("precision", 0.0),
                "recall": report.get(label, {}).get("recall", 0.0),
                "f1": report.get(label, {}).get("f1-score", 0.0),
                "support": report.get(label, {}).get("support", 0),
            }
            for label in label_set
        },
        "confusion_matrix": confusion_matrix(
            true_ids,
            pred_ids,
            labels=list(range(len(label_set))),
        ).tolist(),
        "labels": label_set,
    }


def _missing_torch_payload(args) -> dict:
    return {
        "schema_version": "ai-r8-dl-prototype-metrics-v2",
        "status": "skipped-missing-optional-dependency",
        "model_type": "torch.nn.TransformerEncoder",
        "report_only": True,
        "production_wiring": "disabled",
        "corpus_json": str(args.corpus_json),
        "missing_optional_dependencies": ["torch"],
        "task": "multiclass identity-risk classification, not exact version authority",
    }


def _write_outputs(payload: dict, metrics_output: Path, doc_output: Path) -> None:
    metrics_output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc_output.write_text(build_markdown(payload), encoding="utf-8")


def build_markdown(payload: dict) -> str:
    lines = [
        "# AI R8 DL Prototype",
        "",
        "Generated by `scripts/train_ai_r8_tiny_transformer.py`.",
        "",
        "This is the isolated Phase 6B LibAttention-inspired prototype. Reports may surface its status only; production decision wiring remains disabled. The current corpus uses structured project-evidence tokens, not raw smali pretraining.",
        "",
        f"- Status: `{payload.get('status')}`",
        f"- Model family: `{payload.get('model_type')}`",
        "- Production report wiring: `disabled`",
        "- Authority: identity-risk research only, not exact SBOM versioning or CVE labeling.",
        "",
    ]
    if payload.get("status") == "trained":
        test = payload.get("test", {})
        validation = payload.get("validation", {})
        dataset = payload.get("dataset", {})
        lines.extend(
            [
                "## Dataset",
                "",
                f"- Rows: `{dataset.get('rows', 0)}`",
                f"- Vocabulary size: `{dataset.get('vocab_size', 0)}`",
                f"- Splits: `{json.dumps(dataset.get('splits', {}), sort_keys=True)}`",
                "",
                "## Metrics",
                "",
                f"- Validation macro-F1: `{validation.get('macro_f1')}`",
                f"- Test macro-F1: `{test.get('macro_f1')}`",
                f"- Test accuracy: `{test.get('accuracy')}`",
                "",
                "| Label | Precision | Recall | F1 | Support |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for label, row in test.get("per_class", {}).items():
            lines.append(
                "| "
                f"`{label}` | "
                f"{row.get('precision')} | "
                f"{row.get('recall')} | "
                f"{row.get('f1')} | "
                f"{row.get('support')} |"
            )
        lines.extend(
            [
                "",
                "## Training History",
                "",
                "| Epoch | Train loss | Validation macro-F1 | Validation accuracy |",
                "|---:|---:|---:|---:|",
            ]
        )
        for row in payload.get("history", []):
            lines.append(
                "| "
                f"{row.get('epoch')} | "
                f"{row.get('train_loss')} | "
                f"{row.get('validation_macro_f1')} | "
                f"{row.get('validation_accuracy')} |"
            )
    else:
        lines.extend(
            [
                "## Status",
                "",
                "- `torch` is not installed, so the DL prototype was not trained.",
            ]
        )
    lines.extend(
        [
            "",
            "## Limits",
            "",
        ]
    )
    for limit in payload.get("limits", []):
        lines.append(f"- {limit}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
