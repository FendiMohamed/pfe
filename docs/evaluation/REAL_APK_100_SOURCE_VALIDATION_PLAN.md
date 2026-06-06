# Real APK 100 Source-Validation Plan

This plan tracks the evaluation-growth goal: reach 100 source-validated real APKs while preserving honest clean, partial, blocked, report-only, and limitation buckets.

## Current Position

| Metric | Value |
|---|---:|
| Current source-validated real APKs | 102 |
| Target source-validated real APKs | 100 |
| Remaining source-validated real APKs needed | 0 |
| Current clean source-validated real APKs | 5 |
| Current partial source-validated real APKs | 97 |
| Current source-linked blocked APKs | 0 |

The clean non-sparse bucket remains open. Count growth must not weaken the proof gates.

## Admission Gates

A real APK can be counted only when these artifacts exist:

1. APK hash and generated report.
2. Matching F-Droid source tarball or equivalent source tag/commit evidence.
3. Resolved Gradle runtime dependency tree.
4. `validate-source-deps` JSON and Markdown output.
5. Clean or partial classification in the generated evaluation tables.

Rows that fail any gate stay report-only, source-linked blocked, smoke-real, or limitation evidence.

## Batch Strategy

| Batch | Target outcome | Cumulative target |
|---|---:|---:|
| v14 | 8 new source-validated rows | 83 |
| v15 | 8 new source-validated rows after strict blocker rescue | 91 |
| v16 | 11 new source-validated rows after Password Master strict-module rescue plus Flying Carpet/FitoTrack Gradle 8.13 rescue | 102 |
| v17 | no-Maven-signal audit, report-only AndroidX experiment, and Mastodon fork-family audit; boundary tightening or clean non-sparse quality pass next | 102+ |
| v18 | optional diversity/top-up rows if needed | 100+ |

Each batch should select more candidates than the desired promoted count because some APKs will be sparse, no-Maven-signal, Gradle-blocked, or unsuitable after report generation.

## v14 Selection Policy

v14 prioritizes high proof throughput:

- no native ABI in the F-Droid manifest;
- source tarball available in index-v2;
- target SDK 34+;
- moderate APK/source size;
- not already counted or selected in earlier clean-candidate sweeps;
- likely standard Android/Gradle project;
- diverse app families so the evaluation does not become only notes, browsers, or password utilities.

The v14 batch is saved in `configs/real_apk_clean_candidate_selection_v14.json`.

## v14 Result

v14 reported 8/8 selected APKs and promoted all 8 as source-validated partial rows:

- Bimba: 12/25 confirmed, 13 mismatches, 0 missing.
- wX: 12/19 confirmed, 7 mismatches, 0 missing.
- Egyptian Writer: 13/17 confirmed, 4 mismatches, 0 missing.
- Smouldering Durtles: 8/22 confirmed, 14 mismatches, 0 missing.
- DNS Hero: 4/11 confirmed, 7 mismatches, 0 missing.
- Baby Books: 10/29 confirmed, 18 mismatches, 1 missing after an Android-module-only validation copy pinned `:android`.
- Odysee: 10/15 confirmed, 5 mismatches, 0 missing after a Cordova validation copy added Docker SDK metadata and `XmlParser` compatibility.
- RadarWeather: 5/17 confirmed, 12 mismatches, 0 missing after an old-AGP validation copy added AGP-required namespace/BuildConfig settings.

The three former v14 blocked rows are now rescued and counted. They were no longer blocked at the end of v14.

## v15 Selection Policy

v15 kept the high-throughput/no-native approach but selected a fresh set from the local F-Droid index:

- source tarball available in index-v2;
- no native ABI recorded in the APK metadata;
- target SDK 35-36 where possible;
- not already counted or selected in prior sweeps;
- enough emitted Maven signal to make a source-validation row useful;
- app-family diversity across clock, poetry/reference, music/server, file transfer, fitness, JSON utility, notes/mail sync, and weather.

The v15 batch is saved in `configs/real_apk_clean_candidate_selection_v15.json`.

## v15 Result

v15 reported 8/8 selected APKs and promoted all 8 as source-validated partial rows after strict blocker rescue:

- Clock: 11/38 confirmed, 6 mismatches, 21 missing.
- Poet Assistant: 7/37 confirmed, 9 mismatches, 21 missing after a JCenter-to-Maven-Central validation copy.
- Ultrasonic: 12/39 confirmed, 10 mismatches, 17 missing after strict `:ultrasonic` module probing.
- FTPClient: 13/39 confirmed, 4 mismatches, 22 missing.
- RunnerUp: 16/39 confirmed, 4 mismatches, 19 missing after strict `latestReleaseRuntimeClasspath` flavor probing.
- Json List: 14/38 confirmed, 5 mismatches, 19 missing.
- ImapNotes3: 11/39 confirmed, 6 mismatches, 22 missing after strict `:ImapNotes3` module probing.
- Forecastie: 3/37 confirmed, 10 mismatches, 24 missing after redownloading a corrupt interrupted source tarball.

The three former v15 blocked rows are now rescued and counted. No current source-linked blocked APK rows remain.

## v16 Selection Policy

v16 intentionally selected more candidates than the 9 remaining rows needed for the 100-source-validated target:

- source tarball available in index-v2;
- no native ABI recorded in the APK metadata;
- not already counted or selected in prior sweeps;
- enough expected Maven signal to make a source-validation row useful;
- app-family diversity across cloud/API clients, dictionary/messaging, weather/widgets, education, development/F-Droid tooling, password/security, and privacy-friendly productivity.

The v16 batch is saved in `configs/real_apk_clean_candidate_selection_v16.json`.

## v16 Result

v16 reported 12/12 selected APKs. ProseReader emitted no Maven signal and stays report-only. Eleven source-linked rows advanced to proof, and all eleven were promoted as source-validated partial rows after the blocker rescue pass:

- OceanNex for DigitalOcean: 16/21 confirmed, 5 mismatches, 0 missing.
- Praktika Vortaro: 0/1 confirmed, 1 mismatch, 0 missing.
- MsgGo: 1/4 confirmed, 3 mismatches, 0 missing.
- AF Weather Widget: 13/18 confirmed, 5 mismatches, 0 missing.
- Study Tracker: 3/15 confirmed, 12 mismatches, 0 missing.
- Calliope mini: 11/18 confirmed, 7 mismatches, 0 missing.
- Flying Carpet: 11/17 confirmed, 6 mismatches, 0 missing after a Gradle 8.13 runtime-lane rescue for `:app` `releaseRuntimeClasspath`.
- FitoTrack: 5/18 confirmed, 13 mismatches, 0 missing after a Gradle 8.13 runtime-lane rescue for `:app` `releaseRuntimeClasspath`.
- F-Droid Build Status: 16/24 confirmed, 8 mismatches, 0 missing.
- Password Master: 13/18 confirmed, 5 mismatches, 0 missing after strict `:passwordmaster` module probing.
- Todo List (PFA): 9/17 confirmed, 8 mismatches, 0 missing.

The 100-source-validated-real-APK target is now exceeded at 102/100. No current source-linked blocked rows remain. Flying Carpet and FitoTrack were counted only after Docker proof captured runtime dependency trees and `validate-source-deps` completed.
