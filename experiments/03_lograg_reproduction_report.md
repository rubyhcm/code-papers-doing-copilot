# Trạng thái tái lập LogRAG

## Trạng thái hiện tại — 2026-11-26

Đã cấu hình đường chạy Kaggle cho **BGL theo shared benchmark protocol v1**
dùng Ollama với Mistral-7B-Instruct-v0.1 Q4_K_M GGUF từ Hugging Face và
embeddings local. Đây mới là cấu hình/runner, không phải kết quả thực nghiệm:
chưa chạy trên Kaggle và chưa có metric LogRAG để đưa vào luận văn.

Các thành phần đã chuẩn bị:

- `notebooks/lograg_kaggle_shared_bgl.ipynb`: notebook cài đặt, preflight và
  chạy benchmark; lần chạy đầy đủ phải được bật rõ ràng.
- `LogRAG/main_shared.py`: huấn luyện trên train, chọn ngưỡng bằng validation,
  đánh giá theo các cửa sổ BGL test trong protocol.
- `LogRAG/shared_benchmark.py`: kiểm tra thứ tự dòng/nhãn và tổng hợp dự đoán
  dòng thành kết quả theo cửa sổ.
- `LogRAG/requirements-kaggle.txt`: dependency set riêng cho Kaggle.
- `LogRAG/tests/test_shared_benchmark.py`: các test căn chỉnh protocol; chưa
  được thực thi trong môi trường làm việc này.

Notebook tải GGUF
`hf.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF:Q4_K_M`, khởi động Ollama,
smoke-test model và dùng `sentence-transformers/all-MiniLM-L6-v2` trên CPU
cho embeddings. Repository gốc
`mistralai/Mistral-7B-Instruct-v0.1` là Safetensors; Ollama dùng GGUF conversion.
Cấu hình này không cần OpenAI API key.
Việc dùng MiniLM thay cho embedding API đã cấu hình trước đó làm thay đổi
retrieval component; phải ghi rõ cấu hình này và không gọi đó là tái lập
nguyên trạng nếu paper/code baseline dùng embedding model khác.

## Điều kiện trước khi chạy Kaggle

1. Người dùng cần commit/push các thay đổi để notebook clone được phiên bản
   chứa runner này.
2. Đính kèm BGL structured CSV đầy đủ, BigLog pretrained model và các file
   `benchmark_protocol_v1` làm Kaggle inputs; bật Internet và GPU.
3. Chạy preflight và smoke test Ollama trước; sau khi xác nhận dữ liệu, GGUF,
   embedding model và tài nguyên Kaggle, mới bật benchmark đầy đủ. Lưu
   `results.json`, dự đoán theo cửa sổ, log chạy và `model_activity.json`.

Notebook mặc định không khởi chạy lần chạy đầy đủ. Đây là cấu hình một seed;
không được mô tả thành kết quả nhiều seed hoặc kết quả hai dataset. Ollama
inference không tính phí API, nhưng tiêu thụ thời gian GPU và dung lượng tải
model trên Kaggle.

## HDFS và giới hạn hiện tại

`LogRAG/adapt_hdfs.py` tạo 575.061 BlockId-level session records dạng JSONL,
nhưng pipeline LogRAG hiện tại chưa đọc định dạng đó theo shared HDFS protocol.
Chưa có HDFS runner, dự đoán hay metric; do đó chưa được tuyên bố LogRAG hoàn
thành trên HDFS hoặc trên cả hai dataset. Xem
`experiments/04_lograg_hdfs_extension.md` và Task 3.7 trong
`ke_hoach_agent_executable.md`.

## Kiểm chứng

Chưa thực thi unit tests, Python compilation, notebook validation hoặc benchmark
Kaggle sau khi chuyển sang Ollama. Cần xác nhận các bước này trước khi dựa vào
runner cho luận văn.

## Kết luận

Không có metric LogRAG nào được báo cáo ở thời điểm này. Kết quả chỉ có thể
được thêm sau khi benchmark chạy thành công, protocol alignment được kiểm tra,
và output được lưu/đối chiếu độc lập.
