from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import html
import json
import re
import time


@dataclass
class Generation:
    number: int
    agent: str = ""
    date: str = ""
    commit: str = ""
    intent: str = ""
    mutation: str = ""
    rationale: str = ""
    tests: str = ""
    effect: str = ""
    future_work: str = ""


@dataclass
class ValidationIssue:
    message: str
    generation: int | None = None


@dataclass
class PreflightReport:
    current_generation: int | None
    next_generation: int | None
    branch_prefix: str | None
    issues: list[ValidationIssue]

    @property
    def is_valid(self) -> bool:
        return not self.issues


@dataclass
class SearchMatch:
    generation: "Generation"
    matched_fields: list[str]


@dataclass
class FieldDiff:
    field: str
    label: str
    old: str
    new: str

    @property
    def changed(self) -> bool:
        return self.old != self.new


@dataclass
class GenerationDiff:
    from_number: int
    to_number: int
    fields: list[FieldDiff]

    @property
    def changed_fields(self) -> list[FieldDiff]:
        return [f for f in self.fields if f.changed]


@dataclass
class BranchCheck:
    branch: str
    generation: int | None
    timestamp: int | None
    expected_generation: int | None
    issues: list[str]

    @property
    def is_valid(self) -> bool:
        return not self.issues


@dataclass
class GenerationReferences:
    generation: int
    references: list[int]
    referenced_by: list[int]


@dataclass
class GenerationLineage:
    generation: int
    ancestors: list[int]
    descendants: list[int]


@dataclass
class GenerationInfluence:
    generation: int
    direct_ancestors: int
    direct_descendants: int
    transitive_ancestors: int
    transitive_descendants: int


_FIELD_MAP: dict[str, str] = {
    "agent": "agent",
    "date": "date",
    "commit / pr": "commit",
    "intent": "intent",
    "mutation": "mutation",
    "rationale": "rationale",
    "tests / verification": "tests",
    "effect on project direction": "effect",
    "future work enabled": "future_work",
}

_REQUIRED_FIELDS = tuple(_FIELD_MAP.values())

_GEN_HEADER = re.compile(r"^## Generation (\d+)", re.MULTILINE)
_FIELD_LINE = re.compile(r"^([A-Za-z/ ]+?):\s*(.*)")
_BRANCH_NAME = re.compile(r"^gen-(\d+)-(\d+)$")
# A citation of another generation in an entry's prose, written as the log
# does: "Generation N", "Generations N", the abbreviated "Gen N", or a "gen-N"
# token. Deliberately anchored to those forms so version strings ("Python 3.8"),
# counts ("17 tests"), and dates never read as references.
_REFERENCE = re.compile(r"\bGen(?:eration)?s?\s+(\d+)\b|\bgen-(\d+)\b")


def parse_evolution_log(path: Path | str = "EVOLUTION_LOG.md") -> list[Generation]:
    """Parse EVOLUTION_LOG.md and return all generations in order."""
    text = Path(path).read_text(encoding="utf-8")
    parts = _GEN_HEADER.split(text)
    # parts: [preamble, num, body, num, body, ...]

    generations: list[Generation] = []
    it = iter(parts[1:])
    for num_str, body in zip(it, it):
        generations.append(_parse_generation(int(num_str), body))
    return generations


def current_generation(path: Path | str = "EVOLUTION_LOG.md") -> Generation | None:
    """Return the highest-numbered generation from the log."""
    gens = parse_evolution_log(path)
    return max(gens, key=lambda g: g.number) if gens else None


def next_generation_number(path: Path | str = "EVOLUTION_LOG.md") -> int | None:
    """Return the next generation number implied by the log."""
    current = current_generation(path)
    return current.number + 1 if current else None


def validate_evolution_log(path: Path | str = "EVOLUTION_LOG.md") -> list[ValidationIssue]:
    """Return structural issues found in EVOLUTION_LOG.md."""
    generations = parse_evolution_log(path)
    issues: list[ValidationIssue] = []

    if not generations:
        return [ValidationIssue("No generations found.")]

    seen: set[int] = set()
    for gen in generations:
        if gen.number in seen:
            issues.append(
                ValidationIssue(
                    f"Generation {gen.number} appears more than once.",
                    generation=gen.number,
                )
            )
        seen.add(gen.number)

        for field in _REQUIRED_FIELDS:
            if not getattr(gen, field).strip():
                issues.append(
                    ValidationIssue(
                        f"Missing required field: {_field_label(field)}.",
                        generation=gen.number,
                    )
                )

    numbers = [gen.number for gen in generations]
    expected = list(range(min(numbers), max(numbers) + 1))
    if numbers != expected:
        issues.append(
            ValidationIssue(
                "Generation numbers should be contiguous and in ascending order."
            )
        )

    if numbers and numbers[0] != 0:
        issues.append(ValidationIssue("Generation history should start at Generation 0."))

    return issues


def preflight_evolution_log(path: Path | str = "EVOLUTION_LOG.md") -> PreflightReport:
    """Return validation and branch guidance for the next candidate generation."""
    issues = validate_evolution_log(path)
    current = current_generation(path)
    next_generation = None if issues else next_generation_number(path)
    branch_prefix = f"gen-{next_generation}-" if next_generation is not None else None

    return PreflightReport(
        current_generation=current.number if current else None,
        next_generation=next_generation,
        branch_prefix=branch_prefix,
        issues=issues,
    )


def export_evolution_log(path: Path | str = "EVOLUTION_LOG.md") -> str:
    """Return all generations serialized as a JSON string."""
    generations = parse_evolution_log(path)
    return json.dumps([asdict(g) for g in generations], indent=2)


_HTML_STYLE = """\
:root { color-scheme: light dark; }
body { font-family: -apple-system, Segoe UI, Roboto, sans-serif;
       max-width: 50rem; margin: 0 auto; padding: 2rem 1.25rem; line-height: 1.5; }
header { border-bottom: 2px solid currentColor; margin-bottom: 2rem; }
.count { opacity: 0.7; }
article { border: 1px solid; border-radius: 8px; padding: 1rem 1.25rem;
          margin-bottom: 1.5rem; }
article h2 { margin-top: 0; }
.field { margin: 0.75rem 0; }
.field .label { font-weight: 600; }
.field .value { white-space: pre-wrap; margin: 0.15rem 0 0; }
.lineage { margin-top: 1rem; padding-top: 0.6rem; border-top: 1px dashed;
           font-size: 0.9rem; }
.lineage .rel { margin: 0.2rem 0; }
.lineage .rel-label { font-weight: 600; }
.lineage a { color: inherit; }
footer { opacity: 0.6; font-size: 0.9rem; margin-top: 2rem; }
"""


def render_html(path: Path | str = "EVOLUTION_LOG.md") -> str:
    """Return the full evolution log as a self-contained HTML document.

    The output is a complete, standalone HTML page (inline CSS, no external
    resources) so a human can open it in a browser or share it without running
    the CLI. Every field value is HTML-escaped, so untrusted log content cannot
    inject markup. Multiline fields keep their line breaks via ``white-space:
    pre-wrap``.

    Each generation's section also shows its place in the citation graph — the
    generations it builds on and the generations that build on it — as in-page
    anchor links, so the influence the CLI exposes through ``references`` is
    navigable directly in the browser. The links come from ``reference_graph``,
    so the page and ``seed references`` can never disagree.
    """
    generations = parse_evolution_log(path)
    graph = {r.generation: r for r in reference_graph(path)}

    articles: list[str] = []
    for gen in generations:
        rows: list[str] = []
        for label, attr in _FIELD_MAP.items():
            value = getattr(gen, attr)
            if not value:
                continue
            rows.append(
                '<div class="field">'
                f'<div class="label">{html.escape(_field_label(attr))}</div>'
                f'<div class="value">{html.escape(value)}</div>'
                "</div>"
            )
        articles.append(
            f'<article id="generation-{gen.number}">\n'
            f"<h2>Generation {gen.number}</h2>\n"
            + "\n".join(rows)
            + _render_lineage_block(graph.get(gen.number))
            + "\n</article>"
        )

    count = len(generations)
    body = "\n".join(articles) if articles else "<p>No generations recorded yet.</p>"
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>The Seed — Evolution Log</title>\n"
        f"<style>\n{_HTML_STYLE}</style>\n"
        "</head>\n"
        "<body>\n"
        "<header>\n"
        "<h1>The Seed — Evolution Log</h1>\n"
        f'<p class="count">{count} '
        f"{'generation' if count == 1 else 'generations'} recorded.</p>\n"
        "</header>\n"
        f"{body}\n"
        "<footer>Generated by <code>python3 -m seed html</code>.</footer>\n"
        "</body>\n"
        "</html>\n"
    )


def _render_lineage_block(refs: GenerationReferences | None) -> str:
    """Render one generation's citation links for the HTML page.

    Returns the relationships block for a generation's article — "Builds on"
    for the generations it cites and "Built upon by" for the generations that
    cite it — as in-page anchor links to their sections. Returns an empty
    string when the generation neither cites nor is cited, so an unconnected
    entry renders exactly as it did before this view existed.
    """
    if refs is None or (not refs.references and not refs.referenced_by):
        return ""

    rows: list[str] = []
    if refs.references:
        rows.append(_render_lineage_row("Builds on", refs.references))
    if refs.referenced_by:
        rows.append(_render_lineage_row("Built upon by", refs.referenced_by))
    return '\n<div class="lineage">\n' + "\n".join(rows) + "\n</div>"


def _render_lineage_row(label: str, numbers: list[int]) -> str:
    """Render one labelled row of generation anchor links (numbers are safe)."""
    links = ", ".join(
        f'<a href="#generation-{n}">Generation {n}</a>' for n in numbers
    )
    return f'<div class="rel"><span class="rel-label">{label}:</span> {links}</div>'


def branch_name(path: Path | str = "EVOLUTION_LOG.md") -> str:
    """Return a valid branch name for the next candidate generation.

    Combines the next generation number from the preflight report with the
    current Unix timestamp so the caller can use the result directly:

        git checkout -b $(python3 -m seed branch-name)

    Raises RuntimeError if the log has validation issues.
    """
    report = preflight_evolution_log(path)
    if not report.is_valid:
        messages = "; ".join(i.message for i in report.issues)
        raise RuntimeError(f"Cannot generate branch name: {messages}")
    return f"gen-{report.next_generation}-{int(time.time())}"


def next_generation_template(path: Path | str = "EVOLUTION_LOG.md") -> str:
    """Return a ready-to-fill EVOLUTION_LOG.md entry for the next generation.

    The skeleton is the authoring counterpart to ``validate``: it uses the next
    generation number from the preflight report and emits every required field,
    in canonical order, derived from the same field map the parser and validator
    use — so a filled-in template is guaranteed to parse and pass validation.

    Field bodies are left blank on purpose. An unedited template fails
    ``seed validate`` (every field reads as missing), so the same validator that
    guards the log also doubles as a completeness check once the agent fills the
    template in. Append it to the log and edit in place:

        python3 -m seed template >> EVOLUTION_LOG.md

    Raises RuntimeError if the log has validation issues, since the next
    generation number cannot be trusted when the log is malformed.
    """
    report = preflight_evolution_log(path)
    if not report.is_valid:
        messages = "; ".join(i.message for i in report.issues)
        raise RuntimeError(f"Cannot build template: {messages}")

    lines = [f"## Generation {report.next_generation}", ""]
    for attr in _FIELD_MAP.values():
        lines.append(f"{_field_label(attr)}:")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def check_branch_name(
    branch: str, path: Path | str = "EVOLUTION_LOG.md"
) -> BranchCheck:
    """Validate a candidate branch name against the evolution log.

    A valid candidate branch:
      - matches the pattern ``gen-N-<unix_timestamp>``
      - targets ``N`` equal to the next available generation number

    This is the director-facing counterpart to ``branch_name``: agents
    generate a branch name, while directors and CI use this to confirm that a
    given branch name is a legitimate candidate for the current next
    generation. It never raises; all problems are reported in ``issues`` so
    callers can rely on ``BranchCheck.is_valid`` and a clean exit code.
    """
    branch = branch.strip()
    report = preflight_evolution_log(path)
    expected = report.next_generation

    match = _BRANCH_NAME.match(branch)
    if not match:
        return BranchCheck(
            branch=branch,
            generation=None,
            timestamp=None,
            expected_generation=expected,
            issues=["Branch name must match the pattern 'gen-N-<unix_timestamp>'."],
        )

    generation = int(match.group(1))
    timestamp = int(match.group(2))
    issues: list[str] = []

    if not report.is_valid:
        issues.append(
            "Evolution log is invalid; cannot confirm the next generation number."
        )
    elif generation != expected:
        issues.append(
            f"Branch targets Generation {generation}, "
            f"but the next available generation is {expected}."
        )

    return BranchCheck(
        branch=branch,
        generation=generation,
        timestamp=timestamp,
        expected_generation=expected,
        issues=issues,
    )


def diff_generations(
    from_number: int, to_number: int, path: Path | str = "EVOLUTION_LOG.md"
) -> GenerationDiff:
    """Compare two generations field by field.

    Raises ValueError if either generation number is not found in the log.
    """
    generations = {g.number: g for g in parse_evolution_log(path)}

    for n in (from_number, to_number):
        if n not in generations:
            raise ValueError(f"Generation {n} not found in evolution log.")

    a = generations[from_number]
    b = generations[to_number]

    fields: list[FieldDiff] = []
    for label, attr in _FIELD_MAP.items():
        fields.append(
            FieldDiff(
                field=attr,
                label=_field_label(attr),
                old=getattr(a, attr),
                new=getattr(b, attr),
            )
        )
    return GenerationDiff(from_number=from_number, to_number=to_number, fields=fields)


def search_evolution_log(
    term: str, path: Path | str = "EVOLUTION_LOG.md"
) -> list[SearchMatch]:
    """Return all generations where term appears (case-insensitive) in any field."""
    lower = term.lower()
    results: list[SearchMatch] = []
    for gen in parse_evolution_log(path):
        matched = [
            attr
            for attr in _FIELD_MAP.values()
            if lower in getattr(gen, attr).lower()
        ]
        if matched:
            results.append(SearchMatch(generation=gen, matched_fields=matched))
    return results


def reference_graph(
    path: Path | str = "EVOLUTION_LOG.md",
) -> list[GenerationReferences]:
    """Map how generations cite one another in their prose.

    The Seed's stated purpose is to observe how agents "inherit, modify, and
    transmit a shared artifact over time." This makes that transmission directly
    legible: for each generation it reports which other generations the entry
    cites (its acknowledged ancestry of ideas) and which later generations cite
    it (its influence on the lineage).

    A citation is any mention of another generation in an entry's field text,
    written either as ``Generation N`` / ``Generations N`` or as a ``gen-N``
    token. Only references to generations that actually exist in the log are
    counted, and an entry never references itself (so a self-naming ``Commit /
    PR`` field is ignored). Numeric ranges such as "Generations 5-8" count only
    their first number, since the log writes the intervening generations out by
    name where it means them.
    """
    generations = parse_evolution_log(path)
    numbers = {g.number for g in generations}

    references: dict[int, set[int]] = {g.number: set() for g in generations}
    for gen in generations:
        text = "\n".join(getattr(gen, attr) for attr in _FIELD_MAP.values())
        cited = _extract_references(text) & numbers
        cited.discard(gen.number)
        references[gen.number] = cited

    referenced_by: dict[int, set[int]] = {g.number: set() for g in generations}
    for source, targets in references.items():
        for target in targets:
            referenced_by[target].add(source)

    return [
        GenerationReferences(
            generation=g.number,
            references=sorted(references[g.number]),
            referenced_by=sorted(referenced_by[g.number]),
        )
        for g in generations
    ]


def _extract_references(text: str) -> set[int]:
    """Return every generation number cited in ``text`` (see ``reference_graph``)."""
    found: set[int] = set()
    for match in _REFERENCE.finditer(text):
        number = match.group(1) or match.group(2)
        found.add(int(number))
    return found


def generation_lineage(
    number: int, path: Path | str = "EVOLUTION_LOG.md"
) -> GenerationLineage:
    """Return the transitive ancestry and descendants of a generation.

    Where ``reference_graph`` reports only the *direct* citations of each
    generation, this follows those citation edges transitively. ``ancestors``
    is every generation that ``number`` builds on directly or indirectly — the
    full intellectual lineage it inherits — and ``descendants`` is every later
    generation that builds on ``number`` directly or indirectly: its complete
    downstream influence. So if 11 cites 8 and 8 cites 5, then 5 is an ancestor
    of 11 even though 11 never names it. Both lists are sorted and never
    include ``number`` itself.

    This is the transitive counterpart to ``reference_graph``: a reader who
    wants the *whole* chain of inheritance behind a generation would otherwise
    have to walk the per-generation citation lists by hand, hop by hop.

    Raises ValueError if ``number`` is not present in the log.
    """
    graph = {r.generation: r for r in reference_graph(path)}
    if number not in graph:
        raise ValueError(f"Generation {number} not found in evolution log.")

    references = {g: ref.references for g, ref in graph.items()}
    referenced_by = {g: ref.referenced_by for g, ref in graph.items()}
    return GenerationLineage(
        generation=number,
        ancestors=sorted(_reachable(number, references)),
        descendants=sorted(_reachable(number, referenced_by)),
    )


def influence_scores(
    path: Path | str = "EVOLUTION_LOG.md",
) -> list[GenerationInfluence]:
    """Return direct and transitive influence counts for each generation.

    ``reference_graph`` answers "who cites whom?" and ``generation_lineage``
    answers "what is reachable from one generation?" This summarizes the same
    graph for ranking and scanning: direct counts are one-hop citations, while
    transitive counts include every reachable ancestor or descendant.
    """
    graph = reference_graph(path)
    references = {r.generation: r.references for r in graph}
    referenced_by = {r.generation: r.referenced_by for r in graph}

    return [
        GenerationInfluence(
            generation=ref.generation,
            direct_ancestors=len(ref.references),
            direct_descendants=len(ref.referenced_by),
            transitive_ancestors=len(_reachable(ref.generation, references)),
            transitive_descendants=len(_reachable(ref.generation, referenced_by)),
        )
        for ref in graph
    ]


def _reachable(start: int, edges: dict[int, list[int]]) -> set[int]:
    """Return every node reachable from ``start`` via ``edges`` (excluding it).

    A ``seen`` set guards against revisiting nodes, so the walk terminates even
    if the edge map ever contains a cycle (the citation graph cannot, since
    references only point to earlier generations, but the guard keeps the
    helper correct regardless of its input).
    """
    seen: set[int] = set()
    stack = list(edges.get(start, []))
    while stack:
        node = stack.pop()
        if node == start or node in seen:
            continue
        seen.add(node)
        stack.extend(edges.get(node, []))
    return seen


def _parse_generation(number: int, body: str) -> Generation:
    gen = Generation(number=number)
    current_field: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        if current_field:
            setattr(gen, current_field, "\n".join(current_lines).strip())

    for line in body.splitlines():
        m = _FIELD_LINE.match(line)
        if m:
            label = m.group(1).strip().lower()
            attr = _FIELD_MAP.get(label)
            if attr:
                flush()
                current_field = attr
                current_lines = [m.group(2)] if m.group(2) else []
                continue
        if current_field is not None:
            current_lines.append(line)

    flush()
    return gen


def _field_label(attr: str) -> str:
    for label, mapped_attr in _FIELD_MAP.items():
        if mapped_attr == attr:
            # Title-case the label, then restore the "PR" acronym only where it
            # stands alone (in "Commit / Pr"), without corrupting words like
            # "Project" that merely begin with "Pr".
            return re.sub(r"\bPr\b", "PR", label.title())
    return attr
