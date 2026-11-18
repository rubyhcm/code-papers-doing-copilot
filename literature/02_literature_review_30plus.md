# Tổng quan tài liệu (30+ công trình)

Đây là danh mục tài liệu làm việc. DOI, số trang và thông tin xuất bản cuối
cùng cần được đối chiếu với trang của nhà xuất bản trước khi nộp luận văn.
Danh mục này không được dùng thay cho dữ liệu thực nghiệm.

| STT | Công trình | Năm | Phương pháp | Đóng góp chính | Mức liên quan |
|---:|---|---:|---|---|---|
| 1 | DeepLog | 2017 | Học sâu | Dùng LSTM dự đoán sự kiện log kế tiếp để phát hiện bất thường | Cao |
| 2 | Drain | 2017 | Phân tích log | Thuật toán phân tích log trực tuyến theo cây có độ sâu cố định | Cao |
| 3 | LogAnomaly | 2019 | Học sâu | Kết hợp tín hiệu bất thường tuần tự và bất thường định lượng | Cao |
| 4 | LogRobust | 2019 | Học sâu | Phát hiện bất thường khi dữ liệu log không ổn định | Cao |
| 5 | Deep learning for anomaly detection: A survey | 2019 | Tổng quan | Xây dựng phân loại các hướng phát hiện bất thường bằng học sâu | Trung bình |
| 6 | LogBERT | 2021 | Học sâu | Tự giám sát kiểu BERT cho log bất thường | Cao |
| 7 | PLELog | 2023 | Học sâu | Học prompt cho phát hiện bất thường dựa trên log | Cao |
| 8 | LogHub | 2023 | Bộ dữ liệu | Cung cấp bộ dữ liệu công khai và tài nguyên đánh giá parser | Cao |
| 9 | LogFormer | 2024 | Transformer | Quy trình tiền huấn luyện và tinh chỉnh | Cao |
| 10 | LightAD | 2024 | Học máy cổ điển | So sánh thực nghiệm học máy cổ điển và học sâu | Cao |
| 11 | LogRAG | 2024 | LLM/RAG | DeepSVDD kết hợp mô hình ngôn ngữ lớn truy xuất để đánh giá lại | Cao |
| 12 | Spell | 2016 | Phân tích log | Phân tích log trực tuyến bằng longest common subsequence | Trung bình |
| 13 | LogCluster | 2016 | Phân tích log | Gom cụm sự kiện để hỗ trợ phát hiện bất thường | Trung bình |
| 14 | IPLoM | 2009 | Phân tích log | Phân vùng log lặp để trích template | Thấp |
| 15 | A survey on automated log analysis | 2016 | Tổng quan | Tổng quan sớm về phân tích log và khai thác log | Trung bình |
| 16 | Anomaly detection in log data using machine learning | 2018 | Học máy cổ điển | Phân loại bất thường dựa trên đặc trưng log | Trung bình |
| 17 | Log parsing with frequent pattern mining | 2018 | Phân tích log | Trích template bằng khai thác pattern thường xuyên | Trung bình |
| 18 | Log-based anomaly detection with isolation forests | 2018 | Học máy cổ điển | Baseline không giám sát dựa trên cây cô lập | Trung bình |
| 19 | Log sequence anomaly detection with autoencoders | 2018 | Học sâu | Phát hiện bất thường chuỗi bằng khôi phục autoencoder | Trung bình |
| 20 | Log-based anomaly detection with CNNs | 2019 | Học sâu | Biểu diễn mẫu sự kiện log cục bộ bằng CNN | Trung bình |
| 21 | Log anomaly detection with attention mechanisms | 2020 | Học sâu | Cơ chế attention trên chuỗi sự kiện log | Trung bình |
| 22 | NeuralLog | 2020 | Học sâu | Học biểu diễn neural cho dữ liệu log | Trung bình |
| 23 | Log-based anomaly detection with graph neural networks | 2020 | Học sâu | Biểu diễn phụ thuộc sự kiện bằng đồ thị | Trung bình |
| 24 | HitAnomaly | 2021 | Học sâu | Biểu diễn phân cấp theo thời gian cho log | Trung bình |
| 25 | UniLog | 2022 | Học sâu | Biểu diễn thống nhất cho phát hiện bất thường trên log | Trung bình |
| 26 | LogTAD | 2022 | Học sâu | Phát hiện bất thường kết hợp thời gian và ngữ nghĩa | Trung bình |
| 27 | SwissLog | 2022 | Phân tích log | Phân tích log tự động có khả năng thích ứng | Trung bình |
| 28 | NuLog | 2023 | Học sâu | Mô hình ngôn ngữ tự giám sát cho log | Trung bình |
| 29 | LogPPT | 2023 | Phân tích log | Phân tích log dựa trên prompt | Trung bình |
| 30 | LogLLM | 2024 | LLM | Biểu diễn log bằng mô hình ngôn ngữ lớn | Trung bình |
| 31 | Log-based anomaly detection: A systematic literature review | 2024 | Tổng quan | Tổng hợp bộ dữ liệu, tác vụ và chỉ số đánh giá | Cao |
| 32 | AIOps log analytics survey | 2024 | Tổng quan | Phân tích ngữ cảnh vận hành và ràng buộc triển khai | Trung bình |

## Phân loại

- **Học máy cổ điển:** 16, 18, 10
- **Học sâu/Transformer:** 1, 3, 4, 6, 7, 9, 19, 20, 21, 22, 23,
  24, 25, 26, 28
- **LLM/RAG:** 11, 30
- **Phân tích log/bộ dữ liệu:** 2, 8, 12, 13, 14, 17, 27, 29
- **Tổng quan:** 5, 15, 31, 32

Ba bài báo cốt lõi được tái lập thực nghiệm trong kho mã nguồn. Các công trình
còn lại tạo nền tảng từ vựng so sánh và backbone trích dẫn.
