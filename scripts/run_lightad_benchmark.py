#!/usr/bin/env python3
"""Run LightAD-style DT/KNN/SLFN baselines on HDFS_v1 and BGL."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.evaluate import compute_metrics
from scripts.shared_benchmark_protocol import (
    PROTOCOL_VERSION,
    align_indices,
    load_split_table,
    select_f1_threshold,
)


SEEDS = (42, 123, 456, 789, 2024)
MODELS = ("dt", "knn", "slfn")


def make_model(name: str, seed: int):
    if name == "dt":
        return DecisionTreeClassifier(random_state=seed)
    if name == "knn":
        return KNeighborsClassifier(n_neighbors=1, n_jobs=-1)
    if name == "slfn":
        return MLPClassifier(
            hidden_layer_sizes=(25,),
            max_iter=300,
            random_state=seed,
        )
    raise ValueError(f"Unsupported model: {name}")


def load_hdfs(matrix_path: Path):
    frame = pd.read_csv(matrix_path)
    feature_columns = [f"E{i}" for i in range(1, 30)]
    missing = [column for column in feature_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing HDFS feature columns: {missing}")
    x_data = frame[feature_columns].to_numpy(dtype=np.float32)
    y_data = frame["Label"].replace(
        {"Normal": 0, "Success": 0, "Anomaly": 1, "Fail": 1}
    ).to_numpy(dtype=np.int64)
    return x_data, y_data, frame["BlockId"].astype(str).to_numpy()


def load_bgl(parsed_path: Path, window_size: int = 200):
    feature_ids = set()
    windows = []
    counts = Counter()
    window_labels = []
    records = 0

    with parsed_path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if not line.strip():
                continue
            record = json.loads(line)
            template_id = str(record.get("template_id") or "<unknown>")
            feature_ids.add(template_id)
            counts[template_id] += 1
            window_labels.append(1 if record.get("label") == "Anomaly" else 0)
            records += 1

    ordered_ids = sorted(feature_ids, key=lambda value: int(value)
                         if value.isdigit() else 10**9)
    index = {template_id: position for position, template_id
             in enumerate(ordered_ids)}
    x_rows = []
    y_rows = []
    sample_ids = []

    with parsed_path.open(encoding="utf-8", errors="replace") as stream:
        window_counts = Counter()
        window_label = 0
        position = 0
        for line in stream:
            if not line.strip():
                continue
            record = json.loads(line)
            template_id = str(record.get("template_id") or "<unknown>")
            window_counts[index[template_id]] += 1
            if record.get("label") == "Anomaly":
                window_label = 1
            position += 1
            if position % window_size == 0:
                x_rows.append([
                    window_counts[i] if i in window_counts else 0
                    for i in range(len(ordered_ids))
                ])
                y_rows.append(window_label)
                sample_ids.append(
                    f"bgl:{position - window_size}:{position}"
                )
                window_counts = Counter()
                window_label = 0

    x_data = np.asarray(x_rows, dtype=np.float32)
    y_data = np.asarray(y_rows, dtype=np.int64)
    return x_data, y_data, np.asarray(sample_ids, dtype=str)


def run_model(
    model_name: str,
    x_data: np.ndarray,
    y_data: np.ndarray,
    train_idx: np.ndarray,
    val_idx: np.ndarray,
    test_idx: np.ndarray,
    seed: int,
) -> dict:
    model = make_model(model_name, seed)
    start = time.perf_counter()
    model.fit(x_data[train_idx], y_data[train_idx])
    train_time = time.perf_counter() - start

    if not hasattr(model, "predict_proba"):
        raise TypeError(f"{model_name} must provide predict_proba scores")
    val_scores = model.predict_proba(x_data[val_idx])[:, 1]
    threshold = select_f1_threshold(y_data[val_idx], val_scores)
    val_predictions = (val_scores >= threshold).astype(np.int64)
    val_metrics = compute_metrics(
        y_data[val_idx],
        val_predictions,
        val_scores,
    )

    start = time.perf_counter()
    y_scores = model.predict_proba(x_data[test_idx])[:, 1]
    y_pred = (y_scores >= threshold).astype(np.int64)
    infer_time = time.perf_counter() - start

    metrics = compute_metrics(y_data[test_idx], y_pred, y_scores)
    metrics.update({
        "train_time_seconds": train_time,
        "inference_time_seconds": infer_time,
        "seed": seed,
        "threshold": threshold,
        "validation": {
            key: val_metrics[key]
            for key in ("precision", "recall", "f1")
        },
        "model_config": model.get_params(deep=False),
    })
    return metrics


def aggregate(runs: list[dict]) -> dict:
    metric_names = ("precision", "recall", "f1", "pr_auc", "fpr")
    summary = {}
    for metric in metric_names:
        values = np.asarray([
            0.0 if run[metric] is None else run[metric]
            for run in runs
        ], dtype=np.float64)
        summary[metric] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        }
    summary["train_time_seconds"] = {
        "mean": float(np.mean([run["train_time_seconds"] for run in runs]))
    }
    summary["inference_time_seconds"] = {
        "mean": float(np.mean([run["inference_time_seconds"] for run in runs]))
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hdfs-matrix",
        type=Path,
        default=Path(
            "data/raw/hdfs_v1/preprocessed/"
            "Event_occurrence_matrix.csv"
        ),
    )
    parser.add_argument(
        "--bgl-jsonl",
        type=Path,
        default=Path("data/parsed/bgl_structured.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/rq1_lightad_shared_protocol_v1.json"),
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=200,
    )
    parser.add_argument(
        "--protocol-dir",
        type=Path,
        default=Path("data/splits/benchmark_protocol_v1"),
    )
    args = parser.parse_args()

    if not (args.protocol_dir / "manifest.json").exists():
        parser.error(
            f"Shared benchmark protocol not found in {args.protocol_dir}; "
            "run scripts/shared_benchmark_protocol.py first."
        )
    protocol = json.loads(
        (args.protocol_dir / "manifest.json").read_text(encoding="utf-8")
    )
    if protocol.get("protocol_version") != PROTOCOL_VERSION:
        parser.error(
            f"Expected protocol {PROTOCOL_VERSION}, found "
            f"{protocol.get('protocol_version')!r}."
        )
    hdfs_table = load_split_table(args.protocol_dir, "hdfs_v1")
    bgl_table = load_split_table(args.protocol_dir, "bgl")
    hdfs_x, hdfs_y, hdfs_ids = load_hdfs(args.hdfs_matrix)
    bgl_x, bgl_y, bgl_ids = load_bgl(args.bgl_jsonl, args.window_size)
    hdfs_splits = align_indices(hdfs_ids, hdfs_y, hdfs_table)
    bgl_splits = align_indices(bgl_ids, bgl_y, bgl_table)

    results = {"hdfs_v1": {}, "bgl": {}}
    raw_runs = {"hdfs_v1": {}, "bgl": {}}

    for model_name in MODELS:
        hdfs_runs = []
        for seed in SEEDS:
            run = run_model(
                model_name, hdfs_x, hdfs_y,
                hdfs_splits["train"],
                hdfs_splits["validation"],
                hdfs_splits["test"],
                seed,
            )
            hdfs_runs.append(run)
        raw_runs["hdfs_v1"][model_name] = hdfs_runs
        results["hdfs_v1"][model_name] = aggregate(hdfs_runs)

    for model_name in MODELS:
        bgl_runs = []
        for seed in SEEDS:
            run = run_model(
                model_name, bgl_x, bgl_y,
                bgl_splits["train"],
                bgl_splits["validation"],
                bgl_splits["test"],
                seed,
            )
            bgl_runs.append(run)
        raw_runs["bgl"][model_name] = bgl_runs
        results["bgl"][model_name] = aggregate(bgl_runs)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({
            "summary": results,
            "runs": raw_runs,
            "seeds": list(SEEDS),
            "bgl_window_size": args.window_size,
            "protocol_version": protocol["protocol_version"],
            "split_counts": {
                "hdfs_v1": {
                    split: len(indices)
                    for split, indices in hdfs_splits.items()
                },
                "bgl": {
                    split: len(indices)
                    for split, indices in bgl_splits.items()
                },
            },
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Wrote LightAD RQ1 benchmark -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
