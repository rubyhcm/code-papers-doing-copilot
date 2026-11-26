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

## Shared benchmark protocol v1

- HDFS_v1 đánh giá ở cấp block; BGL đánh giá ở cấp cửa sổ chronological 200
  record, không overlap.
- HDFS split stratified 80/10/10 với split seed 42; BGL split theo thứ tự thời
  gian 80/10/10.
- LightAD chạy model seed 42, 123, 456, 789 và 2024. Báo cáo mean ± sample
  standard deviation trên năm seed.
- Ngưỡng được chọn bằng validation; test chỉ dùng cho đánh giá cuối.
- Kết quả và manifest thực tế được lưu ở
  [`kaggle-lightad-result/`](../kaggle-lightad-result/); báo cáo tổng hợp tại
  [`results/lightad_shared_protocol_v1.md`](../results/lightad_shared_protocol_v1.md).

## Edge cases

- Không có dự đoán positive: precision/recall/F1 lấy 0 thay vì NaN.
- Không có negative thực tế: FPR lấy 0.
- PR-AUC chỉ tính khi y_true có cả hai lớp.
- Từng kết quả cần ghi threshold, seed, model config và hardware khi có thể.
- Kaggle result hiện không ghi peak memory và hardware profile đầy đủ; không
  suy luận hoặc so sánh các đại lượng này từ kết quả cũ.
