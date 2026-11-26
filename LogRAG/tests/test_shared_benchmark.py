import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from shared_benchmark import evaluate_bgl_windows, prepare_bgl_splits


class SharedBGLBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.protocol_dir = self.root / "protocol"
        self.protocol_dir.mkdir()
        self.output_dir = self.root / "splits"
        self.structured_csv = self.root / "bgl.csv"

        labels = [0, 1, 1, 0, 0, 1]
        rows = []
        for window_index, label in enumerate(labels):
            for offset in range(2):
                rows.append({
                    "LineId": window_index * 2 + offset + 1,
                    "Label": "-" if not label else "Anomaly",
                    "Timestamp": window_index * 2 + offset,
                    "Content": f"message {window_index} {offset}",
                    "EventTemplate": f"template {window_index}",
                })
        pd.DataFrame(rows).to_csv(self.structured_csv, index=False)
        table = pd.DataFrame({
            "sample_id": [f"bgl:{i * 2}:{i * 2 + 2}" for i in range(6)],
            "label": labels,
            "start": [i * 2 for i in range(6)],
            "end": [i * 2 + 2 for i in range(6)],
            "split": [
                "train", "train", "validation", "validation", "test", "test"
            ],
        })
        table.to_csv(self.protocol_dir / "bgl.csv", index=False)
        (self.protocol_dir / "manifest.json").write_text(
            json.dumps({"bgl_dropped_incomplete_records": 0}),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_splits_and_window_predictions_match_protocol_ids(self):
        paths = prepare_bgl_splits(
            self.structured_csv,
            self.protocol_dir,
            self.output_dir,
            chunksize=3,
        )
        self.assertEqual(len(pd.read_csv(paths["train"])), 4)
        metrics, predictions = evaluate_bgl_windows(
            paths["test"],
            self.protocol_dir,
            predicted_line_ids=[9, 11],
            split="test",
        )
        self.assertEqual(metrics["samples"], 2)
        self.assertEqual(metrics["precision"], 0.5)
        self.assertEqual(metrics["recall"], 1.0)
        self.assertEqual(predictions["prediction"].tolist(), [1, 1])

    def test_rejects_label_mismatch(self):
        frame = pd.read_csv(self.structured_csv)
        frame.loc[0, "Label"] = "Anomaly"
        frame.to_csv(self.structured_csv, index=False)

        with self.assertRaisesRegex(ValueError, "label mismatch"):
            prepare_bgl_splits(
                self.structured_csv,
                self.protocol_dir,
                self.output_dir,
                chunksize=4,
            )

    def test_rejects_wrong_line_order(self):
        frame = pd.read_csv(self.structured_csv)
        frame.loc[0, "LineId"] = 2
        frame.to_csv(self.structured_csv, index=False)

        with self.assertRaisesRegex(ValueError, "LineId"):
            prepare_bgl_splits(
                self.structured_csv,
                self.protocol_dir,
                self.output_dir,
                chunksize=4,
            )


if __name__ == "__main__":
    unittest.main()
