# Review Tháng 4

## Đã hoàn thành

- LightAD DT/KNN/SLFN đã chạy đủ năm seed theo shared benchmark protocol v1.
- HDFS_v1 dùng block-level stratified split 80/10/10, seed 42; BGL dùng
  cửa sổ chronological 200 record, 80/10/10.
- RQ1: precision, recall, F1, PR-AUC và FPR; RQ2: thời gian train/inference
  và latency/mẫu; RQ3: Pareto theo mean F1 và latency.
- JSON/CSV run mới và manifest nằm trong `kaggle-lightad-result/`; báo cáo
  chuẩn là [`results/lightad_shared_protocol_v1.md`](../results/lightad_shared_protocol_v1.md).

## Kết quả chính

- HDFS_v1 F1: DT 0.999644 ± 0.000133; KNN 0.998812 ± 0.000000;
  SLFN 0.997503 ± 0.000267.
- BGL F1: DT 0.489171 ± 0.002035; KNN 0.232538 ± 0.000000;
  SLFN 0.542315 ± 0.012742.
- KNN có inference chậm nhất: 57.061 s trên HDFS_v1 và 1.069 s trên BGL.
- Pareto: DT trội các mô hình còn lại trên HDFS_v1; DT và SLFN nằm trên
  frontier BGL; KNN bị trội trên BGL.

## Chưa hoàn thành

- LogFormer chưa có benchmark full nhiều seed.
- LogRAG chưa có pretrained encoder, local/hosted LLM hoặc API backend.
- Không được kết luận 3 phương pháp so sánh công bằng cho đến khi hai
  baseline còn lại chạy được.

## Ghi nhận bảo vệ

- Kết quả này hoàn tất LightAD protocol v1, nhưng không đồng nghĩa đã tái lập
  paper gốc hoặc hoàn tất so sánh cả ba phương pháp.
- HDFS_v1 gần-perfect cần audit feature/label leakage.
- Drain3 parse toàn bộ BGL trước split; đây là preprocessing transductive.
- Hardware profile và peak RSS không có trong artifact run mới; không dùng
  số đo cũ để mô tả run hiện tại.
