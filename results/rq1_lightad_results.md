# RQ1 — Kết quả sơ bộ LightAD

## Giao thức

- HDFS_v1: split stratified theo block, seed 42/123/456/789/2024.
- BGL: fixed window 200 dòng, chronological 80/10/10, seed ảnh hưởng mô hình
  ngẫu nhiên nhưng không thay đổi split.
- Metric: Precision, Recall, F1, PR-AUC, FPR.
- PR-AUC/BGL được tính theo predicted probability khi mô hình cung cấp.

## HDFS_v1

| Mô hình | Precision | Recall | F1 | PR-AUC | FPR | Train (s) | Inference (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| DT | 0.997866 ± 0.001154 | 0.999287 ± 0.000497 | 0.998576 ± 0.000823 | 0.998571 ± 0.001233 | 0.000064 ± 0.000035 | 0.290 | 0.006 |
| KNN | 0.998216 ± 0.001184 | 0.995249 ± 0.004241 | 0.996726 ± 0.001948 | 0.993611 ± 0.003753 | 0.000054 ± 0.000036 | 0.050 | 6.153 |
| SLFN | 0.996202 ± 0.001227 | 0.996437 ± 0.002753 | 0.996318 ± 0.001499 | 0.998780 ± 0.001216 | 0.000115 ± 0.000037 | 3.816 | 0.007 |

## BGL

| Mô hình | Precision | Recall | F1 | PR-AUC | FPR | Train (s) | Inference (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| DT | 1.000000 ± 0.000000 | 0.323779 ± 0.001784 | 0.489171 ± 0.002035 | 0.411225 ± 0.001553 | 0.000000 ± 0.000000 | 0.484 | 0.001 |
| KNN | 0.134134 ± 0.000000 | 0.872964 ± 0.000000 | 0.232538 ± 0.000000 | 0.133522 ± 0.000000 | 0.836962 ± 0.000000 | 0.004 | 0.124 |
| SLFN | 0.219295 ± 0.188461 | 0.712052 ± 0.141189 | 0.285299 ± 0.124002 | 0.481332 ± 0.020548 | 0.600000 ± 0.306182 | 1.741 | 0.001 |

## Nhận xét ban đầu

1. LightAD duy trì hiệu quả rất cao trên HDFS_v1 nhưng cần kiểm tra leakage
   và phân phối label trước khi coi đây là kết quả reproduction.
2. BGL khó hơn đáng kể ở mức window 200 dòng.
3. Decision Tree trên BGL có precision cao và FPR bằng 0 nhưng recall thấp.
4. KNN trên BGL có recall cao nhưng quá nhiều false positive.
5. SLFN có biến thiên cao giữa seed; cần thêm phân tích confidence interval
   và nhiều seed trước kết luận.
