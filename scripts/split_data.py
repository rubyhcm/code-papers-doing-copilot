#!/usr/bin/env python3
"""Create reproducible train/validation/test splits for HDFS_v1 and BGL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.model_selection import train_test_split


SEEDS = (42, 123, 456, 789, 2024)


def split_hdfs(npz_path: Path, output_dir: Path, seed: int = 42,
               block_csv_path: Optional[Path] = None) -> dict:
    """Split HDFS at block level using the repository's preprocessed NPZ."""
    with np.load(npz_path, allow_pickle=True) as data:
        x_data = data["x_data"]
        y_data = data["y_data"].astype(np.int64)

    indices = np.arange(len(y_data))
    train_idx, temp_idx = train_test_split(
        indices,
        test_size=0.20,
        random_state=seed,
        stratify=y_data,
    )
    val_idx, test_idx = train_test_split(
        temp_idx,
        test_size=0.50,
        random_state=seed,
        stratify=y_data[temp_idx],
    )
    train_x, train_y = x_data[train_idx], y_data[train_idx]
    val_x, val_y = x_data[val_idx], y_data[val_idx]
    test_x, test_y = x_data[test_idx], y_data[test_idx]

    output_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_dir / "hdfs_train.npz",
        x_data=train_x,
        y_data=train_y,
    )
    np.savez_compressed(
        output_dir / "hdfs_val.npz",
        x_data=val_x,
        y_data=val_y,
    )
    np.savez_compressed(
        output_dir / "hdfs_test.npz",
        x_data=test_x,
        y_data=test_y,
    )

    overlap = None
    if block_csv_path is not None:
        import csv
        if not block_csv_path.exists():
            raise ValueError(f"HDFS block CSV not found: {block_csv_path}")
        with block_csv_path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            block_ids = np.asarray([row["BlockId"] for row in reader])
        if len(block_ids) != len(y_data):
            raise ValueError(
                f"Block CSV/NPZ row mismatch: {len(block_ids)} != {len(y_data)}"
            )
        train_ids = block_ids[train_idx]
        val_ids = block_ids[val_idx]
        test_ids = block_ids[test_idx]
        overlap = {
            "train_validation": len(set(train_ids) & set(val_ids)),
            "train_test": len(set(train_ids) & set(test_ids)),
            "validation_test": len(set(val_ids) & set(test_ids)),
        }
        if any(overlap.values()):
            raise RuntimeError("HDFS block overlap detected between splits")
        np.savetxt(output_dir / "hdfs_train_block_ids.txt",
                   train_ids, fmt="%s")
        np.savetxt(output_dir / "hdfs_val_block_ids.txt",
                   val_ids, fmt="%s")
        np.savetxt(output_dir / "hdfs_test_block_ids.txt",
                   test_ids, fmt="%s")

    def summary(y_values: np.ndarray) -> dict:
        count = len(y_values)
        anomaly = int(np.sum(y_values == 1))
        return {
            "blocks": count,
            "anomaly_blocks": anomaly,
            "anomaly_rate": anomaly / count if count else 0.0,
        }

    return {
        "dataset": "hdfs_v1",
        "unit": "block",
        "seed": seed,
        "overlap": overlap,
        "train": summary(train_y),
        "validation": summary(val_y),
        "test": summary(test_y),
    }


def split_bgl(parsed_path: Path, output_dir: Path,
              window_size: int = 200,
              label_path: Optional[Path] = None) -> dict:
    """Create chronological BGL window indices; labels are optional."""
    if label_path is not None and not label_path.exists():
        raise ValueError(f"BGL label file not found: {label_path}")

    labels = []
    with parsed_path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if not line.strip():
                continue
            record = json.loads(line)
            label_value = record.get("label")
            labels.append(1 if label_value == "Anomaly" else 0)

    record_count = len(labels)

    chunks = []
    starts = range(0, record_count - window_size + 1, window_size)
    for start in starts:
        window_labels = labels[start:start + window_size]
        anomaly_lines = sum(window_labels)
        chunks.append({
            "start": start,
            "end": start + window_size,
            "anomaly_lines": anomaly_lines,
            "window_label": 1 if anomaly_lines else 0,
        })

    if not chunks:
        raise ValueError("BGL window size exceeds the dataset record count")

    n = len(chunks)
    train_end = int(0.8 * n)
    val_end = int(0.9 * n)
    splits = {
        "train": chunks[:train_end],
        "validation": chunks[train_end:val_end],
        "test": chunks[val_end:],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "dataset": "bgl",
        "unit": "fixed_time_or_line_window",
        "source": str(parsed_path),
        "window_size": window_size,
        "label_source": str(label_path) if label_path else None,
        "ordered": True,
        "train": len(splits["train"]),
        "validation": len(splits["validation"]),
        "test": len(splits["test"]),
        "ground_truth": "first-column alert tag",
        "label_unit": "line",
        "window_label_rule": "Anomaly if at least one alert line",
        "train_anomaly_windows": sum(
            window["window_label"] for window in splits["train"]
        ),
        "validation_anomaly_windows": sum(
            window["window_label"] for window in splits["validation"]
        ),
        "test_anomaly_windows": sum(
            window["window_label"] for window in splits["test"]
        ),
    }
    (output_dir / "bgl_window_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for name, entries in splits.items():
        import csv
        with (output_dir / f"bgl_{name}_windows.csv").open(
                "w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=("start", "end", "anomaly_lines", "window_label"),
            )
            writer.writeheader()
            writer.writerows(entries)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hdfs-npz",
        type=Path,
        default=Path("data/raw/hdfs_v1/preprocessed/HDFS.npz"),
    )
    parser.add_argument(
        "--hdfs-block-csv",
        type=Path,
        default=Path("data/raw/hdfs_v1/preprocessed/Event_traces.csv"),
    )
    parser.add_argument(
        "--bgl-jsonl",
        type=Path,
        default=Path("data/parsed/bgl_structured.jsonl"),
    )
    parser.add_argument(
        "--bgl-labels",
        type=Path,
        default=None,
        help="Optional ground-truth CSV for BGL.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/splits"),
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--window-size", type=int, default=200)
    args = parser.parse_args()

    if not args.hdfs_npz.exists():
        parser.error(f"HDFS NPZ not found: {args.hdfs_npz}")

    hdfs_summary = split_hdfs(
        args.hdfs_npz,
        args.output_dir,
        args.seed,
        args.hdfs_block_csv,
    )
    bgl_summary = None
    if args.bgl_jsonl.exists():
        bgl_summary = split_bgl(
            args.bgl_jsonl,
            args.output_dir,
            args.window_size,
            args.bgl_labels,
        )

    output = {
        "hdfs_v1": hdfs_summary,
        "bgl": bgl_summary,
    }
    (args.output_dir / "split_manifest.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
