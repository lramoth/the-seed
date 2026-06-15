import sys
from pathlib import Path

from .evolution import (
    current_generation,
    diff_generations,
    export_evolution_log,
    parse_evolution_log,
    preflight_evolution_log,
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
        print("Usage: python -m seed [current | history | show <N> | validate | export | preflight | diff <N> <M>]")
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
