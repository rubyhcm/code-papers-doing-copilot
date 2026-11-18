#!/usr/bin/env python3
"""Compute dependency-free descriptive statistics from parsed JSONL or CSV."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterator


def records(path: Path) -> Iterator[dict]:
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8", errors="replace") as stream:
            yield from csv.DictReader(stream)
        return
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def is_anomaly(value: object) -> bool:
    return str(value or "").strip().lower() in {
        "1", "true", "anomaly", "anomalous", "yes", "error"
    }


def analyze(path: Path, dataset: str) -> Dict[str, object]:
    total = anomalies = 0
    templates = Counter()
    anomaly_templates = defaultdict(int)
    for row in records(path):
        total += 1
        template = row.get("template_id") or row.get("EventId") or row.get("event_id")
        templates[str(template or "<unknown>")] += 1
        if is_anomaly(row.get("label") or row.get("Label")):
            anomalies += 1
            anomaly_templates[str(template or "<unknown>")] += 1
    return {
        "dataset": dataset,
        "source": str(path),
        "total_lines": total,
        "unique_templates": len(templates),
        "anomaly_lines": anomalies,
        "anomaly_rate": anomalies / total if total else None,
        "top_templates": [
            {"template_id": key, "count": count}
            for key, count in templates.most_common(20)
        ],
        "anomaly_templates": [
            {"template_id": key, "anomaly_count": count}
            for key, count in sorted(anomaly_templates.items(),
                                      key=lambda item: (-item[1], item[0]))
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", action="append", nargs=2, metavar=("NAME", "PATH"),
                        help="Dataset name and parsed input path.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.dataset:
        parser.error("at least one --dataset NAME PATH LABEL is required")
    allowed_names = {"hdfs_v1", "bgl"}
    invalid_names = sorted({
        name for name, _path in args.dataset if name not in allowed_names
    })
    if invalid_names:
        parser.error(
            "unsupported dataset name(s): "
            + ", ".join(invalid_names)
            + ". Use hdfs_v1 or bgl."
        )
    result = {
        name: analyze(Path(path), name)
        for name, path in args.dataset
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(f"Wrote statistics for {len(result)} datasets -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
