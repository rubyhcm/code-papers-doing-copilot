# LogFormer prepared embedding data

## Checkpoint backbone

`sentence_transformer/` contains the downloaded
`sentence-transformers/distilbert-base-nli-mean-tokens` SentenceTransformer
checkpoint, with embedding dimension 768.

## Generated sequence data

- `HDFS_training.npz`, `HDFS_validation.npz`, `HDFS_testing.npz`: HDFS block
  sequences aligned to shared benchmark protocol v1 (460,048 / 57,506 / 57,507
  samples), sequence length 20.
- `BGL_training.npz`, `BGL_validation.npz`, `BGL_testing.npz`: chronological
  200-record windows aligned to shared benchmark protocol v1
  (18,991 / 2,374 / 2,374 samples).
- Both datasets store `int32` template IDs rather than copying a 768-dimensional
  vector into every sequence position. ID `0` is padding/unknown; the shared
  `template_embeddings.npz` includes its zero vector, and `DataGenerator` looks
  up vectors as each batch is loaded.
- `manifest.json`: provenance and exact shapes.

## Không claim

- Đây chưa phải checkpoint sau huấn luyện LogFormer.
- Các artifact phải được tạo lại từ input hiện tại để bảo đảm đúng protocol.
- `--max-hdfs-blocks 10000` chỉ dành cho smoke; dùng `0` để xử lý toàn bộ HDFS.
- Need run LogFormer pre-training/tuning before a trained model artifact exists.
