# Báo cáo xác minh và trạng thái benchmark

## LightAD: shared benchmark protocol v1 đã chạy trên Kaggle

- HDFS_v1: 460.048 train, 57.506 validation, 57.507 test; split stratified
  theo `BlockId`, seed 42.
- BGL: 18.991 train, 2.374 validation, 2.374 test; cửa sổ chronological 200
  record, 163 record cuối bị loại vì không đủ thành cửa sổ.
- LightAD DT/KNN/SLFN đã chạy đủ năm seed: 42, 123, 456, 789, 2024.
- JSON và CSV aggregate được đối chiếu; số liệu mean/std khớp với 30 lượt
  chạy trong JSON.
- Kết quả chi tiết:
  [`results/lightad_shared_protocol_v1.md`](../results/lightad_shared_protocol_v1.md).
- Tập tin gốc và manifest:
  [`kaggle-lightad-result/`](../kaggle-lightad-result/).
- HDFS F1 nằm trong khoảng 0.9975–0.9996; BGL SLFN đạt F1 cao nhất
  (0.5423), nhưng có biến thiên lớn hơn các mô hình HDFS.
- Giới hạn cần nêu: Drain3 parse toàn bộ BGL trước khi chronological split;
  đây là tiền xử lý transductive. HDFS gần-perfect cần audit leakage trước
  khi kết luận về reproduction.

## Trạng thái các phương pháp khác

- LogFormer mới có weighted 5-epoch smoke (HDFS F1=0.5920; BGL F1=0.2122);
  chưa có kết quả full nhiều seed.
- LogRAG chưa có pretrained model hoặc LLM backend để tạo benchmark đầy đủ.
- Chưa có đối chiếu trực tiếp metric với paper gốc; LightAD benchmark không
  đồng nghĩa đã hoàn tất paper reproduction.

## Giao thức benchmark chung v1

- Sample unit: HDFS theo `BlockId`; BGL theo cửa sổ chronological 200 record,
  không overlap.
- Manifest:
  [`kaggle-lightad-result/data/splits/benchmark_protocol_v1/manifest.json`](../kaggle-lightad-result/data/splits/benchmark_protocol_v1/manifest.json).
- LogFormer prep nhận manifest và tạo riêng train/validation/test;
  kiểm tra integration với dữ liệu tổng hợp đã pass. LogFormer HDFS source
  IDs/labels cũng khớp đủ 575.061 BlockId trong manifest.
- LogFormer chọn threshold bằng validation F1; `pos_weight` lấy từ train.
  Trainer smoke trên NPZ tổng hợp đã xác nhận test không được dùng để chọn
  threshold.
- Full LogFormer embedding/training trên Kaggle vẫn chưa được xác nhận; không
  dùng smoke metric thay cho benchmark full.
