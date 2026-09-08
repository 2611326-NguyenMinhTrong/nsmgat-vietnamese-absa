# MODULE `chuyende1/` — Chuyên đề 1

> **Đây là hợp đồng ranh giới của module.** Đọc trước khi ghi bất kỳ file nào vào thư mục này,
> và trước khi ghi bất kỳ file nào *ngoài* thư mục này nhân danh Chuyên đề 1.
>
> Kế hoạch chi tiết: `pLan/chuyende1/PLAN_CHUYENDE1.md` (không commit — tài liệu cá nhân).
> Dàn ý cuốn báo cáo: `pLan/chuyende1/OUTLINE_BAOCAO_CD1.md`.
> Theo dõi tiến độ: `pLan/chuyende1/progress_cd1.md`.

**Phạm vi:** khảo sát SOTA → thực nghiệm 4 mô hình → so sánh, đánh giá → tìm hạn chế →
định hướng cải tiến cho Chuyên đề 2.
**Thời gian:** 15 tuần, 31/08/2026 – 13/12/2026.
**Sản phẩm nộp:** cuốn chuyên đề A4 ~30 trang (`report/`).

---

## 1. BA VÙNG CỦA REPO — CÁI GÌ DÙNG CHUNG, CÁI GÌ RIÊNG

```
┌─ VÙNG 1 — XƯƠNG SỐNG DÙNG CHUNG ────────────────────────────┐
│  src/  configs/  data/  scripts/  tests/  notebooks/         │
│  results/  checkpoints/  docs/                               │
│                                                              │
│  Mọi module đều đọc và ghi vào đây. KHÔNG chia theo module.  │
│  Lý do: mã nguồn, dữ liệu và kết quả thí nghiệm là tài sản   │
│  tái sử dụng — chia nhỏ theo môn học sẽ phải copy-paste      │
│  và số liệu sẽ phân kỳ giữa các bản sao.                     │
└──────────────────────────────────────────────────────────────┘
              │ sản xuất ra                    │ tiêu thụ
              ▼                                 ▼
┌─ VÙNG 2 — MODULE HỌC VỤ ─────┐   ┌─ VÙNG 3 — SẢN PHẨM CUỐI ──┐
│  chuyende1/   ← module này    │   │  paper/    bài báo         │
│  chuyende2/   ← tạo sau       │   │  thesis/   luận văn        │
│                                │   │  slides/   slide bảo vệ    │
│  Mỗi module sở hữu RIÊNG:      │   │                            │
│  báo cáo, bảng, hình, slide,   │   │  Đọc lại từ Vùng 1 và 2,   │
│  khảo sát, phiếu bàn giao.     │   │  không tự sinh số liệu.    │
└────────────────────────────────┘   └────────────────────────────┘
```

**Nguyên tắc một câu:** *code, dữ liệu, kết quả thì dùng chung; văn bản nộp cho từng môn thì
tách riêng.* Nhờ vậy Chuyên đề 2 và luận văn không phải chạy lại thí nghiệm của Chuyên đề 1,
nhưng cuốn báo cáo của ba nơi không bao giờ lẫn vào nhau.

---

## 2. RANH GIỚI SỞ HỮU CỦA MODULE NÀY

### 2.1. Module SỞ HỮU (được tạo, sửa, xoá tự do)

| Đường dẫn | Nội dung |
|---|---|
| `chuyende1/survey/` | Giao thức khảo sát, ma trận phân loại, phân tích khoảng trống, danh sách đọc bắt buộc (`doc_bat_buoc.md`) |
| `chuyende1/report/` | Cuốn `.docx` nộp + `reference.docx` (style UTE). **Được sửa tay tự do trong Word** — chạy lại `scripts/build_cd1_report.py` an toàn, tự chặn nếu đã sửa (REQ-006). File `.generated.json` cùng thư mục là sổ theo dõi nội bộ của cơ chế đó, không cần đụng vào |
| `chuyende1/tables/` | Bảng xuất ra để dán vào báo cáo |
| `chuyende1/figures/` | Hình, biểu đồ của báo cáo |
| `chuyende1/slides/` | Slide bảo vệ CĐ1 — khối A (lõi 15′) + B (mở rộng 30′) + C (dự phòng Q&A), kèm `qa_preparation.md`. **Trỏ tới `tables/` và `figures/`, không vẽ lại số** |
| `chuyende1/notes/` | Phiếu bàn giao sau mỗi step (xem mục 4) |
| `chuyende1/gaps/` | Sổ sai sót — lỗi kế hoạch/code/tài liệu/số liệu/phương pháp phát hiện khi làm |
| `chuyende1/user-require/` | Sổ yêu cầu bổ sung của học viên ngoài phạm vi đã chốt |

### 2.2. Module ĐƯỢC GHI vào vùng chung (theo đúng quy ước có sẵn)

| Đường dẫn | Điều kiện |
|---|---|
| `results/phobert/`, `results/senticgcn/`, `results/visobert/`, `results/llm_zs/` | Đúng schema `metrics.json` đóng băng ở S0.4. **Bốn tên thí nghiệm này thuộc CĐ1** |
| `results/cost_profile.json`, `results/probe_results.json` | Số liệu không có chỗ trong schema — để file riêng, **không** mở rộng `metrics.json` |
| `configs/visobert.yaml`, `configs/llm_zs.yaml` | Config của 2 baseline mới |
| `src/nsmgat/models/visobert.py` | Kế thừa `BaseModel`, không đổi interface |
| `scripts/compare_baselines.py`, `scripts/probe_oracle_rules.py` | CLI mới, thêm chứ không sửa script cũ |
| `scripts/ute_docx.py` | [CD1.1] Thư viện định dạng Word theo quy định UTE — lề, phông, đánh số trang, mục lục tự động, chú thích bảng/hình. CĐ2 và luận văn dùng lại |
| `scripts/md_to_docx_ute.py` | [REQ-004] Markdown → Word cho tài liệu ngắn (phiếu, ghi chú) |
| `scripts/build_cd1_report.py` | [CD1.1/REQ-006] Dựng `reference.docx` và khung cuốn chuyên đề. **An toàn khi chạy lại** — tự phát hiện và chặn nếu file đã bị sửa tay; xem `sync_all()` |
| `tests/test_ute_docx.py` | [CD1.1] Kiểm định dạng thay cho việc in ra đo bằng thước |
| `scripts/survey_tools.py` | [CD1.2] `validate` / `stats` / `table` cho ma trận khảo sát. **Cưỡng chế quy tắc số 7**: dòng `chua_kiem` không thể lọt vào Bảng 3.9 |
| `tests/test_survey_tools.py` | [CD1.2] Kiểm chốt chặn chống bịa trích dẫn |
| `src/nsmgat/models/bilstm.py` + `configs/bilstm.yaml` | [CD1.4b] Baseline BiLSTM + attention theo khía cạnh. Kế thừa `BaseModel`, không đổi interface |
| `scripts/try_lexicon.py` | [CD1.4a] Công cụ thử tay `LexiconModel` — gõ câu bất kỳ, xem điểm từng token và dự đoán. Gọi đúng code thật của mô hình, không viết lại logic |
| `scripts/try_bilstm.py` | [CD1.4b] Công cụ thử tay `BiLSTMModel` — xem **trọng số attention** và chạy cùng một câu qua **mọi khía cạnh**. Gọi `model.ma_hoa()` / `model._chu_y()` chứ không chép lại công thức; có test canh chống lệch |
| `scripts/watch_train.py` + `tests/test_watch_train.py` | [CD1.4b] Theo dõi **liên tục** một lần huấn luyện: thời gian từng epoch, dev_acc/dev_macro_f1, đếm ngược kiên nhẫn, ước lượng giờ xong. Đọc `logs/<exp>/seed<N>.log`, dùng cho **mọi** mô hình về sau |
| `src/nsmgat/trainer.py` (`--resume`) + `tests/test_resume.py` | [CD1.4b] Chạy **tiếp** một lần huấn luyện bị ngắt (S4.4 kéo lên sớm). Ghi `last.pt` mỗi epoch gồm cả trạng thái sinh số ngẫu nhiên, nên chạy tiếp cho kết quả **giống hệt** chạy liền mạch — có test khoá. Chữ ký `Trainer.train()` không đổi |
| `requirements.txt` | [CD1.1] Thêm `python-docx>=1.1` — CI cài từ file này |
| `data/diagnostic/` | Tập chẩn đoán 300 câu (CD1.8) |
| `docs/annotation_guideline.md` | Hướng dẫn chú thích (S6.2) |

### 2.3. Module KHÔNG ĐƯỢC ĐỘNG VÀO

| Đường dẫn | Lý do |
|---|---|
| `src/nsmgat/schema.py`, `graphs/base.py`, `models/base.py` | Ba hợp đồng đóng băng từ S0.2 |
| Schema `results/{exp}/seed{N}/metrics.json` | Đóng băng từ S0.4 |
| `src/nsmgat/rules/`, `graphs/logic.py`, `graphs/affective.py` | Thuộc Chuyên đề 2 — quy tắc "không viết logic của step chưa tới" |
| `src/nsmgat/models/nsmgat.py` | Thuộc Chuyên đề 2 |
| `src/nsmgat/models/layers.py` → **class `EdgeAwareAttention`** | Thuộc Chuyên đề 2 (S4.1). Nhưng **file `layers.py` thì CĐ1 phải tạo ở CD1.5**: S1.2 yêu cầu `GCNLayer` tổng quát (nhận `edge_weight` tuỳ chọn) để Stage 4 dùng lại. Ranh giới ở đây là **theo class, không theo file** |
| `chuyende2/`, `paper/`, `thesis/`, `slides/` | Module/sản phẩm khác |

> Ngoại lệ duy nhất cho `rules/`: thăm dò **P2** ở CD1.11 cần một bộ nhận diện phủ định
> tối giản. Cài nó trong `scripts/probe_oracle_rules.py`, **không** trong `src/nsmgat/rules/engine.py`.
> Đó là bản thăm dò dùng một lần, không phải bản cài đặt thật của S2.2.

---

## 3. TÀI SẢN CĐ1 BÀN GIAO CHO CĐ2 VÀ LUẬN VĂN

Đây là lý do CĐ1 không phải việc làm xong rồi bỏ. Bốn thứ dưới đây được sản xuất ở CĐ1
và **dùng lại nguyên vẹn** về sau:

| Tài sản | Sinh ra ở | CĐ2 dùng để | Luận văn dùng để |
|---|---|---|---|
| `data/diagnostic/diagnostic_300.jsonl` | CD1.8 | Đo cải thiện theo từng hiện tượng của NS-MGAT | Bảng per-phenomenon |
| `results/{phobert,senticgcn,visobert,llm_zs}/` | CD1.4–CD1.7 | Cột baseline của bảng kết quả chính | Chương thực nghiệm |
| `chuyende1/survey/survey_matrix.csv` | CD1.2 | Định vị đóng góp | Chương 2 Related Work |
| `results/probe_results.json` | CD1.11 | Biện minh cho thiết kế NS-MGAT | Trả lời phản biện |

**Quy tắc bàn giao:** CĐ2 và luận văn **đọc** các tài sản này, **không sửa**. Muốn sửa
(ví dụ phát hiện nhãn sai trong tập chẩn đoán) → sửa tại nguồn ở vùng chung, ghi vào
"Sổ quyết định" trong `pLan/chuyende1/progress_cd1.md`, và **chạy lại** mọi bảng phụ thuộc.

---

## 4. QUY TRÌNH LÀM VIỆC — PHIẾU BÀN GIAO SAU MỖI STEP

Bắt buộc theo quy định riêng của học viên trong `README.md`. Sau khi code xong một step,
**trước khi commit và trước khi sang step kế tiếp**, ghi một phiếu bàn giao vào
`chuyende1/notes/CD1.x_<tên-ngắn>.md` theo mẫu `chuyende1/notes/_TEMPLATE_ban_giao.md`,
rồi **dừng lại hỏi học viên** — không tự động chạy tiếp.

Phiếu bàn giao không phải thủ tục hình thức: đến Tuần 13 khi viết Chương 4, chính các phiếu
này là bản nháp sẵn có của mục "phương pháp" và "quyết định thiết kế".

### 4.1. Ba sổ phải ghi trong suốt quá trình

| Sổ | Ghi khi nào | Ghi cái gì | Thu hồi ở đâu |
|---|---|---|---|
| `notes/` | Xong mỗi step | Phiếu bàn giao 7 mục | Chương 4 (phương pháp, quyết định thiết kế); `qa_preparation.md` ở CD1.13 |
| `gaps/` | **Ngay khi phát hiện** sai sót | Nguyên nhân gốc + bài học | Mục 6.2 "Hạn chế của Chuyên đề 1" |
| `user-require/` | Ngay khi nhận yêu cầu mới ngoài plan | Lời gốc + chi phí + ảnh hưởng lịch | Trả lời GVHD "sao lại làm thêm cái này" |

**Ghi ngay, không để dồn.** Ba sổ này mất giá trị rất nhanh nếu viết lại theo trí nhớ: sai sót
mất phần "vì sao lại sai được", yêu cầu mất lời gốc, phiếu bàn giao mất các phương án đã loại.

**Sai sót do Claude Code gây ra và đã sửa xong vẫn phải ghi.** Giá trị nằm ở nguyên nhân gốc
và bài học, không nằm ở chỗ nó còn tồn tại hay không.

**Hai mốc rà soát bắt buộc:**

- **Tuần 8** — đọc `user-require/INDEX.md`: tổng chi phí phát sinh vượt ~20 giờ thì cắt phạm
  vi hoặc báo GVHD, đừng để đến Tuần 14 mới biết.
- **Tuần 13** — đọc `gaps/INDEX.md` khi viết mục 6.2 của báo cáo.

---

## 5. TIÊU CHÍ HOÀN THÀNH MODULE

Module coi là xong khi cả 6 điều sau đúng:

- [ ] `chuyende1/survey/survey_matrix.csv` có ≥ 45 dòng, đủ 6 nhóm phương pháp
- [ ] Mỗi thí nghiệm có `metrics.json` + `predictions.jsonl` hợp lệ (GAP-011: chưa có code nào ghi `predictions.jsonl`):
      `lexicon`, `bilstm`, `phobert`, `asgcn`, `asgcn_linked`, `senticgcn` — mỗi cái 3 seed {42, 1337, 2024};
      `gpt4o_zeroshot` — **1 seed thôi**, vì `temperature = 0` chạy 3 lần cho độ lệch chuẩn 0 giả tạo (GAP-003).
      Tổng: **19 thư mục**. *(Kể tên chứ không ghi số đếm — xem GAP-012.)*
- [ ] `data/diagnostic/diagnostic_300.jsonl` chốt, Cohen's kappa ≥ 0,70
- [ ] `results/probe_results.json` có đủ 3 con số P1, P2, P3
- [ ] `chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx` ~30 trang, qua hết checklist định dạng
      trong `pLan/chuyende1/OUTLINE_BAOCAO_CD1.md` mục C
- [ ] `chuyende1/slides/` có đủ khối A/B/C; khối A chạy ≤ 15 phút khi bấm giờ thật;
      mọi số trên slide dò được về bảng trong cuốn
- [ ] `chuyende1/slides/qa_preparation.md` có 8 câu khó kèm câu trả lời viết sẵn
- [ ] Mọi step trong `pLan/chuyende1/progress_cd1.md` đã `☑` và có phiếu bàn giao tương ứng
