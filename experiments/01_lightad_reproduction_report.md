# Báo cáo tái lập LightAD trên HDFS_v1

## Kịch bản

- Dataset: HDFS_v1.
- Unit: block.
- Feature: 29 cột trong `Event_occurrence_matrix.csv`.
- Split: train 460.048 block, validation 57.506 block, test 57.507 block.
- Seed: 42.
- Phần cứng: macOS ARM, PyTorch MPS khả dụng; bộ baseline scikit-learn chạy CPU.

## Kết quả

| Mô hình | Precision | Recall | F1 | FPR | PR-AUC | Train (s) | Inference (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Decision Tree | 0.999407 | 1.000000 | 0.999703 | 0.000018 | 1.000000 | 0.295 | 0.006 |
| KNN | 0.998813 | 0.999406 | 0.999110 | 0.000036 | 0.998237 | 0.061 | 6.179 |
| SLFN | 0.998216 | 0.997031 | 0.997623 | 0.000054 | 0.999319 | 4.432 | 0.008 |

Kết quả gần-perfect có thể khác baseline gốc do:

- Sử dụng preprocessed 29-event matrix thay cho pipeline parser riêng.
- Cấu hình LightAD trong repository gốc có thể dùng random repeat khác.
- Tệp HDFS.splited đã tồn tại trong repo gốc có thể khác split này.

Kết quả chưa được coi là kết quả paper reproduction cho đến khi:

- đối chiếu lại metric bài báo gốc,
- kiểm tra split cũ/gốc,
- chạy nhiều seed,
- ghi đầy đủ dependency/hardware.
