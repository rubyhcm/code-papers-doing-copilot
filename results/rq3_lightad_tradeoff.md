# RQ3 — Đánh đổi hiệu quả và chi phí LightAD

| Dataset | Mô hình | F1 | Latency/test sample (ms) | Train (s) | Pareto |
|---|---|---:|---:|---:|---|
| hdfs_v1 | DT | 0.998576 | 0.000119 | 0.307698 | Có |
| hdfs_v1 | KNN | 0.996726 | 0.109347 | 0.048526 | Có |
| hdfs_v1 | SLFN | 0.996318 | 0.000133 | 4.417464 | Không |
| bgl | DT | 0.489171 | 0.000488 | 0.469191 | Có |
| bgl | KNN | 0.232538 | 0.051398 | 0.003962 | Có |
| bgl | SLFN | 0.285299 | 0.000368 | 2.052090 | Có |

Ghi chú:
- Pareto dùng cùng ba trục: F1 lớn hơn tốt, latency nhỏ hơn tốt
  và training time nhỏ hơn tốt.
- Đây là phân tích chi phí của LightAD, chưa so sánh LogFormer/LogRAG.
