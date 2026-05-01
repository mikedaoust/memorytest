# Roadmap

This roadmap breaks the long-term goal into functional stages with explicit tests and exit criteria.

## Constraints

- Local-first development on a MacBook Pro M4 Max with 128GB RAM
- No cloud models for the current roadmap unless explicitly revisited later
- Terminal-first MVP
- End goal is a self-hosted companion assistant with autobiographical episodic memory
- Current baseline candidate set: `qwen3.5-27b`, `qwen3.5-35b-a3b`, and `qwen3.5-122b-a10b`
- Fast fallback candidate: `qwen3.5-9b`
- Inference backend should remain replaceable across `llama.cpp`, `vllm-mlx`, `mlx-lm`, or similar local runtimes

## Stage 0: Environment And Baseline

Goal: Confirm the local runtime stack and establish a repeatable development baseline.

Deliverables:
- Confirm the first scripted local inference path while keeping the backend replaceable
- Record the baseline chat model, plus fallback candidates for chat, summarization, and embeddings
- Create a simple benchmark script or checklist for latency, RAM usage, and response quality
- Define the repo structure for app code, memory storage, evals, and logs

Tests:
- Selected model runs locally from terminal
- Prompt-response loop works consistently across repeated runs
- Inference latency is acceptable for interactive use
- Basic storage choice can be read and written locally

Exit criteria:
- One initial scripted runtime path is chosen
- A baseline model is selected from the current Qwen candidate set after benchmarking
- One storage strategy is chosen
- Basic performance and quality notes are documented

## Stage 1: Terminal Assistant MVP

Goal: Build a reliable terminal assistant with session-aware conversation but no advanced episodic recall yet.

Deliverables:
- CLI chat loop
- Conversation persistence
- Session metadata capture
- Basic system prompt and persona scaffold for a companion assistant
- Logging for prompts, responses, timings, and failures

Tests:
- Multi-turn conversations work without losing near-term context
- Sessions are saved and reload correctly
- Restarting the app does not corrupt prior chat history
- Basic regression prompts return acceptable answers

Exit criteria:
- Terminal assistant is usable for daily conversation
- Conversations persist across restarts
- Logs are sufficient for debugging and iteration

## Stage 2: Memory Formation Foundation

Goal: Create the storage and ingestion layer for long-term autobiographical memory, including candidate extraction, daily consolidation, and ritual-aware baseline tracking.

Deliverables:
- Memory schema for events, people, projects, places, facts, and ritual signals
- Ingestion pipeline from chat transcripts into structured candidate memories
- Chunk-level extraction pass that emits memory candidates instead of mini-summaries
- Master daily consolidation pass that merges candidate memories into one coherent day artifact
- Timestamped event storage
- Distinctiveness, emotional significance, practical consequence, and carry-forward scoring fields
- Optional embeddings index for retrieval
- Memory lifecycle rules for raw logs, summaries, and derived memories

Tests:
- New conversations produce candidate memory records reliably
- Chunk extraction preserves who, what, where, when, and why when available without inventing missing details
- Daily consolidation merges repeated themes into one day artifact instead of producing stitched mini-days
- Distinct or unusual events receive more detail than routine background items
- Ritual presence and ritual absence can be tracked without over-surfacing routine repetitions
- Duplicate or conflicting memories are handled predictably
- Stored memories can be queried directly outside the model

Exit criteria:
- Memory data is durable and inspectable
- The system can form one coherent day-memory artifact from real conversations
- The system can store event-like records and ritual signals from conversations
- Retrieval inputs are available for the next stage

## Stage 3: Episodic Recall

Goal: Retrieve and inject autobiographical memories into responses in a useful and grounded way.

Deliverables:
- Retrieval pipeline combining recency, semantic similarity, and structured filters
- Retrieval that can use ritual baselines and baseline deviations, not just explicit event records
- Prompting strategy for grounding responses in recalled episodes
- Memory confidence or provenance metadata
- Recall-specific evaluation set

Tests:
- The assistant recalls specific events when asked who, what, where, when, or why
- The assistant can notice meaningful absence or deviation in recurring rituals when enough prior context exists
- The assistant avoids inventing details that were never stored
- Recall quality remains stable across a representative eval set
- Irrelevant memories are not injected into normal conversation too often

Exit criteria:
- Episodic recall works for a meaningful subset of real conversations
- Failure modes are understood and documented
- Quality is high enough to use in regular personal conversation

## Stage 4: Relationship And Companion Behaviors

Goal: Make the assistant feel coherent over time without sacrificing factual grounding.

Deliverables:
- Stable persona and communication preferences
- Project and life context tracking
- Follow-up reminders or conversational continuity features
- Memory salience rules for important recurring topics

Tests:
- The assistant remembers ongoing projects and recurring themes
- Tone remains consistent across sessions
- Long-running conversations do not degrade memory accuracy excessively

Exit criteria:
- The assistant feels continuous across days and weeks
- Memory supports the companion use case, not just retrieval demos

## Stage 5: Interface Expansion

Goal: Add user interfaces beyond the terminal while preserving the same memory core.

Deliverables:
- Local web interface
- Optional mobile-friendly web experience or iPhone access path
- Shared conversation and memory backend

Tests:
- Web client can start, continue, and resume sessions
- Memory behavior matches terminal behavior
- Basic mobile interaction works from iPhone

Exit criteria:
- The assistant is accessible from MacBook and iPhone
- Interface differences do not break memory behavior

## Stage 6: Hardening And Trust

Goal: Make the system dependable enough for long-term personal use.

Deliverables:
- Backup and restore strategy
- Export and inspect tools for memories
- Privacy controls for deleting or correcting memories
- Regression eval suite

Tests:
- Backups restore correctly
- Memory deletion and correction behave as expected
- Core recall benchmarks do not regress after changes

Exit criteria:
- The system is maintainable over time
- You can trust, inspect, and correct the assistant's memory

## Recommended Near-Term Order

1. Complete Stage 0 before writing much app code
2. Build Stage 1 as a minimal but usable CLI assistant
3. Move directly to Stage 2 and Stage 3 because memory formation and episodic recall are the core technical risks
4. Delay web and mobile until the memory loop is credible

## Current Working Recommendation

- Practical default model for local development: `qwen3.5-35b-a3b`
- Quality reference model for spot checks: `qwen3.5-122b-a10b`
- Dense reference model: `qwen3.5-27b`

## Open Questions

- Which local runtime should be the first implementation target: `llama.cpp`, `vllm-mlx`, `mlx-lm`, Ollama, or another local backend?
- Which storage system should back memory: SQLite, Postgres, or a hybrid approach?
- What response latency is acceptable for a companion conversation workflow?
- How should the system distinguish raw transcript data from trusted autobiographical memory?
- How should distinctiveness be scored so unusual or meaningful events receive richer detail than routine background conversation?
- When enough history exists, how should ritual absence be surfaced without creating false concern?
