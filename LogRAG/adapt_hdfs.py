#!/usr/bin/env python3
"""Create block-based HDFS_v1 sessions for the LogRAG RAG pipeline."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


def create_hdfs_sessions(traces_path: Path, output_path: Path) -> dict:
    if not traces_path.exists():
        raise FileNotFoundError(traces_path)

    frame = pd.read_csv(traces_path)
    required = {"BlockId", "Label", "Features", "Type"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing HDFS trace columns: {sorted(missing)}")

    label_map = {"Success": 0, "Fail": 1, "Normal": 0, "Anomaly": 1}
    session_count = 0
    anomaly_count = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as stream:
        for row in frame.itertuples(index=False):
            label = label_map.get(str(row.Label), None)
            if label is None:
                continue
            session = {
                "session_id": row.BlockId,
                "event_sequence": str(row.Features),
                "log_count": len(re.findall(r"\bE\d+\b", str(row.Features))),
                "label": label,
            }
            stream.write(json.dumps(session, ensure_ascii=False) + "\n")
            session_count += 1
            anomaly_count += int(label == 1)

    return {
        "dataset": "hdfs_v1",
        "session_count": session_count,
        "anomaly_sessions": anomaly_count,
        "anomaly_rate": (
            anomaly_count / session_count if session_count else 0.0
        ),
        "source": str(traces_path),
        "output": str(output_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    repo_root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--traces",
        type=Path,
        default=repo_root
        / "data/raw/hdfs_v1/preprocessed/Event_traces.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/hdfs_sessions.jsonl"),
    )
    args = parser.parse_args()
    summary = create_hdfs_sessions(args.traces, args.output)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
