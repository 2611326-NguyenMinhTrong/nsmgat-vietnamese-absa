# SỔ TAY LỆNH

> Mọi lệnh trong repo này, xếp theo **việc bạn muốn làm**, không theo tên script.
> Mở file này ra tra là xong — không cần nhớ.
>
> Tất cả lệnh đều chạy trong **PowerShell**, đứng ở thư mục gốc
> `D:\DH20DT_Subject\CaoHoc\Subjects\ScientificPaper\Code`.

---

## 0. Bốn điều biết trước sẽ đỡ mất thời gian

**1. Gõ ngắn lại — bật môi trường ảo một lần cho mỗi cửa sổ terminal**

```powershell
.\.venv\Scripts\Activate.ps1
```

Sau lệnh này, đầu dòng nhắc có chữ `(.venv)`, và mọi lệnh dài
`.\.venv\Scripts\python.exe scripts\...` rút gọn còn:

```powershell
python scripts\cham_trac_nghiem.py 01_UIT-ViSFD
```

Thoát ra: `deactivate`. Nếu PowerShell báo *"running scripts is disabled on this system"*
thì **đừng đổi chính sách bảo mật của máy** — cứ dùng cách dài `.\.venv\Scripts\python.exe`,
kết quả y hệt. Trong sổ này tôi viết cách dài để lệnh nào chép cũng chạy được ngay.

**2. Đừng chép dấu `` ` `` từ tin nhắn hay file markdown**

Trong PowerShell, `` ` `` là **ký tự thoát** (vai trò như `\` trong Linux), không phải dấu
trích dẫn. Chép cả dấu `` ` `` bao quanh tên cờ thì nó biến mất và phần còn lại dính vào
nhau thành một tham số lạ:

```
... 01_UIT-ViSFD `--hien-dap-an`.*   →   error: unrecognized arguments: --hien-dap-an.*
```

**3. Quên lệnh thì hỏi chính nó: `--help`**

Mọi script trong `scripts/` đều có. Phần đầu mỗi script còn viết rõ **vì sao nó tồn tại** và
**giới hạn của nó** — đáng đọc trước khi trích số vào báo cáo:

```powershell
.\.venv\Scripts\python.exe scripts\watch_train.py --help
```

**4. Đọc dòng `usage:` khi bị báo lỗi**

```
usage: cham_trac_nghiem.py [-h] [--hien-dap-an | --an-dap-an] [--khong-luu] [ten]
```

| Ký hiệu | Nghĩa |
|---|---|
| `[...]` | tuỳ chọn, có cũng được không cũng được |
| `a \| b` | **chỉ được chọn một**, không đưa cả hai |
| không ngoặc | bắt buộc |

---

## 1. Tra nhanh

| Tôi muốn… | Lệnh | Mục |
|---|---|---|
| Chạy toàn bộ kiểm thử | `pytest -q` | [§2](#2-môi-trường-và-kiểm-thử) |
| Chuẩn bị dữ liệu lần đầu | `python scripts\prepare_data.py` | [§3](#3-dữ-liệu) |
| Huấn luyện một mô hình | `python -m nsmgat.train --config configs\bilstm.yaml --model bilstm --seed 42` | [§4](#4-huấn-luyện) |
| Chạy tiếp sau khi bị ngắt | thêm `--resume` | [§4](#4-huấn-luyện) |
| Xem quá trình huấn luyện | `python scripts\watch_train.py` | [§5](#5-theo-dõi-huấn-luyện) |
| Hỏi mô hình nghĩ gì về một câu | `python scripts\try_bilstm.py --text "..." --aspect BATTERY` | [§6](#6-thử-tay-mô-hình) |
| Làm việc với ma trận khảo sát | `python scripts\survey_tools.py stats` | [§7](#7-ma-trận-khảo-sát-sota) |
| Sửa ma trận khảo sát bằng Excel | `survey_tools.py excel` → sửa → `tu-excel` | [§7](#7-ma-trận-khảo-sát-sota) |
| Chấm trắc nghiệm đọc bài báo | `python scripts\cham_trac_nghiem.py 01_UIT-ViSFD` | [§8](#8-trắc-nghiệm-đọc-bài-báo) |
| Dựng khung cuốn báo cáo Word | `python scripts\build_cd1_report.py` | [§9](#9-báo-cáo-word) |
| Đổi một file .md sang .docx | `python scripts\md_to_docx_ute.py vào.md ra.docx` | [§9](#9-báo-cáo-word) |
| Đo chất lượng đồ thị cú pháp | `python scripts\diagnose_syntactic_graph.py` | [§10](#10-đồ-thị-cú-pháp-cd13) |
| Dựng lại từ điển cảm xúc | `python scripts\build_lexicon_from_train.py` | [§11](#11-từ-điển-cảm-xúc-cd14a) |

---

## 2. Môi trường và kiểm thử

```powershell
pip install -r requirements.txt                    # cài thư viện (lần đầu)
.\.venv\Scripts\python.exe -m pytest -q            # chạy TẤT CẢ test
.\.venv\Scripts\python.exe -m pytest tests\test_cham_trac_nghiem.py -q   # một file
.\.venv\Scripts\python.exe -m pytest -q -k "resume"                      # lọc theo tên test
.\.venv\Scripts\python.exe -m pytest -q -x                               # dừng ngay ở lỗi đầu
```

**Khi nào chạy:** sau **mỗi** lần sửa code, trước mỗi lần commit. Toàn bộ mất ~1 phút.

`-q` là "quiet" — chỉ in tóm tắt. Bỏ `-q` để xem tên từng test.

---

## 3. Dữ liệu

```powershell
.\.venv\Scripts\python.exe scripts\prepare_data.py               # UIT-ViSFD
.\.venv\Scripts\python.exe scripts\prepare_data.py --with-vlsp   # thêm VLSP 2018
```

| | |
|---|---|
| **Làm gì** | Tải UIT-ViSFD từ HuggingFace, tách câu + tách từ bằng VnCoreNLP, ghi ra `data/processed/*.jsonl` và in thống kê nhãn/khía cạnh |
| **Chạy khi** | Lần đầu cài repo, hoặc sau khi xoá `data/processed/` |
| **Mất bao lâu** | Vài phút (VnCoreNLP khởi động ~5 giây, xử lý toàn bộ lâu hơn) |
| **Lưu ý** | `--with-vlsp` đòi bạn **tự tải trước** hai thư mục VLSP vào `data/raw/vlsp2018/` — script không tự tải được. Chuyên đề 1 chưa cần |

---

## 4. Huấn luyện

```powershell
.\.venv\Scripts\python.exe -m nsmgat.train --config configs\bilstm.yaml --model bilstm --seed 42
```

Đây là lệnh **một dòng duy nhất** cho mọi mô hình — chỉ đổi `--config` và `--model`.

| Cờ | Dùng khi |
|---|---|
| `--config configs\<tên>.yaml` | **Bắt buộc.** Có sẵn: `lexicon`, `bilstm`, `phobert`, `senticgcn`, `nsmgat` |
| `--model <tên>` | **Bắt buộc.** Tên đã đăng ký: `lexicon`, `bilstm`, `dummy` (các mô hình sau sẽ thêm vào) |
| `--seed 42` | Đổi hạt giống ngẫu nhiên. Mỗi mô hình chạy **3 seed**: 42, 1337, 2024 |
| `--resume` | **Chạy tiếp** từ `checkpoints/<exp>/seed<N>/last.pt` sau khi bị ngắt (mất điện, rớt mạng, lỡ đóng terminal) |
| `--no-train` | Chỉ đánh giá lại bằng checkpoint đã có, không huấn luyện |
| `--exp-name <tên>` | Đặt tên thí nghiệm khác tên mô hình (mặc định lấy tên mô hình) |

**Kết quả rơi vào đâu:**

| Đường dẫn | Nội dung |
|---|---|
| `results/<exp>/seed<N>/metrics.json` | **Nguồn sự thật** về kết quả: accuracy, macro-F1, F1 từng lớp, `train_time_sec` |
| `results/<exp>/seed<N>/predictions.jsonl` | Từng dự đoán một — dùng để phân tích lỗi, so sánh hai mô hình trên cùng mẫu |
| `checkpoints/<exp>/seed<N>/best.pt` | Trọng số tốt nhất theo dev macro-F1 |
| `checkpoints/<exp>/seed<N>/last.pt` | Trạng thái để `--resume`. **Xong xuôi rồi thì xoá cho nhẹ đĩa** — file này khá nặng |
| `logs/<exp>/seed<N>.log` | Nhật ký từng epoch, để `watch_train.py` đọc |

**Về `--resume` — ba điều cần biết:**

1. Chạy tiếp cho kết quả **giống hệt** chạy liền một mạch (đã có test chứng minh): nó lưu cả
   trạng thái bộ sinh số ngẫu nhiên, optimizer, scheduler, bộ đếm kiên nhẫn.
2. **Đổi config rồi thì không chạy tiếp được** — script từ chối với thông báo
   *"Khong the chay tiep: cau hinh da doi"*. Đúng như vậy: ghép nửa đầu của cấu hình này với
   nửa sau của cấu hình khác thì con số thu được không có ý nghĩa gì.
3. Bỏ `--resume` mà chạy lại thì nó **huấn luyện từ đầu**, ghi đè kết quả cũ.

---

## 5. Theo dõi huấn luyện

Mở **một cửa sổ PowerShell khác** với cửa sổ đang huấn luyện:

```powershell
.\.venv\Scripts\python.exe scripts\watch_train.py                      # tự tìm lần chạy mới nhất
.\.venv\Scripts\python.exe scripts\watch_train.py --exp bilstm --seed 42   # chỉ đích danh
.\.venv\Scripts\python.exe scripts\watch_train.py --mot-lan            # in trạng thái rồi thoát
.\.venv\Scripts\python.exe scripts\watch_train.py --nhip 5             # 5 giây đọc lại một lần
.\.venv\Scripts\python.exe scripts\watch_train.py --file duong\dan\bat_ky.log
```

**Cho biết:** thời gian từng epoch, train_loss, dev_acc, dev_macro_f1, đếm ngược kiên nhẫn
(early stopping), ước lượng lúc nào xong.

| Lưu ý | |
|---|---|
| Mở trước khi huấn luyện bắt đầu cũng được | Script sẽ **đợi** file log xuất hiện |
| `Ctrl+C` để thoát | Chỉ dừng việc **xem**, không đụng gì tới tiến trình huấn luyện — nó chỉ đọc file |
| Cột "kiên nhẫn" là **ước lượng** | Script mô phỏng lại luật dừng sớm để báo trước, không phải đọc trạng thái thật |
| Thời gian epoch ở đây chênh vài giây | Báo cáo chi phí thì lấy `train_time_sec` trong `metrics.json`, không lấy số ở đây |

---

## 6. Thử tay mô hình

Gõ một câu bất kỳ, xem mô hình nghĩ gì. Cả hai công cụ đều gọi **đúng code thật** của mô
hình, không chép lại công thức — nên những gì bạn thấy chính là những gì mô hình làm.

### BiLSTM — xem mô hình *nhìn vào đâu* trong câu

```powershell
.\.venv\Scripts\python.exe scripts\try_bilstm.py                            # chế độ tương tác
.\.venv\Scripts\python.exe scripts\try_bilstm.py --text "pin trau nhung man hinh toi" --aspect BATTERY
.\.venv\Scripts\python.exe scripts\try_bilstm.py --doi-khia-canh "pin trau nhung man hinh toi"
.\.venv\Scripts\python.exe scripts\try_bilstm.py --uid visfd-test-00042-BATTERY
.\.venv\Scripts\python.exe scripts\try_bilstm.py --sai 10                   # 10 ca mô hình đoán SAI
.\.venv\Scripts\python.exe scripts\try_bilstm.py --lop 1                    # lọc theo lớp (0 NEG, 1 NEU, 2 POS)
```

`--doi-khia-canh` là cái đáng xem nhất: chạy **cùng một câu qua mọi khía cạnh** và in trọng
số attention. Nó cho thấy bằng mắt điều quan trọng nhất của bài toán ACSA — đổi khía cạnh
thì mô hình có nhìn sang chỗ khác trong câu không.

### Từ điển — xem mô hình *chấm điểm từng từ* thế nào

```powershell
.\.venv\Scripts\python.exe scripts\try_lexicon.py                     # chế độ tương tác
.\.venv\Scripts\python.exe scripts\try_lexicon.py --text "pin rat trau"
.\.venv\Scripts\python.exe scripts\try_lexicon.py --word tuyet_voi    # tra một từ
.\.venv\Scripts\python.exe scripts\try_lexicon.py --top 15            # 15 từ dương/âm nhất
.\.venv\Scripts\python.exe scripts\try_lexicon.py --sai 10
```

---

## 7. Ma trận khảo sát SOTA

Dữ liệu: `chuyende1/survey/survey_matrix.csv` — **CSV là bản chính**, file Excel chỉ là bản
trung gian để gõ cho dễ.

```powershell
.\.venv\Scripts\python.exe scripts\survey_tools.py validate    # kiểm cấu trúc: cột, giá trị lạ, ref_key trùng
.\.venv\Scripts\python.exe scripts\survey_tools.py stats       # tiến độ: phủ 6 nhóm tới đâu, bao nhiêu dòng đã kiểm chứng
.\.venv\Scripts\python.exe scripts\survey_tools.py table       # sinh Bảng 3.9 cho báo cáo
```

`table` chỉ lấy dòng **đã kiểm chứng** — dòng còn `chua_kiem` không thể lọt vào bảng của cuốn
báo cáo, kể cả khi vô ý. Đó là quy tắc "không bịa trích dẫn" được cưỡng chế bằng code.

### Sửa bằng Excel cho dễ nhìn

```powershell
.\.venv\Scripts\python.exe scripts\survey_tools.py excel       # csv → xlsx
#  ... mở survey_matrix.xlsx, sửa thoải mái, lưu, rồi ĐÓNG Excel ...
.\.venv\Scripts\python.exe scripts\survey_tools.py tu-excel    # xlsx → csv
.\.venv\Scripts\python.exe scripts\survey_tools.py validate    # kiểm lại sau khi nhập về
```

| Lưu ý | |
|---|---|
| **Phải đóng Excel** trước khi chạy `tu-excel` | Excel khoá file; script báo lỗi rõ ràng và **không** ghi đè gì cả |
| Đừng mở thẳng CSV bằng Excel | Excel đọc CSV theo bảng mã ANSI và dấu `;` của máy Việt Nam → chữ vỡ, cột dính. Luôn đi vòng qua `excel` / `tu-excel` |
| Đừng đổi tên cột trong Excel | `tu-excel` từ chối nhập nếu hàng tiêu đề đã khác |

---

## 8. Trắc nghiệm đọc bài báo

Xem thêm [`chuyende1/trac-nghiem/README.md`](chuyende1/trac-nghiem/README.md).

```powershell
.\.venv\Scripts\python.exe scripts\cham_trac_nghiem.py --danh-sach              # có những đề nào, đã làm chưa
.\.venv\Scripts\python.exe scripts\cham_trac_nghiem.py 01_UIT-ViSFD             # chấm
.\.venv\Scripts\python.exe scripts\cham_trac_nghiem.py 01_UIT-ViSFD --hien-dap-an   # chấm + ghi đáp án vào phiếu
.\.venv\Scripts\python.exe scripts\cham_trac_nghiem.py 01_UIT-ViSFD --an-dap-an     # gỡ đáp án khỏi phiếu
.\.venv\Scripts\python.exe scripts\cham_trac_nghiem.py 01_UIT-ViSFD --khong-luu     # chỉ in, không ghi file nào
```

Quy trình: đọc đề trong `de/` → điền phiếu trong `bai-lam/` → **lưu file** → chấm.
Kết quả mỗi lần chấm lưu lại trong `ket-qua/` kèm ngày giờ.

Chưa đạt thì bộ chấm **không hiện đáp án**, chỉ nói câu nào sai và cần đọc lại mục nào.
`--hien-dap-an` là cách bạn chủ động bỏ luật đó.

Hoặc nhắn thẳng Claude Code: *"chấm bài trắc nghiệm UIT-ViSFD"* — sẽ có thêm nhận xét về
**kiểu** lỗi, thứ script không làm được.

---

## 9. Báo cáo Word

```powershell
.\.venv\Scripts\python.exe scripts\build_cd1_report.py           # dựng khung, tự chặn nếu bạn đã sửa tay
.\.venv\Scripts\python.exe scripts\build_cd1_report.py --adopt   # "tôi đã sửa tay, từ nay đừng đụng vào"
.\.venv\Scripts\python.exe scripts\build_cd1_report.py --force   # ghi đè bằng bản mới (tự sao lưu trước)
```

Sinh `chuyende1/report/reference.docx` (mẫu định dạng UTE) và
`chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx` (khung rỗng đủ bìa + 6 chương).

**Chạy lại luôn an toàn:** script nhớ dấu vân tay nội dung lần ghi trước; thấy file đã bị sửa
tay thì nó **từ chối ghi đè** thay vì âm thầm làm mất công sức của bạn.

Đổi một file markdown bất kỳ sang Word đúng định dạng UTE:

```powershell
.\.venv\Scripts\python.exe scripts\md_to_docx_ute.py chuyende1\user-require\REQ-010_dap-an-ngay-tren-phieu.md ra.docx
```

---

## 10. Đồ thị cú pháp (CD1.3)

```powershell
.\.venv\Scripts\python.exe scripts\diagnose_syntactic_graph.py                     # đo trên cả 3 tập
.\.venv\Scripts\python.exe scripts\diagnose_syntactic_graph.py --split train --show 5   # in 5 cây để xem bằng mắt
.\.venv\Scripts\python.exe scripts\probe_force_single_parse.py --n 300             # đo hậu quả của việc ép parse một lần
```

Đo **trước** khi chạy ASGCN/Sentic-GCN. Chỉ số quan trọng nhất: tỉ lệ Example có đồ thị **bị
chia cắt**. Nếu token khía cạnh và từ cảm xúc nằm ở hai mảnh rời nhau thì thêm bao nhiêu lớp
GCN cũng vô ích — và kết quả thấp sẽ là lỗi dữ liệu, không phải kết luận khoa học.

Kết quả: `results/syntactic_graph_stats.json`, `results/force_single_parse_probe.json`.

---

## 11. Từ điển cảm xúc (CD1.4a)

```powershell
.\.venv\Scripts\python.exe scripts\build_lexicon_from_train.py
.\.venv\Scripts\python.exe scripts\build_lexicon_from_train.py --min-freq 5 --smoothing 10
```

Sinh từ điển cảm xúc **từ chính tập train** (kỹ thuật corpus-based lexicon induction), thay
vì phụ thuộc một tài nguyên ngoài chưa kiểm chứng được. Chỉ cần chạy lại khi đổi tham số làm
mượt hoặc ngưỡng tần suất.

---

## 12. Những script CHƯA chạy được

Trong `scripts/` có một số file chỉ dài 3–5 dòng: `make_tables.py`, `error_analysis.py`,
`build_graphs.py`, `analyze_rules.py`, `eval_llm.py`, `check_slides.py`, `calibrate_rules.py`,
`build_affective_lexicon.py`, `analyze_gates.py`, `build_diagnostic_candidates.py`,
`eval_diagnostic_all.py`, `finalize_diagnostic.py`, `make_case_studies.py`, cùng toàn bộ
`*.sh`.

Đó là **chỗ giữ tên cho Chuyên đề 2**, chưa có nội dung. Gọi chúng sẽ không ra gì cả — không
phải bạn gõ sai lệnh.

---

## Khi sổ này không có thứ bạn cần

1. `--help` của script gần nhất.
2. [`chuyende1/MODULE.md`](chuyende1/MODULE.md) — bảng "công cụ": file nào làm gì, vì sao có.
3. Hỏi thẳng Claude Code: *"lệnh nào để …"*.

> **Thêm lệnh mới vào đây** mỗi khi repo có công cụ mới — nếu không, ba tháng nữa lại phải đi
> tìm. Nhắc Claude Code cập nhật file này cùng lúc với việc viết script.
