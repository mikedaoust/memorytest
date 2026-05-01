from __future__ import annotations

import unittest

from memorytest.benchmark import extract_ollama_metrics


class BenchmarkTests(unittest.TestCase):
    def test_extract_ollama_metrics(self) -> None:
        metrics = extract_ollama_metrics(
            {
                "eval_count": 50,
                "eval_duration": 2_000_000_000,
                "prompt_eval_count": 20,
                "prompt_eval_duration": 500_000_000,
                "load_duration": 100_000_000,
            }
        )
        self.assertIsNotNone(metrics)
        assert metrics is not None
        self.assertEqual(metrics["eval_count"], 50)
        self.assertEqual(metrics["tokens_per_second"], 25.0)
        self.assertEqual(metrics["load_duration_seconds"], 0.1)

    def test_extract_ollama_metrics_returns_none_without_required_fields(self) -> None:
        self.assertIsNone(extract_ollama_metrics({"foo": "bar"}))


if __name__ == "__main__":
    unittest.main()
