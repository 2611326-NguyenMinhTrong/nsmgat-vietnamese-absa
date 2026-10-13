# GAP-034 — File Word dùng khổ giấy Letter và tiêu đề hiện bằng Calibri, trái quy định trình bày

**Ngày phát hiện:** 13/10/2026 · **Phát hiện bởi:** Claude Code, khi kiểm file trước lần nộp bốn chương đầu
**Loại:** tài liệu · code
**Mức độ:** trung bình (chưa có bản nào được nộp; sai từ ngày dựng khung 23/09 mà không ai thấy)
**Trạng thái:** ✅ Đã sửa ở mã và ở bản chính (bản rút gọn). File Word của bản đầy đủ được giữ nguyên làm bản lưu, vẫn khổ Letter, không nộp (mục 8)

---

## 1. Sai ở đâu

Quy định trình bày của trường (Phần I mục 1 và Phần III) đòi khổ giấy A4 và "chỉ dùng một kiểu
font chữ". File `chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx` lệch ở hai điểm:

| | Quy định | File hiện tại | Cách đo |
|---|---|---|---|
| Khổ giấy | A4, 21,0 × 29,7 cm | Letter, 21,59 × 27,94 cm, ở cả ba section | thẻ `w:pgSz` có `w=12240 h=15840` |
| Font tiêu đề chương và mục | Times New Roman | Calibri ở cả ba cấp tiêu đề | hỏi chính Word: `Range.Font.Name` của đoạn Heading 1, 2, 3 |

Thân bài, chú thích bảng và mục lục vẫn là Times New Roman. Lề, cỡ chữ, giãn dòng và cách đánh số
trang đúng quy định.

## 2. Phát hiện thế nào

Học viên hỏi còn thiếu gì để nộp bốn chương đầu. Claude đo từng mục của bảng kiểm định dạng trên
chính file thay vì đọc lại mã sinh file. Hai mục trên không khớp.

## 3. Nguyên nhân gốc

- Khổ giấy: `apply_page_setup` trong `scripts/ute_docx.py` chỉ đặt bốn lề. File mẫu mặc định của
  thư viện python-docx là khổ Letter, và không dòng mã nào đổi nó. Bảng trưng bày trong
  `build_cd1_report.py` còn ghi "Khổ giấy: A4" trong khi file không phải A4.
- Font: `_style_font` ghi tên font Times New Roman vào style nhưng không xoá bốn thuộc tính trỏ tới
  font chủ đề (`asciiTheme` và ba thuộc tính cùng loại) mà style Heading của file mẫu có sẵn. Khi
  có cả hai, Word dùng font chủ đề, ở đây là Calibri. Trong `reference.docx` và các bản sao lưu đầu
  tiên, style Heading 1 có đủ cả hai nhóm thuộc tính; sau khi file được lưu bằng Word, nhóm
  Times New Roman bị Word bỏ hẳn.
- Không test nào kiểm khổ giấy. Font của tiêu đề thì có test (`tests/test_ute_docx.py`), nhưng
  test đọc `style.font.name` của python-docx. Giá trị đó là Times New Roman ngay cả khi style còn
  thuộc tính font chủ đề, tức test xanh trong khi Word hiện Calibri.

## 4. Ảnh hưởng lan tới đâu

- Mọi bản Word đã sinh từ 23/09, kể cả các bản học viên chép ra thư mục Backup.
- Số trang: cùng nội dung, bốn chương đầu dài 62 trang ở khổ Letter và 58 trang ở khổ A4. Mọi con
  số trang đã nêu trước đây đều tính trên khổ Letter.
- Không ảnh hưởng tới nội dung hay số liệu.

## 5. Sẽ sửa thế nào

Chưa sửa. Việc cần làm khi học viên đồng ý:

- `apply_page_setup` đặt thêm chiều rộng 21,0 cm và chiều cao 29,7 cm.
- `_style_font` xoá các thuộc tính font chủ đề trước khi ghi tên font.
- Bước ghép chương áp lại hai thiết lập này lên file đang có, vì khung file chỉ được dựng một lần.
- Thêm test đọc thẳng `w:pgSz` và `w:rFonts` của file sinh ra.
- Sau khi sửa, hỏi lại Word font của ba cấp tiêu đề và đếm lại số trang.

## 6. Bài học

Kiểm định dạng thì phải hỏi công cụ sẽ hiển thị file, không hỏi thư viện đã ghi file. Và một bảng
kiểm chỉ có giá trị khi từng dòng của nó được đo trên sản phẩm; dòng "khổ A4" đã nằm trong bảng
kiểm của dàn ý từ đầu mà chưa lần nào được đo.

## 7. Cập nhật ngày 13/10/2026

- `scripts/ute_docx.py`: `apply_page_setup` đặt khổ 21,0 x 29,7 cm; `_style_font` xoá bốn thuộc tính font chủ đề;
  thêm `ap_lai_dinh_dang` để áp lại lên file đã có. Ba test mới đọc thẳng `w:pgSz` và `w:rFonts`.
- `scripts/nhap_chuong_vao_docx.py` có cờ `--sua-dinh-dang`. Không bật mặc định, để lần ghép thường không tự
  đổi file hiện tại.
- File mới `ChuyenDe1_NguyenMinhTrong_rutgon.docx` được ghép với cờ đó. Hỏi lại Word: khổ 21,0 x 29,7 cm, font của
  tiêu đề cấp 1, 2, 3 là Times New Roman.
- File `ChuyenDe1_NguyenMinhTrong.docx` **chưa đổi**: học viên yêu cầu giữ nguyên file hiện tại. Khi học viên đồng ý,
  chạy lần ghép kế tiếp của file đó với `--sua-dinh-dang` rồi đóng mục này.

## 8. Đóng ngày 13/10/2026

Học viên chọn bản rút gọn làm bản chính. File để nộp từ nay là `ChuyenDe1_NguyenMinhTrong_rutgon.docx`. Sau lần
ghép lúc 15:09 ngày 13/10, hỏi lại Word trên một bản sao: khổ 21,0 x 29,7 cm, tiêu đề cấp 1, 2, 3 là
Times New Roman. Bản mà học viên đã mở và lưu bằng Word lúc 15:03 cũng được hỏi lại và cho cùng kết quả, tức việc
Word lưu lại không làm mất hai thiết lập.

File `ChuyenDe1_NguyenMinhTrong.docx` là bản lưu của bản đầy đủ, vẫn ở khổ Letter với tiêu đề Calibri. Nó không
được nộp. Nếu có lúc phải dùng lại, ghép nó với `--sua-dinh-dang` trước.
