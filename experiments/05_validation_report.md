# Báo cáo xác minh Tháng 3

## Kết quả sẵn có

- Split HDFS_v1: 460.048 train, 57.506 validation, 57.507 test.
- Không có block overlap giữa ba split.
- Decision Tree, KNN và SLFN đã chạy trên HDFS_v1.
- `LogRAG/adapt_hdfs.py` đã tạo 575.061 HDFS sessions.

## Chưa xác minh

- Không có kết quả gốc đã trích xuất trực tiếp từ PDF trong report để đối
  chiếu ±5% cho LightAD.
- LogFormer chưa có preprocessed NPZ/checkpoint.
- LogRAG chưa có ground-truth BGL, pretrained model hoặc LLM backend.
- Kết quả LightAD gần-perfect cần chạy thêm nhiều seed và kiểm tra leakage
  trước khi coi là reproduction.
