# Phân loại họ phương pháp

## Học máy cổ điển

- Khoảng cách: KNN trong LightAD.
- Cây quyết định: Decision Tree trong LightAD.
- Mạng nơ-ron nông: SLFN trong LightAD.
- Điểm mạnh: nhẹ, huấn luyện/suy luận nhanh, dễ giải thích tương đối.
- Hạn chế: phụ thuộc biểu diễn đặc trưng và nhãn.

## Học sâu tuần tự/Transformer

- Sequential: LSTM, các mô hình next-event.
- Attention/Transformer: LogFormer tiền huấn luyện và adapter tuning.
- Điểm mạnh: học quan hệ ngữ cảnh và chuỗi dài.
- Hạn chế: chi phí GPU, phụ thuộc parser và dữ liệu huấn luyện.

## Mô hình ngôn ngữ lớn và RAG

- Prompt/zero-shot hoặc fine-tuned LLM.
- RAG truy xuất ngữ cảnh liên quan rồi yêu cầu mô hình tái đánh giá ứng viên.
- LogRAG: DeepSVDD phát hiện ứng viên, sau đó RAG/LLM tái đánh giá.
- Điểm mạnh: khả năng giải thích và xử lý semantic context.
- Hạn chế: độ trễ, API cost, non-determinism, phụ thuộc retrieval quality.

## Ma trận so sánh

| Phương pháp | Họ | Supervision | Chi phí | Khả năng giải thích |
|---|---|---|---|---|
| LightAD | Classical ML | Giám sát/unsupervised tùy mô hình | Thấp | Cao--trung bình |
| LogFormer | Transformer | Tiền huấn luyện + tinh chỉnh | Trung bình--cao | Trung bình |
| LogRAG | LLM + RAG | Bán giám sát | Cao | Cao, tùy prompt/RAG |
