# Thiết lập môi trường thực nghiệm

## Môi trường hiện tại

Repository có virtual environment `.venv312/` cho macOS với Python 3.12.16.
Không commit `.venv312/` hoặc credential.

```bash
python3.12 -m venv .venv312
source .venv312/bin/activate
python -m pip install -r requirements.txt
python scripts/verify_environment.py
```

## Ghi nhận khi chạy

- Phiên bản Python.
- Phiên bản PyTorch/Transformers/scikit-learn/pandas/numpy.
- Kiến trúc CPU/GPU.
- CUDA hoặc MPS availability.
- RAM và dung lượng đĩa.
- API key chỉ đặt qua environment variable.

## Trạng thái baseline

Ba thư mục mã nguồn LightAD, LogFormer và LogRAG đã có trong repository.
Pretrained model LogRAG và các phụ thuộc sâu không được ghi là sẵn sàng cho đến
khi script tải model và test import thành công.
