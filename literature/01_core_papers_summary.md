# Tóm tắt các bài báo cốt lõi

Đây là bản tóm tắt định hướng khả năng tái lập ban đầu. Các con số chỉ được
ghi khi có trong PDF hoặc mã nguồn cục bộ; giá trị chưa trích xuất sẽ được ghi
như một yêu cầu thu thập thêm thay vì suy đoán từ nguồn khác.

## LightAD (Yu và cộng sự, ICSE 2024)

- **Vấn đề:** Xác định liệu học máy cổ điển có thể đạt hoặc vượt học sâu trong
  phát hiện bất thường dựa trên log khi xét đồng thời độ chính xác và độ trễ.
- **Phương pháp:** Tiền xử lý theo từng bộ dữ liệu, sau đó dùng KNN, cây quyết
  định hoặc mạng nơ-ron lan truyền thẳng một tầng. Chế độ tối ưu kết hợp
  F1-score, thời gian huấn luyện và thời gian suy luận.
- **Bộ dữ liệu:** HDFS và một số bộ dữ liệu siêu máy tính, trong đó có BGL.
- **Kết quả:** Kho mã nguồn báo cáo hiệu quả cao trên năm bộ dữ liệu LogAD
  phổ biến. Bảng số liệu đầy đủ nằm trong PDF đã cung cấp và cần được trích
  xuất, kiểm chứng rồi ghi vào manifest thực nghiệm.
- **Hạn chế và khả năng tái lập:** Tiền xử lý phụ thuộc từng bộ dữ liệu và các
  đường dẫn hard-code cần điều chỉnh trước khi so sánh công bằng. Các thư viện
  phụ thuộc được liệt kê trong `LightAD/requirements.txt`; kho mã nguồn cũng
  có một mẫu HDFS nhỏ.

## LogFormer (Guo và cộng sự, AAAI 2024)

- **Vấn đề:** Cải thiện phát hiện bất thường dựa trên log bằng quy trình huấn
  luyện tiền huấn luyện và tinh chỉnh theo tác vụ có thể tái lập.
- **Phương pháp:** Phân tích log, tiền huấn luyện Transformer trên chuỗi sự
  kiện rồi tinh chỉnh mô hình cho bài toán phát hiện bất thường.
- **Bộ dữ liệu:** Các bộ dữ liệu LogHub; kho mã nguồn mô tả quy trình tải dữ
  liệu, phân tích log, tiền huấn luyện và tinh chỉnh.
- **Kết quả:** Số liệu chính xác của bài báo đang chờ trích xuất từ PDF cục bộ.
  Bản tóm tắt này không tự tạo giá trị kết quả.
- **Hạn chế và khả năng tái lập:** Huấn luyện cần GPU và phụ thuộc thứ tự tiền
  xử lý dữ liệu. Kho mã nguồn tách riêng các script tiền huấn luyện và tinh
  chỉnh.

## LogRAG (Jiang và cộng sự, ISSRE 2024)

- **Vấn đề:** Giảm độ nhạy của phát hiện bất thường bán giám sát đối với lỗi
  phân tích log và chuỗi sự kiện không ổn định.
- **Phương pháp:** Giai đoạn DeepSVDD một lớp phát hiện các ứng viên bất
  thường; mô hình ngôn ngữ lớn sử dụng ngữ cảnh truy xuất để đánh giá lại các
  ứng viên dựa trên log token và log template.
- **Bộ dữ liệu:** BGL và Spirit. Luận văn này bổ sung bộ điều hợp cho HDFS thay
  vì ngầm coi HDFS tương đồng với BGL.
- **Kết quả:** README của kho mã nguồn báo cáo cải thiện tương đối F1 là 15%
  trên BGL và 60% trên Spirit so với thuật toán bán giám sát tốt nhất trước đó.
  Đây là kết quả do nguồn gốc công bố, chưa phải kết quả đo lại trong phiên
  làm việc này.
- **Hạn chế và khả năng tái lập:** Cần mô hình BigLog hoặc mô hình ngôn ngữ
  lớn cục bộ, phụ thuộc GPU và API key nếu dùng dịch vụ bên ngoài. Không được
  commit API key. Kích thước cửa sổ, ngưỡng và tham số truy xuất phải được ghi
  cho từng lần chạy.

## Rủi ro tái lập liên bài báo

1. Phiên bản bộ dữ liệu và đơn vị gom log khác nhau.
2. Cách phân tích và truyền nhãn phụ thuộc từng phương pháp.
3. Các chỉ số công bố có thể dùng split và cấp độ tổng hợp khác nhau.
4. Chi phí tính toán và API không trực tiếp so sánh được nếu thiếu giao thức
   phần cứng và đo lường chung.

Bài tóm tắt vì vậy chỉ đóng vai trò ghi nhận nguồn gốc. Các số đo mới phải được
sinh bằng script và cấu hình thống nhất của kho mã nguồn.
