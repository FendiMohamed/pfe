# Datasets, Metrics, and Results

## Why the evaluation is split

APK difficulty is not uniform. A single score would hide whether the tool works
only on controlled examples or survives realistic AndroidX, Kotlin, R8, native,
and legacy build conditions.

## Evidence buckets

### Controlled fixtures

72 APK fixtures contain 84 expected Maven versions. Variants include clear,
R8 rename, shrink, optimize, shrink+optimize, package flattening/repackaging,
inline-like stress, multidex, and multi-library cases.

Result: `84/84` exact confirmations.

Meaning: the implemented mechanics work when the expected library is
represented and the test boundary is controlled. It is not a universal
real-world accuracy claim.

### Clean source-validated real APKs

5 APKs, `47/47` emitted Maven versions confirmed.

Meaning: the MVP can produce exact source-confirmed output on favorable real
APKs. Some rows are sparse, so this bucket cannot stand alone.

### Partial source-validated real APKs

97 APKs, `880/1790` emitted versions confirmed.

Meaning: realistic difficult cases still yield useful evidence while exposing
version drift, reference gaps, family ambiguity, and low-confidence extras.

### Overall source-validated real APKs

102 APKs, `927/1837` confirmed, `636` version mismatches, and `274`
missing/nuance rows.

Rate: `50.5%` emitted Maven version confirmation.

### Limitation and boundary cases

Native-heavy, hidden DEX, protector, and other boundary evidence is reported
separately and excluded from ordinary Maven accuracy.

## Three different denominators

| Metric | Numerator / denominator | Current meaning |
|---|---|---|
| Emitted-version confirmation | correct emitted Maven rows / emitted Maven rows | `927/1837` (`50.5%`) |
| Reference exact-version coverage | source rows whose exact version is stored / all source rows | shared DB baseline `1231/12082` (`10.2%`); priority experiment `9657/12082` (`79.9%`) |
| End-to-end exact source recall | exact emitted source rows / all source rows | shared baseline `927/12082` (`7.7%`) |

These values answer different questions and must not be substituted for one
another.

## Final v2 source-known lane

Across 106 source-tree cases, an evaluation used exact source coordinate/version
slices from a large reference DB:

- `6772/6772` emitted rows exact;
- zero wrong-version emitted rows;
- zero missing emitted rows;
- `5238` source-gap rows still classified separately.

This demonstrates an upper bound when source-known versions constrain the
search. It does not mean the unconstrained APK-only tool has 100% real-world
accuracy.

## AI metrics

| Model | Result | Decision |
|---|---:|---|
| RandomForest | macro-F1 `0.708` | Report-only suggestions |
| Full structured-token Transformer | macro-F1 `0.977` | Research evidence; shortcut risk |
| MVP-safe Transformer | macro-F1 `0.882` | Report-only risk triage |
| Raw-opcode Transformer | macro-F1 `0.110` vs baseline `0.128` | Not promotable |

## Safe thesis wording

> Across 102 source-validated real APKs, the MVP confirms 927 of 1837 emitted
> Maven versions, a 50.5% emitted-version confirmation rate. Controlled, clean,
> partial, and boundary cases are reported separately.

## Primary evidence

- [Thesis evaluation tables](../../evaluation/THESIS_EVALUATION_TABLES.md)
- [Coverage-first dashboard](../../evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md)
- [Final v2 results](../../thesis/FINAL_V2_RESULTS_SECTION.md)
- [AI/R8 final evaluation](../../evaluation/AI_R8_FINAL_EVALUATION.md)
