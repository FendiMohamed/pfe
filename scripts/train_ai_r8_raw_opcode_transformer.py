from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_CORPUS_JSON = Path(
    "data/results/experiments/ai-r8-raw-opcode-prototype/raw-opcode-corpus.json"
)
DEFAULT_METRICS_JSON = Path(
    "data/results/experiments/ai-r8-raw-opcode-prototype/metrics.json"
)
DEFAULT_MODEL_PATH = Path(
    "data/results/experiments/ai-r8-raw-opcode-prototype/raw-opcode-transformer.pt"
)
DEFAULT_DOC = Path("docs/evaluation/AI_R8_RAW_OPCODE_TRANSFORMER.md")
SPECIAL_TOKEN_IDS = {0, 1, 2, 3}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Train an isolated raw DEX/opcode Transformer prototype for the AI/R8 "
            "lane. The model is report-only research evidence and cannot change "
            "matcher, SBOM, CVE, or source-validation behavior."
        )
    )
    parser.add_argument("--corpus-json", default=str(DEFAULT_CORPUS_JSON))
    parser.add_argument("--metrics-output", default=str(DEFAULT_METRICS_JSON))
    parser.add_argument("--model-output", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--output-doc", default=str(DEFAULT_DOC))
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=64)
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

    missing = missing_optional_dependencies()
    if missing:
        payload = missing_dependency_payload(args, missing)
        write_outputs(payload, metrics_output, doc_output)
        print(
            json.dumps(
                {
                    "metrics_json": normalize_path(metrics_output),
                    "diagnostics_doc": normalize_path(doc_output),
                    "status": payload["status"],
                    "missing_optional_dependencies": missing,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    import torch
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        confusion_matrix,
        f1_score,
    )
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.linear_model import LogisticRegression
    from torch import nn

    torch.manual_seed(42)
    corpus = json.loads(Path(args.corpus_json).read_text(encoding="utf-8"))
    rows = corpus.get("rows", [])
    label_set = sorted(corpus.get("summary", {}).get("labels", {}).keys())
    label_to_id = {label: index for index, label in enumerate(label_set)}
    split_rows = case_heldout_split(rows)

    train_loader = loader(split_rows["train"], label_to_id, args.batch_size, shuffle=True)
    validation_loader = loader(split_rows["validation"], label_to_id, args.batch_size)
    test_loader = loader(split_rows["test"], label_to_id, args.batch_size)

    baselines = {
        "majority_class": majority_baseline(
            split_rows,
            label_set,
            classification_report=classification_report,
            confusion_matrix=confusion_matrix,
            f1_score=f1_score,
            accuracy_score=accuracy_score,
        ),
        "opcode_count_logistic_regression": opcode_count_logistic_regression_baseline(
            split_rows,
            label_set,
            DictVectorizer=DictVectorizer,
            LogisticRegression=LogisticRegression,
            classification_report=classification_report,
            confusion_matrix=confusion_matrix,
            f1_score=f1_score,
            accuracy_score=accuracy_score,
        ),
    }

    model = TinyOpcodeTransformerClassifier(
        vocab_size=len(corpus["vocabulary"]),
        labels=len(label_set),
        max_length=corpus["max_sequence_length"],
        d_model=args.d_model,
        nhead=args.nhead,
        layers=args.layers,
        pad_id=corpus["vocabulary"]["<pad>"],
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    loss_fn = nn.CrossEntropyLoss(weight=class_weights(split_rows["train"], label_to_id, torch))

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
        validation = evaluate_model(
            model,
            validation_loader,
            label_set,
            classification_report=classification_report,
            confusion_matrix=confusion_matrix,
            f1_score=f1_score,
            accuracy_score=accuracy_score,
        )
        history.append(
            {
                "epoch": epoch,
                "train_loss": total_loss / max(1, batches),
                "validation_macro_f1": validation["macro_f1"],
                "validation_accuracy": validation["accuracy"],
            }
        )

    validation = evaluate_model(
        model,
        validation_loader,
        label_set,
        classification_report=classification_report,
        confusion_matrix=confusion_matrix,
        f1_score=f1_score,
        accuracy_score=accuracy_score,
    )
    test = evaluate_model(
        model,
        test_loader,
        label_set,
        classification_report=classification_report,
        confusion_matrix=confusion_matrix,
        f1_score=f1_score,
        accuracy_score=accuracy_score,
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

    baseline_comparison = build_baseline_comparison(baselines, test)
    payload = {
        "schema_version": "ai-r8-raw-opcode-transformer-metrics-v1",
        "status": "trained",
        "model_type": "torch.nn.TransformerEncoder",
        "report_only": True,
        "production_wiring": "disabled",
        "corpus_json": normalize_path(args.corpus_json),
        "model_path": normalize_path(model_output),
        "task": "APK-role/obfuscation-profile triage from raw DEX method opcode sequences, not exact version authority",
        "parameters": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "d_model": args.d_model,
            "nhead": args.nhead,
            "layers": args.layers,
            "learning_rate": args.learning_rate,
            "random_state": 42,
        },
        "dataset": {
            **corpus.get("summary", {}),
            "label_set": label_set,
            "splits": split_summary(split_rows),
            "split_strategy": (
                "case-heldout by label: one APK case per label is held out for "
                "test; validation is a deterministic sample from training cases "
                "because the current corpus has two APK cases per label."
            ),
        },
        "baselines": baselines,
        "baseline_comparison": baseline_comparison,
        "history": history,
        "validation": validation,
        "test": test,
        "limits": [
            "This raw opcode model classifies method-level opcode sequences by APK role/obfuscation profile; it is not exact library-version authority.",
            "The current corpus is intentionally bounded for local reproducibility and is not a large external pretraining corpus.",
            "The case-heldout test is stricter than random row splitting, but each label currently has only two APK cases.",
            "The model is not wired into generate-report, matcher scoring, CycloneDX SBOM output, vulnerability labels, or source-validation metrics.",
        ],
    }
    write_outputs(payload, metrics_output, doc_output)
    print(
        json.dumps(
            {
                "metrics_json": normalize_path(metrics_output),
                "diagnostics_doc": normalize_path(doc_output),
                "model_path": normalize_path(model_output),
                "status": payload["status"],
                "test_macro_f1": test["macro_f1"],
                "opcode_count_baseline_macro_f1": baselines[
                    "opcode_count_logistic_regression"
                ]["test"]["macro_f1"],
                "verdict": baseline_comparison["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


class TinyOpcodeTransformerClassifier:
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
                self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
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


def case_heldout_split(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    cases_by_label: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        label = str(row.get("label") or "")
        case_id = str(row.get("case_id") or "")
        if case_id and case_id not in cases_by_label[label]:
            cases_by_label[label].append(case_id)

    test_cases: set[str] = set()
    for label, case_ids in cases_by_label.items():
        sorted_cases = sorted(case_ids)
        if len(sorted_cases) > 1:
            test_cases.add(sorted_cases[-1])

    train_pool = [row for row in rows if str(row.get("case_id") or "") not in test_cases]
    test_rows = [row for row in rows if str(row.get("case_id") or "") in test_cases]

    validation_rows: list[dict[str, Any]] = []
    train_rows: list[dict[str, Any]] = []
    train_by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in train_pool:
        train_by_label[str(row.get("label") or "")].append(row)

    for label, label_rows in train_by_label.items():
        selected_validation = [
            row for row in label_rows if stable_bucket(str(row.get("row_id") or "")) == 0
        ]
        if not selected_validation and len(label_rows) > 1:
            selected_validation = [sorted(label_rows, key=lambda item: item.get("row_id", ""))[0]]
        selected_ids = {id(row) for row in selected_validation}
        validation_rows.extend(selected_validation)
        train_rows.extend(row for row in label_rows if id(row) not in selected_ids)

    return {
        "train": sorted(train_rows, key=lambda row: row.get("row_id", "")),
        "validation": sorted(validation_rows, key=lambda row: row.get("row_id", "")),
        "test": sorted(test_rows, key=lambda row: row.get("row_id", "")),
    }


def stable_bucket(value: str, *, modulo: int = 5) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % modulo


def loader(
    rows: list[dict[str, Any]],
    label_to_id: dict[str, int],
    batch_size: int,
    *,
    shuffle: bool = False,
):
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    token_tensor = torch.tensor([row["token_ids"] for row in rows], dtype=torch.long)
    label_tensor = torch.tensor(
        [label_to_id[str(row["label"])] for row in rows],
        dtype=torch.long,
    )
    return DataLoader(
        TensorDataset(token_tensor, label_tensor),
        batch_size=batch_size,
        shuffle=shuffle,
    )


def class_weights(rows: list[dict[str, Any]], label_to_id: dict[str, int], torch):
    counts = Counter(str(row.get("label") or "") for row in rows)
    total = sum(counts.values())
    weights = [total / max(1, counts.get(label, 0)) for label in label_to_id]
    tensor = torch.tensor(weights, dtype=torch.float)
    return tensor / tensor.mean().clamp_min(1e-6)


def majority_baseline(
    split_rows: dict[str, list[dict[str, Any]]],
    label_set: list[str],
    *,
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
) -> dict[str, Any]:
    majority = Counter(row["label"] for row in split_rows["train"]).most_common(1)[0][0]
    return {
        "prediction": majority,
        "validation": evaluate_predictions(
            [row["label"] for row in split_rows["validation"]],
            [majority for _ in split_rows["validation"]],
            label_set,
            classification_report=classification_report,
            confusion_matrix=confusion_matrix,
            f1_score=f1_score,
            accuracy_score=accuracy_score,
        ),
        "test": evaluate_predictions(
            [row["label"] for row in split_rows["test"]],
            [majority for _ in split_rows["test"]],
            label_set,
            classification_report=classification_report,
            confusion_matrix=confusion_matrix,
            f1_score=f1_score,
            accuracy_score=accuracy_score,
        ),
    }


def opcode_count_logistic_regression_baseline(
    split_rows: dict[str, list[dict[str, Any]]],
    label_set: list[str],
    *,
    DictVectorizer,
    LogisticRegression,
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
) -> dict[str, Any]:
    vectorizer = DictVectorizer()
    train_x = vectorizer.fit_transform(row_token_counts(row) for row in split_rows["train"])
    train_y = [row["label"] for row in split_rows["train"]]
    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=42,
        solver="lbfgs",
    )
    model.fit(train_x, train_y)
    return {
        "model_type": "sklearn.linear_model.LogisticRegression",
        "feature_count": len(vectorizer.feature_names_),
        "validation": evaluate_predictions(
            [row["label"] for row in split_rows["validation"]],
            model.predict(vectorizer.transform(row_token_counts(row) for row in split_rows["validation"])),
            label_set,
            classification_report=classification_report,
            confusion_matrix=confusion_matrix,
            f1_score=f1_score,
            accuracy_score=accuracy_score,
        ),
        "test": evaluate_predictions(
            [row["label"] for row in split_rows["test"]],
            model.predict(vectorizer.transform(row_token_counts(row) for row in split_rows["test"])),
            label_set,
            classification_report=classification_report,
            confusion_matrix=confusion_matrix,
            f1_score=f1_score,
            accuracy_score=accuracy_score,
        ),
    }


def row_token_counts(row: dict[str, Any]) -> dict[str, int]:
    counts = Counter(
        token_id
        for token_id in row.get("token_ids", [])
        if int(token_id) not in SPECIAL_TOKEN_IDS
    )
    return {f"tok:{token_id}": count for token_id, count in sorted(counts.items())}


def build_baseline_comparison(
    baselines: dict[str, Any],
    transformer_test: dict[str, Any],
) -> dict[str, Any]:
    transformer_f1 = float(transformer_test.get("macro_f1") or 0.0)
    baseline_rows = {
        name: float(row.get("test", {}).get("macro_f1") or 0.0)
        for name, row in baselines.items()
    }
    best_name = max(baseline_rows, key=baseline_rows.get)
    best_f1 = baseline_rows[best_name]
    return {
        "best_baseline": best_name,
        "best_baseline_test_macro_f1": best_f1,
        "transformer_test_macro_f1": transformer_f1,
        "delta_vs_best_baseline": transformer_f1 - best_f1,
        "beats_best_baseline": transformer_f1 > best_f1,
        "verdict": (
            "raw-opcode-transformer-research-only-not-promotable"
            if transformer_f1 <= best_f1
            else "raw-opcode-transformer-beats-baseline-needs-larger-controls"
        ),
    }


def evaluate_model(
    model,
    data_loader,
    label_set: list[str],
    *,
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
) -> dict[str, Any]:
    import torch

    model.eval()
    true_ids: list[int] = []
    pred_ids: list[int] = []
    with torch.no_grad():
        for token_ids, labels in data_loader:
            logits = model(token_ids)
            predictions = logits.argmax(dim=1)
            true_ids.extend(labels.tolist())
            pred_ids.extend(predictions.tolist())
    true_labels = [label_set[index] for index in true_ids]
    pred_labels = [label_set[index] for index in pred_ids]
    return evaluate_predictions(
        true_labels,
        pred_labels,
        label_set,
        classification_report=classification_report,
        confusion_matrix=confusion_matrix,
        f1_score=f1_score,
        accuracy_score=accuracy_score,
    )


def evaluate_predictions(
    true_labels: list[str],
    predicted_labels: list[str],
    label_set: list[str],
    *,
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
) -> dict[str, Any]:
    if not true_labels:
        return {"macro_f1": None, "accuracy": None, "per_class": {}, "confusion_matrix": []}
    report = classification_report(
        true_labels,
        predicted_labels,
        labels=label_set,
        target_names=label_set,
        output_dict=True,
        zero_division=0,
    )
    return {
        "macro_f1": f1_score(
            true_labels,
            predicted_labels,
            labels=label_set,
            average="macro",
            zero_division=0,
        ),
        "accuracy": accuracy_score(true_labels, predicted_labels),
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
            true_labels,
            predicted_labels,
            labels=label_set,
        ).tolist(),
        "labels": label_set,
    }


def split_summary(split_rows: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        split: {
            "rows": len(rows),
            "case_ids": len({row.get("case_id") for row in rows}),
            "labels": dict(sorted(Counter(row.get("label") for row in rows).items())),
        }
        for split, rows in split_rows.items()
    }


def missing_optional_dependencies() -> list[str]:
    missing = []
    if importlib.util.find_spec("torch") is None:
        missing.append("torch")
    if importlib.util.find_spec("sklearn") is None:
        missing.append("scikit-learn")
    return missing


def missing_dependency_payload(args, missing: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "ai-r8-raw-opcode-transformer-metrics-v1",
        "status": "skipped-missing-optional-dependency",
        "model_type": "torch.nn.TransformerEncoder",
        "report_only": True,
        "production_wiring": "disabled",
        "corpus_json": normalize_path(args.corpus_json),
        "missing_optional_dependencies": missing,
        "task": "APK-role/obfuscation-profile triage from raw DEX method opcode sequences, not exact version authority",
    }


def write_outputs(payload: dict[str, Any], metrics_output: Path, doc_output: Path) -> None:
    metrics_output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc_output.write_text(build_markdown(payload), encoding="utf-8")


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# AI R8 Raw Opcode Transformer",
        "",
        "Generated by `scripts/train_ai_r8_raw_opcode_transformer.py`.",
        "",
        "This is the isolated raw DEX/opcode Transformer prototype for the AI/R8 lane. It is report-only research evidence; production decision wiring remains disabled.",
        "",
        f"- Status: `{payload.get('status')}`",
        f"- Model family: `{payload.get('model_type')}`",
        "- Production report wiring: `disabled`",
        "- Authority: opcode-profile research only, not exact SBOM versioning or CVE labeling.",
        "",
    ]
    if payload.get("status") != "trained":
        lines.extend(
            [
                "## Status",
                "",
                f"- Missing optional dependencies: `{payload.get('missing_optional_dependencies', [])}`",
                "",
            ]
        )
        return "\n".join(lines)

    dataset = payload.get("dataset", {})
    test = payload.get("test", {})
    validation = payload.get("validation", {})
    baselines = payload.get("baselines", {})
    comparison = payload.get("baseline_comparison", {})
    lines.extend(
        [
            "## Dataset",
            "",
            f"- Method opcode sequence rows: `{dataset.get('method_sequence_rows')}`",
            f"- APKs analyzed: `{dataset.get('apks_analyzed')}`",
            f"- Vocabulary size: `{dataset.get('vocab_size')}`",
            f"- Split strategy: {dataset.get('split_strategy')}",
            "",
            "| Split | Rows | Case IDs | Labels |",
            "|---|---:|---:|---|",
        ]
    )
    for split, row in dataset.get("splits", {}).items():
        lines.append(
            "| "
            f"`{split}` | "
            f"{row.get('rows')} | "
            f"{row.get('case_ids')} | "
            f"`{json.dumps(row.get('labels', {}), sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Baselines",
            "",
            "| Baseline | Validation macro-F1 | Test macro-F1 | Test accuracy |",
            "|---|---:|---:|---:|",
        ]
    )
    for name, row in baselines.items():
        lines.append(
            "| "
            f"`{name}` | "
            f"{row.get('validation', {}).get('macro_f1')} | "
            f"{row.get('test', {}).get('macro_f1')} | "
            f"{row.get('test', {}).get('accuracy')} |"
        )
    lines.extend(
        [
            "",
            "## Transformer Metrics",
            "",
            f"- Validation macro-F1: `{validation.get('macro_f1')}`",
            f"- Validation accuracy: `{validation.get('accuracy')}`",
            f"- Test macro-F1: `{test.get('macro_f1')}`",
            f"- Test accuracy: `{test.get('accuracy')}`",
            f"- Best baseline: `{comparison.get('best_baseline')}`",
            f"- Delta vs best baseline: `{comparison.get('delta_vs_best_baseline')}`",
            f"- Verdict: `{comparison.get('verdict')}`",
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
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This result is useful for the PhD/AI story because it trains directly on raw DEX opcode sequences instead of only structured matcher-evidence tokens. The task is intentionally narrower than SBOM versioning: it asks whether opcode sequences can separate controlled R8/real-world profile classes under a case-heldout split.",
            "",
            "The current result is an honest early negative result: the Transformer does not beat the simple opcode-count baseline on the heldout APK cases. That means raw method-opcode sequences alone should not be promoted; the next DL step needs more APKs, richer class/package context, and APK-level aggregation.",
            "",
            "## Limits",
            "",
        ]
    )
    for limit in payload.get("limits", []):
        lines.append(f"- {limit}")
    lines.append("")
    return "\n".join(lines)


def normalize_path(path: str | Path) -> str:
    return Path(path).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
