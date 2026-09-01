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

**Mức ưu tiên:** 🔴 phải đọc trước khi viết Chương 3/5 · 🟡 nên đọc trước khi bảo vệ · 🟢 tham khảo thêm nếu có thời gian

---

## Chi tiết từng bài

### `SenticNet-7` — SenticNet 7: A Commonsense-based Neurosymbolic AI Framework for Explainable Sentiment Analysis (Cambria et al., LREC 2022)

**Ngày gắn cờ:** 02/09/2026 · **Mức ưu tiên:** 🔴
**Nguồn:** `[CẦN TÌM: link LREC 2022 proceedings]` — trích dẫn lấy từ
`docs/Tom_Tat_Dinh_Huong_Final.docx` mục 5, TLTK chính **[1]**

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
**Nguồn:** `[CẦN TÌM: link Findings of EMNLP 2020]` — trích dẫn lấy từ
`docs/Tom_Tat_Dinh_Huong_Final.docx` mục 5, TLTK chính **[2]**

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
