# DANH SÁCH ĐỌC BẮT BUỘC — Bài báo quan trọng cho luận văn

> **Đây không phải danh sách khảo sát đầy đủ.** Toàn bộ ~45+ công trình khảo sát nằm ở
> `chuyende1/survey/survey_matrix.csv`. File này chỉ giữ **5–10 bài thật sự then chốt** —
> loại mà nếu bảo vệ và bị hỏi chi tiết mà không trả lời được thì mất điểm ngay.
>
> Quy tắc gắn cờ: `README.md` mục "Quy định riêng của học viên" phần D.
> Tiêu chí "quan trọng": xem cùng mục đó.

**Cách dùng:** mỗi khi tôi (Claude Code) phát hiện một bài đáng gắn cờ, tôi thêm một dòng
vào bảng dưới đây, viết một mục chi tiết ở phần "Chi tiết từng bài", và **nói rõ trong câu
trả lời** rằng vừa gắn cờ — không im lặng thêm vào. Học viên tick cột "Đã đọc kỹ" sau khi
đọc xong, và có thể ghi lại điều rút ra ở phần ghi chú.

---

## Bảng theo dõi

| # | ref_key | Ngày gắn cờ | Vì sao quan trọng (rút gọn) | Mức ưu tiên | Đã đọc kỹ |
|---|---|---|---|---|---|
| 1 | `SenticNet-7` | 02/09/2026 | **GVHD đã chọn làm TLTK chính số [1]** trong bản duyệt. Là nền lý thuyết trực tiếp của hướng neuro-symbolic — thứ CĐ2 sẽ mở rộng | 🔴 | ☐ |
| 2 | `PhoBERT` | 02/09/2026 | **GVHD đã chọn làm TLTK chính số [2]** trong bản duyệt. Là baseline `phobert` và là bộ mã hoá nền của cả Sentic-GCN lẫn NS-MGAT | 🔴 | ☐ |
| 3 | `UIT-ViSFD` | 09/09/2026 | **Bài giới thiệu chính tập dữ liệu của đề tài.** Quyết định câu "kết quả của em có so được với bài báo không" — xem REQ-008 rào cản 1 | 🔴 | ☐ *đã đọc 18/09 · chờ đạt trắc nghiệm 01* |
| 4 | `ASGCN` | 09/09/2026 | **Baseline chính thức** (bản GVHD duyệt mục 4). Ý tưởng đồ thị phụ thuộc theo khía cạnh — nền trực tiếp của CĐ2. Có một vấn đề thiết kế phải giải trước CD1.6a | 🔴 | ☐ |
| 5 | `Sentic-GCN` | 09/09/2026 | **Baseline chính thức.** Là mô hình gần NS-MGAT nhất trong các công trình đã có — hội đồng chắc chắn hỏi "khác gì Sentic-GCN?" | 🔴 | ☐ |
| 6 | `ATAE-LSTM` | 09/09/2026 | Kiến trúc mà baseline `bilstm` (CD1.4b) dựa theo. Cần để nói đúng "của em khác bản gốc ở đâu" | 🟡 | ☐ |
| 7 | `PhoBERT-ViSFD-2022` | 09/09/2026 | Công trình đã áp PhoBERT lên chính UIT-ViSFD → **dải tham chiếu để biết kết quả CD1.5 có bất thường không** | 🟡 | ☐ |

**Mức ưu tiên:** 🔴 phải đọc trước khi viết Chương 3/5 · 🟡 nên đọc trước khi bảo vệ · 🟢 tham khảo thêm nếu có thời gian

---

## Chi tiết từng bài

### `SenticNet-7` — SenticNet 7: A Commonsense-based Neurosymbolic AI Framework for Explainable Sentiment Analysis (Cambria et al., LREC 2022)

**Ngày gắn cờ:** 02/09/2026 · **Mức ưu tiên:** 🔴
**Nguồn:** ACL Anthology <https://aclanthology.org/2022.lrec-1.408/> · PDF mở: <https://sentic.net/senticnet-7.pdf>
Cambria, Liu, Decherchi, Xing, Kwok — *LREC 2022*, tr. 3829–3839.
Trích dẫn gốc lấy từ `docs/Tom_Tat_Dinh_Huong_Final.docx` mục 5, TLTK chính **[1]**

**Vì sao bài này quan trọng với luận văn của bạn:**

Đây là bài **GVHD tự chọn** làm tài liệu tham khảo chính số [1] — tức cô coi nó là nền lý
thuyết của đề tài. Nó không chỉ "liên quan": nó là công trình định nghĩa chính khái niệm
*neurosymbolic cho phân tích cảm xúc có giải thích được* — đúng cụm từ trong tên đề tài của bạn.

Ba điểm chạm trực tiếp:

1. **Tri thức cảm xúc** mà `senticgcn` dùng chính là SenticNet. Đọc bài này mới hiểu được
   dữ liệu đó có cấu trúc gì, và vì sao không có bản tiếng Việt tương đương (liên quan GAP-002).
2. **Khả năng giải thích** — bản duyệt mục 2 nêu điểm mới là *"đường dẫn lý do"* thay vì hộp
   đen. SenticNet 7 là mốc so sánh cho tuyên bố đó.
3. **Định vị đóng góp CĐ2** — bản duyệt mục 2 nói khác biệt của bạn là luật không chỉ thêm
   cạnh mà còn *cung cấp mức độ tin cậy*. Muốn phát biểu được "khác với SenticNet ở chỗ nào"
   thì phải biết SenticNet làm gì.

**Câu hỏi cần trả lời được sau khi đọc:**

- SenticNet 7 biểu diễn tri thức cảm xúc dưới dạng gì, và lấy từ đâu?
- Phần "symbolic" trong đó là luật, là đồ thị, hay là ontology? Có độ tin cậy cho từng đơn vị tri thức không?
- Nó giải thích quyết định bằng cách nào? So với "đường dẫn lý do" mà bạn định làm thì khác gì?
- Có tài nguyên tiếng Việt nào tương đương không — hay đây chính là khoảng trống của đề tài?

**Trạng thái đọc:** ☐ Chưa đọc · ☐ Đã đọc lướt · ☐ Đã đọc kỹ

**Ghi chú sau khi đọc** *(điền bởi học viên):*

…

---

### `PhoBERT` — PhoBERT: Pre-trained Language Models for Vietnamese (Nguyen & Nguyen, Findings of EMNLP 2020)

**Ngày gắn cờ:** 02/09/2026 · **Mức ưu tiên:** 🔴
**Nguồn:** ACL Anthology <https://aclanthology.org/2020.findings-emnlp.92/> · arXiv <https://arxiv.org/abs/2003.00744> · mã nguồn <https://github.com/VinAIResearch/PhoBERT>
Nguyen & Nguyen — *Findings of EMNLP 2020*, tr. 1037–1042.
Trích dẫn gốc lấy từ `docs/Tom_Tat_Dinh_Huong_Final.docx` mục 5, TLTK chính **[2]**

**Vì sao bài này quan trọng với luận văn của bạn:**

GVHD chọn làm TLTK chính số [2]. Nhưng lý do thực dụng hơn: PhoBERT **xuất hiện ở ba chỗ**
trong công việc của bạn, không phải một:

1. Là baseline `phobert` — mốc so sánh chính của Chương 4.
2. Là **bộ mã hoá nền của `senticgcn`** (theo đặc tả S1.2 trong `PLAN_NSMGAT.md`) — nên nếu
   hiểu sai cách nó tách từ, cả mô hình đồ thị sẽ sai theo.
3. Sẽ là bộ mã hoá nền của **NS-MGAT ở CĐ2**.

Điểm kỹ thuật bắt buộc phải nắm: PhoBERT **yêu cầu văn bản đã tách từ** bằng VnCoreNLP.
Đây là lý do bước tiền xử lý S0.3 tồn tại, và là chỗ dễ sai nhất khi gộp biểu diễn subword
về mức token để dựng đồ thị.

**Câu hỏi cần trả lời được sau khi đọc:**

- Vì sao PhoBERT cần tách từ trước, trong khi BERT tiếng Anh thì không?
- Dữ liệu tiền huấn luyện của PhoBERT là gì? *(quan trọng: nó có phủ văn bản mạng xã hội như UIT-ViSFD không — đây chính là lý do tôi từng đề xuất thêm ViSoBERT)*
- `phobert-base` khác `phobert-large` ở đâu, và vì sao chọn base?
- Khi một từ bị tách thành nhiều subword, gộp lại về mức token bằng cách nào cho đúng?

**Trạng thái đọc:** ☐ Chưa đọc · ☐ Đã đọc lướt · ☐ Đã đọc kỹ

**Ghi chú sau khi đọc** *(điền bởi học viên):*

…

---

### `UIT-ViSFD` — SA2SL: From Aspect-Based Sentiment Analysis to Social Listening System for Business Intelligence (Phan et al., 2021)

**Ngày gắn cờ:** 09/09/2026 · **Mức ưu tiên:** 🔴 **ƯU TIÊN SỐ 1 — đọc trước CD1.5**
**Nguồn:**
- arXiv (bản đọc miễn phí): <https://arxiv.org/abs/2105.15079>
- Springer (bản chính thức): <https://link.springer.com/chapter/10.1007/978-3-030-82147-0_53>
- Dữ liệu + mã nguồn: <https://github.com/LuongPhan/UIT-ViSFD>
- Bản trên HuggingFace đang dùng: <https://huggingface.co/datasets/visolex/ViSFD>

**Vì sao bài này quan trọng với luận văn của bạn:**

Đây là bài **giới thiệu chính tập dữ liệu** mà cả Chuyên đề 1 lẫn luận văn chạy trên đó.
Không đọc nó thì mọi con số của bạn không có điểm neo nào bên ngoài.

Cụ thể hơn, nó quyết định **một câu hỏi đang treo**: kết quả của bạn có so được với số công
bố không? (xem [`SoSanh_KetQua_voi_So_Cong_Bo.md`](../user-require/SoSanh_KetQua_voi_So_Cong_Bo.md)
rào cản 1). Câu trả lời phụ thuộc vào **cách bài báo chấm điểm nhiệm vụ cảm xúc** — và chỉ
đọc bài mới biết chắc.

**Điều đã tra được sẵn (09/09/2026) — nhưng CHƯA đối chiếu bản chính:**

> ⚠️ Những con số dưới đây do công cụ trích từ bản HTML của arXiv, **không phải do bạn hay
> tôi đọc bản PDF chính thức**. Chúng ở mức `da_kiem_url`, **chưa** ở mức `da_doc_toan_van`.
> **Không được trích vào báo cáo trước khi bạn tự đối chiếu.**

| | Ghi nhận được |
|---|---|
| Chia dữ liệu | 7.786 / 1.112 / 2.224 — **khớp chính xác** với `load_visfd` của repo ✅ |
| Hai giai đoạn đánh giá | *"aspect detection"* và *"sentiment prediction"* |
| Mô hình tốt nhất | Bi-LSTM + fastText |
| F1 nhiệm vụ khía cạnh | 84,48 % |
| F1 nhiệm vụ cảm xúc | 63,06 % |
| Các baseline khác | Naive Bayes 64,65/37,56 · SVM 42,63/19,69 · Random Forest 47,83/20,17 · CNN 69,70/27,16 · LSTM 80,27/52,13 |

**Câu hỏi cần trả lời được sau khi đọc** *(câu đầu là câu quan trọng nhất trong cả file này):*

- **Nhiệm vụ cảm xúc được chấm thế nào?** Mô hình có được cho sẵn khía cạnh đúng rồi mới
  gán cảm xúc (giống bài toán ACSA của bạn), hay phải tự phát hiện khía cạnh trước rồi bị
  chấm trên cặp *khía cạnh#cảm xúc*?
  → *(18/09, sau khi đọc toàn văn: **bài không nói rõ**. Đó chính là câu trả lời — và là câu
  11 của trắc nghiệm 01.)*
- Độ đo là macro-F1 hay micro-F1? Trung bình trên khía cạnh hay trên mẫu? *(macro và micro
  lệch nhau rất xa khi lớp mất cân bằng — lớp trung tính của ta chỉ 12,2 %)*
- Nhãn `{OTHERS}` được xử lý thế nào trong đánh giá của họ? *(ta loại 170 bình luận chỉ có
  nhãn này — họ có loại không, hay tính là một lớp?)*
- Bi-LSTM của họ dùng fastText mức từ. Baseline `bilstm` của ta dùng subword PhoBERT. Khác
  biệt này ảnh hưởng thế nào tới việc đặt hai con số cạnh nhau?

**Trạng thái đọc:** ☑ **Đã đọc** (học viên, 18/09/2026) · ☐ Đã đọc kỹ — *tick khi đạt [trắc nghiệm 01](../trac-nghiem/de/01_UIT-ViSFD.md)*

> 🔎 **Một chỗ nên tự kiểm khi đọc lại Bảng 3:** dòng `SER&ACC` — bài ghi tổng **2.678**, dữ liệu thật trên HuggingFace đếm được **2.878** (9 khía cạnh còn lại khớp tuyệt đối). Lệch đúng 200, khác đúng một chữ số (6 ↔ 8). Có thể là lỗi đánh máy trong bài, có thể do tôi đọc qua bản HTML bị lệch. Nếu bạn cộng các ô Pos/Neu/Neg của dòng đó ra 2.878 thì đó là lỗi đánh máy của bài — đáng ghi một dòng chú thích nếu báo cáo có chép Bảng 3.

**Ghi chú sau khi đọc** *(điền bởi học viên):*

…

---

### `ASGCN` — Aspect-based Sentiment Classification with Aspect-specific Graph Convolutional Networks (Zhang, Li & Song, EMNLP-IJCNLP 2019)

**Ngày gắn cờ:** 09/09/2026 · **Mức ưu tiên:** 🔴 — đọc trước CD1.6a (Tuần 5)
**Nguồn:**
- ACL Anthology: <https://aclanthology.org/D19-1464/> (DOI 10.18653/v1/D19-1464), tr. 4568–4578
- Mã nguồn chính chủ: <https://github.com/GeneZC/ASGCN>

**Vì sao bài này quan trọng với luận văn của bạn:**

Đây là **baseline chính thức** trong bản GVHD đã duyệt (mục 4), và là công trình đầu tiên
đặt GCN lên cây phụ thuộc cho bài toán cảm xúc theo khía cạnh — tức là **tổ tiên trực tiếp**
của NS-MGAT. Đồ thị cú pháp bạn đã dựng ở CD1.3 chính là để chạy mô hình này.

**Và có một vấn đề thiết kế phải giải TRƯỚC khi cài — đọc bài này là cách giải:**

ASGCN làm *aspect-term*: khía cạnh là một **cụm từ nằm trong câu**, ở một vị trí cụ thể. Nhờ
vậy mô hình đo được "khoảng cách từ từ cảm xúc **tới** khía cạnh" trên đồ thị — đó là ý
tưởng cốt lõi của nó.

Nhưng UIT-ViSFD là *aspect-category*: `BATTERY` là một mã tiếng Anh **không xuất hiện ở đâu
trong câu tiếng Việt**. **Không có điểm neo trên đồ thị để đo khoảng cách tới.**

Nếu tới CD1.6a mới phát hiện điều này thì đã muộn.

**Câu hỏi cần trả lời được sau khi đọc:**

- ASGCN dùng vị trí của khía cạnh trong câu ở **những chỗ nào** — chỉ ở bước gộp cuối, hay
  cả trong lúc lan truyền trên đồ thị?
- Nó có dùng đặc trưng "khoảng cách vị trí" (position weight) không? Nếu có thì với
  aspect-category ta thay bằng gì?
- Mô hình xử lý câu có **nhiều** khía cạnh thế nào — chạy lại đồ thị cho từng khía cạnh, hay
  một lần cho cả câu?
- Cạnh phụ thuộc có hướng hay vô hướng? Có thêm cạnh ngược và tự vòng không? *(so với
  `SyntacticGraphBuilder` của ta — xem tài liệu GAP-007)*
- Bài báo có bàn tới trường hợp cây phụ thuộc bị **đứt thành nhiều mảnh** không? *(đúng
  GAP-007 của ta — 52,2 % Example bị chia cắt)*

**Trạng thái đọc:** ☐ Chưa đọc · ☐ Đã đọc lướt · ☐ Đã đọc kỹ

**Ghi chú sau khi đọc** *(điền bởi học viên):*

…

---

### `Sentic-GCN` — Aspect-based sentiment analysis via affective knowledge enhanced graph convolutional networks (Liang, Su, Gui, Cambria & Xu, Knowledge-Based Systems 2022)

**Ngày gắn cờ:** 09/09/2026 · **Mức ưu tiên:** 🔴 — đọc trước CD1.6b (Tuần 6)
**Nguồn:**
- ScienceDirect (bản chính thức): <https://www.sciencedirect.com/science/article/abs/pii/S0950705121009059>
  — Knowledge-Based Systems, vol. 235, bài số 107643
- **Bản đọc miễn phí** (kho lưu trữ ĐH Warwick): <https://wrap.warwick.ac.uk/id/eprint/160893/>
- Mã nguồn chính chủ: <https://github.com/BinLiang-NLP/Sentic-GCN>
- Bản cài đặt lại có tài liệu: <https://sgnlp.aisingapore.net/docs/model/senticgcn.html>

**Vì sao bài này quan trọng với luận văn của bạn:**

Trong toàn bộ các công trình đã có, đây là **mô hình gần NS-MGAT nhất**: nó cũng lấy tri
thức cảm xúc từ SenticNet đưa vào đồ thị phụ thuộc. Nói cách khác, nó là công trình mà hội
đồng sẽ dùng để hỏi câu khó nhất:

> *"Vậy NS-MGAT của em khác Sentic-GCN ở chỗ nào?"*

Không trả lời được câu này thì đóng góp của luận văn không đứng vững. Mà muốn trả lời thì
phải biết Sentic-GCN làm **chính xác** những gì — không thể trả lời từ phần tóm tắt.

Liên quan trực tiếp tới [`GAP-002`](../gaps/GAP-002_senticgcn-can-tu-dien-cam-xuc.md):
Sentic-GCN cần SenticNet, mà SenticNet không có bản tiếng Việt tương đương.

**Câu hỏi cần trả lời được sau khi đọc:**

- Tri thức từ SenticNet được đưa vào đồ thị bằng cách nào — **thêm cạnh mới**, hay **đổi
  trọng số cạnh đã có**? *(bản duyệt mục 2 nói điểm mới của bạn là luật vừa thêm cạnh vừa
  cung cấp mức độ tin cậy — muốn nói "khác" thì phải biết họ làm gì)*
- Mỗi đơn vị tri thức có kèm **độ tin cậy** không, hay coi như đúng tuyệt đối?
- Nếu một từ **không có** trong SenticNet thì mô hình xử lý ra sao? *(rất quan trọng với ta —
  tiếng Việt sẽ thiếu rất nhiều)*
- Bài có làm **thí nghiệm loại bỏ** (ablation) tách riêng phần đóng góp của tri thức cảm xúc
  khỏi phần cú pháp không? Nếu có, phần tri thức đóng góp bao nhiêu điểm?
- Mô hình có giải thích được quyết định không, hay chỉ tăng điểm số?

**Trạng thái đọc:** ☐ Chưa đọc · ☐ Đã đọc lướt · ☐ Đã đọc kỹ

**Ghi chú sau khi đọc** *(điền bởi học viên):*

…

---

### `ATAE-LSTM` — Attention-based LSTM for Aspect-level Sentiment Classification (Wang, Huang, Zhu & Zhao, EMNLP 2016)

**Ngày gắn cờ:** 09/09/2026 · **Mức ưu tiên:** 🟡 — nên đọc trước khi viết Chương 4
**Nguồn:**
- ACL Anthology: <https://aclanthology.org/D16-1058/> (DOI 10.18653/v1/D16-1058), tr. 606–615
- Mã nguồn của tác giả: <https://github.com/thuwyq/EMNLP16-atae-lstm>

**Vì sao bài này quan trọng với luận văn của bạn:**

Baseline `bilstm` bạn vừa chạy xong ở CD1.4b **dựa theo kiến trúc này**. Bài báo mô tả hai
biến thể, và ta dùng biến thể thứ hai:

- **AT-LSTM** — chỉ dùng vector khía cạnh làm truy vấn cho attention
- **ATAE-LSTM** — *"nối thêm vector khía cạnh vào từng vector từ"*, cộng với AT-LSTM

Đúng hai chỗ nhìn thấy khía cạnh mà [`phiếu bàn giao CD1.4b`](../notes/CD1.4b_bilstm.md) mục
3.1 mô tả. Nhưng **cài đặt của ta khác bản gốc**: ta dùng subword PhoBERT thay vì từ mức
word + GloVe. Muốn viết đúng câu *"của em khác bản gốc ở đâu và vì sao"* thì phải biết bản
gốc làm gì.

Mức ưu tiên 🟡 chứ không 🔴 vì baseline này đã chạy xong và kết quả không phụ thuộc việc đọc
bài — nhưng phần **mô tả phương pháp** trong Chương 4 thì phụ thuộc.

**Câu hỏi cần trả lời được sau khi đọc:**

- Vì sao nối vector khía cạnh vào **từng token** lại giúp ích, thay vì chỉ dùng ở bước gộp?
  Bài có đo tách riêng đóng góp của hai chỗ không?
- ATAE-LSTM chạy trên aspect-**term** hay aspect-**category**? *(SemEval-2014 có cả hai —
  cần biết chính xác để nói đúng trong Chương 2)*
- Bài dùng độ đo gì, trên tập nào? *(để điền cột `do_do_bao_cao` và `ket_qua_tot_nhat`)*

**Trạng thái đọc:** ☐ Chưa đọc · ☐ Đã đọc lướt · ☐ Đã đọc kỹ

**Ghi chú sau khi đọc** *(điền bởi học viên):*

…

---

### `PhoBERT-ViSFD-2022` — A New Approach for Vietnamese Aspect-Based Sentiment Analysis (2022)

**Ngày gắn cờ:** 09/09/2026 · **Mức ưu tiên:** 🟡 — hữu ích nhất **ngay trước khi chạy CD1.5**
**Nguồn:** IEEE Xplore: <https://ieeexplore.ieee.org/document/9953759/>

> ⚠️ **Chưa xác minh đầy đủ.** IEEE chặn truy cập nên tôi chưa đọc được nội dung. Thông tin
> duy nhất chắc chắn: bài này áp PhoBERT lên chính UIT-ViSFD. Tên tác giả, năm, và mọi con
> số **phải do bạn kiểm chứng**. Trường có thể có quyền truy cập IEEE — thử qua thư viện ĐH.

**Vì sao bài này quan trọng với luận văn của bạn:**

Đây là công trình dùng **cùng mô hình** (PhoBERT) trên **cùng tập dữ liệu** (UIT-ViSFD) mà
CD1.5 sắp chạy. Nó cho bạn thứ mà không bài nào khác cho được: **một dải để biết kết quả
của mình có bình thường không**.

Khi chạy `phobert` ở Tuần 4:

- Kết quả **thấp hơn hẳn** dải này → gần như chắc chắn **có bug** (sai learning rate, quên
  mở băng encoder, tokenize lệch), **không phải** một phát hiện khoa học.
- Kết quả **cao bất thường** → phải nghi **rò rỉ dữ liệu**.

Cả hai chiều đều cần một con số tham chiếu. Đó là lý do bài này nên đọc **trước** CD1.5 chứ
không phải tới Tuần 13.

**Câu hỏi cần trả lời được sau khi đọc:**

- Họ đạt bao nhiêu trên nhiệm vụ cảm xúc, đo bằng độ đo gì?
- Họ dùng `phobert-base` hay `phobert-large`? Siêu tham số nào? *(để `configs/phobert.yaml`
  của ta không đặt bừa)*
- Họ đặt bài toán giống bài báo gốc UIT-ViSFD (tự phát hiện khía cạnh) hay giống ta (cho sẵn
  khía cạnh)?

**Trạng thái đọc:** ☐ Chưa đọc · ☐ Đã đọc lướt · ☐ Đã đọc kỹ

**Ghi chú sau khi đọc** *(điền bởi học viên):*

…

---

_(mẫu cho bài mới — copy khối dưới đây mỗi khi gắn cờ thêm)_

### `<ref_key>` — `<tên bài, năm>`

**Ngày gắn cờ:** …
**Mức ưu tiên:** …
**Nguồn:** `<link tới bài, hoặc "xem nguon_url trong survey_matrix.csv">`

**Vì sao bài này quan trọng với luận văn của bạn** *(không viết chung chung "liên quan đề
tài" — phải nói rõ nó chạm vào phần nào của NS-MGAT hoặc của CĐ1):*

…

**Câu hỏi cần trả lời được sau khi đọc** *(để tự kiểm tra đã đọc kỹ, không chỉ đọc lướt):*

- …
- …

**Trạng thái đọc:** ☐ Chưa đọc · ☐ Đã đọc lướt · ☐ Đã đọc kỹ

**Ghi chú sau khi đọc** *(điền bởi học viên):*

…
