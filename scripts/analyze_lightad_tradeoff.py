#!/usr/bin/env python3
"""Analyze RQ3 effectiveness/cost trade-off for LightAD results."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def is_dominated(candidate: dict, others: list[dict]) -> bool:
    for other in others:
        if other["name"] == candidate["name"]:
            continue
        no_worse = (
            other["f1"] >= candidate["f1"]
            and other["latency_ms"] <= candidate["latency_ms"]
            and other["train_seconds"] <= candidate["train_seconds"]
        )
        strict = (
            other["f1"] > candidate["f1"]
            or other["latency_ms"] < candidate["latency_ms"]
            or other["train_seconds"] < candidate["train_seconds"]
        )
        if no_worse and strict:
            return True
    return False


def main() -> int:
    rq1_path = ROOT / "results/rq1_lightad_results.json"
    rq2_path = ROOT / "results/rq2_lightad_cost.json"
    if not rq1_path.exists() or not rq2_path.exists():
        raise FileNotFoundError("Run RQ1 and RQ2 result scripts first")

    rq1 = json.loads(rq1_path.read_text(encoding="utf-8"))["summary"]
    rq2 = json.loads(rq2_path.read_text(encoding="utf-8"))

    output = {}
    for dataset in ("hdfs_v1", "bgl"):
        points = []
        for model_name, metrics in rq1[dataset].items():
            cost = rq2[dataset]["models"][model_name]
            points.append({
                "name": model_name,
                "f1": metrics["f1"]["mean"],
                "latency_ms": cost["latency_per_test_sample_ms"],
                "train_seconds": cost["train_time_seconds"],
            })
        for point in points:
            point["pareto"] = not is_dominated(point, points)
        output[dataset] = points

    lines = [
        "# RQ3 — Đánh đổi hiệu quả và chi phí LightAD",
        "",
        "| Dataset | Mô hình | F1 | Latency/test sample (ms) | Train (s) | Pareto |",
        "|---|---|---:|---:|---:|---|",
    ]
    for dataset, points in output.items():
        for point in points:
            lines.append(
                f"| {dataset} | {point['name'].upper()} | "
                f"{point['f1']:.6f} | "
                f"{point['latency_ms']:.6f} | "
                f"{point['train_seconds']:.6f} | "
                f"{'Có' if point['pareto'] else 'Không'} |"
            )

    lines.extend([
        "",
        "Ghi chú:",
        "- Pareto dùng cùng ba trục: F1 lớn hơn tốt, latency nhỏ hơn tốt",
        "  và training time nhỏ hơn tốt.",
        "- Đây là phân tích chi phí của LightAD, chưa so sánh LogFormer/LogRAG.",
    ])

    output_dir = ROOT / "results"
    (output_dir / "rq3_lightad_tradeoff.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "rq3_lightad_tradeoff.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
