# Đặc điểm dữ liệu log

## Các đặc điểm cốt lõi

1. **Bán cấu trúc:** Timestamp, component, mức độ nghiêm trọng và nội dung tự
   do xuất hiện trong cùng một bản ghi. Parser phải tách template sự kiện ổn
   định khỏi tham số thay đổi.
2. **Phi dừng:** Phiên bản phần mềm và điều kiện vận hành có thể tạo ra template
   mới. Một template chưa từng gặp không tự động là bất thường.
3. **Dung lượng và tốc độ sinh lớn:** HDFS và BGL gồm hàng triệu bản ghi. Quy
   trình phân tích và đánh giá cần hỗ trợ xử lý streaming hoặc xử lý theo batch
   có giới hạn bộ nhớ.
4. **Mất cân bằng mạnh:** Bản ghi bình thường chi phối. Accuracy một mình không
   đủ; cần PR-AUC, F1, Recall và false-positive rate.
5. **Ngữ nghĩa phụ thuộc ngữ cảnh:** Cùng một event có thể bình thường hoặc bất
   thường tùy block, session, cửa sổ thời gian hoặc chuỗi log xung quanh.

## Phân loại định dạng

| Định dạng | Ví dụ | Cách gom phù hợp |
|---|---|---|
| Văn bản thô | `timestamp component: message` | Parser tự xác định trường |
| CSV có cấu trúc | `Label,EventId,EventTemplate,...` | Dòng hoặc cửa sổ thời gian |
| Log theo block/session | Các bản ghi HDFS có `BlockId` | Block/session |
| Log theo cửa sổ thời gian | Các bản ghi BGL có timestamp | Cửa sổ cố định hoặc trượt |

## Thách thức phân tích log

- Identifier và giá trị số thay đổi có thể làm phân mảnh template.
- Dấu phân cách và timestamp khác nhau giữa các hệ thống.
- Lỗi parser lan truyền sang event ID, đặc trưng và lời giải thích.
- Template mới tạo thành bài toán tập mở.
- Nhãn có thể gắn với một nhóm thay vì từng dòng riêng lẻ.
- Cấu hình parser có thể tái lập là một phần của dữ liệu thực nghiệm.

Pipeline ghi lại dữ liệu thô, template chuẩn hóa, template ID, tham số và nguồn
gốc để có thể kiểm tra lại từng quyết định của parser.
