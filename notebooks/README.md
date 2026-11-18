# Kaggle notebook

Mở `logad_kaggle_full_benchmark.ipynb` trên Kaggle.

## Dataset trên Kaggle

Add hai dataset vào notebook:

1. HDFS_v1:
   - `HDFS.log`
   - `preprocessed/Event_occurrence_matrix.csv`
   - `preprocessed/anomaly_label.csv`
2. BGL:
   - `BGL.log`

Notebook tự tìm file trong `/kaggle/input`, `/kaggle/working` và thư mục
repo cục bộ.

## Output

- `lightad_full_benchmark_results.json`
- `lightad_full_benchmark_results.csv`
- `lightad_f1_comparison.png`
- `bgl_structured.csv`

Notebook chỉ chạy LightAD DT/KNN/SLFN. Không tạo kết quả giả cho
LogFormer hoặc LogRAG.
