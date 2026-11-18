# Giao thức đánh giá thống nhất

## Granularity

- HDFS_v1: metric ở cấp block/session, không ở từng dòng khi label theo block.
- BGL: raw `BGL.log` có alert label line-level ở cột đầu; `-` là Normal,
  category khác `-` là Anomaly.

## Metric

- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 = 2PR / (P + R)
- FPR = FP / (FP + TN)
- PR-AUC = average precision trên predicted scores

## Edge cases

- Không có dự đoán positive: precision/recall/F1 lấy 0 thay vì NaN.
- Không có negative thực tế: FPR lấy 0.
- PR-AUC chỉ tính khi y_true có cả hai lớp.
- Mọi kết quả ghi threshold, seed, model config và hardware.
