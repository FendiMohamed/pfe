from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


DEFAULT_INVENTORY = Path("data/results/evaluation/apk-testset-inventory.json")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/apk-type-evaluation.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/APK_TYPE_EVALUATION.md")


@dataclass(frozen=True)
class RealCase:
    case_id: str
    name: str
    role: str
    tags: tuple[str, ...]
    expected_difficulty: str
    report_path: str | None = None
    validation_path: str | None = None
    proof_path: str | None = None
    interpretation: str = ""
    next_improvement: str = ""
    validation_note: str | None = None


@dataclass(frozen=True)
class GroupSpec:
    group_id: str
    name: str
    expected_difficulty: str
    interpretation: str
    next_improvement: str
    real_case_ids: tuple[str, ...] = ()
    controlled_filter: Callable[[dict[str, Any]], bool] | None = None


REAL_CASES: tuple[RealCase, ...] = (
    RealCase(
        case_id="fdroid",
        name="F-Droid 1.23.2",
        role="clean-source-validated",
        tags=("real", "clean", "source-validated", "androidx-kmp", "multidex"),
        expected_difficulty="Medium: real multidex Android app, but covered by calibrated source-used references.",
        report_path="data/results/experiments/app-era-coherence-runtime-only/report-real-fdroid/report.json",
        validation_path="data/results/experiments/app-era-coherence-runtime-only/source-validation/fdroid/source-validation.json",
        proof_path="docs/evaluation/MVP_RESULTS_SUMMARY.md",
        interpretation="Clean case: source calibration gives exact emitted Maven versions.",
        next_improvement="Keep as the stable supervisor demo and negative OSV control.",
    ),
    RealCase(
        case_id="opentracks",
        name="OpenTracks 4.27.0irreproducible",
        role="clean-source-validated",
        tags=("real", "clean", "source-validated", "multidex", "no-native"),
        expected_difficulty="Medium: modern real APK with multidex and no native libraries.",
        report_path="data/results/experiments/app-era-coherence-runtime-only/report-real-opentracks/report.json",
        validation_path="data/results/experiments/app-era-coherence-runtime-only/source-validation/opentracks/source-validation.json",
        proof_path="docs/evaluation/OPENTRACKS_PROOF_BUNDLE.md",
        interpretation="Clean case: shared calibrated DB preserves exact source versions.",
        next_improvement="Use as a regression guard for future scorer changes.",
    ),
    RealCase(
        case_id="tusky",
        name="Tusky 32.2",
        role="clean-source-validated",
        tags=("real", "clean", "source-validated", "sparse-maven", "native"),
        expected_difficulty="Low for emitted Maven count, but useful because it is a real APK with many native files.",
        report_path="data/results/experiments/app-era-coherence-runtime-only/report-real-tusky/report.json",
        validation_path="data/results/experiments/app-era-coherence-runtime-only/source-validation/tusky/source-validation.json",
        proof_path="docs/evaluation/REAL_APK_CURRENT_BATCH_RESULTS.md",
        interpretation="Clean but sparse: exact result is useful, yet it should not dominate the accuracy story.",
        next_improvement="Keep it as a clean sparse class, not as proof that all real APKs are easy.",
    ),
    RealCase(
        case_id="daily-dozen",
        name="Daily Dozen 28",
        role="clean-source-validated",
        tags=("real", "clean", "source-validated", "sparse-maven", "no-native", "health"),
        expected_difficulty="Low for emitted Maven count, but useful as another clean no-native real APK with source-resolved dependency evidence.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-daily-dozen/report.json",
        validation_path="data/results/source-validation/csv4/daily-dozen/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V4.md",
        interpretation="Clean but sparse: both emitted Maven components validate exactly, but the row does not close the non-sparse clean bucket.",
        next_improvement="Keep as clean sparse no-native evidence while continuing to search for a clean non-sparse app.",
        validation_note="Docker Gradle captured `:app` `fdroidReleaseRuntimeClasspath`; validation confirms 2/2 emitted Maven versions, with 0 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="cryptomator-lite",
        name="Cryptomator Lite 1.12.3",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "androidx", "kotlin", "gradle-8.13"),
        expected_difficulty="High: modern no-native AndroidX/Kotlin app with many near-version ties.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-cryptomator-lite/report.json",
        validation_path="data/results/source-validation/csv4/cryptomator-lite/source-validation-gradle8.13/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V4.md",
        interpretation="Gradle 8.13 unblocked the source dependency tree; identity recovery is strong, but version selection remains partial.",
        next_improvement="Use as no-native partial evidence for future version-disambiguation work, not as a clean accuracy row.",
        validation_note="Docker Gradle 8.13 captured `:presentation` `liteReleaseRuntimeClasspath`; validation confirms 13/24 emitted Maven versions, with 11 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="easy-xkcd",
        name="Easy Xkcd 8.4",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "androidx", "legacy-jcenter", "gradle-8.13"),
        expected_difficulty="High: no-native app with old repository configuration and AndroidX version-band drift.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-easy-xkcd/report.json",
        validation_path="data/results/source-validation/csv4/easy-xkcd/source-validation-gradle8.13-validation-copy/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V4.md",
        interpretation="A validation-only JCenter URL replacement plus Gradle 8.13 produced source evidence; most coordinates are present but many selected versions are newer than source.",
        next_improvement="Keep as partial no-native evidence and avoid treating validation-only repository edits as APK/source behavior changes.",
        validation_note="Docker Gradle 8.13 captured `:app` `fdroidReleaseRuntimeClasspath` from the validation-only JCenter URL copy; validation confirms 6/23 emitted Maven versions, with 17 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="moneywallet",
        name="MoneyWallet 4.0.5.10",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "older-dependency-profile", "legacy-gradle", "jdk11"),
        expected_difficulty="High: older AndroidX-era app requiring a validation-only JCenter URL copy plus JDK 11 and Gradle 6.1.1.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-moneywallet/report.json",
        validation_path="data/results/source-validation/csv4/moneywallet/source-validation-gradle6.1.1-jdk11-validation-copy/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V4.md",
        interpretation="The legacy validation lane resolves the source dependency tree, but most emitted versions are newer than source and one coordinate is missing.",
        next_improvement="Use as older-toolchain rescue evidence and keep it partial unless source-version coverage can improve without current-control regressions.",
        validation_note="Docker JDK 11 plus Gradle 6.1.1 captured `:app` `flossOsmReleaseRuntimeClasspath` from the validation-only JCenter URL copy; validation confirms 2/9 emitted Maven versions, with 6 mismatches and 1 missing coordinate.",
    ),
    RealCase(
        case_id="privacy-browser",
        name="Privacy Browser 3.20.1",
        role="source-validated-no-maven-signal",
        tags=("real", "source-validated", "no-maven-signal", "clean-candidate", "no-native", "browser", "security", "gradle-9.5"),
        expected_difficulty="Operationally modern no-native browser/security app, but the current APK report emits no Maven components.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-privacy-browser/report.json",
        validation_path="data/results/source-validation/csv4/privacy-browser/source-validation-gradle9.5/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V4.md",
        interpretation="Successful source/dependency/report proof, but it should be treated as a no-signal control rather than source-validated accuracy evidence.",
        next_improvement="Keep as no-native browser/security no-signal evidence unless future extraction emits Maven components.",
        validation_note="Docker installed Android platform 36 in the validation container and Gradle 9.5 captured `:app` `standardReleaseRuntimeClasspath`; validation is 0/0 because the report emits no Maven components while the source tree resolves 87 Maven components.",
    ),
    RealCase(
        case_id="quickdic",
        name="QuickDic 5.8.2",
        role="clean-source-validated",
        tags=("real", "clean", "source-validated", "sparse-maven", "no-native", "dictionary", "gradle-8.14.3"),
        expected_difficulty="Low for emitted Maven count, but useful as a no-native root-project clean control.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-quickdic/report.json",
        validation_path="data/results/source-validation/csv5/quickdic/source-validation-gradle8.14.3/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V5.md",
        interpretation="Clean but sparse: both emitted Maven components validate exactly from a resolved root-project dependency tree.",
        next_improvement="Keep as clean sparse no-native evidence while continuing to search for a clean non-sparse app.",
        validation_note="Docker Gradle 8.14.3 captured root `releaseRuntimeClasspath`; validation confirms 2/2 emitted Maven versions, with 0 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="cirrus",
        name="Cirrus 4.7",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "weather", "multidex", "gradle-8.13"),
        expected_difficulty="Medium: modern no-native weather app with multidex and a broad AndroidX runtime tree.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-cirrus/report.json",
        validation_path="data/results/source-validation/csv5/cirrus/source-validation-gradle8.13/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V5.md",
        interpretation="Strong identity recovery with five version mismatches; useful no-native multidex evidence.",
        next_improvement="Keep as partial evidence and investigate scoped version disambiguation without broad recency bias.",
        validation_note="Docker Gradle 8.13 captured `:app` `releaseRuntimeClasspath`; validation confirms 14/19 emitted Maven versions, with 5 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="afwall-plus",
        name="AFWall+ 4.0.3",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "security", "firewall", "multidex", "gradle-8.13"),
        expected_difficulty="Medium: security/firewall app with multidex and older plus modern Android dependency families.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-afwall-plus/report.json",
        validation_path="data/results/source-validation/csv5/afwall-plus/source-validation-gradle8.13/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V5.md",
        interpretation="Useful security-app partial row: coordinate recovery is strong, while six versions remain mismatched.",
        next_improvement="Keep as partial security evidence and preserve source-resolved older versions during future calibration tests.",
        validation_note="Docker Gradle 8.13 captured `:app` `releaseRuntimeClasspath`; validation confirms 12/18 emitted Maven versions, with 6 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="loop-habit-tracker",
        name="Loop Habit Tracker 2.3.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "modular", "kotlin", "gradle-8.14.3"),
        expected_difficulty="Medium: modular Kotlin project requiring the Android application module dependency tree.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-loop-habit-tracker/report.json",
        validation_path="data/results/source-validation/csv5/loop-habit-tracker/source-validation-gradle8.14.3/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V5.md",
        interpretation="Module-specific Gradle proof resolves cleanly; version selection remains partial on four emitted components.",
        next_improvement="Keep as modular no-native evidence and retain module-specific proof commands in the artifact trail.",
        validation_note="Docker Gradle 8.14.3 captured `:uhabits-android` `releaseRuntimeClasspath`; validation confirms 7/11 emitted Maven versions, with 4 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="yetcalc",
        name="yetCalc 2.0.8",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "calculator", "education", "multidex", "gradle-8.13"),
        expected_difficulty="Medium: modern no-native Kotlin calculator app with multidex and version-catalog dependencies.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-yetcalc/report.json",
        validation_path="data/results/source-validation/csv5/yetcalc/source-validation-gradle8.13/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V5.md",
        interpretation="The report recovers many coordinates, but version drift remains substantial across the modern dependency tree.",
        next_improvement="Use as partial modern-Kotlin evidence and avoid forcing broad newer-version selection rules.",
        validation_note="Docker Gradle 8.13 captured `:app` `releaseRuntimeClasspath`; validation confirms 6/17 emitted Maven versions, with 11 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="broccoli",
        name="Broccoli 1.4.4",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "recipe-manager", "health", "multidex", "gradle-8.13"),
        expected_difficulty="Medium: no-native recipe/health app with multidex and a large source-resolved dependency tree.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-broccoli/report.json",
        validation_path="data/results/source-validation/csv6/broccoli/source-validation-gradle8.13/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V6.md",
        interpretation="Useful v6 partial row: the source tree resolves broadly, but nine emitted versions remain mismatched.",
        next_improvement="Keep as partial no-native health/recipe evidence and use it for future scoped version-disambiguation checks.",
        validation_note="Docker Gradle 8.13 captured `:app` `fdroidReleaseRuntimeClasspath`; validation confirms 11/20 emitted Maven versions, with 9 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="libretube",
        name="LibreTube 31.4",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "internet", "media", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: modern internet/media app with multidex, JitPack dependencies, and a large source tree.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-libretube/report.json",
        validation_path="data/results/source-validation/csv6/libretube/source-validation-gradle9.5/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V6.md",
        interpretation="Strong partial row: most emitted versions validate, but four modern media/networking versions remain mismatched.",
        next_improvement="Use as a no-native internet/media stress row for future guarded reference coverage experiments.",
        validation_note="Docker Gradle 9.5 captured `:app` `releaseRuntimeClasspath`; validation confirms 9/13 emitted Maven versions, with 4 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="retro-music",
        name="Retro Music 6.6.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "media", "kotlin", "gradle-8.14.3"),
        expected_difficulty="Medium: no-native Kotlin media app with an app module plus theme-helper module.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-retro-music/report.json",
        validation_path="data/results/source-validation/csv6/retro-music/source-validation-gradle8.14.3/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V6.md",
        interpretation="Small but useful media partial row: four of six emitted Maven versions validate exactly.",
        next_improvement="Keep as partial media evidence; the low emitted count means it should not be used as broad recall evidence.",
        validation_note="Docker Gradle 8.14.3 captured `:app` `fdroidReleaseRuntimeClasspath`; validation confirms 4/6 emitted Maven versions, with 2 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="micromathematics-plus",
        name="microMathematics Plus 2.23.3",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "calculator", "science-education", "multidex", "gradle-8.13"),
        expected_difficulty="Medium: no-native science/calculator app with multidex and older plus modern dependency families.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-micromathematics-plus/report.json",
        validation_path="data/results/source-validation/csv6/micromathematics-plus/source-validation-gradle8.13/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V6.md",
        interpretation="The APK emits a non-sparse SBOM, but exact version selection is poor on this dependency profile.",
        next_improvement="Use as partial calculator/science evidence and avoid broad scorer changes from this row alone.",
        validation_note="Docker Gradle 8.13 captured `:app` `releaseRuntimeClasspath`; validation confirms 4/16 emitted Maven versions, with 12 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="diaguard",
        name="Diaguard 3.15.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "health", "r8-minified", "gradle-8.13"),
        expected_difficulty="Medium: no-native health diary app whose release build enables minification.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-diaguard/report.json",
        validation_path="data/results/source-validation/csv6/diaguard/source-validation-gradle8.13/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V6.md",
        interpretation="Small source-validated partial row with real release-minify evidence; useful for the real R8/minified bucket.",
        next_improvement="Keep as partial no-native R8/minified evidence and do not treat it as clean accuracy evidence.",
        validation_note="Docker Gradle 8.13 captured `:app` `demoReleaseRuntimeClasspath`; validation confirms 2/5 emitted Maven versions, with 3 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="fulguris-web-browser",
        name="Fulguris Web Browser 2.0.10",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "browser", "internet", "multidex", "gradle-8.14.3"),
        expected_difficulty="High: no-native browser app with multiple flavor dimensions and a large AndroidX-heavy source tree.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-fulguris-web-browser/report.json",
        validation_path="data/results/source-validation/csv7/fulguris-web-browser/source-validation-gradle8.14.3/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V7.md",
        interpretation="Strong browser-family partial row: identity recovery is broad, while four emitted versions still mismatch source.",
        next_improvement="Keep as richer browser evidence and use it for future scoped version-disambiguation work rather than broad scorer changes.",
        validation_note="Docker Gradle 8.14.3 captured `:app` `slionsFullFdroidReleaseRuntimeClasspath`; validation confirms 17/21 emitted Maven versions, with 4 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="working-time-account",
        name="Working Time Account 2.11.012",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "money", "time", "gradle-9.5"),
        expected_difficulty="Medium: no-native modern work/time app with a medium dependency tree and current AndroidX stack.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-working-time-account/report.json",
        validation_path="data/results/source-validation/csv7/working-time-account/source-validation-gradle9.5/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V7.md",
        interpretation="Near-clean partial row: most emitted versions validate, but three coordinates still drift from source.",
        next_improvement="Use as a promising no-native work/time row for guarded source-version triage, not as clean evidence yet.",
        validation_note="Docker Gradle 9.5 captured `:app` `releaseRuntimeClasspath`; validation confirms 12/15 emitted Maven versions, with 3 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="andstatus",
        name="AndStatus 62.03",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "internet", "social-network", "gradle-8.13"),
        expected_difficulty="Medium: no-native social/internet app with older plus modern AndroidX and networking dependencies.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-andstatus/report.json",
        validation_path="data/results/source-validation/csv7/andstatus/source-validation-gradle8.13/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V7.md",
        interpretation="Useful richer social/internet partial row with seven version mismatches remaining.",
        next_improvement="Keep as partial social/internet evidence and preserve the explicit mismatches in thesis-facing reporting.",
        validation_note="Docker Gradle 8.13 captured `:app` `releaseRuntimeClasspath`; validation confirms 12/19 emitted Maven versions, with 7 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="i2p",
        name="I2P 2.11.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "security", "internet", "vpn-proxy", "multidex", "gradle-8.13"),
        expected_difficulty="High: no-native security/networking app with legacyRelease flavor selection and mixed old/new dependency families.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-i2p/report.json",
        validation_path="data/results/source-validation/csv7/i2p/source-validation-gradle8.13/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V7.md",
        interpretation="Security-family partial row: useful coordinate recovery, but eight emitted versions still mismatch source.",
        next_improvement="Keep as partial security evidence and avoid hiding its older/newer version drift.",
        validation_note="Docker Gradle 8.13 captured `:app` `legacyReleaseRuntimeClasspath`; validation confirms 10/18 emitted Maven versions, with 8 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="mastodon",
        name="Mastodon 2.12.3",
        role="source-validated-no-maven-signal",
        tags=("real", "source-validated", "no-maven-signal", "clean-candidate", "no-native", "internet", "social-network", "gradle-8.13"),
        expected_difficulty="Operationally modern no-native social app, but the current APK report emits no Maven components.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-mastodon/report.json",
        validation_path="data/results/source-validation/csv7/mastodon/source-validation-gradle8.13/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V7.md",
        interpretation="Successful source/dependency/report proof, but it is another no-Maven-signal control rather than accuracy evidence.",
        next_improvement="Keep as no-native social no-signal evidence unless future extraction emits Maven components.",
        validation_note="Docker Gradle 8.13 captured `:mastodon` `releaseRuntimeClasspath`; validation is 0/0 because the report emits no Maven components while the source tree resolves 20 Maven components.",
    ),
    RealCase(
        case_id="drift-audio",
        name="Drift // Audio 0.1.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "multimedia", "gradle-8.13"),
        expected_difficulty="Medium: no-native modern multimedia app with a compact APK but a non-trivial AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-drift-audio/report.json",
        validation_path="data/results/source-validation/csv8/drift-audio/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V8.md",
        interpretation="Useful multimedia partial row: the APK emits a non-sparse SBOM, but several selected versions still drift from source.",
        next_improvement="Keep as partial no-native multimedia evidence and preserve the explicit mismatch count in thesis-facing reporting.",
        validation_note="Docker Gradle 8.13 captured `:app` `releaseRuntimeClasspath`; validation confirms 7/13 emitted Maven versions, with 6 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="jamuz",
        name="JaMuz 0.6.14",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "internet", "multimedia", "multidex", "gradle-8.13"),
        expected_difficulty="Medium: no-native media/internet app with multidex and a broader dependency tree than the sparse clean rows.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-jamuz/report.json",
        validation_path="data/results/source-validation/csv8/jamuz/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V8.md",
        interpretation="Strong no-native partial row: broad coordinate recovery with seven remaining version mismatches.",
        next_improvement="Keep as richer media/internet evidence and use it for future guarded version-disambiguation checks rather than broad scorer changes.",
        validation_note="Docker Gradle 8.13 captured `:app` `releaseRuntimeClasspath`; validation confirms 14/21 emitted Maven versions, with 7 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="monocles-browser",
        name="monocles browser 1.9.3",
        role="source-validated-no-maven-signal",
        tags=("real", "source-validated", "no-maven-signal", "clean-candidate", "no-native", "browser", "internet", "gradle-8.13"),
        expected_difficulty="Operationally modern no-native browser app with a large source tree, but the current APK report emits no Maven components.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-monocles-browser/report.json",
        validation_path="data/results/source-validation/csv8/monocles-browser/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V8.md",
        interpretation="Successful source/dependency/report proof, but it is another no-Maven-signal browser control rather than accuracy evidence.",
        next_improvement="Keep as no-native browser no-signal evidence unless future extraction emits Maven components.",
        validation_note="Docker Gradle 8.13 captured `:app` `standardReleaseRuntimeClasspath`; validation is 0/0 because the report emits no Maven components while the source tree resolves a runtime dependency graph.",
    ),
    RealCase(
        case_id="newpipe",
        name="NewPipe 0.28.5",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "modern-androidx", "multidex", "native"),
        expected_difficulty="High: modern AndroidX/Kotlin media app with version-band ties.",
        report_path="data/results/experiments/app-era-coherence-runtime-only/report-real-newpipe/report.json",
        validation_path="data/results/experiments/app-era-coherence-runtime-only/source-validation/newpipe/source-validation.json",
        proof_path="docs/evaluation/REAL_APK_CURRENT_BATCH_RESULTS.md",
        interpretation="Good identity recovery, but version ties remain; this is a partial result, not a failure.",
        next_improvement="Investigate scoped per-coordinate evidence for Startup and Lifecycle without regressing Aegis.",
        validation_note="Earlier saved proof-bundle validation was 10/11; the fresh current-control matrix is used here and is 9/11.",
    ),
    RealCase(
        case_id="antennapod",
        name="AntennaPod 3.11.4",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "modern-androidx", "multidex", "native"),
        expected_difficulty="High: real media app with AndroidX near-version evidence.",
        report_path="data/results/experiments/app-era-coherence-runtime-only/report-real-antennapod/report.json",
        validation_path="data/results/experiments/app-era-coherence-runtime-only/source-validation/antennapod/source-validation.json",
        proof_path="docs/evaluation/ANTENNAPOD_PROOF_BUNDLE.md",
        interpretation="Strong partial case; one AndroidX Core near-tie remains after calibration.",
        next_improvement="Prefer independent evidence over a generic newer-version rule.",
    ),
    RealCase(
        case_id="kde-connect",
        name="KDE Connect 1.35.5",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "androidx", "multidex", "native"),
        expected_difficulty="High: AndroidX and target-variant ambiguity with native files.",
        report_path="data/results/experiments/app-era-coherence-runtime-only/report-real-kde-connect/report.json",
        validation_path="data/results/experiments/app-era-coherence-runtime-only/source-validation/kde-connect/source-validation.json",
        proof_path="docs/evaluation/KDE_CONNECT_PROOF_BUNDLE.md",
        interpretation="Lifecycle coherence helped, but ViewPager2 beta remains unsafe to force globally.",
        next_improvement="Keep ViewPager2 beta as a documented risky tie unless a non-regressing rule appears.",
    ),
    RealCase(
        case_id="wikipedia",
        name="Wikipedia Android r/50586",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "modern-androidx", "multidex", "native"),
        expected_difficulty="High: non-sparse app with AndroidX, OkHttp Android target artifact, and native MapLibre files.",
        report_path="data/results/experiments/app-era-coherence-runtime-only/report-real-wikipedia-android/report.json",
        validation_path="data/results/experiments/app-era-coherence-runtime-only/source-validation/wikipedia-android/source-validation.json",
        proof_path="docs/evaluation/WIKIPEDIA_ANDROID_PROOF_BUNDLE.md",
        interpretation="Useful modern partial case; Startup and ViewPager2 remain near-version limitations.",
        next_improvement="Use it to evaluate any future version-band reranker.",
    ),
    RealCase(
        case_id="conversations",
        name="Conversations 2.20.0+free",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "r8-minified", "messaging", "native"),
        expected_difficulty="High: messaging/security app with R8/minify, multidex, and AndroidX ties.",
        report_path="data/results/experiments/app-era-coherence-runtime-only/report-real-conversations/report.json",
        validation_path="data/results/experiments/app-era-coherence-runtime-only/source-validation/conversations/source-validation.json",
        proof_path="docs/evaluation/CONVERSATIONS_PROOF_BUNDLE.md",
        interpretation="Good hard-case evidence: Gson calibration helped, AndroidX near-ties remain.",
        next_improvement="Preserve the artifact-family nuance separately from simple version errors.",
    ),
    RealCase(
        case_id="aegis",
        name="Aegis Authenticator 3.4.2",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "security", "androidx", "native"),
        expected_difficulty="High: security app with small native barcode libraries and AndroidX ties.",
        report_path="data/results/experiments/app-era-coherence-runtime-only/report-real-aegis-authenticator/report.json",
        validation_path="data/results/experiments/app-era-coherence-runtime-only/source-validation/aegis-authenticator/source-validation.json",
        proof_path="docs/evaluation/AEGIS_AUTHENTICATOR_PROOF_BUNDLE.md",
        interpretation="Important regression guard because a generic newer Lifecycle rule would hurt this case.",
        next_improvement="Use it to reject over-broad recency heuristics.",
    ),
    RealCase(
        case_id="markor",
        name="Markor 2.16.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "older-dependency-profile", "multidex", "no-native"),
        expected_difficulty="High: older dependency stack creates drift against a shared calibrated DB.",
        report_path="data/results/report-real-markor/report.json",
        validation_path="data/results/source-validation/markor-report-validation/source-validation.json",
        proof_path="docs/evaluation/MARKOR_PROOF_BUNDLE.md",
        interpretation="Shows that narrowly guarded source-version coverage can help, while broader app-specific calibration may regress other apps globally.",
        next_improvement="Continue promoting only candidates that pass a fresh current-control matrix.",
        validation_note="The guarded core 1.9.0 promotion lifts the shared DB result to 7/19; the full source-specific experiment reached 19/19 but regressed other apps.",
    ),
    RealCase(
        case_id="nextcloud",
        name="Nextcloud Android 33.1.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "large-modern-tree", "compose", "kotlin", "native"),
        expected_difficulty="Very high: large modern AndroidX/Compose/Kotlin tree with version-band and artifact-family ambiguity.",
        report_path="data/results/experiments/app-era-coherence-runtime-only/report-real-nextcloud-android/report.json",
        validation_path="data/results/experiments/app-era-coherence-runtime-only/source-validation/nextcloud-android/source-validation.json",
        proof_path="docs/evaluation/NEXTCLOUD_ANDROID_PROOF_BUNDLE.md",
        interpretation="Major stress case; guarded promotions improve it without hiding remaining risky ties.",
        next_improvement="Continue only with changes that pass fresh controls across the full real-APK matrix.",
        validation_note="This is the fresh runtime-only current-control validation used by the shared-DB promotion check.",
    ),
    RealCase(
        case_id="vlc-android",
        name="VLC Android 3.7.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "native-heavy", "media", "multidex"),
        expected_difficulty="Very high: native-heavy media APK with six DEX files, large VLC native libraries, and an older dependency stack.",
        report_path="data/results/report-real-vlc-android/report.json",
        validation_path="data/results/source-validation/vlc-android-report-validation/source-validation.json",
        proof_path="docs/evaluation/VLC_ANDROID_PROOF_BUNDLE.md",
        interpretation="Strong hard-case evidence: identity coverage is broad, native files are hash-only, and many Maven versions differ from the shared DB.",
        next_improvement="Use VLC to prioritize source-version coverage diagnostics and native-boundary reporting, not a global version-recency rule.",
        validation_note="Dependency tree was generated from an in-container source extraction with F-Droid prebuild edits and a validation-only fixed Git revision string.",
    ),
    RealCase(
        case_id="osmand",
        name="OsmAnd~ 5.3.10",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "native-heavy", "maps", "multidex"),
        expected_difficulty="Very high: large maps APK with eight DEX files, Qt/OsmAnd native libraries, AndroidX/Kotlin dependencies, and F-Droid prebuild edits.",
        report_path="data/results/report-real-osmand/report.json",
        validation_path="data/results/source-validation/osmand-report-validation/source-validation.json",
        proof_path="docs/evaluation/OSMAND_PROOF_BUNDLE.md",
        interpretation="Strong maps/native stress case; many emitted versions validate, but source mismatches and native hash-only reporting keep it partial.",
        next_improvement="Use OsmAnd for source-version coverage diagnostics and scanner-triage caveats, not as a clean exact-version claim.",
        validation_note="Dependency tree was generated with validation-only F-Droid configuration edits and cached Gradle 8.10.2 because Gradle 9.5.0 breaks the source build script's XmlParser usage.",
    ),
    RealCase(
        case_id="material-files",
        name="Material Files 1.7.4",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "file-manager", "network-storage", "single-dex", "native"),
        expected_difficulty="High: file manager with SMB/SFTP/WebDAV/archive support, native JNI libraries, and AndroidX version-band drift.",
        report_path="data/results/report-real-material-files/report.json",
        validation_path="data/results/source-validation/material-files-report-validation/source-validation.json",
        proof_path="docs/evaluation/MATERIAL_FILES_PROOF_BUNDLE.md",
        interpretation="New file-manager/network-storage family case; APK identity evidence is sparse and both emitted AndroidX versions mismatch source-resolved versions.",
        next_improvement="Use it as a low-confidence AndroidX version-band and native-JNI boundary guard, not as a clean accuracy claim.",
        validation_note="Dependency tree was generated from a validation-only no-native source copy after applying F-Droid nonfree-source removal; Maven runtime dependency resolution is preserved, but native build output is not claimed.",
    ),
    RealCase(
        case_id="davx5",
        name="DAVx5 4.5.12-ose",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "sync-client", "modern-androidx", "multidex", "native"),
        expected_difficulty="High: modern sync client with Kotlin/AndroidX dependencies and native artifacts from the category-balanced smoke batch.",
        report_path="data/results/evaluation/real-apk-growth-batch-v2/report-real-davx5/report.json",
        validation_path="data/results/source-validation/real-apk-growth-batch-v2/davx5/source-validation/source-validation.json",
        proof_path="docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md",
        interpretation="Promoted from the 8-APK smoke batch into source-validated partial evidence; identity is useful, while Startup and Okio versions still mismatch source.",
        next_improvement="Use it as a modern sync-client guard for future AndroidX/Okio version-band work.",
        validation_note="The proof runner captured `:app-ose` `oseReleaseRuntimeClasspath`; source validation confirms 3/5 emitted Maven versions, with 2 mismatches and 0 missing.",
    ),
    RealCase(
        case_id="openvpn-for-android",
        name="OpenVPN for Android 0.7.64",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "native-heavy", "vpn-security", "multidex"),
        expected_difficulty="Very high: native-heavy VPN APK whose Java/Kotlin dependency tree requires a no-native validation copy in the Docker image.",
        report_path="data/results/evaluation/real-apk-growth-batch-v2/report-real-openvpn-for-android/report.json",
        validation_path="data/results/source-validation/real-apk-growth-batch-v2/openvpn-for-android/source-validation/source-validation.json",
        proof_path="docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md",
        interpretation="Useful security/native-heavy partial case; Maven identity evidence is helpful, while several AndroidX/library versions mismatch source.",
        next_improvement="Keep native libraries hash-only and use the Maven mismatches as version-band evidence, not as a native build claim.",
        validation_note="Dependency tree was generated from a validation copy with native CMake/NDK configuration disabled because the Docker image has no matching Android NDK; source validation confirms 13/20 emitted Maven versions, with 7 mismatches and 0 missing.",
    ),
    RealCase(
        case_id="gadgetbridge",
        name="Gadgetbridge 0.91.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "older-long-lived", "device-connectivity", "multidex", "native"),
        expected_difficulty="High: older long-lived device-connectivity APK with native files and broad AndroidX/library dependency surface.",
        report_path="data/results/evaluation/real-apk-growth-batch-v2/report-real-gadgetbridge/report.json",
        validation_path="data/results/source-validation/real-apk-growth-batch-v2/gadgetbridge/source-validation/source-validation.json",
        proof_path="docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md",
        interpretation="Strong partial device-connectivity case: many emitted Maven versions validate, but four AndroidX version mismatches remain.",
        next_improvement="Use it as an older/long-lived app guard for future version-band work.",
        validation_note="The proof runner derived the matching F-Droid source tarball URL, captured `:app` `mainlineReleaseRuntimeClasspath`, and confirms 17/21 emitted Maven versions, with 4 mismatches and 0 missing.",
    ),
    RealCase(
        case_id="shelter",
        name="Shelter 1.9.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "no-native", "security", "small-apk"),
        expected_difficulty="Medium: small no-native security/work-profile APK, but its F-Droid source tarball lacks complete Gradle project wiring for the bundled SetupWizardLibrary.",
        report_path="data/results/evaluation/real-apk-growth-batch-v2/report-real-shelter/report.json",
        validation_path="data/results/source-validation/real-apk-growth-batch-v2/shelter/source-validation/source-validation.json",
        proof_path="docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md",
        interpretation="Good no-native control for emitted Maven components; it stays partial because dependency resolution used a documented validation copy.",
        next_improvement="Use it as a compact no-native guard, but do not call it clean unless the unmodified source build can be resolved.",
        validation_note="Dependency tree was generated from a validation copy that adds missing settings.gradle, applies Docker Gradle compatibility edits, and omits incomplete SetupWizardLibrary project wiring; source validation confirms 3/3 emitted Maven versions.",
    ),
    RealCase(
        case_id="stopwatch",
        name="Stopwatch 1.6",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "low-risk", "no-native", "small-apk"),
        expected_difficulty="Low: small no-native Android app with modern Gradle project shape and quick runtime dependency-tree resolution.",
        report_path="data/results/evaluation/low-risk-real-apk-batch/report-real-stopwatch/report.json",
        validation_path="data/results/source-validation/low-risk-real-apk-batch/stopwatch/source-validation/source-validation.json",
        proof_path="docs/evaluation/LOW_RISK_REAL_APK_PROOF_STATUS.md",
        interpretation="Good low-risk proof candidate: the source and Gradle gates are stable, while one AndroidX version mismatch keeps it partial.",
        next_improvement="Use as a cheap no-native regression guard for future source-version calibration.",
        validation_note="Selected by preflight after source tarball, no-native, modern Gradle, declared dependency, and quick dependency-tree checks; validation confirms 4/5 emitted Maven versions.",
    ),
    RealCase(
        case_id="bubble",
        name="Bubble 3.4",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "low-risk", "no-native", "small-apk"),
        expected_difficulty="Low-to-medium: small no-native utility app with modern Gradle, but older/source-specific dependency versions.",
        report_path="data/results/evaluation/low-risk-real-apk-batch/report-real-bubble/report.json",
        validation_path="data/results/source-validation/low-risk-real-apk-batch/bubble/source-validation/source-validation.json",
        proof_path="docs/evaluation/LOW_RISK_REAL_APK_PROOF_STATUS.md",
        interpretation="Operationally reliable candidate; useful because mismatches appear without native/framework blockers.",
        next_improvement="Treat the mismatches as source-version coverage evidence, not as APK selection failure.",
        validation_note="Selected by preflight after source tarball, no-native, modern Gradle, declared dependency, and quick dependency-tree checks; validation confirms 1/7 emitted Maven versions.",
    ),
    RealCase(
        case_id="audio-source",
        name="Audio Source 1.5",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "low-risk", "no-native", "small-apk"),
        expected_difficulty="Low-to-medium: small no-native Android app with modern Gradle and a compact dependency surface.",
        report_path="data/results/evaluation/low-risk-real-apk-batch/report-real-audio-source/report.json",
        validation_path="data/results/source-validation/low-risk-real-apk-batch/audio-source/source-validation/source-validation.json",
        proof_path="docs/evaluation/LOW_RISK_REAL_APK_PROOF_STATUS.md",
        interpretation="Reliable run/test candidate; all emitted Maven components are currently version mismatches, making it useful for calibration evidence.",
        next_improvement="Use as a compact AndroidX/source-version mismatch control.",
        validation_note="Selected by preflight after source tarball, no-native, modern Gradle, declared dependency, and quick dependency-tree checks; validation confirms 0/3 emitted Maven versions.",
    ),
    RealCase(
        case_id="blue-square-speedometer",
        name="Blue Square Speedometer 1.1.0",
        role="source-validated-no-maven-signal",
        tags=("real", "source-validated", "no-maven-signal", "low-risk", "no-native", "small-apk"),
        expected_difficulty="Low operational difficulty, but the current APK report emits no Maven components.",
        report_path="data/results/evaluation/low-risk-real-apk-batch/report-real-blue-square-speedometer/report.json",
        validation_path="data/results/source-validation/low-risk-real-apk-batch/blue-square-speedometer/source-validation/source-validation.json",
        proof_path="docs/evaluation/LOW_RISK_REAL_APK_PROOF_STATUS.md",
        interpretation="Successful source/build/report proof, but it should be treated as a no-signal control rather than source-validated accuracy evidence.",
        next_improvement="Keep only as a quick smoke/control candidate unless future extraction emits Maven evidence.",
        validation_note="Selected by preflight and passes source/dependency/report gates; validation is 0/0 because the report emits no Maven components.",
    ),
    RealCase(
        case_id="gotify",
        name="Gotify 2.10.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "modern-androidx", "multidex"),
        expected_difficulty="Medium-high: no native libraries and modern source, but a broad AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-gotify/report.json",
        validation_path="data/results/source-validation/clean-real-apk-candidate-sweep-v2/gotify/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS.md",
        interpretation="Useful non-sparse no-native evidence, but source validation shows broad version-band drift.",
        next_improvement="Use as a modern no-native guard for future version-band/reference-coverage experiments.",
        validation_note="Docker Gradle captured `:app` `releaseRuntimeClasspath`; validation confirms 11/23 emitted Maven versions, with 11 mismatches and 1 missing coordinate.",
    ),
    RealCase(
        case_id="foxy-droid",
        name="Foxy Droid 1.3",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "legacy-gradle", "jdk11", "older-dependency-profile"),
        expected_difficulty="High: older no-native app requiring a validation-only JCenter URL copy, local SDK path adaptation, JDK 11, and Gradle 5.1.1.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep/report-real-foxy-droid/report.json",
        validation_path="data/results/source-validation/clean-real-apk-candidate-sweep/foxy-droid/source-validation-gradle5.1.1-jdk11-validation-copy/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS.md",
        interpretation="The legacy validation lane resolves the source dependency tree, but only one emitted version validates exactly and one coordinate is missing.",
        next_improvement="Use as older-toolchain no-native evidence and as a guard against overclaiming latest AndroidX/OkHttp versions.",
        validation_note="Docker JDK 11 plus Gradle 5.1.1 captured root `releaseRuntimeClasspath` from the validation-only JCenter URL and SDK-path copy; validation confirms 1/6 emitted Maven versions, with 4 mismatches and 1 missing coordinate.",
    ),
    RealCase(
        case_id="bettercounter",
        name="BetterCounter 6.0.3",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "kde-utility"),
        expected_difficulty="Low-to-medium: compact no-native utility with low-confidence AndroidX candidates.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-bettercounter/report.json",
        validation_path="data/results/source-validation/clean-real-apk-candidate-sweep-v2/bettercounter/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS.md",
        interpretation="Compact source-validated partial case; most emitted coordinates validate but one version mismatch and one Android target missing row remain.",
        next_improvement="Keep as a small no-native regression guard for candidate-confidence behavior.",
        validation_note="Docker Gradle captured `:app` `releaseRuntimeClasspath`; validation confirms 5/7 emitted Maven versions, with 1 mismatch and 1 missing coordinate.",
    ),
    RealCase(
        case_id="coffee",
        name="Coffee 2.26",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "system-utility"),
        expected_difficulty="Low-to-medium: recent no-native utility with a compact AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-coffee/report.json",
        validation_path="data/results/source-validation/clean-real-apk-candidate-sweep-v2/coffee/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS.md",
        interpretation="Near-clean source-validated partial case; only kotlinx-coroutines-android mismatches source.",
        next_improvement="Treat the remaining coroutines mismatch as a guarded source-version candidate, not an automatic shared-DB promotion.",
        validation_note="Docker Gradle captured `:app` `releaseRuntimeClasspath`; validation confirms 10/11 emitted Maven versions, with 1 mismatch and 0 missing coordinates.",
    ),
    RealCase(
        case_id="medtimer",
        name="MedTimer 1.22.18",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "health-utility", "multidex"),
        expected_difficulty="Medium: no-native health/reminder app with multidex and a broad modern AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-medtimer/report.json",
        validation_path="data/results/source-validation/csv3/medtimer/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V3.md",
        interpretation="Strongest v3 clean-candidate result, but still partial because six emitted versions mismatch source-resolved versions.",
        next_improvement="Use as a no-native multidex guard for future version-band/source-version coverage work.",
        validation_note="Docker Gradle captured `:app` `fossReleaseRuntimeClasspath`; validation confirms 12/18 emitted Maven versions, with 6 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="doodle",
        name="Doodle 6.0.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "wallpaper", "r8-shrink"),
        expected_difficulty="Medium: no-native UI app with release shrinking/optimization enabled but name obfuscation disabled.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-doodle/report.json",
        validation_path="data/results/source-validation/csv3/doodle/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V3.md",
        interpretation="Simple no-native source-validated row; partial because only half of emitted components validate exactly.",
        next_improvement="Use as a compact shrink/optimization guard, not as clean accuracy evidence.",
        validation_note="Docker Gradle captured `:app` `releaseRuntimeClasspath`; validation confirms 3/6 emitted Maven versions, with 2 mismatches and 1 missing coordinate.",
    ),
    RealCase(
        case_id="simple-time-tracker",
        name="Simple Time Tracker 1.57",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "time-tracker", "multidex", "r8-minified"),
        expected_difficulty="Medium-high: no-native time-tracker app with a large modular source tree and minified release build.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-simple-time-tracker/report.json",
        validation_path="data/results/source-validation/csv3/simple-time-tracker/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V3.md",
        interpretation="Useful no-native modular app evidence; partial because six AndroidX version-band rows mismatch source.",
        next_improvement="Keep as a real minified/no-native guard for future scoped R8 and version-band diagnostics.",
        validation_note="Source extraction needed Docker `/tmp` because Windows path length blocked the full tree; Docker Gradle captured `:app` `baseReleaseRuntimeClasspath`; validation confirms 6/12 emitted Maven versions, with 6 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="keepassvault",
        name="KeePassVault 1.16.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "security", "password-manager", "multidex", "gradle-8.13"),
        expected_difficulty="Medium-high: dependency-rich no-native security/password-manager app with multidex and a broad AndroidX/Compose/Kotlin/networking surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-keepassvault/report.json",
        validation_path="data/results/source-validation/csv3/keepassvault/source-validation-gradle8.13/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V3.md",
        interpretation="Useful dependency-rich no-native partial row; exact identity recovery is meaningful, but AndroidX/Compose/Kotlin/Okio version drift keeps it out of the clean bucket.",
        next_improvement="Use as a version-band/reference-coverage guard, not as clean evidence.",
        validation_note="Docker installed Android platform 34 in the validation container and Gradle 8.13 captured `:app` `fdroidReleaseRuntimeClasspath`; validation confirms 8/24 emitted Maven versions, with 15 mismatches and 1 missing coordinate.",
    ),
    RealCase(
        case_id="k9",
        name="K-9 / Thunderbird Android 18.0",
        role="source-linked-blocked",
        tags=("real", "blocked", "source-linked", "multidex", "email", "native"),
        expected_difficulty="High: email/security APK with source proof, but Gradle dependency-tree generation is blocked.",
        report_path="data/results/report-real-k9-thunderbird-android/report.json",
        validation_path=None,
        proof_path="docs/evaluation/K9_THUNDERBIRD_PROOF_BUNDLE.md",
        interpretation="Useful report case, but not an accuracy data point until the resolved dependency tree exists.",
        next_improvement="Resolve the included Gradle build-plugin stall and run source validation.",
    ),
    RealCase(
        case_id="jitsi-meet",
        name="Jitsi Meet 26.0.0",
        role="source-linked-blocked",
        tags=("real", "blocked", "source-linked", "react-native", "framework-boundary", "native-heavy", "multidex"),
        expected_difficulty="Very high: React Native/WebRTC/Hermes APK with source proof, but dependency-tree generation needs Node/npm and F-Droid native prebuild tooling.",
        report_path="data/results/report-real-jitsi-meet/report.json",
        validation_path=None,
        proof_path="docs/evaluation/JITSI_MEET_PROOF_BUNDLE.md",
        interpretation="Useful React Native boundary case; candidate Maven and native hash evidence are reported, but accuracy metrics wait for a resolved dependency tree.",
        next_improvement="Install or containerize the React Native/Node/F-Droid prebuild stack before attempting source validation again.",
        validation_note="Gradle 8.14 reaches React Native module configuration, then fails because `node` is missing in the Docker runtime.",
    ),
    RealCase(
        case_id="fairemail",
        name="FairEmail 1.2315",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "email", "security", "androidx", "native"),
        expected_difficulty="High: real email/security APK with AndroidX drift and native build configuration.",
        report_path="data/results/report-real-fairemail/report.json",
        validation_path="data/results/source-validation/fairemail-report-validation/source-validation.json",
        proof_path="docs/evaluation/FAIREMAIL_PROOF_BUNDLE.md",
        interpretation="Now source-validated via a no-native validation copy; identity is useful, but six AndroidX versions mismatch.",
        next_improvement="Use the mismatches as AndroidX version-band evidence rather than forcing recency globally.",
        validation_note="Dependency tree was generated from a validation-only source copy with native build disabled; Maven runtime dependency resolution is preserved, but native build output is not claimed.",
    ),
    RealCase(
        case_id="organic-maps",
        name="Organic Maps 2026.05.08-4",
        role="limitation-native-heavy",
        tags=("real", "limitation", "native-heavy", "source-linked"),
        expected_difficulty="Boundary case: large native payload; Java/Kotlin components can be emitted, native versions remain hash-only.",
        report_path="data/results/report-real-organic-maps-calibrated-db/report.json",
        validation_path=None,
        proof_path="docs/evaluation/REAL_APK_CURRENT_BATCH_RESULTS.md",
        interpretation="Demonstrates the native boundary of the MVP rather than a Maven-version failure.",
        next_improvement="Keep native package/version identification out of the MVP claim.",
    ),
    RealCase(
        case_id="termux",
        name="Termux 0.119.0-beta.3",
        role="limitation-native-heavy",
        tags=("real", "limitation", "native-heavy", "bootstrap"),
        expected_difficulty="Boundary case: packaging/native bootstrap app with many native files.",
        report_path="data/results/report-real-termux-calibrated-db/report.json",
        validation_path=None,
        proof_path="docs/evaluation/REAL_APK_CURRENT_BATCH_RESULTS.md",
        interpretation="Shows that the SBOM still reports native file hashes, but not native package identities.",
        next_improvement="Use as a limitation example, not an accuracy benchmark.",
    ),
    RealCase(
        case_id="hidden-dex-loader",
        name="Hidden DEX loader fixture",
        role="limitation-obfuscation",
        tags=("controlled", "limitation", "hidden-dex", "protector-style", "native"),
        expected_difficulty="Boundary case: nonstandard DEX and protector-style indicators.",
        report_path="data/results/report-limitation-hidden-dex-loader/report.json",
        validation_path=None,
        proof_path="docs/evaluation/HIDDEN_DEX_LIMITATION_FIXTURE.md",
        interpretation="Correct behavior is to raise risk and avoid false Maven claims.",
        next_improvement="Keep as a negative control for extraction-risk reporting.",
    ),
    RealCase(
        case_id="simplify-obfuscated-app",
        name="Simplify obfuscated sample",
        role="limitation-obfuscation",
        tags=("sample", "limitation", "obfuscated", "normal-dex-layout"),
        expected_difficulty="Boundary case: public obfuscated APK sample with normal DEX layout and no dependency-tree ground truth.",
        report_path="data/results/report-limitation-simplify-obfuscated-app/report.json",
        validation_path=None,
        proof_path="docs/evaluation/SIMPLIFY_OBFUSCATED_LIMITATION.md",
        interpretation="Shows normal-layout obfuscated APK behavior: medium report risk and low-confidence Maven candidates, but no source-validated accuracy claim.",
        next_improvement="Keep as limitation evidence unless a source/dependency tree is available.",
    ),
)


GROUPS: tuple[GroupSpec, ...] = (
    GroupSpec(
        group_id="controlled-clear",
        name="Controlled clear fixtures",
        expected_difficulty="Low: known Maven dependency, no obfuscation.",
        controlled_filter=lambda item: item.get("variant") == "clear" and not item.get("multidex"),
        interpretation="Baseline evidence that the matcher can recover exact components and versions when bytecode is preserved.",
        next_improvement="Keep these as sanity checks; they should never be the only reported result.",
    ),
    GroupSpec(
        group_id="controlled-r8-rename",
        name="Controlled R8 rename fixtures",
        expected_difficulty="Medium: names are rewritten, but enough structure remains.",
        controlled_filter=lambda item: item.get("variant") == "r8-rename",
        interpretation="The tool keeps correct identity/version recovery while lowering confidence instead of overclaiming.",
        next_improvement="Use as the first obfuscation robustness guard.",
    ),
    GroupSpec(
        group_id="controlled-r8-shrink",
        name="Controlled R8 shrink fixtures",
        expected_difficulty="Medium-high: shrinking removes unused bytecode and weakens evidence.",
        controlled_filter=lambda item: item.get("variant") == "r8-shrink",
        interpretation="Shrunk fixtures are still recovered, but confidence behavior matters as much as exact matching.",
        next_improvement="Keep as a no-promotion baseline after the Phase 4 diagnostic found multi-scale regression risk.",
    ),
    GroupSpec(
        group_id="controlled-r8-optimize",
        name="Controlled R8 optimize fixtures",
        expected_difficulty="Medium-high: optimization can rewrite code and call sites while preserving names.",
        controlled_filter=lambda item: item.get("variant") == "r8-optimize",
        interpretation="Optimization-only fixtures show whether structure-preserving R8 rewrites disturb exact-version evidence.",
        next_improvement="Keep as a no-scoring-change control for any future narrower R8 trigger.",
    ),
    GroupSpec(
        group_id="controlled-r8-shrink-optimize",
        name="Controlled R8 shrink plus optimize fixtures",
        expected_difficulty="High: shrink plus optimization removes evidence and can rewrite surviving methods.",
        controlled_filter=lambda item: item.get("variant") == "r8-shrink-optimize",
        interpretation="This is the hardest current controlled R8 mode that still uses ordinary fixture packaging.",
        next_improvement="Keep as a control category after the Phase 4 multi-scale diagnostic found regression risk.",
    ),
    GroupSpec(
        group_id="controlled-r8-package-flattening",
        name="Controlled R8 package flattening fixtures",
        expected_difficulty="High: repackaging collapses namespace evidence and stresses package-based matching.",
        controlled_filter=lambda item: item.get("variant") == "r8-repackage",
        interpretation="These fixtures exercise package flattening/repackaging while keeping matcher scoring unchanged.",
        next_improvement="Use as the package-structure guard for any future R8-aware reranker.",
    ),
    GroupSpec(
        group_id="controlled-r8-inline-stress",
        name="Controlled R8 inline-like call-site stress fixtures",
        expected_difficulty="High: helper call chains and optimization stress method-boundary assumptions.",
        controlled_filter=lambda item: item.get("variant") == "r8-inline-stress",
        interpretation="These fixtures create call-site stress evidence without enabling inlining-aware scoring.",
        next_improvement="Use only for narrower opt-in follow-up experiments after the Phase 4 global blend rejection.",
    ),
    GroupSpec(
        group_id="controlled-multidex-multilib",
        name="Controlled multidex and multi-library fixture",
        expected_difficulty="Medium: multiple known libraries and many DEX files.",
        controlled_filter=lambda item: bool(item.get("multidex")),
        interpretation="Shows package discovery across many DEX files, not just a single tiny APK.",
        next_improvement="Use this as the template for generated larger controlled fixtures.",
    ),
    GroupSpec(
        group_id="real-clean",
        name="Clean source-validated real APKs",
        expected_difficulty="Medium: real apps with source/dependency-tree validation and currently clean emitted Maven versions.",
        real_case_ids=("fdroid", "opentracks", "tusky", "daily-dozen"),
        interpretation="These are the strongest exact-version claims, while Tusky and Daily Dozen are intentionally labeled sparse.",
        next_improvement="Add more non-sparse clean real APKs before making broad real-world accuracy claims.",
    ),
    GroupSpec(
        group_id="real-modern-partial",
        name="Modern AndroidX/Kotlin partials",
        expected_difficulty="High: version-band ties, Android target variants, KMP wrappers, and multidex/native combinations.",
        real_case_ids=("cryptomator-lite", "easy-xkcd", "moneywallet", "foxy-droid", "newpipe", "antennapod", "kde-connect", "wikipedia", "aegis", "nextcloud", "fairemail", "vlc-android", "osmand", "material-files", "davx5"),
        interpretation="Partial accuracy here is expected evidence about APK family difficulty, not a total tool failure.",
        next_improvement="Evaluate future scoring changes only with fresh controls across this whole group.",
    ),
    GroupSpec(
        group_id="real-native-heavy",
        name="Native-heavy source and boundary cases",
        expected_difficulty="Very high: large native payloads plus Java/Kotlin Maven dependencies.",
        real_case_ids=("vlc-android", "osmand", "material-files", "tusky", "jitsi-meet", "organic-maps", "termux"),
        interpretation="VLC and OsmAnd give source-validated Maven evidence while Organic Maps and Termux define the hash-only native boundary.",
        next_improvement="Keep native package/version recovery outside the MVP claim unless a separate native reference method is added.",
    ),
    GroupSpec(
        group_id="real-r8-minified",
        name="R8/minified and messaging/security partials",
        expected_difficulty="High: minification, security/messaging stacks, and related AndroidX ties.",
        real_case_ids=("conversations", "aegis", "kde-connect", "fairemail"),
        interpretation="These apps are useful for showing confidence and limitation labels under harder transformations.",
        next_improvement="Keep artifact-family nuances separate from plain wrong-version errors.",
    ),
    GroupSpec(
        group_id="real-era-drift",
        name="Dependency-era drift stress cases",
        expected_difficulty="High: old or very new dependency stacks do not always fit one shared global reference DB.",
        real_case_ids=("markor", "nextcloud"),
        interpretation="The shared DB should not absorb every app-specific source version if it regresses other APKs.",
        next_improvement="Describe app-specific calibration experiments as evidence, not as the shared MVP default.",
    ),
    GroupSpec(
        group_id="blocked-source-linked",
        name="Source-linked but validation-blocked APKs",
        expected_difficulty="High: APK/source proof exists, but resolved dependency-tree validation is blocked.",
        real_case_ids=("k9", "jitsi-meet"),
        interpretation="These belong in dataset diversity, but not precision/recall/version-accuracy metrics yet.",
        next_improvement="Resolve Gradle, Node/npm, and F-Droid prebuild blockers and then reclassify if source validation succeeds.",
    ),
    GroupSpec(
        group_id="limitations",
        name="Native-heavy, hidden-code, and obfuscated-sample limitation cases",
        expected_difficulty="Boundary: native package versions, hidden DEX, and obfuscated samples are outside the MVP's exact-version claim.",
        real_case_ids=("organic-maps", "termux", "hidden-dex-loader", "simplify-obfuscated-app"),
        interpretation="Correct MVP behavior is transparent hash-only/native reporting, extraction-risk warnings, and low-confidence candidate labeling.",
        next_improvement="Do not count these as Maven-version failures; use them to define scope.",
    ),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate APK-type evaluation summary from controlled inventory and real proof bundles.",
    )
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inventory_path = Path(args.inventory)
    payload = build_evaluation(inventory_path)

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "doc": normalize_path(output_doc),
                "json": normalize_path(output_json),
                "groups": len(payload["groups"]),
                "real_cases": len(payload["real_cases"]),
                "source_validated_real_cases": payload["summary"]["source_validated_real_cases"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_evaluation(inventory_path: Path) -> dict[str, Any]:
    inventory = read_json(inventory_path)
    controlled_items = inventory.get("controlled_apks", [])
    case_details = [build_real_case_detail(case) for case in REAL_CASES]
    case_by_id = {case["case_id"]: case for case in case_details}
    groups = [
        build_group(spec, controlled_items=controlled_items, case_by_id=case_by_id)
        for spec in GROUPS
    ]

    summary = {
        "controlled_cases": len(controlled_items),
        "source_validated_real_cases": count_roles(
            case_details,
            {"clean-source-validated", "source-validated-partial"},
        ),
        "clean_source_validated_real_cases": count_roles(case_details, {"clean-source-validated"}),
        "partial_source_validated_real_cases": count_roles(case_details, {"source-validated-partial"}),
        "source_linked_blocked_cases": count_roles(case_details, {"source-linked-blocked"}),
        "limitation_cases": sum(1 for case in case_details if case["role"].startswith("limitation")),
    }
    summary["principle"] = (
        "Evaluate by APK type and validation level. Improving the matcher is good, but hard APK "
        "families should remain visible instead of being hidden to make a perfect-looking score."
    )

    return {
        "schema_version": 1,
        "inventory_path": normalize_path(inventory_path),
        "summary": summary,
        "groups": groups,
        "real_cases": case_details,
    }


def build_group(
    spec: GroupSpec,
    *,
    controlled_items: list[dict[str, Any]],
    case_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if spec.controlled_filter:
        selected = [item for item in controlled_items if spec.controlled_filter(item)]
        result_summary = summarize_controlled(selected)
        cases = [
            {
                "case_id": item.get("id"),
                "name": item.get("id"),
                "result_summary": summarize_controlled_case(item),
            }
            for item in selected
        ]
    else:
        cases = [case_by_id[case_id] for case_id in spec.real_case_ids]
        result_summary = summarize_real_group(cases)

    return {
        "group_id": spec.group_id,
        "name": spec.name,
        "case_count": len(cases),
        "cases": cases,
        "expected_difficulty": spec.expected_difficulty,
        "result_summary": result_summary,
        "interpretation": spec.interpretation,
        "next_improvement": spec.next_improvement,
    }


def build_real_case_detail(case: RealCase) -> dict[str, Any]:
    report = read_json_if_exists(case.report_path)
    validation = read_json_if_exists(case.validation_path)

    maven_components = len(report.get("detected_components", [])) if report else None
    apk_info = report.get("apk", {}) if report else {}
    native_files = len(apk_info.get("native_libraries", [])) if report else None
    dex_count = len(apk_info.get("dex_files", [])) if report else None
    osv_vulnerabilities = (report.get("osv") or {}).get("vulnerabilities") if report else None
    extraction_risk = (
        (apk_info.get("forensic_summary") or {}).get("extraction_risk") if report else None
    )
    obfuscation_risk = (report.get("obfuscation_risk") or {}).get("level") if report else None

    validation_summary = summarize_validation(validation, case.validation_note)

    return {
        "case_id": case.case_id,
        "name": case.name,
        "role": case.role,
        "tags": list(case.tags),
        "expected_difficulty": case.expected_difficulty,
        "maven_components": maven_components,
        "native_files": native_files,
        "dex_count": dex_count,
        "osv_vulnerabilities": osv_vulnerabilities,
        "extraction_risk": extraction_risk,
        "obfuscation_risk": obfuscation_risk,
        "validation_summary": validation_summary,
        "validation": compact_validation(validation) if validation else None,
        "interpretation": case.interpretation,
        "next_improvement": case.next_improvement,
        "report_path": normalize_optional_path(case.report_path),
        "validation_path": normalize_optional_path(case.validation_path),
        "proof_path": normalize_optional_path(case.proof_path),
    }


def summarize_controlled(items: list[dict[str, Any]]) -> str:
    if not items:
        return "No cases selected."
    totals = controlled_totals(items)
    return (
        f"{totals['component_tp']}/{totals['expected']} expected components matched; "
        f"{totals['version_tp']}/{totals['expected']} exact versions; "
        f"{totals['fp']} FP, {totals['fn']} FN, {totals['version_mismatches']} version mismatches."
    )


def summarize_controlled_case(item: dict[str, Any]) -> str:
    return summarize_controlled([item])


def controlled_totals(items: list[dict[str, Any]]) -> dict[str, int]:
    totals = {
        "expected": 0,
        "component_tp": 0,
        "version_tp": 0,
        "fp": 0,
        "fn": 0,
        "version_mismatches": 0,
    }
    for item in items:
        comparison = item.get("comparison", {})
        totals["expected"] += len(item.get("expected_components", []))
        totals["component_tp"] += len(comparison.get("component_true_positives", []))
        totals["version_tp"] += len(comparison.get("version_true_positives", []))
        totals["fp"] += len(comparison.get("false_positive_components", []))
        totals["fn"] += len(comparison.get("false_negative_components", []))
        totals["version_mismatches"] += len(comparison.get("version_mismatches", []))
    return totals


def summarize_real_group(cases: list[dict[str, Any]]) -> str:
    if not cases:
        return "No cases selected."
    validated = [case for case in cases if case.get("validation")]
    blocked = [case for case in cases if not case.get("validation")]
    if validated:
        confirmed = sum(case["validation"]["confirmed"] for case in validated)
        checked = sum(case["validation"]["checked_components"] for case in validated)
        mismatches = sum(case["validation"]["version_mismatches"] for case in validated)
        missing = sum(case["validation"]["missing"] for case in validated)
        prefix = (
            f"{confirmed}/{checked} emitted Maven versions confirmed across {len(validated)} "
            f"source-validated cases; {plural(mismatches, 'mismatch', 'mismatches')}, "
            f"{plural(missing, 'missing/nuance entry', 'missing/nuance entries')}."
        )
    else:
        prefix = f"{plural(len(blocked), 'case is', 'cases are')} excluded from source-validated accuracy metrics."
    if blocked:
        prefix += f" {plural(len(blocked), 'case remains', 'cases remain')} report-only or limitation evidence."
    return prefix


def summarize_validation(validation: dict[str, Any] | None, note: str | None) -> str:
    if not validation:
        return "Not source-validated; not counted in precision/recall/version-accuracy metrics."
    compact = compact_validation(validation)
    summary = (
        f"{compact['confirmed']}/{compact['checked_components']} confirmed, "
        f"{plural(compact['version_mismatches'], 'mismatch', 'mismatches')}, "
        f"{plural(compact['missing'], 'missing/nuance entry', 'missing/nuance entries')}"
    )
    if compact["candidate_issues"]:
        summary += f"; {plural(compact['candidate_issues'], 'candidate-only issue', 'candidate-only issues')}"
    if note:
        summary += f". Note: {note.rstrip('.')}"
    return summary + "."


def compact_validation(validation: dict[str, Any]) -> dict[str, int]:
    confirmed = int(validation.get("confirmed", 0))
    version_mismatches = int(validation.get("version_mismatches", 0))
    missing = int(validation.get("missing", 0))
    candidate_issues = int(validation.get("candidate_version_mismatches", 0)) + int(
        validation.get("candidate_missing", 0)
    )
    return {
        "confirmed": confirmed,
        "version_mismatches": version_mismatches,
        "missing": missing,
        "candidate_issues": candidate_issues,
        "checked_components": confirmed + version_mismatches + missing,
    }


def count_roles(cases: list[dict[str, Any]], roles: set[str]) -> int:
    return sum(1 for case in cases if case["role"] in roles)


def build_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = [
        "# APK-Type Evaluation",
        "",
        "Generated by `scripts/build_apk_type_evaluation.py`.",
        "",
        "This report complements the older APK inventory. It evaluates the MVP by APK family, validation level, and difficulty class instead of reducing all APKs to one perfect-or-failed score.",
        "",
        "## Evaluation Principle",
        "",
        payload["summary"]["principle"],
        "",
        "## Dataset Buckets",
        "",
        "| Bucket | Count |",
        "|---|---:|",
        f"| Controlled fixtures | {payload['summary']['controlled_cases']} |",
        f"| Clean source-validated real APKs | {payload['summary']['clean_source_validated_real_cases']} |",
        f"| Partial source-validated real APKs | {payload['summary']['partial_source_validated_real_cases']} |",
        f"| Source-linked but validation-blocked APKs | {payload['summary']['source_linked_blocked_cases']} |",
        f"| Limitation/boundary cases | {payload['summary']['limitation_cases']} |",
        "",
        "## Grouped Results",
        "",
        "| APK type / classification | Cases | Result summary | Interpretation | Next improvement |",
        "|---|---:|---|---|---|",
    ]

    for group in payload["groups"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_md(group["name"]),
                    str(group["case_count"]),
                    escape_md(group["result_summary"]),
                    escape_md(group["interpretation"]),
                    escape_md(group["next_improvement"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Real APK Case Details",
            "",
            "| Case | Role | Tags | Maven | Native | DEX | Validation | Evidence |",
            "|---|---|---|---:|---:|---:|---|---|",
        ]
    )

    for case in payload["real_cases"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_md(case["name"]),
                    escape_md(case["role"]),
                    escape_md(", ".join(case["tags"])),
                    unknown_int(case["maven_components"]),
                    unknown_int(case["native_files"]),
                    unknown_int(case["dex_count"]),
                    escape_md(case["validation_summary"]),
                    evidence_links(case),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## How To Use This In The Thesis",
            "",
            "- Report clean source-validated cases as exact-version successes.",
            "- Report partial source-validated cases by APK type and explain the remaining version-band, artifact-family, or reference-coverage limitation.",
            "- Keep source-linked blocked cases out of accuracy metrics until their dependency trees are generated.",
            "- Treat native-heavy and hidden-code cases as scope/limitation evidence, not as failed Maven-version detections.",
            "- Continue improving the matcher only when the change passes fresh controls across clean, partial, and limitation groups.",
            "",
        ]
    )
    return "\n".join(lines)


def evidence_links(case: dict[str, Any]) -> str:
    links = []
    for label, path in (
        ("report", case.get("report_path")),
        ("validation", case.get("validation_path")),
        ("proof", case.get("proof_path")),
    ):
        if path:
            links.append(f"`{label}`: `{path}`")
    return "<br>".join(links) if links else "none"


def unknown_int(value: int | None) -> str:
    return "n/a" if value is None else str(value)


def plural(value: int, singular: str, plural_form: str) -> str:
    noun = singular if value == 1 else plural_form
    return f"{value} {noun}"


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_if_exists(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    json_path = Path(path)
    if not json_path.exists():
        return None
    return read_json(json_path)


def normalize_optional_path(path: str | None) -> str | None:
    if not path:
        return None
    return normalize_path(Path(path))


def normalize_path(path: Path | str) -> str:
    return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
