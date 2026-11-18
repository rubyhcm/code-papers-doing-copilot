# Review Tháng 3

## Đã hoàn thành

- HDFS_v1 split block stratified 80/10/10, seed 42.
- Xác minh không có overlap block giữa train/validation/test.
- BGL window manifest chronological; line-level label từ cột đầu
  `BGL.log` (`-`=Normal, category khác=Anomaly).
- Unified evaluation script và 3 unit tests.
- LightAD HDFS DT/KNN/SLFN đã chạy.
- HDFS session adapter cho LogRAG đã tạo 575.061 session.
- BGL đã parse lại line-level: 4.399.503 Normal, 348.460 Anomaly.

## Blocked

- Không chạy LogFormer vì thiếu preprocessed NPZ và checkpoint.
- Không chạy LogRAG vì thiếu pretrained model/API hoặc local LLM.
- Chưa chạy benchmark 6 cấu hình LightAD/BGL; pipeline HDFS đã chạy, pipeline
  BGL cần kết nối model và ground-truth window.
- Ground-truth BGL đã xác định từ cột đầu dataset: `-` là Normal,
  category khác `-` là Anomaly.

## Rủi ro kết quả LightAD

Kết quả HDFS gần-perfect cần kiểm tra leakage và chạy lại nhiều seed trước
khi dùng làm bằng chứng paper reproduction.
