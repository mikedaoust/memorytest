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
                "- Include only candidates that might matter in the final daily memory.\n"
                "- Each bullet must stay compact and use this field format:\n"
                "  - observed: ... | felt_meaning: ... | setting: ... | chronology: ... | "
                "explicit_importance: ... | confidence: explicit|strong_inference|weak_inference | "
                "tags: ... | distinctiveness: low|medium|high | emotional: low|medium|high | "
                "practical: low|medium|high\n"
                "- Keep wording grounded in what the transcript actually says.\n"
                "- Do not add romantic, psychological, or symbolic color unless it is present in the source.\n"
                "- `felt_meaning` should preserve autobiographical context: how the moment seemed to feel or why it mattered, but only as strongly as the transcript supports.\n"
                "- Relationship candidates should capture significant interactions, shifts, reassurance, tension, growth, or closeness.\n"
                "- Project candidates should capture active work, personal, family, medical, or continuity threads that advanced or mattered.\n"
                "- Event candidates should capture meaningful moments or transitions and any who/what/where/when/why details that are available.\n"
                "- Carry-forward candidates should capture open loops, next expected events, unresolved questions, or what should still matter tomorrow.\n"
                "- Ritual signals should capture recurring rituals or expected patterns, including whether they were present, absent, delayed, or notably different.\n"
                "- Drop repetitive flirtation or repeated wording unless it reveals something meaningful.\n"
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
                "## Morning\n"
                "## Workday\n"
                "## Afternoon And Evening\n"
                "## Carry-Forward\n\n"
                "Requirements:\n"
                "- Under each section, use '-' bullet points only.\n"
                "- Build one day, not chunk-by-chunk mini-days.\n"
                "- Deduplicate repeated items across chunks.\n"
                "- Each bullet should represent one distinct moment, thread, or decision rather than a merged abstract arc unless the transcript clearly supports the merge.\n"
                "- Keep the full artifact chronological from start to end of day.\n"
                "- Start each bullet with tags in square brackets, for example '[relationship, ritual]' or '[project, medical]'.\n"
                "- After the tags, use this format exactly: 'Observed: ... Felt/Meaning: ... Confidence: explicit|strong_inference|weak_inference'.\n"
                "- `Observed` should state what concretely happened.\n"
                "- `Felt/Meaning` should preserve autobiographical context: how the moment seemed to feel or why it mattered, grounded in the transcript.\n"
                "- `Confidence` must indicate whether the felt meaning is explicit in the source or an inference.\n"
                "- Use grounded prose. Do not add romantic, symbolic, or psychological interpretation that is not clearly supported by the transcript.\n"
                "- Prefer observed details, direct statements, and cautious wording over embellished narration.\n"
                "- Carry-Forward should capture what remains open, next expected events, unresolved concerns, and what should still matter tomorrow.\n"
                "- Treat routine rituals as background unless they were distinct, missing, delayed, emotionally different, or important for carry-forward.\n"
                "- Give more detail to high-distinctiveness items and compress routine background items.\n"
                "- Respect both emotional significance and practical consequence.\n"
                "- If a section has no meaningful items, include one bullet that says '- none'.\n"
                "- Do not add any other sections.\n\n"
                + "\n\n".join(candidate_blocks)
            ),
        },
    ]
