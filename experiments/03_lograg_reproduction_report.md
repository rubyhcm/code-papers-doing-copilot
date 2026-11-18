# Trạng thái tái lập LogRAG

## Đã xác minh

- Mã nguồn LogRAG đã có trong repository.
- Cài một phần dependency RAG để kiểm tra import.
- PyTorch 2.15.0 khả dụng; macOS dùng MPS thay cho CUDA.

## Blocker

- BGL raw có ground-truth line-level ở cột đầu: `-` là Normal, category khác
  là Anomaly.
- Không có pretrained BigLog/model trong `LogRAG/pretrained/`.
- Không có API key hợp lệ cho OpenAI.
- Không có local Mistral model.
- Environment gặp xung đột NumPy/SciPy sau khi thêm LangChain phiên bản
  0.2.14; cần environment RAG tách biệt trước benchmark chính.

Không report metric LogRAG cho đến khi có:

- ground-truth BGL,
- model embedding,
- llm backend,
- split thống nhất.
