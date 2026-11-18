# Review Tháng 1

## Trạng thái tổng thể

Tháng 1 đã hoàn thành phần tài liệu, dữ liệu và pipeline parsing/statistics.
Các thư mục/chương Tháng 1 thiếu ở đầu phiên làm việc đã được tạo ở bản nháp.

## Đã hoàn thành

- Tóm tắt ba bài báo cốt lõi.
- Tổng quan tài liệu >=30 công trình.
- Mô tả đặc điểm dữ liệu log.
- Checklist ACM SIGSOFT.
- Dataset HDFS_v1 và BGL đã được tải.
- Parser cho HDFS và BGL đã chạy trên dữ liệu full.
- Thống kê dataset đã được đối chiếu bằng cách tính độc lập.
- Câu hỏi nghiên cứu RQ1-RQ4 đã được định nghĩa.
- Bản nháp Chương 1 và Chương 2 phần nền tảng đã được tạo.

## Kết quả kiểm chứng

- HDFS_v1: 11.175.629 dòng, 45 template, 288.250 dòng Anomaly.
- HDFS_v1: 575.061 block, 558.223 Normal và 16.838 Anomaly.
- BGL: 4.747.963 dòng, 844 template.
- BGL raw có ground-truth line-level ở cột đầu: `-` là Normal, category khác
  là Anomaly. Kết quả hiện tại: 348.460 anomaly, 4.399.503 normal.

## Sai lệch cần theo dõi

- Không dùng HDFS_v3 hoặc TraceBench trong benchmark.
- Không coi nhãn HDFS_v1 ở cấp dòng là nhãn độc lập.
- Không suy ra nhãn BGL từ mức `FATAL/WARN`.
- PDF/thesis v1 cần bổ sung template chính thức của trường trước nộp.

## Gate cho Tháng 2

Đạt điều kiện tối thiểu để bắt đầu taxonomy và chuẩn bị môi trường. Phần
Chương 1-2 cần vẫn được cập nhật khi kết quả benchmark thực tế có thay đổi.
