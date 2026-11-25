# LogFormer prepared embedding data

## Checkpoint backbone

`sentence_transformer/` contains the downloaded
`sentence-transformers/distilbert-base-nli-mean-tokens` SentenceTransformer
checkpoint, with embedding dimension 768.

## Generated sequence data

- `HDFS_training.npz`, `HDFS_testing.npz`: 10.000 HDFS blocks in smoke dataset,
  8.000 train / 2.000 test, window size 20, float16.
- `BGL_training.npz`, `BGL_testing.npz`: 237.398 BGL full windows, 189.918
  train / 47.480 test, window size 20, float16.
- `template_embeddings.npz`: template embedding table.
- `manifest.json`: provenance and exact shapes.

## Không claim

- Đây chưa phải checkpoint sau huấn luyện LogFormer.
- HDFS smoke dùng 10.000 block, chưa phải full 575.061 block.
- BGL sequence uses full 4.747.963 lines grouped into 20-line windows.
- Need run LogFormer pre-training/tuning before a trained model artifact exists.
