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
- Novelty
- Simplicity
- Maintainability
- Testability
- Clear documentation

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

## Philosophy

The purpose of this repository is not merely to produce software.

The purpose is to observe what emerges when intelligent agents inherit, modify, and transmit a shared artifact over time.

Each generation should leave behind a clear record of what it changed and why.

The `main` branch represents the current lineage of the project.

Branches, rejected mutations, abandoned directions, and competing candidate generations are part of the experiment, but only accepted generations become part of the lineage.
