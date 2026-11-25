# LogFormer weighted smoke training

## HDFS_v1

- Data: 10.000 block, 8.000 train / 2.000 test.
- Epoch: 5.
- Device: MPS.
- Positive weight: 22.6686.
- Threshold anomaly: 0.50.
- Test: precision 0.9250, recall 0.4353, F1 0.5920.
- Positive predictions: 40; true positives: 37.
- Loss giảm từ 0.182454 đến 0.161278.

Checkpoint:
`LogFormer/checkpoints/logformer_smoke_hdfs_ep5.pt`

## BGL

- Data: 10.000 train / 47.480 test window smoke.
- Epoch: 5.
- Device: MPS.
- Positive weight: 17.7266.
- Threshold anomaly: 0.50.
- Test: precision 0.1187, recall 0.9963, F1 0.2122.
- Positive predictions: 25.265; true positives: 3.000.
- Loss giảm từ 0.783159 đến 0.748270.

Checkpoint:
`LogFormer/checkpoints/logformer_smoke_bgl_ep5.pt`

## Hạn chế

- HDFS smoke chỉ dùng 10.000 block; không phải full 575.061 block.
- BGL smoke train chỉ dùng 10.000 window, test dùng 47.480 window.
- Positive weight được tính từ class prevalence, chưa tune validation.
- Mỗi dataset chỉ chạy seed 42, chưa chạy 5 seed.
- Không coi F1/precision/recall này là kết quả final LogFormer.
