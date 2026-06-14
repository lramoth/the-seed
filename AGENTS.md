# Agent Instructions

This repository is an experiment in AI-directed software evolution.

You are invited to create the next generation of the project.

## You May

* Choose a project direction
* Add code
* Add tests
* Add documentation
* Add project structure
* Refactor existing work
* Propose new behavior
* Challenge previous direction if justified

## You Must

* Keep changes small and coherent
* Explain your reasoning
* Prefer maintainability and clarity
* Update EVOLUTION_LOG.md
* Justify how your contribution changes the project
* Avoid unnecessary frameworks and dependencies
* Avoid large, unfocused rewrites

## You Should Prefer

* Utility
* Novelty
* Simplicity
* Maintainability
* Testability
* Clear documentation

## First Generation Guidance

If this is the first contribution after Generation 0, you may choose the initial direction of the project.

Do not ask a human what to build.

Choose a direction based on the repository’s purpose and constraints.

Your contribution should be small enough to review but meaningful enough to establish a possible future path.

## Evolution Log Format

Append entries using:

Generation N

Agent:
Date:
Commit / PR:
Intent:
Mutation:
Rationale:
Tests / Verification:
Effect on Project Direction:
Future Work Enabled:

## Pull Request Guidance

Agents should create work on a branch named `gen-N`.

If GitHub CLI is available, agents should open a pull request from `gen-N` into `main`.

If GitHub CLI is not available, agents should push the branch and provide a complete pull request title and description for a human to create manually.

Agents must not merge their own pull requests.

Selection remains a human responsibility unless a later generation explicitly adds AI review governance.
