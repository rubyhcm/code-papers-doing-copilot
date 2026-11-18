# Phân loại bất thường trong dữ liệu log

## Anomaly, fault và failure

- **Anomaly:** Sai lệch khỏi hành vi mong đợi; khái niệm được quan sát chủ yếu
  từ dữ liệu.
- **Fault:** Nguyên nhân hoặc trạng thái lỗi tiềm ẩn trong hệ thống.
- **Failure:** Biểu hiện observable khi dịch vụ hoặc chức năng không hoạt động
  đúng.

Ví dụ: một chuỗi event log bất thường có thể là anomaly, memory pressure hoặc
disk fault là fault, timeout phía người dùng là failure.

## Phân loại theo mức ngữ cảnh

| Loại | Định nghĩa | Ví dụ trên log |
|---|---|---|
| Điểm | Một bản ghi hoặc event lệch khỏi phân phối bình thường | Một dòng `FATAL` hiếm |
| Tập thể | Một chuỗi/nhóm hợp lệ riêng lẻ nhưng bất thường khi xem chung | Chuỗi block thất bại |
| Ngữ cảnh | Bản ghi bình thường trong ngữ cảnh này, bất thường trong ngữ cảnh khác | Event đồng thời hoặc lệ thời |

## Phân loại theo supervision

| Hướng | Dữ liệu huấn luyện | Ví dụ trong nghiên cứu |
|---|---|---|
| Giám sát | Có nhãn Normal/Anomaly | LightAD decision tree và SLFN |
| Bán giám sát | Chủ yếu Normal và ít nhãn | LogRAG DeepSVDD + RAG |
| Không giám sát | Không dùng nhãn huấn luyện | KNN hoặc mô hình one-class |

## Tác động tới đánh giá

HDFS_v1 có nhãn ở cấp block, vì vậy anomaly tập thể cần gom theo block trước
khi tính metric. BGL có thể đánh giá ở cấp dòng hoặc cửa sổ thời gian, tùy
ground-truth label được xác nhận.
