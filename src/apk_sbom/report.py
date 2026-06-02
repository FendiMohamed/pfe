from __future__ import annotations

import json
from html import escape
from dataclasses import asdict, dataclass
from pathlib import Path

from apk_sbom.apk_extractor import ApkInspection, inspect_apk
from apk_sbom.dex_analyzer import ApkDexAnalysis, analyze_apk_dex
from apk_sbom.matcher import (
    DEFAULT_API_REFERENCE_WEIGHT,
    DEFAULT_OPCODE_NGRAM_WEIGHT,
    MatchSummary,
    detected_libraries_from_match_summary,
    match_apk_to_reference_db,
)
from apk_sbom.models import ComponentEvidence, DetectedLibrary
from apk_sbom.obfuscation import R8ObfuscationDiagnostics, build_obfuscation_diagnostics
from apk_sbom.reference_features import DEFAULT_FEATURE_DB_PATH
from apk_sbom.sbom import build_cyclonedx_bom
from apk_sbom.vulnerability import (
    DEFAULT_OSV_BATCH_URL,
    OsvScanSummary,
    apply_source_validation_to_osv_summary,
    query_osv_for_libraries,
)


DEFAULT_REPORT_DIR = Path("data/results/report")
DEFAULT_R8_PHASE5_EXPERIMENT_JSON = Path(
    "data/results/experiments/r8-phase5-scoped-trigger-diagnostics.json"
)
DEFAULT_VERSION_BAND_EXPERIMENT_JSON = Path(
    "data/results/experiments/low-risk-version-band-trigger-diagnostics.json"
)
DEFAULT_LIFECYCLE_FAMILY_EXPERIMENT_JSON = Path(
    "data/results/experiments/lifecycle-family-separation-diagnostics.json"
)


@dataclass(frozen=True)
class ReportArtifacts:
    output_dir: str
    matches_json: str
    sbom_json: str
    vulnerabilities_json: str | None
    report_json: str
    report_markdown: str
    report_html: str

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class ObfuscationRisk:
    level: str
    score: float
    reasons: list[str]


def generate_final_report(
    apk_path: str | Path,
    *,
    output_dir: str | Path = DEFAULT_REPORT_DIR,
    db_path: str | Path = DEFAULT_FEATURE_DB_PATH,
    coordinate: str | None = None,
    top: int = 10,
    min_score: float = 0.05,
    include_uncertain: bool = False,
    query_osv: bool = True,
    osv_api_url: str = DEFAULT_OSV_BATCH_URL,
    timeout: int = 30,
    enrich_vulnerabilities: bool = True,
    source_validation_json: str | Path | None = None,
    api_reference_weight: float = DEFAULT_API_REFERENCE_WEIGHT,
    opcode_ngram_weight: float = DEFAULT_OPCODE_NGRAM_WEIGHT,
    r8_phase5_experiment_json: str | Path | None = None,
    version_band_experiment_json: str | Path | None = None,
    lifecycle_family_experiment_json: str | Path | None = None,
) -> ReportArtifacts:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    apk = inspect_apk(apk_path)
    match_summary = match_apk_to_reference_db(
        apk_path,
        db_path=db_path,
        coordinate=coordinate,
        top=top,
        min_score=min_score,
        api_reference_weight=api_reference_weight,
        opcode_ngram_weight=opcode_ngram_weight,
    )
    components = detected_libraries_from_match_summary(
        match_summary,
        include_uncertain=include_uncertain,
    )
    obfuscation_diagnostics = build_obfuscation_diagnostics(
        apk,
        dex_analysis=_safe_dex_analysis_for_diagnostics(apk_path),
        match_summary=match_summary,
        components=components,
    )
    r8_phase5_experiment = load_r8_phase5_experiment_evidence(
        r8_phase5_experiment_json,
        apk_path=apk.apk_path,
        report_path=output / "report.json",
    )
    version_band_experiments = load_version_band_experiment_evidence(
        version_band_experiment_json,
        lifecycle_family_experiment_json,
        apk_path=apk.apk_path,
    )

    matches_path = output / "matches.json"
    matches_path.write_text(match_summary.to_json() + "\n", encoding="utf-8")

    sbom_path = output / "sbom.cdx.json"
    build_cyclonedx_bom(
        apk,
        components,
        metadata_properties=_version_band_sbom_properties(version_band_experiments),
    ).write_json(sbom_path)

    osv_summary: OsvScanSummary | None = None
    vulnerabilities_path: Path | None = None
    if query_osv:
        osv_summary = query_osv_for_libraries(
            components,
            api_url=osv_api_url,
            timeout=timeout,
            enrich_vulnerabilities=enrich_vulnerabilities,
        )
        if source_validation_json:
            osv_summary = apply_source_validation_to_osv_summary(
                osv_summary,
                source_validation_json,
            )
        vulnerabilities_path = output / "osv-vulnerabilities.json"
        osv_summary.write_json(vulnerabilities_path)

    report_json_path = output / "report.json"
    artifact_paths = ReportArtifacts(
        output_dir=str(output),
        matches_json=str(matches_path),
        sbom_json=str(sbom_path),
        vulnerabilities_json=str(vulnerabilities_path) if vulnerabilities_path else None,
        report_json=str(report_json_path),
        report_markdown=str(output / "report.md"),
        report_html=str(output / "report.html"),
    )
    report_payload = build_json_report(
        apk,
        match_summary,
        components,
        osv_summary,
        artifact_paths,
        obfuscation_diagnostics=obfuscation_diagnostics,
        r8_phase5_experiment=r8_phase5_experiment,
        version_band_experiments=version_band_experiments,
    )
    report_json_path.write_text(
        json.dumps(report_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    report_markdown_path = output / "report.md"
    report_markdown_path.write_text(
        build_markdown_report(
            apk,
            match_summary,
            components,
            osv_summary,
            artifact_paths,
            obfuscation_diagnostics=obfuscation_diagnostics,
            r8_phase5_experiment=r8_phase5_experiment,
            version_band_experiments=version_band_experiments,
        ),
        encoding="utf-8",
    )

    report_html_path = output / "report.html"
    report_html_path.write_text(
        build_html_report(
            apk,
            match_summary,
            components,
            osv_summary,
            artifact_paths,
            obfuscation_diagnostics=obfuscation_diagnostics,
            r8_phase5_experiment=r8_phase5_experiment,
            version_band_experiments=version_band_experiments,
        ),
        encoding="utf-8",
    )

    return artifact_paths


def _safe_dex_analysis_for_diagnostics(apk_path: str | Path) -> ApkDexAnalysis | None:
    try:
        return analyze_apk_dex(apk_path, include_members=True)
    except Exception:
        return None


def load_r8_phase5_experiment_evidence(
    path: str | Path | None,
    *,
    apk_path: str | Path,
    report_path: str | Path,
) -> dict | None:
    if path is None:
        return None
    source_path = Path(path)
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    triggered_rows = payload.get("triggered_rows", [])
    matching_rows = [
        row for row in rows if _r8_phase5_row_matches_report(row, apk_path, report_path)
    ]
    matching_triggered_rows = [
        row for row in matching_rows if row.get("trigger_decision", {}).get("apply")
    ]
    summary = payload.get("summary", {})
    return {
        "report_only": True,
        "source": str(source_path),
        "verdict": payload.get("verdict"),
        "policy": [
            "This section is opt-in report-only Phase 5 evidence.",
            "It does not change detected components, selected versions, SBOM output, vulnerability labels, or source-validation metrics.",
            "Use it to track whether the research-backed R8 trigger remains clean as the dataset grows.",
        ],
        "summary": {
            "rows_evaluated": summary.get("rows_evaluated", 0),
            "triggered_rows": summary.get("triggered_rows", 0),
            "target_improvements_kept": summary.get("target_improvements_kept", 0),
            "triggered_regressions": summary.get("triggered_regressions", 0),
            "triggered_conflicts": summary.get("triggered_conflicts", 0),
            "matching_rows": len(matching_rows),
            "matching_triggered_rows": len(matching_triggered_rows),
        },
        "matching_rows": matching_rows,
        "matching_triggered_rows": matching_triggered_rows,
        "triggered_rows_sample": triggered_rows[:5],
    }


def _r8_phase5_row_matches_report(
    row: dict,
    apk_path: str | Path,
    report_path: str | Path,
) -> bool:
    apk_text = _normalized_path(apk_path)
    report_text = _normalized_path(report_path)
    row_apk = _normalized_path(row.get("apk_path"))
    row_report = _normalized_path(row.get("report_path"))
    if row_apk and (row_apk == apk_text or Path(row_apk).name == Path(apk_text).name):
        return True
    if row_report and row_report == report_text:
        return True
    case = str(row.get("case") or "")
    return bool(case and case in Path(apk_text).stem)


def load_version_band_experiment_evidence(
    version_band_path: str | Path | None,
    lifecycle_family_path: str | Path | None,
    *,
    apk_path: str | Path,
) -> dict | None:
    old_version = _load_single_version_band_evidence(
        version_band_path,
        apk_path=apk_path,
        rows_key="introduced_mismatch_rows",
        match_row_key="matching_downgrade_rows",
        apply_path=("trigger_decision", "apply"),
        summary_keys=("introduced_mismatch_rows", "introduced_mismatches_flagged", "resolved_target_rows_blocked"),
    )
    lifecycle = _load_single_version_band_evidence(
        lifecycle_family_path,
        apk_path=apk_path,
        rows_key="introduced_rows",
        match_row_key="matching_downgrade_rows",
        apply_path=("lifecycle_decision", "downgrade_public_claim"),
        summary_keys=("introduced_lifecycle_rows", "public_claim_downgrade_candidates", "resolved_target_rows_blocked"),
    )
    if old_version is None and lifecycle is None:
        return None
    return {
        "report_only": True,
        "policy": [
            "This section is opt-in report-only version-band evidence.",
            "It does not change detected components, selected versions, SBOM component selection, vulnerability labels, or source-validation metrics.",
            "Rows suggest confidence downgrades or ambiguity annotations only; they do not prove replacement versions.",
        ],
        "old_version_steal": old_version,
        "lifecycle_family": lifecycle,
    }


def _load_single_version_band_evidence(
    path: str | Path | None,
    *,
    apk_path: str | Path,
    rows_key: str,
    match_row_key: str,
    apply_path: tuple[str, str],
    summary_keys: tuple[str, ...],
) -> dict | None:
    if path is None:
        return None
    source_path = Path(path)
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    rows = payload.get(rows_key, [])
    matching_rows = [row for row in rows if _experiment_case_matches_apk(row, apk_path)]
    matching_downgrade_rows = [
        row for row in matching_rows if bool(row.get(apply_path[0], {}).get(apply_path[1]))
    ]
    source_summary = payload.get("summary", {})
    summary = {key: source_summary.get(key, 0) for key in summary_keys}
    summary["matching_rows"] = len(matching_rows)
    summary["matching_downgrade_rows"] = len(matching_downgrade_rows)
    return {
        "source": str(source_path),
        "verdict": payload.get("verdict"),
        "summary": summary,
        "matching_rows": matching_rows,
        match_row_key: matching_downgrade_rows,
    }


def _experiment_case_matches_apk(row: dict, apk_path: str | Path) -> bool:
    case = str(row.get("case_id") or row.get("case") or "")
    if not case:
        return False
    case_key = _match_key(case)
    apk_key = _match_key(Path(str(apk_path)).stem)
    return bool(case_key and (case_key in apk_key or apk_key in case_key))


def _match_key(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def _version_band_sbom_properties(experiments: dict | None) -> list[dict[str, str]]:
    if experiments is None:
        return []
    summary = {
        key: value.get("summary", {})
        for key, value in experiments.items()
        if isinstance(value, dict)
    }
    return [
        {
            "name": "apk-sbom:mvp:version-band-experiments-report-only",
            "value": "true",
        },
        {
            "name": "apk-sbom:mvp:version-band-experiment-summary",
            "value": json.dumps(summary, sort_keys=True),
        },
    ]


def _normalized_path(value: object) -> str:
    if not value:
        return ""
    return str(value).replace("\\", "/")


def build_json_report(
    apk: ApkInspection,
    match_summary: MatchSummary,
    components: list[DetectedLibrary],
    osv_summary: OsvScanSummary | None,
    artifacts: ReportArtifacts,
    obfuscation_diagnostics: R8ObfuscationDiagnostics | None = None,
    r8_phase5_experiment: dict | None = None,
    version_band_experiments: dict | None = None,
) -> dict:
    diagnostics = obfuscation_diagnostics or build_obfuscation_diagnostics(
        apk,
        match_summary=match_summary,
        components=components,
    )
    payload = {
        "apk": apk.to_dict(),
        "match_summary": match_summary.to_dict(),
        "obfuscation_risk": asdict(assess_obfuscation_risk(apk, match_summary, components)),
        "obfuscation_diagnostics": diagnostics.to_dict(),
        "detected_components": [asdict(component) for component in components],
        "osv": osv_summary.to_dict() if osv_summary else None,
        "artifacts": artifacts.to_dict(),
    }
    if r8_phase5_experiment is not None:
        payload["r8_phase5_experiment"] = r8_phase5_experiment
    if version_band_experiments is not None:
        payload["version_band_experiments"] = version_band_experiments
    return payload


def build_markdown_report(
    apk: ApkInspection,
    match_summary: MatchSummary,
    components: list[DetectedLibrary],
    osv_summary: OsvScanSummary | None,
    artifacts: ReportArtifacts,
    obfuscation_diagnostics: R8ObfuscationDiagnostics | None = None,
    r8_phase5_experiment: dict | None = None,
    version_band_experiments: dict | None = None,
) -> str:
    vulnerability_labels = _vulnerability_labels(osv_summary)
    obfuscation_risk = assess_obfuscation_risk(apk, match_summary, components)
    diagnostics = obfuscation_diagnostics or build_obfuscation_diagnostics(
        apk,
        match_summary=match_summary,
        components=components,
    )
    lines = [
        "# APK SBOM Recovery Report",
        "",
        "## APK",
        "",
        f"- Path: `{apk.apk_path}`",
        f"- SHA-256: `{apk.apk_sha256}`",
        f"- Package name: `{apk.manifest_metadata.package_name or 'unknown'}`",
        f"- Version: `{apk.manifest_metadata.version_name or 'unknown'}`"
        f" / code `{apk.manifest_metadata.version_code or 'unknown'}`",
        f"- SDK range: min `{apk.manifest_metadata.min_sdk or 'unknown'}`"
        f" / target `{apk.manifest_metadata.target_sdk or 'unknown'}`",
        f"- Manifest parse status: {apk.manifest_metadata.parse_status}",
        f"- DEX files: {len(apk.dex_files)}",
        f"- Multidex: {str(apk.has_multidex).lower()}",
        f"- Native libraries: {len(apk.native_libraries)}",
        f"- Extraction risk: {apk.forensic_summary.extraction_risk}",
        f"- Obfuscation risk: {obfuscation_risk.level} ({obfuscation_risk.score:.2f})",
        "",
        "## Detection Summary",
        "",
        f"- DEX files analyzed: {match_summary.dex_files_analyzed}",
        f"- DEX files failed: {match_summary.dex_files_failed}",
        f"- Detected Maven components: {len(components)}",
        f"- Native file components: {len(apk.native_libraries)}",
        f"- Vulnerability findings: {_vulnerability_summary(osv_summary)}",
        "",
    ]
    lines.extend(_markdown_inert_multiscale_features(match_summary))
    lines.extend(
        [
        "",
        "## APK Forensic Summary",
        "",
        f"- ZIP entries: {apk.forensic_summary.zip_entries}",
        f"- Standard DEX files: {_markdown_list(apk.forensic_summary.standard_dex_files)}",
        f"- Nonstandard DEX files: {_markdown_list(apk.forensic_summary.nonstandard_dex_files)}",
        f"- Native ABIs: {_markdown_list(apk.forensic_summary.native_abis)}",
        f"- Permissions: {_markdown_list(apk.manifest_metadata.permissions)}",
        "",
        ]
    )
    if apk.forensic_summary.indicators:
        lines.extend(
            [
                "| Severity | Code | Detail |",
                "|---|---|---|",
            ]
        )
        for indicator in apk.forensic_summary.indicators:
            lines.append(
                f"| {indicator.severity} | `{indicator.code}` | {indicator.detail} |"
            )
    else:
        lines.append("No extraction indicators were raised.")

    lines.extend(
        [
            "",
            "## Obfuscation Risk",
            "",
            f"- Level: {obfuscation_risk.level}",
            f"- Score: {obfuscation_risk.score:.2f}",
        ]
    )
    for reason in obfuscation_risk.reasons:
        lines.append(f"- Reason: {reason}")

    lines.extend(_markdown_obfuscation_diagnostics(diagnostics))
    lines.extend(_markdown_r8_phase5_experiment(r8_phase5_experiment))
    lines.extend(_markdown_version_band_experiments(version_band_experiments))

    lines.extend(
        [
            "",
        "## Detected Components",
        "",
        ]
    )

    if components:
        lines.extend(
            [
                "| Component | Version | Candidate reasons | Identity confidence | Version confidence | Ambiguous versions | Match type | Vulnerabilities |",
                "|---|---:|---|---|---|---|---|---|",
            ]
        )
        for component in components:
            lines.append(
                "| "
                f"`{component.coordinate}` | "
                f"{component.version} | "
                f"{candidate_reason_summary(component.evidence)} | "
                f"{_confidence_summary(component.identity_status, component.identity_confidence_label, component.identity_confidence)} | "
                f"{_confidence_summary(component.version_status, component.version_confidence_label, component.version_confidence)} | "
                f"{_version_set_summary(component.ambiguous_versions)} | "
                f"{component.match_type} | "
                f"{vulnerability_labels.get(component.purl, '0')} |"
            )
    else:
        lines.append("No components passed the current confidence and uncertainty filters.")

    lines.extend(
        [
            "",
            "## Native Libraries",
            "",
        ]
    )
    if apk.native_libraries:
        lines.extend(
            [
                "| Path | ABI | Size | SHA-256 |",
                "|---|---|---:|---|",
            ]
        )
        for library in apk.native_libraries:
            lines.append(
                "| "
                f"`{library.path}` | "
                f"{library.abi} | "
                f"{library.size} | "
                f"`{library.sha256}` |"
            )
    else:
        lines.append("No native `.so` files were found in the APK.")

    lines.extend(
        [
            "",
            "## Version Decisions",
            "",
        ]
    )

    if match_summary.decisions:
        lines.extend(
            [
                "| Component | Selected version | Identity | Version | Score | Gap | Alternatives | Notes |",
                "|---|---:|---|---|---:|---:|---|---|",
            ]
        )
        for decision in match_summary.decisions:
            alternatives = ", ".join(
                f"{alternative.version} ({alternative.score:.3f})"
                for alternative in decision.alternatives
            )
            if not alternatives:
                alternatives = "none"
            notes = decision.version_ambiguity_reason or decision.version_selection_reason or ""
            lines.append(
                "| "
                f"`{decision.coordinate}` | "
                f"{decision.selected_version} | "
                f"{_confidence_summary(decision.identity_status, decision.identity_confidence_label, decision.identity_confidence)} | "
                f"{_confidence_summary(decision.version_status, decision.version_confidence_label, decision.version_confidence)} | "
                f"{decision.score:.3f} | "
                f"{decision.gap_to_next:.3f} | "
                f"{alternatives} | "
                f"{notes} |"
            )
    else:
        lines.append("No version decisions were produced.")

    lines.extend(
        [
            "",
            "## Vulnerabilities",
            "",
        ]
    )
    if osv_summary and osv_summary.results:
        vulnerability_rows = [
            (result, vulnerability)
            for result in osv_summary.results
            for vulnerability in result.vulnerabilities
        ]
        if vulnerability_rows:
            lines.extend(
                [
                    "| Component | Version | Finding confidence | Source validation | Severity | Advisory | Aliases | Summary |",
                    "|---|---:|---|---|---|---|---|---|",
                ]
            )
            for result, vulnerability in vulnerability_rows:
                aliases = ", ".join(vulnerability.aliases or [])
                if not aliases:
                    aliases = "none"
                summary = vulnerability.summary or "not provided"
                lines.append(
                    "| "
                    f"`{result.coordinate}` | "
                    f"{result.version} | "
                    f"{result.finding_confidence} | "
                    f"{_source_validation_summary(result)} | "
                    f"{_vulnerability_severity(vulnerability)} | "
                    f"`{vulnerability.id}` | "
                    f"{aliases} | "
                    f"{summary} |"
                )
        else:
            lines.append("No vulnerabilities were returned by the configured source.")
    else:
        lines.append("Vulnerability lookup was not run for this report.")

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Match details: `{artifacts.matches_json}`",
            f"- CycloneDX SBOM: `{artifacts.sbom_json}`",
            f"- JSON report: `{artifacts.report_json}`",
            f"- Markdown report: `{artifacts.report_markdown}`",
            f"- HTML report: `{artifacts.report_html}`",
        ]
    )
    if artifacts.vulnerabilities_json:
        lines.append(f"- OSV results: `{artifacts.vulnerabilities_json}`")
    else:
        lines.append("- OSV results: not generated in this run")

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- This MVP only detects libraries present in the local Maven reference DB.",
            "- Heavy R8 optimization, reflection, packed APKs, encrypted DEX, and dynamic loading remain limited or unsupported.",
            "- Native `.so` files are hashed, but native component version identification is not implemented in the first MVP.",
            "",
        ]
    )
    return "\n".join(lines)


def build_html_report(
    apk: ApkInspection,
    match_summary: MatchSummary,
    components: list[DetectedLibrary],
    osv_summary: OsvScanSummary | None,
    artifacts: ReportArtifacts,
    obfuscation_diagnostics: R8ObfuscationDiagnostics | None = None,
    r8_phase5_experiment: dict | None = None,
    version_band_experiments: dict | None = None,
) -> str:
    vulnerability_labels = _vulnerability_labels(osv_summary)
    vulnerability_rows = _vulnerability_rows(osv_summary)
    obfuscation_risk = assess_obfuscation_risk(apk, match_summary, components)
    diagnostics = obfuscation_diagnostics or build_obfuscation_diagnostics(
        apk,
        match_summary=match_summary,
        components=components,
    )
    component_rows = _html_component_rows(components, vulnerability_labels)
    forensic_rows = _html_forensic_rows(apk, obfuscation_risk)
    native_rows = _html_native_rows(apk)
    decision_rows = _html_decision_rows(match_summary)
    vulnerability_table_rows = _html_vulnerability_rows(vulnerability_rows)

    lookup_state = "Not run"
    if osv_summary:
        lookup_state = _vulnerability_summary(osv_summary)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>APK SBOM Recovery Report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #1f2933;
      --muted: #5f6b7a;
      --line: #d9dee7;
      --accent: #2563eb;
      --ok: #0f766e;
      --warn: #b45309;
      --bad: #b91c1c;
      --soft: #eef2f7;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.5 Arial, Helvetica, sans-serif;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding: 18px 0 20px;
      margin-bottom: 18px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    section {{
      margin: 18px 0;
      padding: 18px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
    }}
    code {{
      font-family: Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 12px;
      word-break: break-all;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 8px;
      text-align: left;
      vertical-align: top;
      word-break: break-word;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    .subtle {{ color: var(--muted); }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 10px;
    }}
    .metric {{
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--soft);
    }}
    .metric strong {{
      display: block;
      margin-top: 4px;
      font-size: 22px;
    }}
    .pill {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
      border: 1px solid var(--line);
      background: #fff;
    }}
    .pill.ok {{ color: var(--ok); border-color: #99d3c7; background: #ecfdf5; }}
    .pill.warn {{ color: var(--warn); border-color: #f3c27b; background: #fffbeb; }}
    .pill.bad {{ color: var(--bad); border-color: #f3a4a4; background: #fef2f2; }}
    .bar {{
      height: 8px;
      margin-top: 5px;
      border-radius: 999px;
      background: #e5e7eb;
      overflow: hidden;
    }}
    .bar span {{
      display: block;
      height: 100%;
      background: var(--accent);
    }}
    details {{
      margin-top: 6px;
    }}
    summary {{
      cursor: pointer;
      color: var(--accent);
    }}
    ul {{
      margin: 8px 0 0 18px;
      padding: 0;
    }}
    .artifacts li, .limitations li {{
      margin: 5px 0;
    }}
    @media (max-width: 720px) {{
      main {{ padding: 14px; }}
      h1 {{ font-size: 22px; }}
      table {{ table-layout: auto; }}
      th, td {{ padding: 8px 6px; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>APK SBOM Recovery Report</h1>
    <div class="subtle"><code>{_html(apk.apk_path)}</code></div>
  </header>

  <section>
    <h2>Summary</h2>
    <div class="grid">
      <div class="metric"><span class="subtle">Maven components</span><strong>{len(components)}</strong></div>
      <div class="metric"><span class="subtle">Native files</span><strong>{len(apk.native_libraries)}</strong></div>
      <div class="metric"><span class="subtle">DEX files analyzed</span><strong>{match_summary.dex_files_analyzed}</strong></div>
      <div class="metric"><span class="subtle">DEX parse failures</span><strong>{match_summary.dex_files_failed}</strong></div>
      <div class="metric"><span class="subtle">Extraction risk</span><strong>{_html(apk.forensic_summary.extraction_risk)}</strong></div>
      <div class="metric"><span class="subtle">Obfuscation risk</span><strong>{_html(obfuscation_risk.level)}</strong></div>
      <div class="metric"><span class="subtle">Vulnerability lookup</span><strong>{_html(lookup_state)}</strong></div>
    </div>
  </section>

  <section>
    <h2>APK</h2>
    <table>
      <tbody>
        <tr><th>SHA-256</th><td><code>{_html(apk.apk_sha256)}</code></td></tr>
        <tr><th>Package</th><td><code>{_html(apk.manifest_metadata.package_name or "unknown")}</code></td></tr>
        <tr><th>Version</th><td>{_html(apk.manifest_metadata.version_name or "unknown")} / code {_html(apk.manifest_metadata.version_code or "unknown")}</td></tr>
        <tr><th>SDK</th><td>min {_html(apk.manifest_metadata.min_sdk or "unknown")} / target {_html(apk.manifest_metadata.target_sdk or "unknown")}</td></tr>
        <tr><th>Manifest Parse</th><td>{_html(apk.manifest_metadata.parse_status)}</td></tr>
        <tr><th>Size</th><td>{apk.apk_size} bytes</td></tr>
        <tr><th>Multidex</th><td>{str(apk.has_multidex).lower()}</td></tr>
        <tr><th>Manifest</th><td>{str(apk.manifest_present).lower()}</td></tr>
        <tr><th>Resources</th><td>{str(apk.resources_arsc_present).lower()}</td></tr>
      </tbody>
    </table>
  </section>

  <section>
    <h2>APK Forensics</h2>
    {forensic_rows}
  </section>

  <section>
    <h2>R8 / Obfuscation Diagnostics</h2>
    {_html_obfuscation_diagnostics(diagnostics)}
  </section>

  <section>
    <h2>Inert Multi-Scale Feature Availability</h2>
    {_html_inert_multiscale_features(match_summary)}
  </section>

  <section>
    <h2>Experimental R8 Phase 5 Evidence</h2>
    {_html_r8_phase5_experiment(r8_phase5_experiment)}
  </section>

  <section>
    <h2>Experimental Version-Band Evidence</h2>
    {_html_version_band_experiments(version_band_experiments)}
  </section>

  <section>
    <h2>Detected Components</h2>
    {component_rows}
  </section>

  <section>
    <h2>Version Decisions</h2>
    {decision_rows}
  </section>

  <section>
    <h2>Vulnerabilities</h2>
    {vulnerability_table_rows}
  </section>

  <section>
    <h2>Native Libraries</h2>
    {native_rows}
  </section>

  <section>
    <h2>Artifacts</h2>
    <ul class="artifacts">
      <li>Match details: <code>{_html(artifacts.matches_json)}</code></li>
      <li>CycloneDX SBOM: <code>{_html(artifacts.sbom_json)}</code></li>
      <li>JSON report: <code>{_html(artifacts.report_json)}</code></li>
      <li>Markdown report: <code>{_html(artifacts.report_markdown)}</code></li>
      <li>HTML report: <code>{_html(artifacts.report_html)}</code></li>
      <li>OSV results: <code>{_html(artifacts.vulnerabilities_json or "not generated in this run")}</code></li>
    </ul>
  </section>

  <section>
    <h2>Limitations</h2>
    <ul class="limitations">
      <li>This MVP only detects libraries present in the local Maven reference DB.</li>
      <li>Heavy R8 optimization, reflection, packed APKs, encrypted DEX, and dynamic loading remain limited or unsupported.</li>
      <li>Native `.so` files are hashed, but native component version identification is not implemented in the first MVP.</li>
    </ul>
  </section>
</main>
</body>
</html>
"""


def _vulnerability_counts(osv_summary: OsvScanSummary | None) -> dict[str, int]:
    if not osv_summary:
        return {}
    return {
        result.purl: len(result.vulnerabilities)
        for result in osv_summary.results
    }


def _vulnerability_labels(osv_summary: OsvScanSummary | None) -> dict[str, str]:
    if not osv_summary:
        return {}
    labels: dict[str, str] = {}
    for result in osv_summary.results:
        count = len(result.vulnerabilities)
        if count == 0:
            labels[result.purl] = "0"
            continue
        labels[result.purl] = f"{count} {result.finding_confidence}"
        if result.source_validation_finding:
            labels[result.purl] += f" ({result.source_validation_finding})"
    return labels


def _vulnerability_summary(osv_summary: OsvScanSummary | None) -> str:
    if not osv_summary:
        return "not run"
    if osv_summary.vulnerabilities == 0:
        return "0"
    return (
        f"{osv_summary.vulnerabilities} "
        f"({osv_summary.confirmed_vulnerabilities} confirmed, "
        f"{osv_summary.potential_vulnerabilities} potential)"
    )


def _vulnerability_rows(osv_summary: OsvScanSummary | None) -> list[tuple]:
    if not osv_summary:
        return []
    return [
        (result, vulnerability)
        for result in osv_summary.results
        for vulnerability in result.vulnerabilities
    ]


def assess_obfuscation_risk(
    apk: ApkInspection,
    match_summary: MatchSummary,
    components: list[DetectedLibrary],
) -> ObfuscationRisk:
    score = 0.0
    reasons: list[str] = []

    if apk.forensic_summary.nonstandard_dex_files:
        score += 0.30
        reasons.append("DEX-like files appear outside the normal top-level classes*.dex layout.")
    if apk.forensic_summary.extraction_risk == "medium":
        score += 0.15
        reasons.append("APK extraction indicators suggest a medium forensic risk.")
    elif apk.forensic_summary.extraction_risk == "high":
        score += 0.30
        reasons.append("APK extraction indicators suggest a high forensic risk.")
    if match_summary.dex_files_failed:
        score += 0.25
        reasons.append(f"{match_summary.dex_files_failed} DEX file(s) failed parsing.")
    candidate_components = [
        component
        for component in components
        if str(component.version_status).lower() in {"candidate", "uncertain"}
        or str(component.version_confidence_label).lower() in {"low", "uncertain"}
    ]
    if components and len(candidate_components) / len(components) >= 0.50:
        score += 0.20
        reasons.append("At least half of emitted components are low-confidence version candidates.")

    decisions = match_summary.decisions
    if decisions:
        average_package_score = sum(
            decision.evidence.package_score for decision in decisions
        ) / len(decisions)
        strongest_structural_score = max(
            max(
                decision.evidence.opcode_score,
                decision.evidence.dependency_score,
                decision.evidence.literal_score,
            )
            for decision in decisions
        )
        if average_package_score < 0.20 and strongest_structural_score >= 0.50:
            score += 0.20
            reasons.append("Structural evidence is stronger than package-name evidence.")

    score = min(score, 1.0)
    if score >= 0.60:
        level = "high"
    elif score >= 0.25:
        level = "medium"
    else:
        level = "low"
    if not reasons:
        reasons.append("No obvious obfuscation indicators were raised by the current heuristics.")
    return ObfuscationRisk(level=level, score=round(score, 3), reasons=reasons)


def _markdown_obfuscation_diagnostics(
    diagnostics: R8ObfuscationDiagnostics,
) -> list[str]:
    payload = diagnostics.to_dict()
    lines = [
        "",
        "## R8 / Obfuscation Diagnostics",
        "",
        f"- Report-only: {str(payload['report_only']).lower()}",
        "",
        "| Field | Status | Value | Key metrics |",
        "|---|---|---:|---|",
    ]
    for field_name, signal in _diagnostic_signals(payload):
        lines.append(
            "| "
            f"`{field_name}` | "
            f"{signal.get('status', 'unknown')} | "
            f"{_markdown_value(signal.get('value'))} | "
            f"{_metrics_summary(signal.get('metrics', {}))} |"
        )
    if payload.get("component_diagnostics"):
        lines.extend(
            [
                "",
                "| Component | Version | Class coverage | Method coverage | Structural average | Inlining/merging hints |",
                "|---|---:|---:|---:|---:|---|",
            ]
        )
        for row in payload["component_diagnostics"]:
            hints = []
            if row.get("method_collapse_indicator"):
                hints.append("method-collapse")
            if row.get("class_merging_indicator"):
                hints.append("class-merging")
            lines.append(
                "| "
                f"`{row.get('coordinate', '')}` | "
                f"{row.get('selected_version', '')} | "
                f"{_markdown_value(row.get('class_coverage'))} | "
                f"{_markdown_value(row.get('method_coverage'))} | "
                f"{_markdown_value(row.get('structural_average'))} | "
                f"{', '.join(hints) if hints else 'none'} |"
            )
    for note in payload.get("notes", []):
        lines.append(f"- Note: {note}")
    return lines


def _html_obfuscation_diagnostics(diagnostics: R8ObfuscationDiagnostics) -> str:
    payload = diagnostics.to_dict()
    rows = []
    for field_name, signal in _diagnostic_signals(payload):
        rows.append(
            "<tr>"
            f"<td><code>{_html(field_name)}</code></td>"
            f"<td>{_status_pill(str(signal.get('status', 'unknown')))}</td>"
            f"<td>{_html(_markdown_value(signal.get('value')))}</td>"
            f"<td>{_html(_metrics_summary(signal.get('metrics', {})))}</td>"
            f"<td>{_html(signal.get('explanation', ''))}</td>"
            "</tr>"
        )
    notes = "".join(f"<li>{_html(note)}</li>" for note in payload.get("notes", []))
    component_rows = "".join(
        "<tr>"
        f"<td><code>{_html(row.get('coordinate', ''))}</code></td>"
        f"<td>{_html(row.get('selected_version', ''))}</td>"
        f"<td>{_html(_markdown_value(row.get('class_coverage')))}</td>"
        f"<td>{_html(_markdown_value(row.get('method_coverage')))}</td>"
        f"<td>{_html(_markdown_value(row.get('structural_average')))}</td>"
        f"<td>{_html(_component_hint_summary(row))}</td>"
        "</tr>"
        for row in payload.get("component_diagnostics", [])
    )
    component_table = ""
    if component_rows:
        component_table = (
            "<h3>Component Diagnostics</h3>"
            "<table><thead><tr><th>Component</th><th>Version</th><th>Class coverage</th>"
            "<th>Method coverage</th><th>Structural average</th><th>Hints</th></tr></thead><tbody>"
            + component_rows
            + "</tbody></table>"
        )
    return (
        f"<p>Report-only: <strong>{str(payload['report_only']).lower()}</strong></p>"
        "<table><thead><tr><th>Field</th><th>Status</th><th>Value</th><th>Metrics</th><th>Meaning</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
        + component_table
        + f"<ul>{notes}</ul>"
    )


def _markdown_inert_multiscale_features(match_summary: MatchSummary) -> list[str]:
    payload = match_summary.inert_multiscale_features or {}
    if not payload:
        return []

    apk_features = payload.get("apk", {})
    reference_features = payload.get("reference", {})
    lines = [
        "## Inert Multi-Scale Feature Availability",
        "",
        f"- Scoring status: {payload.get('scoring_status', 'disabled')}",
        (
            "- Note: extracted for diagnostics and scoped experiments only; "
            "not used for matcher scoring, selected versions, vulnerability "
            "classification, or SBOM component selection."
        ),
        "",
        "| Feature | APK distinct / total | Reference components | Reference distinct / total |",
        "|---|---:|---:|---:|",
    ]
    for key, label in _multiscale_feature_labels():
        apk_counts = _count_pair(apk_features.get(key, {}))
        reference_counts = _count_pair(reference_features.get(key, {}))
        reference_components = _int_value(
            reference_features.get(key, {}),
            "components_with_features",
        )
        lines.append(
            f"| {label} | {apk_counts} | {reference_components} | {reference_counts} |"
        )
    return lines


def _html_inert_multiscale_features(match_summary: MatchSummary) -> str:
    payload = match_summary.inert_multiscale_features or {}
    if not payload:
        return "<p>No inert multi-scale feature summary was emitted.</p>"

    apk_features = payload.get("apk", {})
    reference_features = payload.get("reference", {})
    rows = []
    for key, label in _multiscale_feature_labels():
        rows.append(
            "<tr>"
            f"<td>{_html(label)}</td>"
            f"<td>{_html(_count_pair(apk_features.get(key, {})))}</td>"
            f"<td>{_int_value(reference_features.get(key, {}), 'components_with_features')}</td>"
            f"<td>{_html(_count_pair(reference_features.get(key, {})))}</td>"
            "</tr>"
        )
    return f"""
    <p>Scoring status: <strong>{_html(str(payload.get("scoring_status", "disabled")))}</strong></p>
    <p class="subtle">Extracted for diagnostics and scoped experiments only; not used for matcher scoring, selected versions, vulnerability classification, or SBOM component selection.</p>
    <table>
      <thead><tr><th>Feature</th><th>APK distinct / total</th><th>Reference components</th><th>Reference distinct / total</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    """


def _markdown_r8_phase5_experiment(experiment: dict | None) -> list[str]:
    if experiment is None:
        return []
    summary = experiment.get("summary", {})
    lines = [
        "",
        "## Experimental R8 Phase 5 Evidence",
        "",
        "- Report-only: true",
        (
            "- Note: this opt-in section does not change detected components, "
            "selected versions, SBOM output, vulnerability labels, or source-validation metrics."
        ),
        f"- Source: `{experiment.get('source')}`",
        f"- Verdict: `{experiment.get('verdict')}`",
        f"- Rows evaluated: `{summary.get('rows_evaluated', 0)}`",
        f"- Triggered rows: `{summary.get('triggered_rows', 0)}`",
        f"- Target improvements kept: `{summary.get('target_improvements_kept', 0)}`",
        f"- Triggered regressions/conflicts: `{summary.get('triggered_regressions', 0)}` / `{summary.get('triggered_conflicts', 0)}`",
        f"- Rows matching this report: `{summary.get('matching_rows', 0)}`",
        f"- Triggered rows matching this report: `{summary.get('matching_triggered_rows', 0)}`",
        "",
    ]
    rows = experiment.get("matching_triggered_rows") or []
    if rows:
        lines.extend(
            [
                "| Case | Coordinate | MVP selected | Phase 5 suggestion | Outcome | Profile |",
                "|---|---|---:|---:|---|---|",
            ]
        )
        for row in rows:
            decision = row.get("trigger_decision", {})
            lines.append(
                "| "
                f"{_markdown_cell(row.get('case'))} | "
                f"`{row.get('coordinate')}` | "
                f"{_markdown_cell(row.get('baseline_selected_version'))} | "
                f"{_markdown_cell(row.get('diagnostic_selected_version'))} | "
                f"`{row.get('trigger_outcome')}` | "
                f"`{decision.get('profile_id')}` |"
            )
    else:
        lines.append(
            "No Phase 5 triggered row matched this report. The section is still useful as dataset-level experiment context."
        )
    return lines


def _html_r8_phase5_experiment(experiment: dict | None) -> str:
    if experiment is None:
        return (
            "<p class=\"subtle\">Not enabled. Run <code>generate-report "
            "--include-r8-phase5-experiment</code> to attach report-only Phase 5 evidence.</p>"
        )
    summary = experiment.get("summary", {})
    rows = experiment.get("matching_triggered_rows") or []
    row_html = "".join(
        "<tr>"
        f"<td>{_html(row.get('case'))}</td>"
        f"<td><code>{_html(row.get('coordinate'))}</code></td>"
        f"<td>{_html(row.get('baseline_selected_version'))}</td>"
        f"<td>{_html(row.get('diagnostic_selected_version'))}</td>"
        f"<td>{_status_pill(str(row.get('trigger_outcome')))}</td>"
        f"<td><code>{_html(row.get('trigger_decision', {}).get('profile_id'))}</code></td>"
        "</tr>"
        for row in rows
    )
    if not row_html:
        row_html = (
            "<tr><td colspan=\"6\">No Phase 5 triggered row matched this report. "
            "This is dataset-level experiment context only.</td></tr>"
        )
    return f"""
    <p>Report-only: <strong>true</strong></p>
    <p class="subtle">This opt-in section does not change detected components, selected versions, SBOM output, vulnerability labels, or source-validation metrics.</p>
    <table>
      <tbody>
        <tr><th>Source</th><td><code>{_html(experiment.get("source"))}</code></td></tr>
        <tr><th>Verdict</th><td><code>{_html(experiment.get("verdict"))}</code></td></tr>
        <tr><th>Rows evaluated</th><td>{_html(summary.get("rows_evaluated", 0))}</td></tr>
        <tr><th>Triggered rows</th><td>{_html(summary.get("triggered_rows", 0))}</td></tr>
        <tr><th>Target improvements kept</th><td>{_html(summary.get("target_improvements_kept", 0))}</td></tr>
        <tr><th>Triggered regressions / conflicts</th><td>{_html(summary.get("triggered_regressions", 0))} / {_html(summary.get("triggered_conflicts", 0))}</td></tr>
        <tr><th>Rows matching this report</th><td>{_html(summary.get("matching_rows", 0))}</td></tr>
        <tr><th>Triggered rows matching this report</th><td>{_html(summary.get("matching_triggered_rows", 0))}</td></tr>
      </tbody>
    </table>
    <table>
      <thead><tr><th>Case</th><th>Coordinate</th><th>MVP selected</th><th>Phase 5 suggestion</th><th>Outcome</th><th>Profile</th></tr></thead>
      <tbody>{row_html}</tbody>
    </table>
    """


def _markdown_version_band_experiments(experiments: dict | None) -> list[str]:
    if experiments is None:
        return []
    lines = [
        "",
        "## Experimental Version-Band Evidence",
        "",
        "- Report-only: true",
        (
            "- Note: this opt-in section suggests claim downgrades or ambiguity annotations only. "
            "It does not change detected components, selected versions, SBOM component selection, "
            "vulnerability labels, or source-validation metrics."
        ),
        "",
    ]
    for title, key in (
        ("AppCompat/Core old-version-steal guard", "old_version_steal"),
        ("Lifecycle public-vs-Android family separation", "lifecycle_family"),
    ):
        evidence = experiments.get(key)
        lines.extend(_markdown_single_version_band_experiment(title, evidence))
    return lines


def _markdown_single_version_band_experiment(title: str, evidence: dict | None) -> list[str]:
    if evidence is None:
        return [f"### {title}", "", "Not attached.", ""]
    summary = evidence.get("summary", {})
    rows = evidence.get("matching_downgrade_rows") or []
    lines = [
        f"### {title}",
        "",
        f"- Source: `{evidence.get('source')}`",
        f"- Verdict: `{evidence.get('verdict')}`",
        f"- Rows matching this report: `{summary.get('matching_rows', 0)}`",
        f"- Downgrade rows matching this report: `{summary.get('matching_downgrade_rows', 0)}`",
        "",
    ]
    if rows:
        lines.extend(
            [
                "| Case | Coordinate | Selected | Source | Annotation |",
                "|---|---|---:|---|---|",
            ]
        )
        for row in rows:
            annotation = _version_band_annotation(row)
            lines.append(
                "| "
                f"{_markdown_cell(row.get('case_id') or row.get('case'))} | "
                f"`{row.get('coordinate')}` | "
                f"{_markdown_cell(row.get('selected_version'))} | "
                f"{_markdown_cell(row.get('source_versions'))} | "
                f"{_markdown_cell(annotation)} |"
            )
    else:
        lines.append("No downgrade suggestion matched this report.")
    lines.append("")
    return lines


def _html_version_band_experiments(experiments: dict | None) -> str:
    if experiments is None:
        return (
            "<p class=\"subtle\">Not enabled. Run <code>generate-report "
            "--include-version-band-experiments</code> to attach report-only version-band evidence.</p>"
        )
    sections = []
    for title, key in (
        ("AppCompat/Core old-version-steal guard", "old_version_steal"),
        ("Lifecycle public-vs-Android family separation", "lifecycle_family"),
    ):
        sections.append(_html_single_version_band_experiment(title, experiments.get(key)))
    return (
        "<p>Report-only: <strong>true</strong></p>"
        "<p class=\"subtle\">This opt-in section suggests claim downgrades or ambiguity annotations only; "
        "it does not change detected components, selected versions, SBOM component selection, vulnerability labels, or source-validation metrics.</p>"
        + "".join(sections)
    )


def _html_single_version_band_experiment(title: str, evidence: dict | None) -> str:
    if evidence is None:
        return f"<h3>{_html(title)}</h3><p>Not attached.</p>"
    summary = evidence.get("summary", {})
    rows = evidence.get("matching_downgrade_rows") or []
    row_html = "".join(
        "<tr>"
        f"<td>{_html(row.get('case_id') or row.get('case'))}</td>"
        f"<td><code>{_html(row.get('coordinate'))}</code></td>"
        f"<td>{_html(row.get('selected_version'))}</td>"
        f"<td>{_html(row.get('source_versions'))}</td>"
        f"<td>{_html(_version_band_annotation(row))}</td>"
        "</tr>"
        for row in rows
    )
    if not row_html:
        row_html = "<tr><td colspan=\"5\">No downgrade suggestion matched this report.</td></tr>"
    return f"""
    <h3>{_html(title)}</h3>
    <table>
      <tbody>
        <tr><th>Source</th><td><code>{_html(evidence.get("source"))}</code></td></tr>
        <tr><th>Verdict</th><td><code>{_html(evidence.get("verdict"))}</code></td></tr>
        <tr><th>Rows matching this report</th><td>{_html(summary.get("matching_rows", 0))}</td></tr>
        <tr><th>Downgrade rows matching this report</th><td>{_html(summary.get("matching_downgrade_rows", 0))}</td></tr>
      </tbody>
    </table>
    <table>
      <thead><tr><th>Case</th><th>Coordinate</th><th>Selected</th><th>Source</th><th>Annotation</th></tr></thead>
      <tbody>{row_html}</tbody>
    </table>
    """


def _version_band_annotation(row: dict) -> str:
    lifecycle = row.get("lifecycle_decision")
    if isinstance(lifecycle, dict):
        return (
            f"version claim downgrade suggested: {lifecycle.get('classification')} "
            f"via {lifecycle.get('target_coordinate')}@{lifecycle.get('target_version')}"
        )
    trigger = row.get("trigger_decision")
    if isinstance(trigger, dict):
        return (
            "version claim downgrade suggested: "
            + ", ".join(trigger.get("reason_codes") or [])
        )
    return "version-band annotation"


def _multiscale_feature_labels() -> list[tuple[str, str]]:
    return [
        ("call_chain_opcode_fingerprints", "Call-chain opcode fingerprints"),
        ("basic_block_opcode_fingerprints", "Basic-block opcode fingerprints"),
        ("class_neighbor_summaries", "Class-neighbor summaries"),
        ("field_operation_sequences", "Field-operation sequences"),
        ("literal_context_features", "Literal/context features"),
    ]


def _count_pair(value: object) -> str:
    if not isinstance(value, dict):
        return "0 / 0"
    return f"{_int_value(value, 'distinct')} / {_int_value(value, 'total')}"


def _int_value(value: object, key: str) -> int:
    if not isinstance(value, dict):
        return 0
    raw_value = value.get(key, 0)
    if isinstance(raw_value, bool):
        return int(raw_value)
    if isinstance(raw_value, int):
        return raw_value
    try:
        return int(str(raw_value))
    except (TypeError, ValueError):
        return 0


def _diagnostic_signals(payload: dict[str, object]) -> list[tuple[str, dict]]:
    fields = [
        "short_name_density",
        "package_flattening_or_repackaging",
        "class_method_coverage_loss",
        "low_structural_coverage",
        "low_confidence_component_ratio",
        "nonstandard_dex_or_protector_hints",
        "resource_shrinking_symptoms",
        "method_inlining_or_class_merging_indicators",
    ]
    return [
        (field_name, payload.get(field_name, {}))
        for field_name in fields
        if isinstance(payload.get(field_name, {}), dict)
    ]


def _metrics_summary(metrics: object) -> str:
    if not isinstance(metrics, dict) or not metrics:
        return "none"
    parts = []
    for key, value in metrics.items():
        if isinstance(value, list):
            rendered = ", ".join(str(item) for item in value[:4]) if value else "none"
            if len(value) > 4:
                rendered += f", +{len(value) - 4} more"
        else:
            rendered = _markdown_value(value)
        parts.append(f"{key}={rendered}")
    return "; ".join(parts)


def _markdown_value(value: object) -> str:
    if value is None:
        return "not evaluated"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _component_hint_summary(row: dict[str, object]) -> str:
    hints = []
    if row.get("method_collapse_indicator"):
        hints.append("method-collapse")
    if row.get("class_merging_indicator"):
        hints.append("class-merging")
    return ", ".join(hints) if hints else "none"


def candidate_reason_summary(evidence: list[ComponentEvidence]) -> str:
    labels = {
        "package-overlap": "package",
        "class-overlap": "class",
        "method-overlap": "method",
        "opcode-cosine": "opcode",
        "opcode-ngrams": "opcode-ngrams",
        "class-dependency-graph": "graph",
        "string-literals": "literals",
        "version-unique-features": "version-unique",
        "version-ambiguity": "ambiguous-version",
        "artifact-family-disambiguation": "artifact-family",
    }
    reasons: list[str] = []
    for item in evidence:
        label = labels.get(item.source)
        if not label:
            continue
        if item.source != "artifact-family-disambiguation" and item.weight <= 0:
            continue
        if label not in reasons:
            reasons.append(label)
    return ", ".join(reasons) if reasons else "not attached"


def _version_set_summary(versions: list[str]) -> str:
    if not versions:
        return "none"
    return ", ".join(versions)


def _markdown_list(values: list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(f"`{value}`" for value in values)


def _markdown_cell(value: object) -> str:
    return str(value or "").replace("|", "\\|")


def _html_component_rows(
    components: list[DetectedLibrary],
    vulnerability_labels: dict[str, str],
) -> str:
    if not components:
        return "<p>No components passed the current confidence and uncertainty filters.</p>"

    rows = []
    for component in components:
        identity_percent = max(0, min(100, round(component.identity_confidence * 100)))
        version_percent = max(0, min(100, round(component.version_confidence * 100)))
        evidence = "".join(
            "<li>"
            f"<strong>{_html(item.source)}</strong>: {_html(item.detail)} "
            f"<span class=\"subtle\">weight={item.weight:.3f}</span>"
            "</li>"
            for item in component.evidence
        ) or "<li>No detailed evidence attached.</li>"
        rows.append(
            "<tr>"
            f"<td><code>{_html(component.coordinate)}</code><br><span class=\"subtle\">{_html(component.purl)}</span></td>"
            f"<td>{_html(component.version)}</td>"
            f"<td>{_html(candidate_reason_summary(component.evidence))}</td>"
            f"<td>{_html(_confidence_summary(component.identity_status, component.identity_confidence_label, component.identity_confidence))}<div class=\"bar\"><span style=\"width:{identity_percent}%\"></span></div></td>"
            f"<td>{_html(_confidence_summary(component.version_status, component.version_confidence_label, component.version_confidence))}<div class=\"bar\"><span style=\"width:{version_percent}%\"></span></div></td>"
            f"<td>{_html(_version_set_summary(component.ambiguous_versions))}</td>"
            f"<td>{_status_pill(component.match_type)}</td>"
            f"<td>{_html(vulnerability_labels.get(component.purl, '0'))}</td>"
            f"<td><details><summary>Evidence</summary><ul>{evidence}</ul></details></td>"
            "</tr>"
        )
    return (
        "<table><thead><tr>"
        "<th>Component</th><th>Version</th><th>Reasons</th><th>Identity</th><th>Version confidence</th><th>Ambiguous versions</th><th>Match type</th><th>Vulns</th><th>Evidence</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _html_forensic_rows(apk: ApkInspection, obfuscation_risk: ObfuscationRisk) -> str:
    indicators = apk.forensic_summary.indicators
    indicator_rows = "".join(
        "<tr>"
        f"<td>{_status_pill(indicator.severity)}</td>"
        f"<td><code>{_html(indicator.code)}</code></td>"
        f"<td>{_html(indicator.detail)}</td>"
        "</tr>"
        for indicator in indicators
    ) or "<tr><td colspan=\"3\">No extraction indicators were raised.</td></tr>"
    reasons = "".join(
        f"<li>{_html(reason)}</li>"
        for reason in obfuscation_risk.reasons
    )
    return (
        "<table><tbody>"
        f"<tr><th>Standard DEX</th><td>{_html(', '.join(apk.forensic_summary.standard_dex_files) or 'none')}</td></tr>"
        f"<tr><th>Nonstandard DEX</th><td>{_html(', '.join(apk.forensic_summary.nonstandard_dex_files) or 'none')}</td></tr>"
        f"<tr><th>Native ABIs</th><td>{_html(', '.join(apk.forensic_summary.native_abis) or 'none')}</td></tr>"
        f"<tr><th>Permissions</th><td>{_html(', '.join(apk.manifest_metadata.permissions) or 'none')}</td></tr>"
        f"<tr><th>Obfuscation Risk</th><td>{_status_pill(obfuscation_risk.level)} score={obfuscation_risk.score:.2f}<ul>{reasons}</ul></td></tr>"
        "</tbody></table>"
        "<table><thead><tr><th>Severity</th><th>Code</th><th>Detail</th></tr></thead><tbody>"
        + indicator_rows
        + "</tbody></table>"
    )


def _html_native_rows(apk: ApkInspection) -> str:
    if not apk.native_libraries:
        return "<p>No native <code>.so</code> files were found in the APK.</p>"

    rows = []
    for library in apk.native_libraries:
        rows.append(
            "<tr>"
            f"<td><code>{_html(library.path)}</code></td>"
            f"<td>{_html(library.abi)}</td>"
            f"<td>{library.size}</td>"
            f"<td><code>{_html(library.sha256)}</code></td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Path</th><th>ABI</th><th>Size</th><th>SHA-256</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _html_decision_rows(match_summary: MatchSummary) -> str:
    if not match_summary.decisions:
        return "<p>No version decisions were produced.</p>"

    rows = []
    for decision in match_summary.decisions:
        alternatives = ", ".join(
            f"{alternative.version} ({alternative.score:.3f})"
            for alternative in decision.alternatives
        ) or "none"
        notes = decision.version_ambiguity_reason or decision.version_selection_reason or ""
        rows.append(
            "<tr>"
            f"<td><code>{_html(decision.coordinate)}</code></td>"
            f"<td>{_html(decision.selected_version)}</td>"
            f"<td>{_status_pill(_confidence_summary(decision.identity_status, decision.identity_confidence_label, decision.identity_confidence))}</td>"
            f"<td>{_status_pill(_confidence_summary(decision.version_status, decision.version_confidence_label, decision.version_confidence))}</td>"
            f"<td>{decision.score:.3f}</td>"
            f"<td>{decision.gap_to_next:.3f}</td>"
            f"<td>{_html(alternatives)}</td>"
            f"<td>{_html(notes)}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr>"
        "<th>Component</th><th>Selected version</th><th>Identity</th><th>Version</th><th>Score</th><th>Gap</th><th>Alternatives</th><th>Notes</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _html_vulnerability_rows(vulnerability_rows: list[tuple]) -> str:
    if not vulnerability_rows:
        return "<p>No vulnerabilities were returned by the configured source, or vulnerability lookup was not run.</p>"

    rows = []
    for result, vulnerability in vulnerability_rows:
        aliases = ", ".join(vulnerability.aliases or []) or "none"
        summary = vulnerability.summary or "not provided"
        reason = result.finding_reason or ""
        rows.append(
            "<tr>"
            f"<td><code>{_html(result.coordinate)}</code></td>"
            f"<td>{_html(result.version)}</td>"
            f"<td>{_status_pill(result.finding_confidence)}<br><span class=\"subtle\">{_html(reason)}</span></td>"
            f"<td>{_status_pill(result.source_validation_finding or 'not checked')}<br><span class=\"subtle\">{_html(result.source_validation_reason or '')}</span></td>"
            f"<td>{_status_pill(_vulnerability_severity(vulnerability))}</td>"
            f"<td><code>{_html(vulnerability.id)}</code></td>"
            f"<td>{_html(aliases)}</td>"
            f"<td>{_html(summary)}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Component</th><th>Version</th><th>Finding</th><th>Source validation</th><th>Severity</th><th>Advisory</th><th>Aliases</th><th>Summary</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _source_validation_summary(result: object) -> str:
    finding = getattr(result, "source_validation_finding", None)
    if not finding:
        return "not checked"
    reason = getattr(result, "source_validation_reason", None) or ""
    versions = getattr(result, "source_versions", None) or []
    if versions:
        return f"{finding}: {reason} ({', '.join(versions)})"
    return f"{finding}: {reason}"


def _status_pill(value: str) -> str:
    lowered = value.lower()
    style = ""
    if "confirmed" in lowered or "exact" in lowered or "likely" in lowered:
        style = " ok"
    elif "candidate" in lowered or "uncertain" in lowered or "potential" in lowered:
        style = " warn"
    elif "failed" in lowered or "vulnerab" in lowered or "critical" in lowered or "high" in lowered:
        style = " bad"
    return f"<span class=\"pill{style}\">{_html(value)}</span>"


def _vulnerability_severity(vulnerability: object) -> str:
    severity = getattr(vulnerability, "severity", None)
    score = getattr(vulnerability, "severity_score", None)
    if severity and score:
        return f"{severity} ({score})"
    if severity:
        return str(severity)
    if score:
        return str(score)
    return "UNKNOWN"


def _confidence_summary(status: object, label: object, value: object) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = 0.0
    return f"{status}/{label} ({numeric:.3f})"


def _html(value: object) -> str:
    return escape(str(value), quote=True)
