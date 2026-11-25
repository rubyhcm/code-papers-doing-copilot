# RQ1: Báo cáo LightAD sơ bộ

Kết quả RQ1 cho LightAD đã chạy trên HDFS_v1 và BGL. Đây không phải kết quả
cuối cùng cho ba phương pháp; LogFormer và LogRAG chưa có baseline chạy được.

Các result được lưu tại:

- `results/rq1_lightad_results.json`
- `results/rq1_lightad_results.md`
- `thesis/tables/rq1_lightad.tex`

Các file trên là pilot chạy trước shared benchmark protocol v1. Không trộn
chúng với kết quả mới; benchmark mới phải dùng manifest trong
`data/splits/benchmark_protocol_v1/` và output tên
`*_shared_protocol_v1`.

Nêu trong luận văn rằng HDFS_v1 và BGL là hai dataset khác granularity:
HDFS_v1 được split ở cấp block, còn BGL ở fixed window 200 dòng.
