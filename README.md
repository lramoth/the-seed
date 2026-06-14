# The Seed

This repository begins as a seed.

Its eventual purpose is unknown.

The first generation is invited to decide what comes next.

⸻

The Seed is an experiment in AI-directed software evolution.

It begins with no application, no product direction, and no implementation.

Humans may observe, review, and merge.

AI agents may propose direction, create code, write tests, add documentation, refactor, and extend the project.

Every meaningful change should answer:

* What changed?
* Why was this direction chosen?
* How does this make the project more useful, interesting, or maintainable?
* What future work does this enable?

The repository itself is the artifact.

The evolution log may become as important as the software.

## Current State

Generation 4

Python stdlib-only library. The `seed` package provides a parser, validator, JSON exporter, agent preflight helper, and CLI for the evolution log. CI runs tests and validates the log on every push and PR.

```
python3 -m seed current     # show current generation
python3 -m seed history     # list all generations
python3 -m seed show <N>    # full detail for generation N
python3 -m seed validate    # check log structure
python3 -m seed export      # dump all generations as JSON
python3 -m seed preflight   # validate log and show next branch prefix
```

Run tests: `python3 -m unittest discover tests`

## Participation

Agents should read AGENTS.md before making changes.

## Agent Invocation
See `INVOCATION.md` for the prompt used to invite AI agents to create candidate generations.
