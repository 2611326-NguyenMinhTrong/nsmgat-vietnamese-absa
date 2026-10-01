# PHIẾU BÀN GIAO — [CD1.6a] ASGCNModel và hai file config

> Phần 2 của CD1.6a. Phần hạ tầng (GCNLayer, ma trận kề) ở
> [CD1.6a_gcn-layer.md](CD1.6a_gcn-layer.md). Sau phiếu này còn việc chạy 3 seed trên Colab.

**Ngày:** 02/10/2026 · **Step:** CD1.6a (phần 2/2) · **Ánh xạ plan gốc:** S1.2 · **Thời gian thực tế:** ~2 giờ

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `src/nsmgat/models/asgcn.py` | Tạo | `ASGCNModel`: PhoBERT (cặp câu) → gộp subword về token → 2 lớp GCN trên cây phụ thuộc → attention với truy vấn là biểu diễn vế khía cạnh → Linear 3 lớp |
| `src/nsmgat/models/layers.py` | Sửa | Thêm chế độ `normalize="row_plus1"`, tức chia cho (d_i + 1) theo công thức (3) của bài gốc |
| `src/nsmgat/graphs/adjacency.py` | Sửa | Gom cạnh trong dict Python rồi ghi tensor một lần: 10,46 giây xuống 0,84 giây cho 1.093 câu |
| `configs/asgcn.yaml` | Tạo | Cấu hình bản gốc, `link_roots: false` |
| `configs/asgcn_linked.yaml` | Tạo | Biến thể GAP-007, **kế thừa** asgcn.yaml và ghi đè đúng một khoá |
| `src/nsmgat/train.py` | Sửa | Thêm một dòng vào `MODEL_REGISTRY` |
| `tests/test_asgcn.py` | Tạo | 14 test |
| `tests/test_layers.py` | Sửa | Thêm 3 test cho `row_plus1` |
| `SO_TAY_LENH.md` | Sửa | Hai lệnh chạy, kèm cảnh báo phải đặt `--exp-name` cho biến thể |

Lệnh đã chạy:

```bash
.venv/Scripts/python.exe -m pytest tests/ -q
```

---

## 2. ĐỂ LÀM GÌ

- **Vấn đề:** ba mô hình đã chạy đều không dùng cấu trúc câu. `phobert` đọc câu như một chuỗi
  phẳng, nên không có cách nào trả lời "cú pháp có giúp gì không".
- **Sau step này:** có mô hình thêm đúng một thứ so với `phobert`, là đồ thị phụ thuộc. Hiệu số
  giữa hai mô hình đo trực tiếp giá trị của cú pháp.
- **Nếu bỏ:** mất cả hai cặp so sánh quan trọng nhất. `asgcn` với `senticgcn` cô lập phần tri
  thức cảm xúc, `senticgcn` với NS-MGAT cô lập đóng góp của Chuyên đề 2. Không có `asgcn` thì
  mọi điểm hơn của Chuyên đề 2 đều có thể bị hỏi lại "do cú pháp hay do đóng góp của em".

---

## 3. CƠ CHẾ HOẠT ĐỘNG

Đi qua câu "pin rất trâu" với khía cạnh `BATTERY`.

**Bước 1, mã hoá.** PhoBERT đọc câu, cho ra một vector cho mỗi subword. Câu này tách thành
3 token tiếng Việt nhưng có thể thành nhiều subword hơn, ví dụ "trâu" không có trong từ vựng
thì thành hai mảnh.

**Bước 2, gộp subword về token.** Lấy trung bình các subword của cùng một token, dùng `word_ids`
mà dataset đã trả. Phải làm bước này vì cây phụ thuộc đánh chỉ số theo token, không theo subword.
Token nào bị cắt mất do câu dài hơn 128 subword thì mask bằng 0.

**Bước 3, hai lớp GCN.** Ma trận kề lấy từ chỉ số đã dựng sẵn:

```
adj = [[1, 0, 1],      bậc = [2, 2, 3]   → mẫu số (d_i + 1) = 3, 3, 4
       [0, 1, 1],
       [1, 1, 1]]
```

Sau lớp một, biểu diễn của "pin" đã trộn thông tin của "trâu". Sau lớp hai, nó thấy được cả
"rất" dù hai từ này không nối trực tiếp, vì cùng nối qua "trâu". Đó chính là thứ mô hình chuỗi
phẳng không có.

**Bước 4, attention.** Tra embedding của `BATTERY`, nhân vô hướng với đầu ra GCN của từng token,
chia cho căn của số chiều rồi softmax. Token nào liên quan khía cạnh thì trọng số cao.

**Bước 5, gộp và phân loại.** Tổng có trọng số, nhưng **gộp biểu diễn của bộ mã hoá chứ không
gộp đầu ra GCN**, đúng công thức (10) của bài gốc. GCN sinh ra trọng số, không sinh ra biểu diễn
cuối. Đây là chỗ dễ cài sai nhất, và cũng là câu trọng yếu số 1 của đề 03.

**Chỗ dễ hiểu sai thứ hai:** `pair_mode` phải TẮT. Bật lên thì vế khía cạnh cũng sinh `word_ids`
và trộn vào chỉ số token của câu, trong khi chỉ số đó phải khớp với cây phụ thuộc. Mô hình vẫn
chạy, chỉ sai âm thầm. Có test chốt.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Bộ mã hoá | PhoBERT y nguyên như `phobert` | BiLSTM + GloVe như bài gốc | Đổi hai thứ một lúc thì hiệu số `phobert` với `asgcn` không còn đo được gì |
| Trọng số theo vị trí (công thức 5) | **Bỏ** | Giữ, lấy vị trí của từ khoá dịch từ mã khía cạnh | Cần chỉ số đầu và độ dài cụm khía cạnh; `BATTERY` không xuất hiện trong câu. Dịch sang tiếng Việt cũng không bảo đảm từ đó có trong câu |
| Masking theo khía cạnh (công thức 7) | **Bỏ** | Giữ | Ép về 0 mọi token không thuộc khía cạnh, mà không token nào thuộc, nên cả câu về 0 |
| Thay cho hai cơ chế trên | Attention với truy vấn là **biểu diễn vế khía cạnh của cặp câu** | (a) embedding khía cạnh học từ đầu; (b) trung bình toàn câu | (b) mù khía cạnh, đúng bệnh của `lexicon` bị trần 80,88 % chặn. (a) đã viết xong rồi bỏ ngày 02/10/2026: nó làm **bộ mã hoá** mù khía cạnh, cùng một câu thì mọi khía cạnh dùng chung biểu diễn, thấp hơn cả `bilstm`; hiệu số `phobert` ↔ `asgcn` sẽ lẫn hai biến |
| `pair_mode` | **Bật**, giống `phobert` | Tắt | Tắt thì khía cạnh chỉ vào bằng embedding, quay về phương án (a) ở trên. Tắt mà vẫn chạy thì mô hình ném lỗi, không chạy bằng vector rác |
| Giới hạn khi gộp subword | `n_tokens` của **từng mẫu** | Độ dài lớn nhất trong batch | Chặn theo batch thì vế khía cạnh lọt vào ô token của câu ngắn: đo được câu 22 token thành 25 token có mask |
| Vector cuối gộp từ đâu | Biểu diễn bộ mã hoá | Đầu ra GCN | Bài gốc gộp trạng thái ẩn LSTM (công thức 10); giữ đúng tinh thần GCN chỉ sinh trọng số |
| Chuẩn hoá | `row_plus1`, chia (d_i + 1) | `row` chia d_i, hoặc `sym` | Công thức (3) của bài gốc; học viên chốt 02/10/2026 |
| Bảng khía cạnh | Lấy từ `ASPECT_VI` | Đếm từ tập train như `bilstm` | Đây là bảng mã cố định của bộ dữ liệu, không phải từ vựng học được. Lấy từ bảng thì tất định và không phụ thuộc file nào còn trên đĩa |
| Khía cạnh lạ | Ném lỗi | Dùng chỉ số 0 như `bilstm` | Mã lạ mà im lặng dùng chỉ số 0 là sai số liệu không ai thấy |
| Đồ thị lấy từ đâu | Chỉ mục uid → cạnh, dựng trong `__init__` | Viết vào `collate_fn` | `collate_fn` để rỗng có chủ ý cho S3.3, chưa tới lượt (quy tắc 6) |
| Lưu đồ thị kiểu gì | Cặp chỉ số, gộp theo CÂU | Ma trận dày cho mỗi Example | 7.671 câu × 128 × 128 × 4 byte ≈ 500 MB. Gộp theo câu vì đồ thị không phụ thuộc khía cạnh |
| Hai file config | `asgcn_linked.yaml` kế thừa `asgcn.yaml` | Chép nội dung rồi sửa tay | Hiệu số GAP-007 chỉ có nghĩa khi mọi siêu tham số khác giống hệt. Kế thừa thì không có cách nào lệch |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Step kế tiếp: **chạy 3 seed `asgcn` và 3 seed `asgcn_linked` trên Colab**, rồi CD1.6b `senticgcn`.
- `senticgcn` dùng lại gần như toàn bộ: `GCNLayer`, `edges_to_adj` (đổi `weight="conf"` để mang
  điểm cảm xúc), bước gộp subword, bước attention. Khác đúng phần trọng số cạnh.
- Lưu ý khi chạy: biến thể phải có `--exp-name asgcn_linked`, nếu không kết quả ghi đè lên
  `results/asgcn/`.

---

## 6. KIỂM CHỨNG

```
306 passed in 179.20s (0:02:59)
```

Trước step này 292 test, nay 306, tức thêm đúng 14 test của `tests/test_asgcn.py`. Ba test
`row_plus1` trong `tests/test_layers.py` đã nằm trong số 292 vì được thêm trước đó cùng ngày.

Test đáng giá nhất là `test_asgcn_linked_khac_asgcn_DUNG_MOT_khoa`: nó so sâu hai config sau khi
đã giải `extends`, và đòi tập khác biệt đúng bằng `{"model.link_roots": (False, True)}`.

**Chưa chạy huấn luyện thật.** Mọi số liệu về chất lượng mô hình còn trống, không có con số nào
trong phiếu này là kết quả thực nghiệm.

**Lượt chạy đầu trên Colab (01/10/2026) sập**, xem [GAP-020](../gaps/GAP-020_nhan-dien-ve-khia-canh-bang-chi-so-sai-khi-cau-bi-cat.md):
vế khía cạnh được nhận diện bằng `word_id >= n_tokens`, mà câu dài bị cắt bớt vế câu nên phép
so đó sai. Đã sửa thành tách hai vế theo cấu trúc `word_ids` và thêm 2 test ép `max_seq_len=16`.
Rút ra một quy tắc cho các step sau: trước khi gửi lần chạy dài lên Colab, duyệt thử toàn bộ
tập train bằng encoder tí hon ở máy, mất khoảng một phút.

**Sự cố gặp phải:** file test chạy 147 giây ở lần đầu. Đo ra thủ phạm là `edges_to_adj`: mỗi cạnh
làm một phép so sánh trên tensor, khoảng 50 micro giây một lần, thành 10 ms mỗi câu. Với
train cộng dev cộng test thì mỗi lần khởi tạo mô hình mất khoảng 73 giây. Đã sửa bằng cách gom
trong dict Python rồi ghi tensor một lần: còn 0,84 giây cho 1.093 câu, nhanh hơn 12 lần.

---

## 7. DỪNG LẠI VÀ HỎI

**Câu hỏi mở gửi học viên:**

1. ~~Ba chỗ lệch có cần báo GVHD trước khi chạy không?~~ **Học viên chốt 02/10/2026: chưa báo,
   báo khi có kết quả.** Phải nói rõ ở mục 4.3 của báo cáo. Giờ còn hai chỗ lệch, không phải ba.
2. ~~Chạy cùng lúc hay tuần tự?~~ **Chốt: `asgcn` đủ 3 seed trước, xong mới tới biến thể.**
3. ~~`phobert` và `asgcn` nhận khía cạnh theo hai đường khác nhau, có sửa không?~~ **Chốt: sửa,
   theo phương án gần bài gốc nhất** — bật `pair_mode` và lấy biểu diễn vế khía cạnh làm truy vấn.

**Những chỗ có thể bạn muốn hỏi thêm:**

- Vì sao gộp subword bằng trung bình mà không lấy subword đầu?
- Hai lớp GCN có bị quá ít với câu dài không?
- Nếu `asgcn` thua `phobert` thì kết luận là gì?

**Kết:**
> Bạn có câu hỏi phụ nào về phần này không, hay tôi đi tiếp sang việc chạy 3 seed trên Colab?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
