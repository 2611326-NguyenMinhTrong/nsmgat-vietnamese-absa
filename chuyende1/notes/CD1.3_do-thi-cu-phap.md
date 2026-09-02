# PHIẾU BÀN GIAO — [CD1.3] Đồ thị cú pháp

**Ngày:** 02/09/2026 · **Step:** CD1.3 · **Ánh xạ plan gốc:** **S3.1** · **Thời gian:** ~1,5 giờ

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `src/nsmgat/graphs/syntactic.py` | Điền | `SyntacticGraphBuilder` — sinh cạnh hai chiều + self-loop từ cây phụ thuộc |
| `tests/test_graphs.py` | Điền | 24 test: câu mẫu biết trước, ca biên, dữ liệu thật, đếm thành phần liên thông |
| `scripts/diagnose_syntactic_graph.py` | Tạo | Chẩn đoán chất lượng cây phụ thuộc — giảm thiểu rủi ro **R3** |
| `results/syntactic_graph_stats.json` | Sinh | Số liệu chẩn đoán cho cả 3 split |
| `chuyende1/gaps/GAP-007` | Tạo | Phát hiện 52,2 % đồ thị bị chia cắt |

```bash
python -m pytest tests/test_graphs.py -q          # 24 passed
python scripts/diagnose_syntactic_graph.py         # -> results/syntactic_graph_stats.json
python -m pytest tests/ -q                         # 98 passed
```

## 2. ĐỂ LÀM GÌ

- **Trước:** `graphs/syntactic.py` chỉ là placeholder. Không có cách nào biến cây phụ thuộc
  đã có trong `Example` thành `TypedEdge` mà model dùng được.
- **Sau:** cả `asgcn` và `senticgcn` đã có đầu vào. Đây là **điều kiện cần của cả hai** —
  nằm trên đường găng.
- **Nếu bỏ:** CD1.6a và CD1.6b không chạy được. Và ở CĐ2, cả NS-MGAT cũng dùng chính view
  `syn` này làm một trong ba đồ thị.

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1. Đi qua một ví dụ cụ thể

Câu `"pin rất trâu"`, cây phụ thuộc VnCoreNLP (chỉ số 0-based, −1 = root):

```
  idx  token   head  deprel
   0   pin      2    nsubj        trâu(2)
   1   rất      2    adv          /     \
   2   trâu    -1    root     pin(0)   rất(1)
```

Builder sinh ra **7 cạnh**:

| # | Cạnh | etype | Vì sao có |
|---|---|---|---|
| 1 | 2 → 0 | `DEP:nsubj` | chiều xuôi: head → dependent |
| 2 | 0 → 2 | `DEP:nsubj_rev` | **chiều ngược** |
| 3 | 2 → 1 | `DEP:adv` | |
| 4 | 1 → 2 | `DEP:adv_rev` | |
| 5 | 0 → 0 | `DEP:self` | self-loop |
| 6 | 1 → 1 | `DEP:self` | |
| 7 | 2 → 2 | `DEP:self` | |

Công thức tổng quát: **n token, r root ⇒ 2·(n − r) + n cạnh**.

### 3.2. Vì sao phải có chiều ngược — không phải chi tiết vụn vặt

GCN lan truyền theo **chiều** cạnh. Nếu chỉ giữ chiều `head → dependent`, thông tin chỉ chảy
từ gốc cây xuống lá. Mà trong câu `"pin rất trâu"`, từ cảm xúc `trâu` là **gốc**, còn khía
cạnh `pin` là **lá** — thông tin sẽ chảy đúng chiều. Nhưng đổi câu thành `"máy này pin yếu"`
thì khía cạnh có thể nằm cao hơn từ cảm xúc, và thông tin sẽ **không bao giờ tới nơi**.

Thêm cạnh ngược làm đồ thị vô hướng về mặt hiệu quả, nhưng **giữ nhãn phân biệt**
(`nsubj` vs `nsubj_rev`) để model vẫn biết chiều ngữ pháp gốc — mất chiều là mất thông tin.

### 3.3. Vì sao phải có self-loop

Sau mỗi lớp GCN, biểu diễn của một token bị thay bằng trung bình các láng giềng. Không có
self-loop thì token **mất hoàn toàn** biểu diễn của chính nó sau lớp đầu tiên. Self-loop giữ
lại "chính mình" như một láng giềng.

Ngoài ra self-loop còn cứu các token **bị cô lập**: root của mỗi câu con không có cạnh đi
lên, nếu không có self-loop thì nó thành đỉnh không cạnh và GCN trả về vector 0.

### 3.4. Ba ca biên mà đặc tả S3.1 yêu cầu xử lý

| Ca | Xử lý | Vì sao |
|---|---|---|
| `head == -1` (root) | Bỏ qua, không sinh cạnh đi lên | Root không có head |
| `head` ngoài `[0, n)` | Bỏ qua, **không làm sập** | Dữ liệu hỏng không được làm chết pipeline. Đo được: 0 ca trong UIT-ViSFD |
| `head == dep` | Bỏ qua | Sẽ tạo self-loop trùng với self-loop riêng → mỗi token phải đúng **một** self-loop |

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Xử lý đồ thị bị chia cắt | **Không tự ý nối** — giữ đúng đặc tả | Tự thêm cạnh nối các root | Đó là can thiệp **làm đổi kết quả thí nghiệm**, không có trong đặc tả, và không phải quyết định của tôi → đưa thành GAP-007 để học viên chọn |
| Nhãn cạnh ngược | `DEP:x_rev` (nhãn riêng) | Dùng chung nhãn `DEP:x` | Dùng chung là mất thông tin chiều ngữ pháp |
| Vị trí chẩn đoán | Script riêng `diagnose_syntactic_graph.py` | Nhét vào builder | Builder phải thuần và khớp interface `GraphBuilder`; chẩn đoán là việc phân tích, chạy một lần |
| `head` hỏng | Bỏ qua im lặng trong builder, **đếm** trong script chẩn đoán | Raise exception | Một Example hỏng không được làm chết cả pipeline 23.872 mẫu; nhưng vẫn phải đo được |
| Nơi ghi số liệu | `results/syntactic_graph_stats.json` | Thêm trường vào `metrics.json` | `metrics.json` đóng băng ở S0.4 — quy tắc mục 6.4 của plan |

## 5. ĐIỂM NỐI VỚI STEP SAU

- Step kế tiếp theo lịch: **CD1.4a `lexicon`** và **CD1.4b `bilstm`** (Tuần 3) — **không**
  phụ thuộc step này.
- Phụ thuộc thật: **CD1.6a `asgcn`** và **CD1.6b `senticgcn`** dùng trực tiếp
  `SyntacticGraphBuilder.build()` để dựng ma trận kề.
- ⚠️ **Cả hai đang bị chặn bởi GAP-007** — cần chọn phương án trước khi chạy, nếu không sẽ
  không diễn giải được kết quả.
- Ở CĐ2, `graphs/logic.py` và `graphs/affective.py` sẽ sinh thêm cạnh vào **cùng** danh sách
  `TypedEdge`, phân biệt bằng field `view`. Hợp đồng đó đã có sẵn từ S0.2, step này không đụng vào.

## 6. KIỂM CHỨNG

```
.venv/Scripts/python.exe -m pytest tests/ -q
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 75.34s
```

Trước CD1.3 là 74 test, giờ 98 (+24).

**Kết quả chẩn đoán trên dữ liệu thật:**

| Split | Example | Token TB | Cạnh TB | Root TB | Thành phần | **Bị chia cắt** |
|---|---|---|---|---|---|---|
| train | 23.872 | 39,11 | 112,57 | 2,37 | 2,37 (tối đa 32) | **52,2 %** |
| dev | 3.316 | 37,54 | 107,73 | 2,45 | 2,45 (tối đa 16) | **54,3 %** |
| test | 6.722 | 39,36 | 113,07 | 2,51 | 2,51 (tối đa 16) | **55,4 %** |

Bất thường dữ liệu: **0** head ngoài phạm vi, **0** token tự trỏ vào mình — cây phụ thuộc
từ S0.3 sạch về mặt cấu trúc.

## 7. DỪNG LẠI VÀ HỎI

**Câu hỏi chặn — phải trả lời trước CD1.6:**

**GAP-007: 52,2 % Example có đồ thị cú pháp bị chia cắt.** Nguyên nhân đã truy ra và **không
phải lỗi**: UIT-ViSFD "câu" thực ra là bình luận nhiều câu, VnCoreNLP tách câu nên mỗi câu
con có root riêng.

Ba phương án:

| | Phương án | Được gì | Mất gì |
|---|---|---|---|
| **A** | Giữ nguyên | Trung thực với ASGCN/Sentic-GCN gốc | 52 % dữ liệu đồ thị chia cắt, hai baseline có thể yếu vì lý do ngoài phương pháp |
| **B** | Nối các root liền kề | Đồ thị luôn liên thông | Lệch khỏi phương pháp gốc, cạnh nối không có cơ sở ngôn ngữ học |
| **C** | Chạy cả hai (`asgcn` + `asgcn_linked`) | **Đo được chính xác việc chia cắt gây thiệt hại bao nhiêu điểm** | +~1 ngày GPU |

**Tôi nghiêng về C** — không phải để "làm cho chắc", mà vì hiệu số A↔B **chính là một phát
hiện của Chuyên đề 1**: nó trả lời *"cú pháp có thật sự giúp không, hay chỉ giúp khi đồ thị
liền mạch?"*. Đúng loại hạn chế định lượng mà nhiệm vụ 4 của đề bài yêu cầu, và rẻ vì dùng
chung toàn bộ hạ tầng với `asgcn`.

**Những chỗ bạn có thể muốn hỏi thêm:**

- Vì sao cạnh ngược lại quan trọng đến thế với GCN?
- "Thành phần liên thông" là gì, và vì sao con số đó bằng đúng số root?
- Nếu chọn C thì `asgcn_linked` có phải xin phép GVHD không (nó không có trong bản duyệt)?

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
