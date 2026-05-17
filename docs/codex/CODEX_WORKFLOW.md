# Codex Workflow

This file defines how to use Codex during the whole project.

## Session Startup

At the start of each coding/research session, ask Codex to read:

```text
docs/codex/CODEX_CONTEXT.md
TASKS.md
docs/planning/IMPLEMENTATION_PLAN.md
docs/architecture/MVP_ARCHITECTURE.md
```

Then ask it to continue from the next unfinished task.

## Working Rule

Use Codex in small implementation loops:

```text
1. Choose one task from TASKS.md.
2. Ask Codex to inspect current files.
3. Ask Codex to implement only that task.
4. Ask Codex to run a small verification.
5. Ask Codex to update TASKS.md and decision notes if needed.
```

## Good Prompts

Implementation prompt:

```text
Read the project context and implement the next task in TASKS.md. Keep the change small, run verification, and update TASKS.md.
```

Research prompt:

```text
Read docs/research/EVIDENCE_MAP.md and expand the section for [paper/tool]. Focus on how it affects MVP architecture decisions.
```

Debug prompt:

```text
The command [command] failed with [error]. Inspect the relevant code and fix the smallest root cause. Do not refactor unrelated files.
```

Writing prompt:

```text
Use the architecture and evidence docs to draft a thesis subsection about [topic]. Keep claims aligned with MVP scope and limitations.
```

## Files Codex Should Update Often

| File | When to update |
|---|---|
| `TASKS.md` | After finishing or starting a milestone. |
| `docs/architecture/DECISIONS_LOG.md` | When a major architecture/tool/scope decision changes. |
| `docs/tooling/TOOLCHAIN.md` | When a tool is installed, replaced, or rejected. |
| `docs/planning/EVALUATION_PLAN.md` | When test datasets or metrics change. |

## Skills And Plugins To Use Later

| Need | Codex capability |
|---|---|
| Work with Word thesis files | Documents plugin/skill. |
| Build presentation slides | Presentations plugin/skill. |
| Build result spreadsheets | Spreadsheets plugin/skill. |
| Test local web dashboard | Browser plugin/skill. |
| Generate diagrams | Markdown Mermaid diagrams first. |

## Safety Rule

Do not delete or rewrite research PDFs. New analysis should go into `docs/` or `work/state of the art/`.

