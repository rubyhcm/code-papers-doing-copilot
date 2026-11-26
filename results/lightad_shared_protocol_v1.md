# LightAD results — shared benchmark protocol v1

## Source and protocol

The reported values are from the latest Kaggle run in
[`kaggle-lightad-result`](../kaggle-lightad-result/). The machine-readable
source is [`lightad_full_benchmark_results_shared_protocol_v1.json`](../kaggle-lightad-result/lightad_full_benchmark_results_shared_protocol_v1.json)
and the aggregate export is
[`lightad_full_benchmark_results_shared_protocol_v1.csv`](../kaggle-lightad-result/lightad_full_benchmark_results_shared_protocol_v1.csv).
The split definition and counts are in the
[protocol manifest](../kaggle-lightad-result/data/splits/benchmark_protocol_v1/manifest.json).

- Protocol: `shared-benchmark-v1`; five model seeds: 42, 123, 456, 789, 2024.
- HDFS_v1: 575,061 blocks; block-level stratified 80/10/10 split, fixed split
  seed 42. Each model used the same IDs.
- BGL: 4,747,963 parsed records, grouped into non-overlapping chronological
  windows of 200 records. The final 163 records do not form a complete window.
- A window is anomalous if any record in it is anomalous. The split contains
  18,991/2,374/2,374 train/validation/test windows.
- Decision thresholds are selected on validation; test is reserved for final
  evaluation. Metrics below are mean ± sample standard deviation over five
  seeds.

## RQ1 — Detection quality

| Dataset | Model | Precision | Recall | F1 | PR-AUC | FPR |
|---|---|---:|---:|---:|---:|---:|
| HDFS_v1 | DT | 1.000000 ± 0.000000 | 0.999287 ± 0.000266 | 0.999644 ± 0.000133 | 0.999884 ± 0.000258 | 0.000000 ± 0.000000 |
| HDFS_v1 | KNN | 0.998812 ± 0.000000 | 0.998812 ± 0.000000 | 0.998812 ± 0.000000 | 0.997661 ± 0.000000 | 0.000036 ± 0.000000 |
| HDFS_v1 | SLFN | 0.998454 ± 0.000529 | 0.996556 ± 0.000976 | 0.997503 ± 0.000267 | 0.999511 ± 0.000270 | 0.000047 ± 0.000016 |
| BGL | DT | 1.000000 ± 0.000000 | 0.323779 ± 0.001784 | 0.489171 ± 0.002035 | 0.411226 ± 0.001553 | 0.000000 ± 0.000000 |
| BGL | KNN | 0.134134 ± 0.000000 | 0.872964 ± 0.000000 | 0.232538 ± 0.000000 | 0.133522 ± 0.000000 | 0.836962 ± 0.000000 |
| BGL | SLFN | 0.813067 ± 0.111629 | 0.410423 ± 0.017082 | 0.542315 ± 0.012742 | 0.488484 ± 0.013478 | 0.015578 ± 0.011862 |

HDFS scores are near-perfect for all three models. On BGL, SLFN has the
highest mean F1, while DT trades lower recall for perfect precision and zero
observed false positives. KNN has the highest recall but an FPR of about 0.837,
so it produces too many false alarms at the selected operating point.

## RQ2 — Runtime

Times are means across the five runs. Latency is milliseconds per test sample.
Peak memory and hardware details are not present in the new result artifact and
are therefore not reported here.

| Dataset | Model | Train (s) | Inference (s) | Latency/sample (ms) |
|---|---|---:|---:|---:|
| HDFS_v1 | DT | 0.749175 | 0.008536 | 0.000148 |
| HDFS_v1 | KNN | 0.049092 | 57.060846 | 0.992242 |
| HDFS_v1 | SLFN | 10.772229 | 0.015375 | 0.000267 |
| BGL | DT | 1.320483 | 0.001525 | 0.000642 |
| BGL | KNN | 0.011731 | 1.068568 | 0.450113 |
| BGL | SLFN | 8.188049 | 0.003435 | 0.001447 |

## RQ3 — F1/latency trade-off

Using mean F1 (higher is better) and mean per-sample latency (lower is better),
DT dominates the other methods on HDFS_v1. On BGL, DT and SLFN form the
two-point Pareto frontier: DT is faster, while SLFN has higher F1. KNN is
dominated on BGL by both DT and SLFN.

## Interpretation limits

- The BGL anomaly prevalence differs across chronological splits: 11.61% in
  train, 7.33% in validation, and 12.93% in test. This is a property of the
  chronological protocol and should be considered when interpreting the
  metrics.
- The notebook parses the full BGL stream with Drain3 before forming the
  chronological splits. Labels are not used to fit templates, but test log text
  is visible during unsupervised parsing; describe this as transductive
  preprocessing. A strictly inductive evaluation would fit the parser on train
  only and apply it to validation/test.
- Near-perfect HDFS results warrant a documented feature/label leakage audit.
  The scores alone neither prove nor disprove leakage.
- The single-seed `results/lightad_baseline*.json` files are historical local
  baselines; they are not the current five-seed Kaggle aggregate.
- These results complete the LightAD benchmark only. They are not a complete
  comparison against full LogFormer or LogRAG runs and are not, by themselves,
  a reproduction of the source paper.
