import unittest
import sys
from pathlib import Path

from scripts.evaluate import compute_metrics

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.parse_logs import is_anomaly


class EvaluateTests(unittest.TestCase):
    def test_bgl_alert_category_labels(self):
        self.assertFalse(is_anomaly("-"))
        self.assertTrue(is_anomaly("KERNDTLB"))
        self.assertTrue(is_anomaly("APPSEV"))
        self.assertFalse(is_anomaly("Normal"))
    def test_perfect_binary_result(self):
        metrics = compute_metrics([0, 0, 1, 1], [0, 0, 1, 1],
                                  [0.1, 0.2, 0.8, 0.9])
        self.assertEqual(metrics["precision"], 1.0)
        self.assertEqual(metrics["recall"], 1.0)
        self.assertEqual(metrics["f1"], 1.0)
        self.assertEqual(metrics["fpr"], 0.0)
        self.assertGreater(metrics["pr_auc"], 0.99)

    def test_all_normal_labels(self):
        metrics = compute_metrics([0, 0, 0], [0, 0, 0])
        self.assertEqual(metrics["precision"], 0.0)
        self.assertEqual(metrics["recall"], 0.0)
        self.assertEqual(metrics["f1"], 0.0)
        self.assertEqual(metrics["fpr"], 0.0)
        self.assertIsNone(metrics["pr_auc"])

    def test_false_positive(self):
        metrics = compute_metrics([0, 0, 1], [1, 0, 1])
        self.assertEqual(metrics["false_positive"], 1)
        self.assertEqual(metrics["fpr"], 0.5)


if __name__ == "__main__":
    unittest.main()
