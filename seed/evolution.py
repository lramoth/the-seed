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
