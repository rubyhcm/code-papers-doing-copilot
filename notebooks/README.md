# Kaggle notebook

Mở `logad_kaggle_full_benchmark.ipynb` trên Kaggle. Notebook tự clone hoặc
cập nhật code (bật Internet trong Kaggle) từ
`https://github.com/rubyhcm/code-papers-doing-copilot` vào
`/kaggle/working/code-papers-doing-copilot`.

## Dataset trên Kaggle

Add hai dataset vào notebook:

1. HDFS_v1:
   - `HDFS.log`
   - `preprocessed/Event_occurrence_matrix.csv`
   - `preprocessed/anomaly_label.csv`
2. BGL:
   - `BGL.log`

Notebook tự tìm file dữ liệu trong `/kaggle/input`, `/kaggle/working` và
thư mục hiện tại. Chỉ cần add các dataset vào Kaggle; code benchmark được
clone tự động khi chạy notebook.

LightAD và LogFormer dùng chung
`data/splits/benchmark_protocol_v1/`: HDFS theo BlockId, BGL theo cửa sổ
chronological 200 record. Hãy dùng cùng phiên bản repo và cùng dữ liệu đầu vào
cho cả hai notebook; ngưỡng được chọn trên validation, test chỉ đánh giá cuối.

## Output

- `lightad_full_benchmark_results_shared_protocol_v1.json`
- `lightad_full_benchmark_results_shared_protocol_v1.csv`
- `lightad_f1_comparison.png`
- `bgl_structured.csv`

Notebook chỉ chạy LightAD DT/KNN/SLFN. Không tạo kết quả giả cho
LogFormer hoặc LogRAG.
