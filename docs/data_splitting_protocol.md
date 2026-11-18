# Giao thức chia dữ liệu

## HDFS_v1

Đơn vị split là block ID:

- Train: 80%.
- Validation: 10%.
- Test: 10%.
- Stratify theo nhãn block.
- Seed mặc định: 42.
- Không có block overlap giữa các split.

## BGL

Raw `BGL.log` có ground-truth line-level ở cột đầu: `-` là Normal, category
khác `-` là Anomaly. Script đọc JSONL đã parse để gắn nhãn từng dòng, gom
window 200 dòng và gắn window Anomaly nếu chứa ít nhất một dòng alert.

Split phải chronological:

- Train: 80% window đầu.
- Validation: 10% window kế tiếp.
- Test: 10% window cuối.
