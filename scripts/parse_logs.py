#!/usr/bin/env python3
"""Parse raw or already structured logs into a stable JSONL interchange format.

Drain3 is used for unstructured input. Structured CSV exports (such as the
LogRAG BGL example) are normalized without re-parsing their templates.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, Iterator, Optional


def _drain_parser(dataset: str):
    try:
        from drain3 import TemplateMiner
        from drain3.template_miner_config import TemplateMinerConfig
    except ImportError as exc:
        if (Path(".venv/bin/python").exists()
                or Path(".venv/Scripts/python.exe").exists()):
            hint = ("Drain3 is missing from the active Python. Activate "
                    "`.venv` or run `.venv/bin/python scripts/parse_logs.py`.")
        else:
            hint = ("Create `.venv`, install "
                    "`scripts/requirements.txt`, and run "
                    "`.venv/bin/python scripts/parse_logs.py`.")
        raise RuntimeError(
            f"Drain3 is required for raw logs. {hint}"
        ) from exc

    config_path = Path("config") / f"drain_{dataset}.ini"
    config = TemplateMinerConfig()
    if config_path.exists():
        config.load(str(config_path))
    return TemplateMiner(config=config)


def _iter_csv(path: Path) -> Iterator[Dict[str, object]]:
    with path.open(newline="", encoding="utf-8", errors="replace") as stream:
        for line_number, row in enumerate(csv.DictReader(stream), start=1):
            template = row.get("EventTemplate") or row.get("Content") or ""
            template_id = row.get("EventId") or row.get("EventID")
            label = row.get("Label")
            yield {
                "line_id": row.get("LineId") or line_number,
                "raw": row.get("Content") or "",
                "template": template,
                "template_id": template_id,
                "parameters": row.get("ParameterList", []),
                "label": label,
                "source": row,
            }


def _iter_raw(path: Path, dataset: str,
               labels: Optional[Dict[str, str]] = None) -> Iterator[Dict[str, object]]:
    miner = _drain_parser(dataset)
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line_number, line in enumerate(stream, start=1):
            raw = line.rstrip("\r\n")
            if not raw:
                continue
            result = miner.add_log_message(raw)
            label = None
            if labels:
                block_ids = re.findall(r"\bblk_[A-Za-z0-9_-]+", raw)
                matched = [labels[block_id] for block_id in block_ids
                           if block_id in labels]
                if matched:
                    label = "Anomaly" if any(is_anomaly(item) for item in matched) else "Normal"
            yield {
                "line_id": line_number,
                "raw": raw,
                "template": result["template_mined"],
                "template_id": result["cluster_id"],
                "parameters": result.get("parameter_list", []),
                "label": label,
            }


def is_anomaly(value: object) -> bool:
    return str(value or "").strip().lower() in {
        "1", "true", "anomaly", "anomalous", "yes", "error"
    }


def load_labels(path: Optional[Path]) -> Dict[str, str]:
    if path is None:
        candidates = (
            Path("data/raw/hdfs_v1/preprocessed/anomaly_label.csv"),
            Path("data/raw/hdfs_v1/anomaly_label.csv"),
            Path("LightAD/datasets/original_datasets/anomaly_label.csv"),
            Path("data/raw/hdfs_v1/labels.csv"),
        )
        path = next((candidate for candidate in candidates if candidate.exists()),
                    None)
        if path is None:
            return {}
    if path is None:
        return {}
    if not path.exists():
        raise ValueError(f"label file not found: {path}")
    with path.open(newline="", encoding="utf-8", errors="replace") as stream:
        rows = csv.DictReader(stream)
        if not rows.fieldnames or "BlockId" not in rows.fieldnames:
            raise ValueError("label file must contain a BlockId column")
        return {
            row["BlockId"]: row.get("Label", "")
            for row in rows
            if row.get("BlockId")
        }


def parse_file(input_path: Path, output_path: Path, dataset: str,
               input_format: str = "auto",
               label_path: Optional[Path] = None) -> int:
    if input_format == "auto":
        input_format = "csv" if input_path.suffix.lower() == ".csv" else "raw"
    records: Iterable[Dict[str, object]]
    if input_format == "csv":
        records = _iter_csv(input_path)
    elif input_format == "raw":
        records = _iter_raw(input_path, dataset, load_labels(label_path))
    else:
        raise ValueError(f"Unsupported input format: {input_format}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_path.open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset", required=True, choices=("hdfs", "bgl"))
    parser.add_argument("--input-format", choices=("auto", "raw", "csv"),
                        default="auto")
    parser.add_argument("--labels", type=Path,
                        help="HDFS CSV with BlockId and Label columns")
    args = parser.parse_args()
    try:
        count = parse_file(args.input, args.output, args.dataset,
                           args.input_format, args.labels)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"parse_logs: {exc}", file=sys.stderr)
        return 2
    print(f"Parsed {count:,} records -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
