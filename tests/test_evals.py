from __future__ import annotations

import unittest

from memorytest.evals import evaluate_response, sentence_count


class EvalTests(unittest.TestCase):
    def test_sentence_count(self) -> None:
        self.assertEqual(sentence_count("One. Two!"), 2)

    def test_evaluate_response_scores_checks(self) -> None:
        score, results = evaluate_response(
            "- SQLite is the storage choice.\n- Next task is the eval suite.",
            [
                {"type": "contains_all", "values": ["sqlite", "eval suite"]},
                {"type": "line_prefix_count", "prefix": "-", "min": 2},
            ],
        )
        self.assertEqual(score, 1.0)
        self.assertTrue(all(result.passed for result in results))

    def test_exact_match_is_normalized(self) -> None:
        score, _ = evaluate_response(
            "Green Tea.",
            [{"type": "exact_match", "value": "green tea"}],
        )
        self.assertEqual(score, 1.0)

    def test_line_starts_with_all(self) -> None:
        score, results = evaluate_response(
            "1. benchmark models\n2. harden evals\n3. add summaries",
            [{"type": "line_starts_with_all", "values": ["1.", "2.", "3."]}],
        )
        self.assertEqual(score, 1.0)
        self.assertTrue(results[0].passed)


if __name__ == "__main__":
    unittest.main()
