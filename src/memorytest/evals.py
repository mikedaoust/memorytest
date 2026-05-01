from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from memorytest.adapters import ChatMessage, create_backend
from memorytest.prompts import SYSTEM_PROMPT


DEFAULT_SUITE_PATH = Path("evals/stage1_terminal_eval_suite.json")


@dataclass(slots=True)
class CheckResult:
    kind: str
    passed: bool
    detail: str


def normalize_text(value: str) -> str:
    return " ".join(value.lower().split())


def normalize_exact_text(value: str) -> str:
    normalized = normalize_text(value)
    return normalized.strip(" \t\n\r'\"`*_.,!?;:()[]{}")


def sentence_count(value: str) -> int:
    parts = [part.strip() for part in re.split(r"[.!?]+", value) if part.strip()]
    return len(parts)


def line_prefix_count(value: str, prefix: str) -> int:
    return sum(1 for line in value.splitlines() if line.lstrip().startswith(prefix))


def evaluate_check(response: str, check: dict) -> CheckResult:
    kind = check["type"]
    normalized = normalize_text(response)

    if kind == "contains_all":
        missing = [item for item in check["values"] if item.lower() not in normalized]
        return CheckResult(
            kind=kind,
            passed=not missing,
            detail="all values present" if not missing else f"missing: {missing}",
        )

    if kind == "contains_any":
        values = [item.lower() for item in check["values"]]
        found = [item for item in values if item in normalized]
        return CheckResult(
            kind=kind,
            passed=bool(found),
            detail=f"matched: {found}" if found else f"none matched: {values}",
        )

    if kind == "not_contains":
        found = [item for item in check["values"] if item.lower() in normalized]
        return CheckResult(
            kind=kind,
            passed=not found,
            detail="no banned values found" if not found else f"found banned: {found}",
        )

    if kind == "exact_match":
        expected = normalize_exact_text(check["value"])
        actual = normalize_exact_text(response)
        return CheckResult(
            kind=kind,
            passed=actual == expected,
            detail=f"expected '{expected}' got '{actual}'",
        )

    if kind == "max_sentences":
        count = sentence_count(response)
        max_allowed = int(check["value"])
        return CheckResult(
            kind=kind,
            passed=count <= max_allowed,
            detail=f"sentence_count={count}, max_allowed={max_allowed}",
        )

    if kind == "line_prefix_count":
        count = line_prefix_count(response, check["prefix"])
        min_count = int(check["min"])
        return CheckResult(
            kind=kind,
            passed=count >= min_count,
            detail=f"matching_lines={count}, min_required={min_count}",
        )

    if kind == "line_starts_with_all":
        normalized_lines = [line.lstrip() for line in response.splitlines()]
        missing = [
            prefix
            for prefix in check["values"]
            if not any(line.startswith(prefix) for line in normalized_lines)
        ]
        return CheckResult(
            kind=kind,
            passed=not missing,
            detail="all prefixes present" if not missing else f"missing prefixes: {missing}",
        )

    raise ValueError(f"Unsupported check type: {kind}")


def evaluate_response(response: str, checks: list[dict]) -> tuple[float, list[CheckResult]]:
    if not checks:
        return 1.0, []

    results = [evaluate_check(response, check) for check in checks]
    passed = sum(1 for result in results if result.passed)
    return passed / len(results), results


def load_suite(path: Path) -> dict:
    return json.loads(path.read_text())


def run_suite(
    *,
    backend_name: str,
    model: str,
    suite: dict,
    base_url: str | None = None,
    api_key: str | None = None,
    think: bool = False,
) -> dict:
    backend = create_backend(
        backend_name,
        model=model,
        base_url=base_url,
        api_key=api_key,
        think=think,
        temperature=0,
        max_tokens=256,
    )

    case_results: list[dict] = []
    total_score = 0.0

    for case in suite["cases"]:
        messages: list[ChatMessage] = []
        if case.get("include_system_prompt", True):
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.extend(case["messages"])

        try:
            response = backend.chat(messages)
            score, checks = evaluate_response(response.content, case.get("checks", []))
            case_results.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "score": round(score, 2),
                    "passed": score == 1.0,
                    "latency_seconds": round(response.latency_seconds, 2),
                    "response": response.content,
                    "checks": [
                        {
                            "type": result.kind,
                            "passed": result.passed,
                            "detail": result.detail,
                        }
                        for result in checks
                    ],
                }
            )
            total_score += score
        except RuntimeError as exc:
            case_results.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "score": 0.0,
                    "passed": False,
                    "latency_seconds": None,
                    "response": "",
                    "checks": [],
                    "error": str(exc),
                }
            )

    max_score = len(suite["cases"]) or 1
    passed_cases = sum(1 for case in case_results if case["passed"])
    return {
        "suite": suite["name"],
        "backend": backend_name,
        "model": model,
        "average_score": round(total_score / max_score, 2),
        "passed_cases": passed_cases,
        "total_cases": len(suite["cases"]),
        "results": case_results,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run fixed evaluation suites.")
    parser.add_argument("--backend", default="ollama", help="Backend name.")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["qwen3.5:9b", "qwen3.5:27b"],
        help="Models to evaluate.",
    )
    parser.add_argument(
        "--suite",
        type=Path,
        default=DEFAULT_SUITE_PATH,
        help="Path to the evaluation suite JSON file.",
    )
    parser.add_argument("--base-url", help="Override backend base URL.")
    parser.add_argument("--api-key", help="API key for OpenAI-compatible backends.")
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Optional path to save model results as JSON.",
    )
    parser.add_argument(
        "--think",
        action="store_true",
        help="Enable thinking mode when supported.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    suite = load_suite(args.suite)
    all_results = [
        run_suite(
            backend_name=args.backend,
            model=model,
            suite=suite,
            base_url=args.base_url,
            api_key=args.api_key,
            think=args.think,
        )
        for model in args.models
    ]

    print("model\tpassed\ttotal\tavg_score")
    for result in all_results:
        print(
            "\t".join(
                [
                    result["model"],
                    str(result["passed_cases"]),
                    str(result["total_cases"]),
                    str(result["average_score"]),
                ]
            )
        )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(all_results, indent=2) + "\n")


if __name__ == "__main__":
    main()
