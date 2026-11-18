# Trạng thái tái lập LogFormer

## Đã xác minh

- Mã nguồn LogFormer import thành công trong `.venv312`.
- PyTorch 2.15.0 khả dụng.
- DataGenerator và Model import và khởi tạo được.

## Blocker

- Không có `LogFormer/preprocessed_data/*_training.npz` hoặc
  `*_testing.npz`.
- Script dùng CUDA và `torch.nn.DataParallel` cứng, không sẵn cho MPS.
- Chưa có pretrained checkpoints trong repository.
- Chưa có adapter HDFS/BGL tạo theo split thống nhất.

Không report metric giả. Baseline LogFormer sẽ được chạy sau khi tạo dữ
liệu embedding sequence và chuyển device model sang MPS/CPU.
