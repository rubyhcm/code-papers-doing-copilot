#!/usr/bin/env python3
"""Run the available LightAD classical models on the HDFS_v1 matrix."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.evaluate import compute_metrics


def load_hdfs_matrix(matrix_path: Path) -> tuple[np.ndarray, np.ndarray]:
    frame = pd.read_csv(matrix_path)
    feature_columns = [f"E{i}" for i in range(1, 30)]
    missing = [column for column in feature_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing HDFS feature columns: {missing}")
    x_data = frame[feature_columns].to_numpy(dtype=np.float32)

    labels = frame["Label"].replace({"Success": 0, "Fail": 1})
    y_data = labels.to_numpy(dtype=np.int64)
    return x_data, y_data


def make_model(name: str):
    if name == "dt":
        return DecisionTreeClassifier(random_state=42)
    if name == "knn":
        return KNeighborsClassifier(n_neighbors=1, n_jobs=-1)
    if name == "slfn":
        return MLPClassifier(
            hidden_layer_sizes=(25,),
            max_iter=300,
            random_state=42,
        )
    raise ValueError(f"Unsupported model: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        choices=("dt", "knn", "slfn"),
        action="append",
        required=True,
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path(
            "data/raw/hdfs_v1/preprocessed/"
            "Event_occurrence_matrix.csv"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/lightad_baseline_hdfs.json"),
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not args.matrix.exists():
        parser.error(f"HDFS matrix not found: {args.matrix}")

    x_data, y_data = load_hdfs_matrix(args.matrix)
    indices = np.arange(len(y_data))
    train_idx, temp_idx = train_test_split(
        indices,
        test_size=0.20,
        random_state=args.seed,
        stratify=y_data,
    )
    val_idx, test_idx = train_test_split(
        temp_idx,
        test_size=0.50,
        random_state=args.seed,
        stratify=y_data[temp_idx],
    )

    results = {}
    if args.output.exists():
        try:
            existing = json.loads(args.output.read_text(encoding="utf-8"))
            if isinstance(existing, dict):
                results.update(existing)
        except json.JSONDecodeError:
            pass
    for model_name in dict.fromkeys(args.model):
        model = make_model(model_name)
        start = time.perf_counter()
        model.fit(x_data[train_idx], y_data[train_idx])
        train_time = time.perf_counter() - start

        start = time.perf_counter()
        y_pred = model.predict(x_data[test_idx])
        infer_time = time.perf_counter() - start

        y_scores = None
        if hasattr(model, "predict_proba"):
            y_scores = model.predict_proba(x_data[test_idx])[:, 1]
        metrics = compute_metrics(
            y_data[test_idx],
            y_pred,
            y_scores,
        )
        metrics.update({
            "train_time_seconds": train_time,
            "inference_time_seconds": infer_time,
            "train_blocks": len(train_idx),
            "validation_blocks": len(val_idx),
            "test_blocks": len(test_idx),
            "seed": args.seed,
        })
        results[model_name] = metrics
        print(model_name, json.dumps(metrics, ensure_ascii=False))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote LightAD HDFS results -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
