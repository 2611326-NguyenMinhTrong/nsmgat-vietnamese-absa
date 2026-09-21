# GAP-015 — Gỡ theo dõi file xong nhưng quy tắc `.gitignore` chưa được thêm

**Ngày phát hiện:** 20/09/2026 · **Phát hiện bởi:** Claude Code (đọc `git status` sau khi chạy)
**Loại:** code (thao tác repo)
**Mức độ:** nhẹ (chưa gây hậu quả, nhưng dựng sẵn cái bẫy cho lần sau)
**Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

Học viên yêu cầu không đẩy `SO_TAY_LENH.md` lên GitHub. Việc này gồm **hai bước phải đi cùng
nhau**:

1. `git rm --cached SO_TAY_LENH.md` — thôi theo dõi
2. Thêm `/SO_TAY_LENH.md` vào `.gitignore` — để nó không quay lại

Tôi gộp cả hai vào một chuỗi lệnh. Bước 2 **hỏng** (xem mục 3), bước 1 vẫn chạy và commit
`907711b` vẫn được tạo. Kết quả: file rơi vào trạng thái **chưa theo dõi mà cũng không bị bỏ
qua** — hiện dấu `??` trong `git status`, và một lần `git add .` vô ý sau này sẽ đưa nó trở
lại đúng chỗ học viên vừa bảo gỡ ra.

## 2. Phát hiện thế nào

Đọc đầu ra của chính lệnh mình vừa chạy: `git status --short` in ra `?? SO_TAY_LENH.md`, trong
khi `git check-ignore -v` chỉ liệt kê `README.md`. Nếu chỉ nhìn dòng "commit thành công" thì
lỗi này đã trôi qua.

## 3. Nguyên nhân gốc

**Giả định ngầm không được viết ra: tôi cho rằng `.gitignore` dùng xuống dòng `\n`.** Thực tế
file dùng `\r\n`. Đoạn script tìm chuỗi `"**/README.md\n"` để chèn vào sau → không khớp →
`AssertionError` → không ghi gì cả.

Bản thân việc dừng lại khi không khớp là **đúng** (còn hơn ghi bừa). Cái sai nằm ở chỗ khác:
**hai bước phụ thuộc nhau lại được nối bằng `;` thay vì điều kiện thành công.** Bước sau vẫn
chạy tiếp dù bước trước đã chết.

Đây là lần thứ ba trong Chuyên đề 1 một giả định về **định dạng văn bản** gây hỏng: trước đó là
`cp1252` khi in tiếng Việt, và heredoc nuốt dấu `\` khi viết file có ký tự thoát.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| `SO_TAY_LENH.md` | Có — đã thêm quy tắc bỏ qua ở commit `f5e30eb` |
| Lịch sử trên GitHub | **Không** — nhánh `main` đang đi trước `origin/main` 23 commit, file chưa từng rời khỏi máy |
| Số liệu thí nghiệm | Không liên quan |

## 5. Đã sửa thế nào

- `f5e30eb` thêm `/SO_TAY_LENH.md` vào `.gitignore`, bằng đoạn script **tự nhận diện kiểu
  xuống dòng** của file rồi ghi lại đúng kiểu đó.
- Kiểm chứng bằng `git check-ignore -v` cho cả hai file, không tin vào việc "commit chạy xong".

## 6. Bài học — phòng lần sau bằng cách nào

**Khi một yêu cầu cần nhiều bước phụ thuộc nhau, nối bằng điều kiện thành công (`&&`), không
nối bằng `;` — và sau khi chạy, kiểm bằng lệnh *hỏi trạng thái* (`git check-ignore`,
`git status`), không kết luận từ dòng "đã commit".**

Kèm theo: **đọc byte của file trước khi sửa tự động** — kiểu xuống dòng, BOM và bảng mã là ba
thứ trong repo này đã gây hỏng ba lần.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — sai sót thao tác nội bộ, đã sửa trong cùng phiên, không chạm tới số liệu hay
      kết luận khoa học.
