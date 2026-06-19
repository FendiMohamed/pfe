# Paper-to-Implementation Map

| Research lesson | Project implementation | Why this form was chosen |
|---|---|---|
| Build profiles from known releases | Maven download, D8 conversion, SQLite feature DB | Reproducible exact coordinate/version references are required for version claims. |
| Names alone are fragile | Opcodes, dependency edges, literals, APIs, n-grams, structural diagnostics | R8 can rename or remove identifiers. |
| Structural evidence helps under obfuscation | Class-dependency and multi-scale feature extraction | Structure can survive renaming, but is still affected by shrinking and inlining. |
| Use coarse-to-fine matching | Coordinate filters, package prefilters, family shortlists, diagnostic queues | Full large-DB scoring is expensive, but pruning must preserve recall. |
| Exact versions need special evidence | Version-unique features and literal-context reranking | Adjacent releases often share most code. |
| Realistic datasets lower scores | Controlled, clean, partial, blocked, and boundary buckets | One aggregate number hides where the method works and fails. |
| SBOM output must be standard | CycloneDX 1.5 with Maven PURLs | Makes the result interoperable with vulnerability tooling. |
| Vulnerability certainty depends on version certainty | Confirmed/potential vulnerability labels | A weak version guess must not become a strong CVE claim. |
| AI may help R8 triage | RandomForest and Transformer report-only assistants | Current evidence supports assistance, not decision authority. |
| Reproducibility requires negative results | Failed experiments and promotion gates are stored | Prevents repeatedly testing rejected ideas and supports thesis honesty. |

## Important adaptations

The research often presents one dominant signature. The MVP instead uses a
weighted collection of interpretable feature families. This is easier to
debug, ablate, and explain in a defense.

The literature also tends to focus on “library present or absent.” This project
separates:

1. coordinate or family identity;
2. exact version selection;
3. SBOM emission;
4. vulnerability certainty.

That separation is essential. Correctly identifying `gson` does not prove
which `gson` release is present.

## Important non-adoptions

- No claim of a full Bayesian model: the current scorer is weighted and
  confidence-calibrated, not a trained posterior over all libraries.
- No automatic AI override: learned models do not alter matcher authority.
- No package-overlap-only detector: package overlap created false candidates in
  the priority DB preflight.
- No perfect transitive-dependency reconstruction: APK bytecode and Gradle
  source trees answer different questions.
- No forced answer for native or hidden code boundaries.

## Evidence

The detailed mapping with source files and current measured results is in
[PAPER_TO_IMPLEMENTATION_TRACEABILITY.md](../../thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md).
Decision history is also summarized in
[DECISIONS_LOG.md](../../architecture/DECISIONS_LOG.md).
