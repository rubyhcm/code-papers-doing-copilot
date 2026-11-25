import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.shared_benchmark_protocol import (
    align_indices,
    build_bgl_table,
    build_hdfs_table,
    select_f1_threshold,
    validate_samples_for_split,
)


class SharedBenchmarkProtocolTests(unittest.TestCase):
    def test_hdfs_split_is_repeatable_and_keeps_block_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            matrix_path = Path(temp_dir) / "matrix.csv"
            pd.DataFrame({
                "BlockId": [f"blk_{i}" for i in range(100)],
                "Label": ["Success"] * 80 + ["Fail"] * 20,
            }).to_csv(matrix_path, index=False)

            first = build_hdfs_table(matrix_path, seed=42)
            second = build_hdfs_table(matrix_path, seed=42)

        pd.testing.assert_frame_equal(first, second)
        self.assertEqual(first["sample_id"].nunique(), 100)
        self.assertEqual(first.groupby("split").size().to_dict(), {
            "test": 10,
            "train": 80,
            "validation": 10,
        })

    def test_bgl_windows_are_chronological_and_drop_incomplete_tail(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            parsed_path = Path(temp_dir) / "bgl.jsonl"
            records = [
                {"label": "Anomaly" if i == 2 else "Normal"}
                for i in range(23)
            ]
            parsed_path.write_text(
                "".join(json.dumps(record) + "\n" for record in records),
                encoding="utf-8",
            )

            table, remainder = build_bgl_table(parsed_path, window_size=10)

        self.assertEqual(remainder, 3)
        self.assertEqual(table["sample_id"].tolist(), [
            "bgl:0:10",
            "bgl:10:20",
        ])
        self.assertEqual(table["label"].tolist(), [1, 0])

    def test_alignment_rejects_label_mismatch(self):
        table = pd.DataFrame({
            "sample_id": ["a", "b", "c"],
            "label": [0, 1, 0],
            "split": ["train", "validation", "test"],
        })
        with self.assertRaisesRegex(ValueError, "Label mismatch"):
            align_indices(["a", "b", "c"], [0, 0, 0], table)

    def test_npz_split_validation_rejects_wrong_partition(self):
        table = pd.DataFrame({
            "sample_id": ["a", "b", "c", "d"],
            "label": [0, 1, 0, 1],
            "split": ["train", "train", "validation", "test"],
        })
        with self.assertRaisesRegex(ValueError, "belongs to validation"):
            validate_samples_for_split(["c"], [0], table, "train")

    def test_threshold_uses_validation_scores(self):
        threshold = select_f1_threshold(
            np.asarray([0, 0, 1, 1]),
            np.asarray([0.1, 0.4, 0.6, 0.9]),
        )
        predictions = np.asarray([0.1, 0.4, 0.6, 0.9]) >= threshold
        np.testing.assert_array_equal(predictions, [False, False, True, True])


if __name__ == "__main__":
    unittest.main()
