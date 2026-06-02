# Version-Band Tie Evidence

This audit summarizes current source-validation mismatches for risky AndroidX/Okio version bands. It is evidence for future matcher rules; it is not source-result forcing.

Control root: `data\results\experiments\markor-core-1-9-0-experiment`
Comparison experiment root: `data\results\experiments\markor-coverage-gaps-experiment`

## Classification Counts

| Classification | Count |
|---|---:|
| artifact-family-or-source-coordinate-nuance | 2 |
| bytecode-evidence-prefers-selected-version | 5 |
| feature-equivalent-version-tie | 3 |
| missing-reference-coverage-helped-in-experiment | 2 |
| near-tie-with-source-candidate | 2 |
| source-version-not-in-reference-db | 5 |

## Isolated Experiment Results

| Experiment | Regressed cases | Improved cases | Evidence |
|---|---|---|---|
| app-era-activity-1.9.2-only | fdroid | nextcloud-android | `data\results\experiments\app-era-coherence-activity-only-vs-current-control.json` |
| app-era-viewpager-beta-only | newpipe, antennapod | nextcloud-android | `data\results\experiments\app-era-coherence-viewpager-beta-only-vs-current-control.json` |
| Markor coverage-gap experiment DB | fdroid, opentracks, newpipe, antennapod, kde-connect, wikipedia-android, aegis-authenticator | markor | `data\results\experiments\markor-coverage-gaps-vs-current-control.json` |
| Markor core 1.9.0 experiment DB | none | markor | `data\results\experiments\markor-core-1-9-0-vs-current-control.json` |

## Mismatch Evidence

| Case | Coordinate | MVP | Source | Gap | Classification | Next action |
|---|---|---:|---|---:|---|---|
| aegis-authenticator | `androidx.viewpager2:viewpager2` | 1.0.0 | 1.1.0 | 0.016995 | bytecode-evidence-prefers-selected-version | keep as documented limitation unless a family-specific signal is found |
| antennapod | `androidx.core:core` | 1.15.0 | 1.16.0 | 0.020692 | bytecode-evidence-prefers-selected-version | keep as documented limitation unless a family-specific signal is found |
| conversations | `androidx.concurrent:concurrent-futures` | 1.1.0 | 1.3.0 | 0.000953 | near-tie-with-source-candidate | needs independent evidence; generic recency would regress other cases |
| conversations | `androidx.startup:startup-runtime` | 1.1.1 | 1.2.0 | 0.000655 | feature-equivalent-version-tie | consider an ambiguity downgrade or independent dependency/app-era support, not a version force |
| conversations | `androidx.lifecycle:lifecycle-runtime-android` | 2.9.0 | not found |  | artifact-family-or-source-coordinate-nuance | handle as coordinate-family/reporting nuance before version calibration |
| kde-connect | `androidx.viewpager2:viewpager2` | 1.1.0 | 1.1.0-beta02 |  | source-version-not-in-reference-db | do not promote globally; ViewPager2 beta experiment regressed NewPipe and AntennaPod |
| markor | `androidx.concurrent:concurrent-futures` | 1.1.0 | 1.0.0 |  | missing-reference-coverage-helped-in-experiment | do not promote globally; Markor coverage-gap experiment regressed multiple controls |
| markor | `androidx.activity:activity` | 1.10.1 | 1.6.0 |  | missing-reference-coverage-helped-in-experiment | do not promote globally; Markor coverage-gap experiment regressed AntennaPod |
| newpipe | `androidx.startup:startup-runtime` | 1.1.1 | 1.2.0 | 0.00052 | feature-equivalent-version-tie | consider an ambiguity downgrade or independent dependency/app-era support, not a version force |
| newpipe | `androidx.lifecycle:lifecycle-runtime-android` | 2.9.0 | 2.9.4 | 0.000024 | near-tie-with-source-candidate | needs independent evidence; generic recency would regress other cases |
| nextcloud-android | `androidx.viewpager2:viewpager2` | 1.1.0 | 1.1.0-beta02 |  | source-version-not-in-reference-db | do not promote globally; ViewPager2 beta experiment regressed NewPipe and AntennaPod |
| nextcloud-android | `androidx.concurrent:concurrent-futures` | 1.3.0 | 1.2.0 |  | source-version-not-in-reference-db | keep as documented limitation unless a family-specific signal is found |
| nextcloud-android | `androidx.startup:startup-runtime` | 1.2.0 | 1.1.1 | 0.09919 | bytecode-evidence-prefers-selected-version | keep as documented limitation unless a family-specific signal is found |
| nextcloud-android | `com.squareup.okio:okio-jvm` | 3.16.4 | 3.9.0 |  | source-version-not-in-reference-db | keep as documented limitation unless a family-specific signal is found |
| nextcloud-android | `androidx.swiperefreshlayout:swiperefreshlayout` | 1.0.0 | 1.2.0 | 0.028428 | bytecode-evidence-prefers-selected-version | keep as documented limitation unless a family-specific signal is found |
| nextcloud-android | `androidx.activity:activity` | 1.10.1 | 1.9.2 |  | source-version-not-in-reference-db | do not promote globally; Activity-only experiment regressed F-Droid |
| nextcloud-android | `com.squareup.okhttp3:okhttp-android` | 5.3.2 | not found |  | artifact-family-or-source-coordinate-nuance | handle as coordinate-family/reporting nuance before version calibration |
| wikipedia-android | `androidx.startup:startup-runtime` | 1.1.1 | 1.2.0 | 0.000585 | feature-equivalent-version-tie | consider an ambiguity downgrade or independent dependency/app-era support, not a version force |
| wikipedia-android | `androidx.viewpager2:viewpager2` | 1.0.0 | 1.1.0 | 0.014798 | bytecode-evidence-prefers-selected-version | keep as documented limitation unless a family-specific signal is found |

## Candidate Details

### aegis-authenticator - `androidx.viewpager2:viewpager2`

- Current selected: `1.0.0` (score 0.500888, status candidate)
- Source version(s): `1.1.0`
- Classification: bytecode-evidence-prefers-selected-version
- Next action: keep as documented limitation unless a family-specific signal is found

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.0.0 | 0.500888 | no | 0.444444 | 0.242105 | 0.49076 | 0.636364 | 0.45098 | 0 | 0 |
| 1.1.0 | 0.483893 | yes | 0.4 | 0.225806 | 0.48608 | 0.636364 | 0.444257 | 0.015203 | 1 |

Full experiment selected: `1.0.0` (score 0.500888)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.0.0 | 0.500888 | no | 0.444444 | 0.242105 | 0.49076 | 0.636364 | 0.45098 | 0 | 0 |
| 1.1.0 | 0.483893 | yes | 0.4 | 0.225806 | 0.48608 | 0.636364 | 0.444257 | 0.015203 | 1 |

### antennapod - `androidx.core:core`

- Current selected: `1.15.0` (score 0.489508, status candidate)
- Source version(s): `1.16.0`
- Classification: bytecode-evidence-prefers-selected-version
- Next action: keep as documented limitation unless a family-specific signal is found

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.9.0 | 0.505081 | no |  |  |  |  |  |  | 0 |
| 1.15.0 | 0.489508 | no | 0.441414 | 0.372565 | 0.62248 | 0.624085 | 0.567023 | 0 | 0 |
| 1.16.0 | 0.484389 | yes |  |  |  |  |  |  | 0 |
| 1.18.0 | 0.471086 | no |  |  |  |  |  |  | 0 |

Full experiment selected: `1.15.0` (score 0.489508)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.9.0 | 0.505081 | no |  |  |  |  |  |  | 0 |
| 1.15.0 | 0.489508 | no | 0.441414 | 0.372565 | 0.62248 | 0.624085 | 0.567023 | 0 | 0 |
| 1.16.0 | 0.484389 | yes |  |  |  |  |  |  | 0 |
| 1.18.0 | 0.471086 | no |  |  |  |  |  |  | 0 |

### conversations - `androidx.concurrent:concurrent-futures`

- Current selected: `1.1.0` (score 0.680886, status candidate)
- Source version(s): `1.3.0`
- Classification: near-tie-with-source-candidate
- Next action: needs independent evidence; generic recency would regress other cases

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.0 | 0.680886 | no | 0.7 | 0.514851 | 0.720787 | 0.975 | 0.662338 | 0 | 0 |
| 1.3.0 | 0.679933 | yes | 0.7 | 0.509804 | 0.720787 | 0.975 | 0.658065 | 0 | 0 |

Full experiment selected: `1.0.0` (score 0.680892)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.0.0 | 0.680892 | no | 0.7 | 0.514851 | 0.720787 | 0.975 | 0.662338 | 0 | 0 |
| 1.1.0 | 0.680886 | no | 0.7 | 0.514851 | 0.720787 | 0.975 | 0.662338 | 0 | 0 |
| 1.3.0 | 0.679933 | yes | 0.7 | 0.509804 | 0.720787 | 0.975 | 0.658065 | 0 | 0 |

### conversations - `androidx.startup:startup-runtime`

- Current selected: `1.1.1` (score 0.548511, status candidate)
- Source version(s): `1.2.0`
- Classification: feature-equivalent-version-tie
- Next action: consider an ambiguity downgrade or independent dependency/app-era support, not a version force

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.1 | 0.548511 | no | 0.6 | 0.5 | 0.060123 | 0.5 | 0.8 | 0 | 0 |
| 1.2.0 | 0.547856 | yes | 0.6 | 0.5 | 0.060123 | 0.5 | 0.8 | 0 | 0 |

Full experiment selected: `1.1.1` (score 0.548511)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.1 | 0.548511 | no | 0.6 | 0.5 | 0.060123 | 0.5 | 0.8 | 0 | 0 |
| 1.2.0 | 0.547856 | yes | 0.6 | 0.5 | 0.060123 | 0.5 | 0.8 | 0 | 0 |

### conversations - `androidx.lifecycle:lifecycle-runtime-android`

- Current selected: `2.9.0` (score 0.406129, status uncertain)
- Source version(s): `not found`
- Classification: artifact-family-or-source-coordinate-nuance
- Next action: handle as coordinate-family/reporting nuance before version calibration

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2.9.0 | 0.406129 | no | 0.258065 | 0.246753 | 0.279006 | 0.454545 | 0.34717 | 0 | 0 |
| 2.9.4 | 0.406103 | no |  |  |  |  |  |  | 0 |
| 2.10.0 | 0.405064 | no |  |  |  |  |  |  | 0 |
| 2.8.7 | 0.402486 | no |  |  |  |  |  |  | 0 |

Full experiment selected: `2.9.0` (score 0.406129)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2.9.0 | 0.406129 | no | 0.258065 | 0.246753 | 0.279006 | 0.454545 | 0.34717 | 0 | 0 |
| 2.9.4 | 0.406103 | no |  |  |  |  |  |  | 0 |
| 2.10.0 | 0.405064 | no |  |  |  |  |  |  | 0 |
| 2.8.7 | 0.402486 | no |  |  |  |  |  |  | 0 |

### kde-connect - `androidx.viewpager2:viewpager2`

- Current selected: `1.1.0` (score 0.551132, status candidate)
- Source version(s): `1.1.0-beta02`
- Classification: source-version-not-in-reference-db
- Next action: do not promote globally; ViewPager2 beta experiment regressed NewPipe and AntennaPod

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.0 | 0.551132 | no | 0.46 | 0.335484 | 0.538393 | 0.681818 | 0.496622 | 0.23705 | 8 |
| 1.0.0 | 0.531914 | no | 0.466667 | 0.34386 | 0.531203 | 0.681818 | 0.500891 | 0 | 0 |

Full experiment selected: `1.1.0` (score 0.551132)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.0 | 0.551132 | no | 0.46 | 0.335484 | 0.538393 | 0.681818 | 0.496622 | 0.23705 | 8 |
| 1.0.0 | 0.531914 | no | 0.466667 | 0.34386 | 0.531203 | 0.681818 | 0.500891 | 0 | 0 |

### markor - `androidx.concurrent:concurrent-futures`

- Current selected: `1.1.0` (score 0.877731, status candidate)
- Source version(s): `1.0.0`
- Classification: missing-reference-coverage-helped-in-experiment
- Next action: do not promote globally; Markor coverage-gap experiment regressed multiple controls

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.0 | 0.877731 | no | 0.95 | 0.970297 | 0.994118 | 1 | 0.935065 | 0 | 0 |
| 1.3.0 | 0.875951 | no | 0.95 | 0.960784 | 0.994118 | 1 | 0.929032 | 0 | 0 |

Full experiment selected: `1.0.0` (score 0.877738)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.0.0 | 0.877738 | yes | 0.95 | 0.970297 | 0.994118 | 1 | 0.935065 | 0 | 0 |
| 1.1.0 | 0.877731 | no | 0.95 | 0.970297 | 0.994118 | 1 | 0.935065 | 0 | 0 |
| 1.3.0 | 0.875951 | no | 0.95 | 0.960784 | 0.994118 | 1 | 0.929032 | 0 | 0 |

### markor - `androidx.activity:activity`

- Current selected: `1.10.1` (score 0.598592, status candidate)
- Source version(s): `1.6.0`
- Classification: missing-reference-coverage-helped-in-experiment
- Next action: do not promote globally; Markor coverage-gap experiment regressed AntennaPod

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.8.0 | 0.632459 | no |  |  |  |  |  |  | 0 |
| 1.8.1 | 0.632453 | no |  |  |  |  |  |  | 0 |
| 1.10.1 | 0.598592 | no | 0.549383 | 0.528871 | 0.711035 | 0.658385 | 0.551935 | 0.137103 | 8 |
| 1.13.0 | 0.557698 | no |  |  |  |  |  |  | 0 |

Full experiment selected: `1.6.0` (score 0.912985)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.6.0 | 0.912985 | yes | 0.904762 | 0.938119 | 0.942221 | 1 | 0.904847 | 0.903571 | 27 |
| 1.8.0 | 0.632459 | no |  |  |  |  |  |  | 0 |
| 1.8.1 | 0.632453 | no |  |  |  |  |  |  | 0 |
| 1.10.1 | 0.598592 | no |  |  |  |  |  |  | 0 |

### newpipe - `androidx.startup:startup-runtime`

- Current selected: `1.1.1` (score 0.54645, status candidate)
- Source version(s): `1.2.0`
- Classification: feature-equivalent-version-tie
- Next action: consider an ambiguity downgrade or independent dependency/app-era support, not a version force

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.1 | 0.54645 | no | 0.6 | 0.5 | 0.050846 | 0.5 | 0.8 | 0 | 0 |
| 1.2.0 | 0.54593 | yes | 0.6 | 0.5 | 0.050846 | 0.5 | 0.8 | 0 | 0 |

Full experiment selected: `1.1.1` (score 0.54645)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.1 | 0.54645 | no | 0.6 | 0.5 | 0.050846 | 0.5 | 0.8 | 0 | 0 |
| 1.2.0 | 0.54593 | yes | 0.6 | 0.5 | 0.050846 | 0.5 | 0.8 | 0 | 0 |

### newpipe - `androidx.lifecycle:lifecycle-runtime-android`

- Current selected: `2.9.0` (score 0.400626, status uncertain)
- Source version(s): `2.9.4`
- Classification: near-tie-with-source-candidate
- Next action: needs independent evidence; generic recency would regress other cases

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2.9.0 | 0.400626 | no | 0.193548 | 0.233766 | 0.268545 | 0.818182 | 0.381132 | 0 | 0 |
| 2.9.4 | 0.400602 | yes |  |  |  |  |  |  | 0 |
| 2.10.0 | 0.399546 | no |  |  |  |  |  |  | 0 |
| 2.8.7 | 0.387651 | no |  |  |  |  |  |  | 0 |

Full experiment selected: `2.9.0` (score 0.400626)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2.9.0 | 0.400626 | no | 0.193548 | 0.233766 | 0.268545 | 0.818182 | 0.381132 | 0 | 0 |
| 2.9.4 | 0.400602 | yes |  |  |  |  |  |  | 0 |
| 2.10.0 | 0.399546 | no |  |  |  |  |  |  | 0 |
| 2.8.7 | 0.387651 | no |  |  |  |  |  |  | 0 |

### nextcloud-android - `androidx.viewpager2:viewpager2`

- Current selected: `1.1.0` (score 0.985232, status exact)
- Source version(s): `1.1.0-beta02`
- Classification: source-version-not-in-reference-db
- Next action: do not promote globally; ViewPager2 beta experiment regressed NewPipe and AntennaPod

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.0 | 0.985232 | no | 1 | 1 | 0.993828 | 1 | 0.991554 | 1 | 43 |
| 1.0.0 | 0.873967 | no | 0.977778 | 0.957895 | 0.966135 | 1 | 0.969697 | 0 | 0 |

Full experiment selected: `1.1.0` (score 0.985232)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.0 | 0.985232 | no | 1 | 1 | 0.993828 | 1 | 0.991554 | 1 | 43 |
| 1.0.0 | 0.873967 | no | 0.977778 | 0.957895 | 0.966135 | 1 | 0.969697 | 0 | 0 |

### nextcloud-android - `androidx.concurrent:concurrent-futures`

- Current selected: `1.3.0` (score 0.972254, status exact)
- Source version(s): `1.2.0`
- Classification: source-version-not-in-reference-db
- Next action: keep as documented limitation unless a family-specific signal is found

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.3.0 | 0.972254 | no | 0.95 | 0.990196 | 0.992621 | 0.975 | 0.993548 | 1 | 1 |
| 1.1.0 | 0.879836 | no | 0.95 | 0.990099 | 0.992621 | 0.975 | 0.993506 | 0 | 0 |

Full experiment selected: `1.3.0` (score 0.972254)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.3.0 | 0.972254 | no | 0.95 | 0.990196 | 0.992621 | 0.975 | 0.993548 | 1 | 1 |
| 1.0.0 | 0.879844 | no | 0.95 | 0.990099 | 0.992621 | 0.975 | 0.993506 | 0 | 0 |
| 1.1.0 | 0.879836 | no | 0.95 | 0.990099 | 0.992621 | 0.975 | 0.993506 | 0 | 0 |

### nextcloud-android - `androidx.startup:startup-runtime`

- Current selected: `1.2.0` (score 0.911931, status likely)
- Source version(s): `1.1.1`
- Classification: bytecode-evidence-prefers-selected-version
- Next action: keep as documented limitation unless a family-specific signal is found

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.2.0 | 0.911931 | no | 1 | 1 | 0.076566 | 1 | 1 | 1 | 1 |
| 1.1.1 | 0.812741 | yes |  |  |  |  |  |  | 0 |

Full experiment selected: `1.2.0` (score 0.911931)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.2.0 | 0.911931 | no | 1 | 1 | 0.076566 | 1 | 1 | 1 | 1 |
| 1.1.1 | 0.812741 | yes |  |  |  |  |  |  | 0 |

### nextcloud-android - `com.squareup.okio:okio-jvm`

- Current selected: `3.16.4` (score 0.91031, status candidate)
- Source version(s): `3.9.0`
- Classification: source-version-not-in-reference-db
- Next action: keep as documented limitation unless a family-specific signal is found

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 3.16.4 | 0.91031 | no | 0.936 | 0.989089 | 0.979592 | 1 | 0.980198 | 0.833357 | 155 |
| 3.6.0 | 0.889257 | no | 0.934579 | 0.955224 | 0.968737 | 0.962025 | 0.947977 | 0.3 | 3 |
| 3.7.0 | 0.877754 | no | 0.934579 | 0.957461 | 0.968735 | 0.987261 | 0.952303 | 0.153846 | 1 |
| 3.0.0 | 0.765167 | no |  |  |  |  |  |  | 0 |

Full experiment selected: `3.16.4` (score 0.91031)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 3.16.4 | 0.91031 | no | 0.936 | 0.989089 | 0.979592 | 1 | 0.980198 | 0.833357 | 155 |
| 3.6.0 | 0.889257 | no | 0.934579 | 0.955224 | 0.968737 | 0.962025 | 0.947977 | 0.3 | 3 |
| 3.7.0 | 0.877754 | no | 0.934579 | 0.957461 | 0.968735 | 0.987261 | 0.952303 | 0.153846 | 1 |
| 3.0.0 | 0.765167 | no |  |  |  |  |  |  | 0 |

### nextcloud-android - `androidx.swiperefreshlayout:swiperefreshlayout`

- Current selected: `1.0.0` (score 0.877665, status candidate)
- Source version(s): `1.2.0`
- Classification: bytecode-evidence-prefers-selected-version
- Next action: keep as documented limitation unless a family-specific signal is found

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.0.0 | 0.877665 | no | 1 | 0.989474 | 0.987693 | 1 | 0.98939 | 0 | 0 |
| 1.2.0 | 0.849237 | yes |  |  |  |  |  |  | 0 |

Full experiment selected: `1.0.0` (score 0.877665)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.0.0 | 0.877665 | no | 1 | 0.989474 | 0.987693 | 1 | 0.98939 | 0 | 0 |
| 1.2.0 | 0.849237 | yes |  |  |  |  |  |  | 0 |

### nextcloud-android - `androidx.activity:activity`

- Current selected: `1.10.1` (score 0.86438, status likely)
- Source version(s): `1.9.2`
- Classification: source-version-not-in-reference-db
- Next action: do not promote globally; Activity-only experiment regressed F-Droid

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.10.1 | 0.86438 | no | 0.858025 | 0.904199 | 0.881302 | 0.869565 | 0.912424 | 0.777579 | 49 |
| 1.8.0 | 0.774048 | no |  |  |  |  |  |  | 0 |
| 1.8.1 | 0.774034 | no |  |  |  |  |  |  | 0 |
| 1.13.0 | 0.684842 | no |  |  |  |  |  |  | 0 |

Full experiment selected: `1.10.1` (score 0.86438)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.10.1 | 0.86438 | no | 0.858025 | 0.904199 | 0.881302 | 0.869565 | 0.912424 | 0.777579 | 49 |
| 1.8.0 | 0.774048 | no |  |  |  |  |  |  | 0 |
| 1.8.1 | 0.774034 | no |  |  |  |  |  |  | 0 |
| 1.6.0 | 0.745196 | no |  |  |  |  |  |  | 0 |

### nextcloud-android - `com.squareup.okhttp3:okhttp-android`

- Current selected: `5.3.2` (score 0.855892, status candidate)
- Source version(s): `not found`
- Classification: artifact-family-or-source-coordinate-nuance
- Next action: handle as coordinate-family/reporting nuance before version calibration

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 5.3.2 | 0.855892 | no | 0.909091 | 0.978295 | 0.960243 | 0.996032 | 0.976506 | 0 | 0 |

Full experiment selected: `5.3.2` (score 0.855892)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 5.3.2 | 0.855892 | no | 0.909091 | 0.978295 | 0.960243 | 0.996032 | 0.976506 | 0 | 0 |

### wikipedia-android - `androidx.startup:startup-runtime`

- Current selected: `1.1.1` (score 0.543833, status candidate)
- Source version(s): `1.2.0`
- Classification: feature-equivalent-version-tie
- Next action: consider an ambiguity downgrade or independent dependency/app-era support, not a version force

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.1 | 0.543833 | no | 0.6 | 0.5 | 0.041683 | 0.5 | 0.8 | 0 | 0 |
| 1.2.0 | 0.543248 | yes | 0.6 | 0.5 | 0.041683 | 0.5 | 0.8 | 0 | 0 |

Full experiment selected: `1.1.1` (score 0.543833)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1.1 | 0.543833 | no | 0.6 | 0.5 | 0.041683 | 0.5 | 0.8 | 0 | 0 |
| 1.2.0 | 0.543248 | yes | 0.6 | 0.5 | 0.041683 | 0.5 | 0.8 | 0 | 0 |

### wikipedia-android - `androidx.viewpager2:viewpager2`

- Current selected: `1.0.0` (score 0.498552, status candidate)
- Source version(s): `1.1.0`
- Classification: bytecode-evidence-prefers-selected-version
- Next action: keep as documented limitation unless a family-specific signal is found

| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.0.0 | 0.498552 | no | 0.422222 | 0.287719 | 0.509859 | 0.636364 | 0.475936 | 0 | 0 |
| 1.1.0 | 0.483754 | yes | 0.38 | 0.270968 | 0.503907 | 0.636364 | 0.471284 | 0.030405 | 2 |

Full experiment selected: `1.0.0` (score 0.498552)

| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.0.0 | 0.498552 | no | 0.422222 | 0.287719 | 0.509859 | 0.636364 | 0.475936 | 0 | 0 |
| 1.1.0 | 0.483754 | yes |  |  |  |  |  |  | 0 |
