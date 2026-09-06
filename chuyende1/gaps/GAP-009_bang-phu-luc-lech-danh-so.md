# GAP-009 — Bảng phụ lục còn đánh số CD1.x cũ sau khi sửa GAP-006

**Ngày phát hiện:** 06/09/2026 · **Phát hiện bởi:** học viên (hỏi "CD1.4 là làm những gì?")
**Loại:** tài liệu · **Mức độ:** nhẹ · **Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

`pLan/chuyende1/PLAN_CHUYENDE1.md` có **ba bảng cùng nói về danh sách baseline**:

| Bảng | Mục |
|---|---|
| Bảng 6 mô hình | mục 2 |
| Lịch 15 tuần | mục 4 |
| **Ánh xạ CD1 ↔ plan gốc** | **phụ lục** |

Khi sửa GAP-006 (02/09), tôi cập nhật hai bảng đầu nhưng **quên bảng phụ lục**. Nó vẫn giữ
đánh số cũ:

| Phụ lục ghi (SAI) | Thực tế sau GAP-006 |
|---|---|
| CD1.4 = PhoBERT | CD1.4a = `lexicon`, CD1.4b = `bilstm` |
| CD1.5 = Sentic-GCN | CD1.5 = `phobert` |
| CD1.6 = ViSoBERT | CD1.6a = `asgcn`, CD1.6b = `senticgcn` |
| CD1.7 = LLM | CD1.7 = `gpt4o_zeroshot` (đúng vị trí, sai tên) |

## 2. Phát hiện thế nào

Học viên hỏi một câu rất bình thường: *"CD1.4 là làm những gì?"*. Khi `grep` để trả lời cho
chắc thì thấy hai chỗ trong cùng một file nói hai điều khác nhau.

Đáng chú ý: lỗi này tồn tại **4 ngày** (02/09 → 06/09) mà không ai phát hiện, kể cả khi tôi
sửa cùng file đó nhiều lần cho GAP-007 và CD1.4a.

## 3. Nguyên nhân gốc

**Cùng một mẫu hỏng đã lặp lại lần thứ tư** — GAP-004, GAP-005, GAP-006 và nay GAP-009:
*một thông tin nằm ở nhiều nơi, sửa một nơi mà quên nơi khác.*

Khác biệt lần này: cả ba bảng nằm **trong cùng một file**. Nên bài học không phải "rà nhiều
file hơn" mà là **"đếm xem có bao nhiêu chỗ nói cùng một thứ, TRƯỚC khi sửa chỗ đầu tiên"**.

## 4. Đã sửa thế nào

1. Cập nhật bảng phụ lục cho khớp thực tế (thêm CD1.4a/b, CD1.6a/b, `visobert` tuỳ chọn)
2. Thêm cảnh báo ngay trên bảng: *"phải sửa cùng lúc với bảng ở mục 2 và mục 4"*

## 5. Bài học

Trước khi sửa một thông tin trong tài liệu dài, **`grep` chính thông tin đó trong cùng file
trước** — không chỉ trong các file khác. Trùng lặp trong nội bộ một file khó thấy hơn trùng
lặp giữa các file, vì ta tưởng "đã sửa file này rồi".

Với ba bảng baseline: đã thêm ghi chú chéo để lần sau ai sửa cũng thấy ngay còn hai bảng nữa.

## 6. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — lỗi tài liệu nội bộ, không ảnh hưởng kết quả. Giữ để rút kinh nghiệm về
      mẫu hỏng lặp lại.
