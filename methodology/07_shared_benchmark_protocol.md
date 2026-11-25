# Shared evaluation protocol v1

## Status and scope

This protocol is the gate for new comparative runs of LightAD and LogFormer on
HDFS_v1 and BGL. Existing results generated with earlier splits or sample
granularities remain pilot results and must not be mixed into protocol-v1
aggregates.

## Evaluation units and labels

| Dataset | One evaluated sample | Stable sample ID | Label |
|---|---|---|---|
| HDFS_v1 | One block | `BlockId` | Normal/Success = 0; Anomaly/Fail = 1 |
| BGL | 200 consecutive parsed records, non-overlapping | `bgl:<start>:<end>` using zero-based, end-exclusive record offsets | Anomaly if any record in the window is anomalous |

The final incomplete BGL window is discarded. The BGL offsets refer to parsed
records, excluding blank lines, so all methods must consume the same parsed
JSONL and window manifest.

Models may use different feature representations, but a prediction is
comparable only when its `sample_id` and ground-truth label match the shared
protocol table exactly. LogFormer represents each BGL 200-record sample as a
200-step sequence of template embeddings. For HDFS, each sample remains one
block and LogFormer uses up to 20 events from that block; this model input cap
does not change the block-level evaluation unit.

## Splits

- **HDFS_v1:** stratified 80/10/10 split at `BlockId` level, fixed split seed
  42. The same IDs are used for every method and every model seed.
- **BGL:** chronological split of non-overlapping 200-record windows: first
  80% train, next 10% validation, final 10% test. The same ranges are used by
  every method and every model seed.
- Model seeds (`42, 123, 456, 789, 2024`) control model randomness only. They
  do not generate new test sets.
- The generated CSV tables are the source of truth. Input IDs and labels must
  exactly match the tables; missing/unknown IDs, duplicate IDs, or label
  mismatches stop the run.

Generate and inspect the protocol before feature preparation:

```bash
python scripts/shared_benchmark_protocol.py
```

Artifacts:

- `data/splits/benchmark_protocol_v1/hdfs_v1.csv`
- `data/splits/benchmark_protocol_v1/bgl.csv`
- `data/splits/benchmark_protocol_v1/manifest.json`

## Selection and test isolation

- The test split is held out until the configuration is frozen. It is evaluated
  once per final run and is not used to choose thresholds, class weights,
  checkpoints, epochs, or other hyperparameters.
- LightAD decision thresholds are selected by maximum anomaly F1 on validation
  scores; ties prefer higher precision. LogFormer uses the same rule on
  validation anomaly scores.
- LogFormer `pos_weight` is calculated from normal/anomaly counts in the
  training split only. Model architecture and baseline training settings are
  fixed before test evaluation. If a hyperparameter search is later added, its
  candidate selection must use validation only and be recorded in the run
  configuration.
- Report the selected validation threshold and validation/test class
  prevalence with every result.

## Running and interpretation

1. Generate the shared split tables.
2. Prepare LogFormer data using that protocol directory; use the same BGL
   window size of 200.
3. Run LightAD and LogFormer; both runners validate IDs and labels against the
   common tables. Use model seeds only for training randomness.
4. Keep old results under their existing filenames as pilot data. Protocol-v1
   output files use a distinct name and are the only results eligible for a
   new cross-method aggregate.

This aligns sample units, labels, and evaluation sets; it does not make model
feature extraction or training algorithms identical. Any paper-reproduction
claim must separately document deviations from each original paper.
