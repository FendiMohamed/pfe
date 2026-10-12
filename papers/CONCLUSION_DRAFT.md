# Section 6 — Conclusion (Working Draft)

This paper presents an implemented static workflow for recovering Maven
component and version evidence from compiled Android APKs and carrying that
evidence into CycloneDX and optional OSV reporting. The approach separates
component-family identity from exact-version support, retains alternatives
when evidence is ambiguous, and treats native files and inaccessible code as
explicit boundaries. Its weighted scores and confidence labels are
rule-based; they are not calibrated probabilities.

The retained evaluation snapshots show different outcomes across evidence
lanes. The thesis-facing controlled snapshot documents 84/84 expected-version
rows across 72 generated fixtures, while source-validated real APKs document a
927/1,837 emitted Maven version confirmation rate across 102 APKs, with clean
and partial strata reported separately. The source-denominator summary records
927 exact emitted rows among 12,082 source dependency rows across 106
source-tree cases. A
separate 6,772/6,772 result applies only when per-APK candidate references are
restricted to exact source-known versions; it is an upper-bound recognition
analysis, not ordinary APK-only performance. These values are transcribed from
the retained thesis and evaluation records; the paper does not rerun the
experiments. The 30-fixture/35-component count is an earlier controlled-set
checkpoint, followed by the final recorded 72-fixture/84-row snapshot. The
current checkout lacks some row-level inputs and run metadata needed for
independent recalculation.

The results therefore support a bounded conclusion: the implementation can
produce useful version evidence in controlled and some source-validated
cases, while reference coverage, transformations, ambiguity, and the
source-to-package gap limit end-to-end coverage. The OSV examples demonstrate
how the report distinguishes stronger from weaker component/version evidence;
they do not establish vulnerability precision, recall, or exploitability.
Rejected R8, structural, reference-promotion, and AI experiments further
support keeping unvalidated signals outside default SBOM and vulnerability
authority.

The principal limitations are the incomplete machine-readable reproduction
package in the current checkout, potential
overlap between evaluated applications and reference-version selection,
source dependency trees as an imperfect proxy for packaged code,
source-available sample bias, non-independent rows within APK families, and
limited handling of native, dynamic, packed, encrypted, and protected code.
The documented aggregates cannot be independently regenerated from this
checkout without their row-level inputs and run manifests, and they do not
support population-level generalization.

Future work should release a frozen machine-readable evaluation package;
report grouped
held-out or leave-one-app-family-out results; expand reference coverage while
separating evaluation-only references from globally promoted references;
improve APK-only candidate recall and version discrimination under R8 and
partial library inclusion; calibrate confidence on independent data; and
evaluate vulnerability claims against an explicit component/version oracle.

> **Release note:** Keep the numeric statements tied to the retained thesis and
> evaluation records, with the independent-recalculation limitation stated
> until a machine-readable release package is available. Update the abstract
> after the final metric and venue audit.
