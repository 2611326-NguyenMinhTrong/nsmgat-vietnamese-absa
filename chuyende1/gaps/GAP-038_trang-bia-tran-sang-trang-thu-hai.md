# GAP-038 — Trang bìa tràn sang trang thứ hai

**Ngày phát hiện:** 13/10/2026 · **Phát hiện bởi:** Claude Code, khi hỏi Word trang của từng đoạn trước Chương 1
**Loại:** tài liệu · code
**Mức độ:** nhẹ (chưa bản nào được nộp)
**Trạng thái:** ✅ Đã sửa ở bản chính; khung bìa trong `scripts/build_cd1_report.py` chưa sửa (mục 5)

---

## 1. Sai ở đâu

Trên file Word, trang bìa chiếm hai trang: dòng "CHUYÊN ĐỀ" ở trang 1, còn ba dòng học viên, giảng viên hướng
dẫn và nơi, thời gian ở trang 2. Mục LỜI CẢM ƠN vì vậy bắt đầu ở trang thứ ba của file.

## 2. Phát hiện thế nào

Khi kiểm các trang đầu sau lần ghép, Claude hỏi Word trang bắt đầu và kết thúc của từng đoạn thay vì chỉ xem
trang của các tiêu đề. Số đo trước đó trong ngày (LỜI CẢM ƠN ở trang tuyệt đối 3) đã cho thấy điều này nhưng
không ai đọc ra.

## 3. Nguyên nhân gốc

`build_cover` trong `scripts/build_cd1_report.py` chèn 18 dòng trống giãn dòng 1,5, mỗi dòng còn cách đoạn
6 pt. Cùng với tên đề tài hai thứ tiếng dài nhiều dòng, tổng chiều cao vượt chiều cao vùng chữ của trang A4.
Ở khổ Letter (thấp hơn A4) bìa cũng tràn, nên lỗi có từ ngày dựng khung.

## 4. Ảnh hưởng lan tới đâu

- File Word của bản chính và của bản đầy đủ, cùng mọi bản sao lưu.
- Số trang La Mã của các trang đầu không đổi, vì bìa nằm ở section riêng không đánh số.

## 5. Đã sửa thế nào

`nhap_chuong_vao_docx.py` có hàm `thu_gon_trang_bia`, chạy khi thư mục nháp có `TrangDau.md`: mỗi cụm dòng
trống của bìa còn tối đa 3 dòng, dòng trống dùng giãn dòng đơn và không cách đoạn; dòng có chữ không bị đụng
tới. Sau lần ghép ngày 13/10, hỏi lại Word: cả 11 dòng có chữ của bìa nằm ở trang 1, LỜI CẢM ƠN bắt đầu ở
trang 2 của file.

Chưa sửa `build_cover` của khung: khung chỉ dựng một lần và file đã có được sửa qua lệnh ghép. Nếu dựng khung
cho Chuyên đề 2 thì sửa ở đó trước.

## 6. Bài học

Kiểm bố cục phải kiểm cả chỗ kết thúc của mỗi phần, không chỉ chỗ bắt đầu của tiêu đề.
