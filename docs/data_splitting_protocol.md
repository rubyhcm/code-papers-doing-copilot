# Giao thức chia dữ liệu

## HDFS_v1

Đơn vị split là block ID:

- Train: 80%.
- Validation: 10%.
- Test: 10%.
- Stratify theo nhãn block.
- Seed mặc định: 42.
- Không có block overlap giữa các split.

Trong shared benchmark protocol v1, số lượng là 460.048 train, 57.506
validation và 57.507 test (13.470/1.684/1.684 anomaly).

## BGL

Raw `BGL.log` có ground-truth line-level ở cột đầu: `-` là Normal, category
khác `-` là Anomaly. Script đọc JSONL đã parse để gắn nhãn từng dòng, gom
window 200 dòng và gắn window Anomaly nếu chứa ít nhất một dòng alert.

Split phải chronological:

- Train: 80% window đầu.
- Validation: 10% window kế tiếp.
- Test: 10% window cuối.

Shared benchmark protocol v1 dùng 23.739 cửa sổ: 18.991 train, 2.374
validation và 2.374 test. Có 163 record cuối không đủ tạo một cửa sổ hoàn
chỉnh và không được đưa vào đánh giá. Số anomaly lần lượt là 2.205, 174 và
307; vì split chronological, prevalence có thể khác nhau giữa các đoạn.
