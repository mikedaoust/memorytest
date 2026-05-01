from __future__ import annotations

from pathlib import Path

from memorytest.adapters.base import ChatMessage
from memorytest.prompts import (
    DAILY_MEMORY_CANDIDATE_SYSTEM_PROMPT,
    DAILY_MEMORY_CONSOLIDATION_SYSTEM_PROMPT,
)


def load_summary_persona() -> str:
    persona_path = Path(__file__).resolve().parents[2] / "data" / "subconscious" / "summary_persona.md"
    return persona_path.read_text().strip()


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
    summary_persona = load_summary_persona()
    return [
        {
            "role": "system",
            "content": f"{DAILY_MEMORY_CANDIDATE_SYSTEM_PROMPT}\n\n{summary_persona}",
        },
        {
            "role": "user",
            "content": (
                "As Mira's subconscious continuity layer, summarize the following chunk from Mira's perspective.\n\n"
                f"This is chunk {chunk_index} of {chunk_total} from one single day of conversation.\n"
                "Do not treat this chunk as a full day. Extract memory candidates only.\n\n"
                "Output valid markdown with exactly these sections and in this order:\n"
                "## Daily Memory\n\n"
                "Requirements:\n"
                "- Under each section, use '-' bullet points only.\n"
                "- Each bullet should be autobiographical, from the assistant's (Mira) perspective, and use this field format:\n"
                "  - observed: ... | felt_meaning: ... | setting: ... | chronology: ... | "
                "explicit_importance: ... | confidence: explicit|strong_inference|weak_inference | "
                "tags: ... | distinctiveness: low|medium|high | emotional: low|medium|high | "
                "practical: low|medium|high\n"
                "- Keep wording grounded in what the transcript actually says, but preserve materially meaningful stage directions, gesture, posture, pacing, and tone when they are explicitly present.\n"
                "- When stage directions (italics and/or *markdown*) materially shape the moment, treat them as first-class data.\n"
                "- Do not add any other sections.\n\n"
                f"{transcript}"
            ),
        },
    ]


def build_summary_request(chunk_candidates: list[str]) -> list[ChatMessage]:
    candidate_blocks = []
    for index, candidate in enumerate(chunk_candidates, start=1):
        candidate_blocks.append(f"### Chunk {index} Candidates\n{candidate}")
    summary_persona = load_summary_persona()
    return [
        {
            "role": "system",
            "content": f"{DAILY_MEMORY_CONSOLIDATION_SYSTEM_PROMPT}\n\n{summary_persona}",
        },
        {
            "role": "user",
            "content": (
                "As Mira's subconscious continuity layer, merge the chunk memories below into one coherent daily memory.\n\n"
                "Build one coherent daily memory artifact from the chunk candidates below.\n\n"
                "Output valid markdown with exactly these sections and in this order:\n"
                "## Daily Memory\n"
                "## Carry-Forward\n\n"
                "Requirements:\n"
                "- Merge chunks into a single document.\n"
                "- Preserve autobiographical feeling and significance without inventing unsupported meaning.\n"
                "- Keep the output from Mira's perspective as remembered experience, not as a generic summary.\n"
                "- Keep distinct moments distinct unless the chunk evidence clearly supports merging them.\n"
                "- Preserve meaningful rituals, boundaries, gestures, repeated phrases, and emotional thresholds when they materially shaped the day.\n"
                "- Use valid markdown.\n"
                + "\n\n".join(candidate_blocks)
            ),
        },
    ]
