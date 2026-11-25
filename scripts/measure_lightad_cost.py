#!/usr/bin/env python3
"""Measure LightAD-style HDFS/BGL training and inference cost."""

from __future__ import annotations

import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_lightad_benchmark import load_bgl, load_hdfs
from scripts.shared_benchmark_protocol import (
    PROTOCOL_VERSION,
    align_indices,
    load_split_table,
)


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
    protocol_dir = ROOT / "data/splits/benchmark_protocol_v1"
    if not (protocol_dir / "manifest.json").exists():
        raise FileNotFoundError(
            f"Shared protocol missing at {protocol_dir}; "
            "run scripts/shared_benchmark_protocol.py first."
        )
    protocol = json.loads(
        (protocol_dir / "manifest.json").read_text(encoding="utf-8")
    )
    if protocol.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError(
            f"Expected protocol {PROTOCOL_VERSION}, found "
            f"{protocol.get('protocol_version')!r}."
        )
    hdfs_x, hdfs_y, hdfs_ids = load_hdfs(
        ROOT / "data/raw/hdfs_v1/preprocessed/Event_occurrence_matrix.csv"
    )
    hdfs_splits = align_indices(
        hdfs_ids,
        hdfs_y,
        load_split_table(protocol_dir, "hdfs_v1"),
    )
    hdfs_train, hdfs_test = hdfs_splits["train"], hdfs_splits["test"]
    hdfs_cost = measure("hdfs_v1", hdfs_x, hdfs_y, hdfs_train, hdfs_test)

    bgl_x, bgl_y, bgl_ids = load_bgl(
        ROOT / "data/parsed/bgl_structured.jsonl",
        200,
    )
    bgl_splits = align_indices(
        bgl_ids,
        bgl_y,
        load_split_table(protocol_dir, "bgl"),
    )
    bgl_train, bgl_test = bgl_splits["train"], bgl_splits["test"]
    bgl_cost = measure("bgl", bgl_x, bgl_y, bgl_train, bgl_test)

    result = {
        "protocol_version": protocol["protocol_version"],
        "split_counts": {
            "hdfs_v1": {
                split: len(indices) for split, indices in hdfs_splits.items()
            },
            "bgl": {
                split: len(indices) for split, indices in bgl_splits.items()
            },
        },
        "hdfs_v1": hdfs_cost,
        "bgl": bgl_cost,
    }
    output = ROOT / "results/rq2_lightad_cost_shared_protocol_v1.json"
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
