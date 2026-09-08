# PHIẾU BÀN GIAO — [CD1.4b] Baseline BiLSTM + attention theo khía cạnh

**Ngày:** 07–08/09/2026 · **Tuần:** 3 · **Trạng thái:** ✅ Xong — đủ 3 seed

> Vị trí trong thang bậc: `lexicon` → **`bilstm`** → `phobert` → `asgcn` → `asgcn_linked`
> → `senticgcn` → `gpt4o_zeroshot`
>
> Vai trò: **mốc TRƯỚC kỷ nguyên tiền huấn luyện.** Hiệu số `bilstm ↔ phobert` ở CD1.5 sẽ
> trả lời câu *"mô hình ngôn ngữ tiền huấn luyện đáng giá bao nhiêu điểm?"* — một con số
> đứng riêng thì không nói lên điều đó.

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Nội dung |
|---|---|---|
| `src/nsmgat/models/bilstm.py` | Tạo | BiLSTM 2 chiều + attention truy vấn bằng khía cạnh, kiểu ATAE-LSTM |
| `configs/bilstm.yaml` | Tạo | 30 epoch, lr 1e-3, batch 64, dropout 0,3, dừng sớm sau 5 |
| `src/nsmgat/train.py` | Sửa | Đăng ký `bilstm` vào `MODEL_REGISTRY`; ghi log ra file; `--resume`; ghi `predictions.jsonl` |
| `src/nsmgat/trainer.py` | Sửa | Cơ chế **chạy tiếp** (S4.4 kéo lên sớm); ghi `last.pt` mỗi epoch; ghi file an toàn |
| `src/nsmgat/evaluate.py` | Sửa | `thu_tung_mau=True` → thu dự đoán từng mẫu (GAP-011) |
| `src/nsmgat/utils/logging.py` | Sửa | `them_file_log()` — log ra `logs/<exp>/seed<N>.log` |
| `src/nsmgat/utils/io.py` | Sửa | `config_hash()` chuyển về đây để `Trainer` dùng chung |
| `scripts/try_bilstm.py` | Tạo | Công cụ thử tay — xem attention, chạy một câu qua **mọi** khía cạnh |
| `scripts/watch_train.py` | Tạo | Theo dõi **liên tục** quá trình huấn luyện |
| `tests/test_bilstm.py` · `test_watch_train.py` · `test_resume.py` · `test_predictions.py` | Tạo | 14 + 17 + 9 + 6 test |

**183 test xanh** (từ 137 đầu step).

---

## 2. ĐỂ LÀM GÌ

Trả lời **hai câu hỏi cụ thể** mà CD1.4a đặt ra chứ không phải "thêm một baseline cho đủ":

1. **Trần mù khía cạnh 80,88 % có phá được không?** — CD1.4a chứng minh mọi mô hình không
   nhìn khía cạnh đều bị chặn ở đó. Cần một mô hình *có* nhìn khía cạnh để kiểm.
2. **Lớp trung tính có thật sự bất khả không?** — `lexicon` cho F1 = 0,000, tức không một
   Example nào được đoán là trung tính. Đó là giới hạn của từ điển hay của bài toán?

---

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1. Hai chỗ nhìn thấy khía cạnh, không phải một

```
input_ids (subword PhoBERT)
    → Embedding (khởi tạo NGẪU NHIÊN, học từ đầu — không tiền huấn luyện)
    → nối vector khía cạnh vào TỪNG token        ← chỗ nhìn thứ nhất
    → BiLSTM
    → attention với TRUY VẤN là vector khía cạnh ← chỗ nhìn thứ hai
    → Linear → 3 lớp
```

Vì sao phải **hai** chỗ? Nếu chỉ nối khía cạnh vào lúc gộp cuối, BiLSTM đã mã hoá xong cả
câu mà không biết đang xét khía cạnh nào — nó buộc phải nén mọi khía cạnh vào một biểu diễn
duy nhất rồi mới lọc. Nối từ đầu thì **chính quá trình đọc câu đã bị khía cạnh chi phối**.
Đó là ý tưởng của ATAE-LSTM (Wang et al. 2016).

Có test canh: `test_doi_khia_canh_thi_dau_ra_DOI` — đổi khía cạnh mà đầu ra không đổi thì đỏ.

### 3.2. Bảng nhúng gọn — đo được, không đoán

Từ vựng PhoBERT có 64.000 ô, nhưng **chỉ 9.134 (14,3 %)** thực sự xuất hiện trong tập train.
Cấp phát cả 64.000 thì 85,7 % bảng nhúng **không bao giờ được huấn luyện** — vừa phí tham số,
vừa nguy hiểm: lúc suy luận gặp subword lạ sẽ lấy ra một vector **ngẫu nhiên chưa hề học**.

Nên dùng bảng nhúng gọn 9.136 ô (9.134 + PAD + UNK), với `id_map` là bảng tra `register_buffer`.

| | Nếu dùng cả từ vựng | Thực tế |
|---|---|---|
| Tham số | ~20,5 triệu | **4,02 triệu** |
| Tiết kiệm | — | **~80 %** |

Chỉ số xây **chỉ từ tập TRAIN**. Đọc dev/test để xây từ vựng là rò rỉ dữ liệu — có test canh
(`test_tu_vung_chi_xay_tu_TRAIN`).

### 3.3. Vì sao subword PhoBERT chứ không phải từ mức word + GloVe

ATAE-LSTM gốc dùng từ mức word. Ta chọn khác, có ba lý do:

1. **So sánh sạch hơn với `phobert`.** Dùng chung bộ tách từ ⇒ hiệu số `bilstm ↔ phobert`
   chỉ còn là *(trọng số tiền huấn luyện + kiến trúc)*, bớt một biến gây nhiễu.
2. **Chịu được từ lạ.** UIT-ViSFD là bình luận mạng xã hội, đầy lỗi chính tả và teencode.
   Từ lạ ở mức word → UNK hoàn toàn; ở mức subword → vẫn tách được thành mảnh đã thấy.
3. Dùng lại `input_ids` sẵn có trong batch, không phải đọc lại jsonl như `LexiconModel`.

> ⚠️ **Cái giá:** mô hình này **không phải ATAE-LSTM**. Trong báo cáo phải gọi đúng tên
> `bilstm` và ghi rõ nó khác bản gốc ở đâu — xem [SoSanh_KetQua_voi_So_Cong_Bo.md](../user-require/SoSanh_KetQua_voi_So_Cong_Bo.md) rào cản 3.

---

## 4. KẾT QUẢ — 3 seed

| seed | accuracy | macro-F1 | F1 tiêu cực | F1 trung tính | F1 tích cực | phút | epoch |
|---|---|---|---|---|---|---|---|
| 42 | 0,8582 | 0,7847 | 0,8637 | 0,5797 | 0,9107 | 56,5 | 17 |
| 1337 | 0,8637 | 0,7942 | 0,8693 | 0,5992 | 0,9141 | 52,1 | — |
| 2024 | 0,8706 | 0,8058 | 0,8767 | 0,6231 | 0,9177 | 51,2 | 12 |
| **TB ± σ** | **0,8642 ± 0,0062** | **0,7949 ± 0,0106** | | **0,6007 ± 0,0217** | | 53,3 | |

Độ lệch chuẩn nhỏ (0,62 điểm accuracy) — mô hình **ổn định giữa các seed**, kết luận rút ra
từ đây đáng tin.

### ✅ Phát hiện 1 — trần mù khía cạnh ĐÃ BỊ PHÁ

| | accuracy test | So với trần 80,88 % |
|---|---|---|
| `lexicon` | 0,7471 | dưới trần 6,2 điểm |
| **`bilstm`** | **0,8642** | **vượt trần 5,5 điểm** |

Đây là **bằng chứng số học**, không phải suy đoán từ kiến trúc: một mô hình không nhìn khía
cạnh **không thể** vượt 80,88 %, vì nó buộc phải trả cùng một đáp án cho mọi khía cạnh của
cùng một câu, mà 45,1 % câu trong test có khía cạnh trái nhãn.

Xem trực tiếp bằng `python scripts/try_bilstm.py --doi-khia-canh "pin trâu nhưng màn_hình rất tối"`:
`BATTERY` → tích cực (0,979), `SCREEN` → tiêu cực (1,000). Attention dời từ *trâu* sang *tối*.

### 🟡 Phát hiện 2 — trung tính KHÔNG bất khả, nhưng vẫn là điểm yếu nhất

| | `lexicon` | `bilstm` |
|---|---|---|
| F1 trung tính | **0,0000** | **0,6007** |
| F1 tiêu cực | 0,7545 | 0,8699 |
| F1 tích cực | 0,8180 | 0,9142 |

Kết luận đúng là **"trung tính khó, không phải trung tính bất khả"**. Nhưng khoảng cách vẫn
lớn: 0,60 so với 0,87 và 0,91. Và độ lệch chuẩn của riêng lớp này (0,0217) **gấp 3,5 lần**
độ lệch chuẩn của accuracy — tức đây cũng là lớp *kém ổn định* nhất.

Trung tính chỉ chiếm **12,2 %** tập test. Đây là nguyên liệu trực tiếp cho lập luận của
Chuyên đề 2.

### ⚠️ Quan sát 3 — mô hình đoán chắc nịch cho khía cạnh KHÔNG được nhắc tới

Câu *"pin trâu nhưng màn_hình rất tối"* không nói gì về `CAMERA`, `PRICE`, `STORAGE`, nhưng
mô hình vẫn đoán **tiêu cực** với độ tin 0,98–0,99 cho cả ba.

Có thể nó học "khía cạnh không được nhắc thì đoán theo sắc thái trội của câu" thay vì "không
đủ căn cứ". **Chưa kết luận** — mới quan sát trên vài câu gõ tay, chưa đo trên tập test.
Nếu đúng thì đây là hạn chế đáng ghi mục 6.2. Đo được ở CD1.9 nhờ `predictions.jsonl`.

---

## 5. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã loại phương án nào | Vì sao |
|---|---|---|
| Bảng nhúng **gọn** 9.136 ô | Cả từ vựng 64.000 | 85,7 % tham số sẽ không bao giờ được huấn luyện |
| Subword PhoBERT | Từ mức word + GloVe (như bản gốc) | Bớt một biến nhiễu khi so với `phobert`; chịu được teencode |
| **Không** ghi đè `explain()` | Trả về trọng số attention ngay | Hợp đồng `BaseModel` cho phép trả `[]`; chưa có ai tiêu thụ ⇒ chưa biết CD1.9 cần định dạng gì |
| Tách `ma_hoa()` + `_chu_y()` | Chép công thức attention sang script | Chép lại là cách công cụ và mô hình lệch nhau — có test canh hai đường cho kết quả y hệt |
| lr 1e-3 (không phải 2e-5) | Dùng lr của base.yaml | Học từ đầu, không phải tinh chỉnh PLM — chênh hai bậc độ lớn |
| dropout 0,3 (không phải 0,1) | Dùng của base.yaml | Học từ đầu trên 23,8k mẫu rất dễ quá khớp |

**Một quan sát về `early_stop_patience`:** seed 42 đạt best ở **epoch 12**, *sau khi* đã 5
epoch liền không cải thiện (kiên nhẫn xuống 0/5 ở epoch 11 rồi được nạp lại nhờ epoch 7 nhỉnh
hơn epoch 6 ở chữ số thứ 5). Nếu đặt `patience = 4` thì đã bỏ lỡ. Giữ 5.

---

## 6. KIỂM CHỨNG

| Cách | Kết quả |
|---|---|
| 183 test tự động | ✅ xanh |
| Chạy 3 seed độc lập | ✅ σ = 0,0062 accuracy |
| Thử tay `try_bilstm.py --doi-khia-canh` | ✅ đổi khía cạnh → đổi dự đoán và đổi attention |
| So với trần lý thuyết 80,88 % | ✅ vượt 5,5 điểm |
| `predictions.jsonl` khớp `accuracy` gộp | ✅ có test canh |
| Chạy tiếp (`--resume`) cho kết quả y hệt chạy liền mạch | ✅ có test canh, so từng bit |

---

## 7. DỪNG LẠI VÀ HỎI

### Việc còn tồn của step này

- [ ] **Xoá `last.pt`?** `checkpoints/bilstm/seed2024/last.pt` (46 MB) đã hết tác dụng —
      seed 42 và 1337 không có (chạy trước khi có tính năng). Lệnh:
      `Remove-Item checkpoints\bilstm\seed2024\last.pt`
- [ ] **`lexicon` mới có 1 seed.** Nó gần như tất định nên 3 seed có thể cho σ = 0 giả tạo,
      giống hệt lập luận GAP-003 về LLM. Cần quyết: chạy 3 seed cho đủ hình thức, hay ghi
      rõ "1 seed vì tất định"?

### Sai sót ghi trong step này

| | Nội dung | Trạng thái |
|---|---|---|
| [GAP-011](../gaps/GAP-011_khong-ai-ghi-predictions-jsonl.md) | Không có code nào ghi `predictions.jsonl` | ✅ Đã sửa trong step này |
| [GAP-012](../gaps/GAP-012_tieu-chi-hoan-thanh-con-dem-4-thi-nghiem.md) | Tiêu chí hoàn thành còn đếm "4 thí nghiệm" | ✅ Đã sửa |
| [GAP-013](../gaps/GAP-013_tran-mu-khia-canh-do-tren-train-dung-cho-test.md) | Trần 80,2 % đo trên train, dùng cho test | ✅ Đã sửa → 80,88 % |
| [GAP-014](../gaps/GAP-014_them-dong-vao-base-yaml-lam-doi-van-tay-cau-hinh.md) | Thêm 3 dòng sổ sách vào `base.yaml` làm đổi `config_hash` của mọi kết quả cũ | ✅ Đã sửa |

### Yêu cầu học viên phát sinh trong step này

| | Nội dung |
|---|---|
| Công cụ thử tay `bilstm` | → `scripts/try_bilstm.py` |
| Theo dõi liên tục quá trình train | → `scripts/watch_train.py` + log ra file |
| Chạy tiếp khi bị ngắt | → `--resume` (S4.4 kéo lên sớm) |
| Nhắc xoá file thừa, **không tự xoá** | → mục "Có thể dọn" trong tóm tắt của `watch_train.py` |
| [REQ-008](../user-require/REQ-008_so-sanh-voi-so-cong-bo.md) | Tài liệu "so được với bài báo đến đâu" |

### Step kế tiếp

**CD1.5 `phobert`** (Tuần 4). Không phụ thuộc GAP-007. Hai việc **của học viên** nên xong
trước khi chạy — cần dải tham chiếu để biết kết quả có bất thường không:

1. Đọc bài báo gốc UIT-ViSFD: bài toán là *phát hiện cặp* hay *cho sẵn khía cạnh*?
2. Điền `tap_du_lieu` / `do_do_bao_cao` / `ket_qua_tot_nhat` cho ≥ 5 bài chính

Và một việc thiết kế phải giải **trước CD1.6a**: ASGCN gốc làm aspect-term nên khía cạnh có
điểm neo trong câu; UIT-ViSFD là aspect-category, khía cạnh **không xuất hiện trong câu**.
Neo vào đâu?
