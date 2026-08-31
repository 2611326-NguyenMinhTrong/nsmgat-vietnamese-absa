# PHIẾU BÀN GIAO — [CD1.0] Tách module Chuyên đề 1 + cài quy trình bàn giao

**Ngày:** 27/08/2026 · **Step:** CD1.0 (chuẩn bị, trước CD1.1) · **Ánh xạ plan gốc:** — (mới)

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `chuyende1/MODULE.md` | Tạo | Hợp đồng ranh giới module: 3 vùng repo, cái gì sở hữu / được ghi / cấm động, tài sản bàn giao cho CĐ2 |
| `chuyende1/survey/{survey_protocol.md, survey_matrix.csv, gap_analysis.md}` | Tạo | Khung cho CD1.2; CSV đã có 16 cột header |
| `chuyende1/notes/_TEMPLATE_ban_giao.md` | Tạo | Mẫu phiếu bàn giao 8 mục |
| `chuyende1/{report,tables,figures,slides}/` | Tạo | Thư mục rỗng có `.gitkeep` |
| `chuyende2/MODULE.md` | Tạo | Giữ chỗ + danh sách tài sản nhận bàn giao từ CĐ1 |
| `README.md` | Sửa | Mục "Cấu trúc thư mục" → mô hình 3 vùng; mục "Quy định riêng" → phần A (phiếu bàn giao) và B (ranh giới module); quy tắc số 8 thêm bước bàn giao |
| `pLan/chuyende1/*.md` | Sửa | Đổi đường dẫn `docs/survey/` → `chuyende1/survey/`, `reports/chuyende1/` → `chuyende1/report|tables|figures/`; thêm quy tắc 8, 9 vào mục 10 |

Không sửa: `src/`, `configs/`, `data/`, `scripts/`, `tests/`, `results/`.

## 2. ĐỂ LÀM GÌ

- **Trước:** `results/`, `docs/` và các thư mục sản phẩm dùng chung cho cả CĐ1, CĐ2 và luận
  văn. Đến Tuần 13, khi cả ba cùng có bảng biểu và bản thảo, không phân biệt được file nào
  của môn nào.
- **Sau:** văn bản nộp của từng môn nằm trong module riêng; code/dữ liệu/kết quả vẫn dùng chung.
- **Bỏ đi thì hỏng ở đâu:** khi bắt đầu CĐ2, nếu chưa có ranh giới, việc đầu tiên sẽ là dọn
  thư mục — và mọi đường dẫn trong bản thảo CĐ1 đã nộp sẽ sai.

## 3. CƠ CHẾ HOẠT ĐỘNG

Phân vùng dựa trên **vòng đời của từng loại tài sản**:

- Tài sản **tích luỹ** (code, dữ liệu, kết quả) — càng gộp càng có giá trị, tách ra là phải
  copy và sẽ phân kỳ → Vùng 1.
- Tài sản **đóng băng theo mốc nộp** (cuốn báo cáo CĐ1) — sau khi nộp không sửa nữa → Vùng 2.
- Tài sản **dẫn xuất** (bài báo, luận văn) — đọc lại từ Vùng 1 và 2 → Vùng 3.

Ràng buộc quyết định: schema `results/{exp}/seed{N}/metrics.json` đóng băng ở S0.4 và
`scripts/make_tables.py` chỉ đọc đúng đường dẫn đó. Nếu đổi thành `results/cd1/{exp}/...`
là phá hợp đồng. Vì vậy `results/` giữ phẳng, phân biệt module bằng **tên thí nghiệm**
(`phobert`/`senticgcn`/`visobert`/`llm_zs` thuộc CĐ1; `nsmgat`/`a1_no_conf`/… thuộc CĐ2),
và quyền sở hữu khai báo trong `MODULE.md` chứ không mã hoá vào đường dẫn.

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Vị trí module | `chuyende1/` ở gốc repo | `deliverables/cd1/` | Thêm một tầng mà không thêm thông tin; gốc repo đã có `paper/`, `thesis/` cùng vai trò |
| Tách `results/` theo module | Không — giữ phẳng | `results/cd1/{exp}/` | Phá schema đóng băng S0.4 và `make_tables.py` |
| Tên file manifest | `MODULE.md` | `README.md` | `.gitignore` có `**/README.md` → manifest sẽ bị ẩn khỏi git |
| `scripts/` tách theo module | Không | `chuyende1/scripts/` | `compare_baselines.py` sẽ dùng lại ở CĐ2; tách sẽ phải copy |
| Vị trí plan | Giữ ở `pLan/chuyende1/` | Chuyển vào `chuyende1/plan/` | `/pLan/` đang bị gitignore theo ý học viên ("tài liệu cá nhân"); chuyển ra sẽ vô tình đẩy lên GitHub |

## 5. ĐIỂM NỐI VỚI STEP SAU

- Step kế tiếp: **CD1.1 — Khởi động & khung báo cáo (Tuần 1)**.
- CD1.1 sẽ ghi vào `chuyende1/report/` (2 file `.docx`) và `chuyende1/survey/survey_protocol.md`
  (điền mục 3, 4 đang là `[TODO]`).
- Điều kiện tiên quyết: ~~mã ngành ghi trên bìa~~ ✅ đã chốt 27/08/2026 —
  **NGÀNH: KHOA HỌC MÁY TÍNH · MÃ SỐ: 8480101**. CD1.1 không còn bị chặn.
- Còn thiếu để in bìa hoàn chỉnh: chuỗi **"TÊN HƯỚNG NGHIÊN CỨU DỰ KIẾN"** (chốt với GVHD Tuần 1).

## 6. KIỂM CHỨNG

```
.venv/Scripts/python.exe -m pytest tests/ -q
......................                                                   [100%]
22 passed in 59.22s
```

`git status --short` → `?? chuyende1/`, `?? chuyende2/` (chưa bị `.gitignore` chặn — đúng ý định).
Chưa có số liệu thí nghiệm nào ở step này.

## 7. DỪNG LẠI VÀ HỎI

**Câu hỏi mở:**

1. `chuyende1/report/*.docx` có nên commit lên GitHub không? Hiện đang được track.
2. Có muốn `chuyende1/` bị gitignore giống `/pLan/` và `/docs/` (tài liệu cá nhân) không?

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
