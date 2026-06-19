# Matcher and Version Selection

Primary file: [matcher.py](../../../src/apk_sbom/matcher.py)

## Candidate scoring

For each reference component, the matcher computes available feature
similarities. The default weights are:

| Feature | Default weight |
|---|---:|
| Package coverage | `0.15` |
| Class coverage | `0.45` |
| Method coverage | `0.25` |
| Opcode similarity | `0.15` |
| Dependency similarity | `0.10` |
| Literal overlap | `0.08` |
| Version-unique evidence | `0.12` |
| API references | `0.0` |
| Opcode tri-grams | `0.0` |

Only active feature families participate in the normalized weighted average.
The numeric score ranks evidence; it is not a formal probability.

Class evidence receives the largest default weight because it is highly
discriminative on clear APKs. Structural and literal signals reduce dependence
on names. API and n-gram signals default to zero because their experiments did
not justify unconditional production weight.

## Identity versus version

The best version score alone does not answer both questions:

1. Is this coordinate/library family present?
2. Which exact release is present?

The matcher computes a separate identity confidence and version confidence.
Several versions can support strong identity while remaining too close for an
exact version.

## Ambiguous versions

Candidates close enough to the selected release are retained as alternatives.
The decision can then state that the identity is credible but the exact version
is uncertain.

This protects CVE mapping from false precision.

## Guarded family logic

The matcher contains explicit artifact-family handling for cases such as:

- Okio versus Okio JVM;
- OkHttp versus OkHttp Android;
- Lifecycle public versus Android variants;
- Compose-era coherence.

These rules address known coordinate-family confusion. They are narrow by
design and are backed by target/control experiments.

## Version-unique literal-context reranker

This reranker uses strings that are unique to a reference version plus their
context. It is guarded because raw literal overlap can reward incidental
strings. The CLI exposes enable/disable controls so experiments can compare the
same APK with the reranker on and off.

## Composite family shortlist

The optional shortlist narrows sibling candidates using a score margin. It can
reduce family confusion, but candidate pruning is only safe when it preserves
the true version and controls false emissions.

## Coordinate filtering

`--coordinate group:artifact` is useful for diagnosis and controlled
separability tests. It must not be mistaken for normal unconstrained APK-only
detection because it supplies identity information externally.

## Interpreting output

Inspect:

- total score and each feature score;
- identity and version confidence labels;
- candidate margin;
- ambiguous versions;
- family/reranker decisions;
- evidence and decision status.

Do not report the top string alone.
