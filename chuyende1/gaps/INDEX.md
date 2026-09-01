# SỔ SAI SÓT — Chuyên đề 1

> Nơi lưu mọi sai sót phát hiện trong quá trình thực hiện: lỗi kế hoạch, lỗi code, lỗi tài liệu,
> lỗi số liệu, lỗi phương pháp luận. Mỗi sai sót một file `GAP-00x_<tên-ngắn>.md`
> theo mẫu [`_TEMPLATE_gap.md`](_TEMPLATE_gap.md).

**Vì sao cần sổ này — ba lý do, lý do thứ ba là quan trọng nhất:**

1. Sai sót không ghi lại sẽ tái phát ở Chuyên đề 2.
2. Khi hội đồng hỏi "sao chỗ này khác với plan ban đầu", có chỗ tra.
3. **Đến Tuần 13, sổ này là nguyên liệu có sẵn cho mục 6.2 "Hạn chế của Chuyên đề 1"
   trong cuốn báo cáo.** Thừa nhận hạn chế có bằng chứng cụ thể thuyết phục hơn nhiều
   so với một đoạn văn chung chung viết vội cuối kỳ.

**Quy tắc ghi:** phát hiện lúc nào ghi lúc đó, **kể cả sai sót do chính Claude Code gây ra**
và đã sửa xong. Sai sót đã sửa vẫn phải ghi — giá trị nằm ở mục "nguyên nhân gốc" và
"bài học", không nằm ở việc nó còn tồn tại hay không.

---

## Bảng theo dõi

| ID | Ngày | Loại | Mức độ | Tóm tắt | Trạng thái |
|---|---|---|---|---|---|
| [GAP-001](GAP-001_ranh-gioi-layers-py.md) | 27/08/2026 | Tài liệu | Nhẹ | `MODULE.md` cấm CĐ1 động `models/layers.py`, nhưng S1.2 yêu cầu CD1.5 phải tạo `GCNLayer` trong đó | ✅ Đã sửa |
| [GAP-002](GAP-002_senticgcn-can-tu-dien-cam-xuc.md) | 27/08/2026 | Phương pháp | **Nghiêm trọng** | Sentic-GCN cần từ điển cảm xúc tiếng Việt, nhưng bước dựng từ điển (S2.1) thuộc CĐ2 | 🔴 Mở |
| [GAP-003](GAP-003_llm-3-seed-vo-nghia.md) | 27/08/2026 | Phương pháp | **Nghiêm trọng** | Chạy `llm_zs` 3 seed ở temperature 0 cho std = 0 giả tạo | 🔴 Mở |
| [GAP-004](GAP-004_lech-ten-thi-nghiem-llm.md) | 27/08/2026 | Tài liệu | Nhẹ | Plan gốc ghi `results/gpt4o_zeroshot/`, plan CĐ1 ghi `results/llm_zs/` | 🔴 Mở |
| [GAP-005](GAP-005_sai-ten-hoc-vien-va-hoc-vi-gvhd.md) | 27/08/2026 | Tài liệu | **Nghiêm trọng** | Sai tên học viên (Trọng → **Trộng**) và sai học vị GVHD (ThS. → **TS.**) trên 5 file, gồm cả bìa và phiếu sắp gửi Cô | 🟡 Còn 1 file `.docx` chờ sinh lại |

**Trạng thái:** 🔴 Mở · 🟡 Đang xử lý · ✅ Đã sửa · ⚪ Chấp nhận sống chung (ghi rõ lý do trong file)

---

## Thống kê *(cập nhật khi viết Chương 6)*

| Loại | Số lượng | Đã sửa | Còn mở |
|---|---|---|---|
| Kế hoạch | 0 | 0 | 0 |
| Code | 0 | 0 | 0 |
| Tài liệu | 3 | 1 | 2 |
| Số liệu | 0 | 0 | 0 |
| Phương pháp | 2 | 0 | 2 |
| **Tổng** | **5** | **1** | **4** |

**Mẫu hỏng lặp lại — đáng chú ý:** GAP-004 và GAP-005 cùng một cơ chế — *một giá trị sai
hoặc lệch ở nguồn lan âm thầm ra mọi thứ dẫn xuất từ nó*. Cùng cơ chế với lý do
`metrics.json` được đóng băng làm nguồn duy nhất. Khi thấy một giá trị xuất hiện ở nhiều
file, hỏi ngay: **file nào là nguồn, và ai đã kiểm chứng nguồn đó?**
