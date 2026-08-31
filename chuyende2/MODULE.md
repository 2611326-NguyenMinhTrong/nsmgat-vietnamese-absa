# MODULE `chuyende2/` — Chuyên đề 2 *(chưa bắt đầu)*

Thư mục giữ chỗ. Cấu trúc sẽ dựng khi Chuyên đề 1 kết thúc (dự kiến sau 13/12/2026),
theo đúng khuôn của `chuyende1/MODULE.md`.

**Phạm vi dự kiến:** cài đặt NS-MGAT — tầng symbolic + hiệu chỉnh confidence (S2),
đồ thị cảm xúc và gộp đồ thị (S3.2, S3.3), mô hình (S4), thí nghiệm + ablation (S5).
Chi tiết kỹ thuật: `pLan/PLAN_NSMGAT.md`, Stage S2 → S5.

**Nhận bàn giao từ Chuyên đề 1** (đọc, không sửa — xem `chuyende1/MODULE.md` mục 3):

- `data/diagnostic/diagnostic_300.jsonl` — tập chẩn đoán 300 câu, có kappa
- `results/{phobert,senticgcn,visobert,llm_zs}/seed{42,1337,2024}/` — cột baseline
- `chuyende1/survey/survey_matrix.csv` — định vị đóng góp
- `results/probe_results.json` — trần cải tiến P1/P2/P3, biện minh cho thiết kế

**Chưa được động vào cho tới khi CĐ1 xong:** `src/nsmgat/rules/`, `graphs/logic.py`,
`graphs/affective.py`, `models/nsmgat.py`, `models/layers.py`.
