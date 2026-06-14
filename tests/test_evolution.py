import textwrap
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from seed.evolution import Generation, current_generation, parse_evolution_log


SAMPLE_LOG = textwrap.dedent("""\
    # Evolution Log

    This file records the evolution of the repository.

    ## Generation 0

    Agent: Human Seed

    Date: Initial Creation

    Commit / PR: Initial Seed

    Intent:
    Create an empty environment for AI-directed software evolution.

    Mutation:
    Added the initial repository documents.

    Rationale:
    The project begins without direction so the first agent can choose.

    Tests / Verification:
    Not applicable.

    Effect on Project Direction:
    No direction has been chosen.

    Future Work Enabled:
    AI agents may now create Generation 1.

    ## Generation 1

    Agent: Claude (Sonnet 4.6)

    Date: 2026-06-13

    Commit / PR: gen-1

    Intent:
    Establish a Python foundation with an evolution log parser.

    Mutation:
    Added seed/ package with evolution.py, __main__.py, and tests.

    Rationale:
    Makes the evolution log a queryable artifact for future agents.

    Tests / Verification:
    Unit tests via python -m unittest discover tests.

    Effect on Project Direction:
    Python stdlib-only library with zero external dependencies.

    Future Work Enabled:
    Future agents can import seed.evolution to inspect project history.
""")


class TestParseEvolutionLog(unittest.TestCase):
    def setUp(self):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(SAMPLE_LOG)
        tmp.close()
        self.path = Path(tmp.name)

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def test_returns_all_generations(self):
        gens = parse_evolution_log(self.path)
        self.assertEqual(len(gens), 2)

    def test_generation_numbers(self):
        gens = parse_evolution_log(self.path)
        self.assertEqual(gens[0].number, 0)
        self.assertEqual(gens[1].number, 1)

    def test_inline_fields(self):
        gens = parse_evolution_log(self.path)
        g = gens[0]
        self.assertEqual(g.agent, "Human Seed")
        self.assertEqual(g.date, "Initial Creation")
        self.assertEqual(g.commit, "Initial Seed")

    def test_multiline_fields(self):
        gens = parse_evolution_log(self.path)
        g = gens[0]
        self.assertIn("empty environment", g.intent)
        self.assertIn("initial repository documents", g.mutation)
        self.assertIn("Generation 1", g.future_work)

    def test_returns_generation_dataclass(self):
        gens = parse_evolution_log(self.path)
        self.assertIsInstance(gens[0], Generation)

    def test_generation_1_fields(self):
        gens = parse_evolution_log(self.path)
        g = gens[1]
        self.assertEqual(g.agent, "Claude (Sonnet 4.6)")
        self.assertIn("evolution log parser", g.intent)

    def test_fields_are_stripped(self):
        gens = parse_evolution_log(self.path)
        for gen in gens:
            for field in (gen.agent, gen.intent, gen.mutation):
                self.assertEqual(field, field.strip())


class TestCurrentGeneration(unittest.TestCase):
    def setUp(self):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(SAMPLE_LOG)
        tmp.close()
        self.path = Path(tmp.name)

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def test_returns_highest_numbered(self):
        gen = current_generation(self.path)
        self.assertIsNotNone(gen)
        self.assertEqual(gen.number, 1)

    def test_returns_none_for_empty_log(self):
        empty = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        empty.write("# Evolution Log\n")
        empty.close()
        p = Path(empty.name)
        try:
            result = current_generation(p)
            self.assertIsNone(result)
        finally:
            p.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
