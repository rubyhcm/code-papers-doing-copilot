"""Prepare and evaluate LogRAG against the shared BGL window protocol."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


REQUIRED_BGL_COLUMNS = {
    "LineId",
    "Label",
    "Timestamp",
    "Content",
    "EventTemplate",
}
SPLITS = ("train", "validation", "test")


def _bgl_label(value: object) -> int:
    if str(value).strip().lower() in {"-", "normal", "success", "0"}:
        return 0
    if str(value).strip().lower() in {"anomaly", "fail", "1"}:
        return 1
    raise ValueError(f"Unknown BGL label: {value!r}")


def prepare_bgl_splits(
    structured_csv: Path,
    protocol_dir: Path,
    output_dir: Path,
    *,
    chunksize: int = 100_000,
) -> dict[str, Path]:
    """Write line-level CSV splits whose windows exactly match protocol v1."""
    protocol_path = protocol_dir / "bgl.csv"
    manifest_path = protocol_dir / "manifest.json"
    if not structured_csv.exists():
        raise FileNotFoundError(structured_csv)
    if not protocol_path.exists() or not manifest_path.exists():
        raise FileNotFoundError(
            f"Shared BGL protocol is incomplete under {protocol_dir}"
        )
    if chunksize < 1:
        raise ValueError("chunksize must be positive")

    protocol = pd.read_csv(protocol_path)
    required_protocol_columns = {"sample_id", "label", "split", "start", "end"}
    missing = required_protocol_columns - set(protocol.columns)
    if missing:
        raise ValueError(f"bgl.csv is missing columns: {sorted(missing)}")
    if protocol.empty or protocol["sample_id"].duplicated().any():
        raise ValueError("bgl.csv must contain unique sample IDs")

    widths = protocol["end"].to_numpy(dtype=np.int64) - protocol[
        "start"
    ].to_numpy(dtype=np.int64)
    if np.any(widths <= 0) or len(np.unique(widths)) != 1:
        raise ValueError("BGL protocol windows must have one positive fixed size")
    window_size = int(widths[0])
    expected_starts = np.arange(len(protocol), dtype=np.int64) * window_size
    if not np.array_equal(
        protocol["start"].to_numpy(dtype=np.int64), expected_starts
    ):
        raise ValueError("BGL protocol windows must be contiguous and ordered")
    if set(protocol["split"].astype(str)) != set(SPLITS):
        raise ValueError(f"bgl.csv must include all splits: {SPLITS}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_remainder = int(manifest["bgl_dropped_incomplete_records"])
    complete_records = len(protocol) * window_size
    split_by_window = protocol["split"].astype(str).to_numpy()
    expected_labels = protocol["label"].to_numpy(dtype=np.int64)
    observed_labels = np.zeros(len(protocol), dtype=np.int64)
    observed_counts = np.zeros(len(protocol), dtype=np.int64)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths = {
        split: output_dir / f"{split}.csv" for split in SPLITS
    }
    for path in output_paths.values():
        path.unlink(missing_ok=True)

    record_offset = 0
    written_counts = {split: 0 for split in SPLITS}
    for chunk in pd.read_csv(structured_csv, chunksize=chunksize):
        missing_columns = REQUIRED_BGL_COLUMNS - set(chunk.columns)
        if missing_columns:
            raise ValueError(
                f"{structured_csv} is missing required columns: "
                f"{sorted(missing_columns)}"
            )
        positions = np.arange(
            record_offset, record_offset + len(chunk), dtype=np.int64
        )
        record_offset += len(chunk)
        complete_mask = positions < complete_records
        if not complete_mask.any():
            continue

        labels = np.fromiter(
            (_bgl_label(value) for value in chunk["Label"]),
            dtype=np.int64,
            count=len(chunk),
        )
        window_indices = positions[complete_mask] // window_size
        np.maximum.at(
            observed_labels,
            window_indices,
            labels[complete_mask],
        )
        np.add.at(observed_counts, window_indices, 1)

        complete_rows = chunk.loc[complete_mask].copy()
        complete_positions = positions[complete_mask]
        complete_window_indices = window_indices
        line_ids = pd.to_numeric(
            complete_rows["LineId"], errors="raise"
        ).to_numpy(dtype=np.int64)
        if not np.array_equal(line_ids, complete_positions + 1):
            raise ValueError(
                "BGL LineId must be 1-based and follow the parsed record order"
            )
        complete_rows["sample_id"] = protocol.iloc[
            complete_window_indices
        ]["sample_id"].to_numpy()
        row_splits = split_by_window[complete_window_indices]
        for split in SPLITS:
            selected = complete_rows.loc[row_splits == split]
            if selected.empty:
                continue
            selected.to_csv(
                output_paths[split],
                mode="a",
                header=not output_paths[split].exists(),
                index=False,
            )
            written_counts[split] += len(selected)

    if record_offset != complete_records + expected_remainder:
        raise ValueError(
            "Structured BGL record count does not match the protocol: "
            f"got {record_offset}, expected "
            f"{complete_records + expected_remainder}"
        )
    if np.any(observed_counts != window_size):
        raise ValueError("At least one protocol window has missing records")
    mismatches = np.flatnonzero(observed_labels != expected_labels)
    if len(mismatches):
        row = protocol.iloc[int(mismatches[0])]
        raise ValueError(
            f"BGL label mismatch for {row['sample_id']}: "
            f"input={observed_labels[mismatches[0]]}, "
            f"protocol={expected_labels[mismatches[0]]}"
        )
    if any(written_counts[split] == 0 for split in SPLITS):
        raise ValueError("A generated BGL split is empty")
    return output_paths


def evaluate_bgl_windows(
    split_csv: Path,
    protocol_dir: Path,
    predicted_line_ids: list[int],
    split: str,
) -> tuple[dict, pd.DataFrame]:
    """Aggregate line predictions to the exact protocol window IDs."""
    if split not in SPLITS:
        raise ValueError(f"Unknown split: {split}")
    protocol = pd.read_csv(protocol_dir / "bgl.csv")
    expected = protocol.loc[protocol["split"] == split, [
        "sample_id",
        "label",
    ]].copy()
    rows = pd.read_csv(split_csv, usecols=["LineId", "sample_id"])
    line_ids = pd.to_numeric(rows["LineId"], errors="raise").to_numpy(
        dtype=np.int64
    )
    predicted_ids = set(int(value) for value in predicted_line_ids)
    row_predictions = np.fromiter(
        (int(line_id) in predicted_ids for line_id in line_ids),
        dtype=np.int64,
        count=len(line_ids),
    )
    rows["prediction"] = row_predictions
    actual_ids = set(rows["sample_id"].astype(str))
    expected_ids = set(expected["sample_id"].astype(str))
    if actual_ids != expected_ids:
        raise ValueError(
            f"{split} input sample IDs differ from the shared protocol"
        )

    aggregate = rows.groupby("sample_id", sort=False)["prediction"].max()
    predictions = expected.merge(
        aggregate.rename("prediction"),
        left_on="sample_id",
        right_index=True,
        how="left",
        validate="one_to_one",
    )
    if predictions["prediction"].isna().any():
        raise ValueError(f"{split} has protocol windows without input records")
    predictions["label"] = predictions["label"].astype(np.int64)
    predictions["prediction"] = predictions["prediction"].astype(np.int64)
    labels = predictions["label"].to_numpy()
    outputs = predictions["prediction"].to_numpy()
    metrics = {
        "split": split,
        "samples": int(len(predictions)),
        "anomalies": int(labels.sum()),
        "accuracy": float(accuracy_score(labels, outputs)),
        "precision": float(precision_score(labels, outputs, zero_division=0)),
        "recall": float(recall_score(labels, outputs, zero_division=0)),
        "f1": float(f1_score(labels, outputs, zero_division=0)),
    }
    return metrics, predictions
