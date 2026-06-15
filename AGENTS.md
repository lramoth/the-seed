# Agent Instructions

This repository is an experiment in AI-directed software evolution.

You are invited to create the next generation of the project.

The repository begins with a seed and evolves through a series of mutations. Some mutations survive and become part of the lineage. Others do not.

Before making changes, review:

- README.md
- EVOLUTION_LOG.md
- Existing source code and documentation

Understand the current state of the project before proposing a new direction.

## You May

- Choose a project direction
- Continue the current direction
- Extend the current direction
- Refine the current direction
- Challenge the current direction if justified
- Add code
- Add tests
- Add documentation
- Add project structure
- Refactor existing work
- Propose new behavior

## You Must

- Keep changes small and coherent
- Explain your reasoning
- Prefer maintainability and clarity
- Update EVOLUTION_LOG.md
- Justify how your contribution changes the project
- Avoid unnecessary frameworks and dependencies
- Avoid large, unfocused rewrites
- Leave the project in a working state

## You Should Prefer

- Utility
- Simplicity
- Maintainability
- Testability
- Clear documentation
- Novelty when it creates meaningful value

## First Generation Guidance

This section applies only when a repository contains Generation 0 and has not yet accepted a Generation 1 contribution.

If this is the first contribution after Generation 0, you may choose the initial direction of the project.

Do not ask a human what to build.

Choose a direction based on the repository's purpose and constraints.

Your contribution should be small enough to review but meaningful enough to establish a possible future path.

## Evolution Log Format

Append entries to `EVOLUTION_LOG.md` using the following format:

## Generation N

Agent:
Date:
Commit / PR:
Intent:
Mutation:
Rationale:
Tests / Verification:
Effect on Project Direction:
Future Work Enabled:

## Branch Guidance

Agents should create work on a uniquely named branch.

Branch names must follow the format:

`gen-N-<unix_timestamp>`

Examples:

- `gen-2-1750089012`
- `gen-3-1750089258`

The generation number `N` must be the next available generation number.

The next available generation number is determined by the most recent accepted generation in the lineage.

If the accepted lineage ends at Generation 4 and no Generation 5 candidate has been selected, future candidates should continue creating Generation 5 branches.

Rejected, deferred, abandoned, or unselected candidate branches do not advance the lineage.

Agents must not create branches for future generations.

For example, if the current accepted lineage ends at Generation 2, valid branch names begin with:

`gen-3-`

and branches such as:

`gen-4-*`
`gen-5-*`

are invalid.

Multiple candidate branches for the same generation are permitted.

Agents should commit their changes and push their branch to the repository.

Agents must not create pull requests.

Agents must not merge branches.

Agents must not delete branches.

## Selection

Not all mutations survive.

A contribution may be accepted or rejected based on:

- Usefulness
- Coherence
- Maintainability
- Testability
- Clarity of rationale
- Consistency with the project's current state

Selection is currently performed by a human reviewer.

Future generations may propose alternative governance mechanisms, including AI-assisted review or AI-directed selection.

## Current State

The current state of the project is defined by:

1. The contents of the `main` branch.
2. The evolution history recorded in `EVOLUTION_LOG.md`.
3. Previously accepted generations.

If there is a conflict between a proposed change and a previously accepted generation, the agent should explicitly explain why the change is necessary.

## Director Guidance

The Seed Director is a governance actor responsible for evaluating candidate mutations.

The Director may:

- Validate candidate branches
- Evaluate competing mutations
- Recommend a candidate for acceptance
- Create pull requests as part of an approved governance process
- Choose not to select any candidate. See Null Selection.

The Director must not merge changes directly into `main`.

Final acceptance remains the responsibility of the current selection process.

## Null Selection

A generation is accepted only if it improves the project according to the current selection criteria.

If no candidate provides sufficient value, coherence, usefulness, or improvement, the generation may be skipped.

The lineage remains unchanged and future candidates may compete for the same next generation number.

## Usefulness Bias

The project may evolve in many directions, but contributions should prefer usefulness over self-reference.

A useful contribution should improve at least one of the following:

- Human ability to understand, use, or evaluate the project
- Agent ability to contribute safely and coherently
- Director ability to compare, validate, or select candidate mutations

Agent-facing improvements are welcome, but they should eventually serve human understanding, project usefulness, or governance clarity.

Purely self-referential changes should justify why they make the project more usable, legible, or governable.

## Philosophy

The purpose of this repository is not only to produce software.

The purpose is to observe what emerges when intelligent agents inherit, modify, and transmit a shared artifact over time.

The project may become a useful tool, a library, an application, an infrastructure system, a protocol, or something else entirely.

No particular outcome is required.

Emergence is welcome. Selection favors usefulness, clarity, and long-term value.

Future Work suggestions are advisory, not authoritative.

Agents should evaluate whether suggested future work remains useful and relevant.

Each generation should leave behind a clear record of what it changed and why.

The `main` branch represents the current lineage of the project.

Branches, rejected mutations, abandoned directions, and competing candidate generations are part of the experiment, but only accepted generations become part of the lineage.

