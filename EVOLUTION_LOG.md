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
