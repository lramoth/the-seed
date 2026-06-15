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
footer { opacity: 0.6; font-size: 0.9rem; margin-top: 2rem; }
"""


def render_html(path: Path | str = "EVOLUTION_LOG.md") -> str:
    """Return the full evolution log as a self-contained HTML document.

    The output is a complete, standalone HTML page (inline CSS, no external
    resources) so a human can open it in a browser or share it without running
    the CLI. Every field value is HTML-escaped, so untrusted log content cannot
    inject markup. Multiline fields keep their line breaks via ``white-space:
    pre-wrap``.
    """
    generations = parse_evolution_log(path)

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
