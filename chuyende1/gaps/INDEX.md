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
| [GAP-009](GAP-009_bang-phu-luc-lech-danh-so.md) | 06/09/2026 | Tài liệu | Nhẹ | Bảng phụ lục trong plan còn đánh số CD1.x cũ sau khi sửa GAP-006 — tồn tại 4 ngày | ✅ Đã sửa |
| [GAP-010](GAP-010_cong-cu-nho-keo-theo-transformers.md) | 07/09/2026 | Code | Nhẹ | `try_lexicon.py` sập vì `load_config` nằm trong `train.py` — kéo theo cả `transformers` chỉ để đọc YAML | ✅ Đã sửa |
| [GAP-011](GAP-011_khong-ai-ghi-predictions-jsonl.md) | 08/09/2026 | Code | **Nghiêm trọng** | `MODULE.md` đòi `predictions.jsonl` nhưng KHÔNG có dòng code nào ghi nó — chặn CD1.9 (phân tích lỗi) và phần kiểm định ý nghĩa thống kê ở CD1.10 | 🔴 Mở |
| [GAP-012](GAP-012_tieu-chi-hoan-thanh-con-dem-4-thi-nghiem.md) | 08/09/2026 | Tài liệu | Nhẹ | Tiêu chí hoàn thành còn đếm "4 thí nghiệm / 12 thư mục" sau khi GAP-006 nâng lên 7 thí nghiệm / 19 thư mục | ✅ Đã sửa |
| [GAP-013](GAP-013_tran-mu-khia-canh-do-tren-train-dung-cho-test.md) | 08/09/2026 | Số liệu | Nhẹ | Trần mù khía cạnh 80,2 % đo trên tập **train** nhưng dùng làm trần cho accuracy tập **test** — trần đúng là **80,88 %**. Kết luận không đổi | ✅ Đã sửa |
| [GAP-014](GAP-014_them-dong-vao-base-yaml-lam-doi-van-tay-cau-hinh.md) | 08/09/2026 | Code | **Nghiêm trọng** | Thêm 3 dòng sổ sách vào `base.yaml` làm đổi `config_hash` của mọi kết quả cũ, dù mọi con số y nguyên — hỏng đúng công dụng của vân tay | ✅ Đã sửa |
| [GAP-015](GAP-015_go-theo-doi-file-xong-nhung-quy-tac-ignore-chua-them.md) | 20/09/2026 | Code | Nhẹ | Gỡ `SO_TAY_LENH.md` khỏi git xong nhưng bước thêm vào `.gitignore` chết giữa chừng (file dùng CRLF) — file thành "chưa theo dõi mà cũng không bị bỏ qua", một `git add .` vô ý là quay lại | ✅ Đã sửa |
| [GAP-016](GAP-016_khong-dinh-nghia-cot-ma-tran-khao-sat.md) | 20/09/2026 | Tài liệu | **Nghiêm trọng nếu để lâu** | 18 cột của ma trận khảo sát không được định nghĩa ở đâu — 3 dòng đã điền thì cả 3 lệch chuẩn (một ô trộn kiến trúc vào biểu diễn đầu vào, tiêu đề bài báo gõ vào ô `nam`) | ✅ Đã sửa |
| [GAP-017](GAP-017_vong-excel-nuot-mat-thay-doi-trong-csv.md) | 20/09/2026 | Code | **Nghiêm trọng** (mất dữ liệu âm thầm) | `tu-excel` ghi đè `.csv` từ bản chụp `.xlsx` mà không kiểm `.csv` có đổi sau khi xuất không — nuốt mất 4 nhóm nội dung vừa commit, không cảnh báo. Cơ chế chống ghi đè đã có sẵn ở REQ-006 nhưng không được áp cho đường ghi này | ✅ Đã sửa |
| [GAP-018](GAP-018_so-lieu-khao-sat-lay-tu-nguon-phu-va-doc-bang-sai-cot.md) | 22/09/2026 | Số liệu | **Nghiêm trọng nếu để lâu** | 9 dòng ma trận khảo sát ghi sai so với bài gốc: lấy số từ bảng baseline của bài khác (Jiang 63,4%), đọc bảng nhiều cột bằng `pypdf` chế độ thường nên lệch cột, và suy luận ô có/không thay vì tìm câu trong bài (3 bài SemEval thực ra có công bố mã). Lộ ra nhờ đối chiếu với bảng baseline của bài đọc sau | ✅ Đã sửa |

| [GAP-019](GAP-019_dap-an-trac-nghiem-lap-theo-chu-ky.md) | 01/10/2026 | Phương pháp | **Nghiêm trọng** (phép đo mất hiệu lực) | Đáp án trắc nghiệm 02 lặp chu kỳ `A C B D` bốn lần — phân bố đều hoàn hảo nhưng đoán được sau 8 câu, nên điểm 15/15 không chứng minh được đã đọc. Test cũ chỉ bắt "dồn vào một chữ cái" nên vẫn xanh | ✅ Đã sửa — xáo lại đề, thêm test chặn mọi chu kỳ |

| [GAP-020](GAP-020_nhan-dien-ve-khia-canh-bang-chi-so-sai-khi-cau-bi-cat.md) | 01/10/2026 | Code | **Nghiêm trọng** (chặn CD1.6a) | `ASGCNModel` nhận diện vế khía cạnh bằng `word_id >= n_tokens`; câu dài bị cắt bớt vế câu nên vế khía cạnh mang chỉ số nhỏ hơn `n_tokens` → ném lỗi giữa lúc huấn luyện trên Colab. 16 test đều chạy trên dev với `max_seq_len=128` nên không câu nào đủ dài để chạm nhánh sai | ✅ Đã sửa — tách hai vế theo cấu trúc `word_ids`, thêm 2 test ép `max_seq_len=16` |

| [GAP-021](GAP-021_map-location-day-trang-thai-ngau-nhien-len-gpu.md) | 02/10/2026 | Code | **Nghiêm trọng** (chặn cơ chế chạy tiếp trên GPU) | `torch.load(..., map_location="cuda")` đẩy cả trạng thái sinh số ngẫu nhiên lên GPU, nên `set_rng_state_all` ném `TypeError: RNG state must be a torch.ByteTensor` ngay đầu lần chạy tiếp. Dòng ngay trên đã phòng đúng chuyện này cho trạng thái CPU rồi bỏ sót chỗ anh em cách hai dòng. Test chạy ở máy không có GPU nên nhánh đó chưa bao giờ được chạm tới — cùng mẫu hỏng với GAP-020 | ✅ Đã sửa — tách hàm chuẩn hoá dùng chung, chặn khi số GPU lệch, thêm 2 test giả lập GPU |

| [GAP-022](GAP-022_tieu-chi-kiem-van-tay-bo-quen-seed.md) | 02/10/2026 | Phương pháp | Trung bình (suýt loại 2 lần chạy đúng) | Tiêu chí kiểm file tải về ghi "vân tay phải là `d2d2aebdc30f`", nhưng `train.py` tiêm `cfg["seed"]` trước khi bấm vân tay nên mỗi seed có một vân tay riêng. Giá trị kỳ vọng được tính bằng đường KHÁC với đường sinh ra giá trị thật | ✅ Đã sửa — kiểm lại bằng đúng đường, cả 3 seed khớp; ghi cách tính đúng vào `notebooks/da-chay/QUY-UOC.md` |

| [GAP-023](GAP-023_doan-lenh-kiem-van-tay-thieu-ten-mo-hinh.md) | 04/10/2026 | Phương pháp | Nhẹ (không số liệu nào đổi) | Đoạn lệnh kiểm vân tay trong `notebooks/da-chay/QUY-UOC.md` chỉ tiêm seed, trong khi `train.py` tiêm cả seed lẫn tên mô hình. Vô hình suốt 9 lần chạy vì tên trong file cấu hình trùng `--model`; `senticgcn.yaml` kế thừa `asgcn.yaml` nên là thí nghiệm đầu tiên lệch. Claude kiểm theo đoạn đó và báo lệch cả ba seed đúng. Lần thứ hai cùng bài học với GAP-022 | ✅ Đã sửa tài liệu — còn đề xuất gom thành một hàm dùng chung, chờ học viên quyết |

| [GAP-024](GAP-024_mat-notebook-phien-colab-senticgcn.md) | 04/10/2026 | Tài liệu | Nhẹ (số liệu nguyên vẹn, mất một lớp bằng chứng) | Mất notebook phiên Colab của cả ba seed `senticgcn`. Mục 10 của `colab_train.ipynb` và ô 10 của `SO_TAY_LENH.md`, hai chỗ đọc lúc chạy, ghi "chỉ cần `metrics.json` và `predictions.jsonl`"; yêu cầu giữ notebook chỉ nằm ở `QUY-UOC.md`, file đọc lúc kiểm chứng. Notebook mở từ GitHub không tự lưu nên không cứu được | ⚪ Sống chung — học viên quyết 05/10 không chạy lại; nhật ký từng epoch và vân tay cấu hình là bằng chứng thay thế. Đã sửa cả ba tài liệu |

**Trạng thái:** 🔴 Mở · 🟡 Đang xử lý · ✅ Đã sửa · ⚪ Chấp nhận sống chung (ghi rõ lý do trong file)

---

## Thống kê *(cập nhật khi viết Chương 6)*

| Loại | Số lượng | Đã sửa/đóng | Còn mở |
|---|---|---|---|
| Kế hoạch | 1 | 0 | 1 |
| Code | 3 | 2 | 1 |
| Tài liệu | 5 | 4 | 1 |
| Số liệu | 2 | 1 | 1 |
| Phương pháp | 3 | 0 | 3 (1 nhẹ đi, 1 đã chốt phương án) |
| **Tổng** | **14** | **7** | **7** |

**Mẫu hỏng lặp lại — ĐÃ NĂM LẦN:** GAP-004, GAP-005, GAP-006, GAP-009 và GAP-012 cùng một cơ chế —
*một giá trị sai hoặc lệch ở nguồn lan âm thầm ra mọi thứ dẫn xuất từ nó*. Cùng cơ chế với lý do
`metrics.json` được đóng băng làm nguồn duy nhất. Khi thấy một giá trị xuất hiện ở nhiều
file, hỏi ngay: **file nào là nguồn, và ai đã kiểm chứng nguồn đó?**

GAP-012 cho thấy dạng khó thấy nhất của mẫu này: giá trị dẫn xuất là một **số đếm**
("4 thí nghiệm"), không chứa chữ nào của nguồn, nên mọi cách tìm theo tên đều trượt.
Cách chống: **tiêu chí nghiệm thu viết dạng kể tên, không viết dạng "N cái"**.

GAP-011 là **mặt trái** của cùng cơ chế: không phải giá trị sai lan ra, mà là một yêu cầu
có ở tài liệu tổng (`MODULE.md`) nhưng mất hút ở từng step, nên mỗi step làm xong đều
tưởng mình đủ.


**Mẫu hỏng thứ hai — GAP-013:** *con số đúng, nhưng ngữ cảnh của nó bị mất trên đường đi.*
Trần 80,2 % đo trên train là đúng; cái sai là không ghi "train" cạnh con số, rồi đem so với
một con số của tập test. Cách chống: **mọi chỉ số về dữ liệu phải mang tên tập ngay trong ô
bảng**, không để trong câu văn xung quanh — câu văn bị cắt khi chép sang tài liệu khác.

GAP-013 được phát hiện nhờ một quy tắc đáng giữ: **khi viết tài liệu tổng hợp, đo lại từ
đầu thay vì chép số từ ghi chú cũ.**

**Mẫu hỏng thứ ba — GAP-014:** *kết luận rộng hơn thứ bằng chứng thật sự chứng minh.*
Một test xanh về khoá `resume` được dùng để phát biểu một điều tổng quát về `base.yaml`.
Test chỉ kiểm thứ mình nghĩ ra để kiểm. Cách chống: **trước khi commit, đọc `git diff` của
những file lẽ ra KHÔNG được đổi** — nhất là `results/**/metrics.json`. Lần này diff bắt được,
test thì không.
