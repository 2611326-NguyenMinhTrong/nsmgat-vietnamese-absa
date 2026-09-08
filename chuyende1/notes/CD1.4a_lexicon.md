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

## BỔ SUNG 09/09/2026 — chạy đủ 3 seed

Ban đầu chỉ chạy seed 42 vì tưởng mô hình tất định. Chạy đủ 3 seed theo yêu cầu học viên:

| seed | accuracy | macro-F1 | F1 tiêu cực | F1 trung tính | F1 tích cực |
|---|---|---|---|---|---|
| 42 | 0,7471 | 0,5242 | 0,7545 | **0,0000** | 0,8180 |
| 1337 | 0,7468 | 0,5239 | 0,7540 | **0,0000** | 0,8178 |
| 2024 | 0,7468 | 0,5239 | 0,7537 | **0,0000** | 0,8179 |
| **TB ± σ** | **0,7469 ± 0,0002** | **0,5240 ± 0,0002** | | **0,0000** | |

**Hai điều học được:**

1. **σ khác 0, nhưng nhỏ tới mức không đổi bất kỳ kết luận nào** (0,0002 — so với 0,0062 của
   `bilstm`, tức nhỏ hơn 30 lần). Mô hình vẫn có phần ngẫu nhiên thật: lớp hiệu chỉnh 9 tham
   số được khởi tạo ngẫu nhiên. Nên đây **không** rơi vào trường hợp GAP-003 (chạy nhiều
   seed cho σ = 0 giả tạo) — chạy 3 seed là hợp lệ, chỉ là không cho thêm thông tin gì.

2. **F1 trung tính = 0,0000 ở CẢ BA seed.** Đây mới là điều đáng giá của việc chạy thêm:
   sự sụp đổ của lớp trung tính **không phải rủi may của một seed**. Không một Example nào
   trong 6.722 mẫu test được đoán là trung tính, ở bất kỳ seed nào. Kết luận ở Phát hiện 1
   giờ đứng vững hơn hẳn.

---

### 🔴 Phát hiện 2 — trần mù khía cạnh: 80,88 % (trên test)

Nhãn khía cạnh của UIT-ViSFD là mã phạm trù **tiếng Anh** (`BATTERY`, `CAMERA`, `SER&ACC`)
**không xuất hiện trong câu tiếng Việt**, nên mô hình từ điển không tra cứu được → mọi
Example của **cùng một câu** nhận **cùng một dự đoán**.

Đo được (GAP-013: bản đầu chỉ ghi số của **train** mà không nói rõ, rồi đem so với
accuracy trên **test** — nay ghi cả hai):

| | train | **test** |
|---|---|---|
| Câu có > 1 khía cạnh | 86,6 % | 86,7 % |
| Câu có khía cạnh **trái nhãn** | 47,0 % | 45,1 % |
| **Trần accuracy cho mô hình mù khía cạnh** | 80,22 % | **80,88 %** |

**Dùng con số nào:** `lexicon` và `bilstm` đều báo accuracy trên **test**, nên trần để so
là **80,88 %**. (dev = 81,45 %, cả ba tập gộp = 80,47 % — ghi ở đây để khỏi đo lại.)

`lexicon` đạt 74,7 % — tức **đã dùng gần hết dư địa** của cách tiếp cận mù khía cạnh. Muốn
vượt 80,88 % thì bắt buộc phải nhìn khía cạnh.

**Đã có kết quả:** `bilstm` (CD1.4b, seed 42) đạt **85,82 %** — vượt trần. Đây là bằng chứng
số học cho việc mô hình thật sự dùng thông tin khía cạnh, không phải đoán may.

Con số 80,88 % chính là thứ **định lượng** câu "bài toán cần nhìn khía cạnh đến mức nào" —
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
- Trần 80,88 % tính ra bằng cách nào, và nó có phải trần thật không?

**Step kế tiếp:** **CD1.4b `bilstm`** (cùng Tuần 3) — mốc trước kỷ nguyên PLM.

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |

---

## BỔ SUNG 07/09/2026 — công cụ thử tay `scripts/try_lexicon.py`

Học viên hỏi: *"có cách nào để tôi test chạy thử các hàm lexicon đã code không?"*

Trước đó chỉ có 3 cách chạy, không cách nào cho phép **gõ một câu bất kỳ và xem mô hình
nghĩ gì**:

| Cách có sẵn | Trả lời được câu hỏi gì |
|---|---|
| `pytest tests/test_lexicon.py` | "Code có đúng không" |
| `python -m nsmgat.train ...` | "Chạy hết tập test thì được bao nhiêu điểm" |
| `python scripts/build_lexicon_from_train.py` | "Từ điển sinh ra thế nào" |
| **`python scripts/try_lexicon.py`** ← mới | **"Mô hình nghĩ gì về CÂU NÀY, và vì sao"** |

### Nguyên tắc thiết kế quan trọng nhất

Công cụ gọi **đúng code thật** của mô hình (`model._dac_trung()`, `model.calibrate`), không
viết lại logic. Nếu viết lại, công cụ và mô hình có thể lệch nhau — và học viên sẽ tin vào
một thứ không phải mô hình thật. Đúng loại lỗi mà cả repo này đang chống (xem mẫu hỏng lặp
lại ở `gaps/INDEX.md`).

Hệ quả kỹ thuật: để gọi được `_dac_trung(uid)` cho câu gõ tay, phải chèn tạm một uid vào
`model.uid_to_tokens`. Đây là **sửa trạng thái mô hình** → có 2 test riêng canh việc dọn sạch
sau khi chạy, và canh việc gõ hai câu liên tiếp không bị dùng lại cache của câu trước.

### Năm chế độ

```bash
python scripts/try_lexicon.py                       # tương tác
python scripts/try_lexicon.py --text "pin rất trâu nhưng màn hình hơi tối"
python scripts/try_lexicon.py --word tuyet_voi      # gõ KHÔNG DẤU vẫn tra được
python scripts/try_lexicon.py --top 15
python scripts/try_lexicon.py --uid visfd-test-00042-BATTERY
python scripts/try_lexicon.py --sai 10              # ca mô hình đoán SAI
```

### Một lỗi phát hiện khi tự thử

Lần chạy đầu, `--word tuyet_voi` (không dấu) trả về gợi ý rác: `_`, `e`, `i`, `o` — vì so
khớp chuỗi con quá thô (`key in k or k in key` khớp cả ký tự đơn). Đã sửa: bỏ dấu để so
khớp, và chỉ gợi ý từ dài ≥ 3 ký tự. Có test canh (`test_tra_tu_khong_co_thi_khong_goi_y_rac`).

### Giá trị cho báo cáo

Chế độ `--sai` là nguyên liệu trực tiếp cho **mục 5.3 (ca điển hình)**. Bốn ca đầu tiên đã
cho thấy rõ giới hạn mù khía cạnh:

```
[visfd-test-00001-PERFORMANCE]  vàng=tích cực  đoán=tiêu cực
[visfd-test-00001-SER&ACC]      vàng=tích cực  đoán=tiêu cực
   ^ CÙNG MỘT CÂU, hai khía cạnh, cùng một dự đoán — vì mô hình mù khía cạnh
```

Và câu `"pin rất trâu nhưng màn hình hơi tối"` minh hoạ hoàn hảo trong một dòng: BATTERY nên
là tích cực, SCREEN nên là tiêu cực, nhưng mô hình chỉ đưa ra **một** dự đoán cho cả hai.

**Test:** +12 (137 toàn repo, xanh).
