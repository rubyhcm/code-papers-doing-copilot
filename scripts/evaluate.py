#!/usr/bin/env python3
"""Unified binary classification metrics for LogAD benchmark outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    precision_recall_fscore_support,
)


def compute_metrics(
    y_true,
    y_pred,
    y_scores: Optional[np.ndarray] = None,
) -> dict:
    y_true = np.asarray(y_true).astype(np.int64)
    y_pred = np.asarray(y_pred).astype(np.int64)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="binary",
        pos_label=1,
        zero_division=0,
    )
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fpr = fp / (fp + tn) if fp + tn else 0.0

    pr_auc = None
    if y_scores is not None:
        y_scores = np.asarray(y_scores)
        if len(np.unique(y_true)) >= 2:
            pr_auc = float(average_precision_score(y_true, y_scores))
        else:
            pr_auc = None

    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "fpr": float(fpr),
        "pr_auc": pr_auc,
        "true_negative": tn,
        "false_positive": fp,
    }


def evaluate_from_file(prediction_path: Path, label_path: Path) -> dict:
    import pandas as pd

    predictions = pd.read_csv(prediction_path)
    labels = pd.read_csv(label_path)
    if len(predictions) != len(labels):
        raise ValueError(
            f"Prediction/label row count mismatch: "
            f"{len(predictions)} != {len(labels)}"
        )
    if "pred" not in predictions.columns:
        raise ValueError("prediction CSV must contain a 'pred' column")

    label_column = "label" if "label" in labels.columns else "Label"
    if label_column not in labels.columns:
        raise ValueError("label CSV must contain 'label' or 'Label'")

    y_true = labels[label_column].replace(
        {"Normal": 0, "Anomaly": 1, "Success": 0, "Fail": 1}
    ).astype(np.int64).to_numpy()
    y_pred = predictions["pred"].to_numpy()
    y_scores = (
        predictions["score"].to_numpy()
        if "score" in predictions.columns
        else None
    )
    return compute_metrics(y_true, y_pred, y_scores)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("labels", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    metrics = evaluate_from_file(args.predictions, args.labels)
    rendered = json.dumps(metrics, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
