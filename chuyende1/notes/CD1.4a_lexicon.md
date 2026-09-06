# PHIẾU BÀN GIAO — [CD1.4a] Baseline từ điển cảm xúc

**Ngày:** 06/09/2026 · **Step:** CD1.4a · **Ánh xạ:** `[MỚI]` (bản GVHD duyệt, mục 1) · **Thời gian:** ~2 giờ

> 🎉 **Kết quả thí nghiệm THẬT đầu tiên của Chuyên đề 1.** Từ đây trở đi bảng kết quả
> Chương 4 bắt đầu có số.

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `scripts/build_lexicon_from_train.py` | Tạo | Sinh từ điển cảm xúc **chỉ từ tập train** + đo độ phủ + đo trần mù khía cạnh |
| `src/nsmgat/models/lexicon.py` | Tạo | `LexiconModel` — tra cứu từ điển + `Linear(2,3)` hiệu chỉnh ngưỡng |
| `configs/lexicon.yaml` | Tạo | Cấu hình, kế thừa `base.yaml` |
| `src/nsmgat/train.py` | Sửa | Đăng ký `"lexicon"` vào `MODEL_REGISTRY` (đúng 1 dòng, không đụng luồng) |
| `tests/test_lexicon.py` | Tạo | 18 test |
| `data/lexicon_from_train.json` | Sinh | 5.828 token có điểm |
| `results/lexicon_stats.json` | Sinh | Thống kê từ điển |
| `results/lexicon/seed42/metrics.json` | Sinh | **Kết quả thí nghiệm** |

```bash
python scripts/build_lexicon_from_train.py
python -m nsmgat.train --config configs/lexicon.yaml --model lexicon --seed 42
```

## 2. ĐỂ LÀM GÌ

- **Trước:** bảng kết quả Chương 4 trống. Không có mốc nào để nói "mô hình X có đáng dùng không".
- **Sau:** có **sàn tuyệt đối**. Mọi mô hình sau phải hơn nó — nếu PhoBERT không hơn từ điển
  thì có gì đó sai.
- **Nếu bỏ:** bản GVHD duyệt liệt kê "mô hình dựa trên từ điển" ở mục 1, nên bỏ là đi lệch
  cam kết. Và mất luôn hai con số nền quan trọng ở mục 6.

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1. Từ điển đến từ đâu — và vì sao KHÔNG dùng VietSentiWordNet

Repo chưa có từ điển cảm xúc tiếng Việt nào: `rules/lexicon.py` và
`scripts/build_affective_lexicon.py` đều là placeholder của S2.1/S3.2, **thuộc Chuyên đề 2**.

Thay vì phụ thuộc một tài nguyên ngoài chưa kiểm chứng được, tôi **sinh từ điển từ chính tập
train**. Kỹ thuật này có tên: *corpus-based lexicon induction*. Ưu điểm:

- Tái lập 100 %, không phụ thuộc mạng hay giấy phép bên thứ ba
- Khớp miền tuyệt đối (bình luận điện thoại, có teencode/viết tắt)
- **Đo được** độ phủ chính xác

⚠️ Nhưng phải nói rõ: từ điển này trả lời *"tín hiệu từ vựng thuần đi được bao xa"*,
**KHÔNG** trả lời *"VietSentiWordNet có đủ tốt cho Sentic-GCN không"* — đó vẫn là câu hỏi mở
của GAP-002. Trước đây tôi ghi trong plan rằng `lexicon` "trả lời luôn GAP-002" — **đó là nói
quá**, đã sửa lại.

### 3.2. Công thức tính điểm — hai chi tiết quyết định chất lượng

Với mỗi token `t`, gom nhãn của **mọi Example trong train** có chứa `t`:

```
p_pos(t) = (n_pos + k·P_pos) / (n + k)          ← làm mượt
p_neg(t) = (n_neg + k·P_neg) / (n + k)
score(t) = (p_pos(t) − p_neg(t)) − (P_pos − P_neg)
                                    ^^^^^^^^^^^^^ trừ tỉ lệ nền
```

**Chi tiết 1 — làm mượt (`k = 10`).** Không có nó, một từ xuất hiện đúng 2 lần cả hai đều
tích cực sẽ có điểm `+1.0` tuyệt đối, ngang với từ xuất hiện 500 lần. Từ điển sẽ đầy nhiễu.
Làm mượt kéo từ hiếm về 0 theo mức bằng chứng.

**Chi tiết 2 — trừ tỉ lệ nền.** Dữ liệu lệch lớp nặng (56,6 % tích cực). Không trừ thì **mọi**
từ trung tính vẫn có điểm dương, chỉ vì tích cực chiếm đa số. Trừ xong, `score = 0` mang đúng
nghĩa *"từ này không khác gì tỉ lệ chung"*.

Cả hai chi tiết đều có test riêng canh.

**Kiểm tra bằng mắt** — từ điển sinh ra có hợp lý không:

| | Từ |
|---|---|
| Dương nhất | `tuyệt_vời`, `sang_trọng`, `xịn`, `đẹp_mắt`, `tuyệt`, `đỉnh` |
| Âm nhất | `thất_vọng`, `chán`, `tệ`, `bực_mình`, `loạn_xạ` |

Đúng nghĩa. Có một chỗ nhiễu đáng chú ý: **`j7`** lọt vào nhóm âm — đó là tên một model điện
thoại hay bị chê. Đây là *nhiễu miền*, một hạn chế thật của corpus-based lexicon: nó học cả
những thứ không phải cảm xúc.

### 3.3. Phần học được chỉ có 9 tham số

`Linear(2, 3)` = 6 trọng số + 3 bias. Đầu vào 2 đặc trưng:

- `mean_score` — trung bình điểm của các token **tra cứu được**
- `coverage` — tỉ lệ token tra cứu được (cho biết có bao nhiêu bằng chứng)

Vì sao không đặt ngưỡng bằng tay (`score > 0,1 thì tích cực`)? Vì sẽ phải bịa một con số
không có cơ sở — đúng cái bẫy *"confidence = 0,92 ở đâu ra?"*. Học từ train thì ngưỡng có
nguồn gốc kiểm chứng được.

Có test canh `count_params() == 9` — nếu con số này phình to thì nó không còn là "baseline
từ điển" nữa.

### 3.4. Vì sao model phải tự đọc dữ liệu

`collate_fn` không đưa token thô vào batch, chỉ có `input_ids` đã tokenize bằng PhoBERT. Nên
`LexiconModel` tự dựng chỉ mục `uid → tokens` trong `__init__` — **đúng cách `DummyModel` đọc
`train_path`**. Không sửa `collate_fn` (dùng chung cho mọi model, sửa là ảnh hưởng tất cả).

## 4. KẾT QUẢ — và hai phát hiện quan trọng

```json
"test": {
  "accuracy": 0.747,
  "macro_f1": 0.524,
  "f1_per_class": [0.755, 0.000, 0.818]
}
```

### 🔴 Phát hiện 1 — lớp TRUNG TÍNH sụp đổ hoàn toàn

`f1_per_class[1] = 0.000`. Mô hình **không bao giờ** dự đoán trung tính, dù lớp này chiếm
**12,2 %** dữ liệu.

Đây là **xác nhận thực nghiệm cho giả thuyết (3)** trong plan mục 7 ("lớp NEU bị nuốt bởi
NEG"). Nhưng mới ở **mức sàn** — còn phải kiểm ở 5 mô hình còn lại trước khi kết luận đây là
hạn chế chung.

Và nó minh hoạ hoàn hảo vì sao plan chọn **macro-F1** làm độ đo chính:

| Độ đo | Giá trị | Nói gì |
|---|---|---|
| Accuracy | **74,7 %** | Nghe khá ổn — **che giấu hoàn toàn** việc một lớp bị bỏ rơi |
| Macro-F1 | **0,524** | Lộ ra ngay: một lớp có F1 = 0 kéo trung bình xuống |

Nếu báo cáo chỉ dùng accuracy, sai lầm này sẽ không ai thấy.

### 🔴 Phát hiện 2 — trần mù khía cạnh: 80,2 %

Nhãn khía cạnh của UIT-ViSFD là mã phạm trù **tiếng Anh** (`BATTERY`, `CAMERA`, `SER&ACC`)
**không xuất hiện trong câu tiếng Việt**, nên mô hình từ điển không tra cứu được → mọi
Example của **cùng một câu** nhận **cùng một dự đoán**.

Đo được:

| | |
|---|---|
| Câu có > 1 khía cạnh | 86,6 % |
| Câu có khía cạnh **trái nhãn** | **47,0 %** |
| **Trần accuracy cho mô hình mù khía cạnh** | **80,2 %** |

`lexicon` đạt 74,7 % — tức **đã dùng gần hết dư địa** của cách tiếp cận mù khía cạnh. Muốn
vượt 80,2 % thì bắt buộc phải nhìn khía cạnh.

Con số 80,2 % chính là thứ **định lượng** câu "bài toán cần nhìn khía cạnh đến mức nào" —
một luận cứ sẵn cho Chương 5.

### Độ phủ từ điển

| | |
|---|---|
| Token khác nhau trong train | 11.028 |
| Vào từ điển (≥ 5 lần) | 5.828 |
| **Độ phủ token** | **83,3 %** |
| Example không tra cứu được từ nào | **0** |

## 5. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Chọn | Loại | Vì sao loại |
|---|---|---|---|
| Nguồn từ điển | Sinh từ train | VietSentiWordNet | Chưa có trong repo, phụ thuộc ngoài chưa kiểm chứng được, không tái lập chắc chắn |
| | | Tự viết tay 200 từ | Là tri thức chuyên môn của học viên, không phải việc tôi bịa |
| Ngưỡng quyết định | Học `Linear(2,3)` | Đặt tay `score > 0,1` | Phải bịa một con số không cơ sở |
| Đặc trưng | `[mean_score, coverage]` | Chỉ `mean_score` | `coverage` cho mô hình biết có bao nhiêu bằng chứng — ít bằng chứng thì nên thận trọng |
| Đếm token lặp | Mỗi token **1 lần/Example** | Đếm mọi lần xuất hiện | Từ lặp 10 lần trong 1 câu sẽ bị khuếch đại sai |
| Lấy token | Model tự dựng `uid → tokens` | Sửa `collate_fn` thêm token | `collate_fn` dùng chung mọi model — sửa là ảnh hưởng tất cả |
| Bộ nhớ đệm đặc trưng | **Có** | Không | Không cache thì `train_time_sec` phình lên ~190 s cho mô hình 9 tham số → **sai bảng chi phí ở CD1.10** |

## 6. KIỂM CHỨNG

```
python -m pytest tests/ -q     → xem mục dưới
python -m pytest tests/test_lexicon.py -q   → 18 passed
```

Test quan trọng nhất: **`test_script_chi_doc_tap_train`** — canh rò rỉ dữ liệu. Nếu từ điển
vô tình đọc dev/test thì mọi kết quả của baseline này vô giá trị, và lỗi đó **rất khó phát
hiện bằng mắt**.

Các test khác đáng chú ý:

- `test_lam_muot_keo_tu_hiem_ve_0` — canh chi tiết 1
- `test_tru_ti_le_nen_lam_tu_trung_tinh_ve_0` — canh chi tiết 2
- `test_token_lap_trong_mot_cau_chi_dem_mot_lan`
- `test_rat_it_tham_so_hoc_duoc` — canh `count_params() == 9`

## 7. DỪNG LẠI VÀ HỎI

**Một điều tôi phải tự sửa:** trong plan tôi từng viết `lexicon` "trả lời luôn GAP-002".
Khi thực sự làm mới thấy **đó là nói quá** — từ điển sinh từ train trả lời *"tín hiệu từ vựng
đi được bao xa"*, chứ không trả lời *"VietSentiWordNet có đủ tốt cho Sentic-GCN không"*.
GAP-002 vẫn mở. Đã sửa lại mô tả trong plan.

**Câu hỏi mở:**

1. Có muốn tôi **cũng thử VietSentiWordNet** khi làm CD1.6b (Sentic-GCN) để so với từ điển
   sinh từ train không? Sẽ trả lời trực tiếp GAP-002, nhưng phải tìm và kiểm chứng nguồn.
2. `lexicon` chạy **1 seed** hay **3 seed**? Nó gần như tất định (chỉ 9 tham số, không có
   dropout), nên 3 seed có thể cho kết quả gần giống hệt. Tôi nghiêng về chạy 3 seed cho
   nhất quán với các mô hình khác, và nếu std ≈ 0 thì **đó cũng là một quan sát đáng ghi**.

**Những chỗ bạn có thể muốn hỏi thêm:**

- Vì sao "trừ tỉ lệ nền" lại quan trọng đến thế?
- Lớp trung tính sụp đổ — đó là lỗi của mô hình hay của dữ liệu?
- Trần 80,2 % tính ra bằng cách nào, và nó có phải trần thật không?

**Step kế tiếp:** **CD1.4b `bilstm`** (cùng Tuần 3) — mốc trước kỷ nguyên PLM.

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
