# GAP-006 — Lập plan mà không hỏi "đã có tài liệu nào GVHD duyệt chưa?"

**Ngày phát hiện:** 02/09/2026 · **Phát hiện bởi:** học viên
**Loại:** kế hoạch · **Mức độ:** **nghiêm trọng** (lệch nền tảng) · **Trạng thái:** 🟡 Đang sửa

---

## 1. Sai ở đâu

Toàn bộ `pLan/chuyende1/PLAN_CHUYENDE1.md` (15 tuần, 13 gói việc) và phiếu xin ý kiến GVHD
được soạn **chỉ dựa trên `pLan/PLAN_NSMGAT.md`**, mà không hề biết tồn tại
`docs/Tom_Tat_Dinh_Huong_Final.docx` — bản **Tóm tắt định hướng nghiên cứu đã được GVHD
duyệt**, tức tài liệu có thẩm quyền cao hơn mọi plan nội bộ.

Hệ quả cụ thể, đối chiếu bản duyệt (mục 4) với plan tôi soạn:

| Baseline | Bản GVHD duyệt | Plan tôi soạn |
|---|---|---|
| PhoBERT fine-tune | ✅ mục 4 | ✅ |
| **ASGCN** | ✅ mục 4 | ❌ **THIẾU** — tôi chỉ để làm phương án dự phòng trong GAP-002 |
| Sentic-GCN | ✅ mục 4 | ✅ |
| LLM | ✅ **GPT-4o**, zero/few-shot, **~500 câu** | mơ hồ "LLM", 1.000 mẫu |
| BiLSTM / Bi-GRU | ✅ mục 1 (thực nghiệm lại) | ❌ tôi chủ động loại |
| Mô hình dựa trên từ điển | ✅ mục 1 (thực nghiệm lại) | ❌ tôi chủ động loại |
| ViSoBERT | ❌ không có trong bản duyệt | ✅ tôi tự thêm |

Ngoài baseline, bản duyệt còn chứa những thứ tôi đã phải **đoán hoặc treo câu hỏi**:

| Thông tin | Tôi đã làm gì | Bản duyệt ghi sẵn |
|---|---|---|
| Tên đề tài trên bìa | Tự soạn bản nháp, treo câu hỏi cho GVHD | Có tên chính thức đầy đủ (Việt + Anh) |
| Khoá học | Không biết | 2026A |
| Đơn vị công tác GVHD | Không biết | ĐH Nông Lâm TP.HCM |
| Quy mô UIT-ViSFD | Suy từ dữ liệu đã xử lý | 11.122 mẫu (khớp: 7.786+1.112+2.224) |
| Link dataset | Không có | HuggingFace + GitHub + VLSP chính thức |
| Tài liệu tham khảo chính | Chưa có | SenticNet 7 (LREC 2022), PhoBERT (EMNLP 2020) |

## 2. Phát hiện thế nào

Học viên chất vấn: *"tại sao phải hỏi GVHD về 4 baseline? các baseline khảo sát đã ghi rõ
trong file docs/Tom_Tat_Dinh_Huong_Final.docx, file này đã được GVHD duyệt"*.

Đáng lưu ý: câu hỏi của học viên là **"vì sao còn phải hỏi"** — nhưng khi mở file ra kiểm
thì lộ ra vấn đề ngược lại và nặng hơn: không phải plan thừa một câu hỏi, mà là plan
**thiếu một baseline chính thức** (ASGCN).

## 3. Nguyên nhân gốc

**Không bao giờ đặt câu hỏi "đề tài này đã có tài liệu nào được GVHD phê duyệt chưa?"**
trước khi lập kế hoạch 15 tuần.

Tôi đã rà rất kỹ *nội bộ repo* (đọc `PLAN_NSMGAT.md`, `README.md`, 3 file hợp đồng, schema
`metrics.json`, mẫu UTE trong `forms/`) — nhưng chỉ rà những gì **đã nằm sẵn trong repo**.
Không hỏi về tài liệu học vụ **bên ngoài** repo: biên bản duyệt, tóm tắt định hướng, email
trao đổi với GVHD.

Đây là một biến thể của cùng mẫu hỏng đã ghi ở GAP-004 và GAP-005: *tin vào nguồn có sẵn
trong tầm tay mà không hỏi nguồn nào có thẩm quyền cao hơn*. GAP-005 là chép sai tên/học vị
từ `README.md`; GAP-006 là lập cả kế hoạch từ plan nội bộ trong khi có văn bản đã duyệt.

**Về mốc thời gian:** ở lần khảo sát repo đầu tiên (27/08), `find` liệt kê `docs/` chỉ ra 5
file `.md`, không có file `.docx` này — nhiều khả năng file được chép vào sau đó (thư mục
`docs/` có mtime 02/09). Nhưng điều đó **không gỡ tội**: đúng ra tôi phải *hỏi* ngay từ đầu
"có tài liệu nào GVHD đã duyệt không?", chứ không chờ nó tự xuất hiện trong thư mục.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Mức độ |
|---|---|
| `PLAN_CHUYENDE1.md` mục 2 (danh sách baseline) | Phải sửa — thiếu ASGCN, thiếu BiLSTM, thiếu lexicon |
| `PLAN_CHUYENDE1.md` mục 4 (lịch Tuần 3–7) | Phải sửa — từ 4 mô hình lên 6 |
| `PLAN_CHUYENDE1.md` mục 11 câu 3 (hỏi GVHD duyệt baseline) | **Thừa** — đã duyệt rồi |
| Bìa cuốn chuyên đề (`build_cd1_report.py`) | Phải sửa — dùng tên đề tài chính thức, bỏ bản nháp tôi tự đặt |
| `XinYKien-GVHD_Baseline.docx/.md` | Phần lớn thành thừa — xem mục 5 |
| GAP-002 (Sentic-GCN cần từ điển cảm xúc) | **Nhẹ đi** — ASGCN nay là baseline chính thức riêng, nên phép so "cú pháp thuần vs cú pháp + cảm xúc" có sẵn, không cần chọn A/B/C nữa |
| GAP-004 (lệch tên `gpt4o_zeroshot` vs `llm_zs`) | **Đã giải quyết** — tên `gpt4o_zeroshot` trong `PLAN_NSMGAT.md` truy về đúng bản duyệt (GPT-4o). Giữ tên gốc, bỏ đề xuất đổi thành `llm_zs` |
| Chưa chạy thí nghiệm nào | ✅ **May mắn**: chưa có số liệu nào phải huỷ |

## 5. Đã sửa / đang sửa thế nào

1. Cập nhật `PLAN_CHUYENDE1.md`: danh sách baseline theo đúng bản duyệt (6 mô hình + 1 tuỳ
   chọn), lịch Tuần 3–7, và ghi nhận bản duyệt là **nguồn có thẩm quyền cao nhất**.
2. Sửa tên đề tài trên bìa thành tên chính thức trong bản duyệt.
3. Đóng GAP-004 (giữ tên `gpt4o_zeroshot`), hạ mức GAP-002.
4. Gắn cờ 2 tài liệu tham khảo chính của bản duyệt vào `doc_bat_buoc.md` theo REQ-005.
5. Thu hẹp phiếu xin ý kiến GVHD: bỏ câu hỏi về baseline, giữ lại phần thật sự còn cần hỏi.

## 6. Bài học

**Trước khi lập bất kỳ kế hoạch học vụ nào, hỏi thẳng học viên: "đề tài đã có tài liệu nào
được GVHD hoặc nhà trường phê duyệt chưa? (tóm tắt định hướng, đề cương, biên bản duyệt)".**
Không chờ tài liệu tự xuất hiện trong repo — tài liệu học vụ thường nằm ngoài repo, trong
email hoặc máy cá nhân.

Thứ tự thẩm quyền, từ cao xuống thấp, nay ghi rõ trong `PLAN_CHUYENDE1.md` mục 0:

1. Văn bản đã được GVHD/nhà trường duyệt (`docs/Tom_Tat_Dinh_Huong_Final.docx`)
2. `pLan/PLAN_NSMGAT.md` — đặc tả kỹ thuật
3. `pLan/chuyende1/PLAN_CHUYENDE1.md` — lịch và sản phẩm nộp

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — sai sót nội bộ về quy trình lập kế hoạch, phát hiện trước khi chạy thí
      nghiệm nào, không ảnh hưởng kết quả nghiên cứu. Nhưng **danh sách baseline đã sửa thì
      có** ảnh hưởng trực tiếp tới Chương 4.
