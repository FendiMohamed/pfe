# Safe Experiment Rules

## 1. Preserve the stable baseline

- Do not modify the shared calibrated DB during exploration.
- Use uniquely named configs, caches, DEX roots, DBs, and result directories.
- Record the baseline DB and command beside the experiment.

## 2. Define the question before running

Examples:

- Does Fragment 1.6.2 separate from 1.6.1?
- Does API-reference weight improve exact versions?
- Does a larger DB recover missing I2P modules without extra emissions?

Avoid “try many weights until the row looks right.”

## 3. Use representative gates

Minimum useful preflight:

- two intended targets;
- clean control;
- partial/hard control;
- no-Maven control;
- native, hidden, or other boundary control.

Use controlled fixtures when a change touches R8 or version logic.

## 4. Fail fast

Stop when a material regression already disproves safe promotion:

- correct control flips;
- emitted component count explodes;
- source-missing rows appear;
- target identity is lost;
- runtime becomes impractical.

## 5. Separate source-known from APK-only

Source coordinate/version filters are valuable upper-bound diagnostics. Label
them clearly. They cannot prove that an unconstrained APK-only detector found
the same answer.

## 6. Separate diagnostic from authority

A feature may be:

- extracted but inert;
- shown in a report;
- used in an isolated experiment;
- approved for default matching.

Only the last category changes SBOM authority.

## 7. Protect metric denominators

Never rewrite:

- emitted confirmation as full recall;
- reference coverage as detection accuracy;
- source-known results as unconstrained accuracy;
- boundary/no-Maven rows as ordinary failures or successes.

## 8. Require reproducible evidence

Store:

- exact command and configuration;
- input APK and DB paths;
- JSON or CSV results;
- readable Markdown verdict;
- baseline/candidate comparison;
- target and control outcomes.

## 9. Promotion criteria

A candidate default should:

- improve the intended rows;
- preserve current controlled exact results;
- preserve clean and partial real controls;
- avoid false Maven claims on no-Maven/boundary cases;
- maintain acceptable runtime;
- not depend on unavailable source evidence;
- have tests and documentation.

## 10. Keep negative results

Rejected experiments prevent duplicated effort and demonstrate scientific
discipline. Update the
[Experiment Decision Ledger](../../thesis/EXPERIMENT_DECISION_LEDGER.md).

## 11. Synchronize authoritative surfaces

If current results change, update:

- generated evidence artifacts;
- `TASKS.md`;
- `docs/codex/CODEX_CONTEXT.md`;
- evaluation dashboards;
- thesis tables and assembled report;
- presentation numbers.

## 12. Do not delete project evidence casually

Reference artifacts, source trees, Docker images, and result directories may
support thesis proof. Inventory first and preserve artifacts associated with
the project unless deletion is explicitly approved.
