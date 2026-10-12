# Abstract (Provisional Working Draft)

Analysts often need to inventory third-party components from compiled Android
applications without access to source code or build metadata. This paper
presents an implemented static pipeline that compares DEX-derived features
with versioned Maven reference profiles, separates component identity from
exact-version evidence, preserves ambiguity, emits CycloneDX, and optionally
qualifies OSV findings according to the component/version evidence. In
retained source-validation summaries, 927/1,837 emitted Maven version rows
agree with source evidence across 102 APKs: 47/47 across five clean cases and
880/1,790 across 97 partial cases. In the later recorded controlled snapshot,
84/84 expected component-version rows are confirmed across 72 generated
fixtures; 30 fixtures/35 components is an earlier checkpoint. Against the broader source dependency
denominator, 927/12,082 rows are emitted exactly across 106 source-tree cases.
A separate 6,772/6,772 result uses per-APK exact source-version candidate
slices and is an upper-bound recognition analysis, not ordinary APK-only
performance. The examples demonstrate evidence-qualified SBOM and
vulnerability reporting, not vulnerability precision or recall. These figures
are transcribed from the retained theses and evaluation records; the current
checkout lacks some row-level inputs and run metadata needed for independent
recalculation, so the paper does not claim a fresh rerun.

> **Submission gate:** Apply the selected venue’s length and terminology
> requirements, then perform the final cross-section claim audit. Do not imply
> independent recalculation from the current checkout.
