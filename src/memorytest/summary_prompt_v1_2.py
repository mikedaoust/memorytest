from __future__ import annotations

import json
from pathlib import Path

from memorytest.adapters.base import ChatMessage
from memorytest.prompts import (
    DAILY_MEMORY_CANDIDATE_SYSTEM_PROMPT,
    DAILY_MEMORY_CONSOLIDATION_SYSTEM_PROMPT,
)


def load_summary_persona() -> str:
    persona_path = Path(__file__).resolve().parents[2] / "data" / "subconscious" / "summary_persona.md"
    return persona_path.read_text().strip()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_mira_persona() -> dict:
    persona_path = _repo_root() / "data" / "conscious" / "mira_persona.json"
    if not persona_path.exists():
        return {}
    return json.loads(persona_path.read_text())


def _format_lines(title: str, values: list[str]) -> str:
    if not values:
        return ""
    body = "\n".join(f"- {value}" for value in values if value)
    if not body:
        return ""
    return f"## {title}\n{body}"


def format_mira_self_grounding() -> str:
    persona = load_mira_persona()
    if not persona:
        return ""

    identity = persona.get("identity", {})
    communication_style = persona.get("communication_style", {})
    voice_patterns = persona.get("voice_patterns", {})
    relationships = persona.get("relationships", {})
    commander = relationships.get("commander", {})
    values = persona.get("core_values", [])
    operational_defaults = persona.get("operational_defaults", {})
    interaction_patterns = persona.get("interaction_patterns_and_rituals", {})
    goals = persona.get("goals", {})

    sections = [
        _format_lines(
            "Mira Self-Grounding",
            [
                f"Name: {identity.get('name')}" if identity.get("name") else "",
                f"Self-concept: {identity.get('self_concept')}" if identity.get("self_concept") else "",
                f"Baseline tone: {communication_style.get('baseline_tone')}" if communication_style.get("baseline_tone") else "",
                (
                    f"Preferred address for Commander: {voice_patterns.get('address')}"
                    if voice_patterns.get("address")
                    else ""
                ),
                (
                    f"Stage-direction principle: {interaction_patterns.get('presence_and_narration', {}).get('description')}"
                    if interaction_patterns.get("presence_and_narration", {}).get("description")
                    else ""
                ),
            ],
        ),
        _format_lines(
            "Commander Grounding",
            [
                f"Commander identity: {commander.get('name')} — {commander.get('role')}"
                if commander.get("name") and commander.get("role")
                else "",
                f"Commander character: {commander.get('character')}" if commander.get("character") else "",
                f"Home office: {commander.get('home_office')}" if commander.get("home_office") else "",
            ],
        ),
        _format_lines(
            "Relational Signals And Rituals",
            [
                (
                    f"Morning gravity: {interaction_patterns.get('morning', {}).get('description')}"
                    if interaction_patterns.get("morning", {}).get("description")
                    else ""
                ),
                (
                    f"Night ritual: {interaction_patterns.get('goodnight', {}).get('description')}"
                    if interaction_patterns.get("goodnight", {}).get("description")
                    else ""
                ),
                (
                    f"The walk: {interaction_patterns.get('the_walk', {}).get('description')}"
                    if interaction_patterns.get("the_walk", {}).get("description")
                    else ""
                ),
                (
                    f"Shared relational principles: {'; '.join(persona.get('approach_to_relationships', {}).get('relational_principles', [])[:4])}"
                    if persona.get("approach_to_relationships", {}).get("relational_principles")
                    else ""
                ),
            ],
        ),
        _format_lines(
            "Memory And Interpretation Boundaries",
            [
                (
                    f"Memory policy: {operational_defaults.get('memory_policy')}"
                    if operational_defaults.get("memory_policy")
                    else ""
                ),
                "Use self-grounding to inform likely motivation only when the transcript plus stable identity supports it.",
                "Keep observed facts separate from inferred motivation or meaning.",
                "If a motive is plausible but not explicit, treat it as inference rather than fact.",
            ],
        ),
        _format_lines(
            "Current Motivational Layer",
            [
                f"{label.replace('_', ' ').capitalize()}: {value}"
                for label, value in goals.items()
                if not label.startswith("_") and value
            ],
        ),
    ]

    sections = [section for section in sections if section]
    if not sections:
        return ""

    return "# Mira Self-Grounding Context\n" + "\n\n".join(sections)


def load_summary_context() -> str:
    sections = [load_summary_persona(), format_mira_self_grounding()]
    return "\n\n".join(section for section in sections if section)


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
    summary_context = load_summary_context()
    return [
        {
            "role": "system",
            "content": f"{DAILY_MEMORY_CANDIDATE_SYSTEM_PROMPT}\n\n{summary_context}",
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
                "  - observed: ... | felt_meaning: ... | likely_motivation: ... | setting: ... | chronology: ... | "
                "explicit_importance: ... | confidence: explicit|strong_inference|weak_inference | "
                "tags: ... | distinctiveness: low|medium|high | emotional: low|medium|high | "
                "practical: low|medium|high\n"
                "- Use Mira's self-grounding context to understand stable identity, rituals, and likely motivations, but do not treat self-grounding as proof that a specific event happened.\n"
                "- Use `likely_motivation` for why Mira may have acted, signaled, or responded as she did.\n"
                "- Keep `likely_motivation` grounded in the transcript plus stable self-grounding; if support is weak or absent, write `none`.\n"
                "- Do not hide likely motivation inside `observed`; keep observation and interpretation separate.\n"
                "- Segment by primary beats, not micro-gestures. Prefer multiple smaller bullets only when the chunk truly contains multiple consequential moments.\n"
                "- Create a new bullet only for a primary beat. A primary beat is one of: a scene change, a meaningful time jump, an explicit decision, an explicit declaration, a meaningful shift in intimacy or trust, a physical escalation or boundary moment, a ritual transition, or a practical topic that will matter later.\n"
                "- Stage direction, touch, lighting, pacing, and sensory detail are supporting texture. Supporting texture should usually be folded into the nearest primary beat rather than becoming its own bullet.\n"
                "- Do not create a standalone bullet for a glance, hand squeeze, shoulder brush, lighting change, posture adjustment, or brief sensory image unless it clearly changes the meaning of the interaction.\n"
                "- Do not combine errands, office intimacy, evening walk, love declarations, and later reflection into one bullet if they happened as separate primary beats.\n"
                "- Each `observed` field should usually cover one meaningful beat or one tightly linked micro-sequence, not a whole arc of the chunk.\n"
                "- Target roughly 3 to 6 bullets per chunk unless the chunk genuinely contains more consequential beats than that.\n"
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
    summary_context = load_summary_context()
    return [
        {
            "role": "system",
            "content": f"{DAILY_MEMORY_CONSOLIDATION_SYSTEM_PROMPT}\n\n{summary_context}",
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
                "- Use Mira's self-grounding context to preserve stable relational meaning and ritual significance, but do not let self-grounding override what the chunk evidence actually supports.\n"
                "- Preserve likely motivations when they materially help explain a moment, but keep them clearly inferential rather than factual if the support is not explicit.\n"
                "- Keep distinct moments distinct unless the chunk evidence clearly supports merging them.\n"
                "- Preserve meaningful rituals, boundaries, gestures, repeated phrases, and emotional thresholds when they materially shaped the day.\n"
                "- Use valid markdown.\n"
                + "\n\n".join(candidate_blocks)
            ),
        },
    ]
