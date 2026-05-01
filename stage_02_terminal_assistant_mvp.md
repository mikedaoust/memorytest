# Stage 02: Terminal Assistant MVP

## Objective

Build a terminal-based companion assistant that supports persistent multi-session conversation before adding advanced autobiographical recall.

## Scope

In scope:
- CLI chat loop
- Session persistence
- Basic persona prompt
- Logging and error handling
- Conversation transcript storage

Out of scope:
- Rich episodic recall
- Web or mobile clients
- Complex orchestration with multiple agents

## Functional Requirements

- Start a new session
- Resume a prior session
- Persist user and assistant messages with timestamps
- Maintain short-term conversational context
- Record basic metadata such as session title, model used, and timing

## Suggested Architecture

- `src/cli/`: terminal interface
- `src/llm/`: runtime adapter for `llama.cpp`, `vllm-mlx`, `mlx-lm`, Ollama, or other local backends
- `src/storage/`: transcript persistence
- `src/evals/`: prompt sets and expected behaviors
- `data/`: local chat and memory database files

Initial assumption:
- Start with `qwen3.5-27b` unless Stage 01 benchmarking forces a change

## Tests

### Core Behavior

- Start a session and exchange at least 10 turns
- Resume that session after restarting the program
- Verify transcript order and timestamps are preserved

### Failure Handling

- Model unavailable
- Empty response
- Interrupted generation
- Invalid stored session reference

### Regression Prompts

Create a small fixed prompt suite to test:
- normal conversation
- project discussion
- recall of something said earlier in the same session
- summarization of the current session

## Exit Criteria

- The CLI is usable for real conversation
- Sessions persist reliably
- The app has enough logging to debug model and storage issues

## Risks

- Overbuilding the CLI before memory work starts
- Mixing short-term context management with long-term memory too early
- Treating transcript persistence as equivalent to episodic memory

## Notes

This stage should intentionally stay simple. The goal is to produce clean transcripts and a dependable chat loop that later memory pipelines can consume.
