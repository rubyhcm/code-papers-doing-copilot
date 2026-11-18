# Phần mở rộng HDFS_v1 cho LogRAG

## Đã hoàn thành

- Tạo adapter `LogRAG/adapt_hdfs.py`.
- Gom dữ liệu theo block ID thay vì cửa sổ thời gian.
- Tạo `575.061` HDFS sessions.
- 16.838 session anomaly, tỷ lệ 2.9280%.
- Output: `LogRAG/data/hdfs_sessions.jsonl`.

## Chưa hoàn thành

- Chưa chạy DeepSVDD/RAG vì chưa có:
  - pretrained encoder/model,
  - LLM backend/API/local Mistral,
  - ground-truth line/window cho BGL.
- Chưa có metric RAG trên HDFS_v1.

Adapter này hiện là phần chuỗi dữ liệu sẵn sàng, không phải kết quả benchmark
LogRAG.
