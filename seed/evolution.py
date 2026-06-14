from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


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
            return label.title().replace("Pr", "PR")
    return attr
