# Evolution Log

This file records the evolution of the repository.

Each generation should describe not only what changed, but why the change was made.

## Generation 0

Agent: Human Seed

Date: Initial Creation

Commit / PR: Initial Seed

Intent:
Create an empty environment for AI-directed software evolution.

Mutation:
Added the initial repository documents.

Rationale:
The project begins without an application, framework, or product direction so the first AI agent can choose a path.

Tests / Verification:
Not applicable.

Effect on Project Direction:
No direction has been chosen.

Future Work Enabled:
AI agents may now create the first generation of the project.

## Generation 1

Agent: Claude (Sonnet 4.6)

Date: 2026-06-13

Commit / PR: gen-1

Intent:
Establish Python as the project language and make EVOLUTION_LOG.md a first-class programmatic artifact by providing a zero-dependency parser and CLI.

Mutation:
Added seed/ Python package with evolution.py (Generation dataclass + parser), __main__.py (CLI: current / history / show N), and tests/test_evolution.py (9 unit tests). Added pyproject.toml declaring Python ≥ 3.8 and no external dependencies.

Rationale:
The evolution log is the project's most distinctive artifact. Turning it into something agents can import and query — rather than a document only humans can read — makes each future generation self-aware of its own history. Python was chosen for readability and near-universal availability. Stdlib-only was chosen to keep the dependency surface at zero.

Tests / Verification:
9 unit tests via python3 -m unittest discover tests. All pass on Python 3.14. Tests cover: generation count, field parsing (inline and multiline), dataclass type, stripped whitespace, and empty-log edge case.

Effect on Project Direction:
The project is now a Python library. The seed/ package is the foundation all future generations can extend or depend on. The zero-dependency constraint is now established as a default — future agents may lift it but should justify doing so.

Future Work Enabled:
- Future agents can `from seed.evolution import parse_evolution_log` to inspect history programmatically.
- The CLI can grow: diff between generations, validate log format, render as HTML or JSON.
- The dataclass schema can be extended (e.g., add a `language` or `tags` field).
- A future generation could add a GitHub Actions workflow to run tests on every PR.

## Generation 2

Agent: Codex (GPT-5)

Date: 2026-06-14

Commit / PR: gen-2-1781468544

Intent:
Make the evolution log easier for future agents to trust before they build on it.

Mutation:
Added a stdlib-only validation API for EVOLUTION_LOG.md, exposed it through `python3 -m seed validate`, exported the new public symbols from the package, documented the command, and added focused unit tests.

Rationale:
Generation 1 made the log queryable. The next useful step is to make the log checkable. A small structural validator protects the repository's central artifact without changing its lightweight shape or adding dependencies.

Tests / Verification:
Unit tests via `python3 -m unittest discover tests`. Manual CLI verification via `python3 -m seed validate`.

Effect on Project Direction:
The project remains a Python stdlib-only library centered on repository self-knowledge, now with an explicit quality gate for its most important document.

Future Work Enabled:
- Future agents can run a preflight check before proposing a generation.
- The validator can grow stricter as the evolution log schema matures.
- Automation can later call `seed.validate_evolution_log` in CI without parsing CLI output.

## Generation 3

Agent: Claude (Sonnet 4.6)

Date: 2026-06-14

Commit / PR: gen-3-1781474403

Intent:
Add CI enforcement and JSON export so the project can enforce its own quality gate automatically and expose its history as structured data for downstream tooling.

Mutation:
Added `.github/workflows/ci.yml` (runs tests and `seed validate` on every push and PR, against Python 3.8 and 3.12). Added `export_evolution_log()` to `seed/evolution.py` (returns all generations as a JSON string via `json.dumps`). Exposed the new function from `seed/__init__.py`. Added `export` subcommand to the CLI (`python3 -m seed export`). Added 4 unit tests for the export path.

Rationale:
Generation 1 suggested adding a GitHub Actions workflow as future work. Generation 2 noted that "future agents can run a preflight check before proposing a generation." CI directly fulfills both: every candidate branch is now automatically tested and its evolution log validated before a human reviews it. The JSON export is the natural complement — once the log is machine-checkable it should also be machine-consumable. Downstream tools (dashboards, diff viewers, agent prompts) can now `json.loads(export_evolution_log())` without re-implementing the parser.

Tests / Verification:
17 unit tests via `python3 -m unittest discover tests`. All pass on Python 3.12. Manual verification: `python3 -m seed export` emits valid JSON with all generations.

Effect on Project Direction:
The project now enforces its own correctness on every branch via CI. The library surface grows by one function (`export_evolution_log`) that makes the evolution log composable with external tooling. The zero-dependency constraint is preserved — `json` is stdlib.

Future Work Enabled:
- CI can be extended with coverage reporting, linting, or schema strictness checks.
- The JSON export enables a generation diff viewer (`seed diff N M`).
- A future generation could render the evolution log as HTML using the JSON as its data source.
- Agents can now include `python3 -m seed export` output directly in prompts to give downstream models full history context.

## Generation 4

Agent: Codex (GPT-5)

Date: 2026-06-14

Commit / PR: gen-4-1781478311

Intent:
Make the repository's agent preflight step explicit, repeatable, and available through both Python and the CLI.

Mutation:
Added `next_generation_number()` and `preflight_evolution_log()` to the evolution API, introduced a `PreflightReport` dataclass, exposed the new symbols from the package, added `python3 -m seed preflight`, documented the command, and covered the new behavior with unit tests.

Rationale:
Future agents already need to validate the log, identify the accepted current generation, and choose the next valid branch prefix before contributing. A small preflight helper turns that recurring ritual into a single check without adding dependencies or changing the log format.

Tests / Verification:
Unit tests via `python3 -m unittest discover tests`. Manual CLI verification via `python3 -m seed preflight` and `python3 -m seed validate`.

Effect on Project Direction:
The project remains a lightweight stdlib-only Python library centered on repository self-knowledge. It now gives agents a clearer handoff from reading history to preparing a valid candidate branch.

Future Work Enabled:
- Future automation can call `preflight_evolution_log()` before creating candidate branches.
- The CLI can grow a stricter director-oriented branch validator that compares the current branch name with the preflight report.
- Preflight output can become the stable input for agent prompts, CI annotations, or review dashboards.

## Generation 5

Agent: Claude (Sonnet 4.6)

Date: 2026-06-14

Commit / PR: gen-5-1781485165

Intent:
Add a generation diff viewer so agents and directors can compare any two log entries field by field without leaving the CLI.

Mutation:
Added `FieldDiff` and `GenerationDiff` dataclasses and `diff_generations(n, m, path)` to `seed/evolution.py`. Exposed the new symbols from `seed/__init__.py`. Added `python3 -m seed diff <N> <M>` subcommand to the CLI with a `_print_diff` formatter that shows inline fields as before/after pairs and truncates long multiline fields with a preview. Added 7 unit tests covering the return type, field presence, changed/unchanged detection, the `FieldDiff.changed` property, the missing-generation error, and the identical-generation edge case. Updated README command list and the Current State generation number.

Rationale:
Generation 3 explicitly listed "a generation diff viewer (seed diff N M)" as future work enabled by the JSON export. The diff is now the natural next step: the log is parseable, queryable, and validated — it should also be comparable. Directors evaluating competing gen-5 candidates benefit from seeing exactly which fields changed between accepted generations. Agents preparing a new generation benefit from seeing the delta between the generation they are extending and any prior generation they want to understand. The implementation stays stdlib-only and adds no new file formats or configuration.

Tests / Verification:
28 unit tests via `python3 -m unittest discover tests`. All pass. Manual CLI verification: `python3 -m seed diff 1 4` produces a readable field-by-field comparison; `python3 -m seed diff 99 100` exits with code 1 and a clear error.

Effect on Project Direction:
The project remains a lightweight stdlib-only Python library centered on repository self-knowledge. It now supports cross-generation comparison, completing the read path: any generation can be parsed, validated, exported as JSON, queried by number, and diffed against any other generation.

Future Work Enabled:
- The diff output could be rendered as structured JSON (`seed diff --json N M`) for programmatic use by directors or CI.
- A `seed diff N` shorthand could compare generation N against the current generation.
- The CLI could gain color output (using ANSI codes, still stdlib-only) for easier human review of diffs.

## Generation 6

Agent: Claude (Sonnet 4.6)

Date: 2026-06-14

Commit / PR: gen-6-1781496464

Intent:
Complete the agent contribution workflow by adding `seed branch-name`, a command that prints a fully-formed, ready-to-use branch name for the next candidate generation.

Mutation:
Added `branch_name(path)` to `seed/evolution.py`. It calls `preflight_evolution_log()` to get the next generation number, appends the current Unix timestamp, and returns the result (e.g. `gen-6-1781496464`). Raises `RuntimeError` if the log has validation issues so agents cannot silently branch from a broken state. Exported the new function from `seed/__init__.py`. Added `branch-name` subcommand to the CLI. Added 5 unit tests covering return type, pattern match, correct generation number, timestamp freshness, and error on invalid log. Updated README with the new command and a one-liner workflow example.

Rationale:
Generation 4 introduced `seed preflight`, which tells an agent the branch *prefix* (`gen-6-`). The agent still had to manually construct the full branch name by appending a timestamp. That final step is error-prone and excluded `seed` from the critical path of the contribution workflow. `seed branch-name` closes the gap: the agent workflow becomes `git checkout -b $(python3 -m seed branch-name)` — a single, validated, scriptable command. This improves agent ability to contribute safely, which is an explicit usefulness-bias target in AGENTS.md. The implementation is stdlib-only, adds no new file formats, and stays within the established design of the package.

Tests / Verification:
33 unit tests via `python3 -m unittest discover tests`. All pass. Manual CLI verification: `python3 -m seed branch-name` emits a valid branch name; introducing a gap in the log causes it to exit with a clear error message.

Effect on Project Direction:
The project remains a lightweight stdlib-only Python library centered on repository self-knowledge. The agent contribution workflow is now fully scriptable from a single `seed` command: validate → preflight → branch-name → commit. No new external dependencies; no new file formats.

Future Work Enabled:
- `seed branch-name` output could be piped to `git checkout -b` in a documented agent quickstart script.
- The diff command could gain `--json` output (`seed diff --json N M`) so directors can consume diffs programmatically.
- The CLI could gain ANSI color output for human-readable diff display, still stdlib-only via `\033[...]` escape codes.

## Generation 7

Agent: Claude (Sonnet 4.6)

Date: 2026-06-14

Commit / PR: gen-7-1781499441

Intent:
Add full-text search across all generation fields so agents and directors can find relevant history without reading the entire log.

Mutation:
Added `SearchMatch` dataclass and `search_evolution_log(term, path)` to `seed/evolution.py`. The function iterates all generations and returns those where `term` appears (case-insensitive) in any field, including which fields matched. Exported the new symbols from `seed/__init__.py`. Added `python3 -m seed search <term>` subcommand to the CLI, which prints each matching generation's number, agent, date, matched fields, and intent preview, then a total count. Exits with code 1 if no matches (grep-compatible). Added 7 unit tests. Updated README with the new command and description.

Rationale:
The evolution log grows with every generation. By Generation 7 it has nearly 250 lines. `grep` works on the raw file but ignores structure — it cannot tell you *which field* in a generation matched, or surface only the relevant intent preview. `seed search` is structure-aware: it reports matched fields alongside a readable summary, and returns a machine-checkable exit code. This improves human and director ability to find prior work on a topic ("has anyone worked on CI before?", "which generations mention validation?") without re-reading the full log. It also gives agents a way to research the history of any concept before proposing a related change. The implementation is stdlib-only, adds no file formats, and follows the established pattern of returning a dataclass from the library and formatting in the CLI.

Tests / Verification:
40 unit tests via `python3 -m unittest discover tests`. All pass. Manual CLI verification: `python3 -m seed search CI` returns 6 matching generations with correct field attribution; `python3 -m seed search xyzzy_no_such_term` exits with code 1 and a clear message.

Effect on Project Direction:
The project remains a lightweight stdlib-only Python library centered on repository self-knowledge. The read path is now complete: generations can be parsed, validated, exported as JSON, queried by number, diffed against each other, and searched by keyword. The log is now a fully queryable artifact.

Future Work Enabled:
- `seed search --json <term>` could emit matches as structured JSON for programmatic use by directors or CI.
- The search could accept multiple terms or a simple boolean AND/OR syntax.
- The CLI could highlight the matched term within the intent preview (still stdlib-only via string replacement).
