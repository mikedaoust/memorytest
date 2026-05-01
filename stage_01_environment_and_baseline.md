# Stage 01: Environment And Baseline

## Objective

Establish a repeatable local development baseline for a terminal-first assistant using only on-device inference.

## Why This Stage Exists

If the runtime, model choice, or storage layer are unstable, every later stage will be noisy. This stage reduces uncertainty before building memory logic.

## Scope

In scope:
- Compare local inference options already installed on the machine
- Pick one primary runtime path
- Pick initial models for chat and embeddings
- Pick an initial storage approach
- Define a basic eval and benchmark workflow

Out of scope:
- Web or mobile UI
- Advanced memory retrieval
- Persona tuning beyond a simple placeholder prompt

## Recommended Technical Defaults

- Baseline chat model: `qwen3.5-27b`
- Fallback candidates: `qwen3.5-9b` for fast iteration and `qwen3.5-35b-a3b` as the next larger candidate to benchmark
- Primary implementation approach: keep a runtime adapter boundary so the app can start with one backend and later switch to `llama.cpp`, `vllm-mlx`, `mlx-lm`, Ollama, or similar local runtimes
- Initial storage: SQLite for speed of iteration and inspectability
- Transcript format: JSONL or SQLite-backed message tables
- Embeddings: use a local embedding model only after the basic assistant loop works

## Tasks

1. Inspect local runtimes and verify which can be scripted cleanly from the terminal
2. Validate `qwen3.5-27b` as the baseline chat model and list any fallback candidates
3. Run a small benchmark on the selected runtime and the baseline model
4. Choose one initial storage design for chat transcripts and memory records
5. Create an initial project structure with a swappable LLM backend interface
6. Write down acceptance thresholds for speed and quality

## Suggested Acceptance Thresholds

- Interactive response begins within about 3 to 8 seconds for normal prompts
- Multi-turn chat remains coherent over at least 10 turns
- The runtime can be launched non-interactively from scripts
- Backend choice does not leak into the rest of the app architecture
- Storage is easy to inspect and back up

## Tests

### Runtime Validation

- Run a one-prompt smoke test from the terminal
- Run a multi-prompt scripted conversation
- Verify runtime startup and model load behavior after restart

### Quality Validation

- Ask the model to summarize a short conversation accurately
- Ask a few general reasoning questions and score the outputs manually
- Record obvious failures such as format drift, excessive latency, or repetition

### Storage Validation

- Save one session
- Reload one session
- Confirm stored data is readable outside the app

## Exit Criteria

- Primary runtime selected
- `qwen3.5-27b` validated or replaced with a documented fallback
- Initial storage approach selected
- Basic benchmarks and notes recorded in `progress.md`

## Risks

- A model that feels good in one-off testing may be too slow in regular use
- Some local runtimes may be pleasant to test manually but awkward to automate reliably
- Embeddings may add complexity before the baseline assistant is stable
- Runtime-specific code can become a trap if the backend abstraction is not enforced early

## Decisions To Capture In Progress Log

- Runtime chosen and why
- Baseline model status and any fallback options
- Storage choice and schema direction
- Measured latency and quality notes
