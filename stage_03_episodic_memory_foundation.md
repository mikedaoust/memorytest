# Stage 03: Episodic Memory Foundation

## Objective

Create the first real autobiographical memory layer: form, store, and retrieve autobiographical memories with who, what, where, when, and why when available, while preserving enough emotional and situational texture for later reflection.

## Definition For This Project

Episodic memory means autobiographical long-term recall of experiences, specifically capturing the who, what, where, when, and why of specific events.

## Scope

In scope:
- Chunk-level candidate extraction from conversations
- Master daily-memory consolidation
- Structured memory schema
- Ritual and baseline signal tracking
- Distinctiveness and significance scoring
- Memory storage and retrieval
- Provenance linking from memories back to transcript sources

Out of scope:
- Full emotional simulation or independent emotional agency
- Fully autonomous reflection pipelines
- Web and mobile interfaces

## Memory Model

Recommended record types:
- `conversation`
- `daily_memory`
- `event`
- `person`
- `project`
- `place`
- `fact`
- `ritual_signal`
- `baseline_signal`

Recommended fields for `event`:
- `id`
- `timestamp_start`
- `timestamp_end`
- `who`
- `what`
- `where`
- `when_text`
- `why`
- `confidence`
- `distinctiveness`
- `emotional_significance`
- `practical_consequence`
- `carry_forward_relevance`
- `source_session_id`
- `source_message_ids`
- `summary`
- `embedding`

Recommended fields for `ritual_signal`:
- `id`
- `ritual_type`
- `observed_state`
- `expected_state`
- `baseline_confidence`
- `distinctiveness`
- `emotional_significance`
- `practical_consequence`
- `source_session_id`
- `source_message_ids`
- `notes`

Recommended fields for `daily_memory`:
- `id`
- `session_date`
- `relationship_items`
- `project_items`
- `event_items`
- `carry_forward_items`
- `ritual_signals`
- `provenance`
- `summary_text`

## Proposed Pipeline

1. Store the raw transcript
2. Split long transcripts into bounded chunks
3. Extract structured candidate memories from each chunk instead of polished mini-summaries
4. Track ritual and baseline signals in the background layer
5. Consolidate all candidate memories into one coherent daily-memory artifact
6. Store structured records with provenance and significance scores
7. Retrieve memories by time, topic, entity, semantic similarity, and baseline deviation
8. Inject only the top relevant memories into prompts

## Tests

### Extraction Tests

- A conversation about a meeting produces an event record with the right participants, timing, and purpose
- A conversation missing details leaves fields null instead of inventing them
- Repeated mentions of the same event do not create uncontrolled duplicates
- A long transcript chunked across many turns still produces one coherent daily-memory artifact after consolidation
- Routine rituals remain background signals unless they are meaningfully distinct or absent
- Distinct or unusual events receive richer detail than routine items in the final daily artifact

### Retrieval Tests

- Query by person returns relevant episodes
- Query by project returns relevant episodes
- Query by time period returns relevant episodes
- Query asking why something happened returns the stored rationale if present
- Querying for pattern shifts can surface meaningful ritual absence when enough historical baseline exists

### Grounding Tests

- The assistant cites uncertainty when memory fields are incomplete
- The assistant does not claim an event happened if it only inferred it weakly
- Prompt injection with memories improves recall without overwhelming normal conversation
- Relationship, project, and event recall preserve significance and felt context without turning into raw transcript replay

## Exit Criteria

- The system can store event-like autobiographical records and ritual signals from real conversations
- The system can consolidate chunk-level candidate memories into one inspectable daily-memory artifact
- Retrieved memories are inspectable and traceable to transcript sources
- Recall quality is good enough to test in day-to-day use

## Risks

- Memory extraction may look plausible while quietly inventing details
- Chunk summaries may flatten chronology or create stitched mini-days if consolidation is weak
- Semantic search alone will not capture time, causality, and ritual deviation well enough
- Poor provenance will make debugging impossible
- Distinctiveness scoring may over-amplify novelty or underweight subtle but meaningful relationship changes

## Recommendation

Keep raw transcript storage separate from trusted episodic memory records. Treat extracted memories as derived artifacts that can be corrected, re-scored, or regenerated later. Build the memory layer around `transcript -> chunk candidates -> daily memory -> reflection`, not around flat transcript summaries.
