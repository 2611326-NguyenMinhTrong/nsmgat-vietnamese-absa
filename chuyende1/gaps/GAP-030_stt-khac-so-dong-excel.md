# GAP-030 — Cột stt lệch 1 so với số dòng của Excel, học viên sửa nhầm dòng

**Ngày phát hiện:** 13/10/2026 · **Phát hiện bởi:** Claude Code
**Loại:** tài liệu · code
**Mức độ:** nhẹ (bắt được trước khi vào CSV)
**Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

Hai chỗ, lộ ra cùng lúc.

1. Phiếu bàn giao CD1.8d và `VIEC_CAN_LAM.md` giao việc "xem các dòng stt 9, 27, 34, 229, …"
   trong `candidates_chu_thich.xlsx` mà không nói `stt` là giá trị ở cột A, khác số dòng Excel
   in ở lề trái. Dòng 1 của Excel là tiêu đề nên stt 229 nằm ở dòng 230.
   Trong bản `.xlsx` học viên lưu lúc 01:40 ngày 13/10, stt 228 (`00950-PERFORMANCE`) bị đổi
   `negation` thành `regular` kèm ghi chú "giá làm khung", còn stt 229 (`00950-PRICE`, dòng được
   đề xuất) giữ nguyên.
2. `scripts/chu_thich_chan_doan.py excel --ghi-de` sập bằng traceback `PermissionError` khi file
   `.xlsx` đang mở trong Excel, và đã kịp sinh một bản `.bak` trước khi sập.

## 2. Phát hiện thế nào

Trước khi sinh lại `.xlsx` từ CSV, Claude thấy file khoá `~$candidates_chu_thich.xlsx` và giờ sửa
file mới hơn lần sinh gần nhất, nên so từng ô chú thích giữa `.xlsx` và CSV. Có đúng hai ô lệch,
cùng ở stt 228. Đọc câu thì thấy ở khía cạnh PERFORMANCE chữ "không" phủ định đúng lời phàn nàn về
máy, tức `negation` là đúng; dòng cần đổi là dòng PRICE ngay dưới.

## 3. Nguyên nhân gốc

Giả định ngầm không được viết ra: người viết coi "stt" là hiển nhiên, người đọc nhìn con số ở lề
Excel. Hai dòng liền nhau lại cùng một câu nên nhìn nội dung không thấy sai.

Với lỗi thứ hai: chưa bao giờ chạy lệnh trong lúc file đang mở, nên không có test cho ca đó.

## 4. Ảnh hưởng lan tới đâu

Không lan. Thay đổi nhầm chưa qua `tu-excel` nên chưa vào `candidates.csv`. Nếu học viên chạy
`tu-excel` thì một dòng PERFORMANCE đúng sẽ rời nhóm phủ định, và 14 dòng K2 sửa trong CSV sẽ bị
bản `.xlsx` cũ ghi đè ngược lại.

## 5. Đã sửa thế nào

- 14 dòng K2 sửa thẳng trong CSV theo `uid`, không theo `stt`; `.xlsx` sinh lại từ CSV sau khi
  học viên đóng Excel. Bản `.xlsx` có dòng sửa nhầm còn ở
  `data/diagnostic/candidates_chu_thich.20261013-014537.xlsx.bak`.
- `cmd_excel` thử mở file để ghi trước khi sao lưu; file đang khoá thì in hướng dẫn đóng Excel và
  trả mã 2. Có test `test_excel_dang_mo_thi_dung_gon_khong_sinh_ban_sao_luu`.
- `VIEC_CAN_LAM.md` mục A13 ghi rõ tìm dòng theo cột `stt`.

## 6. Bài học

Giao việc sửa một dòng cụ thể thì đưa thứ nhận ra được trong chính dòng đó: mã câu và khía cạnh,
không chỉ số thứ tự. Và trước khi ghi đè một file người khác đang sửa, so nó với nguồn.
