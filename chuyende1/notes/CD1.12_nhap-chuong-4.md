# CD1.12 (sớm) — Bản nháp Chương 4: thực nghiệm và so sánh

**Ngày:** 06/10/2026 · **Trạng thái:** nháp lần một, còn 13 chỗ đánh dấu · **Step kế:** chờ học viên chọn

Plan xếp thứ tự viết là Chương 4 trước, rồi 5, 3, cuối cùng 1, 2, 6. Chương 3 đã có nháp từ
05/10. Phiếu này ghi lại lần viết đầu của Chương 4, làm sớm hơn lịch (Tuần 11) vì 18 lần chạy
đã đủ để viết bốn trong bảy mục.

---

## 1. ĐÃ LÀM GÌ

| File | Việc | Lên GitHub? |
|---|---|---|
| `chuyende1/report/nhap/Chuong4_ThucNghiem.md` | Tạo. Bảy mục 4.1 đến 4.7, tám bảng, một công thức, tám tài liệu | Không, đã bị `.gitignore` chặn |
| `chuyende1/gaps/GAP-028_*.md` + `INDEX.md` | Tạo. Giao thức trong plan lệch với việc đã chạy | Có |
| `chuyende1/notes/CD1.12_nhap-chuong-4.md` | Phiếu này | Có |

Ba đoạn mã tạm dùng để tính số nằm ở thư mục nháp của phiên làm việc, không vào kho.

**Bổ sung cùng ngày, sau câu hỏi của học viên "không phải viết trong file Word à?":** đúng,
cuốn nộp là `chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx`, và bản nháp Markdown chưa hề vào
đó. Đã thêm:

| File | Việc | Lên GitHub? |
|---|---|---|
| `scripts/nhap_chuong_vao_docx.py` | Tạo. Thay phần thân của một chương trong cuốn Word bằng file Markdown | Có |
| `tests/test_nhap_chuong_vao_docx.py` | Tạo. 7 test trên một cuốn Word tí hon | Có |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx` | **Chương 4 đã vào**: 71 khối, 8 bảng, mục 4.1.1 và 4.1.2 là mục cấp 3 | Không |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong.20261006-002023.docx.bak` | Bản sao lưu khung rỗng trước khi ghi. **File sinh ra, bạn tự quyết xoá** | Không, đã thêm vào `.gitignore` |
| `SO_TAY_LENH.md` mục 9, `chuyende1/MODULE.md` | Thêm mục cho công cụ mới | Sổ tay không lên |

Quy ước từ nay: trong lúc còn nháp thì **sửa ở file `.md`** rồi chạy lại lệnh với `--ghi-de`.
Sửa thẳng trong Word rồi chạy `--ghi-de` sẽ mất chỗ sửa của chương đó (còn trong bản sao lưu).
Chương 3 chưa đưa vào Word, chờ học viên quyết.

## 2. ĐỂ LÀM GÌ

- Viết khi còn nhớ chi tiết thí nghiệm, đúng lý do plan chọn viết ngược.
- Lộ sớm những số còn thiếu. Viết xong mới thấy rõ mục nào đang rỗng vì việc gì chưa làm.
- Có văn bản để mang tới buổi báo cáo GVHD ở Tuần 8.

## 3. CƠ CHẾ — chương được dựng thế nào

**Mọi con số tính lại từ file gốc, không chép từ phiếu cũ.** Nguồn của từng nhóm số:

| Nhóm số | Nguồn |
|---|---|
| Bảng 4.1, 4.2, trần 80,88 % | `data/processed/visfd_{train,dev,test}.jsonl` |
| Bảng 4.5, 4.6, 4.8 | 18 file `results/<exp>/seed<N>/metrics.json` |
| Bảng 4.7 (số lần đoán, precision, recall, số sai) | 18 file `predictions.jsonl` |
| Độ phủ từ điển, đồ thị chia cắt | `results/lexicon_stats.json`, `results/syntactic_graph_stats.json` |
| Siêu tham số | `configs/*.yaml` |
| Tỉ lệ bị cắt ở 128 | Đo mới ngày 06/10, xem GAP-028 |

Độ lệch chuẩn là độ lệch chuẩn **mẫu** (chia n − 1), khớp với mọi phiếu trước.

**Trạng thái từng mục:**

| Mục | Trạng thái | Chờ gì |
|---|---|---|
| 4.1.1 Dữ liệu | Đủ số, thiếu hình và một đoạn mô tả nguồn | Bạn chép từ bài gốc; vẽ Hình 4.1 |
| 4.1.2 Tập chẩn đoán | Mới có đoạn về phủ định viết tắt | CD1.8b, c, d |
| 4.2 Giao thức | Đủ, trừ tên CPU và phiên bản thư viện | Bạn điền |
| 4.3 Mô hình | Đủ năm bậc và một biến thể | CD1.7 cho mô hình ngôn ngữ lớn |
| 4.4 Kết quả chính | Đủ, thiếu cột p-value | CD1.10 |
| 4.5 Chi phí | Có tham số và thời gian huấn luyện | CD1.10: thời gian suy luận, bộ nhớ GPU |
| 4.6 Tập chẩn đoán | Rỗng | CD1.8d |
| 4.7 Nhận xét | Viết theo số hiện có | Viết lại sau CD1.10 |

## 4. QUYẾT ĐỊNH KHI VIẾT

| Quyết định | Đã chọn | Vì sao |
|---|---|---|
| Số mô hình | Năm bậc và một biến thể, theo bản GVHD duyệt | Dàn ý ghi "bốn mô hình" là bản cũ, plan đã sửa thành sáu |
| Đơn vị kết quả | Phần trăm, hai chữ số thập phân, dấu phẩy | Quy định của trường. `metrics.json` vẫn là số gốc |
| Tên gọi | "Từ điển cảm xúc", "ASGCN nối gốc"… | Không dùng mã thí nghiệm trong văn bản gửi ra ngoài |
| "Example" | Gọi là "mẫu" | Cần một từ tiếng Việt. **Chương 2 và 3 phải dùng cùng từ này** |
| Kết luận về cú pháp và điểm cảm xúc | "Chưa cho lợi ích đo được", không viết "làm hại" hay "có ích" | Hiệu số đổi dấu theo hạt giống, chưa có kiểm định |
| Số đã công bố trên UIT-ViSFD | Không đưa vào bảng, chỉ một đoạn nói rõ không so được | Bài toán khác, đã chốt 05/10 |
| Từ điển của Sentic-GCN | Nói thẳng là suy từ nhãn tập huấn luyện | Ghi chú trong config yêu cầu; hội đồng sẽ hỏi |
| Giao thức | Viết theo config và log, không theo plan | GAP-028 |

## 5. ĐIỂM NỐI

- Chương 5 dùng lại Bảng 4.2 (PRICE giữ 40,1 % mẫu trung tính) và Bảng 4.7.
- Tóm tắt và slide lấy số từ Bảng 4.5. Sửa bảng thì phải sửa theo.
- Chương 3 đang viết phần trăm không có khoảng trắng ("84,0%"), Chương 4 viết có ("84,0 %")
  theo quy định. Phải thống nhất khi ghép.
- Tài liệu đánh số riêng trong từng chương. Khi ghép cuốn phải đánh lại theo toàn văn.

## 6. KIỂM CHỨNG

- Đã dò lại bằng tay mọi hiệu số trong phần lời với Bảng 4.5, 4.6, 4.7.
- Đã kiểm tổng hàng, tổng cột của Bảng 4.1 và 4.2.
- 1.181.184 tham số thêm của ba mô hình đồ thị bằng đúng 2 × (768 × 768 + 768).
- Kiểm văn phong: 0 gạch ngang dài, 0 backtick, 0 chỗ in đậm, 0 mã step, 0 số thập phân dấu chấm.
- Phần thân khoảng 3.990 âm tiết không tính bảng. Chưa đo ra số trang.
- **Chưa kiểm:** tỉ lệ bị cắt chưa đối chiếu với `ACSADataset`; trích dẫn VnCoreNLP viết theo
  trí nhớ, đã đánh dấu; chưa chuyển sang Word.

## 7. VIỆC CỦA BẠN VÀ CÂU HỎI

Việc tay, tất cả sửa trong `chuyende1/report/nhap/Chuong4_ThucNghiem.md`, tìm theo dấu `[`:

1. Mục 4.1.1, đoạn đầu: thay `[CẦN KIỂM: nguồn thu thập…]` bằng hai câu chép từ mục mô tả dữ
   liệu của bài UIT-ViSFD.
2. Mục 4.2, dòng "Phần cứng": điền tên CPU, RAM, phiên bản PyTorch, Transformers, VnCoreNLP.
3. Mục 4.3, đoạn "Mô hình từ điển", câu cuối: bạn đã thử từ điển tiếng Việt nào chưa? Chưa thì xoá câu.
4. Tài liệu [2]: đối chiếu trích dẫn VnCoreNLP với bản gốc.

Câu hỏi:

1. **GAP-028:** giữ một cấu hình cho mỗi mô hình (A), hay dò 3 learning rate (B, khoảng 8 đến 9 giờ T4)?
2. Viết tiếp chương nào: **Chương 2** (cơ sở lý thuyết, không phụ thuộc số liệu nào còn thiếu),
   hay quay lại **CD1.8b** để tập chẩn đoán kịp lịch?
3. Có muốn tôi vẽ Hình 4.1 bây giờ không?

---

## 8. BỔ SUNG 06/10/2026 — Chương 1, 2, 3 vào cuốn Word, đánh số tài liệu theo toàn văn

Học viên yêu cầu "viết cả chương 1, 2, 3 vào". Mục 1 đến 7 ở trên mô tả lúc mới có Chương 4;
mục này ghi trạng thái sau cùng.

### Đã làm

| File | Việc | Lên GitHub? |
|---|---|---|
| `chuyende1/report/nhap/Chuong1_TongQuan.md` | Viết mới. Chín mục 1.1 đến 1.9, một bảng kế hoạch. Khoảng 2.250 âm tiết | Không |
| `chuyende1/report/nhap/Chuong2_CoSoLyThuyet.md` | Viết mới. Sáu mục, mười công thức (2.1) đến (2.10). Khoảng 2.820 âm tiết | Không |
| `chuyende1/report/nhap/Chuong3_KhaoSat.md` | Đổi sang trích dẫn dạng khoá `[@...]`, thêm khoảng trắng trước dấu % ở 69 chỗ. Nội dung không đổi | Không |
| `chuyende1/report/nhap/Chuong4_ThucNghiem.md` | Đổi 9 chỗ trích dẫn sang khoá, bỏ danh mục cuối file | Không |
| `chuyende1/report/nhap/tai_lieu.json` | Tạo. 56 tài liệu: 48 từ ma trận khảo sát, 8 viết theo trí nhớ có đánh dấu | Không |
| `scripts/nhap_chuong_vao_docx.py` | Viết lại: ghép mọi chương, đánh số theo toàn văn, viết mục TÀI LIỆU THAM KHẢO | Có |
| `tests/test_nhap_chuong_vao_docx.py` | 11 test. Cả bộ: 394 passed | Có |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx` | **Chương 1 đến 4 và danh mục 56 tài liệu đã vào** | Không |

### Cơ chế đánh số

Bản nháp không ghi số mà ghi khoá, ví dụ `[@PhoBERT]`. Lúc ghép, công cụ đọc Chương 1 đến 4
theo thứ tự, gặp khoá nào lần đầu thì cấp số kế tiếp. Vì vậy thêm một trích dẫn ở Chương 1 làm
mọi số phía sau dịch đi, và đó là lý do công cụ luôn ghép tất cả các chương trong một lần chạy.
Khoá không có trong `tai_lieu.json` thì báo lỗi, không ghi gì.

### Những gì viết ở Chương 1 và 2 cần bạn biết

- **Chương 1 không có số liệu thị trường hay thống kê ngoài.** Luận cứ "phải xuống mức khía cạnh"
  dùng hai con số tự đo: 86,7 % bình luận có từ hai khía cạnh, 45,1 % có khía cạnh trái nhãn.
- **Mục 1.5 có bốn câu hỏi**, theo `survey_protocol.md` mục 1. Khung Word cũ ghi ba.
- **Mục 1.6 nói rõ bốn việc không làm**, trong đó có "không dò siêu tham số" (GAP-028).
- **Bảng 1.1** là kế hoạch 15 tuần, viết theo giai đoạn, không có mã step. Cột tình trạng ghi
  theo ngày 06/10 và phải cập nhật trước khi nộp.
- **Chương 2, công thức viết bằng ký tự thường.** Trong Word chúng là dòng chữ canh giữa, chưa
  phải công thức của Word. Phải gõ lại bằng Equation trước khi nộp.
- **Mục 2.4 nói thẳng** điểm cảm xúc suy từ nhãn huấn luyện không phải tri thức bên ngoài.
- **Mục 2.3 có công thức GAT** dù chuyên đề không chạy mô hình GAT nào, vì dàn ý yêu cầu và nó
  là nền của định hướng ở Chương 5. Nếu bị hỏi "sao có lý thuyết không dùng" thì đây là câu trả lời.

### Chưa kiểm, và việc của bạn

1. **Tám tài liệu viết theo trí nhớ**, hiện màu đỏ trong danh mục: VnCoreNLP, Transformer, BERT,
   RoBERTa, GCN của Kipf và Welling, GAT, kappa của Cohen, bootstrap của Berg-Kirkpatrick. Đối
   chiếu từng cái với bản gốc rồi sửa trong `tai_lieu.json`, xoá phần `[CẦN KIỂM ...]`.
2. **Chưa mở file bằng Word.** Cấu trúc đã kiểm bằng mã: 16 mục cấp 1 còn đủ, 13 bảng, không
   còn khoá `[@` nào, số trích dẫn lớn nhất là 56 bằng đúng số tài liệu. Trình bày thực tế
   (bảng tràn lề, ngắt trang, cỡ chữ) phải nhìn bằng mắt.
3. **Số trang chưa đo.** Phần thân bốn chương khoảng 14.200 âm tiết chưa tính bảng, so với ngân
   sách 24 trang của bốn chương này. Chương 3 vẫn vượt ngân sách như đã ghi ở phiếu trước.
4. **21 chỗ đánh dấu đỏ trong bốn chương** (1, 4, 4, 12), cộng 8 ở danh mục.
5. Hai hình chưa vẽ: Hình 2.1 (cơ chế tự chú ý), Hình 4.1 (phân bố nhãn theo khía cạnh).
6. Hai file `.docx.bak` trong `chuyende1/report/` là bản sao lưu, bạn tự quyết xoá.
