import textwrap
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from seed.evolution import (
    Generation,
    current_generation,
    export_evolution_log,
    next_generation_number,
    parse_evolution_log,
    preflight_evolution_log,
    validate_evolution_log,
)


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


class TestNextGenerationNumber(unittest.TestCase):
    def setUp(self):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(SAMPLE_LOG)
        tmp.close()
        self.path = Path(tmp.name)

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def test_returns_next_number(self):
        self.assertEqual(next_generation_number(self.path), 2)

    def test_returns_none_for_empty_log(self):
        empty = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        empty.write("# Evolution Log\n")
        empty.close()
        p = Path(empty.name)
        try:
            self.assertIsNone(next_generation_number(p))
        finally:
            p.unlink(missing_ok=True)


class TestPreflightEvolutionLog(unittest.TestCase):
    def _write_log(self, text):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(text)
        tmp.close()
        return Path(tmp.name)

    def test_valid_log_reports_branch_guidance(self):
        path = self._write_log(SAMPLE_LOG)
        try:
            report = preflight_evolution_log(path)
            self.assertTrue(report.is_valid)
            self.assertEqual(report.current_generation, 1)
            self.assertEqual(report.next_generation, 2)
            self.assertEqual(report.branch_prefix, "gen-2-")
            self.assertEqual(report.issues, [])
        finally:
            path.unlink(missing_ok=True)

    def test_invalid_log_reports_issues_without_branch_guidance(self):
        bad_log = SAMPLE_LOG.replace("## Generation 1", "## Generation 3")
        path = self._write_log(bad_log)
        try:
            report = preflight_evolution_log(path)
            self.assertFalse(report.is_valid)
            self.assertEqual(report.current_generation, 3)
            self.assertIsNone(report.next_generation)
            self.assertIsNone(report.branch_prefix)
            self.assertTrue(any("contiguous" in issue.message for issue in report.issues))
        finally:
            path.unlink(missing_ok=True)


class TestValidateEvolutionLog(unittest.TestCase):
    def _write_log(self, text):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(text)
        tmp.close()
        return Path(tmp.name)

    def test_valid_sample_has_no_issues(self):
        path = self._write_log(SAMPLE_LOG)
        try:
            self.assertEqual(validate_evolution_log(path), [])
        finally:
            path.unlink(missing_ok=True)

    def test_reports_empty_log(self):
        path = self._write_log("# Evolution Log\n")
        try:
            issues = validate_evolution_log(path)
            self.assertEqual(len(issues), 1)
            self.assertIn("No generations", issues[0].message)
        finally:
            path.unlink(missing_ok=True)

    def test_reports_missing_required_field(self):
        bad_log = SAMPLE_LOG.replace(
            "Agent: Claude (Sonnet 4.6)",
            "Agent:",
        )
        path = self._write_log(bad_log)
        try:
            issues = validate_evolution_log(path)
            self.assertTrue(
                any(
                    issue.generation == 1
                    and "Missing required field: Agent" in issue.message
                    for issue in issues
                )
            )
        finally:
            path.unlink(missing_ok=True)

    def test_reports_non_contiguous_generations(self):
        bad_log = SAMPLE_LOG.replace("## Generation 1", "## Generation 3")
        path = self._write_log(bad_log)
        try:
            issues = validate_evolution_log(path)
            self.assertTrue(
                any("contiguous" in issue.message for issue in issues)
            )
        finally:
            path.unlink(missing_ok=True)


class TestExportEvolutionLog(unittest.TestCase):
    def setUp(self):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(SAMPLE_LOG)
        tmp.close()
        self.path = Path(tmp.name)

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def test_returns_valid_json(self):
        import json
        result = export_evolution_log(self.path)
        data = json.loads(result)
        self.assertIsInstance(data, list)

    def test_contains_all_generations(self):
        import json
        data = json.loads(export_evolution_log(self.path))
        self.assertEqual(len(data), 2)

    def test_generation_fields_present(self):
        import json
        data = json.loads(export_evolution_log(self.path))
        g = data[0]
        for key in ("number", "agent", "date", "commit", "intent",
                    "mutation", "rationale", "tests", "effect", "future_work"):
            self.assertIn(key, g)

    def test_generation_numbers_correct(self):
        import json
        data = json.loads(export_evolution_log(self.path))
        self.assertEqual(data[0]["number"], 0)
        self.assertEqual(data[1]["number"], 1)


if __name__ == "__main__":
    unittest.main()
