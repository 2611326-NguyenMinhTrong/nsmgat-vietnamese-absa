# PHIẾU BÀN GIAO — [CD1.12q] Lượt tìm tài liệu cho mục 5.5, viết mục 5.5 và Chương 6

**Ngày:** 23–24/10/2026 · **Step:** CD1.12 (viết báo cáo), nối CD1.11b · **Thời gian thực tế:** khoảng 4 giờ

Học viên: "Làm lượt tìm tài liệu cho mục 5.5, rồi viết 5.5 và Chương 6". Rủi ro R7 của plan đã xảy ra (trần của luật lật cực
dưới 1,5 điểm), nên mục 5.5 phải nói hướng NS-MGAT được điều chỉnh thế nào cho khớp số đo, không viết lại nguyên hướng cũ.

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `chuyende1/survey/survey_protocol.md` | Sửa | Nhật ký mục 6: 17 truy vấn ngày 23/10/2026, số kết quả đếm từ trang kết quả, giữ 7 |
| `chuyende1/survey/survey_matrix.csv` | Sửa | 7 dòng mới, đủ 19 cột, `da_doc_toan_van`; `validate` hợp lệ (57 dòng) |
| `chuyende1/survey/khong_trinh_bay.csv` | Sửa | 7 khoá mới: trình bày ở Chương 5, không ở Chương 3 |
| `chuyende1/report/nhap_rut_gon/tai_lieu.json` (không push) | Sửa | 7 mục tài liệu |
| `chuyende1/report/nhap_rut_gon/Chuong5_HanCheVaDinhHuong.md` (không push) | Sửa | Viết mục 5.5 |
| `chuyende1/report/nhap_rut_gon/Chuong6_KetLuan.md` (không push) | Viết | Chương 6: 6.1, 6.2, 6.3 với Bảng 6.1 |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx` (không push) | Sửa | Ghép Chương 5, 6 và danh mục tài liệu; đổi [46], [47] ở Bảng A.1 thành [53], [54] bằng COM; cập nhật mục lục; 70 trang |
| `scripts/doi_chieu_chuong5.py` + test | Sửa | Chỗ kiểm cho 5.5, chứng cứ nguyên văn của 7 công trình (`CHUNG_CU`); 84 chỗ; 8 test |
| `scripts/doi_chieu_chuong6.py` + `tests/test_doi_chieu_chuong6.py` | Tạo | Đối chiếu Chương 6 với chương nguồn, 29 nhận định, 5 test |
| `scripts/nhap_chuong_vao_docx.py` + test | Sửa | `--chi ... tai_lieu`: thay riêng danh mục tài liệu |
| `scripts/doi_chieu_ban_goc.py` | Sửa | Kiểm Chương 1 đến 6; đường dẫn bản gốc của hai bài ngoài ACL Anthology |
| `chuyende1/MODULE.md`, `SO_TAY_LENH.md` (chỉ ở máy) | Sửa | Công cụ mới, cờ mới |

Sao lưu: ma trận, `khong_trinh_bay.csv`, `tai_lieu.json` ở `chuyende1/survey/sao_luu_20261023/`; bản nháp Chương 6 cũ ở
`nhap_rut_gon/sao_luu/20261023-sua-15-cho-chuong-5/`; file Word ở `..._rutgon.20261024-125439.docx.bak` (trước khi ghép),
`.20261024-125446.docx.bak` (trước bước COM), `.20261024-125719.docx.bak` và `.20261024-125728.docx.bak` (lần ghép lại Chương 6
sau khi sửa Bảng 6.1). File Word lưu lúc 12:57:33 ngày 24/10.

---

## 2. ĐỂ LÀM GÌ

- **Vấn đề:** mục 5.5 và Chương 6 còn là câu giữ chỗ, trong khi mục 1.5, 3.10 và dàn ý đều hứa mục 5.5; hướng đề tài (mục 1.3)
  lại mâu thuẫn với số đo của Chương 4 và mục 5.3.
- **Sau step này:** đủ sáu chương; hướng đề xuất có căn cứ ở cả số đo của chuyên đề lẫn bảy công trình đọc toàn văn.

---

## 3. CƠ CHẾ — mục 5.5 nói gì

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Đoạn mở | Giữ hướng kết hợp đồ thị và luật có độ tin cậy, nhưng luật tác động vào chỗ khác với lật cực | Mục 3.10, kết quả Chương 4, mục 5.3 |
| Ba công trình khớp với số đo | Barnes 2019: lỗi chung nhiều nhất ở câu không cảm xúc và câu lẫn lộn, mỗi loại khoảng gấp đôi phủ định; MAMS: tập tiếng Anh phải dựng riêng câu nhiều khía cạnh khác cực, ở UIT-ViSFD loại này chiếm hơn nửa tập kiểm tra; Krishna 2018: chưng cất luật "A-but-B" gần như vô tác dụng khi lấy trung bình nhiều seed | Câu nguyên văn trong bản gốc (`CHUNG_CU`) |
| Ba điểm đổi vai trò của luật | (1) đánh dấu mệnh đề và phạm vi thay vì lật cực, có cơ sở ở Wang 2018, AC-MIMLLN, CAN; (2) tách quyết định "được đánh giá rõ hay không" khỏi quyết định cực, ghi rõ là giả thuyết; (3) độ tin cậy của luật học từ dữ liệu theo data programming, đối chiếu bằng tập chẩn đoán | P2 (độ chính xác dưới ba phần năm), mục 5.1 |
| Ba ràng buộc | Đồ thị không giữ mặc định; so với PhoBERT và ASGCN bỏ GCN, năm seed, hai phép kiểm định; đánh giá theo nhóm và thêm người chú thích thứ hai | Chương 4: mọi chênh lệch giữa các mô hình dùng PhoBERT dưới 1 điểm và đổi dấu theo seed |

Ví dụ một nhận định và cách nó được kiểm: câu "Hai nguồn lỗi nhiều nhất là câu không mang cảm xúc và câu có cảm xúc lẫn lộn,
mỗi nguồn khoảng gấp đôi số câu sai có phủ định" đứng trên ba câu nguyên văn của Barnes và cộng sự: "come from the
no-sentiment (214), mixed category", "(185), non-standard spelling and hashtags", "Negation, which accounts for 97 errors".
Công cụ đọc ba số đó từ bản gốc và kiểm tỉ lệ nằm trong khoảng 1,5 đến 2,5.

Chương 6: 6.1 đối chiếu bốn mục tiêu và trả lời ba câu hỏi của mục 1.3; 6.2 sáu hạn chế; 6.3 Bảng 6.1 (sáu mốc trong 15 tuần,
theo S2 đến S5 của plan nén 6 tháng, đã điều chỉnh theo mục 5.5) và đoạn rủi ro. Chương không có con số nào ngoài Bảng 6.1.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Bài TASLP 2024 về phát hiện phạm vi | Không dùng | Trích theo tóm tắt | Không có bản mở, không đọc toàn văn được |
| Bài chỉ có trên arXiv (EDU-level, Structural Scope) | Không giữ | Giữ | Tiêu chí nhận của giao thức: nơi có phản biện |
| 7 công trình mới trong ma trận | Thêm vào `khong_trinh_bay.csv` | Để vào bảng Chương 3 | Bảng A.1 và các con số 34 công trình của Chương 1, 3, Tóm tắt sẽ đổi |
| Phụ lục khi số trích dẫn đổi | Đổi hai số bằng COM | Ghép `--chi phu_luc` | So định dạng hiệu lực bằng Word: dòng GitHub trong Word là liên kết căn trái, có màu; ghép sẽ mất |
| Nhận định không có số ở Chương 6 | Công cụ dẫn chiếu mới | Chép số từ Chương 4, 5 | Quy tắc văn phong số 10; dẫn chiếu tự báo khi chương nguồn đổi |
| Bảng 6.1 | Hai cột | Bốn cột | Lệnh ghép chia cột đều, cột "Tuần" chiếm chỗ, bảng dài gần hai trang |
| Câu "chưa có công trình nào tách quyết định trung tính" | Không viết | Viết | Câu phủ định cần lần tìm riêng; ghi là giả thuyết chưa kiểm |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Phần Tóm tắt (`TrangDau.md` và Word) chưa có câu nào về Chương 5, và câu cuối "Đây là căn cứ để chuyên đề sau tập trung xử lý
  tường minh phủ định và chuyển ý" cần thêm ý của mục 5.5. Đoạn cuối mục 4.7 cũng vậy. Cả hai nằm trong phần Word học viên đã
  sửa tay, phải sửa bằng COM.
- Khi có kết quả GPT-4o (E9): `doi_chieu_chuong6.py` sẽ báo MẤT CHỨNG CỨ ở câu GPT-4o của mục 6.1, phải viết lại câu đó.
- Bảng 6.1 giả định Chuyên đề 2 dài 15 tuần như Chuyên đề 1; chưa có lịch chính thức.
- Hướng điều chỉnh ở mục 5.5 nên báo GVHD (plan, rủi ro R7).

---

## 6. KIỂM CHỨNG

```
doi_chieu_chuong4.py          234 chỗ, khớp 234
doi_chieu_chuong5.py          84 chỗ, khớp 84 (mọi con số có chỗ kiểm; chứng cứ của 7 công trình có trong bản gốc)
doi_chieu_chuong6.py          29 nhận định, khớp hết; không con số lạ
doi_chieu_ban_goc.py kiem     Chương 5, 6: 0 con số gắn với công trình khác
survey_tools.py validate      hợp lệ, 57 dòng; table-gon giống hệt bảng sinh từ ma trận trước khi thêm (34 công trình)
kiem_sua_tay_word.py          trước khi ghép: mã 1, 8 chỗ, đều là chỗ dự kiến; sau: mã 2; 9 phương trình
pytest tests -q               572 passed, 1 skipped in 146.38s
```

- Chạy thử trên bản sao: Chương 1 đến 4 và các trang đầu giống hệt XML; danh mục tài liệu: mọi mục cũ giống hệt định dạng sau
  khi quy đổi số, 7 mục mới cùng định dạng; Phụ lục: định dạng hiệu lực giống hệt, chỉ khác hai số. File thật giống bản thử.
- Ảnh xuất từ Word: Chương 5 trang 38 đến 47, Chương 6 trang 48 đến 51, file 70 trang.

---

## 7. DỪNG LẠI VÀ HỎI

1. Mục 5.5 giữ khung NS-MGAT đã duyệt nhưng đổi vai trò của luật (đánh dấu mệnh đề, phạm vi; độ tin cậy học từ dữ liệu) và thêm
   giả thuyết tách quyết định trung tính. Bạn có đồng ý hướng này trước khi báo cô không?
2. Bảng 6.1 giả định Chuyên đề 2 dài 15 tuần. Bạn có lịch chính thức không?
3. Sửa phần Tóm tắt và đoạn cuối mục 4.7 cho khớp mục 5.5 không?
4. File nay 70 trang (Chương 5 dài 10 trang, Chương 6 dài 4 trang). Giữ, hay cắt?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi hay yêu cầu của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi không |
|---|---|---|
| "chương 6 chỉ cần ghi hướng cải tiến là sẽ làm những gì, không cần ghi rõ plan và thời gian ra" (24/10/2026) | Mục 6.3 đổi tên thành "Hướng cải tiến trong Chuyên đề 2": một câu dẫn và sáu việc sẽ làm (luật, độ tin cậy, mô hình, so sánh và loại bỏ thành phần, đánh giá theo nhóm, chéo miền nếu còn điều kiện). Bỏ Bảng 6.1 và đoạn rủi ro, vì đoạn này là phương án xử lý, cũng thuộc kế hoạch. Tên chương thành "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN". Câu hỏi 2 ở mục 7 không còn cần | Có. Bản nháp (sao lưu ở `nhap_rut_gon/sao_luu/20261024-chuong-6-bo-lich/`); Word: ghép `--chi 6 --ghi-de` (sao lưu `.20261024-133611.docx.bak` trước khi ghép), đổi tên chương và cập nhật mục lục bằng COM (sao lưu `.20261024-133612.docx.bak` trước bước COM); lưu 13:36:43, 69 trang, Chương 6 trang 48 đến 50, danh sách bảng không còn Bảng 6.1. `doi_chieu_chuong6.py`: bỏ Bảng 6.1 khỏi lượt quét số, bỏ hai dẫn chiếu của đoạn rủi ro, thêm sáu dẫn chiếu từ mục 6.3 sang mục 5.5 (33 nhận định); test bảng lịch đổi thành "bảng lịch thêm lại thì bị báo". Chạy thử trên bản sao trước: chỉ Chương 6 và ba danh sách đổi; file thật giống bản thử; `kiem_sua_tay_word.py` mã 2 |
