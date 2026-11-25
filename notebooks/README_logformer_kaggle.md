# LogFormer full Kaggle training notebook

Notebook: `logformer_kaggle_full_training.ipynb`

## Kaggle setup

1. Add HDFS_v1 and BGL raw/preprocessed files as Kaggle datasets.
2. Enable Internet in Kaggle Notebook settings so the notebook can clone the
   repository into `/kaggle/working/code-papers-doing-copilot`.
3. Enable GPU in Kaggle Notebook settings.
4. Run all cells. On reruns, the notebook fast-forwards the existing clone.

## Required files

- HDFS: `HDFS.log`, `Event_traces.csv`, `HDFS.log_templates.csv`,
  `Event_occurrence_matrix.csv`, `anomaly_label.csv`.
- BGL: `BGL.log`.
- Scripts: `prepare_logformer_embeddings.py`, `parse_logs.py`,
  `shared_benchmark_protocol.py`, `train_logformer_smoke.py`.

## Default full configuration

- Seeds: 42, 123, 456, 789, 2024.
- Epochs: 20.
- HDFS evaluation unit: one block, stratified 80/10/10 split (seed 42).
- BGL evaluation unit: non-overlapping chronological windows of 200 records,
  split 80/10/10.
- Both datasets use the shared split manifest in
  `data/splits/benchmark_protocol_v1/`.
- Threshold is selected on validation; test is reserved for final evaluation.
- LogFormer sequence length: HDFS 20 events per block; BGL 200 embedded records.
- Batch size: 64.
- Learning rate: 1e-5.
- HDFS max blocks: 0 (full).
- BGL: full chronological 200-record windows.

Adjust `SEEDS`, `EPOCHS`, `BATCH_SIZE` and `LEARNING_RATE` in the notebook
configuration cell before training.

## Outputs

- `LogFormer/preprocessed_data/`
- `LogFormer/checkpoints/logformer_full_*_seed*_ep20.pt`
- `LogFormer/checkpoints/logformer_full_*_seed*_ep20.json`
- `logformer_full_results_shared_protocol_v1.json`
