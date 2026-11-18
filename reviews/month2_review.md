# Review Tháng 2

## Đã hoàn thành

- Đã hệ thống hóa anomaly/fault/failure, point/collective/contextual và
  supervised/semi-supervised/unsupervised.
- Đã phân loại classical ML, deep learning/Transformer và LLM/RAG.
- Đã tạo hai sơ đồ taxonomy và sơ đồ pipeline thực nghiệm.
- Đã viết bản nháp Chương 2 phần phát hiện bất thường.
- Đã viết bản nháp Chương 3 phương pháp nghiên cứu.
- Đã tạo `environment.yml`, script verification và tài liệu môi trường.
- Đã compile `thesis/thesis_draft_v3.pdf`.

## Trạng thái môi trường

- `.venv312` hoạt động với Python 3.12.16.
- Drain3 0.9.11, PyTorch 2.15.0, Transformers 5.23.0, scikit-learn 1.9.1,
  pandas 3.1.1 và numpy 2.5.5 đã được cài và xác minh.
- PyTorch MPS khả dụng; CUDA không khả dụng trên macOS ARM.
- LightAD, LogFormer và LogRAG đã có dưới dạng thư mục source trong repo.
- Pretrained model LogRAG chưa xác minh.
- Không có conda/micromamba trong PATH; environment.yml đã được chuẩn bị cho
  một môi trường Python độc lập.

## Gate sang Tháng 3

Chưa đạt gate đầy đủ cho chạy baseline vì thiếu ML dependencies và pretrained
model. Có thể tiếp tục chuẩn bị script adapter, splitting/evaluation hoặc hoàn
thiện dữ liệu BGL labels nhưng không nên báo baseline HDFS/LogRAG đã pass.
