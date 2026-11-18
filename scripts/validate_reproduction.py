#!/usr/bin/env python3
"""Validate available Month 3 result files without inventing paper baselines."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = []

    split_path = root / "data/splits/split_manifest.json"
    if split_path.exists():
        split = json.loads(split_path.read_text(encoding="utf-8"))
        hdfs = split.get("hdfs_v1", {})
        overlap = hdfs.get("overlap", {})
        if overlap and any(overlap.values()):
            errors.append("HDFS block overlap detected")
        total = sum(
            hdfs.get(name, {}).get("blocks", 0)
            for name in ("train", "validation", "test")
        )
        if total != 575061:
            errors.append(f"Unexpected HDFS split block total: {total}")
    else:
        errors.append("Missing data/splits/split_manifest.json")

    lightad_path = root / "results/lightad_baseline_hdfs.json"
    if lightad_path.exists():
        lightad = json.loads(lightad_path.read_text(encoding="utf-8"))
        for model in ("dt", "knn", "slfn"):
            if model not in lightad:
                errors.append(f"Missing LightAD {model} result")
            elif not 0.0 <= lightad[model].get("f1", -1.0) <= 1.0:
                errors.append(f"Invalid LightAD {model} F1")
    else:
        errors.append("Missing LightAD HDFS result")

    if errors:
        print("\n".join(f"FAIL: {error}" for error in errors))
        return 2
    print("PASS: available Month 3 split and LightAD results are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
