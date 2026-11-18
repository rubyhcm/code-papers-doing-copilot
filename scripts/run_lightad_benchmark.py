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
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.evaluate import compute_metrics


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
    return x_data, y_data


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
                window_counts = Counter()
                window_label = 0

    x_data = np.asarray(x_rows, dtype=np.float32)
    y_data = np.asarray(y_rows, dtype=np.int64)
    return x_data, y_data


def chronological_split(y_data: np.ndarray):
    train_end = int(0.8 * len(y_data))
    val_end = int(0.9 * len(y_data))
    return (
        np.arange(train_end),
        np.arange(train_end, val_end),
        np.arange(val_end, len(y_data)),
    )


def stratified_split(y_data: np.ndarray, seed: int):
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
    return train_idx, val_idx, test_idx


def run_model(
    model_name: str,
    x_data: np.ndarray,
    y_data: np.ndarray,
    train_idx: np.ndarray,
    val_idx: np.ndarray,
    test_idx: np.ndarray,
    seed: int,
) -> dict:
    del val_idx
    model = make_model(model_name, seed)
    start = time.perf_counter()
    model.fit(x_data[train_idx], y_data[train_idx])
    train_time = time.perf_counter() - start

    start = time.perf_counter()
    y_pred = model.predict(x_data[test_idx])
    infer_time = time.perf_counter() - start
    y_scores = None
    if hasattr(model, "predict_proba"):
        y_scores = model.predict_proba(x_data[test_idx])[:, 1]

    metrics = compute_metrics(y_data[test_idx], y_pred, y_scores)
    metrics.update({
        "train_time_seconds": train_time,
        "inference_time_seconds": infer_time,
        "seed": seed,
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
        default=Path("results/rq1_lightad_results.json"),
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=200,
    )
    args = parser.parse_args()

    hdfs_x, hdfs_y = load_hdfs(args.hdfs_matrix)
    bgl_x, bgl_y = load_bgl(args.bgl_jsonl, args.window_size)

    results = {"hdfs_v1": {}, "bgl": {}}
    raw_runs = {"hdfs_v1": {}, "bgl": {}}

    for model_name in MODELS:
        hdfs_runs = []
        for seed in SEEDS:
            train_idx, val_idx, test_idx = stratified_split(hdfs_y, seed)
            run = run_model(
                model_name, hdfs_x, hdfs_y,
                train_idx, val_idx, test_idx, seed,
            )
            hdfs_runs.append(run)
        raw_runs["hdfs_v1"][model_name] = hdfs_runs
        results["hdfs_v1"][model_name] = aggregate(hdfs_runs)

    train_idx, val_idx, test_idx = chronological_split(bgl_y)
    for model_name in MODELS:
        bgl_runs = []
        for seed in SEEDS:
            run = run_model(
                model_name, bgl_x, bgl_y,
                train_idx, val_idx, test_idx, seed,
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
            "bgl_split": "chronological 80/10/10",
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Wrote LightAD RQ1 benchmark -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
