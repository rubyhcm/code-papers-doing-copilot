# Chuẩn bị embedding và checkpoint LogFormer

> Artifact dưới đây được tạo theo pipeline smoke cũ (BGL window 20 và split
> 80/20), không thuộc shared benchmark protocol v1. Không dùng các checkpoint
> hoặc metric này trong so sánh mới.

## Đã hoàn thành

- Cài `sentence-transformers`.
- Tải backbone
  `sentence-transformers/distilbert-base-nli-mean-tokens`.
- Lưu checkpoint SentenceTransformer tại
  `LogFormer/preprocessed_data/sentence_transformer/`.
- Tạo embedding table 768 chiều cho HDFS/BGL templates.
- Tạo smoke HDFS sequence:
  10.000 block, 8.000 train, 2.000 test.
- Tạo full BGL sequence:
  237.398 window 20 dòng, 189.918 train, 47.480 test.
- Sửa `TransformerEncoderLayer.forward` để tương thích Torch 2.15
  `is_causal` argument.
- Smoke forward pass HDFS và BGL đã ra output `(batch, 2)`.

## Artifact

- `LogFormer/preprocessed_data/template_embeddings.npz`
- `LogFormer/preprocessed_data/sentence_transformer/`
- `LogFormer/preprocessed_data/HDFS_training.npz`
- `LogFormer/preprocessed_data/HDFS_testing.npz`
- `LogFormer/preprocessed_data/BGL_training.npz`
- `LogFormer/preprocessed_data/BGL_testing.npz`
- `LogFormer/preprocessed_data/manifest.json`

## Hạn chế

HDFS hiện chỉ là smoke 10.000 block để kiểm tra pipeline. Full HDFS
575.061 block tạo sequence 20×768 float16 cần khoảng 17.7GB thô; script hỗ
trợ `--max-hdfs-blocks 0` nhưng chưa chạy trên máy hạn chế disk/RAM.

Benchmark mới dùng BGL window 200 record và shared split manifest:
`data/splits/benchmark_protocol_v1/`. Cần tạo lại embedding NPZ trước khi
chạy LogFormer theo protocol mới.
