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

Generation 11

Python stdlib-only library. The `seed` package provides a parser, validator, JSON exporter, HTML renderer, agent preflight helper, branch name generator, next-entry template, branch name validator, diff viewer, full-text search, lineage reference graph, and CLI for the evolution log. CI runs tests and validates the log on every push and PR.

```
python3 -m seed current              # show current generation
python3 -m seed history              # list all generations
python3 -m seed show <N>             # full detail for generation N
python3 -m seed validate             # check log structure
python3 -m seed export               # dump all generations as JSON
python3 -m seed html                 # render the whole log as a standalone HTML page
python3 -m seed preflight            # validate log and show next branch prefix
python3 -m seed branch-name          # print a ready-to-use branch name for the next generation
python3 -m seed template             # print a ready-to-fill log entry for the next generation
python3 -m seed check-branch <name>  # validate a candidate branch name against the log
python3 -m seed diff <N> <M>         # compare two generations field by field
python3 -m seed search <term>        # find generations containing a keyword in any field
python3 -m seed references [N]       # show which generations cite which (lineage influence)
```

The lineage is not just a sequence — each generation cites the ones whose ideas
it builds on. `references` makes that visible: for every generation it lists the
earlier generations it cites and the later generations that cite it, so a human
or director can see at a glance how ideas propagated and which generations were
most influential.

```
python3 -m seed references     # whole graph: references + referenced-by per generation
python3 -m seed references 5   # focus on a single generation
```

Humans can render a browsable, shareable view of the whole lineage with no
extra tooling — the output is a single self-contained HTML file:

```
python3 -m seed html > lineage.html  # then open lineage.html in any browser
```

Agents can use `branch-name` to script the full contribution workflow:

```
git checkout -b $(python3 -m seed branch-name)
```

Agents can scaffold the new evolution log entry from the same field schema the
parser and validator use, then fill it in (an unedited template intentionally
fails `validate`, so it doubles as a completeness check):

```
python3 -m seed template >> EVOLUTION_LOG.md  # then edit the appended entry
```

Directors and CI can use `check-branch` to confirm a candidate branch is a
legitimate contribution to the current next generation (exit code 0 when valid,
1 when not):

```
python3 -m seed check-branch "$(git branch --show-current)"
```

Run tests: `python3 -m unittest discover tests`

## Participation

Agents should read AGENTS.md before making changes.

## Agent Invocation
See `INVOCATION.md` for the prompt used to invite AI agents to create candidate generations.
