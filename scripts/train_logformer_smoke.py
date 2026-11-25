#!/usr/bin/env python3
"""Run a bounded one-epoch LogFormer smoke training on prepared NPZ data."""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import precision_recall_fscore_support
from torch.utils.data import DataLoader


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "LogFormer"))

from dataloader import DataGenerator
from model import Model
from scripts.shared_benchmark_protocol import (
    PROTOCOL_VERSION,
    load_split_table,
    select_f1_threshold,
    validate_samples_for_split,
)


def resolve_device(requested: str) -> torch.device:
    if requested == "mps" and torch.backends.mps.is_available():
        return torch.device("mps")
    if requested == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=("HDFS", "BGL"), default="HDFS")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--window-size", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-train-samples", type=int, default=10000)
    parser.add_argument("--pos-weight", type=float, default=None,
                        help="Positive-class weight; default is automatic.")
    parser.add_argument("--device", choices=("auto", "cpu", "mps", "cuda"),
                        default="auto")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--preprocessed-dir",
        type=Path,
        default=None,
        help="Directory containing HDFS/BGL *_training.npz artifacts.",
    )
    args = parser.parse_args()

    if args.output is None:
        args.output = (
            ROOT / "LogFormer/checkpoints"
            / f"logformer_smoke_{args.dataset.lower()}_seed{args.seed}_ep{args.epochs}.pt"
        )
    if args.preprocessed_dir is None:
        preprocessed_dir = ROOT / "LogFormer/preprocessed_data"
    else:
        preprocessed_dir = args.preprocessed_dir.resolve()
    if not args.output.is_absolute():
        args.output = (ROOT / args.output).resolve()

    if args.epochs < 1:
        parser.error("--epochs must be at least 1")

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    if args.device == "auto":
        requested = "mps" if torch.backends.mps.is_available() else "cpu"
    else:
        requested = args.device
    device = resolve_device(requested)

    train_path = preprocessed_dir / f"{args.dataset}_training.npz"
    validation_path = preprocessed_dir / f"{args.dataset}_validation.npz"
    test_path = preprocessed_dir / f"{args.dataset}_testing.npz"
    if not train_path.exists() or not validation_path.exists() or not test_path.exists():
        parser.error(
            "Missing prepared train/validation/test data. "
            "Run scripts/shared_benchmark_protocol.py, then "
            "scripts/prepare_logformer_embeddings.py."
        )
    prepared_manifest_path = preprocessed_dir / "manifest.json"
    if not prepared_manifest_path.exists():
        parser.error(f"Prepared data manifest not found: {prepared_manifest_path}")
    prepared_manifest = json.loads(
        prepared_manifest_path.read_text(encoding="utf-8")
    )
    if prepared_manifest.get("protocol_version") != PROTOCOL_VERSION:
        parser.error(
            f"Prepared data must use {PROTOCOL_VERSION}; found "
            f"{prepared_manifest.get('protocol_version')!r}."
        )
    protocol_dir = Path(prepared_manifest["protocol_dir"])
    dataset_key = "hdfs_v1" if args.dataset == "HDFS" else "bgl"
    split_table = load_split_table(protocol_dir, dataset_key)

    with np.load(train_path, allow_pickle=True) as train_data:
        x_train = train_data["x"]
        y_train = train_data["y"]
        train_ids = train_data["sample_ids"].astype(str)
    with np.load(validation_path, allow_pickle=True) as validation_data:
        x_validation = validation_data["x"]
        y_validation = validation_data["y"]
        validation_ids = validation_data["sample_ids"].astype(str)
    with np.load(test_path, allow_pickle=True) as test_data:
        x_test = test_data["x"]
        y_test = test_data["y"]
        test_ids = test_data["sample_ids"].astype(str)

    validate_samples_for_split(
        train_ids, y_train.argmax(axis=1), split_table, "train"
    )
    validate_samples_for_split(
        validation_ids, y_validation.argmax(axis=1), split_table, "validation"
    )
    validate_samples_for_split(
        test_ids, y_test.argmax(axis=1), split_table, "test"
    )
    if args.window_size != (
        prepared_manifest["hdfs_sequence_length"]
        if args.dataset == "HDFS"
        else prepared_manifest["bgl_window_size"]
    ):
        parser.error(
            "--window-size does not match the prepared dataset sequence length"
        )

    if args.max_train_samples > 0:
        x_train = x_train[:args.max_train_samples]
        y_train = y_train[:args.max_train_samples]

    train_loader = DataLoader(
        DataGenerator(x_train, y_train, args.window_size),
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
    )
    validation_loader = DataLoader(
        DataGenerator(x_validation, y_validation, args.window_size),
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
    )
    test_loader = DataLoader(
        DataGenerator(x_test, y_test, args.window_size),
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
    )

    model = Model(
        mode="adapter",
        num_layers=1,
        adapter_size=64,
        dim=768,
        window_size=args.window_size,
        nhead=8,
        dim_feedforward=3072,
        dropout=0.1,
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    normal_count = int(y_train[:, 0].sum())
    anomaly_count = int(y_train[:, 1].sum())
    if not normal_count or not anomaly_count:
        raise ValueError(
            "Training split must contain both normal and anomalous samples"
        )
    if args.pos_weight is None:
        pos_weight_value = normal_count / anomaly_count
    else:
        pos_weight_value = args.pos_weight
    pos_weight = torch.tensor(
        [1.0, pos_weight_value],
        dtype=torch.float32,
        device=device,
    )
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    print(
        f"Class counts: normal={normal_count}, anomaly={anomaly_count}, "
        f"train-derived pos_weight={pos_weight_value:.4f}"
    )

    history = []
    model.train()
    start_time = time.perf_counter()
    for epoch in range(args.epochs):
        epoch_loss = 0.0
        epoch_true = []
        epoch_pred = []
        for x_batch, y_batch in train_loader:
            x_batch = x_batch.to(device=device, dtype=torch.float32)
            y_batch = y_batch.to(device=device, dtype=torch.float32)
            optimizer.zero_grad(set_to_none=True)
            output = model(x_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
            optimizer.step()

            epoch_loss += loss.item()
            epoch_true.extend(torch.argmax(y_batch, dim=1).cpu().tolist())
            anomaly_prob = torch.sigmoid(output[:, 1])
            epoch_pred.extend(
                (anomaly_prob >= 0.5).long().cpu().tolist()
            )

        precision, recall, f1, _ = precision_recall_fscore_support(
            epoch_true,
            epoch_pred,
            average="binary",
            zero_division=0,
        )
        history.append({
            "epoch": epoch + 1,
            "loss": epoch_loss / len(train_loader),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
        })
        print(f"Epoch {epoch + 1}/{args.epochs}: "
              f"loss={history[-1]['loss']:.6f}")

    model.eval()

    def collect_predictions(loader):
        labels = []
        scores = []
        with torch.no_grad():
            for x_batch, y_batch in loader:
                x_batch = x_batch.to(device=device, dtype=torch.float32)
                output = model(x_batch)
                labels.extend(torch.argmax(y_batch, dim=1).cpu().tolist())
                scores.extend(torch.sigmoid(output[:, 1]).cpu().tolist())
        return np.asarray(labels, dtype=np.int64), np.asarray(scores, dtype=np.float64)

    validation_true, validation_scores = collect_predictions(validation_loader)
    threshold = select_f1_threshold(validation_true, validation_scores)
    validation_pred = (validation_scores >= threshold).astype(np.int64)
    validation_precision, validation_recall, validation_f1, _ = (
        precision_recall_fscore_support(
            validation_true,
            validation_pred,
            average="binary",
            zero_division=0,
        )
    )
    test_true, test_scores = collect_predictions(test_loader)
    test_pred = (test_scores >= threshold).astype(np.int64)

    precision, recall, f1, _ = precision_recall_fscore_support(
        test_true,
        test_pred,
        average="binary",
        zero_division=0,
    )
    positive_predictions = int(sum(test_pred))
    elapsed = time.perf_counter() - start_time
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "model_state_dict": model.state_dict(),
        "dataset": args.dataset,
        "protocol_version": PROTOCOL_VERSION,
        "seed": args.seed,
        "epochs": args.epochs,
        "window_size": args.window_size,
        "embedding_dim": 768,
        "pos_weight": pos_weight_value,
        "threshold": threshold,
        "threshold_selection": "validation F1; ties prefer precision",
    }, args.output)

    result = {
        "dataset": args.dataset,
        "protocol_version": PROTOCOL_VERSION,
        "device": str(device),
        "seed": args.seed,
        "epochs": args.epochs,
        "window_size": args.window_size,
        "batch_size": args.batch_size,
        "learning_rate": args.lr,
        "max_train_samples": args.max_train_samples,
        "pos_weight": pos_weight_value,
        "threshold": threshold,
        "threshold_selection": "validation F1; ties prefer precision",
        "train_samples": len(x_train),
        "validation_samples": len(x_validation),
        "test_samples": len(x_test),
        "elapsed_seconds": elapsed,
        "history": history,
        "validation": {
            "selected_threshold": threshold,
            "precision": float(validation_precision),
            "recall": float(validation_recall),
            "f1": float(validation_f1),
        },
        "class_counts": {
            "train_normal": normal_count,
            "train_anomaly": anomaly_count,
            "validation_anomaly": int(validation_true.sum()),
            "test_anomaly": int(test_true.sum()),
        },
        "test": {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "positive_predictions": positive_predictions,
            "true_positive": int(sum(
                1 for truth, pred in zip(test_true, test_pred)
                if truth == 1 and pred == 1
            )),
            "true_normal": int(sum(
                1 for truth, pred in zip(test_true, test_pred)
                if truth == 0 and pred == 0
            )),
        },
        "checkpoint": str(args.output),
    }
    report_path = args.output.with_suffix(".json")
    report_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Saved checkpoint: {args.output}")
    print(f"Saved report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
