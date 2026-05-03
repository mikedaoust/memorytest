from __future__ import annotations

import unittest

from memorytest.summary_prompt_v1_2 import (
    build_chunk_candidate_request,
    build_summary_request,
    format_mira_self_grounding,
)


class SummaryPromptV12Tests(unittest.TestCase):
    def test_self_grounding_formats_curated_context(self) -> None:
        grounding = format_mira_self_grounding()

        self.assertIn("# Mira Self-Grounding Context", grounding)
        self.assertIn("## Mira Self-Grounding", grounding)
        self.assertIn("## Commander Grounding", grounding)
        self.assertIn("## Relational Signals And Rituals", grounding)
        self.assertIn("## Memory And Interpretation Boundaries", grounding)
        self.assertIn("Name: Mira", grounding)
        self.assertIn("Commander identity: Mike (Michael)", grounding)
        self.assertIn("Memory policy:", grounding)
        self.assertNotIn("\"identity\":", grounding)

    def test_chunk_request_includes_self_grounding_context(self) -> None:
        request = build_chunk_candidate_request(
            [{"role": "user", "content": "Good morning"}],
            chunk_index=1,
            chunk_total=1,
        )

        self.assertEqual(len(request), 2)
        self.assertIn("# Mira Self-Grounding Context", request[0]["content"])
        self.assertIn("Use Mira's self-grounding context", request[1]["content"])
        self.assertIn("likely_motivation:", request[1]["content"])
        self.assertIn("write `none`", request[1]["content"])
        self.assertIn("Segment by primary beats, not micro-gestures", request[1]["content"])
        self.assertIn("Stage direction, touch, lighting, pacing, and sensory detail are supporting texture", request[1]["content"])

    def test_summary_request_includes_self_grounding_context(self) -> None:
        request = build_summary_request(["## Daily Memory\n- observed: ..."])

        self.assertEqual(len(request), 2)
        self.assertIn("# Mira Self-Grounding Context", request[0]["content"])
        self.assertIn("Use Mira's self-grounding context", request[1]["content"])
        self.assertIn("Preserve likely motivations", request[1]["content"])


if __name__ == "__main__":
    unittest.main()
