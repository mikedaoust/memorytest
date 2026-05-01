from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from memorytest.adapters import create_backend


DEFAULT_PROMPT = "Reply with one sentence about why provenance matters in memory systems."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark local model backends.")
    parser.add_argument("--backend", default="ollama", help="Backend name.")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["qwen3.5:9b", "qwen3.5:27b", "qwen3.5-35b-a3b"],
        help="Models to benchmark.",
    )
    parser.add_argument("--base-url", help="Override backend base URL.")
    parser.add_argument("--api-key", help="API key for OpenAI-compatible backends.")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Prompt text.")
    parser.add_argument("--repeats", type=int, default=2, help="Measured runs per model.")
    parser.add_argument(
        "--warm-runs",
        type=int,
        default=0,
        help="Warm-up runs per model that are excluded from the summary.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=128,
        help="Maximum generated tokens per run.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Optional path to save raw benchmark results as JSON.",
    )
    parser.add_argument(
        "--think",
        action="store_true",
        help="Enable thinking mode when supported.",
    )
    return parser


def extract_ollama_metrics(raw: dict | None) -> dict | None:
    if not raw:
        return None
    if "eval_count" not in raw or "eval_duration" not in raw:
        return None

    eval_duration_seconds = raw["eval_duration"] / 1_000_000_000
    prompt_eval_duration_seconds = raw.get("prompt_eval_duration", 0) / 1_000_000_000
    load_duration_seconds = raw.get("load_duration", 0) / 1_000_000_000
    tokens_per_second = None
    if eval_duration_seconds > 0:
        tokens_per_second = raw["eval_count"] / eval_duration_seconds

    return {
        "eval_count": raw["eval_count"],
        "eval_duration_seconds": eval_duration_seconds,
        "prompt_eval_count": raw.get("prompt_eval_count"),
        "prompt_eval_duration_seconds": prompt_eval_duration_seconds,
        "load_duration_seconds": load_duration_seconds,
        "tokens_per_second": tokens_per_second,
    }


def main() -> None:
    args = build_parser().parse_args()
    prompt_messages = [{"role": "user", "content": args.prompt}]
    results: list[dict] = []

    for model in args.models:
        backend = create_backend(
            args.backend,
            model=model,
            base_url=args.base_url,
            api_key=args.api_key,
            think=args.think,
            temperature=0,
            max_tokens=args.max_tokens,
        )
        measured_latencies: list[float] = []
        warm_latencies: list[float] = []
        throughput_values: list[float] = []
        load_durations: list[float] = []
        run_details: list[dict] = []
        status = "ok"
        last_preview = ""
        total_runs = args.warm_runs + args.repeats

        for run_index in range(total_runs):
            try:
                response = backend.chat(prompt_messages)
            except RuntimeError as exc:
                status = f"error: {exc}"
                break

            metrics = extract_ollama_metrics(response.raw)
            run_record = {
                "run_index": run_index,
                "is_warmup": run_index < args.warm_runs,
                "latency_seconds": round(response.latency_seconds, 2),
                "response_preview": response.content.replace("\n", " ")[:120],
                "ollama_metrics": metrics,
            }
            run_details.append(run_record)
            last_preview = response.content.replace("\n", " ")[:120]
            if run_index < args.warm_runs:
                warm_latencies.append(response.latency_seconds)
            else:
                measured_latencies.append(response.latency_seconds)
                if metrics and metrics["tokens_per_second"] is not None:
                    throughput_values.append(metrics["tokens_per_second"])
                if metrics:
                    load_durations.append(metrics["load_duration_seconds"])

        if measured_latencies:
            summary = {
                "backend": args.backend,
                "model": model,
                "status": status,
                "warm_runs": args.warm_runs,
                "measured_runs": len(measured_latencies),
                "warm_avg_latency_seconds": (
                    round(statistics.mean(warm_latencies), 2) if warm_latencies else None
                ),
                "min_latency_seconds": round(min(measured_latencies), 2),
                "max_latency_seconds": round(max(measured_latencies), 2),
                "avg_latency_seconds": round(statistics.mean(measured_latencies), 2),
                "avg_tokens_per_second": (
                    round(statistics.mean(throughput_values), 2)
                    if throughput_values
                    else None
                ),
                "avg_load_duration_seconds": (
                    round(statistics.mean(load_durations), 2) if load_durations else None
                ),
                "response_preview": last_preview,
                "runs": run_details,
            }
        else:
            summary = {
                "backend": args.backend,
                "model": model,
                "status": status,
                "warm_runs": args.warm_runs,
                "measured_runs": 0,
                "warm_avg_latency_seconds": (
                    round(statistics.mean(warm_latencies), 2) if warm_latencies else None
                ),
                "min_latency_seconds": None,
                "max_latency_seconds": None,
                "avg_latency_seconds": None,
                "avg_tokens_per_second": None,
                "avg_load_duration_seconds": None,
                "response_preview": "",
                "runs": run_details,
            }

        results.append(summary)

    print("backend\tmodel\tstatus\twarm\tmeasured\tavg_tps\tmin\tavg\tmax")
    for result in results:
        print(
            "\t".join(
                [
                    result["backend"],
                    result["model"],
                    result["status"],
                    str(result["warm_runs"]),
                    str(result["measured_runs"]),
                    str(result["avg_tokens_per_second"]),
                    str(result["min_latency_seconds"]),
                    str(result["avg_latency_seconds"]),
                    str(result["max_latency_seconds"]),
                ]
            )
        )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
