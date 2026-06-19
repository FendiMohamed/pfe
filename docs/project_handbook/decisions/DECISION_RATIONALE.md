# Decision Rationale

## Hybrid static analysis

**Decision:** combine names, bytecode behavior, structure, literals, and
metadata.

**Why:** package names and hashes are fragile; one structural signature is also
insufficient under shrinking, inlining, and version similarity.

**Rejected:** package-only, hash-only, and dynamic-analysis-first designs.

Dynamic analysis may be useful later, but it is expensive, incomplete by
coverage, and not necessary for the first reproducible APK-to-SBOM MVP.

## Maven version reference profiles

**Decision:** build local fingerprints from selected Maven JAR/AAR releases.

**Why:** exact SBOM and vulnerability claims need coordinate/version evidence.
Reference artifacts are reproducible and auditable.

**Rejected:** library-name-only output and direct vulnerability search without
package versions.

## DEX-to-DEX comparison

**Decision:** convert reference bytecode through D8 and compare Android bytecode
representations.

**Why:** APK code is DEX. Comparing DEX-derived features reduces differences
caused purely by class-file versus DEX representation.

## CycloneDX first

**Decision:** emit CycloneDX 1.5 JSON.

**Why:** standard component schema, PURL support, vulnerability-tool
interoperability, and a practical JSON format.

**Deferred:** SPDX as an additional export. A custom format would reduce
interoperability.

## OSV first

**Decision:** query OSV using Maven package/version information.

**Why:** OSV is ecosystem-aware and directly supports Maven packages.

**Rejected:** NVD/CPE-only matching and manual advisory lookup as the primary
pipeline.

## Confidence instead of forced precision

**Decision:** separate identity and exact-version confidence and preserve
ambiguous alternatives.

**Why:** an APK can strongly contain a library family while adjacent versions
are observationally inseparable. CVE certainty depends on this distinction.

## Native files as hash-only components

**Decision:** inventory and hash `.so` files without asserting arbitrary names
or versions.

**Why:** native provenance requires a dedicated reference and symbol/build-ID
pipeline.

**Deferred:** full native package/version identification.

## Source validation as an external gate

**Decision:** compare emitted SBOM rows with resolved Gradle dependency trees
where available.

**Why:** source evidence reveals wrong-version and extra-emission behavior.

**Boundary:** it validates emitted rows; it is not automatically a complete
source recall metric.

## Category-separated evaluation

**Decision:** report controlled, clean, partial, no-Maven, blocked, and boundary
evidence separately.

**Why:** realistic benchmark research shows that one aggregate score hides
major differences in difficulty and can exaggerate performance.

## Experiment DB isolation

**Decision:** new versions and large catalogs enter isolated DBs first.

**Why:** reference growth can change candidate competition and create
regressions even when the added row is correct.

The Fragment 1.6.2 and priority DB results demonstrate why this policy matters.

## Fail-fast target/control gates

**Decision:** stop an experiment as soon as a material regression appears.

**Why:** continuing a 106-case matrix after the first severe false-positive
expansion wastes time and does not make the candidate safer.

## Narrow rules over global heuristics

**Decision:** keep guarded Okio, OkHttp, Lifecycle, and literal-context behavior
where evidence supports it.

**Rejected:** global recency, broad family, POM override, API, n-gram, and
multi-scale scoring changes that did not pass controls.

## AI as report-only assistance

**Decision:** permit AI to annotate risk and suggest investigation, but block it
from matcher/SBOM/CVE authority.

**Why:** the MVP-safe Transformer is useful, but no strict APK-only promotion
candidate passed all gates, and the raw-opcode model underperformed its simple
baseline.

## Priority DB not promoted

**Decision:** retain the 2477-component DB as evaluation evidence only.

**Why:** high reference coverage did not translate into safe unconstrained
candidate emission. The user chose not to spend additional deadline time on a
stronger retrieval gate.

## Canonical decision records

- [Architecture Decisions Log](../../architecture/DECISIONS_LOG.md)
- [Experiment Decision Ledger](../../thesis/EXPERIMENT_DECISION_LEDGER.md)
- [Paper-to-implementation traceability](../../thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md)
