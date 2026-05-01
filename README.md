# memorytest

Terminal-first local assistant scaffold for experimenting with local models, persistent conversation storage, and future episodic memory.

## What Exists

- Swappable LLM backend layer with a working Ollama adapter
- Generic OpenAI-compatible adapter for future LM Studio server or similar local runtimes
- SQLite-backed terminal chat loop
- Benchmark script for comparing candidate models and backends
- Fixed eval suite runner for conversation, summarization, and short-term recall checks
- Two-stage daily-memory summarizer for long transcripts: chunk candidate extraction plus master consolidation
- Basic unit tests for storage and adapter plumbing

## Quick Start

Run the terminal chat with Ollama:

```bash
PYTHONPATH=src python3 -m memorytest.chat --backend ollama --model qwen3.5:35b-a3b-q4_K_M
```

For long `/summarize` runs, you can raise the summary output budget if needed:

```bash
PYTHONPATH=src python3 -m memorytest.chat \
  --backend ollama \
  --model qwen3.5:35b-a3b-q4_K_M \
  --summary-max-tokens 2600
```

Inside the terminal chat, useful commands include:

- `/session` to inspect session metadata and the stored summary
- `/summarize` to generate and save a structured daily-memory artifact through chunk candidate extraction plus final consolidation
- `/history` to print the transcript stored so far

Run a quick benchmark:

```bash
PYTHONPATH=src python3 -m memorytest.benchmark \
  --backend ollama \
  --models qwen3.5:9b qwen3.5:27b \
  --warm-runs 1 \
  --repeats 2
```

Run the Stage 1 eval suite:

```bash
PYTHONPATH=src python3 -m memorytest.evals \
  --backend ollama \
  --models qwen3.5:9b qwen3.5:27b \
  --output-json data/evals/stage1_ollama_results.json
```

Use an OpenAI-compatible local server later:

```bash
PYTHONPATH=src python3 -m memorytest.chat \
  --backend openai-compat \
  --base-url http://127.0.0.1:1234/v1 \
  --model qwen3.5-35b-a3b
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Notes

- The benchmark defaults include `qwen3.5-35b-a3b`, but that model will only succeed if the chosen backend can serve it.
- For Ollama, the benchmark now reports both wall-clock latency and average generated tokens per second when the backend exposes raw timing metrics.
- The first eval suite is intentionally narrow and heuristic-based. It is meant to catch obvious regressions before richer episodic-memory evals exist.
- The summarizer now uses a two-stage pipeline so long sessions are handled as chunk candidates that merge into one day-memory, rather than stitched mini-day summaries.
- Summary generation now has its own configurable output budget via `--summary-max-tokens` so long daily artifacts do not inherit the shorter normal chat limit. The current default is `2600`.
- The terminal scaffold intentionally focuses on dependable transcript persistence first. Long-term episodic memory extraction is still a later stage.
