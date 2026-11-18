# Review Tháng 4

## Đã hoàn thành

- LightAD DT/KNN/SLFN đã benchmark HDFS_v1 và BGL.
- HDFS_v1 chạy 5 seed: 42, 123, 456, 789, 2024.
- BGL fixed window 200 dòng, chronological 80/10/10.
- RQ1: precision, recall, F1, PR-AUC và FPR.
- RQ2: train, inference, latency/test sample và peak RSS.
- RQ3: phân tích Pareto cho LightAD.
- Kết quả được lưu thành JSON, Markdown và LaTeX.

## Kết quả chính

- HDFS_v1: cả ba mô hình LightAD đạt F1 khoảng 0.9963–0.9986.
- BGL: Decision Tree F1 khoảng 0.4892; KNN 0.2325; SLFN 0.2853.
- DT và SLFN inference nhanh trên BGL/HDFS; KNN inference chậm nhất trên
  HDFS_v1.

## Chưa hoàn thành

- LogFormer chưa có preprocessed training/test NPZ và checkpoint.
- LogRAG chưa có pretrained encoder, local/hosted LLM hoặc API backend.
- Không được kết luận 3 phương pháp so sánh công bằng cho đến khi hai
  baseline còn lại chạy được.

## Ghi nhận bảo vệ

- Đây là kết quả sơ bộ của LightAD trong pipeline mới.
- HDFS_v1 gần-perfect cần thêm kiểm tra leakage/seed/duplication.
- BGL được đánh giá theo window và không thể so trực tiếp F1 line-level của
  mọi nghiên cứu nếu giao thức grouping khác.
