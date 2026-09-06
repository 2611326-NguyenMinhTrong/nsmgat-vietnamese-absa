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
| [GAP-002](GAP-002_senticgcn-can-tu-dien-cam-xuc.md) | 27/08/2026 | Phương pháp | ~~Nghiêm trọng~~ → **Nhẹ** | Sentic-GCN cần từ điển cảm xúc tiếng Việt | 🟡 Nhẹ đi nhờ GAP-006: bản duyệt có sẵn `asgcn` (cú pháp thuần) và `lexicon` (đo trực tiếp chất lượng từ điển) |
| [GAP-003](GAP-003_llm-3-seed-vo-nghia.md) | 27/08/2026 | Phương pháp | **Nghiêm trọng** | Chạy `llm_zs` 3 seed ở temperature 0 cho std = 0 giả tạo | 🔴 Mở |
| [GAP-004](GAP-004_lech-ten-thi-nghiem-llm.md) | 27/08/2026 | Tài liệu | Nhẹ | Lệch tên `gpt4o_zeroshot` vs `llm_zs` | ✅ **Đã đóng** — bản GVHD duyệt chỉ đích danh GPT-4o, giữ tên gốc `gpt4o_zeroshot` |
| [GAP-005](GAP-005_sai-ten-hoc-vien-va-hoc-vi-gvhd.md) | 27/08/2026 | Tài liệu | **Nghiêm trọng** | Sai tên học viên (Trọng → **Trộng**) và sai học vị GVHD (ThS. → **TS.**) trên 5 file, gồm cả bìa và phiếu sắp gửi Cô | 🟡 Còn 1 file `.docx` chờ sinh lại |
| [GAP-006](GAP-006_khong-doc-tai-lieu-gvhd-da-duyet.md) | 02/09/2026 | Kế hoạch | **Nghiêm trọng** | Lập plan 15 tuần mà không hỏi "đã có tài liệu nào GVHD duyệt chưa?" → thiếu hẳn baseline `asgcn`, tự đặt tên đề tài khác bản chính thức | 🟡 Đang sửa |
| [GAP-007](GAP-007_do-thi-cu-phap-bi-chia-cat.md) | 02/09/2026 | Phương pháp | **Nghiêm trọng** | **52,2 % Example có đồ thị cú pháp bị chia cắt** (2–32 mảnh rời nhau). Đo sâu hơn: chỉ 12,5 % câu chuyển ý bị đứt → nhẹ hơn lo ngại ban đầu | 🟡 **Đã chốt phương án C** (06/09) — hạ tầng `link_roots` xong + 9 test; chờ chạy ở CD1.6a. Đã thử và loại phương án D (ép parse: đổi 24,8% head) |
| [GAP-008](GAP-008_train-time-bi-nhiem-chi-phi-tokenize.md) | 06/09/2026 | Số liệu | Nhẹ (sẽ nặng ở CD1.10) | `train_time_sec` gồm cả tokenize PhoBERT mà `lexicon` không dùng — ~127/198 s là lãng phí, sẽ thổi phồng chi phí baseline rẻ nhất trong bảng 4.5 | 🔴 Mở — xử lý ở CD1.10 |

**Trạng thái:** 🔴 Mở · 🟡 Đang xử lý · ✅ Đã sửa · ⚪ Chấp nhận sống chung (ghi rõ lý do trong file)

---

## Thống kê *(cập nhật khi viết Chương 6)*

| Loại | Số lượng | Đã sửa/đóng | Còn mở |
|---|---|---|---|
| Kế hoạch | 1 | 0 | 1 |
| Code | 0 | 0 | 0 |
| Tài liệu | 3 | 2 | 1 |
| Số liệu | 1 | 0 | 1 |
| Phương pháp | 3 | 0 | 3 (1 nhẹ đi, 1 đã chốt phương án) |
| **Tổng** | **8** | **2** | **6** |

**Mẫu hỏng lặp lại — đáng chú ý:** GAP-004, GAP-005 và GAP-006 cùng một cơ chế — *một giá trị sai
hoặc lệch ở nguồn lan âm thầm ra mọi thứ dẫn xuất từ nó*. Cùng cơ chế với lý do
`metrics.json` được đóng băng làm nguồn duy nhất. Khi thấy một giá trị xuất hiện ở nhiều
file, hỏi ngay: **file nào là nguồn, và ai đã kiểm chứng nguồn đó?**
