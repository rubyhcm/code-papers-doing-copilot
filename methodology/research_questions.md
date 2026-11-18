# Câu hỏi nghiên cứu và giao thức đo lường

## RQ1 — Hiệu quả phát hiện

**Câu hỏi:** Precision, Recall, F1, PR-AUC và FPR của LightAD, LogFormer và
LogRAG trên HDFS_v1 và BGL là bao nhiêu khi đánh giá theo cùng giao thức chia
dữ liệu và truyền nhãn?

**Giao thức:** Báo cáo kết quả ở cấp dòng và cấp nhóm khi phù hợp, đồng thời
ghi positive prevalence và ngưỡng quyết định. Không so sánh trực tiếp điểm số
công bố trong bài báo với kết quả mới nếu chưa ghi rõ split và cấp độ tổng hợp.

## RQ2 — Chi phí tính toán

**Câu hỏi:** Thời gian huấn luyện, độ trễ hoặc throughput suy luận, bộ nhớ
đỉnh và chi phí token/API bên ngoài của LogRAG là bao nhiêu?

**Giao thức:** Dùng cùng phần cứng khi có thể, warm-up trước khi đo, đo thời
gian wall-clock có đồng bộ hóa với thiết bị GPU và báo cáo rõ mọi phép đo không
có.

## RQ3 — Đánh đổi hiệu quả và chi phí

**Câu hỏi:** Phương pháp nào nằm trên Pareto frontier giữa chất lượng phát hiện
và chi phí tài nguyên?

**Giao thức:** Xác định mục tiêu trước khi xem kết quả. Một phương pháp bị
dominated nếu phương pháp khác không kém hiệu quả hơn, không tốn chi phí cao
hơn và có ít nhất một chỉ tiêu cải thiện. Vẽ F1/PR-AUC theo độ trễ và bộ nhớ.

## RQ4 — Kiểu lỗi và khả năng giải thích

**Câu hỏi:** Điều kiện dữ liệu nào lặp lại dẫn đến FP/FN và lời giải thích của
từng phương pháp có actionable hay không?

**Giao thức:** Phân tầng mẫu FP/FN theo độ mới của template, mức severity,
kích thước nhóm và loại nhãn. Chấm lời giải thích bằng rubric mù gồm quyết
định, bằng chứng và nguyên nhân có thể hành động; lưu ID mẫu và phiên bản rubric.

## Kiểm soát khả năng tái lập

Mọi lần chạy ghi commit hash, checksum/phiên bản dataset, cấu hình parser,
split seed, cấu hình mô hình, phần cứng, phiên bản phần mềm và đường dẫn output.
Các seed dự kiến là `42, 123, 456, 789, 2024`; phương pháp ngẫu nhiên báo cáo
giá trị trung bình và độ lệch chuẩn thay vì chọn seed cho ra kết quả đẹp nhất.
