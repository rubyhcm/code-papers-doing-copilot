# ĐỀ CƯƠNG CHI TIẾT LUẬN VĂN THẠC SĨ (TỔNG HỢP)

---

## THÔNG TIN CHUNG

**Tên đề tài (Tiếng Việt):**
Đánh giá thực nghiệm các phương pháp phát hiện bất thường dựa trên dữ liệu log: Từ học máy cổ điển đến mô hình ngôn ngữ lớn

**Tên đề tài (Tiếng Anh):**
An Empirical Evaluation of Log-Based Anomaly Detection Methods: From Classical Machine Learning to Large Language Models

---

## CHƯƠNG 1: GIỚI THIỆU

### 1.1. Bối cảnh và động lực nghiên cứu

Các hệ thống phần mềm hiện đại — từ cụm phân tán (Hadoop, HDFS), siêu máy tính (BlueGene/L), đến hạ tầng đám mây (OpenStack) — liên tục sinh ra khối lượng log khổng lồ (hàng triệu dòng/ngày). Log là nguồn dữ liệu quan trọng bậc nhất để giám sát vận hành, phát hiện sự cố và bảo đảm an ninh hệ thống.

Phát hiện bất thường dựa trên log (*Log-Based Anomaly Detection — LogAD*) là bài toán tự động phân loại hoặc gắn cờ những bản ghi/chuỗi sự kiện bất thường nhằm rút ngắn thời gian phát hiện lỗi, giảm thiểu thời gian dừng dịch vụ và cảnh báo sớm cho đội vận hành (SRE).

Trong giai đoạn 2024–2025, bài toán LogAD chứng kiến sự bùng nổ với các xu hướng kỹ thuật rất khác nhau:

| Xu hướng | Đại diện | Điểm nổi bật |
|---|---|---|
| Học máy cổ điển được đánh giá lại | **LightAD** (ICSE'24) | KNN/DT/SLFN cho hiệu quả đáng ngạc nhiên |
| Học sâu tuần tự cải tiến | **LogFormer** (AAAI'24) | Pre-train + Adapter tuning trên Transformer |
| Transformer đa phương thức | **CoLog** (Sci. Reports 2025) | Collaborative Transformers + MHIA + MAL |
| Mạng nơ-ron đồ thị | **Logs2Graph** (ICSE'24 Companion) | OCDiGCN: One-Class Digraph Inception GCN |
| LLM + RAG bán giám sát | **LogRAG** (ISSRE'24) | DeepSVDD + RAG + LLM tái đánh giá |
| Thống kê cải tiến | **SemPCA** | PCA++ trên biểu diễn ngữ nghĩa log |

### 1.2. Vấn đề nghiên cứu và khoảng trống

Mỗi phương pháp thường được công bố với bộ dữ liệu, giao thức đánh giá, môi trường và cách tiền xử lý **riêng biệt**, dẫn đến khó khăn trong việc đối chiếu trực tiếp. Cụ thể:

1. **Thiếu giao thức đánh giá thống nhất:** Các nghiên cứu dùng cách chia dữ liệu, cách tính chỉ số và cách xử lý nhãn khác nhau.
2. **Chưa có benchmark đa họ kỹ thuật:** Chưa có đánh giá nào đặt **đồng thời cả ba họ kỹ thuật chủ đạo** (ML cổ điển siêu nhẹ, Transformer, LLM+RAG) lên cùng một benchmark thống nhất.
3. **Chưa so sánh chi phí tính toán công bằng:** Đánh đổi giữa chi phí LLM/RAG (LogRAG) so với phương pháp nhẹ (LightAD) chưa được làm rõ trong cùng điều kiện phần cứng.
4. **Độ ổn định giữa các bộ dữ liệu:** Chưa rõ phương pháp tốt trên HDFS có ổn định trên BGL hay không, đặc biệt khi so sánh fault injection có kiểm soát (HDFS_v3) với lỗi tự nhiên production (BGL).
5. **Thiếu phân tích lỗi có cấu trúc:** Chưa có phân tích FP/FN đặc trưng của từng phương pháp, chưa làm rõ kiểu lỗi nào phổ biến với ML cổ điển, Transformer hay LLM+RAG.

### 1.3. Ý nghĩa khoa học và thực tiễn

**Về khoa học:**
- Cung cấp bằng chứng so sánh đáng tin cậy, có thể tái lập cho cộng đồng nghiên cứu LogAD
- Chuẩn hóa giao thức đánh giá và chỉ ra hướng nghiên cứu tiếp theo

**Về thực tiễn:**
- Đưa ra khuyến nghị lựa chọn phương pháp có điều kiện (theo loại dữ liệu, ràng buộc tài nguyên, yêu cầu về độ trễ và khả năng giải thích)
- Giúp kỹ sư vận hành (SRE) quyết định nhanh nên triển khai công cụ nào

### 1.4. Mục tiêu nghiên cứu

**Mục tiêu tổng quát:**
Đánh giá một cách có hệ thống và công bằng hiệu quả phát hiện bất thường, chi phí tính toán, tính ổn định và khả năng giải thích của ba phương pháp LogAD đại diện cho ba họ kỹ thuật chủ đạo (ML cổ điển, Transformer, LLM+RAG), trên hai bộ dữ liệu log chuẩn (HDFS_v3, BGL), trong một giao thức thực nghiệm mô tả rõ và có thể tái lập.

**Mục tiêu cụ thể:**

1. **Hệ thống hóa kiến thức nền tảng:** Làm rõ bản chất, cấu trúc và thách thức của dữ liệu log; tổng hợp pipeline phân tích log (parsing, biểu diễn, nhóm phiên); xác lập khung khái niệm phát hiện bất thường trên log.
2. **Tái lập và chuẩn hóa:** Tái lập thành công mã nguồn của ba phương pháp (LightAD — ML cổ điển, LogFormer — Transformer, LogRAG — LLM+RAG) trong môi trường chung; xây dựng pipeline tiền xử lý và đánh giá thống nhất cho HDFS_v3 và BGL.
3. **Đánh giá đa chiều:** Đo lường và so sánh hiệu quả phát hiện (P/R/F1/PR-AUC) và chi phí tính toán (thời gian huấn luyện, độ trễ suy luận, bộ nhớ).
4. **Phân tích chuyên sâu:** Phân tích độ ổn định giữa HDFS_v3 (fault injection) và BGL (lỗi tự nhiên); phân tích lỗi có cấu trúc (FP/FN); đánh giá khả năng giải thích.
5. **Khuyến nghị thực tiễn:** Rút ra cẩm nang lựa chọn phương pháp theo điều kiện triển khai (tài nguyên, độ trễ, khả năng giải thích).

### 1.5. Câu hỏi nghiên cứu (Research Questions)

| RQ | Nội dung | Mục đích |
|---|---|---|
| **RQ1** | Ba phương pháp đạt Precision, Recall, F1, PR-AUC như thế nào trên HDFS_v3 và BGL khi đánh giá theo cùng một giao thức? | Xác lập baseline so sánh công bằng |
| **RQ2** | Thứ hạng và hiệu quả có thay đổi giữa HDFS_v3 (fault injection) và BGL (lỗi tự nhiên)? Phương pháp nào ổn định nhất? | Đánh giá khả năng tổng quát hóa và ổn định |
| **RQ3** | Đánh đổi giữa độ chính xác và chi phí tính toán (thời gian huấn luyện, độ trễ suy luận, bộ nhớ) như thế nào? | So sánh ML nhẹ vs. Transformer vs. LLM+RAG |
| **RQ4** | Kiểu trường hợp nào thường bị bỏ sót (FN) hoặc gây cảnh báo sai (FP)? Phương pháp nào hỗ trợ giải thích quyết định tốt nhất? | Hiểu cơ chế thất bại, đánh giá khả năng giải thích |

### 1.6. Phạm vi và giả định

- **Trong phạm vi:** 3 phương pháp đại diện (LightAD — ML cổ điển, LogFormer — Transformer, LogRAG — LLM+RAG); 2 bộ dữ liệu chuẩn (HDFS_v3, BGL) từ LogHub
- **Ngoài phạm vi:** Không đề xuất thuật toán mới; không so sánh số liệu từ bài báo gốc mà không tái lập; không tinh chỉnh mô hình bằng tập kiểm thử; không đánh giá phương pháp không có mã nguồn; không bao gồm các phương pháp GNN, Transformer đa phương thức, và thống kê nâng cao (sẽ là hướng mở rộng tương lai)

### 1.7. Đóng góp dự kiến

1. **Benchmark có thể tái lập** gồm mã nguồn, cấu hình, script tiền xử lý và đánh giá thống nhất cho ba phương pháp đại diện trên hai bộ dữ liệu
2. **Bảng kết quả và phân tích định lượng** so sánh hiệu quả phát hiện và chi phí tính toán giữa ML cổ điển, Transformer, và LLM+RAG
3. **Phân tích lỗi có cấu trúc** (taxonomy của FP/FN) gắn với đặc tính dữ liệu (fault injection vs. lỗi tự nhiên)
4. **So sánh khả năng giải thích** giữa tính minh bạch của ML cổ điển, attention mechanism của Transformer, và reasoning của LLM
5. **Khuyến nghị thực tiễn** lựa chọn phương pháp theo điều kiện vận hành cụ thể (ràng buộc tài nguyên, độ trễ, nhu cầu giải thích)

### 1.8. Cấu trúc luận văn

*(Trình bày tóm tắt nội dung các chương)*

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ TỔNG QUAN NGHIÊN CỨU

### 2.1. Log hệ thống: đặc điểm, cấu trúc và vai trò

- Định nghĩa log hệ thống và các thành phần: timestamp, severity level, component, content
- Mẫu log (*log template/event*), chuỗi sự kiện, phiên/session/block/trace
- Vai trò của log trong AIOps và giám sát hệ thống

### 2.2. Bài toán phát hiện bất thường log: định nghĩa và phân loại

- Bất thường điểm (*point anomaly*) và bất thường tập thể (*collective anomaly*)
- Các dạng bài toán LogAD: phân loại nhị phân, phát hiện tuần tự, không giám sát/bán giám sát, trực tuyến và phát hiện sớm
- So sánh supervised vs. semi-supervised vs. unsupervised trong bối cảnh LogAD

### 2.3. Quy trình Log Anomaly Detection chuẩn

```
Raw Logs → Log Parsing → Log Grouping → Feature Extraction → Anomaly Detection → Alert
```

- **Log Parsing:** Drain (He et al., 2017) — cây có độ sâu cố định, phân tích trực tuyến
- Ảnh hưởng của lỗi parsing tới downstream task (LogRAG paper chỉ ra vấn đề này)
- **Log Grouping:** theo session/block/trace/window (fixed-size, sliding, session-based)
- **Feature Extraction:** event count vector, TF-IDF, semantic embedding, graph structure

### 2.4. Phân loại các họ phương pháp

| Họ kỹ thuật | Đại diện được đánh giá | Ý tưởng cốt lõi | Kiểu học |
|---|---|---|---|
| **ML cổ điển siêu nhẹ** | **LightAD (ICSE'24)** | Phân loại đơn giản (KNN, DT, SLFN) trên event count vector | Giám sát |
| **Học sâu Transformer** | **LogFormer (AAAI'24)** | Pre-train Transformer + Adapter fine-tune | Tự giám sát + tinh chỉnh |
| **LLM + RAG bán giám sát** | **LogRAG (ISSRE'24)** | DeepSVDD phát hiện sơ bộ + RAG + LLM tái đánh giá | Bán giám sát |

**Lưu ý:** Phân loại trên chỉ bao gồm ba họ kỹ thuật chủ đạo được đánh giá trong nghiên cứu này. Các họ kỹ thuật khác (Transformer đa phương thức, GNN, thống kê PCA nâng cao) sẽ là hướng mở rộng trong nghiên cứu tương lai.

### 2.5. Tổng quan chi tiết ba phương pháp được đánh giá

#### 2.5.1. LightAD (ICSE 2024)

- **Kiến trúc:** KNN (k=1), Decision Tree, SLFN (MLP 1 hidden layer, 25 units)
- **Ý tưởng:** Đánh giá lại ML cổ điển với tiền xử lý đơn giản; chứng minh ML nhẹ có thể đạt SOTA
- **Tiền xử lý:** Loại bỏ token chứa chữ số → event count vector (naive aggregation); có tùy chọn deduplicate
- **Chiến lược chia:** HDFS theo random shuffle (5 lần), BGL theo chronological split
- **Dữ liệu hỗ trợ:** HDFS, BGL, Spirit, Liberty, Thunderbird
- **Ưu điểm:** Siêu nhẹ, nhanh, dễ giải thích (đặc biệt Decision Tree); không cần GPU
- **Hạn chế:** Không khai thác thứ tự sự kiện và ngữ cảnh phức tạp

#### 2.5.2. LogFormer (AAAI 2024)

- **Kiến trúc:** Transformer Encoder (4 layers, 8 heads, d=768) + Adapter modules + Positional Encoding
- **Ý tưởng:** Pipeline hai giai đoạn: (1) Pre-train trên log không nhãn bằng masked prediction, (2) Adapter tuning (chỉ fine-tune adapter + classifier, đóng băng backbone)
- **Chế độ huấn luyện:** `train_adapter()` (adapter + norm layers), `train_classifier()` (chỉ FC layer cuối)
- **Tiền xử lý:** Drain parsing → Sentence embedding (768d)
- **Dữ liệu hỗ trợ:** LogHub (HDFS, BGL, Thunderbird, Spirit, OpenStack, …) — hỗ trợ sẵn HDFS_v3 và BGL
- **Ưu điểm:** Khai thác ngữ cảnh tuần tự; pre-train giúp học biểu diễn tốt; adapter tuning hiệu quả tham số
- **Hạn chế:** Cần GPU; thời gian training dài hơn ML cổ điển

#### 2.5.3. LogRAG (ISSRE 2024)

- **Kiến trúc:** 2-phase pipeline:
  - Phase 1: DeepSVDD (soft-boundary, MLP network) phát hiện anomaly sơ bộ bằng log token embeddings
  - Phase 2: RAG + LLM (GPT-3.5-turbo hoặc Mistral-7B) tái đánh giá các mẫu được phát hiện bằng log template embeddings
- **Ý tưởng:** Giảm FP bằng cách dùng LLM + RAG để xác minh lại kết quả; dùng cả log token lẫn log template để giảm ảnh hưởng parsing errors
- **Tiền xử lý:** Drain parsing → BigLog pretrained encoder → window-based grouping (window_size=200, window_time=1800s)
- **Dữ liệu hỗ trợ (mã nguồn):** BGL, Spirit (cần mở rộng cho HDFS_v3)
- **Ưu điểm:** Giảm FP nhờ LLM reasoning; khả năng giải thích tốt nhất (LLM reasoning output bằng ngôn ngữ tự nhiên)
- **Hạn chế:** Cần API key OpenAI hoặc Mistral-7B local; chi phí tính toán và tài chính cao (latency + API cost); phụ thuộc vào chất lượng LLM

### 2.6. Bộ dữ liệu benchmark: HDFS_v3, BGL

#### 2.6.1. Mô tả chi tiết

| Đặc tính | HDFS_v3 (TraceBench) | BGL |
|---|---|---|
| **Loại hệ thống** | Hệ phân tán (Hadoop HDFS) | Siêu máy tính (BlueGene/L) |
| **Quy mô** | ~14.8M dòng, 2.96 GiB | ~4.75M dòng, 708.76 MiB |
| **Cơ chế nhãn** | Fault injection có kiểm soát (MTracer, 17 loại fault) | Lỗi tự nhiên production |
| **Cấp độ nhãn** | Trace-level | Line-level (alert tag) |
| **Tỷ lệ bất thường** | Có kiểm soát theo kịch bản | ~7.3% (tự nhiên) |
| **Nguồn** | LogHub / TraceBench | LogHub / USENIX CFDR |

#### 2.6.2. Ma trận hỗ trợ (mã nguồn hiện tại)

| Phương pháp | HDFS_v3 | BGL | Cần mở rộng |
|---|---|---|---|
| LightAD | ✓ | ✓ | — (hỗ trợ đầy đủ) |
| LogFormer | ✓ | ✓ | — (hỗ trợ đầy đủ) |
| LogRAG | ✗ | ✓ | HDFS_v3 |

#### 2.6.3. Lý do chọn hai bộ dữ liệu

- **Bao phủ hai loại môi trường hệ thống quan trọng:** hệ phân tán (HDFS_v3) và siêu máy tính (BGL)
- **Khác nhau về cơ chế nhãn:** fault injection có kiểm soát (HDFS_v3) vs. lỗi tự nhiên production (BGL) — cho phép đánh giá tính ổn định của phương pháp
- **Khác nhau về cấp độ nhãn:** trace-level (HDFS_v3) vs. line-level (BGL) — kiểm tra khả năng thích ứng với granularity khác nhau
- **Khác nhau về quy mô và đặc điểm:** HDFS_v3 lớn hơn (~3× về số dòng); BGL có tỷ lệ bất thường tự nhiên thấp (~7.3%)
- **Được sử dụng rộng rãi:** cả hai đều có nhãn công khai, là chuẩn benchmark trong cộng đồng nghiên cứu LogAD

### 2.7. Chỉ số đánh giá và sự không đồng nhất trong tài liệu

- Precision, Recall, F1-score: cách tính khác nhau giữa các bài báo (cấp mẫu, cấp window, cấp block)
- PR-AUC vs. ROC-AUC: lựa chọn trong bối cảnh dữ liệu mất cân bằng
- FPR: quan trọng cho vận hành thực tế nhưng thường bị bỏ qua
- Chi phí tính toán: hiếm khi được báo cáo đồng nhất

### 2.8. Khoảng trống nghiên cứu (tổng hợp)

1. **Chưa có benchmark thống nhất cho ba họ kỹ thuật chủ đạo:** Chưa có đánh giá nào đặt đồng thời ML cổ điển siêu nhẹ (LightAD), Transformer (LogFormer), và LLM+RAG (LogRAG) lên cùng một giao thức thực nghiệm thống nhất trên HDFS_v3 và BGL.
2. **Chưa có phân tích chi phí tính toán so sánh trực tiếp:** Đánh đổi giữa chi phí LLM/RAG (cả API cost lẫn latency) so với phương pháp Transformer và ML cổ điển siêu nhẹ chưa được làm rõ trên cùng phần cứng.
3. **Chưa có phân tích ổn định giữa fault injection và lỗi tự nhiên:** Chưa rõ phương pháp nào ổn định nhất khi chuyển từ HDFS_v3 (fault injection có kiểm soát) sang BGL (lỗi tự nhiên production).
4. **Chưa có phân tích lỗi có cấu trúc so sánh ba họ kỹ thuật:** Chưa có taxonomy FP/FN đặc trưng để hiểu kiểu lỗi nào phổ biến với ML cổ điển, Transformer, hay LLM+RAG.
5. **Khả năng giải thích chưa được so sánh trực tiếp:** Chưa có đánh giá so sánh giữa tính minh bạch của ML cổ điển (feature importance, decision path), attention mechanism của Transformer, và LLM reasoning output.

---

## CHƯƠNG 3: PHƯƠNG PHÁP NGHIÊN CỨU VÀ THIẾT KẾ THỰC NGHIỆM

### 3.1. Câu hỏi nghiên cứu chi tiết

*(Xem Mục 1.5 — mỗi RQ được phát triển thành: mục đích, kết quả cần có, phương pháp trả lời)*

| RQ | Kết quả cần có | Phương pháp trả lời |
|---|---|---|
| RQ1 | Bảng benchmark chéo (3 × 2 × P/R/F1/PR-AUC) | So sánh trực tiếp trên cùng pipeline |
| RQ2 | Rank correlation (Spearman/Kendall); phân tích đặc trưng fault injection vs. lỗi tự nhiên | Phân tích thay đổi thứ hạng; so sánh HDFS_v3 vs. BGL |
| RQ3 | Biểu đồ F1 vs. latency; bảng RAM/GPU memory; phân tích API cost (LogRAG) | Đo thời gian + bộ nhớ + chi phí API trên cùng phần cứng |
| RQ4 | Taxonomy lỗi FP/FN cho từng phương pháp; case study; so sánh khả năng giải thích | Lấy mẫu 50-100 FP/FN; phân loại thủ công; đánh giá LightAD (minh bạch), LogFormer (attention), LogRAG (LLM reasoning) |

### 3.2. Tiêu chí lựa chọn baseline

Ba phương pháp được chọn vì thỏa mãn đồng thời:

1. **Tính đại diện:** bao phủ ba họ kỹ thuật chủ đạo (ML cổ điển siêu nhẹ, Transformer, LLM+RAG)
2. **Tính thời sự:** công bố 2024 (SOTA gần nhất)
3. **Khả năng tái lập:** có mã nguồn mở đầy đủ trong dự án
4. **Tính so sánh:** có giao thoa bộ dữ liệu để đánh giá chung (HDFS_v3 và/hoặc BGL)
5. **Tính đặc trưng:** mỗi phương pháp có điểm mạnh và đánh đổi riêng biệt về chi phí-hiệu quả

Mỗi baseline được ghi nhận:
- Trích dẫn gốc, nhóm phương pháp, kiểu học
- Yêu cầu nhãn, đầu vào/đầu ra, tiền xử lý
- Mã nguồn/commit, điểm mạnh/hạn chế
- Rủi ro tái lập (dependencies, hardcoded paths, etc.)

### 3.3. Lựa chọn và mô tả bộ dữ liệu

- **Nguồn:** LogHub (logpai/loghub) — ghi nhận phiên bản/commit khi tải
- **Ghi nhận:** số bản ghi, tỷ lệ bất thường, cấp độ nhãn
- **Lý do chọn HDFS_v3 và BGL:** (xem Mục 2.6.3)
  - Bao phủ hai loại hệ thống quan trọng (phân tán, siêu máy tính)
  - Khác nhau về cơ chế nhãn (fault injection vs. lỗi tự nhiên)
  - Khác nhau về cấp độ nhãn (trace-level vs. line-level)
  - Đều được hỗ trợ tốt bởi các phương pháp được chọn
- **Đặc biệt lưu ý:** cấp độ nhãn ảnh hưởng tới cách tính metric và yêu cầu grouping strategy phù hợp

### 3.4. Quy trình tiền xử lý thống nhất

```
┌──────────────────────────────────────────────────────────────────┐
│                    UNIFIED PREPROCESSING PIPELINE                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Raw Logs ──→ Drain Parsing ──→ Template + Parameters             │
│                    │                                              │
│                    ├──→ Session/Block/Window Grouping              │
│                    │         │                                    │
│                    │         ├──→ Event Count Vector (LightAD)    │
│                    │         ├──→ Sentence Embedding (LogFormer)  │
│                    │         └──→ DeepSVDD Embedding (LogRAG)     │
│                    │                                              │
└──────────────────────────────────────────────────────────────────┘
```

**Nguyên tắc:**
- **Drain** là log parser chuẩn cho cả ba phương pháp
- Ghi tỷ lệ lỗi parsing cho từng dataset
- Chuẩn hóa timestamp; loại bỏ bản ghi thiếu trường bắt buộc
- Xử lý dữ liệu trùng lặp, thiếu và mẫu không hợp lệ
- **Grouping strategy phù hợp với từng dataset:**
  - HDFS_v3: theo Block ID (trace-level)
  - BGL: theo time window hoặc session ID (line-level)

### 3.5. Đồng bộ hóa pipeline đầu vào (mở rộng mã nguồn)

| Phương pháp | Mở rộng cần thực hiện | Mức độ phức tạp | Chi tiết kỹ thuật |
|---|---|---|---|
| LightAD | Không cần | — | Đã hỗ trợ đầy đủ HDFS_v3 và BGL |
| LogFormer | Không cần | — | Đã hỗ trợ đầy đủ HDFS_v3 và BGL |
| LogRAG | Thêm HDFS_v3 | Trung bình-Cao | Tạo `log_structured.csv` cho HDFS_v3; điều chỉnh window strategy theo trace ID |

**Ưu điểm của việc giảm xuống 3 phương pháp và 2 dataset:**
- LightAD và LogFormer đã hỗ trợ sẵn cả HDFS_v3 và BGL
- Chỉ cần mở rộng LogRAG cho HDFS_v3
- Giảm đáng kể công việc chuẩn bị pipeline (so với 6 phương pháp × 3 datasets)

### 3.6. Giao thức chia dữ liệu và kiểm soát data leakage

| Dataset | Chiến lược chia | Chi tiết |
|---|---|---|
| **HDFS_v3** | Theo trace ID | `normal_trace.csv` + `failure_trace.csv`; 80/10/10; đảm bảo phân phối loại fault đa dạng trong test |
| **BGL** | Chronological split | Fixed-size window theo thời gian; không random shuffle để tránh data leakage |

**Kiểm soát:**
- Kiểm tra mẫu trùng lặp/chuỗi chồng lấn giữa train/val/test
- Không dùng thông tin tương lai trong thí nghiệm
- Ngưỡng chỉ chọn trên validation, không trên test
- Đảm bảo tỷ lệ normal/anomaly nhất quán giữa train/val/test

### 3.7. Thiết lập huấn luyện và hiệu chỉnh siêu tham số

- Siêu tham số từ bài báo gốc làm điểm khởi đầu
- Grid search giới hạn trên validation khi bài báo không công bố đủ
- Áp dụng cùng quy trình tuning cho **TẤT CẢ** phương pháp
- **Random seed cố định:** 42 cho mọi thành phần
- Chạy lặp nhiều lần khi có yếu tố ngẫu nhiên → báo cáo trung bình ± std

**Siêu tham số quan trọng theo phương pháp (từ mã nguồn):**

| Phương pháp | Siêu tham số chính |
|---|---|
| LightAD | KNN: n_neighbors=1; DT: default; SLFN: hidden_layer_sizes=(25,) |
| LogFormer | num_layers=4, nhead=8, dim=768, adapter_size=64, dim_feedforward=3072, dropout=0.1 |
| LogRAG | lr=0.0001, n_epochs=150, batch_size=40960, window_size=200, threshold=0.8, topk=5 |

### 3.8. Chỉ số đánh giá chi tiết

| Chỉ số | Đơn vị / cách tính | RQ liên quan |
|---|---|---|
| Precision | TP/(TP+FP) cấp mẫu | RQ1, RQ2 |
| Recall | TP/(TP+FN) cấp mẫu | RQ1, RQ2 |
| F1-score | 2×P×R/(P+R) | RQ1, RQ2 |
| PR-AUC | Khi mô hình cho anomaly score | RQ1 |
| False Positive Rate | FP/(FP+TN) | RQ1, RQ4 |
| Thời gian huấn luyện | giây (trên cùng phần cứng) | RQ3 |
| Độ trễ suy luận | ms/sample trung bình | RQ3 |
| Bộ nhớ đỉnh | MB/GB (GPU + RAM) | RQ3 |
| Chi phí API (LogRAG) | USD (ước tính) | RQ3 |
| Rank correlation | Spearman/Kendall τ giữa HDFS_v3 và BGL | RQ2 |
| Taxonomy lỗi FP/FN | Phân nhóm có tiêu chí rõ | RQ4 |

### 3.9. Thiết kế đánh giá phát hiện sớm (RQ4)

- Định nghĩa "sớm" bằng tỷ lệ tiền tố: 10%, 25%, 50%, 75%, 100%
- Chỉ áp dụng với dataset/phương pháp cho phép xác định dự đoán tại từng tiền tố
- Không dùng thông tin xuất hiện sau thời điểm giả định phát hiện
- Vẽ đường cong hiệu quả theo tiền tố; phân tích đánh đổi early detection vs. FPR
- Tách riêng phân tích cho: fault injection (HDFS_v3) vs. lỗi tự nhiên (BGL) vs. cloud failure (OpenStack)

### 3.9. Quy trình phân tích lỗi (RQ4)

1. Trích xuất **50–100 FP** và **50–100 FN** từ mỗi phương pháp trên mỗi dataset
2. Phân loại thủ công (với kiểm tra chéo) vào các nhóm:
   - Unseen log template (template chưa gặp trong training)
   - Chuỗi quá ngắn/quá dài
   - Bất thường lặp lại (repeated anomaly pattern)
   - Nhiễu nhãn (noisy labels)
   - Mất cân bằng lớp (class imbalance effect)
   - Parsing errors (ảnh hưởng đến representation)
3. Tổng hợp tỷ lệ từng nhóm lỗi theo phương pháp và dataset
4. **Đánh giá khả năng giải thích:**
   - **LightAD:** Tính minh bạch của quyết định (feature importance cho SLFN/DT, nearest neighbor cho KNN)
   - **LogFormer:** Attention weights visualization — log event nào được chú ý nhiều nhất
   - **LogRAG:** LLM reasoning output — lý do tái phân loại qua prompt, khả năng giải thích bằng ngôn ngữ tự nhiên
5. **So sánh chất lượng giải thích:** đánh giá định tính độ hữu ích cho kỹ sư vận hành (actionability, clarity, correctness)

### 3.10. Môi trường thực nghiệm

| Thành phần | Yêu cầu | Ghi chú |
|---|---|---|
| GPU | NVIDIA RTX 3090 hoặc tương đương | Cùng GPU cho mọi phương pháp |
| RAM | ≥ 32 GB | |
| Python | 3.8+ | Compatibility tốt cho cả ba phương pháp |
| PyTorch | 1.13+ | LogFormer dùng nn.MultiheadAttention batch_first; LogRAG cần PyTorch |
| scikit-learn | latest | LightAD |
| transformers | 4.x | LogRAG, LogFormer |
| LLM API | OpenAI GPT-3.5-turbo hoặc Mistral-7B local | LogRAG; cần API key hoặc GPU đủ cho Mistral |

**Lợi ích khi giảm xuống 3 phương pháp:**
- Không còn xung đột scikit-learn version (SemPCA yêu cầu ≤ 0.24)
- Không cần spaCy `en_core_web_lg` (CoLog)
- Không cần GloVe embeddings (SemPCA)
- Giảm phức tạp môi trường thực nghiệm

### 3.11. Kiểm soát sai lệch, độ tin cậy và tái lập

- Ngăn rò rỉ dữ liệu giữa train/validation/test
- So sánh công bằng: giữ giống nhau điều kiện có thể; ghi rõ khác biệt khi cần thiết
- Báo cáo tính ngẫu nhiên và độ biến thiên
- Tránh khẳng định nhân quả khi thiết kế chỉ cho thấy mối liên hệ
- Cung cấp gói tái lập: mã, cấu hình, script, tài liệu
- Nêu rõ giới hạn chia sẻ (API key, giấy phép dữ liệu)
- Báo cáo cả lần chạy thất bại

---

## CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM

### 4.1. RQ1: Hiệu quả phát hiện tổng thể

- Bảng benchmark chéo: 3 phương pháp × 2 dataset × (P, R, F1, PR-AUC, FPR)
- Thống kê: trung bình ± std qua nhiều lần chạy
- So sánh với kết quả báo cáo trong bài báo gốc (nếu có thể)
- Phân tích: phương pháp nào đạt F1 cao nhất tổng thể? Có khác biệt đáng kể?
- So sánh giữa ba họ kỹ thuật: ML cổ điển vs. Transformer vs. LLM+RAG

### 4.2. RQ2: Độ ổn định giữa HDFS_v3 và BGL

- Rank correlation (Spearman ρ, Kendall τ) giữa thứ hạng trên 2 datasets
- Trường hợp điển hình: phương pháp nào "overfit" vào đặc trưng một loại log?
- **So sánh quan trọng:** hiệu quả trên fault injection có kiểm soát (HDFS_v3) vs. lỗi tự nhiên production (BGL)
- Phân tích: phương pháp nào ổn định nhất? Phương pháp nào phụ thuộc vào đặc tính dữ liệu?
- Heatmap thay đổi thứ hạng

### 4.3. RQ3: Chi phí tính toán

- Bảng chi phí: thời gian huấn luyện, độ trễ suy luận, bộ nhớ GPU/RAM
- Biểu đồ scatter: F1 vs. inference latency
- Biểu đồ: F1 vs. total memory footprint
- **Phân tích đặc biệt:** 
  - Chi phí API LLM của LogRAG (USD + latency) vs. thời gian chạy LightAD (giây) vs. LogFormer (phút)
  - Throughput (samples/second) cho kịch bản thời gian thực
  - Pareto frontier: phương pháp nào tối ưu về đánh đổi F1 vs. cost?

### 4.4. RQ4: Phân tích lỗi và khả năng giải thích

- **Taxonomy lỗi FP/FN:**
  - Bảng tổng hợp tỷ lệ từng nhóm lỗi theo phương pháp và dataset
  - So sánh đặc điểm lỗi: HDFS_v3 (fault injection) vs. BGL (lỗi tự nhiên)
  - Case study minh họa (ví dụ cụ thể cho từng nhóm lỗi)
- **Đánh giá định tính khả năng giải thích:**
  - **LightAD:** ví dụ feature importance (SLFN/DT), nearest neighbor analysis (KNN)
  - **LogFormer:** ví dụ attention visualization — log events nào được chú ý
  - **LogRAG:** ví dụ LLM reasoning output — giải thích bằng ngôn ngữ tự nhiên
- **So sánh chất lượng giải thích:** actionability, clarity, correctness
- Phân tích liên hệ giữa kiểu lỗi và đặc tính dữ liệu

---

## CHƯƠNG 5: THẢO LUẬN

### 5.1. Tổng hợp phát hiện chính theo RQ

- Bảng tóm tắt câu trả lời cho mỗi RQ (RQ1-RQ4)
- Phát hiện bất ngờ / mâu thuẫn với kết quả bài báo gốc
- So sánh hiệu quả ba họ kỹ thuật: ML cổ điển siêu nhẹ vs. Transformer vs. LLM+RAG

### 5.2. Khuyến nghị lựa chọn phương pháp theo điều kiện thực tế

| Ràng buộc | Khuyến nghị (dự kiến) |
|---|---|
| **Tài nguyên hạn chế, cần nhanh, không có GPU** | LightAD (KNN/DT/SLFN) |
| **Yêu cầu F1 cao nhất, có GPU, có thể chấp nhận training time dài** | LogFormer |
| **Cần giải thích anomaly bằng ngôn ngữ tự nhiên, giảm FP quan trọng, có ngân sách API** | LogRAG |
| **Log từ hệ phân tán (HDFS-like)** | (Tùy thuộc kết quả RQ1-RQ2) |
| **Log từ siêu máy tính (BGL-like)** | (Tùy thuộc kết quả RQ1-RQ2) |
| **Triển khai production thời gian thực (latency < 100ms)** | LightAD |
| **Cần khả năng giải thích actionable** | LogRAG (LLM reasoning) > LightAD (minh bạch) > LogFormer (attention) |

### 5.3. So sánh ba họ kỹ thuật

- **ML cổ điển (LightAD):** Ưu điểm nhanh, nhẹ, giải thích được; hạn chế không khai thác ngữ cảnh tuần tự phức tạp
- **Transformer (LogFormer):** Ưu điểm khai thác ngữ cảnh tốt, pre-training hiệu quả; hạn chế cần GPU, training time dài
- **LLM+RAG (LogRAG):** Ưu điểm giảm FP, giải thích tốt nhất; hạn chế chi phí cao (API + latency), phụ thuộc LLM quality

### 5.4. Hạn chế của nghiên cứu

- Chỉ đại diện cho **3 phương pháp** và **2 bộ dữ liệu**
- Các họ kỹ thuật khác (GNN, Transformer đa phương thức, thống kê nâng cao) không được đánh giá
- Số đo hiệu năng trên 1 môi trường phần cứng cụ thể
- Yêu cầu đặc thù (API LLM cho LogRAG)
- Không đánh giá streaming/online detection
- Không đánh giá trên log đám mây (OpenStack)

### 5.5. Threats to Validity

- **Internal validity:** data leakage, hyperparameter fairness, random seed consistency
- **External validity:** 2 datasets không đại diện cho mọi hệ thống; thiếu đánh giá log đám mây
- **Construct validity:** metric definition consistency, label granularity differences
- **Conclusion validity:** statistical significance, multiple comparisons

### 5.6. Hướng nghiên cứu tiếp theo

- **Mở rộng bộ dữ liệu:** thêm OpenStack và các dataset đám mây khác
- **Mở rộng phương pháp:** đánh giá GNN (Logs2Graph), Transformer đa phương thức (CoLog), thống kê (SemPCA)
- **Streaming/online detection:** đánh giá trong môi trường streaming thời gian thực
- **Ensemble methods:** kết hợp ưu điểm của nhiều họ phương pháp
- **AutoML for LogAD:** tự động hóa lựa chọn phương pháp
- **Đánh giá trên dữ liệu log thương mại thực tế**
- **Phát hiện sớm (early detection):** đánh giá khả năng phát hiện khi chỉ có một phần chuỗi log

---

## CHƯƠNG 6: KẾT LUẬN

- Tóm tắt câu trả lời cho 4 RQ
- Đóng góp chính:
  1. Benchmark thống nhất cho 3 phương pháp đại diện (ML cổ điển, Transformer, LLM+RAG) trên 2 datasets chuẩn
  2. Phân tích chi phí tính toán so sánh trực tiếp
  3. Đánh giá ổn định giữa fault injection và lỗi tự nhiên
  4. Taxonomy lỗi và so sánh khả năng giải thích
  5. Khuyến nghị thực tiễn lựa chọn phương pháp
- Lời kết và ý nghĩa thực tiễn

---

## TÀI LIỆU THAM KHẢO

### Bài báo gốc của 3 phương pháp đánh giá:
1. Yu, B., Yao, J., Fu, Q., et al. (2024). *Deep Learning or Classical Machine Learning? An Empirical Study on Log-Based Anomaly Detection.* ICSE 2024. **(LightAD)**
2. Guo, H., Yang, J., Liu, J., et al. (2024). *LogFormer: A Pre-train and Tuning Pipeline for Log Anomaly Detection.* AAAI 2024. **(LogFormer)**
3. Jiang, C. et al. (2024). *Leveraging RAG-Enhanced Large Language Model for Semi-Supervised Log Anomaly Detection.* ISSRE 2024. **(LogRAG)**

### Phương pháp khác (để mở rộng trong tương lai):
4. Nasirzadeh, M., Tahmoresnezhad, J., & Rashidi-Khazaee, P. (2025). *A unified framework for detecting point and collective anomalies in operating system logs via collaborative transformers.* Scientific Reports, 15, Article 27693. **(CoLog)**
5. Li, Z., Shi, J., & van Leeuwen, M. (2024). *Graph Neural Networks based Log Anomaly Detection and Explanation.* ICSE-Companion 2024. **(Logs2Graph)**
6. *Try with Simpler – An Evaluation of Improved Principal Component Analysis in Log-based Anomaly Detection.* **(SemPCA)**

### Công trình nền tảng:
7. He, P., Zhu, J., Zheng, Z., & Lyu, M. R. (2017). *Drain: An Online Log Parsing Approach with Fixed Depth Tree.* ICWS 2017.
8. Du, M., Li, F., Zheng, G., & Srikumar, V. (2017). *DeepLog: Anomaly Detection and Diagnosis from System Logs through Deep Learning.* CCS 2017.
9. Meng, W., et al. (2019). *LogAnomaly: Unsupervised Detection of Sequential and Quantitative Anomalies in Unstructured Logs.* IJCAI 2019.
10. Zhang, X., et al. (2019). *Robust Log-Based Anomaly Detection on Unstable Log Data.* FSE 2019. (LogRobust)
11. Guo, H., et al. (2021). *LogBERT: Log Anomaly Detection via BERT.* IJCNN 2021.

### Bộ dữ liệu:
12. Zhu, J., et al. (2023). *Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics.* ISSRE 2023.
13. Zhou, X., et al. (2014). *TraceBench: An Open Data Set for Trace-oriented Monitoring.* CloudCom 2014. (HDFS_v3)
14. Oliner, A. & Stearley, J. (2007). *What Supercomputers Say: A Study of Five System Logs.* DSN 2007. (BGL)

### Phương pháp luận:
15. ACM SIGSOFT Empirical Standards (thiết kế và báo cáo nghiên cứu thực nghiệm)

---

## PHỤ LỤC

### Phụ lục A: Bảng tổng hợp bài báo tham khảo (20-30 bài)
- Bảng trích xuất: tên, năm, kiến trúc, kiểu học, dữ liệu, metric, hạn chế

### Phụ lục B: Bảng đặc tả kỹ thuật chi tiết 3 phương pháp
- Input/Output format
- Dependencies và phiên bản
- Kiến trúc mô hình (sơ đồ)
- Training procedure
- Inference procedure

### Phụ lục C: Cấu hình siêu tham số chi tiết
- Bảng siêu tham số cuối cùng cho mỗi baseline × mỗi dataset
- Grid search ranges đã thử (nếu có)
- Lệnh chạy chính xác

### Phụ lục D: Kết quả thô đầy đủ
- Bảng kết quả cho mọi lần chạy (không chỉ trung bình)
- Confusion matrices
- Script tạo biểu đồ

### Phụ lục E: Mô tả pipeline tái lập
- Hướng dẫn cài đặt (Docker / virtualenv)
- Hướng dẫn chạy từng bước
- Cấu trúc repository

### Phụ lục F: Danh sách trường hợp lỗi trong phân tích lỗi (RQ4)
- Ví dụ cụ thể FP/FN với log content
- Phân nhóm và giải thích

### Phụ lục G: Checklist thực nghiệm
- Threats to validity checklist
- Reproducibility checklist
