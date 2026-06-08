# Account Handoff Continuation Prompt

Paste this into the new chat/account:

```text
You are continuing an Android APK-to-SBOM/CVE extraction PFE project in:

C:\Users\PC CABA DZ\Documents\pfe-final

First, read these repo files before doing any work:

- AGENTS.md
- docs/codex/CODEX_CONTEXT.md
- TASKS.md
- docs/codex/VERSION_R8_EXPERIMENTS_SUMMARY_FOR_HANDOFF.md
- docs/evaluation/NEXT_REAL_APK_GROWTH_QUEUE.md
- docs/planning/IMPLEMENTATION_PLAN.md

Important behavior:

- Continue from repo truth, not from memory alone.
- Do not revert or delete existing dirty work. The worktree is intentionally dirty with many generated docs, scripts, reports, tests, APK artifacts, and evaluation outputs from prior passes.
- Keep evidence buckets separate: clean source-validated, partial source-validated, source-linked blocked, no-Maven-signal, smoke/limitation. Do not count blocked, source-linked-only, no-Maven-signal, or limitation rows as source-validated accuracy metrics.
- For real APK work, prefer batch-style execution. Use Docker for report/proof/Gradle validation where local Python or Gradle dependencies are missing.
- If commands need F-Droid, Gradle, Maven, or Docker network/access, request the needed approval rather than silently skipping work.

Latest completed checkpoint:

- Post-v16 optimization checkpoint:
  - Source-linked blockers remain closed at 0.
  - The no-Maven-signal lane is complete with an audit, AndroidX report-only experiment, and Mastodon fork-family report-only audit.
  - The limitation/boundary lane is complete with `docs/evaluation/LIMITATION_BOUNDARY_DASHBOARD.md`: 4 explicit limitation/boundary cases, 0 counted in accuracy, 2 native-heavy limitation rows, 2 obfuscation limitation rows, and Jitsi recorded as the hybrid Maven-validated/framework-native boundary case.
  - The wrong-version lane now has `docs/evaluation/WRONG_VERSION_OPTIMIZATION_DASHBOARD.md`: 636 emitted wrong-version rows, 38 unique coordinates, 96 APK cases, 0 source-linked blocked rows in scope, and 0 metric/scoring/SBOM changes.
  - The first guarded P1 wrong-version experiment is complete at `docs/evaluation/WRONG_VERSION_P1_COROUTINES_ANDROID_1_6_4_EXPERIMENT.md`: isolated `org.jetbrains.kotlinx:kotlinx-coroutines-android@1.6.4` fixes 20/20 target rows, but shared DB promotion is rejected because clean F-Droid regresses from source-confirmed `1.7.3` to `1.6.4`, and Organic Maps/Termux limitation-boundary report-only component sets change.
  - The reference DB coverage-first lane is now anchored at `docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md`: 106 source-tree cases, 12,082 source coordinate+version rows, 1,370 unique source coordinates, 3,391 unique source coordinate+version pairs, 18.4% coordinate coverage in the shared DB, 10.2% exact-version coverage, and 7.7% end-to-end exact source recall. This explicitly separates emitted-component confirmation (`927/1837`, 50.5%) from full dependency recall.
  - The source-observed reference catalog lane has started at `docs/evaluation/SOURCE_OBSERVED_REFERENCE_CATALOG.md`: `configs/source_observed_reference_catalog.json` and `configs/libraries.source_observed_versions.json` cover 1,370 source-observed coordinates / 3,391 source-version slots, with 1,361 bytecode-buildable coordinates / 3,347 buildable source-version slots and 9 metadata-only BOM skips.
  - The evaluation-only source-observed DB build is logged at `docs/evaluation/SOURCE_OBSERVED_REFERENCE_DB_BATCH_LOG.md`: batches 000-012 attempted the first 1000 source-version slots, downloaded 939 artifacts, recorded 61 real 404 download failures, stored 655 bytecode-bearing conversion records, and recorded 284 no-bytecode conversion skips in ignored `data/reference_db/reference_features_source_observed_versions.sqlite`.
  - Priority lanes are P1 Kotlin/coroutines source-version controls (147 rows), P1 AndroidX core/activity/fragment/lifecycle controls (259 rows), P2 ViewPager2/support AndroidX controls (157 rows), and P2 CVE-sensitive networking/JSON audits (38 rows).
  - Next work should continue the source-observed evaluation-only DB batches first: resume downloads at `--limit 100 --offset 1000`, compute the conversion offset from the current downloaded metadata count, then expand `configs/source_observed_reference_catalog.json` with `expand-reference-config --all-versions`, record artifact/no-bytecode skips, and only after that coverage/recall evaluation resume wrong-version optimization as the main lane.
- v16 reached and then exceeded the 100 source-validated real APK target.
- v16 selected 12 F-Droid APKs: OceanNex for DigitalOcean, Praktika Vortaro, MsgGo, AF Weather Widget, Study Tracker, Calliope mini, ProseReader, Flying Carpet, FitoTrack, F-Droid Build Status, Password Master, and Todo List (PFA).
- Reports generated for 12/12 APKs under `data/results/evaluation/clean-real-apk-candidate-sweep-v16/`.
- ProseReader emitted no Maven signal and stays report-only/no-Maven-signal.
- Eleven source-linked rows advanced through Docker proof gates; all eleven were promoted honestly as source-validated partial after the blocker rescue pass:
  - OceanNex for DigitalOcean 1.0.0: 16/21 confirmed, 5 mismatches, 0 missing from `:app` `freeReleaseRuntimeClasspath`.
  - Praktika Vortaro 0.26: 0/1 confirmed, 1 mismatch, 0 missing from `:app` `releaseRuntimeClasspath`.
  - MsgGo 3.9: 1/4 confirmed, 3 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
  - AF Weather Widget 3.2: 13/18 confirmed, 5 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
  - Study Tracker 1.0.7: 3/15 confirmed, 12 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
  - Calliope mini 2.0.9: 11/18 confirmed, 7 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
  - Flying Carpet 9.0.8: 11/17 confirmed, 6 mismatches, 0 missing from `:app` `releaseRuntimeClasspath` with `/opt/gradle-8.13/bin/gradle`.
  - FitoTrack 15.6: 5/18 confirmed, 13 mismatches, 0 missing from `:app` `releaseRuntimeClasspath` with `/opt/gradle-8.13/bin/gradle`.
  - F-Droid Build Status 5.14.0: 16/24 confirmed, 8 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
  - Password Master 1.5.1: 13/18 confirmed, 5 mismatches, 0 missing after strict `:passwordmaster` `releaseRuntimeClasspath` probing.
  - Todo List (PFA) 3.4.0: 9/17 confirmed, 8 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
- Flying Carpet and FitoTrack are no longer source-linked blocked. They were counted only after runtime dependency-tree capture and `validate-source-deps` output existed.
- The 100-real-APK target is now exceeded at 102/100. The clean non-sparse bucket remains open.

Previous completed checkpoint:

- v15 continued the 100 source-validated real APK target.
- v15 selected 8 F-Droid APKs: Clock, Poet Assistant, Ultrasonic, FTPClient, RunnerUp, Json List, ImapNotes3, and Forecastie.
- Reports generated for 8/8 APKs under `data/results/evaluation/clean-real-apk-candidate-sweep-v15/`.
- All 8 rows advanced through Docker proof gates and were promoted honestly as source-validated partial after targeted blocker rescue:
  - Clock 2.29: 11/38 confirmed, 6 mismatches, 21 missing from `:app` `releaseRuntimeClasspath`.
  - Poet Assistant 1.31.1: 7/37 confirmed, 9 mismatches, 21 missing after a JCenter-to-Maven-Central validation copy captured `:app` `releaseRuntimeClasspath`.
  - Ultrasonic 4.9.0: 12/39 confirmed, 10 mismatches, 17 missing after strict `:ultrasonic` `releaseRuntimeClasspath` probing.
  - FTPClient 3.0.1: 13/39 confirmed, 4 mismatches, 22 missing from `:app` `releaseRuntimeClasspath`.
  - RunnerUp 2.11.0.1: 16/39 confirmed, 4 mismatches, 19 missing after strict `:app` `latestReleaseRuntimeClasspath` flavor probing.
  - Json List 1.10: 14/38 confirmed, 5 mismatches, 19 missing from `:app` `releaseRuntimeClasspath`.
  - ImapNotes3 v1.4-07: 11/39 confirmed, 6 mismatches, 22 missing after strict `:ImapNotes3` `releaseRuntimeClasspath` probing.
  - Forecastie 1.23: 3/37 confirmed, 10 mismatches, 24 missing after the first interrupted/corrupt source tarball was moved aside and the source tarball was redownloaded.
- The former Ultrasonic, RunnerUp, and ImapNotes3 blocked rows are now source-validated partial rows. Generic probing missed their real module/flavor runtime configurations, but strict rescue profiles captured dependency trees and validation output.
- At the v15 checkpoint, the 100-real-APK target was at 91/100, with 9 more source-validated rows needed.
- The clean non-sparse bucket remains open.

Previous completed checkpoint:

- v14 was the first explicit growth batch for the 100 source-validated real APK target.
- v14 selected 8 F-Droid APKs: Bimba, wX, Egyptian Writer, Smouldering Durtles, Baby Books, Odysee, DNS Hero, and RadarWeather.
- Reports generated for 8/8 APKs under `data/results/evaluation/clean-real-apk-candidate-sweep-v14/`.
- All eight rows were advanced through Docker proof gates and promoted honestly as source-validated partial after targeted blocker rescue:
  - Bimba 3.99: 12/25 confirmed, 13 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
  - wX 55990: 12/19 confirmed, 7 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
  - Egyptian Writer 14.05.2026@0.1.0.1: 13/17 confirmed, 4 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
  - Smouldering Durtles 1.2.3: 8/22 confirmed, 14 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
  - DNS Hero 1.7.0: 4/11 confirmed, 7 mismatches, 0 missing after Gradle captured `:app` `fossReleaseRuntimeClasspath`.
  - Baby Books 0.9.2: 10/29 confirmed, 18 mismatches, 1 missing after an Android-module-only validation copy pinned `:android` and captured `releaseRuntimeClasspath`.
  - Odysee 0.0.124: 10/15 confirmed, 5 mismatches, 0 missing after a Cordova validation copy added Docker SDK metadata and `XmlParser` compatibility.
  - RadarWeather 6.7: 5/17 confirmed, 12 mismatches, 0 missing after an old-AGP validation copy added AGP-required namespace/BuildConfig settings.
- The v14 source-linked blocked set was closed by targeted rescues.

Previous completed checkpoint:

- Clean-candidate sweep v13 was started after the v12 evidence-growth pass to keep searching for a clean non-sparse real APK while adding honest no-native source-validated rows.
- v13 selected 6 F-Droid APKs: LibChecker, OpenTopoMap Viewer, Railway station photos, LinkDroid for Linkwarden, Quasseldroid, and TTRSS-Reader.
- Reports generated for 6/6 APKs under `data/results/evaluation/clean-real-apk-candidate-sweep-v13/`.
- Four high-signal rows were advanced through Docker proof gates and promoted honestly as source-validated partial:
  - OpenTopoMap Viewer 1.29: 13/22 confirmed, 9 mismatches, 0 missing after Gradle captured `:app` `fossReleaseRuntimeClasspath`.
  - Railway station photos 16.4.0: 18/23 confirmed, 5 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
  - LinkDroid for Linkwarden 2.1.9: 12/20 confirmed, 8 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
  - Quasseldroid 1.8.0: 14/17 confirmed, 3 mismatches, 0 missing from `:app` `releaseRuntimeClasspath`.
- LibChecker and TTRSS-Reader were collected/reported but left out of proof promotion because LibChecker was sparse and TTRSS-Reader emitted no Maven signal.
- The remaining source-linked blocked set was empty at that checkpoint.
- The clean non-sparse bucket remains open.

Previous completed checkpoint:

- Clean-candidate sweep v12 was started after the K-9 rescue to keep growing no-native real-APK evidence.
- v12 selected 6 F-Droid APKs: Password Generator, Todo Agenda, Keep it up, SkillApp, c3nav, and Nextcloud News.
- Reports generated for 6/6 APKs under `data/results/evaluation/clean-real-apk-candidate-sweep-v12/`.
- The strongest four rows were advanced through Docker proof gates and promoted honestly as source-validated partial:
  - Password Generator 1.9.0: 11/16 confirmed, 5 mismatches, 0 missing after strict `:passwordgenerator` module probing.
  - Todo Agenda 4.13.3: 10/16 confirmed, 6 mismatches, 0 missing after a validation-only copy omitted only the obsolete `archivesBaseName` output naming line.
  - Keep it up 1.11.1: 3/5 confirmed, 1 mismatch, 1 missing after strict `:keepitupmain` module probing.
  - c3nav 4.7.0: 7/14 confirmed, 7 mismatches, 0 missing from the nested `CongressRoutePlanner` `:app` runtime tree.
- SkillApp and Nextcloud News were collected/reported but left out of proof promotion because their emitted Maven signal was sparse and lower priority.
- At the v12 checkpoint, no source-linked blocked rows remained.
- The clean non-sparse bucket remains open.

Previous completed checkpoint:

- K-9 / Thunderbird Android `18.0`/39035 was rescued from the final source-linked blocked row and is now `source-validated-partial`.
- The successful validation lane used a validation-only plugin-lite/runtime-graph source copy at `data/results/source-validation/k9-thunderbird-android/source-plugin-lite`.
- Docker captured `:app-k9mail` `fossReleaseRuntimeClasspath` at `data/results/source-validation/k9-thunderbird-android/fossReleaseRuntimeClasspath.plugin-lite-runtimegraph-composefix.txt`.
- Source validation output is at `data/results/source-validation/k9-thunderbird-android-report-validation/source-validation.json` and `.md`.
- Result: 5/11 emitted Maven versions confirmed, 6 mismatches, 0 missing.

Previous completed checkpoint:

- Clean-candidate sweep v11 was started after v10.
- v11 candidates: floccus bookmark sync, Waistline, OpenCloud, NightDream, SambaLite.
- Reports generated for 5/5 APKs:
  - floccus: 13 Maven SBOM components, no native `.so`.
  - Waistline: 15 Maven SBOM components, no native `.so`.
  - OpenCloud: 22 Maven SBOM components, no native `.so`.
  - NightDream: 21 Maven SBOM components, no native `.so`.
  - SambaLite: 19 Maven SBOM components, no native `.so`.
- floccus, Waistline, OpenCloud, SambaLite, and NightDream were promoted honestly as source-validated partial:
  - floccus bookmark sync 5.9.1: 9/13 confirmed, 4 mismatches, 0 missing.
  - Waistline 3.10.1: 9/15 confirmed, 6 mismatches, 0 missing.
  - OpenCloud 1.2.3: 8/22 confirmed, 14 mismatches, 0 missing.
  - SambaLite 2.5.1: 16/19 confirmed, 3 mismatches, 0 missing.
  - NightDream 2.11.26: 15/21 confirmed, 6 mismatches, 0 missing.
- OpenCloud was rescued from the earlier proof-timeout/modern Gradle blocker:
  - blocker profile: `configs/real_apk_blocker_rescue_profiles.json`;
  - workflow doc: `docs/evaluation/REAL_APK_BLOCKER_RESCUE_WORKFLOW.md`;
  - validation-only source copy disables KSP/Kotlin/Parcelize/Detekt/Sonar build-time plugins only for dependency-tree capture;
  - Docker captured `:opencloudApp` `originalReleaseRuntimeClasspath` and source validation completed.
- Waistline was rescued from the earlier Cordova Gradle blocker:
  - blocker profile: `configs/real_apk_blocker_rescue_profiles.json`;
  - workflow doc: `docs/evaluation/REAL_APK_BLOCKER_RESCUE_WORKFLOW.md`;
  - validation-only source copy clones only `platforms/android`, adds Docker SDK `local.properties`, imports Cordova's Groovy `XmlParser`, aligns build-tools metadata with Docker build-tools 36.0.0, and replaces the plugin `jcenter()` repository call with the archived Maven URL;
  - Docker captured `:app` `releaseRuntimeClasspath` and source validation completed.
- The clean non-sparse bucket remains open.

Previous completed checkpoint:

- Clean-candidate sweep v10 was completed.
- v10 candidates: Etar - OpenSource Calendar, RadioDroid, SimpleLogin Anti-spam, Omni Notes, Primitive FTPd.
- Reports generated for 5/5 APKs.
- Source-validation proof gates completed in Docker.
- Promoted five honest source-validated partial rows:
  - Etar - OpenSource Calendar 1.0.55: 15/38 confirmed, 2 mismatches, 21 missing.
  - RadioDroid 0.86: 5/39 confirmed, 15 mismatches, 19 missing after JCenter-to-Maven-Central validation-copy rescue with Gradle 8.13.
  - SimpleLogin Anti-spam 1.22.0: 9/39 confirmed, 13 mismatches, 17 missing after Detekt-only validation-copy rescue with Gradle 8.13.
  - Omni Notes 6.3.1: 4/39 confirmed, 16 mismatches, 19 missing after Sonar/test-logger/Jacoco validation-copy rescue with Gradle 8.13.
  - Primitive FTPd 8.1: 12/38 confirmed, 4 mismatches, 22 missing after strict `:primitiveFTPd` module-profile rescue.
- Rescued two more blockers after the v10/v11 pass:
  - ownCloud 4.8.0: 7/22 confirmed, 14 mismatches, 1 missing after a Kotlin/KSP/Parcelize/Ktlint/Detekt/Sonar/CycloneDX validation-copy rescue with Docker Gradle 8.13 and pinned `:owncloudApp`.
  - Jitsi Meet 26.0.0: 5/7 confirmed, 2 mismatches, 0 missing after a React Native/Node/npm source-compatible Gradle 8.13 rescue for `:app` `releaseRuntimeClasspath`.
- The clean non-sparse bucket remains open.

Latest thesis/evaluation stats after the v16 blocker rescue:

- Controlled fixtures: 72 cases, 84/84 expected versions confirmed.
- Clean source-validated real APKs: 5 cases, 47/47 emitted Maven versions confirmed.
- Partial source-validated real APKs: 97 cases, 880/1790 emitted Maven versions confirmed.
- Overall source-validated real APKs: 102 cases, 927/1837 emitted Maven versions confirmed.
- Source-linked blocked cases: 0.
- Limitation/boundary cases: 4.
- 100-real-APK target: 102/100 source-validated real APKs, 0 remaining.

Latest v16 artifacts:

- docs/evaluation/REAL_APK_100_SOURCE_VALIDATION_PLAN.md
- configs/real_apk_clean_candidate_selection_v16.json
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_SWEEP_V16.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V16_PASSWORD_MASTER_RESCUE.md
- data/results/evaluation/clean-real-apk-candidate-sweep-v16.json
- data/results/evaluation/clean-real-apk-candidate-proof-status-v16.json
- data/results/evaluation/clean-real-apk-candidate-proof-status-v16-password-master-rescue.json
- data/results/evaluation/clean-real-apk-candidate-sweep-v16/
- data/results/source-validation/csv16/{oceannex,praktika-vortaro,msggo,af-weather-widget,study-tracker,calliope-mini,fdroid-build-status,password-master,todo-list-pfa,flying-carpet,fitotrack}/
- data/source/clean-real-apk-candidate-sweep-v16/
- data/test_apks/real/{oceannex,praktika-vortaro,msggo,af-weather-widget,study-tracker,calliope-mini,prosereader,flying-carpet,fitotrack,fdroid-build-status,password-master,todo-list-pfa}/

Latest v14 artifacts:

- configs/real_apk_clean_candidate_selection_v14.json
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_SWEEP_V14.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V14.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V14_RESCUE.md
- data/results/evaluation/clean-real-apk-candidate-sweep-v14.json
- data/results/evaluation/clean-real-apk-candidate-proof-status-v14.json
- data/results/evaluation/clean-real-apk-candidate-proof-status-v14-rescue.json
- data/results/evaluation/clean-real-apk-candidate-sweep-v14/
- data/results/source-validation/csv14/{bimba,wx,egyptian-writer,smouldering-durtles,dns-hero,baby-books,odysee,radarweather}/
- data/source/clean-real-apk-candidate-sweep-v14/
- data/test_apks/real/{bimba,wx,egyptian-writer,smouldering-durtles,baby-books,odysee,dns-hero,radarweather}/

Latest v13 artifacts:

- configs/real_apk_clean_candidate_selection_v13.json
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_SWEEP_V13.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V13.md
- data/results/evaluation/clean-real-apk-candidate-sweep-v13.json
- data/results/evaluation/clean-real-apk-candidate-proof-status-v13.json
- data/results/evaluation/clean-real-apk-candidate-sweep-v13/
- data/results/source-validation/csv13/{opentopomap-viewer,railway-station-photos,linkdroid,quasseldroid}/
- data/source/clean-real-apk-candidate-sweep-v13/
- data/test_apks/real/{libchecker,opentopomap-viewer,railway-station-photos,linkdroid,quasseldroid,ttrss-reader}/

Latest v12 artifacts:

- configs/real_apk_clean_candidate_selection_v12.json
- configs/real_apk_blocker_rescue_profiles.json
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_SWEEP_V12.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V12.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V12_PASSWORD_GENERATOR.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V12_TODO_AGENDA.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V12_KEEP_IT_UP.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V12_C3NAV.md
- data/results/evaluation/clean-real-apk-candidate-sweep-v12.json
- data/results/evaluation/clean-real-apk-candidate-proof-status-v12.json
- data/results/evaluation/clean-real-apk-candidate-sweep-v12/
- data/results/source-validation/csv12/{password-generator,todo-agenda,keep-it-up,c3nav}/
- data/source/clean-real-apk-candidate-sweep-v12/
- data/test_apks/real/{password-generator,todo-agenda,keep-it-up,skillapp,c3nav,nextcloud-news}/

Latest v11 artifacts:

- configs/real_apk_clean_candidate_selection_v11.json
- configs/real_apk_blocker_rescue_profiles.json
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_SWEEP_V11.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V11.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V11_OPENCLOUD_RESCUE.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V11_WAISTLINE_RESCUE.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V11.md
- docs/evaluation/REAL_APK_BLOCKER_RESCUE_WORKFLOW.md
- data/results/evaluation/clean-real-apk-candidate-sweep-v11.json
- data/results/evaluation/clean-real-apk-candidate-sweep-v11-proof-status.json
- data/results/evaluation/clean-real-apk-candidate-sweep-v11-opencloud-rescue-status.json
- data/results/evaluation/clean-real-apk-candidate-sweep-v11-waistline-rescue-status.json
- data/results/evaluation/clean-real-apk-candidate-sweep-v11/
- data/results/source-validation/csv11/
- data/source/csv11/
- data/test_apks/real/{floccus,waistline,opencloud,nightdream,sambalite}/

Latest v10 artifacts:

- configs/real_apk_clean_candidate_selection_v10.json
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_SWEEP_V10.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V10.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V10.md
- data/results/evaluation/clean-real-apk-candidate-sweep-v10.json
- data/results/evaluation/clean-real-apk-candidate-sweep-v10-proof-status.json
- data/results/evaluation/clean-real-apk-candidate-sweep-v10/
- data/results/source-validation/csv10/
- data/source/csv10/
- data/test_apks/real/{etar,radiodroid,simplelogin,omni-notes,primitive-ftpd}/

Latest v9 ownCloud rescue artifacts:

- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V9_OWNCLOUD_RESCUE.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V9.md
- docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V9.md
- docs/evaluation/REAL_APK_BLOCKED_APK_TRIAGE.md
- data/results/evaluation/clean-real-apk-candidate-sweep-v9-owncloud-rescue-status.json
- data/results/evaluation/clean-real-apk-candidate-sweep-v9-proof-status.json
- data/results/source-validation/csv9/owncloud/source-validation/source-validation.json

Latest Jitsi rescue artifacts:

- docs/evaluation/JITSI_MEET_PROOF_BUNDLE.md
- docs/evaluation/REAL_APK_BLOCKED_APK_TRIAGE.md
- data/results/source-validation/jitsi-meet/releaseRuntimeClasspath.txt
- data/results/source-validation/jitsi-meet/gradle-exit-code.txt
- data/results/source-validation/jitsi-meet-report-validation/source-validation.json
- data/results/source-validation/jitsi-meet-report-validation/source-validation.md

Latest K-9 rescue artifacts:

- docs/evaluation/K9_THUNDERBIRD_PROOF_BUNDLE.md
- docs/evaluation/K9_BLOCKER_DIAGNOSTICS.md
- docs/evaluation/REAL_APK_BLOCKED_APK_TRIAGE.md
- data/results/source-validation/k9-thunderbird-android/source-plugin-lite/
- data/results/source-validation/k9-thunderbird-android/source-plugin-lite/k9-runtime-project-graph.txt
- data/results/source-validation/k9-thunderbird-android/fossReleaseRuntimeClasspath.plugin-lite-runtimegraph-composefix.txt
- data/results/source-validation/k9-thunderbird-android-report-validation/source-validation.json
- data/results/source-validation/k9-thunderbird-android-report-validation/source-validation.md

Latest verification after the P1 wrong-version coroutines experiment:

- Docker `python scripts/evaluate_wrong_version_p1_experiment.py --reuse-existing`: passed and regenerated the rejected experiment summary.
- `python scripts\build_wrong_version_optimization_dashboard.py`: passed and preserved the completed-experiment table.
- `python scripts\build_thesis_artifact_index.py`: passed.
- `python -m compileall scripts\evaluate_wrong_version_p1_experiment.py scripts\build_wrong_version_optimization_dashboard.py scripts\build_thesis_artifact_index.py`: passed.
- Docker `python -m compileall src scripts tests`: passed.
- JSON validation for the wrong-version experiment summary and dashboard output: passed.
- git diff --check: passed with only normal Windows LF/CRLF warnings.
- JSON validation for the v16 selection/sweep/proof outputs, APK type evaluation, thesis evaluation tables, thesis artifact index, dataset coverage matrix, and MVP cons plan: passed.
- Python compile/compileall checks for touched scripts and project code: passed.
- Stale-count scan for old 91/100 and 829/1666 thesis totals: passed for current docs; only historical checkpoint rows may mention earlier totals.
- git diff --check: passed with only normal Windows LF/CRLF warnings.

What changed in MVP architecture/tool behavior recently:

- The v14 real-APK pass and follow-up blocker rescue did not change matcher scoring, selected Maven versions, SBOM component selection, CVE/OSV labeling, reference DB contents, or production architecture. It added eight source-validated partial metrics rows: Bimba, wX, Egyptian Writer, Smouldering Durtles, DNS Hero, Baby Books, Odysee, and RadarWeather. The three former v14 blockers were rescued through validation-only Gradle/Cordova/AGP lanes and are now counted only because dependency-tree capture and `validate-source-deps` both succeeded.
- The v16 real-APK pass did not change matcher scoring, selected Maven versions, SBOM component selection, CVE/OSV labeling, reference DB contents, or production architecture. It added eleven source-validated partial metrics rows: OceanNex, Praktika Vortaro, MsgGo, AF Weather Widget, Study Tracker, Calliope mini, Flying Carpet, FitoTrack, F-Droid Build Status, Password Master, and Todo List (PFA). Password Master added one strict `:passwordmaster` runtime dependency-tree rescue profile. Flying Carpet and FitoTrack added a Gradle 8.13 runtime-lane rescue profile and are counted only because dependency-tree capture and `validate-source-deps` succeeded.
- The v15 real-APK pass did not change matcher scoring, selected Maven versions, SBOM component selection, CVE/OSV labeling, reference DB contents, or production architecture. It added eight source-validated partial metrics rows: Clock, Poet Assistant, Ultrasonic, FTPClient, RunnerUp, Json List, ImapNotes3, and Forecastie. Poet Assistant added one validation-only JCenter-to-Maven-Central rescue lane for dependency-tree capture; Ultrasonic, RunnerUp, and ImapNotes3 were later rescued through strict module/flavor runtime dependency-tree profiles.
- The v13 real-APK pass did not change matcher scoring, selected Maven versions, SBOM component selection, CVE/OSV labeling, reference DB contents, or production architecture. It added four source-validated partial metrics rows: OpenTopoMap Viewer, Railway station photos, LinkDroid for Linkwarden, and Quasseldroid.
- The v12 real-APK pass did not change matcher scoring, selected Maven versions, SBOM component selection, CVE/OSV labeling, reference DB contents, or production architecture. It added four source-validated partial metrics rows: Password Generator, Todo Agenda, Keep it up, and c3nav. It also added strict module hints for `:passwordgenerator`, `:keepitupmain`, and c3nav `:app`, plus a validation-only Todo Agenda archive-name compatibility copy for dependency-tree capture.
- The ownCloud rescue did not change matcher scoring, selected Maven versions, SBOM component selection, CVE/OSV labeling, reference DB contents, or production architecture. It added one validation-only blocker rescue profile/helper and promoted ownCloud to source-validated partial evidence after Docker captured `:owncloudApp` `originalReleaseRuntimeClasspath` and `validate-source-deps` completed.
- The Jitsi rescue did not change matcher scoring, selected Maven versions, SBOM component selection, CVE/OSV labeling, reference DB contents, or production architecture. It promoted Jitsi to source-validated partial evidence after Docker captured `:app` `releaseRuntimeClasspath` with Gradle 8.13 and Node/npm available; native React Native/WebRTC/Hermes files remain hash-only boundary evidence.
- The v11 real-APK pass did not change matcher scoring, selected Maven versions, SBOM component selection, CVE/OSV labeling, reference DB contents, or production architecture. It added five source-validated partial metrics rows: floccus, Waistline, OpenCloud, SambaLite, and NightDream. It also added validation-only blocker rescue profiles for repeated Gradle/source-tree proof blockers, including OpenCloud's modern Gradle lane and Waistline's Cordova lane.
- The v10 real-APK pass did not change matcher scoring, selected Maven versions, SBOM component selection, CVE/OSV labeling, reference DB contents, or production architecture.
- Earlier dirty work in this same workspace already includes matcher/report changes such as guarded version-unique literal/context reranking, composite family shortlist default promotion, and generic version uncertainty reporting. Do not revert these.
- The R8/obfuscation work is intentionally diagnostic/report-only unless explicitly enabled. Do not wire Phase 5 R8 suggestions into default matcher scoring, selected versions, SBOM output, vulnerability labels, or source-validation metrics without fresh controls.

Next recommended task:

Continue from docs/evaluation/NO_MAVEN_SIGNAL_AUDIT.md, docs/evaluation/NO_MAVEN_SIGNAL_DIAGNOSTICS.md, docs/evaluation/NO_MAVEN_ANDROIDX_REPORT_ONLY_EXPERIMENT.md, docs/evaluation/MASTODON_FORK_FAMILY_REPORT_ONLY_AUDIT.md, docs/evaluation/LIMITATION_BOUNDARY_DASHBOARD.md, docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md, docs/evaluation/SOURCE_OBSERVED_REFERENCE_CATALOG.md, docs/evaluation/SOURCE_OBSERVED_REFERENCE_DB_BATCH_LOG.md, docs/evaluation/WRONG_VERSION_OPTIMIZATION_DASHBOARD.md, docs/evaluation/WRONG_VERSION_P1_COROUTINES_ANDROID_1_6_4_EXPERIMENT.md, docs/evaluation/NO_MAVEN_SIGNAL_AUDIT_PREP.md, docs/planning/RESEARCH_BACKED_REAL_APK_OPTIMIZATION_PLAN.md, docs/evaluation/NEXT_REAL_APK_GROWTH_QUEUE.md, and docs/evaluation/REAL_APK_100_SOURCE_VALIDATION_PLAN.md. The target of 100 source-validated real APKs is exceeded at 102/100, and no current source-linked blocked rows remain. The no-Maven-signal audit is complete: 0/4 are true runtime dependency-free controls, Privacy Browser/monocles browser/Blue Square Speedometer are AndroidX identity-coverage miss controls, and Mastodon is a `me.grishka.litex:*` fork-family/reference boundary with weak direct Gson evidence. `scripts/build_no_maven_signal_diagnostics.py` now generates JSON/CSV/Markdown dashboard seed artifacts. `apk-sbom no-maven-androidx-experiment` and `scripts/build_no_maven_androidx_report_only_experiment.py` now surface 6 source-backed AndroidX report-only candidates, keep 8 weak rows suppressed, and record 0 default/SBOM/source-validation metric changes. `apk-sbom no-maven-fork-family-experiment` and `scripts/build_mastodon_fork_family_report_only_audit.py` now surface 2 `me.grishka.litex:*` fork-family report-only suggestions and 1 weak direct Gson suggestion, keep 7 fork rows suppressed, and record 0 default/SBOM/source-validation metric changes. `scripts/build_limitation_boundary_dashboard.py` records 4 explicit limitation/boundary cases, 0 counted in accuracy, 2 native-heavy limitation rows, 2 obfuscation limitation rows, and Jitsi as the hybrid framework/native row. `scripts/build_reference_db_coverage_dashboard.py` records the honest denominator: 106 source-tree cases, 12,082 source coordinate+version rows, 18.4% coordinate coverage, 10.2% exact-version coverage, and 7.7% end-to-end exact source recall. `scripts/build_source_observed_reference_catalog.py` turns that denominator into source-observed reference growth inputs: 1,370 coordinates, 3,391 source-version slots, 1,361 buildable coordinates, 3,347 buildable source-version slots, and 9 metadata-only BOM skips. Batches 000-012 of the evaluation-only DB build attempted the first 1000 source-version slots, downloaded 939 artifacts, recorded 61 real 404 download failures, stored 655 bytecode-bearing conversion records, and recorded 284 no-bytecode conversion skips in ignored `data/reference_db/reference_features_source_observed_versions.sqlite`; resume downloads at `--limit 100 --offset 1000`. `scripts/build_wrong_version_optimization_dashboard.py` records 636 emitted wrong-version rows across 38 coordinates and 96 APK cases, but this lane is now behind coverage-first broad reference evaluation. The first P1 coroutines Android source-version experiment fixes 20/20 target rows but is rejected for promotion due to 3 control regressions; do not add rows just to inflate the count, and do not present emitted-component confirmation as full dependency recall.

Suggested first actions:

1. Run git status --short and do not clean the tree.
2. Read the files listed above.
3. Use `docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md`, `docs/evaluation/SOURCE_OBSERVED_REFERENCE_CATALOG.md`, and `docs/evaluation/SOURCE_OBSERVED_REFERENCE_DB_BATCH_LOG.md` before choosing the next lane; continue source-observed evaluation-only DB batches before more mainline wrong-version optimization.
4. Use `docs/evaluation/WRONG_VERSION_OPTIMIZATION_DASHBOARD.md` plus `docs/evaluation/WRONG_VERSION_P1_COROUTINES_ANDROID_1_6_4_EXPERIMENT.md` when wrong-version work resumes; do not promote plain `kotlinx-coroutines-android@1.6.4`, because it regresses F-Droid and limitation-boundary controls.
5. Inspect configs/real_apk_clean_candidate_selection_v16.json and previous v5-v15 selection configs only if selecting new APKs; avoid repeat candidates.
6. For blocker-style continuation, inspect `configs/real_apk_blocker_rescue_profiles.json` and `docs/evaluation/REAL_APK_BLOCKED_APK_TRIAGE.md` for Flying Carpet/FitoTrack rescue precedent before selecting any new candidates.
7. Use Docker for report/proof work; local Python lacks required project dependencies.
8. If selecting another batch, use the local F-Droid index at data/results/evaluation/fdroid-index-v2.json and save it as the next numbered selection config.
9. Regenerate canonical docs/tables if any row is admitted:
   - python scripts/build_apk_type_evaluation.py
   - python scripts/build_thesis_evaluation_tables.py
   - python scripts/build_thesis_artifact_index.py
   - python scripts/build_dataset_coverage_matrix.py
10. Verify with local compileall, Docker compileall, Docker pytest -q, and git diff --check.
```
