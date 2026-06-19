# Third-Party Library Matching Features

TPL means third-party library. The matcher compares features extracted from an
APK with the same feature families extracted from known reference releases.

## Name-based features

### Packages

Package overlap is cheap and useful for candidate discovery. It is weak under
repackaging and too broad for exact version selection.

### Classes and methods

Class descriptors and method signatures are highly discriminative when names
survive. R8 renaming, shrinking, and inlining reduce their reliability.

## Structure and behavior features

### Opcode histograms

An opcode histogram counts instruction types. Cosine similarity compares the
shape of bytecode behavior without requiring exact names. Histograms lose
instruction order, so unrelated code can occasionally look similar.

### Opcode tri-grams

Tri-grams preserve short instruction sequences. They are richer than a global
histogram but more expensive and still sensitive to optimization.

### Dependency edges

Edges record relations such as extends, implements, field type, and method
signature references. They approximate a class dependency graph and can
survive some renaming.

### API references

Invoked API/member references provide behavioral context. They can separate
libraries that have similar names but use different platform or dependency
APIs.

### Literals and literal context

String constants often survive obfuscation. Raw literal overlap can be noisy;
version-unique literals and their method/class context are more useful for
adjacent-version ties.

## Multi-scale diagnostic features

The analyzer can also collect basic-block, call-chain, class-neighbor, field
operation, and literal-context summaries. Much of this work remains diagnostic
or report-only because a feature must pass control and regression gates before
changing production scores.

## Default weighted score

The production matcher combines interpretable signals. Current defaults include
class, method, package, opcode, dependency, literal, and version-unique
evidence. API-reference and opcode n-gram weights default to zero unless an
experiment explicitly enables them.

Weights are not probabilities. The resulting score is ranking evidence that is
later interpreted together with candidate margins, family logic, and
confidence rules.

## Read next

- [Matcher and version selection](../implementation/MATCHER_AND_VERSION_SELECTION.md)
- [matcher.py](../../../src/apk_sbom/matcher.py)
- [DEX analyzer](../implementation/EXTRACTOR_AND_DEX_ANALYZER.md)
