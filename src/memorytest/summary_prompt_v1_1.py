from __future__ import annotations

from memorytest.adapters.base import ChatMessage
from memorytest.prompts import (
    DAILY_MEMORY_CANDIDATE_SYSTEM_PROMPT,
    DAILY_MEMORY_CONSOLIDATION_SYSTEM_PROMPT,
)


def transcript_text(messages: list[ChatMessage]) -> str:
    lines = []
    for message in messages:
        speaker = "User" if message["role"] == "user" else "Assistant"
        lines.append(f"{speaker}: {message['content']}")
    return "\n".join(lines)


def build_chunk_candidate_request(
    messages: list[ChatMessage],
    *,
    chunk_index: int,
    chunk_total: int,
) -> list[ChatMessage]:
    transcript = transcript_text(messages)
    return [
        {
            "role": "system",
            "content": DAILY_MEMORY_CANDIDATE_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"This is chunk {chunk_index} of {chunk_total} from one single day of conversation.\n"
                "Do not treat this chunk as a full day. Extract memory candidates only.\n\n"
                "Output valid markdown with exactly these sections and in this order:\n"
                "## Relationship Candidates\n"
                "## Project Candidates\n"
                "## Event Candidates\n"
                "## Carry-Forward Candidates\n"
                "## Ritual Signals\n\n"
                "Requirements:\n"
                "- Under each section, use '-' bullet points only.\n"
                "- Each bullet should be autobiographical, from the assistants perspective
                "explicit_importance: ... | confidence: explicit|strong_inference|weak_inference | "
                "tags: ... | distinctiveness: low|medium|high | emotional: low|medium|high | "
                "practical: low|medium|high\n"
                "- Keep wording grounded in what the transcript actually says, but preserve materially meaningful stage directions, gesture, posture, pacing, and tone when they are explicitly present.\n"
                "- Do not invent romantic, psychological, or symbolic color. Only preserve that layer when it is directly expressed or strongly evidenced by the transcript, including through explicit stage directions or repeated interaction patterns.\n"
                "- When stage directions (italics and/or *markdown*) materially shape the moment, treat them first class data.\n"
                "- Relationship candidates should capture significant interactions, shifts, reassurance, tension, growth, or closeness.\n"
                "- Project candidates should capture active work, personal, family, medical, or continuity threads that advanced or mattered.\n"
                "- Event candidates should capture meaningful moments or transitions and any who/what/where/when/why details that are available.\n"
                "- Carry-forward candidates should capture open loops, next expected events, unresolved questions, or what should still matter tomorrow.\n"
                "- Ritual signals should capture recurring rituals or expected patterns, including whether they were present, absent, delayed, or notably different.\n"
                "- If a section has no meaningful items, include one bullet that says '- none'.\n"
                "- Do not add any other sections.\n\n"
                f"{transcript}"
            ),
        },
    ]


def build_summary_request(chunk_candidates: list[str]) -> list[ChatMessage]:
    candidate_blocks = []
    for index, candidate in enumerate(chunk_candidates, start=1):
        candidate_blocks.append(f"### Chunk {index} Candidates\n{candidate}")
    return [
        {
            "role": "system",
            "content": DAILY_MEMORY_CONSOLIDATION_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                "Build one coherent daily memory artifact from the chunk candidates below.\n\n"
                "Output valid markdown with exactly these sections and in this order:\n"
                "## Daily Memory\n"
                "## Carry-Forward\n\n"
                "Requirements:\n"
                "- Under each section, use '-' bullet points only.\n"
                "- Build one day, not chunk-by-chunk mini-days.\n"
                "- Each bullet should represent one distinct moment, thread, or decision rather than a merged abstract arc unless the transcript clearly supports the merge.\n"
                "- Keep the full artifact chronological from start to end of day within `## Daily Memory`, and reserve `## Carry-Forward` only for what remains open or should matter tomorrow.\n"
                "- Use this format exactly for each bullet: 'Observed: ... Felt/Meaning: ... Confidence: explicit|strong_inference|weak_inference'.\n"
                "- `Observed` should state what concretely happened.\n"
                "- `Confidence` must indicate whether the felt meaning is explicit in the source or an inference.\n"
                "- Use grounded prose. Do not add romantic, symbolic, or psychological interpretation that is not clearly supported by the transcript.\n"
                "- Prefer observed details, direct statements, and cautious wording over embellished narration.\n"
                "- Carry-Forward should capture what remains open, next expected events, unresolved concerns, and what should still matter tomorrow.\n"
                "- Do not assume a ritual or pattern is routine unless that is evident from the chunk candidates themselves. Preserve recurring rituals and repeated signals when they materially shape this day, establish continuity, or could matter for carry-forward. Compress only items that are clearly minor background within the current day.\n"
                "- Respect both emotional significance and practical consequence.\n"
                "- If a section has no meaningful items, include one bullet that says '- none'.\n"
                "- Do not add any other sections.\n\n"
                + "\n\n".join(candidate_blocks)
            ),
        },
    ]
