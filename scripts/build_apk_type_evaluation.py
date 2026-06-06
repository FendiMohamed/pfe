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
        case_id="your-local-weather",
        name="Your local weather 6.4.0-FOSS",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "weather", "multidex"),
        expected_difficulty="Medium: no-native weather app with multidex and a broad AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-your-local-weather/report.json",
        validation_path="data/results/source-validation/csv9/your-local-weather/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V9.md",
        interpretation="Useful non-sparse weather partial row: most emitted Maven versions validate, but two selected versions still drift from source.",
        next_improvement="Keep as partial no-native weather evidence and use the remaining Kotlin/SwipeRefreshLayout mismatches for guarded version-disambiguation checks.",
        validation_note="Docker Gradle 9.5 captured `:app` `fossReleaseRuntimeClasspath`; validation confirms 15/17 emitted Maven versions, with 2 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="homefeed-rss-widget",
        name="HomeFeed - RSS Widget 1.3.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "news", "rss-widget"),
        expected_difficulty="Medium: no-native RSS/news widget with a compact APK and modern AndroidX/Kotlin dependency drift.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-homefeed-rss-widget/report.json",
        validation_path="data/results/source-validation/csv9/homefeed-rss-widget/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V9.md",
        interpretation="Useful compact internet/news partial row: source validation succeeds quickly, but six emitted versions mismatch the source tree.",
        next_improvement="Use as a small no-native internet/news guard for future source-version coverage experiments.",
        validation_note="Docker Gradle 9.5 captured `:app` `releaseRuntimeClasspath`; validation confirms 11/17 emitted Maven versions, with 6 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="etar",
        name="Etar - OpenSource Calendar 1.0.55",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "calendar", "time", "multidex"),
        expected_difficulty="Medium: no-native calendar/time app with multidex and a broad modern AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-etar/report.json",
        validation_path="data/results/source-validation/csv10/etar/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V10.md",
        interpretation="Useful non-sparse calendar partial row: many core AndroidX/Kotlin versions validate, but low-confidence extra emissions create missing-source entries.",
        next_improvement="Keep as partial no-native calendar evidence and use the missing/low-confidence rows to tune uncertainty output rather than overclaiming clean accuracy.",
        validation_note="Docker Gradle 9.5 captured `:app` `releaseRuntimeClasspath`; validation confirms 15/38 emitted Maven versions, with 2 mismatches and 21 missing coordinates.",
    ),
    RealCase(
        case_id="dolidroid",
        name="DoliDroid 3.0.69",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "erp-crm", "legacy-jcenter", "gradle-9.5-validation-copy"),
        expected_difficulty="High: no-native ERP/CRM front-end with a webview-heavy asset payload and legacy JCenter repository wiring.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-dolidroid/report.json",
        validation_path="data/results/source-validation/csv9/dolidroid/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V9.md",
        interpretation="Useful v9 internet/ERP partial row: the JCenter validation copy resolves source dependencies, but exact version selection remains split across AndroidX/security components.",
        next_improvement="Keep as partial legacy-JCenter evidence and use the seven version mismatches as version-band/reference-coverage targets.",
        validation_note="The blocker-rescue profile replaced removed `jcenter()` calls with Maven Central in a validation copy; Docker captured `:app` `releaseRuntimeClasspath`; validation confirms 7/14 emitted Maven versions, with 7 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="owncloud",
        name="ownCloud 4.8.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "cloud-storage", "internet", "multidex", "gradle-8.13-validation-copy"),
        expected_difficulty="High: no-native cloud-storage client with multidex and modern Kotlin/KSP/analysis plugin wiring that blocks the unpatched Gradle dependency-tree lane.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-owncloud/report.json",
        validation_path="data/results/source-validation/csv9/owncloud/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V9.md",
        interpretation="Useful cloud-storage partial row: the validation-copy lane resolves the app runtime tree, while version selection still drifts across modern AndroidX/Kotlin dependencies.",
        next_improvement="Keep as partial no-native cloud evidence and use the 14 mismatches plus one missing coordinate for future version-disambiguation work.",
        validation_note="The blocker-rescue profile used a validation copy that disables ownCloud Kotlin/KSP/Parcelize/Ktlint/Detekt/Sonar/CycloneDX build-time wiring, pins `:owncloudApp`, and uses Docker Gradle 8.13; validation confirms 7/22 emitted Maven versions, with 14 mismatches and 1 missing coordinate.",
    ),
    RealCase(
        case_id="openkeychain",
        name="OpenKeychain: Easy PGP 6.0.4",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "security", "crypto", "older-profile", "legacy-jcenter", "gradle-8.13-validation-copy"),
        expected_difficulty="High: no-native security/PGP app with a large source tree, older-profile dependencies, removed JCenter wiring, and incomplete F-Droid local submodule sources.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-openkeychain/report.json",
        validation_path="data/results/source-validation/csv9/openkeychain/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V9.md",
        interpretation="Useful v9 security/crypto partial row: the rescue lane reaches source validation, but source-resolved AndroidX versions are mostly older than the emitted candidates.",
        next_improvement="Keep as partial legacy/security evidence and use the seven version mismatches as version-band/reference-coverage targets.",
        validation_note="The blocker-rescue profile added a minimal validation-copy settings.gradle, replaced removed `jcenter()` calls with Maven Central, enabled AGP-required BuildConfig/AndroidX properties, omitted unavailable local project wires, and used Docker Gradle 8.13; validation confirms 5/12 emitted Maven versions, with 7 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="radiodroid",
        name="RadioDroid 0.86",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "multimedia", "radio", "multidex", "legacy-jcenter", "gradle-8.13-validation-copy"),
        expected_difficulty="High: no-native radio/media app with old Android Gradle plugin wiring, JCenter repository calls, flavors, and multidex output.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-radiodroid/report.json",
        validation_path="data/results/source-validation/csv10/radiodroid/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V10.md",
        interpretation="Useful v10 radio/media partial row: the rescue lane reaches source validation, but many low-confidence emitted components are absent or version-shifted relative to the source tree.",
        next_improvement="Keep as partial multimedia evidence and use the missing-coordinate set to tune uncertainty/report filtering before any scorer change.",
        validation_note="The blocker-rescue profile replaced removed `jcenter()` calls with Maven Central in a validation copy and used Docker Gradle 8.13 for AGP compatibility; validation confirms 5/39 emitted Maven versions, with 15 mismatches and 19 missing coordinates.",
    ),
    RealCase(
        case_id="simplelogin",
        name="SimpleLogin Anti-spam 1.22.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "email", "internet", "security", "multidex", "gradle-8.13-validation-copy"),
        expected_difficulty="High: no-native email/security app with multidex, modern AndroidX/Kotlin dependencies, Detekt build-time plugin incompatibility, and a broad low-confidence emitted set.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-simplelogin/report.json",
        validation_path="data/results/source-validation/csv10/simplelogin/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V10.md",
        interpretation="Useful v10 email/security partial row: the rescue lane reaches source validation, but many low-confidence emitted components are absent from the source tree and several AndroidX/Kotlin versions drift.",
        next_improvement="Keep as partial email/security evidence and use the missing low-confidence rows to tune uncertainty/report filtering before any scorer change.",
        validation_note="The blocker-rescue profile copied the real `SimpleLogin` Gradle root, disabled only the Detekt build-time analysis plugin/configuration, used Docker Gradle 8.13, and captured `:app` `fdroidReleaseRuntimeClasspath`; validation confirms 9/39 emitted Maven versions, with 13 mismatches and 17 missing coordinates.",
    ),
    RealCase(
        case_id="omni-notes",
        name="Omni Notes 6.3.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "notes", "task", "writing", "gradle-8.13-validation-copy"),
        expected_difficulty="High: no-native notes/task app with older build-time analysis plugins, multidex-era AndroidX dependencies, and a broad low-confidence emitted set.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-omni-notes/report.json",
        validation_path="data/results/source-validation/csv10/omni-notes/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V10.md",
        interpretation="Useful v10 notes/productivity partial row: the rescue lane reaches source validation, but most low-confidence emitted components are absent or version-shifted relative to the source tree.",
        next_improvement="Keep as partial notes/productivity evidence and use the missing low-confidence rows to tune uncertainty/report filtering before any scorer change.",
        validation_note="The blocker-rescue profile used a validation-only copy, disabled SonarQube/test-logger/Jacoco build-time analysis wiring, narrowed Gradle probing to the real `:omniNotes` module, used Docker Gradle 8.13, and captured `fossReleaseRuntimeClasspath`; validation confirms 4/39 emitted Maven versions, with 16 mismatches and 19 missing coordinates.",
    ),
    RealCase(
        case_id="primitive-ftpd",
        name="Primitive FTPd 8.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "connectivity", "file-transfer", "multidex", "gradle-9.5"),
        expected_difficulty="High: no-native connectivity/file-transfer app with a broad AndroidX/network-service dependency surface and multidex APK output.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-primitive-ftpd/report.json",
        validation_path="data/results/source-validation/csv10/primitive-ftpd/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V10.md",
        interpretation="Useful v10 connectivity/file-transfer partial row: the strict module rescue confirms source coordinate identity for part of a rich dependency tree, but most emitted coordinates remain missing from the resolved source tree.",
        next_improvement="Keep as partial network-service evidence and use the missing-coordinate set to guide future reference coverage or matcher filtering work.",
        validation_note="The blocker-rescue profile narrowed Gradle probing to the actual `:primitiveFTPd` app module; Docker captured `releaseRuntimeClasspath`; validation confirms 12/38 emitted Maven versions, with 4 mismatches and 22 missing coordinates.",
    ),
    RealCase(
        case_id="floccus",
        name="floccus bookmark sync 5.9.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "bookmark", "internet", "reading", "multidex"),
        expected_difficulty="Medium: no-native bookmark-sync app with a large Capacitor/Android source tree and multidex APK output.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v11/report-real-floccus/report.json",
        validation_path="data/results/source-validation/csv11/floccus/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V11.md",
        interpretation="Useful v11 no-native internet/reading partial row: core AndroidX/Kotlin identity is recovered, but four selected versions are newer than source.",
        next_improvement="Keep as partial bookmark-sync evidence and use Activity, Fragment, Kotlin, and Core-KTX mismatches as future version-band/reference-coverage targets.",
        validation_note="A floccus-specific proof hint narrowed Gradle probing to `:app:dependencies`; Docker captured `releaseRuntimeClasspath`; validation confirms 9/13 emitted Maven versions, with 4 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="opencloud",
        name="OpenCloud 1.2.3",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "cloud-storage", "sync-client", "multidex"),
        expected_difficulty="High: no-native cloud-sync app with multidex and modern AndroidX/Kotlin dependencies, rescued through a validation-only Gradle plugin-compatibility copy.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v11/report-real-opencloud/report.json",
        validation_path="data/results/source-validation/csv11/opencloud/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V11.md",
        interpretation="Useful v11 cloud/sync partial row: the rescue profile confirms source coordinate identity for many emitted components, but most selected versions are newer than the source-resolved tree.",
        next_improvement="Keep as partial cloud-sync evidence and use AndroidX/Kotlin version mismatches as future reference-coverage and version-band targets.",
        validation_note="The OpenCloud blocker-rescue profile created a validation-only source copy, disabled KSP/Kotlin/Detekt/Sonar build-time plugins only for dependency-tree capture, and captured `:opencloudApp` `originalReleaseRuntimeClasspath`; validation confirms 8/22 emitted Maven versions, with 14 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="sambalite",
        name="SambaLite 2.5.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "cloud-storage", "connectivity", "file-transfer", "multidex"),
        expected_difficulty="Medium: no-native SMB/CIFS client with multidex and a modern AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v11/report-real-sambalite/report.json",
        validation_path="data/results/source-validation/csv11/sambalite/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V11.md",
        interpretation="Useful v11 non-sparse connectivity partial row: most emitted Maven versions validate, but three selected versions mismatch source.",
        next_improvement="Keep as partial no-native connectivity evidence; use the ViewPager2, SwipeRefreshLayout, and Kotlin version mismatches as future version-band/reference-coverage targets.",
        validation_note="The v11 targeted Docker proof gate captured `:app` `debugRuntimeClasspath`; validation confirms 16/19 emitted Maven versions, with 3 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="nightdream",
        name="NightDream 2.11.26",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "clock", "weather", "multidex"),
        expected_difficulty="Medium: no-native clock/weather app with multidex and a modern AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v11/report-real-nightdream/report.json",
        validation_path="data/results/source-validation/csv11/nightdream/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V11.md",
        interpretation="Useful v11 non-sparse clock/weather partial row: many emitted Maven versions validate, but six modern AndroidX/Kotlin versions mismatch source.",
        next_improvement="Keep as partial no-native clock/weather evidence; use the Concurrent Futures, Kotlin, RecyclerView, Activity, Work, and Core-KTX mismatches as future version-band/reference-coverage targets.",
        validation_note="The v11 targeted Docker proof gate captured `:app` `fullReleaseRuntimeClasspath`; validation confirms 15/21 emitted Maven versions, with 6 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="waistline",
        name="Waistline 3.10.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "health", "diet", "cordova"),
        expected_difficulty="High: no-native health/diet app with a Cordova Android source tree, rescued through a validation-only Gradle/Cordova compatibility copy.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v11/report-real-waistline/report.json",
        validation_path="data/results/source-validation/csv11/waistline/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V11.md",
        interpretation="Useful v11 no-native health/diet partial row: the Cordova rescue confirms most emitted coordinates, while six AndroidX/Kotlin selected versions remain newer than source.",
        next_improvement="Keep as partial Cordova health-app evidence; use Core, Kotlin, Coroutines, Core-KTX, and Activity mismatches as future version-band/reference-coverage targets.",
        validation_note="The Waistline blocker-rescue profile cloned only `platforms/android`, added Docker SDK metadata, imported Cordova's Groovy XML parser class, aligned build-tools metadata with Docker build-tools 36.0.0, replaced the plugin `jcenter()` call with the archived Maven URL, and captured `:app` `releaseRuntimeClasspath`; validation confirms 9/15 emitted Maven versions, with 6 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="password-generator",
        name="Password Generator 1.9.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "security", "password", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: no-native security/password utility with multidex and a modern AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v12/report-real-password-generator/report.json",
        validation_path="data/results/source-validation/csv12/password-generator/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V12.md",
        interpretation="Useful v12 security partial row: source validation confirms many core AndroidX/Kotlin identities, but five emitted versions are newer than the source-resolved tree.",
        next_improvement="Keep as partial no-native security evidence and use the RecyclerView, Core/Core-KTX, and Coroutines mismatches as future version-band targets.",
        validation_note="The v12 proof profile narrowed Gradle probing to `:passwordgenerator` `releaseRuntimeClasspath`; validation confirms 11/16 emitted Maven versions, with 5 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="todo-agenda",
        name="Todo Agenda 4.13.3",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "calendar", "task", "time", "gradle-9.5-validation-copy"),
        expected_difficulty="Medium: no-native calendar/task app with a modern AndroidX/Kotlin dependency tree and one obsolete build-output property.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v12/report-real-todo-agenda/report.json",
        validation_path="data/results/source-validation/csv12/todo-agenda/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V12.md",
        interpretation="Useful v12 calendar/task partial row: the validation copy reaches a clean runtime tree, while six emitted versions still drift from source.",
        next_improvement="Keep as partial no-native calendar/task evidence; do not treat the validation-only archive-name edit as an APK/source dependency change.",
        validation_note="The v12 validation copy omitted only Todo Agenda's obsolete `archivesBaseName` output naming line, preserved app/colorpicker runtime dependencies, and captured `:app` `releaseRuntimeClasspath`; validation confirms 10/16 emitted Maven versions, with 6 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="keep-it-up",
        name="Keep it up 1.11.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "connectivity", "internet", "network-monitor", "gradle-9.5"),
        expected_difficulty="Medium: no-native network-monitoring app with a compact emitted SBOM and a richer source runtime tree.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v12/report-real-keep-it-up/report.json",
        validation_path="data/results/source-validation/csv12/keep-it-up/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V12.md",
        interpretation="Compact v12 connectivity partial row: three emitted versions validate, one Startup version mismatches, and one Lifecycle Android-target coordinate is missing from the source tree.",
        next_improvement="Use as a compact network-monitor guard for artifact-family and Android-target coordinate handling.",
        validation_note="The v12 proof profile narrowed Gradle probing to `:keepitupmain` `releaseRuntimeClasspath`; validation confirms 3/5 emitted Maven versions, with 1 mismatch and 1 missing coordinate.",
    ),
    RealCase(
        case_id="c3nav",
        name="c3nav 4.7.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "navigation", "maps", "gradle-9.5"),
        expected_difficulty="Medium: no-native navigation/maps app with a nested Android Gradle root and older plus modern AndroidX dependency drift.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v12/report-real-c3nav/report.json",
        validation_path="data/results/source-validation/csv12/c3nav/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V12.md",
        interpretation="Useful v12 navigation partial row: runtime dependency capture succeeds from the nested CongressRoutePlanner root, but half of emitted versions are newer than source.",
        next_improvement="Keep as partial maps/navigation evidence and use AppCompat/Core/Kotlin/Coroutines mismatches for future version-band checks.",
        validation_note="The v12 proof profile captured `CongressRoutePlanner` `:app` `releaseRuntimeClasspath`; validation confirms 7/14 emitted Maven versions, with 7 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="opentopomap-viewer",
        name="OpenTopoMap Viewer 1.29",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "navigation", "maps", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: no-native navigation/map app with multidex and a broad AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v13/report-real-opentopomap-viewer/report.json",
        validation_path="data/results/source-validation/csv13/opentopomap-viewer/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V13.md",
        interpretation="Useful v13 navigation partial row: source validation confirms a majority of emitted Maven versions, while nine selected AndroidX/Kotlin versions remain newer than source.",
        next_improvement="Keep as partial no-native map evidence and use its AppCompat/Core/Kotlin/Coroutines mismatches as future version-band/reference-coverage targets.",
        validation_note="The v13 Docker proof gate captured `:app` `fossReleaseRuntimeClasspath` after probing multiple configurations; validation confirms 13/22 emitted Maven versions, with 9 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="railway-station-photos",
        name="Railway station photos 16.4.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "navigation", "public-transport", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: no-native public-transport/navigation app with multidex and modern AndroidX/Kotlin dependency drift.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v13/report-real-railway-station-photos/report.json",
        validation_path="data/results/source-validation/csv13/railway-station-photos/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V13.md",
        interpretation="Strong v13 public-transport partial row: 18 emitted versions validate and only five remain mismatched, making it near-clean but still honest partial evidence.",
        next_improvement="Keep as a high-quality no-native navigation guard and use its few AndroidX/Kotlin mismatches for future reference/version-band analysis.",
        validation_note="The v13 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 18/23 emitted Maven versions, with 5 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="linkdroid",
        name="LinkDroid for Linkwarden 2.1.9",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "bookmark", "reading", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: no-native internet/bookmark client with multidex and a modern networking/UI dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v13/report-real-linkdroid/report.json",
        validation_path="data/results/source-validation/csv13/linkdroid/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V13.md",
        interpretation="Useful v13 internet/bookmark partial row: most emitted coordinates are source-present, but eight versions drift from the resolved runtime tree.",
        next_improvement="Keep as partial no-native sync-client-style evidence; use its AndroidX/Kotlin and networking version mismatches as future version-band targets.",
        validation_note="The v13 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 12/20 emitted Maven versions, with 8 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="quasseldroid",
        name="Quasseldroid 1.8.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "messaging", "gradle-9.5"),
        expected_difficulty="Medium: no-native internet/messaging app with a compact but non-sparse emitted SBOM.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v13/report-real-quasseldroid/report.json",
        validation_path="data/results/source-validation/csv13/quasseldroid/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V13.md",
        interpretation="Strong v13 messaging partial row: 14/17 emitted versions validate, leaving only three explicit version mismatches.",
        next_improvement="Keep as a high-quality no-native messaging guard; its few remaining mismatches are good future version-band/reference-coverage targets.",
        validation_note="The v13 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 14/17 emitted Maven versions, with 3 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="bimba",
        name="Bimba 3.99",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "navigation", "public-transport", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: no-native public-transport app with multidex and a broad AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-bimba/report.json",
        validation_path="data/results/source-validation/csv14/bimba/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V14.md",
        interpretation="Useful v14 public-transport partial row: source validation confirms almost half of emitted Maven versions while keeping 13 version mismatches explicit.",
        next_improvement="Keep as partial no-native navigation evidence and use its AndroidX/Kotlin version mismatches as future version-band/reference-coverage targets.",
        validation_note="The v14 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 12/25 emitted Maven versions, with 13 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="wx",
        name="wX 55990",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "weather", "science", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: no-native weather/science app with multidex and a modern dependency tree.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-wx/report.json",
        validation_path="data/results/source-validation/csv14/wx/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V14.md",
        interpretation="Useful v14 weather/science partial row: 12/19 emitted versions validate and seven remain explicit source-version mismatches.",
        next_improvement="Keep as partial weather evidence and use its remaining AndroidX/Kotlin mismatches for future scoped version-band analysis.",
        validation_note="The v14 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 12/19 emitted Maven versions, with 7 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="egyptian-writer",
        name="Egyptian Writer 14.05.2026@0.1.0.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "reading", "science", "writing", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: no-native reading/writing app with multidex and modern UI/text-processing dependencies.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-egyptian-writer/report.json",
        validation_path="data/results/source-validation/csv14/egyptian-writer/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V14.md",
        interpretation="Strong v14 reading/writing partial row: 13/17 emitted versions validate, leaving only four explicit version mismatches.",
        next_improvement="Keep as a high-quality no-native education/writing guard and use its few remaining mismatches as reference-coverage targets.",
        validation_note="The v14 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 13/17 emitted Maven versions, with 4 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="smouldering-durtles",
        name="Smouldering Durtles 1.2.3",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "science", "education", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: no-native education client with multidex and a broad source-resolved dependency tree.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-smouldering-durtles/report.json",
        validation_path="data/results/source-validation/csv14/smouldering-durtles/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V14.md",
        interpretation="Useful v14 education partial row: source validation confirms 8/22 emitted versions and exposes a larger set of version-band mismatches.",
        next_improvement="Keep as partial education-client evidence and use its mismatches to test future guarded reference expansion.",
        validation_note="The v14 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 8/22 emitted Maven versions, with 14 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="dns-hero",
        name="DNS Hero 1.7.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "dns", "gradle-9.5"),
        expected_difficulty="Medium: no-native DNS/internet utility with a compact emitted SBOM and a FOSS runtime dependency configuration.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-dns-hero/report.json",
        validation_path="data/results/source-validation/csv14/dns-hero/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V14.md",
        interpretation="Compact v14 DNS partial row: four emitted versions validate while seven source-present coordinates remain version mismatches.",
        next_improvement="Keep as partial networking-utility evidence and use the FOSS runtime tree as a guard for future compact app validation.",
        validation_note="The v14 Docker proof gate captured `:app` `fossReleaseRuntimeClasspath` after probing multiple configurations; validation confirms 4/11 emitted Maven versions, with 7 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="baby-books",
        name="Baby Books 0.9.2",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "reading", "science", "writing", "multidex", "gradle-8.13-validation-copy"),
        expected_difficulty="High: no-native reading/writing app whose Android runtime tree needed an Android-module-only validation copy.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-baby-books/report.json",
        validation_path="data/results/source-validation/csv14/baby-books/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V14.md",
        interpretation="Useful v14 reading/writing partial row: source validation confirms 10/29 emitted versions after omitting unrelated frontend/web/CLI Gradle modules from the validation copy.",
        next_improvement="Keep as a Gradle-flexibility proof and use its AndroidX/Ktor/Kotlin mismatches as future guarded calibration targets.",
        validation_note="The v14 blocker rescue used a validation-only Android-module copy, pinned `:android`, used Docker Gradle 8.13, and captured `releaseRuntimeClasspath`; validation confirms 10/29 emitted Maven versions, with 18 mismatches and 1 missing coordinate.",
    ),
    RealCase(
        case_id="odysee",
        name="Odysee 0.0.124",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "multimedia", "media-client", "cordova", "gradle-8.14-validation-copy"),
        expected_difficulty="High: Cordova media/internet app requiring a validation-copy Groovy XML parser compatibility patch.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-odysee/report.json",
        validation_path="data/results/source-validation/csv14/odysee/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V14.md",
        interpretation="Strong v14 Cordova/media partial row: source validation confirms 10/15 emitted versions after a validation-copy Cordova Gradle compatibility rescue.",
        next_improvement="Use as another framework/build-system flexibility proof; keep the five Kotlin/AndroidX version mismatches explicit.",
        validation_note="The v14 blocker rescue added Docker SDK metadata and Cordova `XmlParser` import in a validation copy, then captured `:app` `releaseRuntimeClasspath` with Docker Gradle 8.14.3; validation confirms 10/15 emitted Maven versions, with 5 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="radarweather",
        name="RadarWeather 6.7",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "weather", "gradle-9.5-validation-copy"),
        expected_difficulty="High: older AGP weather app requiring a validation-copy AGP compatibility upgrade before dependency-tree capture.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-radarweather/report.json",
        validation_path="data/results/source-validation/csv14/radarweather/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V14.md",
        interpretation="Useful v14 weather partial row: source validation confirms 5/17 emitted versions after an old-AGP validation-copy rescue.",
        next_improvement="Keep as old-AGP flexibility evidence and use the AndroidX/Kotlin version drift as future reference-calibration stress.",
        validation_note="The v14 blocker rescue upgraded only the validation-copy Android Gradle plugin path, added AGP-required namespace/BuildConfig settings, and captured `:app` `releaseRuntimeClasspath`; validation confirms 5/17 emitted Maven versions, with 12 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="clock",
        name="Clock 2.29",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "time", "clock", "timer", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: no-native clock/timer app with multidex and a broad AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-clock/report.json",
        validation_path="data/results/source-validation/csv15/clock/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V15.md",
        interpretation="Useful v15 time-utility partial row: source validation confirms 11/38 emitted Maven versions while many low-confidence emissions remain missing from the resolved source tree.",
        next_improvement="Use as a dependency-rich no-native time/clock guard and keep its AndroidX/Kotlin drift explicit.",
        validation_note="The v15 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 11/38 emitted Maven versions, with 6 mismatches and 21 missing coordinates.",
    ),
    RealCase(
        case_id="poet-assistant",
        name="Poet Assistant 1.31.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "writing", "dictionary", "tts", "gradle-9.5-validation-copy"),
        expected_difficulty="High: no-native writing/dictionary app whose runtime tree needed a JCenter-to-Maven-Central validation copy.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-poet-assistant/report.json",
        validation_path="data/results/source-validation/csv15/poet-assistant/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V15.md",
        interpretation="Useful v15 writing/dictionary partial row: a narrow JCenter validation-copy rescue reaches runtime dependency validation without changing matcher or SBOM behavior.",
        next_improvement="Keep as another legacy-repository flexibility proof and use its missing/shifted dependency rows for reference-coverage diagnostics.",
        validation_note="The v15 blocker rescue replaced removed `jcenter()` calls in a validation copy and captured `:app` `releaseRuntimeClasspath`; validation confirms 7/37 emitted Maven versions, with 9 mismatches and 21 missing coordinates.",
    ),
    RealCase(
        case_id="ftpclient",
        name="FTPClient 3.0.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "cloud-storage", "file-transfer", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: no-native FTP/FTPS/SFTP client with multidex and compact source runtime dependencies.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-ftpclient/report.json",
        validation_path="data/results/source-validation/csv15/ftpclient/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V15.md",
        interpretation="Useful v15 connectivity/file-transfer partial row: source validation confirms 13 emitted versions and keeps 22 missing-source emissions visible.",
        next_improvement="Use as a file-transfer/internet guard for future source-version and low-confidence emission pruning work.",
        validation_note="The v15 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 13/39 emitted Maven versions, with 4 mismatches and 22 missing coordinates.",
    ),
    RealCase(
        case_id="json-list",
        name="Json List 1.10",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "development", "json-viewer", "multidex", "gradle-9.5"),
        expected_difficulty="Medium: no-native development/JSON viewer app with multidex and modern AndroidX/Kotlin dependencies.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-json-list/report.json",
        validation_path="data/results/source-validation/csv15/json-list/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V15.md",
        interpretation="Useful v15 development-tool partial row: 14 emitted versions validate while missing-source emissions expose over-broad low-confidence output.",
        next_improvement="Use as a development-tool guard for future low-confidence pruning and reference-coverage diagnostics.",
        validation_note="The v15 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 14/38 emitted Maven versions, with 5 mismatches and 19 missing coordinates.",
    ),
    RealCase(
        case_id="forecastie",
        name="Forecastie 1.23",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "weather", "gradle-9.5"),
        expected_difficulty="Medium-high: no-native weather app with older dependency-era source versions and a compact emitted SBOM.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-forecastie/report.json",
        validation_path="data/results/source-validation/csv15/forecastie/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V15.md",
        interpretation="Useful v15 weather partial row: the source gate was repaired after a corrupt tarball retry, then runtime validation confirmed a small exact subset.",
        next_improvement="Keep as older-weather dependency drift evidence and as a reminder to verify source tarball hashes after interrupted downloads.",
        validation_note="The v15 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 3/37 emitted Maven versions, with 10 mismatches and 24 missing coordinates.",
    ),
    RealCase(
        case_id="ultrasonic",
        name="Ultrasonic 4.9.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "internet", "multimedia", "music-streaming", "strict-module-rescue"),
        expected_difficulty="High: no-native media client with a modern AndroidX/Kotlin dependency surface and a strict `:ultrasonic` module rescue.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-ultrasonic/report.json",
        validation_path="data/results/source-validation/csv15/ultrasonic/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V15_BLOCKER_RESCUE.md",
        interpretation="Useful v15 media/internet partial row: strict `:ultrasonic` module probing rescued the former blocked row and confirmed a meaningful exact subset.",
        next_improvement="Keep AndroidX/Kotlin/media dependency drift explicit; use the strict-module rescue as a precedent for future non-`:app` F-Droid projects.",
        validation_note="The v15 blocker rescue captured `:ultrasonic` `releaseRuntimeClasspath`; validation confirms 12/39 emitted Maven versions, with 10 mismatches and 17 missing coordinates.",
    ),
    RealCase(
        case_id="runnerup",
        name="RunnerUp 2.11.0.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "sports-health", "workout", "gps-tracker", "strict-flavor-rescue"),
        expected_difficulty="High: no-native sports/GPS tracker with a flavor-prefixed runtime configuration and location/fitness dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-runnerup/report.json",
        validation_path="data/results/source-validation/csv15/runnerup/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V15_BLOCKER_RESCUE.md",
        interpretation="Useful v15 sports/health partial row: strict `latestReleaseRuntimeClasspath` probing rescued the former blocked row.",
        next_improvement="Keep as a guard for flavor-prefixed Gradle configurations; do not treat missing generic `releaseRuntimeClasspath` as a source-validation failure.",
        validation_note="The v15 blocker rescue captured `:app` `latestReleaseRuntimeClasspath`; validation confirms 16/39 emitted Maven versions, with 4 mismatches and 19 missing coordinates.",
    ),
    RealCase(
        case_id="imapnotes3",
        name="ImapNotes3 v1.4-07",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "email", "internet", "notes", "writing", "strict-module-rescue"),
        expected_difficulty="Medium-high: no-native IMAP note app with mail/sync dependencies and a nonstandard app module name.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-imapnotes3/report.json",
        validation_path="data/results/source-validation/csv15/imapnotes3/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V15_BLOCKER_RESCUE.md",
        interpretation="Useful v15 email/notes partial row: strict `:ImapNotes3` module probing rescued the former blocked row.",
        next_improvement="Use as a simple precedent for source trees whose Android app module is capitalized or app-specific rather than `:app`.",
        validation_note="The v15 blocker rescue captured `:ImapNotes3` `releaseRuntimeClasspath`; validation confirms 11/39 emitted Maven versions, with 6 mismatches and 22 missing coordinates.",
    ),
    RealCase(
        case_id="oceannex",
        name="OceanNex for DigitalOcean 1.0.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "cloud", "digitalocean", "multidex", "gradle-9.5"),
        expected_difficulty="Medium-high: no-native cloud-management app with multidex and AndroidX/Kotlin version-band drift.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-oceannex/report.json",
        validation_path="data/results/source-validation/csv16/oceannex/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md",
        interpretation="Useful v16 cloud/API-client partial row: source validation confirms most emitted versions while preserving five version mismatches.",
        next_improvement="Use as a no-native cloud/API guard for future version-band and low-confidence emission pruning work.",
        validation_note="The v16 Docker proof gate captured `:app` `freeReleaseRuntimeClasspath`; validation confirms 16/21 emitted Maven versions, with 5 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="praktika-vortaro",
        name="Praktika Vortaro 0.26",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "dictionary", "esperanto", "sparse-maven", "gradle-9.5"),
        expected_difficulty="Low for emitted Maven count, but useful as a sparse dictionary app with source-linked runtime validation.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-praktika-vortaro/report.json",
        validation_path="data/results/source-validation/csv16/praktika-vortaro/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md",
        interpretation="Sparse v16 dictionary row: the single emitted Maven component mismatches the source tree, so it is partial and not clean evidence.",
        next_improvement="Keep as sparse-source validation evidence and avoid letting it imply non-sparse clean performance.",
        validation_note="The v16 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 0/1 emitted Maven versions, with 1 mismatch and 0 missing coordinates.",
    ),
    RealCase(
        case_id="msggo",
        name="MsgGo 3.9",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "messaging", "internet", "gradle-9.5"),
        expected_difficulty="Medium: compact no-native messaging/internet app with a small AndroidX dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-msggo/report.json",
        validation_path="data/results/source-validation/csv16/msggo/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md",
        interpretation="Compact v16 messaging partial row: one emitted version validates and three mismatches show remaining version drift.",
        next_improvement="Use as a small no-native internet control for scoped source-version evidence.",
        validation_note="The v16 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 1/4 emitted Maven versions, with 3 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="af-weather-widget",
        name="AF Weather Widget 3.2",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "weather", "widget", "gradle-9.5"),
        expected_difficulty="Medium-high: no-native weather widget with a moderately broad AndroidX/Kotlin dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-af-weather-widget/report.json",
        validation_path="data/results/source-validation/csv16/af-weather-widget/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md",
        interpretation="Strong v16 weather/widget partial row: source validation confirms 13 emitted versions and leaves five version mismatches explicit.",
        next_improvement="Use as another weather/no-native guard before changing AndroidX/Kotlin version selection.",
        validation_note="The v16 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 13/18 emitted Maven versions, with 5 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="study-tracker",
        name="Study Tracker 1.0.7",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "education", "productivity", "gradle-9.5"),
        expected_difficulty="Medium-high: no-native education/productivity app whose source tree exposes many version-band mismatches.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-study-tracker/report.json",
        validation_path="data/results/source-validation/csv16/study-tracker/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md",
        interpretation="Useful v16 education/productivity partial row: only three emitted versions validate, making the version-drift limitation visible.",
        next_improvement="Use its mismatch-heavy profile for future low-confidence and source-version calibration diagnostics.",
        validation_note="The v16 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 3/15 emitted Maven versions, with 12 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="calliope-mini",
        name="Calliope mini 2.0.9",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "education", "hardware", "bluetooth", "gradle-9.5"),
        expected_difficulty="Medium-high: no-native education/hardware companion app with Bluetooth/device dependencies and AndroidX drift.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-calliope-mini/report.json",
        validation_path="data/results/source-validation/csv16/calliope-mini/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md",
        interpretation="Useful v16 education/hardware partial row: source validation confirms 11 emitted versions and keeps seven mismatches explicit.",
        next_improvement="Use as a device-companion no-native guard for future reference-coverage changes.",
        validation_note="The v16 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 11/18 emitted Maven versions, with 7 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="fdroid-build-status",
        name="F-Droid Build Status 5.14.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "fdroid", "development", "monitoring", "gradle-9.5"),
        expected_difficulty="Medium-high: no-native F-Droid/development monitor with a broad but source-resolved dependency surface.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-fdroid-build-status/report.json",
        validation_path="data/results/source-validation/csv16/fdroid-build-status/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md",
        interpretation="Strong v16 F-Droid/development partial row: 16 emitted versions validate while eight mismatches remain honest.",
        next_improvement="Use as a development-tool guard for future source-version and low-confidence pruning work.",
        validation_note="The v16 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 16/24 emitted Maven versions, with 8 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="password-master",
        name="Password Master 1.5.1",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "password", "security", "strict-module-rescue"),
        expected_difficulty="High: no-native password/security app whose source tree uses the real `:passwordmaster` module instead of generic `:app`.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-password-master/report.json",
        validation_path="data/results/source-validation/csv16/password-master/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md",
        interpretation="Useful v16 security partial row: a strict module rescue captured the runtime tree and validated 13 emitted versions.",
        next_improvement="Use as a precedent for non-`:app` module probing before marking small F-Droid projects blocked.",
        validation_note="The v16 blocker rescue captured `:passwordmaster` `releaseRuntimeClasspath`; validation confirms 13/18 emitted Maven versions, with 5 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="todo-list-pfa",
        name="Todo List (PFA) 3.4.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "clean-candidate", "no-native", "privacy-friendly", "todo", "productivity", "gradle-9.5"),
        expected_difficulty="Medium-high: no-native privacy-friendly todo app with AndroidX dependency drift.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-todo-list-pfa/report.json",
        validation_path="data/results/source-validation/csv16/todo-list-pfa/source-validation/source-validation.json",
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md",
        interpretation="Useful v16 productivity partial row: source validation confirms nine emitted versions and records eight mismatches.",
        next_improvement="Use as another privacy-friendly/productivity guard for future version-disambiguation changes.",
        validation_note="The v16 Docker proof gate captured `:app` `releaseRuntimeClasspath`; validation confirms 9/17 emitted Maven versions, with 8 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="flying-carpet",
        name="Flying Carpet 9.0.8",
        role="source-linked-blocked",
        tags=("real", "source-linked", "blocked", "clean-candidate", "no-native", "file-transfer", "gradle-blocked"),
        expected_difficulty="High: no-native file-transfer app with APK/source proof, but the Docker Gradle lane cannot resolve a runtime dependency tree yet.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-flying-carpet/report.json",
        validation_path=None,
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md",
        interpretation="Source tarball and APK report exist, but every attempted runtime configuration fails before dependency-tree validation.",
        next_improvement="Investigate the `org/gradle/api/artifacts/SelfResolvingDependency` Gradle/toolchain blocker before admission to source-validated metrics.",
    ),
    RealCase(
        case_id="fitotrack",
        name="FitoTrack 15.6",
        role="source-linked-blocked",
        tags=("real", "source-linked", "blocked", "clean-candidate", "no-native", "fitness", "gps-tracker", "gradle-blocked"),
        expected_difficulty="High: no-native fitness tracker with APK/source proof, but Gradle configuration/toolchain failures block dependency-tree capture.",
        report_path="data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-fitotrack/report.json",
        validation_path=None,
        proof_path="docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md",
        interpretation="Source tarball and APK report exist, but the attempted runtime configurations fail before source validation can run.",
        next_improvement="Investigate the Gradle `SelfResolvingDependency` and missing `compileSdkVersion` blockers before admission to source-validated metrics.",
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
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "multidex", "email", "native", "validation-copy"),
        expected_difficulty="High: email/security APK with complex included Gradle build logic and a broad modern AndroidX/Kotlin runtime tree.",
        report_path="data/results/report-real-k9-thunderbird-android/report.json",
        validation_path="data/results/source-validation/k9-thunderbird-android-report-validation/source-validation.json",
        proof_path="docs/evaluation/K9_THUNDERBIRD_PROOF_BUNDLE.md",
        interpretation="Source-validated partial after an included-build/plugin-lite validation copy; identity recovery is useful, but six AndroidX versions mismatch source.",
        next_improvement="Use K-9 as email/security partial evidence and preserve the validation-copy proof as a build-system rescue precedent.",
        validation_note="Docker Gradle 9.5 captured `:app-k9mail` `fossReleaseRuntimeClasspath` from a validation-only plugin-lite/runtime-graph copy; validation confirms 5/11 emitted Maven versions, with 6 mismatches and 0 missing coordinates.",
    ),
    RealCase(
        case_id="jitsi-meet",
        name="Jitsi Meet 26.0.0",
        role="source-validated-partial",
        tags=("real", "partial", "source-validated", "react-native", "framework-boundary", "native-heavy", "multidex", "gradle-8.13", "node-npm"),
        expected_difficulty="Very high: React Native/WebRTC/Hermes APK with source proof, but dependency-tree generation needs Node/npm and F-Droid native prebuild tooling.",
        report_path="data/results/report-real-jitsi-meet/report.json",
        validation_path="data/results/source-validation/jitsi-meet-report-validation/source-validation.json",
        proof_path="docs/evaluation/JITSI_MEET_PROOF_BUNDLE.md",
        interpretation="Useful React Native/framework-boundary partial row; 5/7 emitted Maven components validate, while native libraries remain hash-only and two AndroidX versions mismatch source.",
        next_improvement="Keep React Native/WebRTC native files as boundary evidence and use the two AndroidX mismatches for version-disambiguation diagnostics.",
        validation_note="Docker Gradle 8.13 captured `:app` `releaseRuntimeClasspath` after Node/npm became available; SDK manager installed NDKs 27.1.12297006 and 26.1.10909125 during configuration; validation confirms 5/7 emitted Maven versions, with 2 mismatches and 0 missing coordinates.",
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
        real_case_ids=("fdroid", "opentracks", "tusky", "daily-dozen", "quickdic"),
        interpretation="These are the strongest exact-version claims, while Tusky and Daily Dozen are intentionally labeled sparse.",
        next_improvement="Add more non-sparse clean real APKs before making broad real-world accuracy claims.",
    ),
    GroupSpec(
        group_id="real-modern-partial",
        name="Modern AndroidX/Kotlin partials",
        expected_difficulty="High: version-band ties, Android target variants, KMP wrappers, and multidex/native combinations.",
        real_case_ids=("cryptomator-lite", "easy-xkcd", "moneywallet", "foxy-droid", "dolidroid", "openkeychain", "your-local-weather", "homefeed-rss-widget", "etar", "radiodroid", "simplelogin", "omni-notes", "primitive-ftpd", "floccus", "opencloud", "waistline", "sambalite", "nightdream", "password-generator", "todo-agenda", "keep-it-up", "c3nav", "opentopomap-viewer", "railway-station-photos", "linkdroid", "quasseldroid", "bimba", "wx", "egyptian-writer", "smouldering-durtles", "dns-hero", "baby-books", "odysee", "radarweather", "clock", "poet-assistant", "ftpclient", "json-list", "forecastie", "ultrasonic", "runnerup", "imapnotes3", "oceannex", "praktika-vortaro", "msggo", "af-weather-widget", "study-tracker", "calliope-mini", "fdroid-build-status", "password-master", "todo-list-pfa", "newpipe", "antennapod", "kde-connect", "wikipedia", "aegis", "nextcloud", "fairemail", "k9", "vlc-android", "osmand", "material-files", "davx5"),
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
        real_case_ids=("conversations", "aegis", "kde-connect", "fairemail", "k9"),
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
        real_case_ids=("flying-carpet", "fitotrack"),
        interpretation="The v16 pass keeps these APK/source rows visible but excludes them from source-validated metrics until a runtime dependency tree exists.",
        next_improvement="Try targeted Gradle/toolchain rescue profiles; do not count them as validated until `validate-source-deps` completes.",
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
