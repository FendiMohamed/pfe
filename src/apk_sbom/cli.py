from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from apk_sbom.apk_extractor import inspect_apk
from apk_sbom.dex_analyzer import analyze_apk_dex
from apk_sbom.maven_downloader import (
    DEFAULT_MAVEN_REPOSITORY_URL,
    DEFAULT_REFERENCE_ARTIFACT_ROOT,
    artifacts_from_libraries,
    download_artifacts,
)
from apk_sbom.matcher import (
    DEFAULT_API_REFERENCE_WEIGHT,
    DEFAULT_CLASS_WEIGHT,
    COMPOSITE_FAMILY_SHORTLIST_MARGIN,
    DEFAULT_DEPENDENCY_WEIGHT,
    DEFAULT_LITERAL_WEIGHT,
    DEFAULT_METHOD_WEIGHT,
    DEFAULT_OPCODE_NGRAM_WEIGHT,
    DEFAULT_OPCODE_WEIGHT,
    DEFAULT_PACKAGE_WEIGHT,
    DEFAULT_UNIQUE_VERSION_WEIGHT,
    detected_libraries_from_match_summary,
    match_apk_to_reference_db,
)
from apk_sbom.obfuscation import build_obfuscation_diagnostics
from apk_sbom.reference_config import load_libraries_config
from apk_sbom.reference_converter import (
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_DEX_ROOT,
    convert_reference_artifacts,
    discover_artifact_records,
    planned_conversion,
)
from apk_sbom.reference_features import (
    DEFAULT_FEATURE_DB_PATH,
    discover_conversion_results,
    extract_reference_features_to_db,
)
from apk_sbom.r8_phase5_experiment import (
    DEFAULT_OUTPUT_DOC as DEFAULT_R8_PHASE5_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON as DEFAULT_R8_PHASE5_OUTPUT_JSON,
    DEFAULT_PHASE4_JSON as DEFAULT_R8_PHASE5_PHASE4_JSON,
    build_payload as build_r8_phase5_payload,
    write_outputs as write_r8_phase5_outputs,
)
from apk_sbom.version_band_trigger_diagnostics import (
    DEFAULT_INPUT_JSON as DEFAULT_VERSION_BAND_INPUT_JSON,
    DEFAULT_OUTPUT_DOC as DEFAULT_VERSION_BAND_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON as DEFAULT_VERSION_BAND_OUTPUT_JSON,
    build_payload as build_version_band_payload,
    write_outputs as write_version_band_outputs,
)
from apk_sbom.lifecycle_family_diagnostics import (
    DEFAULT_INPUT_JSON as DEFAULT_LIFECYCLE_FAMILY_INPUT_JSON,
    DEFAULT_OUTPUT_DOC as DEFAULT_LIFECYCLE_FAMILY_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON as DEFAULT_LIFECYCLE_FAMILY_OUTPUT_JSON,
    build_payload as build_lifecycle_family_payload,
    write_outputs as write_lifecycle_family_outputs,
)
from apk_sbom.no_maven_androidx_experiment import (
    DEFAULT_INPUT_JSON as DEFAULT_NO_MAVEN_ANDROIDX_INPUT_JSON,
    DEFAULT_OUTPUT_DOC as DEFAULT_NO_MAVEN_ANDROIDX_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON as DEFAULT_NO_MAVEN_ANDROIDX_OUTPUT_JSON,
    build_payload as build_no_maven_androidx_payload,
    write_outputs as write_no_maven_androidx_outputs,
)
from apk_sbom.no_maven_fork_family_experiment import (
    DEFAULT_INPUT_JSON as DEFAULT_NO_MAVEN_FORK_FAMILY_INPUT_JSON,
    DEFAULT_OUTPUT_DOC as DEFAULT_NO_MAVEN_FORK_FAMILY_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON as DEFAULT_NO_MAVEN_FORK_FAMILY_OUTPUT_JSON,
    build_payload as build_no_maven_fork_family_payload,
    write_outputs as write_no_maven_fork_family_outputs,
)
from apk_sbom.literal_context_diagnostics import (
    DEFAULT_INPUT_JSON as DEFAULT_LITERAL_CONTEXT_INPUT_JSON,
    DEFAULT_OUTPUT_DOC as DEFAULT_LITERAL_CONTEXT_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON as DEFAULT_LITERAL_CONTEXT_OUTPUT_JSON,
    build_payload as build_literal_context_payload,
    write_outputs as write_literal_context_outputs,
)
from apk_sbom.version_unique_literal_context_diagnostics import (
    DEFAULT_OUTPUT_DOC as DEFAULT_VERSION_UNIQUE_LITERAL_CONTEXT_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON as DEFAULT_VERSION_UNIQUE_LITERAL_CONTEXT_OUTPUT_JSON,
    DEFAULT_PHASE4_JSON as DEFAULT_VERSION_UNIQUE_LITERAL_CONTEXT_PHASE4_JSON,
    DEFAULT_REFERENCE_DB as DEFAULT_VERSION_UNIQUE_LITERAL_CONTEXT_REFERENCE_DB,
    build_payload as build_version_unique_literal_context_payload,
    write_outputs as write_version_unique_literal_context_outputs,
)
from apk_sbom.reference_expander import (
    DEFAULT_EXPANDED_CONFIG,
    DEFAULT_REFERENCE_CATALOG,
    expand_reference_catalog,
)
from apk_sbom.report import (
    DEFAULT_R8_MINIFIED_CONFIDENCE_POLICY_JSON,
    DEFAULT_R8_PHASE5_EXPERIMENT_JSON,
    DEFAULT_LIFECYCLE_FAMILY_EXPERIMENT_JSON,
    DEFAULT_REPORT_DIR,
    DEFAULT_VERSION_BAND_EXPERIMENT_JSON,
    generate_final_report,
)
from apk_sbom.sbom import build_cyclonedx_bom, make_mock_detection
from apk_sbom.source_validation import (
    DEFAULT_SOURCE_VALIDATION_DIR,
    parse_maven_component_spec,
    write_source_validation_report,
)
from apk_sbom.vulnerability import (
    DEFAULT_OSV_BATCH_URL,
    load_detected_libraries_from_cyclonedx,
    query_osv_for_libraries,
)


DEFAULT_VERSION_UNIQUE_LITERAL_CONTEXT_RERANKER_ENABLED = True
DEFAULT_COMPOSITE_FAMILY_SHORTLIST_ENABLED = True


def add_version_unique_literal_context_reranker_args(
    parser: argparse.ArgumentParser,
) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--enable-version-unique-literal-context-reranker",
        dest="enable_version_unique_literal_context_reranker",
        action="store_true",
        default=DEFAULT_VERSION_UNIQUE_LITERAL_CONTEXT_RERANKER_ENABLED,
        help=(
            "Enable the guarded version-unique literal/context near-tie reranker. "
            "This is now the default; the flag is kept for command compatibility."
        ),
    )
    group.add_argument(
        "--disable-version-unique-literal-context-reranker",
        dest="enable_version_unique_literal_context_reranker",
        action="store_false",
        help=(
            "Disable the guarded version-unique literal/context near-tie reranker "
            "to reproduce the pre-promotion baseline."
        ),
    )


def add_composite_family_shortlist_experiment_args(
    parser: argparse.ArgumentParser,
) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--enable-composite-family-shortlist",
        "--enable-composite-family-shortlist-experiment",
        dest="enable_composite_family_shortlist",
        action="store_true",
        default=DEFAULT_COMPOSITE_FAMILY_SHORTLIST_ENABLED,
        help=(
            "Enable the guarded balanced composite family shortlist before full "
            "reference scoring. This is now the default; the experiment flag is "
            "kept as a compatibility alias."
        ),
    )
    group.add_argument(
        "--disable-composite-family-shortlist",
        dest="enable_composite_family_shortlist",
        action="store_false",
        help=(
            "Disable the guarded balanced composite family shortlist to reproduce "
            "the pre-promotion baseline."
        ),
    )
    parser.add_argument(
        "--composite-family-shortlist-margin",
        type=float,
        default=COMPOSITE_FAMILY_SHORTLIST_MARGIN,
        help="Family shortlist score margin used by the guarded shortlist.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apk-sbom",
        description="MVP utilities for recovering SBOM evidence from compiled Android APKs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser(
        "inspect-apk",
        help="Inspect an APK archive and output a JSON extraction summary.",
    )
    inspect_parser.add_argument("apk_path", help="Path to the APK file.")

    analyze_parser = subparsers.add_parser(
        "analyze-dex",
        help="Parse APK DEX files and output class/package/opcode feature counts.",
    )
    analyze_parser.add_argument("apk_path", help="Path to the APK file.")

    mock_sbom_parser = subparsers.add_parser(
        "generate-mock-sbom",
        help="Generate a minimal CycloneDX SBOM from one mocked library detection.",
    )
    mock_sbom_parser.add_argument("apk_path", help="Path to the APK file.")
    mock_sbom_parser.add_argument(
        "--output",
        default="data/results/mock-sbom.cdx.json",
        help="Output path for the CycloneDX JSON SBOM.",
    )

    sbom_parser = subparsers.add_parser(
        "generate-sbom",
        help="Generate CycloneDX SBOM from real matcher decisions.",
    )
    sbom_parser.add_argument("apk_path", help="Path to the APK file.")
    sbom_parser.add_argument(
        "--output",
        default="data/results/sbom.cdx.json",
        help="Output path for the CycloneDX JSON SBOM.",
    )
    sbom_parser.add_argument(
        "--db-path",
        default=str(DEFAULT_FEATURE_DB_PATH),
        help="SQLite reference feature database path.",
    )
    sbom_parser.add_argument(
        "--coordinate",
        help="Optional coordinate filter, for example com.google.code.gson:gson.",
    )
    sbom_parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Maximum number of ranked candidates used for report context.",
    )
    sbom_parser.add_argument(
        "--min-score",
        type=float,
        default=0.05,
        help="Minimum match score required for a candidate to be considered.",
    )
    sbom_parser.add_argument(
        "--include-uncertain",
        action="store_true",
        help="Include uncertain version decisions as SBOM components.",
    )
    add_version_unique_literal_context_reranker_args(sbom_parser)
    add_composite_family_shortlist_experiment_args(sbom_parser)

    download_parser = subparsers.add_parser(
        "download-maven",
        help="Download selected Maven artifacts for the local reference DB.",
    )
    download_parser.add_argument(
        "--config",
        default="configs/libraries.json",
        help="Path to the Maven library selection config.",
    )
    download_parser.add_argument(
        "--output-root",
        default=str(DEFAULT_REFERENCE_ARTIFACT_ROOT),
        help="Directory where Maven artifacts and metadata will be stored.",
    )
    download_parser.add_argument(
        "--repository-url",
        default=DEFAULT_MAVEN_REPOSITORY_URL,
        help="Base Maven repository URL.",
    )
    download_parser.add_argument(
        "--coordinate",
        help="Optional coordinate filter, for example com.google.code.gson:gson.",
    )
    download_parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of artifacts to process.",
    )
    download_parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Number of selected artifacts to skip before processing.",
    )
    download_parser.add_argument(
        "--packaging",
        default="jar",
        choices=["jar", "aar"],
        help="Artifact packaging extension to download.",
    )
    download_parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Download timeout in seconds per artifact.",
    )
    download_parser.add_argument(
        "--force",
        action="store_true",
        help="Redownload artifacts even when artifact and metadata files already exist.",
    )
    download_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned artifact URLs and paths without downloading.",
    )
    download_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only status counts instead of full per-artifact JSON.",
    )

    expand_parser = subparsers.add_parser(
        "expand-reference-config",
        help="Resolve a reference catalog into a libraries config with selected Maven versions.",
    )
    expand_parser.add_argument(
        "--catalog",
        default=str(DEFAULT_REFERENCE_CATALOG),
        help="Path to the coordinate catalog to expand.",
    )
    expand_parser.add_argument(
        "--output",
        default=str(DEFAULT_EXPANDED_CONFIG),
        help="Output path for the generated libraries config.",
    )
    expand_parser.add_argument(
        "--repository-url",
        default=DEFAULT_MAVEN_REPOSITORY_URL,
        help="Base Maven repository URL.",
    )
    expand_parser.add_argument(
        "--latest-count",
        type=int,
        default=1,
        help="Number of latest stable versions to select per catalog coordinate.",
    )
    expand_parser.add_argument(
        "--all-versions",
        action="store_true",
        help="Select every metadata-published version instead of only the latest stable versions.",
    )
    expand_parser.add_argument(
        "--include-prerelease",
        action="store_true",
        help="Allow alpha, beta, RC, milestone, preview, EAP, and snapshot versions.",
    )
    expand_parser.add_argument(
        "--coordinate",
        help="Optional coordinate filter, for example com.google.code.gson:gson.",
    )
    expand_parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of catalog coordinates to process.",
    )
    expand_parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Maven metadata request timeout in seconds.",
    )
    expand_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print expansion results without writing the generated config.",
    )
    expand_parser.add_argument(
        "--summary-output",
        help="Optional path for the full expansion summary JSON.",
    )
    expand_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only a short expansion summary.",
    )

    convert_parser = subparsers.add_parser(
        "convert-reference-dex",
        help="Convert downloaded Maven reference artifacts to DEX with D8.",
    )
    convert_parser.add_argument(
        "--artifact-root",
        default=str(DEFAULT_ARTIFACT_ROOT),
        help="Directory containing downloaded Maven artifacts and metadata.",
    )
    convert_parser.add_argument(
        "--output-root",
        default=str(DEFAULT_DEX_ROOT),
        help="Directory where converted reference DEX files will be stored.",
    )
    convert_parser.add_argument(
        "--coordinate",
        help="Optional coordinate filter, for example com.google.code.gson:gson.",
    )
    convert_parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of artifacts to process.",
    )
    convert_parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Number of discovered artifact metadata records to skip before processing.",
    )
    convert_parser.add_argument(
        "--d8-command",
        default="d8",
        help="D8 command to execute. Defaults to 'd8'.",
    )
    convert_parser.add_argument(
        "--min-api",
        type=int,
        default=21,
        help="Android min API passed to D8.",
    )
    convert_parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="D8 timeout in seconds per artifact.",
    )
    convert_parser.add_argument(
        "--force",
        action="store_true",
        help="Run conversion even when conversion metadata and DEX files already exist.",
    )
    convert_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned conversion records without running D8.",
    )
    convert_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only status counts instead of full conversion JSON and D8 warnings.",
    )

    features_parser = subparsers.add_parser(
        "extract-reference-features",
        help="Extract features from converted reference DEX files into SQLite.",
    )
    features_parser.add_argument(
        "--dex-root",
        default=str(DEFAULT_DEX_ROOT),
        help="Directory containing converted reference DEX metadata.",
    )
    features_parser.add_argument(
        "--db-path",
        default=str(DEFAULT_FEATURE_DB_PATH),
        help="SQLite database path for extracted reference features.",
    )
    features_parser.add_argument(
        "--coordinate",
        help="Optional coordinate filter, for example com.google.code.gson:gson.",
    )
    features_parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of converted artifacts to process.",
    )
    features_parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Number of discovered conversion metadata records to skip before processing.",
    )
    features_parser.add_argument(
        "--include-skipped",
        action="store_true",
        help="Include skipped conversion records in the summary.",
    )
    features_parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate the SQLite feature database before extraction.",
    )
    features_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only database row counts and extraction status counts.",
    )

    match_parser = subparsers.add_parser(
        "match-apk",
        help="Rank Maven reference library versions by package/class/method overlap.",
    )
    match_parser.add_argument("apk_path", help="Path to the APK file.")
    match_parser.add_argument(
        "--db-path",
        default=str(DEFAULT_FEATURE_DB_PATH),
        help="SQLite reference feature database path.",
    )
    match_parser.add_argument(
        "--coordinate",
        help="Optional coordinate filter, for example com.google.code.gson:gson.",
    )
    match_parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Maximum number of ranked candidates to output.",
    )
    match_parser.add_argument(
        "--min-score",
        type=float,
        default=0.05,
        help="Minimum overlap score required for a candidate to be returned.",
    )
    match_parser.add_argument(
        "--package-weight",
        type=float,
        default=DEFAULT_PACKAGE_WEIGHT,
        help="Weight for package reference coverage.",
    )
    match_parser.add_argument(
        "--class-weight",
        type=float,
        default=DEFAULT_CLASS_WEIGHT,
        help="Weight for class reference coverage.",
    )
    match_parser.add_argument(
        "--method-weight",
        type=float,
        default=DEFAULT_METHOD_WEIGHT,
        help="Weight for method reference coverage.",
    )
    match_parser.add_argument(
        "--opcode-weight",
        type=float,
        default=DEFAULT_OPCODE_WEIGHT,
        help="Weight for opcode histogram cosine similarity.",
    )
    match_parser.add_argument(
        "--dependency-weight",
        type=float,
        default=DEFAULT_DEPENDENCY_WEIGHT,
        help="Weight for class dependency graph similarity.",
    )
    match_parser.add_argument(
        "--literal-weight",
        type=float,
        default=DEFAULT_LITERAL_WEIGHT,
        help="Weight for string literal overlap.",
    )
    match_parser.add_argument(
        "--unique-version-weight",
        type=float,
        default=DEFAULT_UNIQUE_VERSION_WEIGHT,
        help="Weight for version-unique class/method/literal tie-breakers.",
    )
    match_parser.add_argument(
        "--api-reference-weight",
        type=float,
        default=DEFAULT_API_REFERENCE_WEIGHT,
        help="Weight for invoked API/member reference overlap.",
    )
    match_parser.add_argument(
        "--opcode-ngram-weight",
        type=float,
        default=DEFAULT_OPCODE_NGRAM_WEIGHT,
        help="Weight for opcode tri-gram cosine similarity.",
    )
    add_version_unique_literal_context_reranker_args(match_parser)
    add_composite_family_shortlist_experiment_args(match_parser)

    osv_parser = subparsers.add_parser(
        "scan-sbom-osv",
        help="Query OSV for Maven components in a CycloneDX SBOM.",
    )
    osv_parser.add_argument("sbom_path", help="Path to a CycloneDX JSON SBOM.")
    osv_parser.add_argument(
        "--output",
        default="data/results/osv-vulnerabilities.json",
        help="Output path for the OSV vulnerability result JSON.",
    )
    osv_parser.add_argument(
        "--api-url",
        default=DEFAULT_OSV_BATCH_URL,
        help="OSV querybatch API URL.",
    )
    osv_parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds.",
    )
    osv_parser.add_argument(
        "--no-enrich",
        action="store_true",
        help="Do not fetch individual OSV advisory details for aliases and summaries.",
    )

    report_parser = subparsers.add_parser(
        "generate-report",
        help="Run the MVP pipeline and write JSON/Markdown report artifacts.",
    )
    report_parser.add_argument("apk_path", help="Path to the APK file.")
    report_parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory where report artifacts will be written.",
    )
    report_parser.add_argument(
        "--db-path",
        default=str(DEFAULT_FEATURE_DB_PATH),
        help="SQLite reference feature database path.",
    )
    report_parser.add_argument(
        "--coordinate",
        help="Optional coordinate filter, for example com.google.code.gson:gson.",
    )
    report_parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Maximum number of ranked candidates to include.",
    )
    report_parser.add_argument(
        "--min-score",
        type=float,
        default=0.05,
        help="Minimum match score required for a candidate to be considered.",
    )
    report_parser.add_argument(
        "--api-reference-weight",
        type=float,
        default=DEFAULT_API_REFERENCE_WEIGHT,
        help="Weight for invoked API/member reference overlap.",
    )
    report_parser.add_argument(
        "--opcode-ngram-weight",
        type=float,
        default=DEFAULT_OPCODE_NGRAM_WEIGHT,
        help="Weight for opcode tri-gram cosine similarity.",
    )
    report_parser.add_argument(
        "--include-uncertain",
        action="store_true",
        help="Include uncertain version decisions as SBOM/report components.",
    )
    add_version_unique_literal_context_reranker_args(report_parser)
    add_composite_family_shortlist_experiment_args(report_parser)
    report_parser.add_argument(
        "--enable-reference-package-prefilter",
        action="store_true",
        help=(
            "Experiment-only speedup: score only reference components sharing at "
            "least one package with the APK. Default behavior is unchanged."
        ),
    )
    report_parser.add_argument(
        "--reference-package-prefilter-min-overlap",
        type=int,
        default=1,
        help="Minimum shared APK/reference packages required by --enable-reference-package-prefilter.",
    )
    report_parser.add_argument(
        "--reference-package-prefilter-limit",
        type=int,
        help="Maximum number of package-overlap prefilter components to score.",
    )
    report_parser.add_argument(
        "--reference-package-prefilter-per-coordinate-limit",
        type=int,
        help=(
            "Maximum package-overlap prefilter components to keep per coordinate before "
            "the optional global --reference-package-prefilter-limit is applied."
        ),
    )
    report_parser.add_argument(
        "--skip-osv",
        action="store_true",
        help="Do not query OSV while generating the report.",
    )
    report_parser.add_argument(
        "--osv-api-url",
        default=DEFAULT_OSV_BATCH_URL,
        help="OSV querybatch API URL.",
    )
    report_parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="OSV request timeout in seconds.",
    )
    report_parser.add_argument(
        "--no-enrich",
        action="store_true",
        help="Do not fetch individual OSV advisory details for aliases and summaries.",
    )
    report_parser.add_argument(
        "--source-validation-json",
        help=(
            "Optional source-validation.json artifact used to relabel OSV findings "
            "as source-confirmed, source-version-mismatch, source-missing, or not-source-validated."
        ),
    )
    report_parser.add_argument(
        "--include-r8-phase5-experiment",
        action="store_true",
        help=(
            "Attach opt-in, report-only Phase 5 R8 scoped-trigger evidence. "
            "This does not change matcher scoring, selected versions, SBOM output, "
            "vulnerability labels, or source-validation metrics."
        ),
    )
    report_parser.add_argument(
        "--r8-phase5-experiment-json",
        default=str(DEFAULT_R8_PHASE5_EXPERIMENT_JSON),
        help="Phase 5 experiment JSON to attach when --include-r8-phase5-experiment is used.",
    )
    report_parser.add_argument(
        "--include-version-band-experiments",
        action="store_true",
        help=(
            "Attach opt-in, report-only version-band diagnostics. This does not change "
            "matcher scoring, selected versions, SBOM component selection, vulnerability labels, "
            "or source-validation metrics."
        ),
    )
    report_parser.add_argument(
        "--version-band-experiment-json",
        default=str(DEFAULT_VERSION_BAND_EXPERIMENT_JSON),
        help="Old-version-steal experiment JSON to attach when --include-version-band-experiments is used.",
    )
    report_parser.add_argument(
        "--lifecycle-family-experiment-json",
        default=str(DEFAULT_LIFECYCLE_FAMILY_EXPERIMENT_JSON),
        help="Lifecycle family experiment JSON to attach when --include-version-band-experiments is used.",
    )
    report_parser.add_argument(
        "--include-r8-minified-confidence-policy",
        action="store_true",
        help=(
            "Attach opt-in, report-only minified/R8 confidence and ambiguity policy "
            "evidence. This changes report wording only and does not change matcher "
            "scoring, selected versions, SBOM output, vulnerability labels, or "
            "source-validation metrics."
        ),
    )
    report_parser.add_argument(
        "--r8-minified-confidence-policy-json",
        default=str(DEFAULT_R8_MINIFIED_CONFIDENCE_POLICY_JSON),
        help=(
            "R8 minified confidence policy JSON to attach when "
            "--include-r8-minified-confidence-policy is used."
        ),
    )

    r8_phase5_parser = subparsers.add_parser(
        "r8-phase5-experiment",
        help=(
            "Run the opt-in Phase 5 scoped R8 trigger experiment from a Phase 4 "
            "diagnostic JSON without changing MVP matcher/report/SBOM behavior."
        ),
    )
    r8_phase5_parser.add_argument(
        "--phase4-json",
        default=str(DEFAULT_R8_PHASE5_PHASE4_JSON),
        help="Phase 4 scoped experiment JSON used as the experiment input.",
    )
    r8_phase5_parser.add_argument(
        "--output-json",
        default=str(DEFAULT_R8_PHASE5_OUTPUT_JSON),
        help="Output path for the Phase 5 experiment JSON.",
    )
    r8_phase5_parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_R8_PHASE5_OUTPUT_DOC),
        help="Output path for the Phase 5 experiment Markdown report.",
    )
    r8_phase5_parser.add_argument(
        "--json-only",
        action="store_true",
        help="Write only the JSON artifact and skip the Markdown report.",
    )

    version_band_parser = subparsers.add_parser(
        "version-band-experiment",
        help=(
            "Run the opt-in AndroidX old-version-steal diagnostic without changing "
            "matcher scoring, selected versions, SBOM output, or the shared DB."
        ),
    )
    version_band_parser.add_argument(
        "--input-json",
        default=str(DEFAULT_VERSION_BAND_INPUT_JSON),
        help="Low-risk version-band diagnostic JSON used as the experiment input.",
    )
    version_band_parser.add_argument(
        "--output-json",
        default=str(DEFAULT_VERSION_BAND_OUTPUT_JSON),
        help="Output path for the scoped version-band experiment JSON.",
    )
    version_band_parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_VERSION_BAND_OUTPUT_DOC),
        help="Output path for the scoped version-band experiment Markdown report.",
    )

    lifecycle_family_parser = subparsers.add_parser(
        "lifecycle-family-experiment",
        help=(
            "Run the opt-in Lifecycle public-vs-Android family separation diagnostic "
            "without changing matcher scoring, selected versions, SBOM output, or the shared DB."
        ),
    )
    lifecycle_family_parser.add_argument(
        "--input-json",
        default=str(DEFAULT_LIFECYCLE_FAMILY_INPUT_JSON),
        help="Low-risk version-band diagnostic JSON used as the experiment input.",
    )
    lifecycle_family_parser.add_argument(
        "--output-json",
        default=str(DEFAULT_LIFECYCLE_FAMILY_OUTPUT_JSON),
        help="Output path for the Lifecycle family experiment JSON.",
    )
    lifecycle_family_parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_LIFECYCLE_FAMILY_OUTPUT_DOC),
        help="Output path for the Lifecycle family experiment Markdown report.",
    )

    no_maven_androidx_parser = subparsers.add_parser(
        "no-maven-androidx-experiment",
        help=(
            "Run the opt-in no-Maven AndroidX report-only diagnostic without changing "
            "matcher scoring, selected versions, SBOM output, or the shared DB."
        ),
    )
    no_maven_androidx_parser.add_argument(
        "--input-json",
        default=str(DEFAULT_NO_MAVEN_ANDROIDX_INPUT_JSON),
        help="No-Maven signal diagnostic JSON used as the experiment input.",
    )
    no_maven_androidx_parser.add_argument(
        "--output-json",
        default=str(DEFAULT_NO_MAVEN_ANDROIDX_OUTPUT_JSON),
        help="Output path for the no-Maven AndroidX experiment JSON.",
    )
    no_maven_androidx_parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_NO_MAVEN_ANDROIDX_OUTPUT_DOC),
        help="Output path for the no-Maven AndroidX experiment Markdown report.",
    )

    no_maven_fork_family_parser = subparsers.add_parser(
        "no-maven-fork-family-experiment",
        help=(
            "Run the opt-in Mastodon fork-family diagnostic without changing "
            "matcher scoring, selected versions, SBOM output, or the shared DB."
        ),
    )
    no_maven_fork_family_parser.add_argument(
        "--input-json",
        default=str(DEFAULT_NO_MAVEN_FORK_FAMILY_INPUT_JSON),
        help="No-Maven signal diagnostic JSON used as the experiment input.",
    )
    no_maven_fork_family_parser.add_argument(
        "--output-json",
        default=str(DEFAULT_NO_MAVEN_FORK_FAMILY_OUTPUT_JSON),
        help="Output path for the Mastodon fork-family audit JSON.",
    )
    no_maven_fork_family_parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_NO_MAVEN_FORK_FAMILY_OUTPUT_DOC),
        help="Output path for the Mastodon fork-family audit Markdown report.",
    )

    literal_context_parser = subparsers.add_parser(
        "literal-context-experiment",
        help=(
            "Evaluate raw literal/context version-tie evidence without changing "
            "matcher scoring, selected versions, SBOM output, or the shared DB."
        ),
    )
    literal_context_parser.add_argument(
        "--input-json",
        default=str(DEFAULT_LITERAL_CONTEXT_INPUT_JSON),
        help="Phase 4 multi-scale diagnostic JSON used as the experiment input.",
    )
    literal_context_parser.add_argument(
        "--output-json",
        default=str(DEFAULT_LITERAL_CONTEXT_OUTPUT_JSON),
        help="Output path for the literal/context diagnostic JSON.",
    )
    literal_context_parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_LITERAL_CONTEXT_OUTPUT_DOC),
        help="Output path for the literal/context diagnostic Markdown report.",
    )

    version_unique_literal_context_parser = subparsers.add_parser(
        "version-unique-literal-context-experiment",
        help=(
            "Evaluate version-unique literal/context evidence without changing "
            "matcher scoring, selected versions, SBOM output, or the shared DB."
        ),
    )
    version_unique_literal_context_parser.add_argument(
        "--phase4-json",
        default=str(DEFAULT_VERSION_UNIQUE_LITERAL_CONTEXT_PHASE4_JSON),
        help="Phase 4 diagnostic JSON used for APK/source-validation row metadata.",
    )
    version_unique_literal_context_parser.add_argument(
        "--reference-db",
        default=str(DEFAULT_VERSION_UNIQUE_LITERAL_CONTEXT_REFERENCE_DB),
        help="Reference feature DB used to compute version-unique literal/context features.",
    )
    version_unique_literal_context_parser.add_argument(
        "--output-json",
        default=str(DEFAULT_VERSION_UNIQUE_LITERAL_CONTEXT_OUTPUT_JSON),
        help="Output path for the version-unique literal/context diagnostic JSON.",
    )
    version_unique_literal_context_parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_VERSION_UNIQUE_LITERAL_CONTEXT_OUTPUT_DOC),
        help="Output path for the version-unique literal/context diagnostic Markdown report.",
    )

    source_validation_parser = subparsers.add_parser(
        "validate-source-deps",
        help="Compare a CycloneDX SBOM against a Gradle dependency tree.",
    )
    source_validation_parser.add_argument(
        "--sbom",
        required=True,
        help="Path to the CycloneDX JSON SBOM produced by the MVP.",
    )
    source_validation_parser.add_argument(
        "--dependency-tree",
        required=True,
        help="Path to a Gradle dependencies output file, such as fullReleaseRuntimeClasspath.",
    )
    source_validation_parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_SOURCE_VALIDATION_DIR),
        help="Directory where source validation JSON and Markdown reports will be written.",
    )
    source_validation_parser.add_argument(
        "--candidate",
        action="append",
        default=[],
        help=(
            "Optional extra Maven candidate to check, formatted as group:artifact@version "
            "or pkg:maven/group/artifact@version. Can be repeated."
        ),
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "inspect-apk":
        try:
            inspection = inspect_apk(args.apk_path)
            dex_analysis = analyze_apk_dex(args.apk_path, include_members=True)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        payload = inspection.to_dict()
        payload["obfuscation_diagnostics"] = build_obfuscation_diagnostics(
            inspection,
            dex_analysis=dex_analysis,
        ).to_dict()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if args.command == "analyze-dex":
        try:
            analysis = analyze_apk_dex(args.apk_path)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(analysis.to_json())
        return 0

    if args.command == "generate-mock-sbom":
        try:
            inspection = inspect_apk(args.apk_path)
            bom = build_cyclonedx_bom(inspection, [make_mock_detection()])
            output_path = bom.write_json(args.output)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"wrote {output_path}")
        return 0

    if args.command == "generate-sbom":
        try:
            inspection = inspect_apk(args.apk_path)
            match_summary = match_apk_to_reference_db(
                args.apk_path,
                db_path=args.db_path,
                coordinate=args.coordinate,
                top=args.top,
                min_score=args.min_score,
                enable_version_unique_literal_context_reranker=(
                    args.enable_version_unique_literal_context_reranker
                ),
                enable_composite_family_shortlist=args.enable_composite_family_shortlist,
                composite_family_shortlist_margin=args.composite_family_shortlist_margin,
            )
            components = detected_libraries_from_match_summary(
                match_summary,
                include_uncertain=args.include_uncertain,
            )
            bom = build_cyclonedx_bom(inspection, components)
            output_path = bom.write_json(args.output)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(f"wrote {output_path} with {len(components)} component(s)")
        return 0

    if args.command == "download-maven":
        try:
            libraries = load_libraries_config(args.config)
            artifacts = artifacts_from_libraries(
                libraries,
                repository_url=args.repository_url,
                packaging=args.packaging,
                coordinate=args.coordinate,
                limit=args.limit,
                offset=args.offset,
            )
            if args.dry_run:
                payload = [
                    {
                        "coordinate": artifact.coordinate,
                        "version": artifact.version,
                        "packaging": artifact.packaging,
                        "purl": artifact.purl,
                        "url": artifact.url,
                        "path": str(artifact.artifact_path(args.output_root)),
                        "metadata_path": str(artifact.metadata_path(args.output_root)),
                    }
                    for artifact in artifacts
                ]
                print(json.dumps(payload, indent=2, sort_keys=True))
                return 0

            results = download_artifacts(
                artifacts,
                output_root=args.output_root,
                timeout=args.timeout,
                force=args.force,
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        if args.quiet:
            print(json.dumps(_download_summary_payload(results), indent=2, sort_keys=True))
            return 1 if any(result.status == "failed" for result in results) else 0

        payload = [result.to_dict() for result in results]
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1 if any(result.status == "failed" for result in results) else 0

    if args.command == "expand-reference-config":
        try:
            summary = expand_reference_catalog(
                args.catalog,
                output_path=args.output,
                repository_url=args.repository_url,
                latest_count=args.latest_count,
                all_versions=args.all_versions,
                include_prerelease=args.include_prerelease,
                coordinate=args.coordinate,
                limit=args.limit,
                timeout=args.timeout,
                dry_run=args.dry_run,
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        if args.summary_output:
            summary.write_json(args.summary_output)
        if args.quiet:
            print(
                "expanded "
                f"{summary.selected_libraries}/{summary.total_entries} "
                f"libraries; failed={summary.failed}; output={summary.output_path}"
            )
        else:
            print(summary.to_json())
        return 1 if summary.failed else 0

    if args.command == "convert-reference-dex":
        try:
            records = discover_artifact_records(
                args.artifact_root,
                coordinate=args.coordinate,
                limit=args.limit,
                offset=args.offset,
            )
            if args.dry_run:
                payload = [planned_conversion(record, args.output_root) for record in records]
                print(json.dumps(payload, indent=2, sort_keys=True))
                return 0

            results = convert_reference_artifacts(
                records,
                output_root=args.output_root,
                d8_command=args.d8_command,
                min_api=args.min_api,
                timeout=args.timeout,
                force=args.force,
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        if args.quiet:
            print(json.dumps(_conversion_summary_payload(results), indent=2, sort_keys=True))
            return 1 if any(result.status == "failed" for result in results) else 0

        payload = [result.to_dict() for result in results]
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1 if any(result.status == "failed" for result in results) else 0

    if args.command == "extract-reference-features":
        try:
            conversions = discover_conversion_results(
                args.dex_root,
                coordinate=args.coordinate,
                limit=args.limit,
                offset=args.offset,
                include_skipped=args.include_skipped,
            )
            summary = extract_reference_features_to_db(
                conversions,
                db_path=args.db_path,
                reset=args.reset,
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        if args.quiet:
            print(json.dumps(_feature_summary_payload(summary), indent=2, sort_keys=True))
            return 1 if any(result.status == "failed" for result in summary.results) else 0

        print(summary.to_json())
        return 1 if any(result.status == "failed" for result in summary.results) else 0

    if args.command == "match-apk":
        try:
            summary = match_apk_to_reference_db(
                args.apk_path,
                db_path=args.db_path,
                coordinate=args.coordinate,
                top=args.top,
                min_score=args.min_score,
                package_weight=args.package_weight,
                class_weight=args.class_weight,
                method_weight=args.method_weight,
                opcode_weight=args.opcode_weight,
                dependency_weight=args.dependency_weight,
                literal_weight=args.literal_weight,
                unique_version_weight=args.unique_version_weight,
                api_reference_weight=args.api_reference_weight,
                opcode_ngram_weight=args.opcode_ngram_weight,
                enable_version_unique_literal_context_reranker=(
                    args.enable_version_unique_literal_context_reranker
                ),
                enable_composite_family_shortlist=args.enable_composite_family_shortlist,
                composite_family_shortlist_margin=args.composite_family_shortlist_margin,
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(summary.to_json())
        return 0

    if args.command == "scan-sbom-osv":
        try:
            libraries = load_detected_libraries_from_cyclonedx(args.sbom_path)
            summary = query_osv_for_libraries(
                libraries,
                api_url=args.api_url,
                timeout=args.timeout,
                enrich_vulnerabilities=not args.no_enrich,
            )
            output_path = summary.write_json(args.output)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(
            f"wrote {output_path} with {summary.vulnerabilities} vulnerability result(s) "
            f"across {summary.vulnerable_components} component(s) "
            f"({summary.confirmed_vulnerabilities} confirmed, "
            f"{summary.potential_vulnerabilities} potential)"
        )
        return 0

    if args.command == "generate-report":
        try:
            artifacts = generate_final_report(
                args.apk_path,
                output_dir=args.output_dir,
                db_path=args.db_path,
                coordinate=args.coordinate,
                top=args.top,
                min_score=args.min_score,
                api_reference_weight=args.api_reference_weight,
                opcode_ngram_weight=args.opcode_ngram_weight,
                enable_version_unique_literal_context_reranker=(
                    args.enable_version_unique_literal_context_reranker
                ),
                enable_composite_family_shortlist=args.enable_composite_family_shortlist,
                composite_family_shortlist_margin=args.composite_family_shortlist_margin,
                enable_reference_package_prefilter=args.enable_reference_package_prefilter,
                reference_package_prefilter_min_overlap=args.reference_package_prefilter_min_overlap,
                reference_package_prefilter_limit=args.reference_package_prefilter_limit,
                reference_package_prefilter_per_coordinate_limit=(
                    args.reference_package_prefilter_per_coordinate_limit
                ),
                include_uncertain=args.include_uncertain,
                query_osv=not args.skip_osv,
                osv_api_url=args.osv_api_url,
                timeout=args.timeout,
                enrich_vulnerabilities=not args.no_enrich,
                source_validation_json=args.source_validation_json,
                r8_phase5_experiment_json=(
                    args.r8_phase5_experiment_json
                    if args.include_r8_phase5_experiment
                    else None
                ),
                version_band_experiment_json=(
                    args.version_band_experiment_json
                    if args.include_version_band_experiments
                    else None
                ),
                lifecycle_family_experiment_json=(
                    args.lifecycle_family_experiment_json
                    if args.include_version_band_experiments
                    else None
                ),
                r8_minified_confidence_policy_json=(
                    args.r8_minified_confidence_policy_json
                    if args.include_r8_minified_confidence_policy
                    else None
                ),
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(artifacts.to_json())
        return 0

    if args.command == "r8-phase5-experiment":
        try:
            payload = build_r8_phase5_payload(Path(args.phase4_json))
            result = write_r8_phase5_outputs(
                payload,
                output_json=Path(args.output_json),
                output_doc=None if args.json_only else Path(args.output_doc),
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "version-band-experiment":
        try:
            payload = build_version_band_payload(Path(args.input_json))
            result = write_version_band_outputs(
                payload,
                output_json=Path(args.output_json),
                output_doc=Path(args.output_doc),
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "lifecycle-family-experiment":
        try:
            payload = build_lifecycle_family_payload(Path(args.input_json))
            result = write_lifecycle_family_outputs(
                payload,
                output_json=Path(args.output_json),
                output_doc=Path(args.output_doc),
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "no-maven-androidx-experiment":
        try:
            payload = build_no_maven_androidx_payload(Path(args.input_json))
            result = write_no_maven_androidx_outputs(
                payload,
                output_json=Path(args.output_json),
                output_doc=Path(args.output_doc),
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "no-maven-fork-family-experiment":
        try:
            payload = build_no_maven_fork_family_payload(Path(args.input_json))
            result = write_no_maven_fork_family_outputs(
                payload,
                output_json=Path(args.output_json),
                output_doc=Path(args.output_doc),
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "literal-context-experiment":
        try:
            payload = build_literal_context_payload(Path(args.input_json))
            result = write_literal_context_outputs(
                payload,
                output_json=Path(args.output_json),
                output_doc=Path(args.output_doc),
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "version-unique-literal-context-experiment":
        try:
            payload = build_version_unique_literal_context_payload(
                phase4_json=Path(args.phase4_json),
                reference_db=Path(args.reference_db),
            )
            result = write_version_unique_literal_context_outputs(
                payload,
                output_json=Path(args.output_json),
                output_doc=Path(args.output_doc),
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "validate-source-deps":
        try:
            extra_candidates = [
                parse_maven_component_spec(candidate)
                for candidate in args.candidate
            ]
            artifacts = write_source_validation_report(
                args.sbom,
                args.dependency_tree,
                output_dir=args.output_dir,
                extra_candidates=extra_candidates,
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(artifacts.to_json())
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


def _download_summary_payload(results) -> dict:
    statuses = Counter(result.status for result in results)
    return {
        "total": len(results),
        "statuses": dict(sorted(statuses.items())),
        "failed": [
            {
                "coordinate": result.artifact.coordinate,
                "version": result.artifact.version,
                "error": result.error,
            }
            for result in results
            if result.status == "failed"
        ],
    }


def _conversion_summary_payload(results) -> dict:
    statuses = Counter(result.status for result in results)
    return {
        "total": len(results),
        "statuses": dict(sorted(statuses.items())),
        "failed": [
            {
                "coordinate": result.coordinate,
                "version": result.version,
                "error": result.error,
            }
            for result in results
            if result.status == "failed"
        ],
        "skipped": [
            {
                "coordinate": result.coordinate,
                "version": result.version,
                "error": result.error,
            }
            for result in results
            if result.status == "skipped"
        ],
    }


def _feature_summary_payload(summary) -> dict:
    statuses = Counter(result.status for result in summary.results)
    return {
        "db_path": summary.db_path,
        "components": summary.components,
        "dex_files": summary.dex_files,
        "packages": summary.packages,
        "classes": summary.classes,
        "methods": summary.methods,
        "opcodes": summary.opcodes,
        "opcode_ngrams": summary.opcode_ngrams,
        "class_dependencies": summary.class_dependencies,
        "dependency_shapes": summary.dependency_shapes,
        "string_literals": summary.string_literals,
        "api_references": summary.api_references,
        "basic_block_opcode_fingerprints": summary.basic_block_opcode_fingerprints,
        "call_chain_opcode_fingerprints": summary.call_chain_opcode_fingerprints,
        "class_neighbor_summaries": summary.class_neighbor_summaries,
        "field_operation_sequences": summary.field_operation_sequences,
        "literal_context_features": summary.literal_context_features,
        "processed": len(summary.results),
        "statuses": dict(sorted(statuses.items())),
        "failed": [
            {
                "coordinate": result.coordinate,
                "version": result.version,
                "error": result.error,
            }
            for result in summary.results
            if result.status == "failed"
        ],
    }


if __name__ == "__main__":
    raise SystemExit(main())
