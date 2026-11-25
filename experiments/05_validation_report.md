# Báo cáo xác minh Tháng 3

## Kết quả sẵn có

- Split HDFS_v1: 460.048 train, 57.506 validation, 57.507 test.
- Không có block overlap giữa ba split.
- Decision Tree, KNN và SLFN đã chạy trên HDFS_v1.
- `LogRAG/adapt_hdfs.py` đã tạo 575.061 HDFS sessions.
- LogFormer đã có SentenceTransformer backbone 768 chiều, HDFS/BGL
  preprocessed NPZ và smoke checkpoint.
- Smoke weighted 5 epoch:
  HDFS F1=0.5920; BGL F1=0.2122.

## Chưa xác minh

- Không có kết quả gốc đã trích xuất trực tiếp từ PDF trong report để đối
  chiếu ±5% cho LightAD.
- LogFormer chưa có kết quả full HDFS/BGL nhiều seed; smoke 5 epoch chưa
  phải baseline reproduction.
- LogRAG chưa có pretrained model hoặc LLM backend.
- Kết quả LightAD gần-perfect cần chạy thêm nhiều seed và kiểm tra leakage
  trước khi coi là reproduction.

## Giao thức benchmark chung v1

- Đã chốt sample unit: HDFS theo `BlockId`; BGL theo cửa sổ chronological
  200 record, không overlap.
- Đã sinh `data/splits/benchmark_protocol_v1/`: HDFS stratified 80/10/10
  (seed 42), BGL chronological 80/10/10. BGL bỏ 163 record cuối không đủ
  tạo cửa sổ 200 record.
- Đã xác minh toàn bộ LightAD inputs khớp manifest: HDFS 575.061 block,
  BGL 23.739 cửa sổ; cả IDs và labels đều khớp.
- LogFormer prep giờ nhận manifest và tạo riêng train/validation/test;
  kiểm tra integration với dữ liệu tổng hợp đã pass. LogFormer HDFS source
  IDs/labels cũng khớp đủ 575.061 BlockId trong manifest.
- LogFormer chọn threshold bằng validation F1; `pos_weight` lấy từ train.
  Trainer smoke trên NPZ tổng hợp đã xác nhận test không được dùng để chọn
  threshold.
- Chưa chạy full embedding/preparation và full training trên Kaggle. Do đó
  protocol v1 đã được tạo và kiểm tra ID/label, nhưng kết quả cũ vẫn là pilot;
  cần chạy smoke thực tế trước benchmark chính.
