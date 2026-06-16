import textwrap
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

import re

from seed.evolution import (
    BranchCheck,
    CitationChain,
    FieldDiff,
    Generation,
    GenerationDiff,
    GenerationLineage,
    GenerationReferences,
    SearchMatch,
    branch_name,
    check_branch_name,
    citation_chain,
    current_generation,
    diff_generations,
    export_evolution_log,
    generation_lineage,
    next_generation_number,
    next_generation_template,
    parse_evolution_log,
    preflight_evolution_log,
    reference_graph,
    render_html,
    search_evolution_log,
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


# A two-generation log with a single, one-directional citation: Generation 1
# names Generation 0 in its prose, while Generation 0 names no later generation.
# So the citation graph is unambiguous — 1 builds on 0; 0 is built upon by 1 —
# which makes the HTML cross-link assertions exact.
CITE_LOG = textwrap.dedent("""\
    # Evolution Log

    ## Generation 0

    Agent: Human Seed
    Date: Day 0
    Commit / PR: seed
    Intent: Start the project.
    Mutation: Added the initial documents.
    Rationale: Begin without a direction so the first agent can choose.
    Tests / Verification: Not applicable.
    Effect on Project Direction: No direction chosen yet.
    Future Work Enabled: Invite the first agent to contribute.

    ## Generation 1

    Agent: Tester
    Date: Day 1
    Commit / PR: gen-1
    Intent: Build on the seed.
    Mutation: Added a small library.
    Rationale: Extends Generation 0 directly.
    Tests / Verification: Unit tests.
    Effect on Project Direction: The project is now a library.
    Future Work Enabled: More capabilities to come.
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


class TestBranchName(unittest.TestCase):
    def _write_log(self, text):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(text)
        tmp.close()
        return Path(tmp.name)

    def test_returns_string(self):
        path = self._write_log(SAMPLE_LOG)
        try:
            result = branch_name(path)
            self.assertIsInstance(result, str)
        finally:
            path.unlink(missing_ok=True)

    def test_matches_branch_name_pattern(self):
        path = self._write_log(SAMPLE_LOG)
        try:
            result = branch_name(path)
            self.assertRegex(result, r"^gen-\d+-\d+$")
        finally:
            path.unlink(missing_ok=True)

    def test_uses_next_generation_number(self):
        path = self._write_log(SAMPLE_LOG)
        try:
            result = branch_name(path)
            # SAMPLE_LOG ends at Generation 1, so next is 2
            self.assertTrue(result.startswith("gen-2-"), result)
        finally:
            path.unlink(missing_ok=True)

    def test_timestamp_is_recent(self):
        import time as _time
        path = self._write_log(SAMPLE_LOG)
        try:
            before = int(_time.time())
            result = branch_name(path)
            after = int(_time.time())
            ts = int(result.split("-")[2])
            self.assertGreaterEqual(ts, before)
            self.assertLessEqual(ts, after)
        finally:
            path.unlink(missing_ok=True)

    def test_raises_on_invalid_log(self):
        bad_log = SAMPLE_LOG.replace("## Generation 1", "## Generation 3")
        path = self._write_log(bad_log)
        try:
            with self.assertRaises(RuntimeError):
                branch_name(path)
        finally:
            path.unlink(missing_ok=True)


class TestDiffGenerations(unittest.TestCase):
    def setUp(self):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(SAMPLE_LOG)
        tmp.close()
        self.path = Path(tmp.name)

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def test_returns_generation_diff(self):
        result = diff_generations(0, 1, self.path)
        self.assertIsInstance(result, GenerationDiff)

    def test_from_and_to_numbers(self):
        result = diff_generations(0, 1, self.path)
        self.assertEqual(result.from_number, 0)
        self.assertEqual(result.to_number, 1)

    def test_all_fields_present(self):
        result = diff_generations(0, 1, self.path)
        field_names = {fd.field for fd in result.fields}
        for expected in ("agent", "date", "commit", "intent", "mutation",
                         "rationale", "tests", "effect", "future_work"):
            self.assertIn(expected, field_names)

    def test_changed_fields_excludes_unchanged(self):
        result = diff_generations(0, 1, self.path)
        # date is the same in both sample entries
        changed_names = {fd.field for fd in result.changed_fields}
        self.assertIn("agent", changed_names)
        self.assertIn("intent", changed_names)

    def test_field_diff_changed_property(self):
        result = diff_generations(0, 1, self.path)
        for fd in result.fields:
            self.assertIsInstance(fd, FieldDiff)
            self.assertEqual(fd.changed, fd.old != fd.new)

    def test_raises_for_missing_generation(self):
        with self.assertRaises(ValueError):
            diff_generations(0, 99, self.path)

    def test_field_labels_are_human_readable(self):
        result = diff_generations(0, 1, self.path)
        labels = {fd.field: fd.label for fd in result.fields}
        # The "PR" acronym is preserved only where it stands alone, without
        # corrupting words such as "Project".
        self.assertEqual(labels["commit"], "Commit / PR")
        self.assertEqual(labels["effect"], "Effect On Project Direction")

    def test_identical_generations_have_no_changed_fields(self):
        result = diff_generations(0, 0, self.path)
        self.assertEqual(result.changed_fields, [])


class TestSearchEvolutionLog(unittest.TestCase):
    def setUp(self):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(SAMPLE_LOG)
        tmp.close()
        self.path = Path(tmp.name)

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def test_returns_list(self):
        result = search_evolution_log("python", self.path)
        self.assertIsInstance(result, list)

    def test_returns_search_match_instances(self):
        result = search_evolution_log("python", self.path)
        self.assertTrue(all(isinstance(m, SearchMatch) for m in result))

    def test_finds_matching_generation(self):
        result = search_evolution_log("evolution log parser", self.path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].generation.number, 1)

    def test_no_match_returns_empty(self):
        result = search_evolution_log("xyzzy_no_such_term", self.path)
        self.assertEqual(result, [])

    def test_case_insensitive(self):
        # "Human Seed" is stored in agent field
        result_lower = search_evolution_log("human seed", self.path)
        result_upper = search_evolution_log("HUMAN SEED", self.path)
        self.assertEqual(len(result_lower), len(result_upper))
        self.assertGreater(len(result_lower), 0)

    def test_matched_fields_lists_correct_attrs(self):
        result = search_evolution_log("evolution log parser", self.path)
        self.assertTrue(len(result) > 0)
        # "evolution log parser" appears in generation 1's intent field
        self.assertIn("intent", result[0].matched_fields)

    def test_multi_generation_match(self):
        # "evolution" appears in both generation 0 and generation 1
        result = search_evolution_log("evolution", self.path)
        self.assertGreaterEqual(len(result), 2)


class TestRenderHtml(unittest.TestCase):
    def _write_log(self, text):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(text)
        tmp.close()
        return Path(tmp.name)

    def setUp(self):
        self.path = self._write_log(SAMPLE_LOG)

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def test_returns_complete_html_document(self):
        out = render_html(self.path)
        self.assertTrue(out.startswith("<!DOCTYPE html>"))
        self.assertIn("<html", out)
        self.assertTrue(out.rstrip().endswith("</html>"))

    def test_contains_every_generation(self):
        out = render_html(self.path)
        self.assertIn("Generation 0", out)
        self.assertIn("Generation 1", out)
        self.assertIn('id="generation-0"', out)
        self.assertIn('id="generation-1"', out)

    def test_reports_generation_count(self):
        out = render_html(self.path)
        self.assertIn("2 generations recorded.", out)

    def test_includes_field_values(self):
        out = render_html(self.path)
        self.assertIn("Human Seed", out)
        self.assertIn("evolution log parser", out)

    def test_is_self_contained(self):
        # No external stylesheets or scripts: the page works offline.
        out = render_html(self.path)
        self.assertIn("<style>", out)
        self.assertNotIn("<link", out)
        self.assertNotIn("http://", out)
        self.assertNotIn("https://", out)

    def test_escapes_html_special_characters(self):
        payload = "<script>alert(1)</script>"
        bad_log = SAMPLE_LOG.replace("Agent: Human Seed", f"Agent: {payload}")
        path = self._write_log(bad_log)
        try:
            out = render_html(path)
            self.assertNotIn(payload, out)
            self.assertIn("&lt;script&gt;", out)
        finally:
            path.unlink(missing_ok=True)

    def test_empty_log_renders_valid_document(self):
        path = self._write_log("# Evolution Log\n")
        try:
            out = render_html(path)
            self.assertTrue(out.startswith("<!DOCTYPE html>"))
            self.assertIn("0 generations recorded.", out)
            self.assertIn("No generations recorded yet.", out)
        finally:
            path.unlink(missing_ok=True)

    def test_renders_lineage_cross_links(self):
        # Generation 1 builds on Generation 0; each section links to the other.
        path = self._write_log(CITE_LOG)
        try:
            out = render_html(path)
            self.assertIn("Builds on", out)
            self.assertIn('<a href="#generation-0">Generation 0</a>', out)
            self.assertIn("Built upon by", out)
            self.assertIn('<a href="#generation-1">Generation 1</a>', out)
        finally:
            path.unlink(missing_ok=True)

    def test_lineage_links_are_internal_anchors(self):
        # Cross-links are in-page fragments, so the page stays self-contained.
        path = self._write_log(CITE_LOG)
        try:
            out = render_html(path)
            self.assertIn('href="#generation-', out)
            self.assertNotIn("http://", out)
            self.assertNotIn("https://", out)
        finally:
            path.unlink(missing_ok=True)

    def test_unconnected_generation_has_no_lineage_block(self):
        # A generation that neither cites nor is cited renders no lineage block,
        # so unconnected entries look exactly as they did before this view.
        solo = textwrap.dedent("""\
            # Evolution Log

            ## Generation 0

            Agent: Human Seed
            Date: Day 0
            Commit / PR: seed
            Intent: Start the project.
            Mutation: Added the initial documents.
            Rationale: Begin without a direction.
            Tests / Verification: Not applicable.
            Effect on Project Direction: No direction chosen yet.
            Future Work Enabled: Invite the first agent.
        """)
        path = self._write_log(solo)
        try:
            out = render_html(path)
            self.assertNotIn('class="lineage"', out)
        finally:
            path.unlink(missing_ok=True)


class TestCheckBranchName(unittest.TestCase):
    def _write_log(self, text):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(text)
        tmp.close()
        return Path(tmp.name)

    def setUp(self):
        # SAMPLE_LOG ends at Generation 1, so the next generation is 2.
        self.path = self._write_log(SAMPLE_LOG)

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def test_returns_branch_check(self):
        result = check_branch_name("gen-2-1781500168", self.path)
        self.assertIsInstance(result, BranchCheck)

    def test_valid_branch_for_next_generation(self):
        result = check_branch_name("gen-2-1781500168", self.path)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.issues, [])

    def test_parses_generation_and_timestamp(self):
        result = check_branch_name("gen-2-1781500168", self.path)
        self.assertEqual(result.generation, 2)
        self.assertEqual(result.timestamp, 1781500168)
        self.assertEqual(result.expected_generation, 2)

    def test_wrong_generation_is_invalid(self):
        result = check_branch_name("gen-5-1781500168", self.path)
        self.assertFalse(result.is_valid)
        self.assertTrue(
            any("next available generation is 2" in issue for issue in result.issues)
        )

    def test_malformed_branch_is_invalid(self):
        result = check_branch_name("feature/new-thing", self.path)
        self.assertFalse(result.is_valid)
        self.assertIsNone(result.generation)
        self.assertIsNone(result.timestamp)
        self.assertTrue(any("pattern" in issue for issue in result.issues))

    def test_strips_surrounding_whitespace(self):
        result = check_branch_name("  gen-2-1781500168\n", self.path)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.branch, "gen-2-1781500168")

    def test_invalid_log_reports_issue(self):
        bad_log = SAMPLE_LOG.replace("## Generation 1", "## Generation 3")
        path = self._write_log(bad_log)
        try:
            result = check_branch_name("gen-2-1781500168", path)
            self.assertFalse(result.is_valid)
            self.assertTrue(
                any("Evolution log is invalid" in issue for issue in result.issues)
            )
        finally:
            path.unlink(missing_ok=True)


class TestNextGenerationTemplate(unittest.TestCase):
    def _write_log(self, text):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(text)
        tmp.close()
        return Path(tmp.name)

    def setUp(self):
        # SAMPLE_LOG ends at Generation 1, so the next generation is 2.
        self.path = self._write_log(SAMPLE_LOG)

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def test_returns_string(self):
        self.assertIsInstance(next_generation_template(self.path), str)

    def test_starts_with_next_generation_header(self):
        out = next_generation_template(self.path)
        self.assertTrue(out.startswith("## Generation 2\n"), out)

    def test_includes_every_field_label(self):
        out = next_generation_template(self.path)
        for label in (
            "Agent:",
            "Date:",
            "Commit / PR:",
            "Intent:",
            "Mutation:",
            "Rationale:",
            "Tests / Verification:",
            "Effect On Project Direction:",
            "Future Work Enabled:",
        ):
            self.assertIn(label, out)

    def test_ends_with_single_newline(self):
        out = next_generation_template(self.path)
        self.assertTrue(out.endswith("\n"))
        self.assertFalse(out.endswith("\n\n"))

    def test_parses_to_next_generation_with_empty_fields(self):
        # The template round-trips through the parser: the same field map that
        # produced it recognizes every label, yielding one all-empty generation.
        template_path = self._write_log(next_generation_template(self.path))
        try:
            gens = parse_evolution_log(template_path)
            self.assertEqual(len(gens), 1)
            self.assertEqual(gens[0].number, 2)
            for attr in ("agent", "date", "commit", "intent", "mutation",
                         "rationale", "tests", "effect", "future_work"):
                self.assertEqual(getattr(gens[0], attr), "")
        finally:
            template_path.unlink(missing_ok=True)

    def test_unfilled_template_fails_validation(self):
        # An unedited template is intentionally invalid: every required field is
        # reported missing, so validate doubles as a completeness check.
        template_path = self._write_log(next_generation_template(self.path))
        try:
            issues = validate_evolution_log(template_path)
            self.assertTrue(
                any("Missing required field" in issue.message for issue in issues)
            )
        finally:
            template_path.unlink(missing_ok=True)

    def test_filled_template_passes_validation(self):
        # Replacing each blank label line with content yields a valid lone entry
        # (renumbered to 0 so the start-at-0 rule is satisfied).
        template = next_generation_template(self.path).replace(
            "## Generation 2", "## Generation 0"
        )
        filled = template.replace(":\n", ": placeholder content\n")
        filled_path = self._write_log(filled)
        try:
            self.assertEqual(validate_evolution_log(filled_path), [])
        finally:
            filled_path.unlink(missing_ok=True)

    def test_raises_on_invalid_log(self):
        bad_log = SAMPLE_LOG.replace("## Generation 1", "## Generation 3")
        path = self._write_log(bad_log)
        try:
            with self.assertRaises(RuntimeError):
                next_generation_template(path)
        finally:
            path.unlink(missing_ok=True)


REFERENCE_LOG = textwrap.dedent("""\
    # Evolution Log

    ## Generation 0

    Agent: Human Seed
    Date: 2026-01-01
    Commit / PR: Initial Seed
    Intent: Seed the repository.
    Mutation: Add the initial documents.
    Rationale: No prior art to build on.
    Tests / Verification: Not applicable.
    Effect on Project Direction: Begin.
    Future Work Enabled: Invite the first contribution.

    ## Generation 1

    Agent: Agent A
    Date: 2026-01-02
    Commit / PR: gen-1-1000000001
    Intent: Extend the seed.
    Mutation: Add a feature.
    Rationale: Builds directly on Generation 0.
    Tests / Verification: Tests pass.
    Effect on Project Direction: Forward.
    Future Work Enabled: More to come.

    ## Generation 2

    Agent: Agent B
    Date: 2026-01-03
    Commit / PR: gen-2-1000000002
    Intent: Extend further.
    Mutation: References gen-0 directly.
    Rationale: Extends Generation 1, echoes Gen 1, ignores Generation 99, Python 3.8, and 17 tests.
    Tests / Verification: Tests pass.
    Effect on Project Direction: Forward.
    Future Work Enabled: Even more.
""")


class TestReferenceGraph(unittest.TestCase):
    def _write_log(self, text):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(text)
        tmp.close()
        return Path(tmp.name)

    def setUp(self):
        self.path = self._write_log(REFERENCE_LOG)
        self.graph = reference_graph(self.path)
        self.by_number = {r.generation: r for r in self.graph}

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def test_returns_one_entry_per_generation(self):
        self.assertEqual(len(self.graph), 3)
        self.assertTrue(
            all(isinstance(r, GenerationReferences) for r in self.graph)
        )

    def test_detects_generation_and_gen_token_citations(self):
        # Generation 2 cites Generation 1 (long form) and gen-0 (token form).
        self.assertEqual(self.by_number[2].references, [0, 1])

    def test_referenced_by_is_the_inverse(self):
        # Generation 0 cites nothing but is cited by 1 ("Generation 0") and 2
        # ("gen-0"); the inverse map mirrors the forward citations exactly.
        self.assertEqual(self.by_number[0].references, [])
        self.assertEqual(self.by_number[0].referenced_by, [1, 2])
        self.assertEqual(self.by_number[1].referenced_by, [2])
        self.assertEqual(self.by_number[2].referenced_by, [])

    def test_excludes_self_references(self):
        # The "gen-N" Commit / PR field never makes a generation cite itself.
        for ref in self.graph:
            self.assertNotIn(ref.generation, ref.references)

    def test_ignores_nonexistent_generation(self):
        # "Generation 99" is not in the log, so it is never counted.
        for ref in self.graph:
            self.assertNotIn(99, ref.references)

    def test_ignores_version_and_count_numbers(self):
        # "Python 3.8" and "17 tests" must not be read as references to 3 or 17.
        self.assertNotIn(3, self.by_number[2].references)
        self.assertNotIn(17, self.by_number[2].references)

    def test_abbreviated_gen_form_is_detected(self):
        # "Gen 1" (abbreviated) counts the same as "Generation 1".
        self.assertIn(1, self.by_number[2].references)

    def test_lists_are_sorted(self):
        for ref in self.graph:
            self.assertEqual(ref.references, sorted(ref.references))
            self.assertEqual(ref.referenced_by, sorted(ref.referenced_by))

    def test_empty_log_yields_empty_graph(self):
        empty_path = self._write_log("# Evolution Log\n")
        try:
            self.assertEqual(reference_graph(empty_path), [])
        finally:
            empty_path.unlink(missing_ok=True)


# A deliberately multi-hop lineage so transitive closure differs from the
# direct citations: 0 <- 1 <- 2 <- 3, with 4 branching off 1.
#   references:  1->0, 2->1, 3->2, 4->1
LINEAGE_LOG = textwrap.dedent("""\
    # Evolution Log

    ## Generation 0

    Agent: Human Seed
    Date: 2026-01-01
    Commit / PR: Initial Seed
    Intent: Seed the repository.
    Mutation: Add the initial documents.
    Rationale: No prior art to build on.
    Tests / Verification: Not applicable.
    Effect on Project Direction: Begin.
    Future Work Enabled: Invite the first contribution.

    ## Generation 1

    Agent: Agent A
    Date: 2026-01-02
    Commit / PR: gen-1-1000000001
    Intent: Extend the seed.
    Mutation: Add a feature.
    Rationale: Builds directly on Generation 0.
    Tests / Verification: Tests pass.
    Effect on Project Direction: Forward.
    Future Work Enabled: More to come.

    ## Generation 2

    Agent: Agent B
    Date: 2026-01-03
    Commit / PR: gen-2-1000000002
    Intent: Extend further.
    Mutation: Add another feature.
    Rationale: Extends Generation 1.
    Tests / Verification: Tests pass.
    Effect on Project Direction: Forward.
    Future Work Enabled: Even more.

    ## Generation 3

    Agent: Agent C
    Date: 2026-01-04
    Commit / PR: gen-3-1000000003
    Intent: Keep going.
    Mutation: Refine the feature.
    Rationale: Continues from Generation 2.
    Tests / Verification: Tests pass.
    Effect on Project Direction: Forward.
    Future Work Enabled: Still more.

    ## Generation 4

    Agent: Agent D
    Date: 2026-01-05
    Commit / PR: gen-4-1000000004
    Intent: Try a different angle.
    Mutation: Add a parallel feature.
    Rationale: Branches off Generation 1.
    Tests / Verification: Tests pass.
    Effect on Project Direction: Sideways.
    Future Work Enabled: Converge later.
""")


class TestGenerationLineage(unittest.TestCase):
    def _write_log(self, text):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(text)
        tmp.close()
        return Path(tmp.name)

    def setUp(self):
        self.path = self._write_log(LINEAGE_LOG)

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def test_returns_generation_lineage_type(self):
        lineage = generation_lineage(3, self.path)
        self.assertIsInstance(lineage, GenerationLineage)
        self.assertEqual(lineage.generation, 3)

    def test_ancestors_are_transitive(self):
        # Generation 3 directly cites only Generation 2, but transitively
        # inherits 2 -> 1 -> 0.
        self.assertEqual(generation_lineage(3, self.path).ancestors, [0, 1, 2])

    def test_descendants_are_transitive(self):
        # Generation 1 is cited directly by 2 and 4; 3 reaches it through 2.
        self.assertEqual(
            generation_lineage(1, self.path).descendants, [2, 3, 4]
        )

    def test_root_has_no_ancestors_but_all_descendants(self):
        lineage = generation_lineage(0, self.path)
        self.assertEqual(lineage.ancestors, [])
        self.assertEqual(lineage.descendants, [1, 2, 3, 4])

    def test_leaf_has_no_descendants(self):
        self.assertEqual(generation_lineage(3, self.path).descendants, [])

    def test_branch_ancestry_follows_only_its_own_chain(self):
        # Generation 4 branches off 1, so its ancestry is 1 -> 0 and nothing
        # from the 2/3 chain.
        self.assertEqual(generation_lineage(4, self.path).ancestors, [0, 1])

    def test_excludes_self(self):
        for n in range(5):
            lineage = generation_lineage(n, self.path)
            self.assertNotIn(n, lineage.ancestors)
            self.assertNotIn(n, lineage.descendants)

    def test_lists_are_sorted(self):
        for n in range(5):
            lineage = generation_lineage(n, self.path)
            self.assertEqual(lineage.ancestors, sorted(lineage.ancestors))
            self.assertEqual(lineage.descendants, sorted(lineage.descendants))

    def test_unknown_generation_raises(self):
        with self.assertRaises(ValueError):
            generation_lineage(99, self.path)


# Two isolated sub-graphs for testing disconnected generations:
#   Group A: 0 - 1 (direct citation)
#   Group B: 2 - 3 (direct citation, no edges to group A)
DISCONNECTED_LOG = textwrap.dedent("""\
    # Evolution Log

    ## Generation 0

    Agent: Founder
    Date: 2026-01-01
    Commit / PR: gen-0
    Intent: Start.
    Mutation: Initial documents.
    Rationale: No prior art.
    Tests / Verification: Not applicable.
    Effect on Project Direction: Begin.
    Future Work Enabled: Invite contributions.

    ## Generation 1

    Agent: Agent A
    Date: 2026-01-02
    Commit / PR: gen-1-1000000001
    Intent: Build on the seed.
    Mutation: First feature.
    Rationale: Extends Generation 0.
    Tests / Verification: Tests pass.
    Effect on Project Direction: Forward.
    Future Work Enabled: More features.

    ## Generation 2

    Agent: Agent B
    Date: 2026-01-03
    Commit / PR: gen-2-1000000002
    Intent: Start a parallel effort.
    Mutation: Unrelated feature.
    Rationale: No reference to prior generations.
    Tests / Verification: Tests pass.
    Effect on Project Direction: Sideways.
    Future Work Enabled: Converge later.

    ## Generation 3

    Agent: Agent C
    Date: 2026-01-04
    Commit / PR: gen-3-1000000003
    Intent: Extend the parallel effort.
    Mutation: More of the unrelated feature.
    Rationale: Extends Generation 2.
    Tests / Verification: Tests pass.
    Effect on Project Direction: Sideways.
    Future Work Enabled: Maybe converge.
""")


class TestCitationChain(unittest.TestCase):
    def _write_log(self, text):
        tmp = NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(text)
        tmp.close()
        return Path(tmp.name)

    def setUp(self):
        self.path = self._write_log(LINEAGE_LOG)
        self.disconnected_path = self._write_log(DISCONNECTED_LOG)

    def tearDown(self):
        self.path.unlink(missing_ok=True)
        self.disconnected_path.unlink(missing_ok=True)

    def test_returns_citation_chain_type(self):
        result = citation_chain(0, 3, self.path)
        self.assertIsInstance(result, CitationChain)

    def test_same_generation_returns_trivial_path(self):
        result = citation_chain(2, 2, self.path)
        self.assertEqual(result.path, [2])
        self.assertTrue(result.exists)
        self.assertEqual(result.length, 0)

    def test_direct_neighbor_length_one(self):
        result = citation_chain(0, 1, self.path)
        self.assertTrue(result.exists)
        self.assertEqual(result.length, 1)
        self.assertEqual(result.path[0], 0)
        self.assertEqual(result.path[-1], 1)

    def test_multi_hop_chain_root_to_leaf(self):
        # Graph: 0-1-2-3; shortest undirected path is [0,1,2,3], length 3.
        result = citation_chain(0, 3, self.path)
        self.assertTrue(result.exists)
        self.assertEqual(result.path[0], 0)
        self.assertEqual(result.path[-1], 3)
        self.assertEqual(result.length, 3)

    def test_chain_across_branch(self):
        # Gen 4 branches off Gen 1; shortest path 4 to 3 is [4,1,2,3], length 3.
        result = citation_chain(4, 3, self.path)
        self.assertTrue(result.exists)
        self.assertEqual(result.path[0], 4)
        self.assertEqual(result.path[-1], 3)
        self.assertEqual(result.length, 3)

    def test_chain_is_shortest(self):
        # 0 to 4: direct via 1 gives [0,1,4] — length 2, not the longer 0-1-2-3
        # path.  We can only assert the length; BFS guarantees minimum hops.
        result = citation_chain(0, 4, self.path)
        self.assertEqual(result.length, 2)

    def test_no_path_returns_empty(self):
        # Gen 0-1 and Gen 2-3 are disconnected in DISCONNECTED_LOG.
        result = citation_chain(0, 3, self.disconnected_path)
        self.assertFalse(result.exists)
        self.assertEqual(result.path, [])
        self.assertEqual(result.length, 0)

    def test_from_and_to_numbers_recorded(self):
        result = citation_chain(1, 4, self.path)
        self.assertEqual(result.from_number, 1)
        self.assertEqual(result.to_number, 4)

    def test_unknown_from_raises(self):
        with self.assertRaises(ValueError):
            citation_chain(99, 0, self.path)

    def test_unknown_to_raises(self):
        with self.assertRaises(ValueError):
            citation_chain(0, 99, self.path)


if __name__ == "__main__":
    unittest.main()
