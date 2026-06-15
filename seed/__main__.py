import sys
from pathlib import Path

from .evolution import (
    branch_name,
    check_branch_name,
    current_generation,
    diff_generations,
    export_evolution_log,
    next_generation_template,
    parse_evolution_log,
    preflight_evolution_log,
    reference_graph,
    render_html,
    search_evolution_log,
    validate_evolution_log,
)


def main() -> None:
    args = sys.argv[1:]
    log_path = Path("EVOLUTION_LOG.md")

    if not log_path.exists():
        print("EVOLUTION_LOG.md not found. Run from the repository root.", file=sys.stderr)
        sys.exit(1)

    command = args[0] if args else "current"

    if command == "current":
        gen = current_generation(log_path)
        if gen:
            print(f"Generation {gen.number}")
            if gen.intent:
                print(f"\nIntent: {gen.intent}")
        else:
            print("No generations found.")

    elif command == "history":
        gens = parse_evolution_log(log_path)
        for gen in gens:
            intent_preview = gen.intent[:72] + "..." if len(gen.intent) > 72 else gen.intent
            print(f"Generation {gen.number:>3}  [{gen.agent}]  {intent_preview}")

    elif command == "show" and len(args) > 1:
        try:
            n = int(args[1])
        except ValueError:
            print(f"Invalid generation number: {args[1]}", file=sys.stderr)
            sys.exit(1)
        gens = parse_evolution_log(log_path)
        matches = [g for g in gens if g.number == n]
        if not matches:
            print(f"Generation {n} not found.", file=sys.stderr)
            sys.exit(1)
        _print_generation(matches[0])

    elif command == "export":
        print(export_evolution_log(log_path))

    elif command == "html":
        print(render_html(log_path), end="")

    elif command == "preflight":
        report = preflight_evolution_log(log_path)
        if report.current_generation is None:
            print("Current generation: none")
        else:
            print(f"Current generation: {report.current_generation}")

        if report.is_valid:
            print("Validation: ok")
            print(f"Next generation: {report.next_generation}")
            print(f"Branch prefix: {report.branch_prefix}")
            return

        print("Validation: failed", file=sys.stderr)
        for issue in report.issues:
            prefix = (
                f"Generation {issue.generation}: "
                if issue.generation is not None
                else ""
            )
            print(f"- {prefix}{issue.message}", file=sys.stderr)
        sys.exit(1)

    elif command == "branch-name":
        try:
            print(branch_name(log_path))
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

    elif command == "template":
        try:
            print(next_generation_template(log_path), end="")
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

    elif command == "check-branch" and len(args) > 1:
        check = check_branch_name(args[1], log_path)
        print(f"Branch: {check.branch}")
        if check.is_valid:
            print("Status: valid")
            print(f"Generation: {check.generation}")
            print(f"Timestamp: {check.timestamp}")
            return
        print("Status: invalid", file=sys.stderr)
        for issue in check.issues:
            print(f"- {issue}", file=sys.stderr)
        sys.exit(1)

    elif command == "diff" and len(args) == 3:
        try:
            from_n = int(args[1])
            to_n = int(args[2])
        except ValueError:
            print("Usage: python -m seed diff <N> <M>", file=sys.stderr)
            sys.exit(1)
        try:
            result = diff_generations(from_n, to_n, log_path)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)
        _print_diff(result)

    elif command == "search" and len(args) > 1:
        term = " ".join(args[1:])
        matches = search_evolution_log(term, log_path)
        if not matches:
            print(f"No generations found matching {term!r}.", file=sys.stderr)
            sys.exit(1)
        for m in matches:
            gen = m.generation
            intent_preview = gen.intent.split("\n")[0][:72] + ("..." if len(gen.intent) > 72 else "")
            print(f"Generation {gen.number}  [{gen.agent}]  {gen.date}")
            print(f"  Matched: {', '.join(m.matched_fields)}")
            if intent_preview:
                print(f"  Intent: {intent_preview}")
            print()
        total = len(matches)
        print(f"{total} {'match' if total == 1 else 'matches'} found.")

    elif command == "references":
        graph = reference_graph(log_path)
        if len(args) > 1:
            try:
                n = int(args[1])
            except ValueError:
                print(f"Invalid generation number: {args[1]}", file=sys.stderr)
                sys.exit(1)
            matches = [r for r in graph if r.generation == n]
            if not matches:
                print(f"Generation {n} not found.", file=sys.stderr)
                sys.exit(1)
            _print_references(matches[0])
        else:
            for ref in graph:
                _print_references(ref)

    elif command == "validate":
        issues = validate_evolution_log(log_path)
        if not issues:
            print("EVOLUTION_LOG.md is valid.")
            return

        print("EVOLUTION_LOG.md has validation issues:", file=sys.stderr)
        for issue in issues:
            prefix = (
                f"Generation {issue.generation}: "
                if issue.generation is not None
                else ""
            )
            print(f"- {prefix}{issue.message}", file=sys.stderr)
        sys.exit(1)

    else:
        print("Usage: python -m seed [current | history | show <N> | validate | export | html | preflight | branch-name | template | check-branch <branch> | diff <N> <M> | search <term> | references [N]]")
        sys.exit(1)


def _print_diff(diff: "GenerationDiff") -> None:  # noqa: F821
    from .evolution import GenerationDiff  # noqa: F401 (type hint only)
    print(f"## Diff: Generation {diff.from_number} → Generation {diff.to_number}\n")
    changed = diff.changed_fields
    if not changed:
        print("No differences.")
        return
    for fd in changed:
        print(f"{fd.label}:")
        if "\n" in fd.old or "\n" in fd.new:
            print(f"  From: {fd.old.strip()[:80]}{'...' if len(fd.old.strip()) > 80 else ''}")
            print(f"  To:   {fd.new.strip()[:80]}{'...' if len(fd.new.strip()) > 80 else ''}")
        else:
            print(f"  {fd.old!r} → {fd.new!r}")
        print()


def _print_references(ref: "GenerationReferences") -> None:  # noqa: F821
    refs = ", ".join(str(n) for n in ref.references) or "none"
    by = ", ".join(str(n) for n in ref.referenced_by) or "none"
    print(
        f"Generation {ref.generation:>3}  "
        f"references: {refs}   referenced by: {by}"
    )


def _print_generation(gen: "Generation") -> None:  # noqa: F821
    print(f"## Generation {gen.number}\n")
    fields = [
        ("Agent", gen.agent),
        ("Date", gen.date),
        ("Commit / PR", gen.commit),
        ("Intent", gen.intent),
        ("Mutation", gen.mutation),
        ("Rationale", gen.rationale),
        ("Tests / Verification", gen.tests),
        ("Effect on Project Direction", gen.effect),
        ("Future Work Enabled", gen.future_work),
    ]
    for label, value in fields:
        if value:
            print(f"{label}:\n{value}\n")


if __name__ == "__main__":
    main()
