# REQ-003 — Sổ sai sót `gaps/` và sổ yêu cầu bổ sung `user-require/`

**Ngày yêu cầu:** 27/08/2026 · **Trạng thái:** ✅ Xong

---

## 1. Yêu cầu nguyên văn

> "tạo cho tôi thêm thư mục /gaps trong /chuyende1 để có thể lưu trữ các tài liệu sai sót
> trong quá trình thực hiện, tạo thêm một thư mục /user-require để lưu trữ các tài liệu mà
> tôi yêu cầu làm thêm trong quá trình thực hiện, đặt trong thư mục /chuyende1 luôn"

## 2. Hiểu thành gì

Hai sổ ghi hai loại "lệch" khác nhau so với kế hoạch ban đầu:

| Thư mục | Ghi cái gì | Nguồn gốc |
|---|---|---|
| `gaps/` | Sai sót phát hiện khi làm — lỗi kế hoạch, code, tài liệu, số liệu, phương pháp | Lỗi từ bên trong |
| `user-require/` | Yêu cầu bổ sung của học viên ngoài phạm vi đã chốt | Thay đổi từ bên ngoài |

Không gộp làm một, vì hai loại này xử lý khác nhau: sai sót cần **nguyên nhân gốc + bài học**;
yêu cầu cần **lời gốc + chi phí + ảnh hưởng lịch**.

## 3. Vì sao học viên muốn thế

Suy ra từ ngữ cảnh (học viên không nói rõ): trong 15 tuần sẽ có nhiều lệch nhỏ so với plan.
Không ghi lại thì đến lúc viết Chương 6 (hạn chế) và trả lời hội đồng sẽ phải nhớ lại bằng
trí nhớ — không đáng tin.

Đây cũng là hệ quả tự nhiên của REQ-002: đã muốn học trong lúc làm thì phải có chỗ lưu cái
đã học được, kể cả (nhất là) học từ sai sót.

## 4. Đã làm gì để đáp ứng

| File | Tạo | Nội dung |
|---|---|---|
| `chuyende1/gaps/INDEX.md` | ✓ | Bảng theo dõi + thống kê theo loại |
| `chuyende1/gaps/_TEMPLATE_gap.md` | ✓ | Mẫu 7 mục, trọng tâm ở "nguyên nhân gốc" và "bài học" |
| `chuyende1/user-require/INDEX.md` | ✓ | Bảng theo dõi + tổng chi phí phát sinh |
| `chuyende1/user-require/_TEMPLATE_require.md` | ✓ | Mẫu 7 mục, trọng tâm ở "yêu cầu nguyên văn" |
| `chuyende1/MODULE.md` | Sửa | Thêm 2 thư mục vào mục 2.1 (sở hữu) và mục 4 (quy trình) |
| `README.md`, `PLAN_CHUYENDE1.md` | Sửa | Cập nhật cây thư mục |

**Đã điền sẵn nội dung thật thay vì để rỗng:**

- `gaps/`: 4 sai sót đã phát hiện trong phiên đầu tiên (GAP-001 → GAP-004)
- `user-require/`: 3 yêu cầu đã nhận (REQ-001 → REQ-003, gồm chính file này)

Nếu để thư mục rỗng, những phát hiện này chỉ còn nằm trong lịch sử hội thoại và sẽ mất.

## 5. Chi phí

- **Một lần:** ~1 giờ (dựng khung + ghi lại 7 mục đã tích luỹ)
- **Lặp lại:** ~10 phút mỗi lần ghi một GAP hoặc REQ mới
- **Cả kỳ ước tính:** ~2–3 giờ

## 6. Có làm lệch kế hoạch gốc không

- [x] **Không** — chỉ thêm nơi lưu trữ, không thêm việc nghiên cứu.

Ngược lại còn **tiết kiệm** thời gian ở Tuần 13: `gaps/INDEX.md` là nguyên liệu sẵn cho mục
6.2 "Hạn chế của Chuyên đề 1" trong báo cáo.

## 7. Việc phát sinh về sau

Có — nghĩa vụ lặp lại:

- Phát hiện sai sót → ghi ngay một file `GAP-00x`, **kể cả sai sót do Claude Code gây ra và
  đã sửa xong**
- Nhận yêu cầu mới ngoài plan → ghi ngay một file `REQ-00x`, chép **nguyên văn** lời học viên
- **Tuần 8:** rà bảng chi phí trong `user-require/INDEX.md`; nếu vượt ~20 giờ thì cắt phạm vi
  hoặc báo GVHD sớm
- **Tuần 13:** đọc lại `gaps/INDEX.md` khi viết mục 6.2 của báo cáo

Đã ghi vào `chuyende1/MODULE.md` mục 4.
