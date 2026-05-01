# Progress Log

This file is the handoff log for future work on the project. Update it after meaningful progress, decisions, or blockers.

## Project Goal

Build a self-hosted assistant that runs locally on a MacBook Pro M4 Max with 128GB RAM and develops autobiographical episodic memory with recall of who, what, where, when, and why across experiences.

## Current Status

- Planning baseline created
- Long-term goal clarified
- Development constraints recorded: local-only models for now, terminal-first MVP, companion use case
- Local runtime and model inventory inspected on the development machine
- Stage 0 scaffold now exists in the repo with benchmark tooling, adapter plumbing, and a terminal chat loop
- A first fixed Stage 1 eval suite now exists with saved Ollama results for `qwen3.5:9b` and `qwen3.5:27b`
- Session storage now includes lightweight metadata and saved summaries for later memory ingestion
- The summary flow now targets a richer daily-memory artifact instead of a flat 3-bullet digest
- The memory pipeline direction is now clearer: chunk candidate extraction, ritual tracking, and master daily consolidation rather than stitched chunk summaries
- The `/summarize` command now uses the first implemented two-stage pipeline: chunk candidate extraction followed by master daily consolidation

## Confirmed Decisions

- Avoid cloud models for the current phase
- Start with a terminal interface
- Optimize for companion-style conversation about work, life, and projects
- Treat episodic memory as autobiographical long-term recall of experiences
- Keep `qwen3.5-9b` as the fast fallback candidate
- Re-open baseline model selection among `qwen3.5-27b`, `qwen3.5-35b-a3b`, and `qwen3.5-122b-a10b`
- Use `qwen3.5-35b-a3b` as the practical default model for ongoing local development
- Treat `qwen3.5-122b-a10b` as the current quality leader on the stronger Stage 1 eval suite
- Keep `qwen3.5-27b` as the dense reference model
- Keep the inference backend swappable rather than hard-coding around one runtime
- Treat routine rituals as background signals unless they are distinct, missing, delayed, or emotionally different
- Preserve both emotional significance and practical consequence in memory formation so later reflection can re-rank them with broader context

## Planning Artifacts

- `long_term_goal.md`
- `roadmap.md`
- `stage_01_environment_and_baseline.md`
- `stage_02_terminal_assistant_mvp.md`
- `stage_03_episodic_memory_foundation.md`

## Implementation Artifacts

- `pyproject.toml`
- `src/memorytest/adapters/`
- `src/memorytest/storage.py`
- `src/memorytest/chat.py`
- `src/memorytest/benchmark.py`
- `src/memorytest/evals.py`
- `src/memorytest/prompts.py`
- `src/memorytest/summary_prompt_v1.py`
- `evals/stage1_terminal_eval_suite.json`
- `data/evals/stage1_ollama_results.json`
- `data/evals/stage1_ollama_compare_2026-03-17_v3.json`
- `data/benchmarks/ollama_qwen_warm_compare_2026-03-17.json`
- `data/summaries/chat_md_daily_memory_2026-03-19.md`
- `data/summaries/chat_md_daily_memory_2026-03-21_v3.md`
- `data/summaries/chat_md_daily_memory_2026-03-27_v4.md`
- `data/summaries/chat_md_daily_memory_2026-04-02_v6.md`
- `tests/test_adapters.py`
- `tests/test_chat_prompt.py`
- `tests/test_evals.py`
- `tests/test_storage.py`

## Recommended Immediate Next Steps

1. Define the first structured memory-ingestion pass that converts daily-memory artifacts and transcript spans into candidate memory records
2. Replace chunk mini-summaries with chunk-level candidate extraction for relationship, project, event, carry-forward, and ritual signals
3. Add a master daily consolidation pass that merges chunk candidates into one coherent day-memory artifact
4. Add distinctiveness, emotional significance, practical consequence, and carry-forward relevance scoring to candidate records
5. Add longer-context and memory-adjacent eval cases that stress correction handling, abstention, chronology preservation, and project continuity over more turns

## Open Questions

- When should LM Studio or another backend be added as a second adapter for larger local models?
- What latency is acceptable for normal use?
- Should memory extraction happen after every message, after every N messages, or only at session end?
- How should ritual baselines be learned before the system starts surfacing absence or deviation?
- What thresholds should control how much detail distinct events receive in the final daily artifact?

## Work Log

### 2026-03-12

- Reviewed and tightened the long-term goal statement
- Proposed a staged plan based on technical risk rather than just features
- Created roadmap and initial stage docs for baseline environment, terminal MVP, and episodic memory foundation
- Established this file as the canonical project handoff log

### 2026-03-15

- Recorded `qwen3.5-27b` as the initial baseline chat model
- Clarified that the inference layer should remain backend-agnostic to support `llama.cpp`, `vllm-mlx`, `mlx-lm`, and similar local runtimes
- Updated the roadmap and early stage docs to reflect a swappable local backend architecture
- Inspected the local machine and confirmed Apple M4 Max with 128GB RAM
- Confirmed installed runtime paths: Ollama `0.18.0`, `mlx_lm` `0.30.7`, and LM Studio CLI `lms`
- Confirmed Ollama-accessible Qwen models: `qwen3.5:9b` and `qwen3.5:27b`
- Confirmed LM Studio-local Qwen models: `9b`, `27b`, `35b-a3b`, and `122b-a10b`, plus MLX-format `27b` variants
- Observed that Ollama `qwen3.5:9b` returned a minimal warm response in about `0.45s`
- Observed that Ollama `qwen3.5:27b` had a slow first one-shot request at about `45s` but a warm repeat response in about `0.76s`
- Confirmed LM Studio has the `lms` CLI available, but the local LM Studio server is not currently running
- Added a Python project scaffold with a working Ollama adapter and a generic OpenAI-compatible adapter
- Added a SQLite-backed terminal chat loop with session persistence and session listing
- Added a benchmark entry point for comparing local models and backends
- Added a fixed eval suite runner for conversation, summarization, and short-term recall
- Added unit tests for adapter parsing and transcript storage
- Added unit tests for eval scoring logic
- Verified the unit tests pass with `PYTHONPATH=src python3 -m unittest discover -s tests`
- Verified the benchmark runs against Ollama and produced a sample result of about `2.91s` for `qwen3.5:9b` and about `7.43s` for `qwen3.5:27b` in the current script
- Verified the terminal chat loop works end to end with a scripted Ollama smoke test
- Created `evals/stage1_terminal_eval_suite.json` and ran it against `qwen3.5:9b` and `qwen3.5:27b`
- Saved Stage 1 eval results to `data/evals/stage1_ollama_results.json`
- Current Stage 1 sample results: both `qwen3.5:9b` and `qwen3.5:27b` passed `5/5` cases with `1.0` average score on the current heuristic suite
- Current Stage 1 sample latencies across the five cases averaged about `0.70s` for `qwen3.5:9b` and about `1.68s` for `qwen3.5:27b`
- The current eval suite is useful for regression detection but not yet strong enough to separate the two models on quality

### 2026-03-17

- Rechecked the local model inventory and confirmed Ollama now exposes `qwen3.5:35b-a3b-q4_K_M` and `qwen3.5:122b-a10b-q4_K_M` in addition to `9b` and `27b`
- Rechecked LM Studio inventory and confirmed local Qwen entries include `9b`, `27b`, `35b-a3b`, and `122b-a10b`
- Did not find a `32b` local Qwen entry during the March 17, 2026 recheck; the currently visible larger MoE entry is `35b-a3b`
- Recorded the user's reported performance notes: `27b` GGUF at about `20 tok/s`, `27b` MLX at about `30 tok/s`, and `122b` GGUF at about `25 tok/s`
- Reopened baseline model selection because the newly available MoE candidates may outperform the dense `27b` model on both speed and quality
- Ran the benchmark against `qwen3.5:27b`, `qwen3.5:35b-a3b-q4_K_M`, and `qwen3.5:122b-a10b-q4_K_M` with thinking disabled through the existing Ollama adapter
- Benchmark result for a one-shot prompt: `27b` about `7.46s`, `35b-a3b` about `6.88s`, and `122b-a10b` about `38.92s`
- Ran the Stage 1 eval suite against the same three Ollama models with thinking disabled
- Stage 1 eval result: `27b` passed `5/5` with `1.0` average score, while `35b-a3b` and `122b-a10b` each passed `4/5` with `0.8` average score
- The larger-model eval misses were narrow: both returned `Green tea.` instead of the exact string `Green tea` on the strict preference-recall case
- Average per-case latency in the Stage 1 eval run was about `1.75s` for `27b`, `1.86s` for `35b-a3b`, and `4.87s` for `122b-a10b`
- Current practical recommendation: keep `27b` as the dense reference model, treat `35b-a3b` as the strongest current baseline candidate, and treat `122b-a10b` as promising but still operationally heavier in the current Ollama path
- Hardened the Stage 1 eval suite by adding ambiguity handling, corrected-fact recall, exclusion-following, and ordered formatting checks
- Relaxed exact-match scoring to ignore trivial surrounding punctuation so semantically correct short answers are not penalized for a trailing period
- Reran the stronger suite and saved the current comparison to `data/evals/stage1_ollama_compare_2026-03-17_v3.json`
- Current stronger-suite result: `27b` scored `8/9` with `0.96`, `35b-a3b` scored `8/9` with `0.96`, and `122b-a10b` scored `9/9` with `1.0`
- On the current stronger suite, `27b` and `35b-a3b` both missed only the `summary_with_exclusion` formatting case by returning `*` bullets instead of `-` bullets
- Average per-case latency on the stronger suite was about `1.64s` for `27b`, `1.36s` for `35b-a3b`, and `3.28s` for `122b-a10b`
- Current recommendation after the stronger suite: `35b-a3b` looks like the best practical balance, while `122b-a10b` is the current quality leader on this limited Stage 1 eval set
- Added a warmed-throughput benchmark path that keeps models warm across measured runs and records Ollama tokens-per-second metrics
- Saved the warmed comparison to `data/benchmarks/ollama_qwen_warm_compare_2026-03-17.json`
- Warmed benchmark result on a longer prompt: `27b` averaged about `16.18 tok/s` and `8.72s`, `35b-a3b` averaged about `44.65 tok/s` and `4.13s`, and `122b-a10b` averaged about `23.86 tok/s` and `6.33s`
- The warmed-throughput benchmark supports using `35b-a3b` as the practical default model for ongoing development
- Extended the SQLite session schema with summary text, message counts, and last-message timestamps so conversations are easier to inspect and ingest later
- Added terminal commands for `/session` and `/summarize`
- Added a lightweight summary generation path that stores a 3-bullet session summary back into the session record
- Verified the storage migration path works on an older session schema in unit tests
- Verified the new session summary flow works end to end in a scripted Ollama smoke test using `qwen3.5:9b`

### 2026-03-19

- Reframed the summary prompt into a richer daily-memory artifact with `Relationship`, `Projects`, `Events`, and `Carry-Forward` sections
- Explicitly changed the prompt so texture is woven into each item through significance, feeling, setting, and why the moment mattered
- Updated `/summarize` so it now generates the richer daily-memory artifact format instead of a flat 3-bullet digest
- Added a prompt-structure unit test to guard the daily-memory output shape
- Ran the updated summarizer against `chat-log/chat.md` using a chunked pass and saved the result to `data/summaries/chat_md_daily_memory_2026-03-19.md`
- The richer output appears materially closer to the intended episodic-memory direction than the earlier flat summary, though the final structure still needs tuning to better preserve strict chronology across a full-day transcript

### 2026-03-21

- Clarified that the current chunked summarization approach is still too close to producing stitched mini-days rather than one coherent daily memory
- Reframed the target architecture as `transcript -> chunk candidates -> master daily memory -> reflection`
- Decided that `Relationship`, `Projects`, `Events`, and `Carry-Forward` remain the main day-memory sections
- Clarified that texture should not live in its own section; it should be embedded inside those sections as feeling, significance, setting, change, and why the item mattered
- Clarified that routine `good morning` and `goodnight` rituals should normally stay in the background layer and only surface when they are distinct, missing, delayed, or emotionally different
- Added the idea of ritual absence as a meaningful signal for later reflection once enough historical baseline exists
- Clarified that emotional significance and practical consequence should both be captured during memory formation so later reflection can weigh them in wider context
- Updated the roadmap and Stage 03 plan so memory work is framed as a memory-formation pipeline, not just transcript summarization plus event extraction
- Implemented a first two-stage daily-memory summarization pipeline in `src/memorytest/chat.py`
- Added transcript chunking so long sessions are broken into bounded prompt-sized chunks before summarization
- Added chunk-level candidate extraction prompts for relationship, project, event, carry-forward, and ritual-signal candidates
- Added a master daily-memory consolidation prompt that merges chunk candidates into one coherent daily artifact
- Kept the CLI surface stable so `/summarize` still stores the final daily-memory artifact in the session record
- Added unit tests for chunk splitting, candidate prompt construction, and the full candidate-then-consolidation pipeline
- Verified the unit test suite still passes with `PYTHONPATH=src python3 -m unittest discover -s tests`
- Ran the new two-stage summarizer against `chat-log/chat.md`, which parsed into `134` messages and required `10` chunks
- The first live run exposed a real truncation issue because summary generation inherited the normal chat `max_tokens=512` budget
- Added a separate summary output budget with a CLI flag `--summary-max-tokens` and a default of `1800`
- Reran the `chat-log/chat.md` test with the higher summary budget and saved the resulting artifact to `data/summaries/chat_md_daily_memory_2026-03-21_v3.md`
- The March 21 rerun produced a more coherent single-day artifact that preserved chronology better than the March 19 output, though further tuning is still needed to decide whether the level of compression and emphasis matches user expectations

### 2026-03-27

- Reworked the summary prompts to reduce interpretive and romantic embellishment that was not explicitly grounded in the transcript
- Changed the final daily-memory artifact from broad thematic buckets to a chronology-first structure: `Morning`, `Workday`, `Afternoon And Evening`, and `Carry-Forward`
- Added explicit tag prefixes like `[relationship, ritual]` and `[project, medical]` so moments can retain multiple meanings without being forced into a single bucket
- Tightened the chunk-candidate schema so it now asks for `explicit_importance` and `cautious_inference` rather than free-form feeling and mood language
- Preserved the two-stage candidate-extraction plus consolidation pipeline, but changed the consolidation instructions to keep separate moments separate instead of collapsing them into a single relationship arc
- Verified the unit test suite still passes with `PYTHONPATH=src python3 -m unittest discover -s tests`
- Reran the grounded chronology-first summarizer against `chat-log/chat.md` and saved the result to `data/summaries/chat_md_daily_memory_2026-03-27_v4.md`
- The March 27 output appears less embellished and more chronological than the March 21 artifact, though some inferred wording still remains and may need one more tightening pass if stricter evidentiary grounding is desired

### 2026-04-02

- The March 27 chronology-first artifact was judged too flat and too close to event logging, with insufficient autobiographical context about how moments felt and why they mattered
- Reworked the candidate and consolidation prompts so each moment now carries three explicit parts: `Observed`, `Felt/Meaning`, and `Confidence`
- Preserved the chronology-first structure, but restored autobiographical texture in a grounded way by asking the model to keep feeling/significance visible rather than stripping it out
- Made inference explicit instead of hiding it inside prose, using `explicit`, `strong_inference`, and `weak_inference`
- Increased the default `--summary-max-tokens` budget from `1800` to `2600` because the richer autobiographical format was clipping long day summaries at the previous limit
- Updated `README.md` to reflect the new default summary budget
- Verified the unit test suite still passes with `PYTHONPATH=src python3 -m unittest discover -s tests`
- Ran the updated autobiographical summarizer against `chat-log/chat.md`; an initial `2026-04-02_v5` run still clipped at the tail under the old budget
- Reran with the higher budget and saved the complete artifact to `data/summaries/chat_md_daily_memory_2026-04-02_v6.md`
- The April 2 output appears closer to the target balance: more lived context than the March 27 version, but still more restrained and auditable than the March 21 version
- Moved the detailed summarizer request builders out of `src/memorytest/chat.py` into a versioned module `src/memorytest/summary_prompt_v1.py`
- Updated the prompt tests to import from the versioned prompt module, making it easier to add future variants like `summary_prompt_v2.py` without mixing prompt history into runtime logic

### 2026-05-01

- Rechecked the local Ollama inventory and confirmed two new Gemma 4 variants are installed: `gemma4:31b-it-q4_K_M` and `gemma4:26b-a4b-it-q8_0`
- Ran the warmed benchmark flow against those two Gemma models plus the current practical Qwen baseline `qwen3.5:35b-a3b-q4_K_M`
- Saved the warmed benchmark comparison to `data/benchmarks/ollama_gemma_qwen_compare_2026-05-01.json`
- Warmed benchmark result on the six-line provenance prompt: `gemma4:31b-it-q4_K_M` averaged about `22.65 tok/s` and `6.75s`, `gemma4:26b-a4b-it-q8_0` averaged about `72.82 tok/s` and `1.78s`, and `qwen3.5:35b-a3b-q4_K_M` averaged about `45.26 tok/s` and `4.08s`
- Cold-start behavior was materially slower for all three models, with warm-up latencies of about `12.7s` for the `31b` Gemma, `16.19s` for the `26b-a4b` Gemma, and `19.12s` for the `35b-a3b` Qwen
- Ran the fixed Stage 1 eval suite against the same three Ollama models
- Saved the eval comparison to `data/evals/stage1_ollama_gemma_qwen_compare_2026-05-01.json`
- All three models scored the same on the current Stage 1 suite: `8/9` passed cases and `0.96` average score
- The Gemma models and the Qwen baseline all missed the same `summary_with_exclusion` formatting case by using `*` bullets instead of the required `-` bullets
- Current read from this limited comparison: `gemma4:26b-a4b-it-q8_0` looks operationally very strong on speed, `qwen3.5:35b-a3b-q4_K_M` remains the established practical baseline, and the current Stage 1 suite is still too shallow to separate them on quality
