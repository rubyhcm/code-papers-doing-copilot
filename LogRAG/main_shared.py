"""Run LogRAG on the shared BGL 80/10/10 window protocol."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import main as legacy_main
from postprocess import RAG
from shared_benchmark import evaluate_bgl_windows, prepare_bgl_splits


def main() -> int:
    configs = legacy_main.configs
    if not configs.get("protocol_dir"):
        raise ValueError("Set LOGRAG_PROTOCOL_DIR to the shared protocol directory")
    if not configs.get("log_structed_path"):
        raise ValueError("Set LOGRAG_STRUCTURED_CSV to the structured BGL CSV")
    if not Path(configs["encoder_path"]).exists():
        raise FileNotFoundError(
            f"BigLog encoder not found: {configs['encoder_path']}"
        )
    if configs.get("dataset_name") != "BGL":
        raise ValueError("This runner currently supports the BGL protocol only")
    if configs.get("device", "").startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; enable a Kaggle GPU accelerator")

    seed = int(configs.get("seed", 42))
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    output_dir = Path(configs["shared_output_dir"])
    split_dir = output_dir / "input_splits"
    output_dir.mkdir(parents=True, exist_ok=True)
    split_paths = prepare_bgl_splits(
        Path(configs["log_structed_path"]),
        Path(configs["protocol_dir"]),
        split_dir,
    )

    train_csv = split_paths["train"]
    model_path = legacy_main.train_deepsvdd(str(train_csv))
    results = {
        "protocol_version": json.loads(
            (Path(configs["protocol_dir"]) / "manifest.json").read_text(
                encoding="utf-8"
            )
        )["protocol_version"],
        "dataset": "BGL",
        "seed": seed,
        "decision_policy": (
            "DeepSVDD score > 0; RAG retrieval threshold and prompt are fixed "
            "by config.yaml, not selected on test"
        ),
        "splits": {},
    }

    for split in ("validation", "test"):
        split_csv = split_paths[split]
        anomaly_csv, anomaly_line_ids = legacy_main.anomaly_detection(
            model_path,
            str(split_csv),
        )
        model_activity = None
        if configs.get("is_rag", False):
            rag = RAG.RAGPostProcessor(
                configs,
                train_data_path=str(train_csv),
                logger=legacy_main.logger,
            )
            anomaly_line_ids = rag.post_process(
                anomaly_csv,
                str(split_csv),
            )
            model_activity = rag.model_activity

        metrics, predictions = evaluate_bgl_windows(
            split_csv,
            Path(configs["protocol_dir"]),
            anomaly_line_ids,
            split,
        )
        prediction_path = output_dir / f"{split}_window_predictions.csv"
        predictions.to_csv(prediction_path, index=False)
        metrics["predictions_file"] = prediction_path.name
        if model_activity is not None:
            metrics["model_activity"] = model_activity
        results["splits"][split] = metrics

    config_for_record = {
        key: ("***" if key == "api_key" and value else value)
        for key, value in configs.items()
    }
    results["config"] = config_for_record
    results_path = output_dir / "results.json"
    results_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    legacy_main.logger.info("Saved shared-protocol LogRAG results to %s", results_path)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
