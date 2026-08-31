# GAP-004 — Lệch tên thư mục thí nghiệm LLM giữa hai plan

**Ngày phát hiện:** 27/08/2026 · **Phát hiện bởi:** Claude Code (khi đọc đặc tả S1.3)
**Loại:** tài liệu · **Mức độ:** nhẹ · **Trạng thái:** 🔴 Mở

---

## 1. Sai ở đâu

Hai nguồn ghi hai tên khác nhau cho cùng một thí nghiệm:

| Nguồn | Tên thư mục |
|---|---|
| `pLan/PLAN_NSMGAT.md` mục S1.3 | `results/gpt4o_zeroshot/` |
| `pLan/chuyende1/PLAN_CHUYENDE1.md` | `results/llm_zs/` |

`exp_name` không nằm trong nhóm hợp đồng đóng băng (chỉ `schema.py`, `graphs/base.py`,
`models/base.py` và schema `metrics.json` mới đóng băng), nên đổi tên **không phá hợp đồng**.
Nhưng để hai tên cùng tồn tại thì `scripts/make_tables.py` và `compare_baselines.py` sẽ đọc
hụt một thư mục, và bảng kết quả sẽ thiếu dòng mà không báo lỗi.

## 2. Nguyên nhân gốc

Khi viết plan CĐ1, tôi đặt tên mới cho dễ đọc mà **không đối chiếu với tên đã có trong plan
gốc**. Đây là rủi ro cố hữu của việc có hai tài liệu kế hoạch cùng mô tả một thí nghiệm.

## 3. Nên chốt tên nào

**Đề xuất: `llm_zs`.** Lý do:

- `gpt4o_zeroshot` gắn cứng nhà cung cấp và phiên bản model vào **đường dẫn thư mục**. Đổi
  sang Gemini hay Claude là phải đổi tên thư mục, mà đổi tên thư mục thì mọi bảng đã sinh
  đều hỏng.
- Thông tin nhà cung cấp/phiên bản thuộc về **nội dung** `configs/llm_zs.yaml`, không thuộc
  về **định danh** thí nghiệm.
- Nếu sau này chạy thêm few-shot thì đặt `llm_fs` — cùng họ tên, dễ nhóm.

Đổi lại: phải sửa một dòng trong `PLAN_NSMGAT.md` mục S1.3 (Output). Đây là plan gốc — theo
quy tắc số 5 của repo, **báo học viên trước khi sửa**, không tự đổi.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Ghi chú |
|---|---|
| `pLan/PLAN_NSMGAT.md` S1.3 | Cần học viên đồng ý mới sửa |
| `scripts/eval_llm.py` (chưa cài) | Sẽ viết theo tên đã chốt |
| `scripts/run_all_baselines.sh` | Kiểm lại khi làm CD1.7 |

Chưa chạy nên chưa có thư mục nào sai tên.

## 5. Bài học

**Khi tạo tài liệu kế hoạch thứ hai mô tả cùng một thí nghiệm, `grep` mọi định danh (tên
thí nghiệm, tên file, tên config) trong tài liệu gốc trước khi đặt tên mới.** Định danh là
thứ hai tài liệu bắt buộc phải khớp — mô tả thì có thể diễn đạt khác nhau, tên thì không.

## 6. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — thuần tuý quy ước đặt tên nội bộ.
