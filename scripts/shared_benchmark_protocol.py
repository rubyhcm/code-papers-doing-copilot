#!/usr/bin/env python3
"""Build and validate the shared sample-level benchmark protocol."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


PROTOCOL_VERSION = "shared-benchmark-v1"
SPLITS = ("train", "validation", "test")
DEFAULT_OUTPUT_DIR = Path("data/splits/benchmark_protocol_v1")


def _binary_label(value: object, dataset: str) -> int:
    labels = {
        "Normal": 0,
        "Success": 0,
        "Anomaly": 1,
        "Fail": 1,
    }
    try:
        return labels[str(value)]
    except KeyError as exc:
        raise ValueError(f"Unknown {dataset} label: {value!r}") from exc


def build_hdfs_table(matrix_path: Path, seed: int = 42) -> pd.DataFrame:
    """Create one fixed stratified split whose sample key is the HDFS BlockId."""
    frame = pd.read_csv(matrix_path, usecols=["BlockId", "Label"])
    frame["sample_id"] = frame["BlockId"].astype(str)
    if frame["sample_id"].duplicated().any():
        raise ValueError("HDFS BlockId values must be unique")
    labels = np.asarray(
        [_binary_label(value, "HDFS") for value in frame["Label"]],
        dtype=np.int64,
    )
    indices = np.arange(len(frame))
    train_idx, remainder_idx = train_test_split(
        indices,
        test_size=0.20,
        random_state=seed,
        stratify=labels,
    )
    validation_idx, test_idx = train_test_split(
        remainder_idx,
        test_size=0.50,
        random_state=seed,
        stratify=labels[remainder_idx],
    )
    assignments = np.full(len(frame), "", dtype=object)
    assignments[train_idx] = "train"
    assignments[validation_idx] = "validation"
    assignments[test_idx] = "test"
    return pd.DataFrame({
        "sample_id": frame["sample_id"],
        "label": labels,
        "split": assignments,
    })


def build_bgl_table(parsed_path: Path, window_size: int = 200) -> tuple[pd.DataFrame, int]:
    """Create non-overlapping chronological windows over parsed BGL records."""
    if window_size < 1:
        raise ValueError("BGL window size must be positive")

    windows: list[dict[str, object]] = []
    current_anomaly = False
    record_index = 0
    with parsed_path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if not line.strip():
                continue
            record = json.loads(line)
            label = record.get("label")
            if label not in ("Normal", "Anomaly"):
                raise ValueError(
                    f"Unexpected BGL label at record {record_index}: {label!r}"
                )
            current_anomaly = current_anomaly or label == "Anomaly"
            record_index += 1
            if record_index % window_size == 0:
                start = record_index - window_size
                windows.append({
                    "sample_id": f"bgl:{start}:{record_index}",
                    "label": int(current_anomaly),
                    "start": start,
                    "end": record_index,
                })
                current_anomaly = False

    remainder = record_index % window_size
    if not windows:
        raise ValueError("BGL contains no complete windows")

    table = pd.DataFrame(windows)
    n_windows = len(table)
    train_end = int(0.8 * n_windows)
    validation_end = int(0.9 * n_windows)
    table["split"] = ""
    table.loc[:train_end - 1, "split"] = "train"
    table.loc[train_end:validation_end - 1, "split"] = "validation"
    table.loc[validation_end:, "split"] = "test"
    return table, remainder


def _split_counts(table: pd.DataFrame) -> dict:
    counts = {}
    for split in SPLITS:
        rows = table[table["split"] == split]
        counts[split] = {
            "samples": int(len(rows)),
            "anomalies": int(rows["label"].sum()),
            "normals": int(len(rows) - rows["label"].sum()),
        }
    return counts


def create_protocol(
    hdfs_matrix: Path,
    bgl_parsed: Path,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    hdfs_seed: int = 42,
    bgl_window_size: int = 200,
) -> dict:
    hdfs_table = build_hdfs_table(hdfs_matrix, seed=hdfs_seed)
    bgl_table, bgl_dropped_records = build_bgl_table(
        bgl_parsed,
        window_size=bgl_window_size,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    hdfs_path = output_dir / "hdfs_v1.csv"
    bgl_path = output_dir / "bgl.csv"
    hdfs_table.to_csv(hdfs_path, index=False)
    bgl_table.to_csv(bgl_path, index=False)
    load_split_table(output_dir, "hdfs_v1")
    load_split_table(output_dir, "bgl")

    manifest = {
        "protocol_version": PROTOCOL_VERSION,
        "split_policy": {
            "hdfs_v1": (
                "BlockId-level stratified 80/10/10 split; fixed seed "
                f"{hdfs_seed}; all methods use the same IDs."
            ),
            "bgl": (
                f"Non-overlapping chronological {bgl_window_size}-record "
                "windows; first 80% train, next 10% validation, final 10% "
                "test; all methods use the same record ranges."
            ),
        },
        "evaluation_unit": {
            "hdfs_v1": "HDFS block",
            "bgl": f"{bgl_window_size}-record log window",
        },
        "label_rule": {
            "hdfs_v1": "Success/Normal=0; Fail/Anomaly=1",
            "bgl": "Anomaly if any record in the window is labeled Anomaly",
        },
        "sources": {
            "hdfs_matrix": str(hdfs_matrix),
            "bgl_parsed": str(bgl_parsed),
        },
        "bgl_dropped_incomplete_records": bgl_dropped_records,
        "files": {
            "hdfs_v1": hdfs_path.name,
            "bgl": bgl_path.name,
        },
        "counts": {
            "hdfs_v1": _split_counts(hdfs_table),
            "bgl": _split_counts(bgl_table),
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def load_split_table(protocol_dir: Path, dataset: str) -> pd.DataFrame:
    if dataset not in ("hdfs_v1", "bgl"):
        raise ValueError(f"Unsupported dataset: {dataset}")
    filename = "hdfs_v1.csv" if dataset == "hdfs_v1" else "bgl.csv"
    path = protocol_dir / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Shared split table not found: {path}. "
            "Run scripts/shared_benchmark_protocol.py first."
        )
    table = pd.read_csv(path, dtype={"sample_id": str, "split": str})
    required = {"sample_id", "label", "split"}
    if not required.issubset(table.columns):
        raise ValueError(f"{path} must contain columns {sorted(required)}")
    if table["sample_id"].duplicated().any():
        raise ValueError(f"{path} contains duplicate sample IDs")
    if not set(table["split"]).issubset(SPLITS) or set(table["split"]) != set(SPLITS):
        raise ValueError(f"{path} must contain all split names: {SPLITS}")
    if not set(table["label"].unique()).issubset({0, 1}):
        raise ValueError(f"{path} labels must be binary")
    for split in SPLITS:
        labels = set(table.loc[table["split"] == split, "label"].astype(int))
        if labels != {0, 1}:
            raise ValueError(f"{dataset} {split} split must contain both classes")
    return table


def align_indices(
    sample_ids: list[str] | np.ndarray,
    labels: list[int] | np.ndarray,
    table: pd.DataFrame,
    *,
    allow_subset: bool = False,
) -> dict[str, np.ndarray]:
    """Map dataset rows to the common split, rejecting ID/label mismatches."""
    ids = np.asarray(sample_ids, dtype=str)
    y = np.asarray(labels, dtype=np.int64)
    if len(ids) != len(y):
        raise ValueError("Sample ID and label counts differ")
    if len(set(ids)) != len(ids):
        raise ValueError("Input sample IDs must be unique")

    split_by_id = table.set_index("sample_id")["split"]
    label_by_id = table.set_index("sample_id")["label"].astype(int)
    unknown = sorted(set(ids) - set(split_by_id.index))
    missing = sorted(set(split_by_id.index) - set(ids))
    if unknown:
        raise ValueError(f"Input contains IDs absent from shared protocol: {unknown[:3]}")
    if missing and not allow_subset:
        raise ValueError(f"Input is missing {len(missing)} IDs from shared protocol")

    expected_labels = np.asarray([label_by_id[sample_id] for sample_id in ids])
    if not np.array_equal(expected_labels, y):
        mismatch = int(np.flatnonzero(expected_labels != y)[0])
        raise ValueError(
            f"Label mismatch for sample {ids[mismatch]}: "
            f"input={y[mismatch]}, protocol={expected_labels[mismatch]}"
        )
    assignments = np.asarray([split_by_id[sample_id] for sample_id in ids])
    indices = {
        split: np.flatnonzero(assignments == split)
        for split in SPLITS
    }
    if any(len(indices[split]) == 0 for split in SPLITS):
        raise ValueError("Aligned input must contain samples in all three splits")
    return indices


def validate_samples_for_split(
    sample_ids: list[str] | np.ndarray,
    labels: list[int] | np.ndarray,
    table: pd.DataFrame,
    expected_split: str,
) -> None:
    """Reject NPZ data whose IDs, labels, or assigned split differ."""
    if expected_split not in SPLITS:
        raise ValueError(f"Unknown expected split: {expected_split}")
    ids = np.asarray(sample_ids, dtype=str)
    y = np.asarray(labels, dtype=np.int64)
    if len(ids) != len(y):
        raise ValueError("Sample ID and label counts differ")
    if len(set(ids)) != len(ids):
        raise ValueError(f"{expected_split} NPZ contains duplicate sample IDs")

    indexed = table.set_index("sample_id")
    unknown = sorted(set(ids) - set(indexed.index))
    if unknown:
        raise ValueError(
            f"{expected_split} NPZ contains IDs absent from shared protocol: "
            f"{unknown[:3]}"
        )
    expected = indexed.loc[ids]
    wrong_split = expected["split"].to_numpy() != expected_split
    if np.any(wrong_split):
        sample_id = ids[int(np.flatnonzero(wrong_split)[0])]
        raise ValueError(
            f"Sample {sample_id} belongs to {expected.loc[sample_id, 'split']}, "
            f"not {expected_split}"
        )
    expected_labels = expected["label"].to_numpy(dtype=np.int64)
    if not np.array_equal(expected_labels, y):
        mismatch = int(np.flatnonzero(expected_labels != y)[0])
        raise ValueError(
            f"Label mismatch for sample {ids[mismatch]}: "
            f"input={y[mismatch]}, protocol={expected_labels[mismatch]}"
        )


def select_f1_threshold(labels: np.ndarray, scores: np.ndarray) -> float:
    """Select an anomaly threshold on validation data; ties prefer precision."""
    y = np.asarray(labels, dtype=np.int64)
    values = np.asarray(scores, dtype=np.float64)
    if len(y) == 0 or len(y) != len(values):
        raise ValueError("Validation labels and scores must have equal non-zero length")
    if set(np.unique(y)) != {0, 1}:
        raise ValueError("Validation threshold selection requires both classes")
    if not np.all(np.isfinite(values)):
        raise ValueError("Validation scores must all be finite")

    candidates = np.unique(values)
    candidates = np.append(candidates, np.nextafter(candidates[-1], np.inf))
    best_threshold = float(candidates[0])
    best_f1 = -1.0
    best_precision = -1.0
    for threshold in candidates:
        predictions = values >= threshold
        true_positive = int(np.sum((y == 1) & predictions))
        false_positive = int(np.sum((y == 0) & predictions))
        false_negative = int(np.sum((y == 1) & ~predictions))
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive else 0.0
        )
        recall = true_positive / (true_positive + false_negative)
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0
        )
        if (f1 > best_f1 or
                (np.isclose(f1, best_f1) and precision > best_precision) or
                (np.isclose(f1, best_f1) and np.isclose(precision, best_precision)
                 and threshold > best_threshold)):
            best_f1 = f1
            best_precision = precision
            best_threshold = float(threshold)
    return best_threshold


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hdfs-matrix",
        type=Path,
        default=Path("data/raw/hdfs_v1/preprocessed/Event_occurrence_matrix.csv"),
    )
    parser.add_argument(
        "--bgl-parsed",
        type=Path,
        default=Path("data/parsed/bgl_structured.jsonl"),
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--hdfs-seed", type=int, default=42)
    parser.add_argument("--bgl-window-size", type=int, default=200)
    args = parser.parse_args()

    for path in (args.hdfs_matrix, args.bgl_parsed):
        if not path.exists():
            parser.error(f"Required source file not found: {path}")
    manifest = create_protocol(
        args.hdfs_matrix,
        args.bgl_parsed,
        args.output_dir,
        args.hdfs_seed,
        args.bgl_window_size,
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
