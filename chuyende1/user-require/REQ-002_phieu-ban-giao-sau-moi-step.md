# REQ-002 — Giải thích sau mỗi step rồi dừng lại hỏi

**Ngày yêu cầu:** 27/08/2026 · **Trạng thái:** ✅ Xong (đang áp dụng từ CD1.0)

---

## 1. Yêu cầu nguyên văn

> "trong quá trình code tôi muốn khi code xong một stage hoặc step thì phải giải thích rõ
> phần đó đã làm gì, để làm gì, hỏi tôi còn những câu hỏi phụ nào không hoặc sẽ đi sang code
> phần tiếp theo, vì tôi muốn nếu có thắc mắc tôi sẽ được học ngay trong quá trình code"

## 2. Hiểu thành gì

Đổi nhịp làm việc từ *code liên tục nhiều step rồi tổng kết* sang
**code → giải thích → hỏi → mới đi tiếp**.

Điểm cốt lõi nằm ở vế cuối: *"để được học ngay trong quá trình code"*. Nghĩa là phần giải
thích không phải bản tóm tắt hành chính, mà phải **dạy được** — nêu cơ chế, nêu vì sao chọn
cách này chứ không phải cách kia.

| Điểm mơ hồ | Đã hỏi | Trả lời |
|---|---|---|
| "stage hoặc step" — mức nào? | Chưa hỏi, tự chọn mức **step** (nhỏ hơn) | Nếu học viên thấy quá dày, hạ xuống mức stage |

## 3. Vì sao học viên muốn thế

Đây là luận văn thạc sĩ — học viên phải **bảo vệ trước hội đồng** và trả lời câu hỏi về từng
chi tiết kỹ thuật. Code chạy được nhưng không giải thích được thì bảo vệ không qua. Học ngay
lúc làm rẻ hơn nhiều so với học lại vào Tuần 15.

## 4. Đã làm gì để đáp ứng

| File | Tạo/Sửa | Nội dung |
|---|---|---|
| `README.md` mục "Quy định riêng" phần A | Sửa | Đặc tả đầy đủ phiếu bàn giao 7 mục + quy tắc khi học viên hỏi thêm + ngoại lệ |
| `README.md` quy tắc bắt buộc số 8 | Sửa | Thêm bước "viết phiếu bàn giao và DỪNG LẠI hỏi" |
| `chuyende1/notes/_TEMPLATE_ban_giao.md` | Tạo | Mẫu 8 mục |
| `chuyende1/notes/CD1.0_tach-module.md` | Tạo | Phiếu đầu tiên — áp dụng ngay cho chính thay đổi này |
| `pLan/chuyende1/PLAN_CHUYENDE1.md` mục 10 | Sửa | Thêm quy tắc số 8 |

**Vì sao đặt ở `README.md`:** đó là file mà theo hợp đồng repo, Claude Code phải đọc **trước
mỗi phiên code**. Đặt ở chỗ khác sẽ bị quên sau vài phiên.

Mục quan trọng nhất của phiếu là **mục 3 — Cơ chế hoạt động**, bắt buộc giải thích bằng một
ví dụ cụ thể chạy xuyên suốt (một câu tiếng Việt thật, một tensor có số thật), không mô tả
trừu tượng.

## 5. Chi phí

- **Một lần:** ~1 giờ (dựng mẫu + viết quy định)
- **Lặp lại:** +15–30 phút mỗi step
- **Cả kỳ:** ~+6 giờ trên khoảng 15–18 step

Đây là chi phí **đáng trả**: các phiếu bàn giao đến Tuần 13 trở thành bản nháp có sẵn cho
mục "phương pháp" và "quyết định thiết kế" của Chương 4, và cho `qa_preparation.md` ở CD1.13.
Tức là phần lớn chi phí này được thu hồi.

## 6. Có làm lệch kế hoạch gốc không

- [x] **Có, nhưng không đội lịch** — thời gian nằm trong giờ làm việc của từng step, không
      sinh step mới.

## 7. Việc phát sinh về sau

Có, và là nghĩa vụ **lặp lại ở mọi step còn lại**:

- Ghi vào `README.md` mục "Quy định riêng" phần A *(bắt buộc đọc trước mỗi phiên)*
- Nhắc lại ở `chuyende1/MODULE.md` mục 4
- Nhắc lại ở `pLan/chuyende1/PLAN_CHUYENDE1.md` mục 10 quy tắc 8

**Ngoại lệ đã thoả thuận:** khi học viên nói rõ *"làm luôn X rồi Y"* hoặc *"chạy tiếp đi"*
thì bỏ nhịp dừng cho đúng phạm vi đó, nhưng vẫn ghi phiếu.
