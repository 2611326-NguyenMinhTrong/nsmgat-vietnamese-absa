# GAP-029 — Hai file khảo sát học viên tự làm có số liệu sai và chi tiết không có căn cứ

**Ngày phát hiện:** 11/10/2026 · **Phát hiện bởi:** Claude Code (khi học viên nhờ xem hai file để tối ưu đề tài)
**Loại:** số liệu, trích dẫn · **Mức độ:** nghiêm trọng nếu lọt vào bản nộp · **Trạng thái:** 🟡 Đã thẩm định, chưa có gì lọt vào báo cáo; còn việc của học viên

---

## 1. Sai ở đâu

Hai file `khaosat_cosolythuyet.docx` và `khaosat_chuong3_cacphuongphap.docx` trong
`chuyende1/report/nhap/docs/` (thư mục không lên GitHub). Đối chiếu với ma trận khảo sát và số
liệu tự chạy cho ra:

- **11 chỗ sai so với nguồn đã kiểm**, trong đó: hai kết quả trên UIT-ViSFD (ghi 64,55 % và
  69,57 %, đúng là 63,06 % và 81,10 %); công thức Sentic-GCN có thêm trị tuyệt đối không có trong
  bài; bốn danh sách tác giả có tên người không tồn tại trong bài (UIT-ViSFD, Kocon, Varia, VLSP).
- **14 chi tiết thêm vào không có căn cứ trong kho**: ba tài liệu chưa ai đọc, số trang của 58
  tài liệu, các lời giải thích nguyên nhân mà bài gốc không viết.
- **Câu tự chứng nhận** "mọi con số đã đối chiếu với bài gốc" đi kèm chính những chỗ sai đó.

Bảng đầy đủ: `chuyende1/report/nhap/docs/THAM_DINH_hai_file_khao_sat.md`.

## 2. Phát hiện thế nào

Trích chữ của hai file rồi tìm từng chi tiết trong mọi cột của ma trận, kể cả `ghi_chu`. Chi
tiết nào ma trận có thì so; chi tiết nào ma trận không có thì xếp vào "chưa kiểm được".

## 3. Nguyên nhân gốc

Phần lớn nội dung hai file trùng với bản nháp và ma trận; phần viết rộng thêm thì không có dấu
vết đối chiếu với bản gốc. Claude không biết hai file được soạn bằng cách nào; điều quan sát
được là những chỗ ma trận thiếu thông tin (danh sách tác giả đầy đủ, số trang, một con số kết
quả) lại chính là những chỗ sai. Lời văn khẳng định chắc chắn làm người đọc không phân
biệt được đâu là phần đã kiểm.

Cùng mẫu hỏng với GAP-027: một ô chưa đối chiếu mang dáng vẻ đã kiểm chứng.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Tình trạng |
|---|---|
| Cuốn Word, bốn bản nháp chương, `tai_lieu.json`, ma trận | **Không bị ảnh hưởng.** Đã tìm: không có 64,55, 69,57, "hem", "Luong Nguyen", "Jacek Tao" ở đâu trong kho ngoài hai file đó |
| Ba hình trong `chuyende1/report/nhap/pictures/` | Hình 4.2 và Hình 2.1 có số không đo được hoặc không so được; Hình 4.1 bản hai khung có một chú thích sai. Chưa hình nào vào cuốn Word |

## 5. Đã xử lý thế nào

- Viết bản thẩm định, không sửa hai file của học viên.
- Sửa một câu ở bản nháp Chương 1 mà lần thẩm định này làm lộ ra: câu về Moore và Barnes viết
  "các mô hình mức khía cạnh", trong khi bài gốc là bài toán trích mục tiêu kèm cảm xúc.

## 6. Bài học

**Một văn bản tổng hợp, dù tự ghi "đã thẩm định toàn văn", chỉ là bản nháp cho tới khi từng con
số được dò lại với ma trận hoặc bản gốc.** Cách dò rẻ nhất: với mỗi con số và mỗi tên riêng,
tìm nó trong `survey_matrix.csv`; không thấy thì coi là chưa kiểm.

Danh sách tác giả đầy đủ và số trang là hai thứ dễ bị điền bừa nhất. `tai_lieu.json` cố ý viết
"và cộng sự" ở những bài chưa chép đủ tác giả từ bản gốc.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — chưa có gì lọt vào bản nộp.
