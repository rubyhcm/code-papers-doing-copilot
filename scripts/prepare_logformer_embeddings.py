#!/usr/bin/env python3
"""Prepare LogFormer-compatible embeddings and sequence NPZ artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.shared_benchmark_protocol import (
    PROTOCOL_VERSION,
    align_indices,
    load_split_table,
)


SEED = 42
DEFAULT_MODEL = "sentence-transformers/distilbert-base-nli-mean-tokens"


def encode_templates(
    templates: list[str],
    model_name: str,
    output_dir: Path,
) -> tuple[SentenceTransformer, dict[str, np.ndarray]]:
    model = SentenceTransformer(model_name)
    unique_templates = sorted(set(template for template in templates
                                 if isinstance(template, str) and template.strip()))
    embeddings = model.encode(
        unique_templates,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    template_map = {
        template: embedding.astype(np.float16)
        for template, embedding in zip(unique_templates, embeddings)
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    backbone_dir = output_dir / "sentence_transformer"
    model.save(str(backbone_dir))

    np.savez_compressed(
        output_dir / "template_embeddings.npz",
        templates=np.asarray(unique_templates, dtype=object),
        embeddings=embeddings.astype(np.float16),
    )
    return model, template_map


def prepare_hdfs(
    traces_path: Path,
    labels_path: Path,
    templates_path: Path,
    template_map: dict[str, np.ndarray],
    output_dir: Path,
    protocol_dir: Path,
    sequence_length: int,
    max_blocks: int,
) -> dict:
    template_df = pd.read_csv(templates_path)
    event_template_map = dict(zip(template_df["EventId"],
                                  template_df["EventTemplate"]))
    event_template_map = {
        str(event_id): template_map.get(str(template), np.zeros(768, np.float16))
        for event_id, template in event_template_map.items()
    }

    traces = pd.read_csv(traces_path)
    labels = pd.read_csv(labels_path)
    label_by_id = dict(zip(labels["BlockId"], labels["Label"]))

    block_ids = list(dict.fromkeys(traces["BlockId"].tolist()))
    if max_blocks:
        block_ids = block_ids[:max_blocks]

    kept_block_ids = set(block_ids)
    grouped = traces[traces["BlockId"].isin(kept_block_ids)].groupby(
        "BlockId",
        sort=False,
    )

    x_data = []
    y_data = []
    kept_ids = []
    for block_id, block in grouped:
        label = label_by_id.get(block_id)
        if label not in {"Normal", "Anomaly"}:
            continue
        event_ids = re.findall(
            r"\bE\d+\b",
            " ".join(block["Features"].dropna().astype(str).tolist()),
        )
        event_ids = event_ids[:sequence_length]
        sequence = [
            event_template_map.get(event_id, np.zeros(768, np.float16))
            for event_id in event_ids
        ]
        if not sequence:
            continue
        padded = np.zeros((sequence_length, 768), dtype=np.float16)
        padded[:len(sequence)] = np.asarray(sequence, dtype=np.float16)
        x_data.append(padded)
        y_data.append([1, 0] if label == "Normal" else [0, 1])
        kept_ids.append(block_id)

    x_array = np.asarray(x_data, dtype=np.float16)
    y_array = np.asarray(y_data, dtype=np.int64)
    split_table = load_split_table(protocol_dir, "hdfs_v1")
    split_indices = align_indices(
        kept_ids,
        y_array.argmax(axis=1),
        split_table,
        allow_subset=max_blocks > 0,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for split, filename in (
        ("train", "HDFS_training.npz"),
        ("validation", "HDFS_validation.npz"),
        ("test", "HDFS_testing.npz"),
    ):
        path = output_dir / filename
        indices = split_indices[split]
        np.savez_compressed(
            path,
            x=x_array[indices],
            y=y_array[indices],
            sample_ids=np.asarray(kept_ids, dtype=str)[indices],
        )
        paths[split] = str(path)

    return {
        "dataset": "hdfs_v1",
        "blocks": len(y_array),
        "split_blocks": {
            split: int(len(indices))
            for split, indices in split_indices.items()
        },
        "x_shape": list(x_array.shape),
        "y_shape": list(y_array.shape),
        "dtype": "float16",
        "anomaly_blocks": int(y_array[:, 1].sum()),
        "split_paths": paths,
        "sequence_length": sequence_length,
        "split_protocol": str(protocol_dir.resolve()),
        "full_requested": max_blocks == 0,
    }


def prepare_bgl(
    parsed_path: Path,
    template_map: dict[str, np.ndarray],
    output_dir: Path,
    protocol_dir: Path,
    window_size: int,
) -> dict:
    records = pd.read_json(parsed_path, lines=True)
    template_sequences = []
    labels = []
    sample_ids = []

    for start in range(0, len(records) - window_size + 1, window_size):
        window = records.iloc[start:start + window_size]
        vectors = []
        for template in window["template"].tolist():
            vectors.append(template_map.get(template, np.zeros(768, np.float16)))
        padded = np.zeros((window_size, 768), dtype=np.float16)
        padded[:len(vectors)] = np.asarray(vectors, dtype=np.float16)
        template_sequences.append(padded)
        labels.append(
            [1, 0] if not (window["label"] == "Anomaly").any()
            else [0, 1]
        )
        sample_ids.append(f"bgl:{start}:{start + window_size}")

    x_array = np.asarray(template_sequences, dtype=np.float16)
    y_array = np.asarray(labels, dtype=np.int64)
    split_table = load_split_table(protocol_dir, "bgl")
    split_indices = align_indices(
        sample_ids,
        y_array.argmax(axis=1),
        split_table,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for split, filename in (
        ("train", "BGL_training.npz"),
        ("validation", "BGL_validation.npz"),
        ("test", "BGL_testing.npz"),
    ):
        path = output_dir / filename
        indices = split_indices[split]
        np.savez_compressed(
            path,
            x=x_array[indices],
            y=y_array[indices],
            sample_ids=np.asarray(sample_ids, dtype=str)[indices],
        )
        paths[split] = str(path)

    return {
        "dataset": "bgl",
        "windows": len(y_array),
        "split_windows": {
            split: int(len(indices))
            for split, indices in split_indices.items()
        },
        "x_shape": list(x_array.shape),
        "y_shape": list(y_array.shape),
        "dtype": "float16",
        "anomaly_windows": int(y_array[:, 1].sum()),
        "split_paths": paths,
        "window_size": window_size,
        "split_protocol": str(protocol_dir.resolve()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--hdfs-traces", type=Path,
                        default=Path("data/raw/hdfs_v1/preprocessed/Event_traces.csv"))
    parser.add_argument("--hdfs-labels", type=Path,
                        default=Path("data/raw/hdfs_v1/preprocessed/anomaly_label.csv"))
    parser.add_argument("--hdfs-templates", type=Path,
                        default=Path("data/raw/hdfs_v1/preprocessed/HDFS.log_templates.csv"))
    parser.add_argument("--bgl-jsonl", type=Path,
                        default=Path("data/parsed/bgl_structured.jsonl"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("LogFormer/preprocessed_data"))
    parser.add_argument("--protocol-dir", type=Path,
                        default=Path("data/splits/benchmark_protocol_v1"))
    parser.add_argument("--hdfs-sequence-length", type=int, default=20)
    parser.add_argument("--bgl-window-size", type=int, default=200)
    parser.add_argument("--max-hdfs-blocks", type=int, default=10000,
                        help="0 means all HDFS blocks; default is 10,000 for smoke tests")
    args = parser.parse_args()

    if not (args.protocol_dir / "manifest.json").exists():
        parser.error(
            f"Shared benchmark protocol not found in {args.protocol_dir}; "
            "run scripts/shared_benchmark_protocol.py first."
        )
    protocol_manifest = json.loads(
        (args.protocol_dir / "manifest.json").read_text(encoding="utf-8")
    )
    if protocol_manifest.get("protocol_version") != PROTOCOL_VERSION:
        parser.error(
            f"Expected protocol {PROTOCOL_VERSION}, found "
            f"{protocol_manifest.get('protocol_version')!r}."
        )

    templates = []
    hdfs_template_df = pd.read_csv(args.hdfs_templates)
    templates.extend(hdfs_template_df["EventTemplate"].tolist())
    if args.bgl_jsonl.exists():
        bgl_records = pd.read_json(args.bgl_jsonl, lines=True)
        templates.extend(bgl_records["template"].drop_duplicates().tolist())

    model, template_map = encode_templates(
        templates,
        args.model,
        args.output_dir,
    )

    hdfs_summary = None
    if args.hdfs_traces.exists() and args.hdfs_labels.exists():
        hdfs_summary = prepare_hdfs(
            args.hdfs_traces,
            args.hdfs_labels,
            args.hdfs_templates,
            template_map,
            args.output_dir,
            args.protocol_dir,
            args.hdfs_sequence_length,
            args.max_hdfs_blocks,
        )

    bgl_summary = None
    if args.bgl_jsonl.exists():
        bgl_summary = prepare_bgl(
            args.bgl_jsonl,
            template_map,
            args.output_dir,
            args.protocol_dir,
            args.bgl_window_size,
        )

    manifest = {
        "model": args.model,
        "embedding_dim": model.get_embedding_dimension(),
        "checkpoint": str(args.output_dir / "sentence_transformer"),
        "template_embeddings": str(args.output_dir / "template_embeddings.npz"),
        "protocol_version": protocol_manifest["protocol_version"],
        "protocol_dir": str(args.protocol_dir.resolve()),
        "hdfs_sequence_length": args.hdfs_sequence_length,
        "bgl_window_size": args.bgl_window_size,
        "hdfs": hdfs_summary,
        "bgl": bgl_summary,
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
