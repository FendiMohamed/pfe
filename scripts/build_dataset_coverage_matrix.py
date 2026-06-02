from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable


DEFAULT_INVENTORY = Path("data/results/evaluation/apk-testset-inventory.json")
DEFAULT_CANDIDATES = Path("data/results/evaluation/real-apk-candidates.json")
DEFAULT_OUTPUT_DIR = Path("data/results/evaluation")
DEFAULT_DOC_PATH = Path("docs/evaluation/DATASET_COVERAGE_MATRIX.md")


ItemPredicate = Callable[[dict[str, Any]], bool]
CandidatePredicate = Callable[[dict[str, Any]], bool]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate dataset coverage matrix for controlled and real APK criteria.",
    )
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--candidates", default=str(DEFAULT_CANDIDATES))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--doc-path", default=str(DEFAULT_DOC_PATH))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inventory_path = Path(args.inventory)
    candidates_path = Path(args.candidates)
    inventory = read_json(inventory_path)
    candidates = read_json(candidates_path)

    matrix = build_matrix(
        inventory,
        candidates,
        inventory_path=inventory_path,
        candidates_path=candidates_path,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "dataset-coverage-matrix.json"
    json_path.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    doc_path = Path(args.doc_path)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(build_markdown(matrix), encoding="utf-8")

    print(
        json.dumps(
            {
                "criteria": len(matrix["criteria"]),
                "doc": normalize_path(str(doc_path)),
                "json": normalize_path(str(json_path)),
                "missing_or_weak": [
                    item["id"]
                    for item in matrix["criteria"]
                    if item["coverage_status"] in {"missing", "weak"}
                ],
                "next_recommendations": matrix["next_recommendations"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_matrix(
    inventory: dict[str, Any],
    candidates_payload: dict[str, Any],
    *,
    inventory_path: Path,
    candidates_path: Path,
) -> dict[str, Any]:
    controlled = inventory.get("controlled_apks", [])
    real = inventory.get("real_apks", [])
    limitations = inventory.get("limitation_apks", [])
    candidates = candidates_payload.get("candidates", [])
    criteria_rows = [
        evaluate_criterion(definition, controlled, real, limitations, candidates)
        for definition in criterion_definitions()
    ]
    return {
        "schema_version": 1,
        "purpose": (
            "Track controlled and real APK diversity by evaluation criteria, so new APKs "
            "are selected to cover specific research questions instead of being added at random."
        ),
        "source_inventory": normalize_path(str(inventory_path)),
        "source_candidates": normalize_path(str(candidates_path)),
        "summary": {
            "controlled_apks": len(controlled),
            "source_validated_real_apks": len(real),
            "limitation_apks": len(limitations),
            "criteria_total": len(criteria_rows),
            "covered": sum(1 for item in criteria_rows if item["coverage_status"] == "covered"),
            "weak": sum(1 for item in criteria_rows if item["coverage_status"] == "weak"),
            "missing": sum(1 for item in criteria_rows if item["coverage_status"] == "missing"),
            "candidate_only": sum(
                1 for item in criteria_rows if item["coverage_status"] == "candidate-only"
            ),
        },
        "criteria": criteria_rows,
        "next_recommendations": build_next_recommendations(criteria_rows),
    }


def evaluate_criterion(
    definition: dict[str, Any],
    controlled: list[dict[str, Any]],
    real: list[dict[str, Any]],
    limitations: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    controlled_hits = [
        item
        for item in controlled
        if definition["inventory_predicate"](item)
    ]
    real_hits = [item for item in real if definition["inventory_predicate"](item)]
    limitation_hits = [
        item for item in limitations if definition["inventory_predicate"](item)
    ]
    candidate_hits = [
        item
        for item in candidates
        if item.get("proof_status") != "complete"
        and definition["candidate_predicate"](item)
    ]
    coverage_status = classify_coverage(
        definition,
        controlled_hits=controlled_hits,
        real_hits=real_hits,
        limitation_hits=limitation_hits,
        candidate_hits=candidate_hits,
    )
    return {
        "id": definition["id"],
        "criterion": definition["criterion"],
        "research_question": definition["research_question"],
        "target": definition["target"],
        "coverage_status": coverage_status,
        "controlled_count": len(controlled_hits),
        "source_validated_real_count": len(real_hits),
        "limitation_count": len(limitation_hits),
        "candidate_count": len(candidate_hits),
        "covered_by_controlled": [item["id"] for item in controlled_hits],
        "covered_by_real": [item["id"] for item in real_hits],
        "covered_by_limitation": [item["id"] for item in limitation_hits],
        "candidate_apks": [candidate_label(item) for item in candidate_hits],
        "recommended_next_action": recommendation(definition, coverage_status, candidate_hits),
        "notes": definition["notes"],
    }


def classify_coverage(
    definition: dict[str, Any],
    *,
    controlled_hits: list[dict[str, Any]],
    real_hits: list[dict[str, Any]],
    limitation_hits: list[dict[str, Any]],
    candidate_hits: list[dict[str, Any]],
) -> str:
    required = definition["required"]
    controlled_ok = len(controlled_hits) >= required.get("controlled", 0)
    real_ok = len(real_hits) >= required.get("real", 0)
    total_ok = (
        len(controlled_hits) + len(real_hits) + len(limitation_hits)
        >= required.get("total", 0)
    )
    if controlled_ok and real_ok and total_ok:
        return "covered"
    if definition["id"] in {"heavy-obfuscation-limitation", "native-heavy-boundary"} and any(
        item.get("proof_status") == "limitation-complete" for item in candidate_hits
    ):
        return "covered"
    if candidate_hits:
        return "candidate-only"
    if controlled_hits or real_hits or limitation_hits:
        return "weak"
    return "missing"


def build_next_recommendations(criteria_rows: list[dict[str, Any]]) -> list[str]:
    recommendations: list[str] = []
    if row_by_id(criteria_rows, "controlled-multidex")["coverage_status"] != "covered":
        recommendations.append("Add a controlled multidex fixture with exact ground truth.")
    if row_by_id(criteria_rows, "controlled-multi-library")["coverage_status"] != "covered":
        recommendations.append("Add a controlled two-library fixture to test package discovery.")
    if row_by_id(criteria_rows, "heavy-obfuscation-limitation")["coverage_status"] != "covered":
        recommendations.append("Add one limitation fixture/APK with heavy obfuscation or protector indicators.")
    if not recommendations:
        recommendations.append(
            "OsmAnd and Material Files now cover maps/native and file-manager/native-JNI source-validated "
            "stress cases; next, improve guarded source-version/reference coverage or scanner/source-version "
            "triage before adding another category-driven APK batch."
        )
    return recommendations


def row_by_id(rows: list[dict[str, Any]], row_id: str) -> dict[str, Any]:
    return next(row for row in rows if row["id"] == row_id)


def recommendation(
    definition: dict[str, Any],
    coverage_status: str,
    candidate_hits: list[dict[str, Any]],
) -> str:
    if coverage_status == "covered":
        return "Keep current examples; add more only when scaling dataset size."
    if coverage_status == "candidate-only" and candidate_hits:
        first = candidate_label(candidate_hits[0])
        return f"Prioritize proof collection for {first}."
    return definition["fallback_action"]


def criterion_definitions() -> list[dict[str, Any]]:
    return [
        criterion(
            "controlled-clear-baseline",
            "Controlled clear APK baseline",
            "Can the MVP recover exact library/version when names and structure are preserved?",
            {"controlled": 3},
            has_variant("clear"),
            candidate_never,
            "covered by several current controlled fixtures",
            "Add more clear fixtures only for new library families.",
            "Clear fixtures are the precision/recall sanity check.",
        ),
        criterion(
            "r8-rename",
            "R8 rename/minify",
            "Does the matcher avoid failing when names are changed but much code remains?",
            {"controlled": 2},
            has_r8_mode("rename"),
            candidate_has_any("likely R8", "R8/minify"),
            "at least two controlled rename fixtures",
            "Add another R8 rename fixture using a modern AndroidX/Kotlin library.",
            "Current behavior should be low-confidence candidate rather than exact overclaiming.",
        ),
        criterion(
            "r8-shrink",
            "R8 shrink/partial library survival",
            "Does the matcher still emit cautious candidates when shrinking removes code?",
            {"controlled": 2},
            has_r8_mode("shrink"),
            candidate_has_any("likely R8", "R8/minify"),
            "at least two controlled shrink fixtures",
            "Add a controlled shrink fixture with two dependencies.",
            "This is the best controlled proxy for partial-library survival.",
        ),
        criterion(
            "heavy-obfuscation-limitation",
            "Heavy obfuscation/protector limitation",
            "Does the MVP warn or lower confidence instead of overclaiming unsupported APKs?",
            {"total": 1},
            has_heavy_or_protector_signal,
            candidate_has_any("dynamic/tooling boundary", "React Native/native-heavy possibility"),
            "at least one limitation APK/fixture",
            "Add a limitation APK or controlled fixture with heavy obfuscation/protector indicators.",
            "This is limitation evidence, not accuracy evidence.",
        ),
        criterion(
            "single-dex",
            "Single DEX path",
            "Does the extractor and matcher work on simple single-DEX APKs?",
            {"controlled": 3},
            lambda item: int(item.get("dex_count") or 0) == 1,
            candidate_has_any("simple baseline", "single or low-complexity DEX likely", "smaller app"),
            "several controlled APKs",
            "Add a simple real source-validated APK such as Markor or Aegis later.",
            "Already well-covered by controlled fixtures.",
        ),
        criterion(
            "multidex-real",
            "Real multidex APK",
            "Does the MVP parse all classes*.dex files on real apps?",
            {"real": 2},
            lambda item: item.get("dataset_layer") == "source-validated-real"
            and bool(item.get("multidex")),
            candidate_has_any("likely multidex", "multidex likely", "large modern app"),
            "at least two source-validated real APKs",
            "Collect NewPipe/Tusky/K-9 proof bundles and keep DEX count in the inventory.",
            "F-Droid and OpenTracks currently cover this in real APKs.",
        ),
        criterion(
            "controlled-multidex",
            "Controlled multidex APK",
            "Can multidex behavior be measured with exact known ground truth?",
            {"controlled": 1},
            lambda item: item.get("dataset_layer") == "controlled" and bool(item.get("multidex")),
            candidate_never,
            "one controlled multidex fixture",
            "Build a controlled multidex fixture with exact one/two-library ground truth.",
            "This is currently a gap because real multidex is covered, but exact controlled multidex is not.",
        ),
        criterion(
            "native-so-reporting",
            "Native .so hash-only reporting",
            "Does the report show native files without claiming native package versions?",
            {"real": 1},
            lambda item: int(item.get("native_so_count") or 0) > 0,
            candidate_has_any("native-heavy", "native .so boundary", "C++/Java/Kotlin mix"),
            "at least one source-validated or limitation APK with native files",
            "Use Organic Maps/VLC/OsmAnd for stronger native-heavy coverage.",
            "F-Droid covers native hash-only reporting; Organic Maps would stress it.",
        ),
        criterion(
            "no-native-real",
            "Real APK without native files",
            "Can the MVP produce clean Java/Kotlin SBOMs without native noise?",
            {"real": 1},
            lambda item: item.get("dataset_layer") == "source-validated-real"
            and int(item.get("native_so_count") or 0) == 0,
            candidate_has_any("simple/medium app"),
            "one source-validated real APK with 0 native files",
            "Keep OpenTracks as the no-native baseline.",
            "OpenTracks covers this.",
        ),
        criterion(
            "java-only",
            "Java-only or mostly Java",
            "Does the MVP work on classic Java bytecode libraries/apps?",
            {"controlled": 3, "real": 1},
            lambda item: "Java" in str(item.get("language", ""))
            or "Java" in str(item.get("primary_language", "")),
            candidate_has_any("Kotlin/Java", "C++/Java/Kotlin mix"),
            "controlled Java fixtures plus at least one real Java-heavy APK",
            "Add more Java-heavy real apps only after first-batch proof bundles.",
            "Controlled fixtures and OpenTracks cover this.",
        ),
        criterion(
            "kotlin-androidx-real",
            "Kotlin/AndroidX real app",
            "Does the MVP handle modern Kotlin/AndroidX dependency profiles?",
            {"real": 1},
            lambda item: item.get("dataset_layer") == "source-validated-real"
            and contains_any(item, "Kotlin", "AndroidX", "Jetpack"),
            candidate_has_any("modern Kotlin", "AndroidX", "Kotlin/Java", "AndroidX/Kotlin/Java"),
            "one source-validated real APK",
            "Collect Tusky or NewPipe next to strengthen Kotlin/AndroidX coverage.",
            "F-Droid covers this, but more real apps are useful.",
        ),
        criterion(
            "kmp-artifact-family",
            "KMP / Android target artifact family",
            "Does artifact-family disambiguation avoid wrong wrapper/target variants?",
            {"real": 2},
            lambda item: item.get("dataset_layer") == "source-validated-real"
            and contains_any(item, "KMP", "target variants", "Lifecycle", "Okio"),
            candidate_has_any("modern Kotlin", "AndroidX", "networking"),
            "two source-validated real APKs",
            "Keep F-Droid/OpenTracks as the current KMP/artifact-family examples.",
            "This is now covered by Okio and Lifecycle family cases.",
        ),
        criterion(
            "old-dependencies",
            "Older dependency profile",
            "Can the dataset reveal version/vulnerability behavior on older dependencies?",
            {"total": 1},
            lambda item: contains_any(item, "older", "old", "2.9.10.8"),
            candidate_has_any("older history", "older dependencies", "older codebase history"),
            "one controlled or real APK with older dependencies",
            "Keep Markor, Conversations, and K-9/Thunderbird visible as old/older-dependency evidence.",
            "Jackson controlled fixture covers a known old vulnerable dependency.",
        ),
        criterion(
            "modern-release",
            "Modern release profile",
            "Does the dataset include current Android Gradle/R8/AndroidX behavior?",
            {"real": 2},
            lambda item: item.get("release_era") == "modern",
            candidate_has_any("modern", "modern Kotlin", "modern release", "large modern app"),
            "at least two source-validated real APKs",
            "Continue with modern first-batch apps.",
            "F-Droid and OpenTracks currently cover modern releases.",
        ),
        criterion(
            "transitive-complexity",
            "Large transitive dependency tree",
            "Can the MVP stay precise when the source tree has many resolved dependencies?",
            {"real": 1},
            lambda item: str(item.get("transitive_dependency_complexity")) == "high",
            candidate_has_any("large modern app", "networking", "media app"),
            "one high-complexity source-validated real APK",
            "Collect NewPipe/Tusky or Wikipedia Android for more high-complexity coverage.",
            "F-Droid covers high transitive complexity.",
        ),
        criterion(
            "controlled-multi-library",
            "Controlled multi-library APK",
            "Can the matcher separate multiple known libraries in one controlled APK?",
            {"controlled": 1},
            lambda item: item.get("dataset_layer") == "controlled"
            and len(item.get("expected_components", [])) >= 2,
            candidate_never,
            "one controlled fixture with two or more expected components",
            "Build a controlled two-library fixture, for example OkHttp + Gson.",
            "This is a current controlled-dataset gap.",
        ),
        criterion(
            "vulnerability-positive",
            "Known vulnerable dependency",
            "Does OSV produce a positive result with confirmed severity?",
            {"controlled": 1},
            lambda item: int(item.get("osv", {}).get("confirmed_vulnerabilities") or 0) > 0,
            candidate_has_any("email/security", "security/crypto"),
            "one controlled vulnerable APK",
            "Keep Jackson; later add a source-validated vulnerable real app if available.",
            "Jackson Databind currently covers OSV-positive behavior.",
        ),
        criterion(
            "vulnerability-clean",
            "Clean OSV result",
            "Does OSV correctly return no findings for current source-confirmed components?",
            {"real": 2},
            lambda item: item.get("dataset_layer") == "source-validated-real"
            and int(item.get("osv", {}).get("vulnerabilities") or 0) == 0,
            candidate_has_any("modern", "AndroidX", "networking"),
            "two source-validated real APKs with OSV 0",
            "Keep F-Droid/OpenTracks as clean OSV examples.",
            "F-Droid and OpenTracks cover clean OSV behavior.",
        ),
        criterion(
            "native-heavy-boundary",
            "Native-heavy boundary APK",
            "Does the MVP clearly show native hash-only limitations on large native apps?",
            {"total": 1},
            lambda item: int(item.get("native_so_count") or 0) >= 8
            or contains_any(item, "native-heavy"),
            candidate_has_any("native-heavy", "native .so boundary", "C++/Java/Kotlin mix"),
            "one native-heavy real or limitation APK",
            "Prioritize Organic Maps as the native-heavy boundary case.",
            "F-Droid has native files, but not enough to stress the boundary.",
        ),
    ]


def criterion(
    row_id: str,
    criterion_name: str,
    research_question: str,
    required: dict[str, int],
    inventory_predicate: ItemPredicate,
    candidate_predicate: CandidatePredicate,
    target: str,
    fallback_action: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "id": row_id,
        "criterion": criterion_name,
        "research_question": research_question,
        "required": required,
        "inventory_predicate": inventory_predicate,
        "candidate_predicate": candidate_predicate,
        "target": target,
        "fallback_action": fallback_action,
        "notes": notes,
    }


def has_variant(variant: str) -> ItemPredicate:
    return lambda item: item.get("variant") == variant


def has_r8_mode(mode: str) -> ItemPredicate:
    return lambda item: item.get("r8_mode") == mode


def has_heavy_or_protector_signal(item: dict[str, Any]) -> bool:
    return (
        str(item.get("dataset_layer")) == "limitation"
        or str(item.get("obfuscation_level", "")).lower() == "heavy"
        or contains_positive_any(
            item.get("packer_protector_indicators"),
            "protector",
            "packer",
            "encrypted",
        )
        or positive_signal(item.get("dynamic_loading_indicators"))
        or contains_positive_any(item.get("forensic_summary", {}), "protector", "packer", "encrypted")
    )


def positive_signal(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip().lower()
    if not text or text in {"none", "false", "0", "[]", "not applicable", "n/a"}:
        return False
    return not (
        text.startswith("none ")
        or text.startswith("no ")
        or "none confirmed" in text
        or "not detected" in text
        or "not observed" in text
    )


def contains_positive_any(item: Any, *needles: str) -> bool:
    values = [value for value in text_values(item) if positive_signal(value)]
    haystack = " ".join(values).lower()
    return any(needle.lower() in haystack for needle in needles)


def contains_any(item: Any, *needles: str) -> bool:
    haystack = " ".join(text_values(item)).lower()
    return any(needle.lower() in haystack for needle in needles)


def text_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        values: list[str] = []
        for item in value.values():
            values.extend(text_values(item))
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(text_values(item))
        return values
    if value is None:
        return []
    return [str(value)]


def candidate_has_any(*needles: str) -> CandidatePredicate:
    lowered = [needle.lower() for needle in needles]

    def predicate(candidate: dict[str, Any]) -> bool:
        values = " ".join(
            [
                " ".join(candidate.get("criteria", [])),
                str(candidate.get("reason", "")),
                str(candidate.get("target_layer", "")),
                str(candidate.get("validation_level", "")),
            ]
        ).lower()
        return any(needle in values for needle in lowered)

    return predicate


def candidate_never(candidate: dict[str, Any]) -> bool:
    return False


def candidate_label(candidate: dict[str, Any]) -> str:
    return (
        f"{candidate.get('id', 'unknown')} "
        f"({candidate.get('app', 'unknown')}, {candidate.get('proof_status', 'unknown')})"
    )


def build_markdown(matrix: dict[str, Any]) -> str:
    lines = [
        "# Dataset Coverage Matrix",
        "",
        "This file is generated by `scripts/build_dataset_coverage_matrix.py`.",
        "It maps APK choices to the criteria they test, so controlled and real APKs are added for research coverage instead of at random.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
    ]
    for key, value in matrix["summary"].items():
        lines.append(f"| {key.replace('_', ' ')} | {value} |")

    lines.extend(
        [
            "",
            "## Coverage Table",
            "",
            "| Criterion | Status | Controlled | Source-validated real | Limitation | Candidate APKs | Recommended next action |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in matrix["criteria"]:
        candidates = ", ".join(row["candidate_apks"]) or "-"
        lines.append(
            "| "
            f"{row['criterion']} | "
            f"{row['coverage_status']} | "
            f"{row['controlled_count']} | "
            f"{row['source_validated_real_count']} | "
            f"{row['limitation_count']} | "
            f"{candidates} | "
            f"{row['recommended_next_action']} |"
        )

    lines.extend(
        [
            "",
            "## Details",
            "",
        ]
    )
    for row in matrix["criteria"]:
        lines.extend(
            [
                f"### {row['criterion']}",
                "",
                "| Field | Value |",
                "|---|---|",
                f"| Status | {row['coverage_status']} |",
                f"| Research question | {row['research_question']} |",
                f"| Target | {row['target']} |",
                f"| Controlled examples | {', '.join(f'`{item}`' for item in row['covered_by_controlled']) or 'none'} |",
                f"| Source-validated real examples | {', '.join(f'`{item}`' for item in row['covered_by_real']) or 'none'} |",
                f"| Limitation examples | {', '.join(f'`{item}`' for item in row['covered_by_limitation']) or 'none'} |",
                f"| Candidate APKs | {', '.join(row['candidate_apks']) or 'none'} |",
                f"| Next action | {row['recommended_next_action']} |",
                f"| Notes | {row['notes']} |",
                "",
            ]
        )

    lines.extend(
        [
            "## Next Recommendations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in matrix["next_recommendations"])
    lines.extend(
        [
            "",
            "## Regeneration Command",
            "",
            "```powershell",
            "python scripts/build_dataset_coverage_matrix.py",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
