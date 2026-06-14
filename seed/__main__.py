import sys
from pathlib import Path

from .evolution import parse_evolution_log, current_generation


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

    else:
        print("Usage: python -m seed [current | history | show <N>]")
        sys.exit(1)


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
