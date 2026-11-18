Seed (random seed — hạt giống ngẫu nhiên)

Nhiều phương pháp học máy có yếu tố ngẫu nhiên: khởi tạo trọng số mạng nơ-ron, shuffle dữ liệu, random sampling... Nếu chạy 2 lần không cố định seed, kết quả sẽ khác
nhau mỗi lần, không ai biết số nào là đúng.

Cố định seed (ví dụ seed = 42) có nghĩa: buộc tất cả phương pháp dùng cùng một chuỗi số ngẫu nhiên → đảm bảo kết quả có thể tái lập (reproducible). Người khác chạy lại
code của bạn với cùng seed sẽ ra đúng con số đó.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

std (standard deviation — độ lệch chuẩn)

Dù đã cố định seed, một số phương pháp vẫn có biến thiên giữa các lần chạy (ví dụ: random sampling trong LogRAG, khởi tạo khác nhau). Vì vậy cần chạy lặp nhiều lần (v
í dụ 5 lần) rồi báo cáo:

│ F1 = 0.923 ± 0.008

Con số sau ± chính là std — cho biết kết quả ổn định hay bất ổn. Std nhỏ = phương pháp ổn định; std lớn = kết quả phụ thuộc nhiều vào may rủi khởi tạo, cần thận trọng
khi kết luận.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tại sao quan trọng với luận văn này?

Vì bạn so sánh 6 phương pháp — nếu phương pháp A đạt F1 = 0.91 và phương pháp B đạt F1 = 0.90, kết luận A tốt hơn B chỉ có giá trị khi std của cả hai đủ nhỏ (ví dụ ±
0.003). Nếu std của B là ±0.02 thì hai phương pháp thực chất không khác nhau có ý nghĩa thống kê.

8% > std và seed trong phần đánh giá là gì?

> std (standard deviation — độ lệch chuẩn) và seed là hai khái niệm kiểm soát chất lượng thực nghiệm:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Seed (random seed — hạt giống ngẫu nhiên)

Nhiều phương pháp học máy có yếu tố ngẫu nhiên: khởi tạo trọng số mạng nơ-ron, shuffle dữ liệu, random sampling... Nếu chạy 2 lần không cố định seed, kết quả sẽ khác
nhau mỗi lần, không ai biết số nào là đúng.

Cố định seed (ví dụ seed = 42) có nghĩa: buộc tất cả phương pháp dùng cùng một chuỗi số ngẫu nhiên → đảm bảo kết quả có thể tái lập (reproducible). Người khác chạy lại
code của bạn với cùng seed sẽ ra đúng con số đó.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

std (standard deviation — độ lệch chuẩn)

Dù đã cố định seed, một số phương pháp vẫn có biến thiên giữa các lần chạy (ví dụ: random sampling trong LogRAG, khởi tạo khác nhau). Vì vậy cần chạy lặp nhiều lần (v
í dụ 5 lần) rồi báo cáo:

│ F1 = 0.923 ± 0.008

Con số sau ± chính là std — cho biết kết quả ổn định hay bất ổn. Std nhỏ = phương pháp ổn định; std lớn = kết quả phụ thuộc nhiều vào may rủi khởi tạo, cần thận trọng
khi kết luận.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tại sao quan trọng với luận văn này?

Vì bạn so sánh 6 phương pháp — nếu phương pháp A đạt F1 = 0.91 và phương pháp B đạt F1 = 0.90, kết luận A tốt hơn B chỉ có giá trị khi std của cả hai đủ nhỏ (ví dụ ±
0.003). Nếu std của B là ±0.02 thì hai phương pháp thực chất không khác nhau có ý nghĩa thống kê.

▸ Credits: 0.34 • Time: 10s

9% > có nên đặt seed cố định không?

> Có, và đây là thực hành bắt buộc trong nghiên cứu thực nghiệm. Nhưng cần hiểu đúng vai trò của nó.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Seed cố định để làm gì

Để tái lập được (reproducibility) — người khác chạy lại code của bạn với cùng seed ra đúng con số đó. Đây là yêu cầu tối thiểu của ACM SIGSOFT Empirical Standards mà
luận văn bạn đã cam kết tuân theo.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nhưng seed cố định không đủ một mình

Seed cố định chỉ đảm bảo cùng một người chạy lại được kết quả giống nhau. Nó không trả lời câu hỏi: "kết quả này có ổn định không, hay chỉ may mắn với seed đó?"

Vì vậy cần làm thêm: chạy lặp với nhiều seed khác nhau (ví dụ 5 lần với seed = 0, 1, 2, 3, 4), rồi báo cáo trung bình ± std. Đây mới là bằng chứng thống kê thuyết phụ
c.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thực tế với 6 phương pháp của bạn

| Phương pháp      | Yếu tố ngẫu nhiên                | Cần chạy lặp?                    |
| ---------------- | -------------------------------- | -------------------------------- |
| LightAD (KNN/DT) | Gần như không có                 | Ít cần, nhưng vẫn nên            |
| SemPCA           | PCA xác định, seed ảnh hưởng nhỏ | Ít cần                           |
| LogFormer        | Khởi tạo trọng số, dropout       | Cần                              |
| CoLog            | Khởi tạo trọng số                | Cần                              |
| Logs2Graph       | Khởi tạo GNN                     | Cần                              |
| LogRAG           | DeepSVDD + sampling LLM          | Rất cần — LLM không deterministc |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Khuyến nghị thực tế

Cố định seed = 42 (hoặc bộ seed 42, 0, 1, 2, 3) cho tất cả. Chạy ít nhất 3 lần cho các phương pháp có học sâu. Với LightAD/SemPCA chạy 1 lần cũng chấp nhận được nếu
ghi rõ lý do.

Riêng LogRAG cần ghi chú thêm rằng phần LLM có thể không hoàn toàn deterministic dù cố định seed phía Python — đây là giới hạn kỹ thuật cần nêu trong phần Threats to
Validity.

▸ Credits: 0.35 • Time: 10s

9% > làm sao biết chọn seed bao nhiêu?

> Không có quy tắc khoa học nào để chọn con số cụ thể. Seed chỉ là một số nguyên bất kỳ để khởi tạo bộ sinh số ngẫu nhiên — bản thân con số không có ý nghĩa gì.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tại sao 42 phổ biến đến vậy?

Đây là truyền thống trong cộng đồng ML/research, xuất phát từ cuốn tiểu thuyết khoa học viễn tưởng The Hitchhiker's Guide to the Galaxy của Douglas Adams — trong đó 42
là "câu trả lời cho mọi câu hỏi trong vũ trụ". Không có lý do thống kê nào cả, chỉ là quy ước không chính thức.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Điều thực sự quan trọng

Không phải chọn seed bao nhiêu, mà là:

1. Chọn trước khi chạy, không phải sau khi thấy kết quả. Nếu bạn thử seed 1, 2, 3... rồi chọn seed nào cho kết quả đẹp nhất để báo cáo — đó là gian lận thực nghiệm (_
   seed hacking_), tương tự p-hacking trong thống kê.

2. Ghi rõ seed đã dùng trong phụ lục để người khác tái lập được.

3. Dùng nhiều seed nếu muốn kết quả đáng tin — chạy với seed = 0, 1, 2, 3, 4 rồi lấy trung bình ± std. Lúc này con số cụ thể của từng seed không còn quan trọng nữa.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Kết luận thực tế cho luận văn

Chọn seed = 42 cho đơn giản, nhất quán, dễ giải thích. Quan trọng hơn là dùng nó nhất quán cho tất cả 6 phương pháp — không phải mỗi phương pháp một seed khác nhau.

Searched for "3.10"
Viewed de_cuong_chi_tiet_tong_hop.md:368-415

Để giúp bạn nắm rõ và tự tin bảo vệ đề cương trước Hội đồng / CBHD, dưới đây là giải thích chi tiết về **RQ4: Phân loại lỗi có cấu trúc trên 50–100 mẫu FP/FN mỗi phương pháp và đánh giá khả năng giải thích**.

---

### 1. Vì sao cần RQ4? (Động lực nghiên cứu)

Hầu hết các bài báo chỉ dừng lại ở việc báo cáo điểm số tổng thể ($F_1$, Precision, Recall). Tuy nhiên:

- **Con số $F_1$ không cho biết _vì sao_ mô hình thất bại:** Một mô hình đạt $F_1 = 0.95$ vẫn có thể mắc những lỗi ngớ ngẩn hoặc nguy hiểm trong thực tế.
- **Trong vận hành hệ thống (AIOps/SRE):**
  - **False Positive (FP - Báo động giả):** Khiến kỹ sư trực ca bị quá tải cảnh báo (_alert fatigue_), dần dần mất niềm tin và bỏ qua cảnh báo của hệ thống.
  - **False Negative (FN - Bỏ sót lỗi):** Nguy hiểm nhất, vì sự cố thực tế diễn ra mà hệ thống không cảnh báo, dẫn đến sập dịch vụ (_outage_).
- **Hộp đen (Black-box):** Dù mô hình báo đúng (True Positive), nếu kỹ sư không hiểu _tại sao_ nó coi chuỗi log đó là bất thường, họ sẽ mất rất nhiều thời gian dò tìm nguyên nhân gốc rễ (Root Cause Analysis).

👉 **Mục tiêu của RQ4:** Trả lời hai câu hỏi lớn:

1. _Mỗi họ phương pháp thường chết ở những kiểu dữ liệu/kịch bản nào (failure modes)?_
2. _Khi đưa ra quyết định, phương pháp nào cung cấp được lời giải thích mà kỹ sư con người có thể hiểu và tin cậy được?_

---

### 2. Tại sao lại là "50–100 mẫu FP/FN mỗi phương pháp"?

- **Cơ sở thực nghiệm:** Tập kiểm thử (test set) trên BGL hay HDFS có từ hàng chục nghìn đến hàng triệu chuỗi log. Số lượng lỗi FP/FN có thể lên tới hàng nghìn mẫu, **không thể phân tích thủ công toàn bộ**.
- **Tính đại diện thống kê:** Theo chuẩn thực nghiệm công nghệ phần mềm (_ACM SIGSOFT Empirical Standards_), việc lấy mẫu ngẫu nhiên có phân tầng (**Stratified Random Sampling**) từ **50 đến 100 mẫu FP** và **50 đến 100 mẫu FN** cho mỗi mô hình là đủ lớn để phản ánh phân bố các loại lỗi, đồng thời vừa sức để kiểm tra chéo thủ công (**Manual Inspection & Cross-Validation**) giữa học viên và người kiểm chứng độc lập.

---

### 3. "Phân loại lỗi có cấu trúc" (Structured Error Taxonomy) là làm gì?

Từng mẫu lỗi trong tập 50–100 mẫu được trích xuất sẽ được phân tích nội dung log và xếp vào **Hệ thống phân loại 5 nhóm nguyên nhân gốc rễ (Error Taxonomy)**:

```
                  ┌────────────────────────────────────────────────────────┐
                  │       PHÂN LOẠI LỖI CÓ CẤU TRÚC (ERROR TAXONOMY)       │
                  └────────────────────────────────────────────────────────┘
                                               │
         ┌──────────────────┬──────────────────┼──────────────────┬──────────────────┐
         ▼                  ▼                  ▼                  ▼                  ▼
   [Nhóm 1: Cú pháp]  [Nhóm 2: Độ dài]  [Nhóm 3: Lặp lại]  [Nhóm 4: Nhãn]     [Nhóm 5: Sự kiện hiếm]
   Unseen Templates   Sequence Length   Repeated Anomaly   Noisy Ground       Rare Normal Events
   (Template mới lạ)  (Quá ngắn/dài)    (Vòng lặp lỗi)     Truth (Nhiễu nhãn) (Nhầm hiếm là lỗi)
```

| Nhóm lỗi                                                  | Bản chất kỹ thuật                                                                                                  | Ví dụ thực tế                                                                                                                                         | Họ mô hình hay gặp                                                                                                                               |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **1. Unseen Log Template** _(Trôi dạt cú pháp)_           | Chuỗi log chứa câu log có template chưa từng xuất hiện trong tập huấn luyện (do cập nhật phần mềm, tham số mới).   | Bản log xuất hiện: `Received block blk_999 of size 0` (lần đầu thấy size = 0).                                                                        | **LightAD, SemPCA** (dễ báo **FP** vì vector tần suất xuất hiện chiều lạ). Ngược lại, **LogFormer, LogRAG** ít bị hơn nhờ hiểu ngữ nghĩa từ ngữ. |
| **2. Sequence Length Extremes** _(Cực trị độ dài)_        | Chuỗi log quá ngắn (1–2 sự kiện, không đủ ngữ cảnh chuỗi) hoặc quá dài (>1.000 sự kiện, vượt context window).      | Một tiến trình kết thúc ngay sau khi khởi tạo (chỉ có 2 dòng log).                                                                                    | **Logs2Graph** (đồ thị quá ít nút/cạnh, không trích xuất được đặc trưng đồ thị), **LogFormer** (tràn cửa sổ Transformer).                        |
| **3. Repeated Anomaly Patterns** _(Vòng lặp bất thường)_  | Một lỗi hệ thống lặp lại hàng trăm lần (ví dụ: vòng lặp thử lại kết nối `Connection reset by peer` liên tục).      | Khi lỗi lặp lại quá đều đặn, phân bố thống kê của nó trông lại "mượt mà" và ổn định.                                                                  | Các mô hình dựa trên tái tạo/khoảng cách dễ bị **FN** (bỏ sót) vì nhầm là hành vi bình thường lặp lại.                                           |
| **4. Noisy / Mislabeled Ground Truth** _(Nhiễu nhãn gốc)_ | Nhãn trong dataset gốc bị sai hoặc gây tranh cãi.                                                                  | Trong BGL, log ghi tag cảnh báo phần cứng nhưng hệ thống vẫn hoạt động bình thường; hoặc HDFS có inject fault nhưng hàm gọi lỗi không được kích hoạt. | Mô hình dự đoán đúng thực tế nhưng lại bị tính là **FP** hoặc **FN** trên số liệu benchmark.                                                     |
| **5. Rare Normal Events** _(Sự kiện hiếm gặp)_            | Các tác vụ bình thường nhưng có tần suất cực thấp (ví dụ: cronjob dọn đĩa lúc nửa đêm, log khởi động lại bảo trì). | Mô hình không phân biệt được giữa _"ít gặp"_ (infrequent) và _"bất thường"_ (anomalous).                                                              | **SemPCA, DeepSVDD** (coi điểm nằm xa tâm/ngoài không gian con là bất thường → sinh ra **FP**).                                                  |

**Kết quả đầu ra của phần này:**
Một bảng ma trận % phân bố nguyên nhân lỗi cho từng mô hình. Ví dụ: _LightAD có 45% FP do Unseen Template, trong khi Logs2Graph chỉ có 12% FP do Unseen Template nhưng 38% FN do chuỗi quá ngắn._

---

### 4. "Đánh giá khả năng giải thích" (Explainability) làm như thế nào?

Không chỉ dừng lại ở việc phân loại lỗi, luận văn sẽ đánh giá xem **khi mô hình phát hiện ra một sự cố (True Positive), nó giúp kỹ sư giải thích sự cố đó tốt đến mức nào**.

Trong 6 phương pháp, có 2 phương pháp có cơ chế giải thích nội tại (_intrinsic explainability_) vượt trội:

#### A. Logs2Graph (Giải thích dựa trên đồ thị — Graph Node Importance)

- **Cơ chế:** Logs2Graph biểu diễn chuỗi log thành đồ thị có hướng (nút = sự kiện log, cạnh = chuyển tiếp tuần tự). Mô hình sử dụng mạng GNN để tính điểm bất thường cho toàn đồ thị, đồng thời trích xuất được trọng số đóng góp của từng nút (**Node Importance Score**).
- **Thực nghiệm đánh giá:**
  - Với các chuỗi log bất thường được phát hiện đúng, trích xuất Top-3 nút log có trọng số cao nhất.
  - So sánh đối chiếu: _Dòng log mà mô hình chỉ ra có đúng là dòng log ghi nhận lỗi gốc không_ (ví dụ: dòng log `Connection timed out` hay `OutOfMemoryError`)?
  - Đo lường chỉ số **Hit@1 / Hit@3** (tỷ lệ dòng log lỗi gốc nằm trong Top-1 hoặc Top-3 nút quan trọng nhất mà mô hình chỉ ra).

#### B. LogRAG (Giải thích dựa trên LLM — LLM Reasoning Chain)

- **Cơ chế:** Khi DeepSVDD lọc ra các chuỗi nghi ngờ, LogRAG dùng cơ chế RAG để truy vấn các mẫu log tương tự trong quá khứ và đưa vào prompt để LLM (GPT-3.5-turbo / Mistral-7B) đưa ra kết luận kèm lời giải thích bằng ngôn ngữ tự nhiên.
- **Thực nghiệm đánh giá:**
  - Kiểm tra chất lượng lập luận (_Reasoning quality_): Lời giải thích của LLM có chỉ ra đúng ngữ cảnh kỹ thuật không?
  - Đánh giá hiện tượng **ảo giác (Hallucination)**: LLM có bịa ra mã lỗi hay tiến trình không tồn tại trong chuỗi log không?
  - Tính hữu dụng thực tế: Đánh giá định tính xem lời giải thích của LLM có giúp giảm thời gian khoanh vùng sự cố cho kỹ sư vận hành hay không.

#### C. Đối chiếu với các mô hình còn lại

- **LightAD (Cây quyết định / KNN):** Cung cấp giải thích dạng luật logic đơn giản (`if event_A > 3 then anomaly`), dễ hiểu nhưng nông.
- **LogFormer / CoLog (Transformer):** Hộp đen; chỉ có thể dùng Attention Map nhưng Attention weight thường bị nhiễu và khó diễn giải thành hành động cụ thể cho kỹ sư SRE.

---

### 5. Tóm lại: RQ4 mang lại giá trị gì cho Luận văn?

1. **Nâng tầm học thuật:** Đưa luận văn từ một đề tài _"chạy benchmark lấy số thông thường"_ thành một **nghiên cứu thực nghiệm chuyên sâu (In-depth Empirical Study)** theo đúng chuẩn ACM SIGSOFT.
2. **Giá trị thực tiễn cao:** Kỹ sư SRE khi đọc luận văn sẽ biết chính xác:
   - Nếu hệ thống hay cập nhật code (nhiều template mới) → Không nên chọn LightAD/SemPCA vì sẽ bị dội bom cảnh báo giả (FP).
   - Nếu cần khoanh vùng nhanh dòng log gây lỗi → Nên chọn Logs2Graph.
   - Nếu cần tóm tắt sự cố bằng tiếng người cho đội trực ban → Cân nhắc LogRAG (chấp nhận chi phí API).
