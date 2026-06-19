# Failed, Blocked, and Non-Promoted Experiments

Negative results are part of the project contribution. A method may detect a
real signal and still be unsafe as a production default.

## Global opcode tri-gram weight

Tested idea: add a global opcode n-gram contribution.

Result: weight `0.02` regressed OpenTracks and Conversations without improving
confirmed versions.

Decision: default remains `0.0`; retain as diagnostic evidence.

## Global API-reference weight

Tested idea: add API/member-reference overlap globally.

Result: weight `0.05` changed no source-validation metrics in the guarded slice.

Decision: default remains `0.0`; no measured benefit justified complexity.

## Generic newer-version or recency rule

Tested idea: prefer a newer release in close adjacent-version ties.

Result: helped selected Activity, ViewPager2, Concurrent Futures, or Lifecycle
rows but regressed other APKs. Release recency is not bytecode evidence.

Decision: rejected globally.

## Broad POM coherence

Tested idea: use dependency metadata to override ambiguous bytecode ranking.

Result: useful explanations, but generic rules were not clean enough.

Decision: diagnostic or narrowly scoped only.

## New global artifact-family rules

Tested idea: generalize family selection across Android/JVM/KTX/runtime
artifacts.

Result: known Okio, OkHttp, and Lifecycle cases support narrow rules, but
general expansion introduced unsafe assumptions.

Decision: preserve only scoped, tested families.

## Global Phase 4 multi-scale blend

Tested idea: globally blend call-chain, basic-block, class-neighbor,
field-operation, and context evidence.

Result:

- 4 real target improvements;
- 6 controlled regressions;
- 30 source-validated real regressions;
- 8 clean-real regressions.

Decision: rejected as a global scorer. Feature extraction remains inert and
available for research.

## Phase 5 scoped R8 trigger

Result: 4 target improvements and no triggered regression in its validation
gates.

Decision: still experiment-only/report-only. A promising trigger is not enough
to silently change the frozen MVP without broader proof.

## Source-used reference additions

Tested idea: add exact versions observed in individual source trees.

Result: target cases improved, but broad additions could change other apps and
create app-specific overfitting.

Decision: only narrowly guarded subsets may be promoted; experimental DBs stay
separate.

## Fragment 1.6.2

The isolated Fragment experiment compared 1.6.2 with the shared 1.6.1 row.
Most feature families were identical, leaving tiny opcode/API/context
differences that did not justify shared DB promotion under the target/control
gate.

Decision: keep 1.6.2 experiment-only. Shared calibrated DB unchanged.

Proof: [Fragment 1.6.2 preflight](../../evaluation/WRONG_VERSION_P1_FRAGMENT_1_6_2_PREFLIGHT.md).

## Priority DB broad package shortlist

The DB improved exact source-row coverage to `79.9%`, but an I2P preflight
expanded output from 18 rows to 111, with 25 mismatches and 14 rows absent from
source. A stricter shortlist still emitted 51 rows and lost two intended I2P
modules.

Decision: fail fast; no production promotion.

## Raw-opcode Transformer

Result: macro-F1 `0.110`, below opcode-count baseline `0.128`.

Decision: research-only negative evidence.

## Hidden DEX/protector recovery

Tested idea: infer Maven packages from hidden or protected payload indicators.

Decision: rejected as a package/version claim. Report risk, do not invent
components.

## Native version identification

Decision: outside MVP. Native `.so` files remain hash-only components because a
trusted native reference/provenance pipeline is a separate research problem.

## Blocked build-system cases

Some source dependency trees initially failed because of obsolete Gradle,
JCenter, plugins, or timeouts. Many were rescued with isolated validation
copies and compatible Gradle/JDK versions. Unresolved cases were never forced
into clean accuracy.

## Full ledger

See [Experiment Decision Ledger](../../thesis/EXPERIMENT_DECISION_LEDGER.md).
