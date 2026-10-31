# PHIẾU BÀN GIAO — [CD1.11c] Sửa 15 chỗ của Chương 5 sau đợt rà soát

**Ngày:** 23/10/2026 · **Step:** CD1.11 (phần "Viết Chương 5", lần sửa) · **Thời gian thực tế:** khoảng 2 giờ

Học viên nhờ rà kỹ Chương 5, 6. Đợt rà ra 15 chỗ ở Chương 5 (5 chỗ lập luận sai hoặc nói quá, 6 chỗ thiếu căn cứ, 4 chỗ nhỏ);
học viên: "Sửa cả 15 chỗ của Chương 5, nhớ backup". Năm chỗ nặng ghi ở GAP-044.

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `chuyende1/report/nhap_rut_gon/Chuong5_HanCheVaDinhHuong.md` (không push) | Sửa | Viết lại 15 chỗ, đổi thứ tự mục: 5.2 ca điển hình, 5.3 thăm dò, 5.4 hạn chế |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx` (không push) | Sửa | Ghép riêng Chương 5, cập nhật mục lục và hai danh sách bằng COM; 64 trang |
| `scripts/doi_chieu_chuong5.py` | Sửa | Hàm mới `so_lieu_tu_du_doan`: mức nền của lỗi rơi vào nhãn kia, tìm lại trung tính theo khía cạnh, yếu tố đi cùng độ dài; 50 lên 72 chỗ kiểm |
| `tests/test_doi_chieu_chuong5.py` | Sửa | Thêm test: ghi sai nhóm hiện tượng của một ca phải bị báo |
| `chuyende1/gaps/GAP-044_...md`, `INDEX.md` | Tạo, sửa | Tỉ lệ không có mức nền, suy từ tập rút cân bằng nhãn ra toàn tập |

Sao lưu: bản nháp cũ ở `nhap_rut_gon/sao_luu/20261023-sua-15-cho-chuong-5/`; Word trước khi ghép ở
`..._rutgon.20261023-120412.docx.bak` (trùng mã băm file lúc trước khi ghép), trước khi cập nhật mục lục ở
`..._rutgon.20261023-120700.docx.bak`. File Word lưu lúc 12:07:03 ngày 23/10.

---

## 2. ĐỂ LÀM GÌ

- **Vấn đề:** mọi con số của Chương 5 đều đúng nguồn, nhưng một số câu rút kết luận mà số liệu không đỡ (GAP-044).
- **Sau step này:** mỗi tỉ lệ dùng làm bằng chứng có mốc so hoặc nói rõ quần thể; công cụ kiểm cả mốc so đó.

---

## 3. CƠ CHẾ — 15 chỗ đã sửa

| # | Chỗ | Sửa thế nào |
|---|---|---|
| 1 | 5.1, trung tính và PRICE | Câu chủ đề viết lại theo số: PhoBERT tìm lại 87,6 % mẫu trung tính ở PRICE, 58,0 % ở chín khía cạnh còn lại |
| 2 | 5.1 và hạn chế 2, lỗi rơi vào nhãn kia | Thêm mức nền 46,6 đến 48,5 %, phần chênh 14 đến 18 điểm; hạn chế 2 nói "nhiều hơn rõ so với mức nền" |
| 3 | 5.3, sau Bảng 5.1 | Nói rõ tập chẩn đoán rút cân bằng nhãn; trên toàn tập, lỗi có nhãn gốc trung tính 44,6 %, lỗi ngược cực 17,5 % |
| 4 | Hạn chế 4 | Đổi thành "ở cả bốn nhóm, kể cả nhóm thường"; tiêu đề hạn chế thu lại ở "mẫu có chuyển ý" (gấp hơn hai lần) |
| 5 | Hạn chế 1, 4 và 5.2 | Nhắc nhận định đồng ý hay không là của một người, kém ổn định (mục 4.1.2) |
| 6 | 5.1, độ dài | Thêm hai yếu tố đi cùng: tỉ lệ trái nhãn 40,0 lên 67,3 %, trung tính 10,4 lên 16,1 %; chuyển đoạn xuống sau Hình 5.1 để thuật ngữ "trái nhãn" đã được định nghĩa |
| 7 | 5.1, lỗi chung | Định nghĩa "lỗi cứng", nói "phần lớn trùng nhau" (59 đến 66 %), gộp câu lặp |
| 8 | Hạn chế 1 | Bỏ cách coi trung tính là "không có ý kiến"; dùng định nghĩa học viên tự xác định ở `docs/annotation_guideline.md`, ghi là "chuyên đề hiểu" |
| 9 | Hạn chế 2 và 5.3 mục 1 | Bỏ hai câu không có căn cứ; dẫn mục 2.1, 4.3 và [@KiritchenkoNegators] (đã có ở mục 2.5) |
| 10 | 5.3, đoạn kết | Kết luận về cây cú pháp thu về đúng phép đo; nói rõ phép thứ ba chưa đo việc nối hiện tượng với khía cạnh |
| 11 | Hạn chế 3 | "lỗi của PhoBERT ở các nhóm này" (tỉ lệ ngược cực theo nhóm chỉ đo cho PhoBERT) |
| 12 | 5.1, câu đầu | "Mọi tỉ lệ về kết quả của mô hình là trung bình năm seed" |
| 13 | 5.2, bốn ca | Nêu thành phần 30 mẫu, nói bốn ca chọn để minh hoạ, không đại diện; ghi nhóm hiện tượng của từng ca; "bình luận" thay "câu" |
| 14 | 5.3, phép thứ ba | Dẫn lại mục 4.1.2 |
| 15 | Thứ tự mục | Bằng chứng trước kết luận: thăm dò (5.3) đứng trước hạn chế (5.4) |

Mức nền ở chỗ 2: với mỗi lỗi ở bình luận có đúng hai nhãn, xác suất rơi vào nhãn còn lại nếu lỗi của lớp đó chia cho hai lớp
kia theo ma trận nhầm lẫn của các mẫu ngoài nhóm (cùng mô hình, cùng seed); lấy trung bình trên mọi lỗi. Ví dụ PhoBERT: thực
tế 63,4 %, mức nền 47,6 %.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Đưa vào Word | Ghép riêng `--chi 5 --ghi-de` | Sửa bằng COM như phiếu rà soát đã nói | Có đổi thứ tự mục; Chương 5 không có phương trình, và so từng ký tự, định dạng với bản ngay sau lần ghép 18/10 thì giống hệt (học viên chưa sửa tay) |
| Câu về PRICE | Chỉ mô tả | Nêu quy ước "tầm giá" của bộ dữ liệu làm nguyên nhân | Quy ước đó chưa có trong báo cáo và chưa có chỗ kiểm |
| Định nghĩa trung tính | "Chuyên đề hiểu ..." | Ghi là định nghĩa của UIT-ViSFD | Bài gốc không định nghĩa; hướng dẫn chú thích dặn không ghi là của bộ dữ liệu |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Mục 5.5 và Chương 6 vẫn là đoạn giữ chỗ. 5.5 phải gỡ mâu thuẫn: mục 1.3 và phần Tóm tắt nêu hướng "kết hợp đồ thị và luật",
  trong khi Chương 4 và mục 5.3 cho thấy phần đồ thị và luật lật cực không đem lại lợi ích đo được.
- Viết xong 5.5 thì sửa đoạn cuối phần Tóm tắt và đoạn cuối mục 4.7 (bằng COM, hai phần này có trong Word đã sửa tay).
- Chương 5 dài 8 trang (38 đến 45), trước là 6; trang 41 trống khoảng một phần ba vì tên Bảng 5.1 đi liền bảng.

---

## 6. KIỂM CHỨNG

```
doi_chieu_chuong5.py          72 chỗ, khớp 72; mọi con số có chỗ kiểm
                              7 lần cố ý sửa sai một số trên bản sao: cả 7 bị báo
doi_chieu_chuong4.py          234 chỗ, khớp 234
kiem_sua_tay_word.py          trước khi ghép: mã 1, sáu chỗ, cả sáu là chữ cũ của Chương 5; sau khi ghép: mã 2
phương trình / chỉ số / hình  9 / 21 / 3 trước và sau
pytest tests -q               565 passed, 1 skipped in 165.56s
```

- Chạy thử ghép trên bản sao: mọi mục cấp 1 ngoài Chương 5 giống hệt XML (bỏ rsid); file thật giống hệt bản thử.
- Cập nhật mục lục chạy thử trên bản sao trước: chỉ mục lục và hai danh sách đổi; Word bỏ phần định dạng trực tiếp trùng
  style Normal ở các đoạn vừa ghép, đọc lại bằng Word thì định dạng hiệu lực của 76 đoạn Chương 5 không đổi.
- Xem bố cục bằng ảnh xuất từ Word, trang in 38 đến 46.

---

## 7. DỪNG LẠI VÀ HỎI

1. Làm lượt tìm tài liệu cho mục 5.5 rồi viết 5.5 và Chương 6?
2. Commit notebook phiên Kaggle `notebooks/da-chay/cost/` và cập nhật trạng thái các GAP đã xử lý xong trong `INDEX.md`?
3. Chương 5 nay 8 trang: giữ, hay cắt?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi hay yêu cầu của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi không |
|---|---|---|
| | | |
