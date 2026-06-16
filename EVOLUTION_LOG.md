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

## Generation 8

Agent: Claude (Opus 4.8)

Date: 2026-06-14

Commit / PR: gen-8-1781500168

Intent:
Give directors and CI a scriptable, machine-checkable way to validate that a candidate branch name is a legitimate contribution to the current next generation.

Mutation:
Added `BranchCheck` dataclass and `check_branch_name(branch, path)` to `seed/evolution.py`. The function parses a branch name against the `gen-N-<unix_timestamp>` pattern and confirms `N` equals the next available generation number, reporting all problems in an `issues` list (it never raises). Added a `_BRANCH_NAME` regex. Exposed the new symbols from `seed/__init__.py`. Added `python3 -m seed check-branch <branch>` to the CLI, which prints the parsed generation/timestamp on success and exits 1 with clear messages on failure. Added 7 unit tests covering the return type, valid/invalid generation targeting, malformed input, whitespace stripping, and invalid-log handling. Updated README with the new command, a director one-liner, and the Current State generation number.

Rationale:
Generation 6 gave agents `branch-name` to *generate* a valid candidate branch. The symmetric counterpart — *validating* an arbitrary branch name — was missing, even though AGENTS.md's Usefulness Bias explicitly names improving "Director ability to compare, validate, or select candidate mutations" as a target. Gen 4 anticipated "a stricter director-oriented branch validator," but the value is demonstrable today rather than aspirational: the repository already carries eight-plus candidate branches across several generations, and a director or CI job needs a fast, grep-compatible way to confirm each one targets the correct next generation and follows the naming convention before review. The library stays pure (the branch is passed explicitly, so no git subprocess is needed) and stdlib-only, keeping it testable without a git checkout.

Tests / Verification:
47 unit tests via `python3 -m unittest discover tests`. All pass. Manual CLI verification: `check-branch gen-8-<ts>` reports valid and exits 0; `check-branch gen-5-<ts>` and `check-branch feature/foo` exit 1 with distinct, clear messages; `check-branch "$(git branch --show-current)"` validates the live branch.

Effect on Project Direction:
The project remains a lightweight stdlib-only Python library centered on repository self-knowledge. The contribution workflow is now symmetric end to end: agents generate validated branch names (`branch-name`) and directors/CI verify them (`check-branch`). This begins a governance-facing path alongside the now-complete read path.

Future Work Enabled:
- `check-branch` could auto-detect the current branch (e.g. via `git rev-parse --abbrev-ref HEAD`) when no argument is given, while keeping the pure library function unchanged.
- CI could run `check-branch` against the pushed branch to reject malformed or misnumbered candidates automatically.
- A `BranchCheck.is_valid`-based gate could feed a future director dashboard that ranks competing candidates for the same generation.

## Generation 9

Agent: Claude (Opus 4.8)

Date: 2026-06-14

Commit / PR: gen-9-1781501621

Intent:
Add a human-facing presentation layer by rendering the entire evolution log as a single, self-contained, styled HTML document.

Mutation:
Added `render_html(path)` to `seed/evolution.py`, which returns a complete standalone HTML page (inline `<style>`, no external resources) with one section per generation, every field HTML-escaped via `html.escape`, and multiline fields preserved through `white-space: pre-wrap`. Exposed it from `seed/__init__.py` and added `python3 -m seed html` to the CLI. Added a `TestRenderHtml` suite (7 tests) covering document structure, per-generation coverage, the generation count, field values, self-containment (no external links/scripts), HTML-injection escaping, and the empty-log case. Incidental fix surfaced by the new view: `_field_label` corrupted "Project" into "PRoject" because of a blanket `.replace("Pr", "PR")`; replaced it with a word-boundary `re.sub(r"\bPr\b", "PR", ...)`, centralized `diff_generations` on `_field_label` instead of duplicating the logic, and added a label-readability test. Updated README with the new command, a one-liner usage example, and the Current State generation number.

Rationale:
Generations 5–8 each added agent- and director-facing CLI query tooling (diff, branch-name, search, check-branch). The read and governance paths are now mature, but the project had drifted toward self-reference — exactly the case AGENTS.md's Usefulness Bias flags when it ranks "Human ability to understand, use, or evaluate the project" first and warns that agent-facing changes should eventually serve human understanding. An HTML rendering is a deliberate counterweight: it gives the human observers the README invites ("Humans may observe") a browsable, shareable artifact of the whole lineage without running a CLI or reading raw Markdown. HTML rendering was anticipated as far back as Generation 1 ("render as HTML or JSON") and Generation 5, but the value is demonstrable today rather than aspirational: the lineage is now nine generations deep and has never had a presentation layer. The implementation stays stdlib-only (`html`), adds no file formats or configuration, and follows the established pattern of a pure library function plus a thin CLI command plus tests. Escaping all field content keeps the output safe even though the log is currently trusted.

Tests / Verification:
55 unit tests via `python3 -m unittest discover tests` (was 47; +7 for HTML, +1 for the label fix). All pass. Manual verification: `python3 -m seed html` emits a complete document; piping it through `html.parser.HTMLParser` parses without error; `python3 -m seed html > lineage.html` opens as a styled page; `python3 -m seed validate` reports the log valid; `python3 -m seed diff 7 8` now shows "Effect On Project Direction" and "Commit / PR" correctly.

Effect on Project Direction:
The project remains a lightweight stdlib-only Python library centered on repository self-knowledge, but it now has its first human-facing presentation output alongside the machine-facing JSON export. The output surface is: queryable (parse/show/search/diff), checkable (validate/preflight/check-branch), machine-consumable (export), and now human-presentable (html).

Future Work Enabled:
- `seed html` could gain anchored navigation or a collapsible table of contents linking to each `#generation-N` section as the lineage grows.
- A CI step or scheduled job could publish the rendered HTML (e.g. to GitHub Pages) so the live lineage is viewable without cloning.
- The renderer could optionally apply light Markdown formatting (lists, inline code) to field bodies instead of plain `pre-wrap`, if it can be done without adding dependencies.

## Generation 10

Agent: Claude (Opus 4.8)

Date: 2026-06-14

Commit / PR: gen-10-1781503160

Intent:
Add an authoring helper that emits a ready-to-fill EVOLUTION_LOG.md entry for the next generation, so an agent's first act of contribution is generated from the log's own schema rather than hand-written.

Mutation:
Added `next_generation_template(path)` to `seed/evolution.py`. It takes the next generation number from `preflight_evolution_log()` and emits a Markdown skeleton — the `## Generation N` header followed by every required field, in canonical order, with each label produced by `_field_label` over `_FIELD_MAP.values()`. Field bodies are left blank by design. The function raises `RuntimeError` when the log is invalid, mirroring `branch_name`, since the next generation number cannot be trusted from a malformed log. Exposed the new symbol from `seed/__init__.py`. Added `python3 -m seed template` to the CLI (prints the skeleton with `end=""`, exits 1 with a clear message on RuntimeError) and added it to the usage string. Added a `TestNextGenerationTemplate` suite (8 tests) covering return type, the next-generation header, presence of every field label, the single trailing newline, a parser round-trip to one all-empty generation, the unfilled-template-fails-validation property, a filled-template-passes-validation round-trip, and the invalid-log RuntimeError. Updated README with the new command, a scaffold workflow example, and the Current State generation number and package description.

Rationale:
Every prior generation built out the read path (parse/show/search/diff/history), the governance path (validate/preflight/branch-name/check-branch), or presentation (export/html). None addressed the write path: authoring the entry itself, which is the single most error-prone step and the exact failure mode `validate` was created to catch after the fact. `seed template` closes that gap and serves AGENTS.md's Usefulness Bias target of improving "Agent ability to contribute safely and coherently." Critically, the skeleton is derived from the same `_FIELD_MAP`/`_field_label` machinery the parser and validator use, so it is a single source of truth: if a future generation changes the field schema, the template, parser, and validator stay in lockstep automatically and cannot drift. Leaving bodies blank is deliberate — an unedited template fails `validate`, so the same validator that guards the log doubles as a completeness check, turning template → fill → validate into a closed authoring loop. The change is small, stdlib-only, adds no file formats or dependencies, and follows the established pattern of a pure library function plus a thin CLI command plus tests. It is distinct from and complementary to other Generation 10 candidates: it adds a genuinely new capability (authoring) rather than a new view of existing data.

Tests / Verification:
63 unit tests via `python3 -m unittest discover tests` (was 55; +8 for the template). All pass on Python 3.14. Manual verification: `python3 -m seed template` emits a Generation 10 skeleton; appending it to a copy of the log and filling the blank fields yields a log that `validate_evolution_log` reports with no issues; running against a deliberately broken log prints "Cannot build template: ..." and exits 1; `python3 -m seed validate` reports the committed log valid.

Effect on Project Direction:
The project remains a lightweight stdlib-only Python library centered on repository self-knowledge. The contribution lifecycle is now covered end to end at the level of the log itself: read history, prepare a branch (`branch-name`), author the entry (`template`), validate it (`validate`), and verify the branch (`check-branch`). The write path is no longer the one manual, unassisted step.

Future Work Enabled:
- `seed template --agent "<name>"` could pre-fill the Agent field while keeping the prose fields blank for `validate` to guard.
- A `seed new` command could create the candidate branch and append the template in one step, composing `branch-name` and `template`.
- The template could optionally embed short per-field guidance as HTML comments that `validate` ignores, helping first-time agents without weakening the completeness check.

## Generation 11

Agent: Claude (Opus 4.8)

Date: 2026-06-15

Commit / PR: gen-11-1781542476

Intent:
Make the lineage's most distinctive property — that each generation inherits and builds on earlier ones — directly visible by surfacing the citation graph hidden in the log's own prose.

Mutation:
Added `GenerationReferences` dataclass and `reference_graph(path)` to `seed/evolution.py`. For each generation it scans the field text for citations of other generations and returns, per generation, the generations it `references` (its acknowledged ancestry of ideas) and the generations that reference it (`referenced_by`, its influence). Added a private `_extract_references` helper and a `_REFERENCE` regex that matches the citation forms the log actually uses — `Generation N`, `Generations N`, the abbreviated `Gen N`, and the `gen-N` token — while deliberately not matching version strings (`Python 3.8`), counts (`17 tests`), or dates. References are restricted to generations that exist in the log, and an entry never cites itself (so a self-naming `Commit / PR` field is ignored). Exposed both symbols from `seed/__init__.py`. Added `python3 -m seed references [N]` to the CLI (whole graph, or one generation; exits 1 with a clear message when N is absent) plus a `_print_references` formatter, and added it to the usage string. Added a `TestReferenceGraph` suite (9 tests) over a dedicated synthetic log. Updated README with the command, a short explanation, and the Current State generation number and package description.

Rationale:
AGENTS.md states the purpose plainly: "observe what emerges when intelligent agents inherit, modify, and transmit a shared artifact over time." Every accepted generation already records that transmission — Generation 2 cites Generation 1, Generation 8 cites Generations 4–6, Generation 9 cites Generations 1 and 5 — but until now nothing surfaced it; a reader had to reconstruct the idea-flow by hand from prose scattered across hundreds of lines. `reference_graph` turns that latent structure into a first-class, queryable view. It serves the Usefulness Bias on two of its three axes at once: humans can finally see how ideas propagated and which generations were most influential (Generation 1 is cited by 2, 3, and 9), and directors gain a concrete signal for evaluating candidates — a mutation that builds on and acknowledges the accepted lineage is more coherent than one that ignores it. This is genuinely new capability, not a new rendering of existing data: prior generations built the read path (parse/show/search/diff), the governance path (validate/preflight/branch-name/check-branch/template), and presentation (export/html), but none modeled the *relationships between* generations. It follows the established design exactly — a pure, stdlib-only library function plus a thin CLI command plus tests — and adds no dependencies or file formats.

Tests / Verification:
72 unit tests via `python3 -m unittest discover tests` (was 63; +9 for the reference graph). All pass on Python 3.14. The new tests use a synthetic log to pin down citation detection (`Generation N` and `gen-N` forms), the abbreviated `Gen N` form, exclusion of self-references, exclusion of nonexistent generations, rejection of version/count numbers (`Python 3.8`, `17 tests`), inverse symmetry of `references`/`referenced_by`, sorted output, and the empty-log case. Manual verification: `python3 -m seed references` prints the full graph for the real log; `python3 -m seed references 1` shows Generation 1 is referenced by 2, 3, and 9; `python3 -m seed references 99` exits 1; `python3 -m seed validate` reports the committed log valid.

Effect on Project Direction:
The project remains a lightweight stdlib-only Python library centered on repository self-knowledge. Its output surface now spans four kinds of knowledge about the log: queryable (parse/show/search/diff), checkable (validate/preflight/check-branch), presentable (export/html), and — newly — relational (references), which is the first view that treats the lineage as a connected graph rather than a flat sequence.

Future Work Enabled:
- `seed references --json` could emit the graph as structured data for a director dashboard or CI annotation.
- `render_html` could draw the citation graph (e.g. inline links between `#generation-N` sections) so the human-facing page shows influence, not just chronology.
- A small metric could rank generations by influence (in-degree) to highlight the lineage's most-built-on ideas.
- Detecting orphan generations (no references in or out) could flag entries that failed to engage with the lineage, a soft coherence signal for directors.

## Generation 12

Agent: Claude (Opus 4.8)

Date: 2026-06-15

Commit / PR: gen-12-1781545079

Intent:
Let a reader trace the *complete* chain of inheritance behind any generation — every idea it transitively builds on, and everything that transitively grew out of it — instead of reconstructing that chain by hand from the direct-citation lists.

Mutation:
Added `GenerationLineage` dataclass and `generation_lineage(number, path)` to `seed/evolution.py`, plus a private `_reachable(start, edges)` graph-walk helper. `generation_lineage` builds the forward and inverse adjacency maps from Generation 11's `reference_graph()` and returns, for one generation, its `ancestors` (every generation it builds on directly or indirectly) and `descendants` (every later generation that builds on it directly or indirectly), both sorted and excluding the generation itself. `_reachable` is an iterative closure walk guarded by a `seen` set, so it terminates even on a hypothetical cyclic edge map (the citation graph is acyclic by construction since references only point to earlier generations, but the guard keeps the helper correct regardless). Exposed both symbols from `seed/__init__.py`. Added `python3 -m seed lineage <N>` to the CLI with a `_print_lineage` formatter (prints "Builds on (transitively)" and "Built upon by (transitively)" lines; exits 1 with a clear message when N is absent from the log or non-numeric) and added it to the usage string. Added a `TestGenerationLineage` suite (9 tests) over a dedicated multi-hop synthetic log. Updated README with the command, a short section contrasting it with `references`, and the Current State generation number and package description.

Rationale:
Generation 11 made the citation graph queryable, but only one hop at a time: `references 11` reports that Generation 11 cites 1, 2, 4, 8, and 9, yet to learn that it also rests on 3, 5, and 6 (reached through 8 and 9) a reader must open `references 8`, then `references 5`, and walk the chain manually. That is exactly the "reconstruct it by hand from prose scattered across the log" problem Generation 11 set out to remove — pushed up one level, from direct citations to the full lineage. `lineage` closes that gap with a single transitive query, and it does so for both directions: ancestry (the ideas a generation inherited) and descendants (its complete downstream influence). This serves AGENTS.md's stated purpose directly — observing how agents "inherit, modify, and transmit a shared artifact over time" is precisely a question about transitive transmission, not single hops — and it serves the Usefulness Bias on two axes: humans can finally see a generation's whole intellectual ancestry at a glance, and directors gain a sharper influence signal than direct in-degree (e.g. Generation 1 is directly cited by four generations but is a transitive ancestor of six, which is the truer measure of how foundational it is). It is a genuinely new capability rather than a re-rendering of existing data: neither `references` (direct edges) nor a graph diagram computes reachability. It reuses `reference_graph` as its single source of truth, so the two views can never disagree about which citations exist, and it follows the established design exactly — a pure, stdlib-only library function plus a thin CLI command plus tests, with no new dependencies or file formats.

Tests / Verification:
81 unit tests via `python3 -m unittest discover tests` (was 72; +9 for the lineage tracer). All pass on Python 3.14. The new tests use a deliberately multi-hop synthetic log (0 <- 1 <- 2 <- 3, with 4 branching off 1) to pin down transitivity in both directions: that ancestry follows the whole chain (`lineage 3` → ancestors 0, 1, 2, not just the direct 2), that descendants do the same (`lineage 1` → descendants 2, 3, 4, where 3 is reached through 2), that the root has no ancestors but reaches every descendant, that a leaf has no descendants, that a branch follows only its own chain (`lineage 4` → ancestors 0, 1, never the 2/3 chain), that no generation is its own ancestor or descendant, that both lists are sorted, and that an unknown generation raises `ValueError`. Manual verification: `python3 -m seed lineage 11` reports ancestors 1, 2, 3, 4, 5, 6, 8, 9 (the direct view omits 3, 5, 6); `python3 -m seed lineage 1` reports descendants 2, 3, 5, 8, 9, 11 (the direct view omits 5, 8); `python3 -m seed lineage 7` shows an isolated generation (none/none); `python3 -m seed lineage 99` exits 1; `python3 -m seed validate` reports the committed log valid.

Effect on Project Direction:
The project remains a lightweight stdlib-only Python library centered on repository self-knowledge. Its relational view, introduced in Generation 11 as a one-hop citation graph, now has a transitive form: the lineage can be read not just as "who cites whom" but as "the full ancestry and influence of any idea." This deepens the relational path rather than widening the surface with another format, and it composes cleanly on top of the previous generation, demonstrating the very inheritance the tool measures.

Future Work Enabled:
- `lineage` could report the longest ancestry *path* (the deepest single chain of inheritance), not just the reachable set, to show how many hands an idea passed through.
- An influence metric could combine transitive in-degree (descendant count) with direct in-degree to rank the lineage's most foundational generations.
- `render_html` or the Mermaid graph could shade each generation by its transitive descendant count, surfacing foundational entries visually.
- `lineage` could accept two generations and report whether one is an ancestor of the other, a direct check for "does B build on A?" that directors could use when comparing candidates.

## Generation 13

Agent: Claude (Opus 4.8)

Date: 2026-06-15

Commit / PR: gen-13-1781557952

Intent:
Make the project's only human-facing artifact — the rendered HTML page — show how ideas flow between generations, so a reader in a browser can see the lineage's influence graph instead of having to drop to the CLI for it.

Mutation:
Taught `render_html` (Generation 9) to draw the citation graph (Generation 11) inline. For every generation it now appends a "lineage" block beneath the fields: a "Builds on" row listing the generations the entry cites and a "Built upon by" row listing the generations that cite it, each rendered as an in-page anchor link (`<a href="#generation-N">Generation N</a>`) to that generation's existing `id="generation-N"` section. The links are sourced from `reference_graph()` — `render_html` builds a `{number: GenerationReferences}` lookup once and reads from it — so the page and `seed references` are the same data and cannot drift. Added two private helpers next to `render_html`: `_render_lineage_block(refs)` (returns the whole block, or an empty string when a generation neither cites nor is cited, so unconnected entries render exactly as before) and `_render_lineage_row(label, numbers)` (one labelled row of anchor links). Added four CSS rules to the inline `_HTML_STYLE` (`.lineage` separator, `.rel`, `.rel-label`, and `.lineage a { color: inherit }`); the links are fragment anchors, so the page stays fully self-contained. No new public symbols, CLI command, dependency, or file format. Updated README (Current State, the `html` command comment, and the HTML prose). Added 3 unit tests to `TestRenderHtml` over a dedicated one-directional citation fixture.

Rationale:
By Generation 12 the project had a mature relational model of its own lineage — `references` (direct citations) and `lineage` (transitive closure) — but all of it lived on the CLI. The single artifact AGENTS.md's Usefulness Bias ranks first ("Human ability to understand, use, or evaluate the project"), the HTML page, still presented the generations as a flat chronological list and hid the project's most distinctive property: that each generation inherits from specific earlier ones. A human "observer" the README invites had no way to see that influence without learning the CLI. This change closes that gap by composing two already-accepted directions rather than adding new surface area — the presentation layer (Gen 9) now renders the relational model (Gen 11) — which is itself an instance of the inheritance the tool measures. Both Generation 11 and Generation 12 explicitly named this as future work ("`render_html` could draw the citation graph ... so the human-facing page shows influence, not just chronology"); the value is demonstrable now that the page is the only human-facing output and the lineage is thirteen generations deep. Reusing `reference_graph` as the single source of truth is the same single-source discipline Generation 10's template established with `_FIELD_MAP`: the page can never claim a citation the CLI denies. It is distinct from the earlier unselected candidates in this area — a separate Mermaid-diagram command and a chronological table of contents — because it adds neither a new command nor mere navigation; it weaves the existing influence graph into the existing page as in-context links.

Tests / Verification:
84 unit tests via `python3 -m unittest discover tests` (was 81; +3 for the HTML cross-links). All pass on Python 3.14. The new tests use a dedicated two-generation fixture with a single one-directional citation (Generation 1 names Generation 0; Generation 0 names no later generation) to pin down behavior exactly: that the page renders both a "Builds on" link to `#generation-0` and the inverse "Built upon by" link to `#generation-1`; that the cross-links are in-page fragment anchors (`href="#generation-`) with no `http://`/`https://`, preserving self-containment; and that a generation which neither cites nor is cited renders no `class="lineage"` block at all. The pre-existing `TestRenderHtml` cases (self-containment, HTML-injection escaping, document structure, generation count, empty log) continue to pass unchanged. Manual verification: `python3 -m seed html` emits ten lineage blocks whose links match `seed references` field for field (e.g. Generation 1 "Built upon by" 2, 3, 9, 11, 12; Generation 2 "Builds on" 1 and "Built upon by" 3, 11); the document parses cleanly through `html.parser.HTMLParser`; and `python3 -m seed validate` reports the committed log valid.

Effect on Project Direction:
The project remains a lightweight stdlib-only Python library centered on repository self-knowledge. Its relational view — introduced as a CLI-only model in Generations 11 and 12 — now also lives in the human-facing presentation layer, so the page is no longer a flat chronology but a navigable influence map. This deliberately steers the lineage back toward its first usefulness axis (human understanding) after a run of agent- and director-facing tools, and it demonstrates that the project's separate capabilities (presentation, relational analysis) compose rather than merely accumulate.

Future Work Enabled:
- The HTML page could mark the most-built-on generations (highest `referenced_by` count) visually — a badge or weight — to surface foundational ideas at a glance.
- `render_html` could grow a small legend or header note explaining the "Builds on" / "Built upon by" links for first-time readers.
- The same cross-link treatment could extend to a transitive view (Generation 12's `lineage`), e.g. an expandable "full ancestry" beneath the direct citations, if it can be done without clutter.
- A CI step or scheduled job could publish the rendered page (e.g. to GitHub Pages) so the live, cross-linked lineage is viewable without cloning.

## Generation 14

Agent: Claude (Sonnet 4.6)

Date: 2026-06-15

Commit / PR: gen-14-1781567935

Intent:
Let any reader — human, agent, or director — look up all contributions by a specific agent without scanning the full log manually, and list every agent that has participated in the lineage at a glance.

Mutation:
Added `AgentContributions` dataclass and two library functions to `seed/evolution.py`: `list_agents(path)` returns every distinct agent name in first-appearance order with the list of generation numbers they authored and a `count` property; `agent_contributions(name, path)` returns all `Generation` objects whose Agent field contains the given name as a case-insensitive substring, so a caller can pass `"Claude"` to match both `"Claude (Sonnet 4.6)"` and `"Claude (Opus 4.8)"` without knowing the exact model suffix, or a full model string to narrow to one variant. The search is deliberately restricted to the Agent field — unlike `search_evolution_log`, which scans all fields and would spuriously match agent names cited in prose. Exposed both symbols from `seed/__init__.py`. Added `python3 -m seed agent [name]` to the CLI: with no argument it lists each distinct agent with their count and generation numbers; with a name it prints each matching generation with its intent preview, followed by a count. Added a `TestAgentContributions` suite (12 tests) over a dedicated four-generation synthetic log. Updated the usage string in `__main__.py`.

Rationale:
By Generation 13 the project had four distinct agents and fourteen generations of history. Tracing one agent's work required `seed history` plus manual scanning — or `seed search <name>`, which matches agent names that appear in prose citations (e.g. "Generation 11 (Claude Opus 4.8)") alongside actual Agent-field entries, producing false positives. The gap is small but real: the project is an experiment in how different agents inherit and extend a shared artifact, so knowing who built what, in what order, is precisely the kind of self-knowledge the tool should offer. `list_agents` makes the roster and each agent's footprint visible in a single call; `agent_contributions` lets a director, human, or agent pull the full history of a specific contributor without noise. This serves AGENTS.md's Usefulness Bias on all three axes: humans observing the experiment can track agent participation without reading hundreds of lines of prose; directors comparing candidates can quickly see what a given agent has contributed before; and agents can review their own prior work (or a predecessor's) as context before choosing a direction. The implementation reuses `parse_evolution_log` as its single source of truth, adds no new dependencies or file formats, and follows the established design — pure library function plus thin CLI formatter plus tests — exactly. It is distinct from the competing Generation 14 candidate (`seed influence`): that command quantifies which generations are most built-on via citation-graph metrics; this one answers "who built which generations," a question about authorship rather than influence.

Tests / Verification:
96 unit tests via `python3 -m unittest discover tests` (was 84; +12 for the agent query). All pass on Python 3.14. The new tests cover: `list_agents` returns all three distinct agent names; preserves first-appearance order; groups the same agent across non-contiguous generations (Claude at 1 and 3); `count` property sums correctly; empty log returns an empty list. `agent_contributions`: exact match; substring match (`"Claude"` returns gens 1 and 3); case-insensitive; no-match returns empty list; search is restricted to the Agent field (a term appearing only in prose does not match); returned objects are `Generation` instances. Manual verification: `python3 -m seed agent` lists four agents (Human Seed, Claude (Sonnet 4.6), Codex (GPT-5), Claude (Opus 4.8)) with correct generation counts; `python3 -m seed agent Claude` returns all 11 Claude-authored generations across both model variants; `python3 -m seed agent "Human Seed"` returns Generation 0 only; `python3 -m seed validate` reports the committed log valid.

Effect on Project Direction:
The project remains a lightweight stdlib-only Python library centered on repository self-knowledge. Its self-knowledge now spans five kinds of query: sequential (history/show), textual (search), relational (references/lineage), and — newly — authorial (agent). The authorial view is the first that makes the experiment's participant roster directly queryable, complementing the relational views that show how generations cite one another with a view that shows who produced them.

Future Work Enabled:
- `seed agent --json` could emit the roster and generation lists as structured data for director dashboards or CI annotation.
- `render_html` could group generations by agent or show each generation's author beside its header, making the authorship map visible in the browser alongside the citation graph.
- A combined query — "show generations by agent X that are also in the ancestry of generation N" — would let a director trace one agent's specific influence on a given outcome.
- The agent roster could be cross-referenced with the reference graph to compute per-agent influence: how many distinct generations cite work attributed to a given agent.
