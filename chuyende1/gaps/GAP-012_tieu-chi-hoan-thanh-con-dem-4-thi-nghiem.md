# GAP-012 — Tiêu chí hoàn thành còn đếm "4 thí nghiệm" sau khi GAP-006 nâng lên 7

**Ngày phát hiện:** 08/09/2026 · **Phát hiện bởi:** Claude Code (cùng lúc với GAP-011)
**Loại:** tài liệu
**Mức độ:** nhẹ (chỉ lệch tài liệu — nhưng là tài liệu định nghĩa "xong")
**Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

`chuyende1/MODULE.md` mục 5, dòng tiêu chí thứ hai:

> **12 thư mục** `results/**{4 exp}**/seed{42,1337,2024}/`

Con số này có từ trước GAP-006. Sau khi đối chiếu bản GVHD đã duyệt
(`docs/Tom_Tat_Dinh_Huong_Final.docx`), danh sách thí nghiệm đã thành **7**:

| # | Thí nghiệm | Step |
|---|---|---|
| 1 | `lexicon` | CD1.4a |
| 2 | `bilstm` | CD1.4b |
| 3 | `phobert` | CD1.5 |
| 4 | `asgcn` | CD1.6a |
| 5 | `asgcn_linked` | CD1.6a |
| 6 | `senticgcn` | CD1.6b |
| 7 | `gpt4o_zeroshot` | CD1.7 |

Nên con số đúng là **19 thư mục**, không phải 12: 6 thí nghiệm × 3 seed = 18, cộng
`gpt4o_zeroshot` chỉ **1** thư mục — vì GAP-003 đã chỉ ra chạy LLM 3 seed ở
`temperature = 0` cho độ lệch chuẩn bằng 0 một cách giả tạo, không phải đo được gì.

## 2. Phát hiện thế nào

Đang tra `predictions.jsonl` cho GAP-011 thì đọc trúng dòng bên cạnh và thấy `{4 exp}`.
Tức là phát hiện **tình cờ**, không phải nhờ có cơ chế nào bắt được.

Đó chính là điều đáng lo: GAP-009 (cũng là số CD1.x cũ sót lại) tồn tại 4 ngày, cũng chỉ
lộ ra khi học viên tình cờ hỏi một câu.

## 3. Nguyên nhân gốc

**Cùng một cơ chế đã ghi trong `INDEX.md` — nay là lần thứ NĂM:**
*một giá trị nằm ở nhiều nơi, sửa nơi này quên nơi kia.*

Cụ thể hơn ở lần này: khi sửa GAP-006 đã đi sửa danh sách baseline trong plan và trong
bảng phụ lục (GAP-009), nhưng **không ai đi tìm những chỗ chỉ chứa *số đếm* của danh sách
đó**. Tìm chuỗi `"visobert"` hay `"asgcn"` thì ra; tìm số `4` thì không ai nghĩ tới.

Đây là dạng khó thấy nhất của mẫu hỏng này: **giá trị dẫn xuất** (số đếm) không chứa
bất kỳ chữ nào của nguồn, nên mọi cách tìm theo tên đều trượt.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| `chuyende1/MODULE.md` mục 5 | Có — đã sửa |
| Số liệu đã sinh ra | Không. Đây là tiêu chí *nghiệm thu*, không tham gia tính toán gì |
| Rủi ro thật | Nếu tới Tuần 13 mới đọc dòng này, có thể tưởng đã xong khi mới có 12/19 thư mục |

## 5. Đã sửa thế nào

Sửa `MODULE.md` mục 5: thay `12 thư mục results/{4 exp}/...` bằng danh sách **kể tên
từng thí nghiệm**, kèm ghi chú vì sao `gpt4o_zeroshot` chỉ 1 seed (trỏ về GAP-003).

**Kể tên thay vì đếm số** là phần chính của cách sửa: một danh sách tên thì tìm kiếm theo
tên bắt được, còn một con số thì không.

## 6. Bài học — phòng lần sau bằng cách nào

**Khi sửa một danh sách, tìm luôn cả những chỗ chỉ chứa SỐ ĐẾM của danh sách đó — và nếu
sửa được thì thay số đếm bằng danh sách kể tên.** Số đếm là giá trị dẫn xuất không mang
dấu vết của nguồn, nên không có cách nào tìm ra nó bằng tên.

Áp dụng ngay: sau này mọi tiêu chí nghiệm thu viết dạng liệt kê, không viết dạng "N cái".

## 7. Có cần đưa vào báo cáo không

- [ ] Có — đưa vào mục 6.2
- [x] Không — sai sót nội bộ, đã sửa, không chạm tới số liệu.
      Nhưng **cơ chế** gây ra nó (lần thứ năm) thì đáng một đoạn trong mục 6.2 nói về
      bài học quản lý tài liệu khi làm nghiên cứu một mình.
