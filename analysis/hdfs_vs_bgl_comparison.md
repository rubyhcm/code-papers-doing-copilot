# HDFS_v1 và BGL

## Trạng thái dữ liệu hiện tại

Thư mục `data/raw/hdfs_v1/` hiện chứa:

- `HDFS.log`: 11,175,629 dòng log thô.
- `README.md`: mô tả dataset HDFS_v1.

Các nhãn block không nằm trong thư mục này. Repository hiện chứa
`data/raw/hdfs_v1/preprocessed/anomaly_label.csv`, gồm 575,061 nhãn
`BlockId,Label` với giá trị `Normal` hoặc `Anomaly`.

Thư mục HDFS_v1 không còn chứa TraceBench hoặc trace CSV.

| Thuộc tính | HDFS_v1 | BGL |
|---|---|---|
| Hệ thống | Hadoop Distributed File System | BlueGene/L supercomputer |
| Kiểu dữ liệu | 11,175,629 dòng log thô | Log thô hoặc CSV đã parse Drain |
| Đơn vị nhãn | Block/session | Dòng log hoặc cửa sổ thời gian |
| Nhãn hiện có | CSV `BlockId,Label` trong LightAD | Cột `Label` hoặc alert/thời gian tùy phiên bản |
| Nhóm dữ liệu | Theo block ID xuất hiện trong message | Theo timestamp/window hoặc line |
| Nguy cơ chính | Rò rỉ giữa các dòng cùng block | Trôi thời gian và nhãn alert |
| Chiến lược chia | Chia theo block; không random split dòng | Chia theo thời gian; không random shuffle |

## Kiểm tra trạng thái nhãn thực tế

- HDFS_v1 đã truyền nhãn thành công cho 11.175.629 dòng:
  10.887.379 dòng `Normal` và 288.250 dòng `Anomaly`.
- Tất cả 575.061 block trong file nhãn đều xuất hiện trong `HDFS.log`.
- Trong 575.061 block: 558.223 block `Normal` và 16.838 block `Anomaly`.
- BGL raw có 4.747.963 dòng. Cột đầu `-` là Normal và category khác `-`
  là Anomaly. JSONL hiện có 4.399.503 Normal và 348.460 Anomaly.

## HDFS_v1

HDFS_v1 là log phân tán theo session/block. Nhiều dòng có thể thuộc cùng một
`BlockId`; nhãn của block là Normal hoặc Anomaly. Vì block là đơn vị nhãn,
các dòng của cùng một block không được đưa sang hai split khác nhau.

Kích thước thực tế đã xác minh: 11,175,629 dòng trong `HDFS.log`.
Trước khi chạy phân tích, label file phải được đối chiếu bằng `BlockId` và
nguồn nhãn, checksum và parser version phải được ghi lại.

## BGL

BGL là log siêu máy tính với nhãn lỗi tự nhiên/cảnh báo ở cấp dòng hoặc cửa
sổ thời gian. Việc đánh giá theo fixed-size/time window hoặc line-level phải
được đăng ký trước và thống nhất cho mọi phương pháp.

## Tác động thực nghiệm

1. HDFS_v1 và BGL cần hai chiến lược split khác nhau: block-based và
   chronological/window-based.
2. Không được chuyển metric hoặc template count giữa HDFS_v1 và BGL.
3. Cả hai dataset mất cân bằng; accuracy không phải metric chính.
4. Mọi metric HDFS phải ghi rõ granularity: `line`, `block` hoặc `session`.
5. Prevalence, threshold, seed và số mẫu train/test/validation phải được ghi
   trong manifest thực nghiệm.
