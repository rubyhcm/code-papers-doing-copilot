#!/usr/bin/env python3
"""Measure LightAD-style HDFS/BGL training and inference cost."""

from __future__ import annotations

import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_lightad_benchmark import load_bgl, load_hdfs


def peak_rss_mb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS returns bytes; Linux returns KiB.
    if sys.platform == "darwin":
        return usage / (1024 ** 2)
    return usage / 1024


def make_model(name: str, seed: int = 42):
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
    raise ValueError(name)


def hdfs_split(y: np.ndarray, seed: int = 42):
    indices = np.arange(len(y))
    train_idx, temp_idx = train_test_split(
        indices, test_size=0.20, random_state=seed, stratify=y
    )
    val_idx, test_idx = train_test_split(
        temp_idx, test_size=0.50, random_state=seed,
        stratify=y[temp_idx]
    )
    del val_idx
    return train_idx, test_idx


def bgl_split(y: np.ndarray):
    train_end = int(0.8 * len(y))
    val_end = int(0.9 * len(y))
    train_idx = np.arange(train_end)
    test_idx = np.arange(val_end, len(y))
    return train_idx, test_idx


def measure(dataset: str, x: np.ndarray, y: np.ndarray,
            train_idx: np.ndarray, test_idx: np.ndarray) -> dict:
    model_results = {}
    for model_name in ("dt", "knn", "slfn"):
        model = make_model(model_name)

        start = time.perf_counter()
        model.fit(x[train_idx], y[train_idx])
        train_time = time.perf_counter() - start

        start = time.perf_counter()
        predictions = model.predict(x[test_idx])
        infer_time = time.perf_counter() - start
        del predictions

        model_results[model_name] = {
            "train_time_seconds": train_time,
            "inference_time_seconds": infer_time,
            "latency_per_test_sample_ms": (
                infer_time / len(test_idx) * 1000
            ),
            "test_samples": len(test_idx),
        }

    return {
        "dataset": dataset,
        "models": model_results,
        "peak_rss_mb": peak_rss_mb(),
    }


def main() -> int:
    hdfs_x, hdfs_y = load_hdfs(
        ROOT / "data/raw/hdfs_v1/preprocessed/Event_occurrence_matrix.csv"
    )
    hdfs_train, hdfs_test = hdfs_split(hdfs_y)
    hdfs_cost = measure("hdfs_v1", hdfs_x, hdfs_y, hdfs_train, hdfs_test)

    bgl_x, bgl_y = load_bgl(
        ROOT / "data/parsed/bgl_structured.jsonl",
        200,
    )
    bgl_train, bgl_test = bgl_split(bgl_y)
    bgl_cost = measure("bgl", bgl_x, bgl_y, bgl_train, bgl_test)

    result = {"hdfs_v1": hdfs_cost, "bgl": bgl_cost}
    output = ROOT / "results/rq2_lightad_cost.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Wrote RQ2 LightAD cost -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
