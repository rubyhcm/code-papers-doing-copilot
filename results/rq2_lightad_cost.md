# RQ2 — Chi phí tính toán LightAD

## HDFS_v1

| Mô hình | Train (s) | Inference (s) | Latency/test sample (ms) | Peak RSS quá trình (MB) |
|---|---:|---:|---:|---:|
| DT | 0.307698 | 0.006858 | 0.000119 | 713.484375 |
| KNN | 0.048526 | 6.288217 | 0.109347 | 713.484375 |
| SLFN | 4.417464 | 0.007635 | 0.000133 | 713.484375 |

## BGL

| Mô hình | Train (s) | Inference (s) | Latency/test sample (ms) | Peak RSS quá trình (MB) |
|---|---:|---:|---:|---:|
| DT | 0.469191 | 0.001158 | 0.000488 | 787.484375 |
| KNN | 0.003962 | 0.122019 | 0.051398 | 787.484375 |
| SLFN | 2.052090 | 0.000874 | 0.000368 | 787.484375 |

Peak RSS được đo bằng `resource.getrusage` của một process đo cả tải
HDFS và BGL. Thời gian là một lần đo trên seed 42, chưa báo mean/std RQ2.
