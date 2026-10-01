# GAP-020 — Nhận diện vế khía cạnh bằng chỉ số, sai khi câu bị cắt

**Ngày phát hiện:** 01/10/2026 · **Phát hiện bởi:** học viên (chạy seed 42 trên Colab)
**Loại:** code · **Mức độ:** **nghiêm trọng** (chặn hẳn CD1.6a) · **Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

`ASGCNModel` lấy biểu diễn vế khía cạnh trong cặp câu `<s> câu </s></s> pin </s>` làm truy
vấn attention. Bản đầu nhận diện vế đó bằng một phép so chỉ số:

```python
if w is not None and w >= int(n):   # n = n_tokens
    la_khia_canh[b, l] = 1.0
```

Phép so này giả định mọi token của câu đều có mặt trong đầu vào. Nhưng `ACSADataset` cắt
bớt **vế câu** khi quá `max_seq_len` (`truncation="only_first"`), nên với câu dài, vế khía
cạnh mang chỉ số **nhỏ hơn** `n_tokens` thật. Khi đó không vị trí nào thoả điều kiện, mô
hình ném `ValueError` giữa lúc huấn luyện:

```
ValueError: Khong tim thay ve khia canh trong dau vao. `asgcn` doi `data.pair_mode: true`
```

Thông báo lỗi còn chỉ sai hướng: nó đổ cho cấu hình, trong khi cấu hình đúng.

## 2. Vì sao test không bắt được

16 test của `tests/test_asgcn.py` đều chạy trên **tập dev với `max_seq_len=128`**. Câu dài
nhất của dev không đủ dài để bị cắt, nên nhánh code sai không bao giờ được chạy tới.

Đây là mẫu hỏng **khác** với các GAP trước: không phải test kiểm sai thứ, mà là **dữ liệu
test không chạm tới điều kiện biên**. Test xanh chỉ chứng minh "đúng với câu ngắn".

Chi phí thật của lỗ hổng này: học viên chờ tải 540 MB trọng số PhoBERT trên Colab rồi mới
nhận lỗi.

## 3. Nguyên nhân gốc

**Suy ra vị trí từ một con số thay vì đọc cấu trúc có sẵn.** `n_tokens` mô tả *câu gốc*, còn
`word_ids` mô tả *đầu vào thật sau khi tokenize và cắt*. Dùng cái thứ nhất để suy về cái thứ
hai là đặt một giả định ngầm — "không có gì bị cắt" — mà không viết ra ở đâu.

Cấu trúc cần thiết vốn đã có sẵn ngay trong `word_ids`: các ô đặc biệt mang `None`, nên hai
vế tách nhau rõ ràng mà không cần biết `n_tokens`.

## 4. Đã sửa thế nào

Thêm `ASGCNModel._cac_ve()`: tách `word_ids` thành các đoạn liên tiếp không phải ô đặc biệt.
Đoạn đầu là vế câu, đoạn cuối là vế khía cạnh. Cả hai chỗ dùng chung hàm này: bước gộp
subword lấy đoạn đầu, bước dựng truy vấn lấy đoạn cuối.

Cùng một lỗi có hai mặt, và mặt thứ hai cũng đã được sửa theo: với câu bị cắt, phép so chỉ
số cũ cũng **không chặn được** vế khía cạnh lọt vào ô token của câu.

Thêm 2 test, cả hai ép `max_seq_len=16` để mọi câu đều bị cắt:

- `test_cau_bi_cat_van_tim_thay_ve_khia_canh`
- `test_ve_khia_canh_khong_lan_vao_token_khi_cau_bi_cat`

## 5. Bài học

**Test phải chạm điều kiện biên của dữ liệu thật, không chỉ chạy được trên mẫu tiện tay.**
Ở đây biên là "câu dài hơn `max_seq_len`". Cách rẻ để có: trong bộ test của mỗi mô hình, luôn
có ít nhất một ca ép `max_seq_len` nhỏ.

Quy tắc kèm theo cho các step sau: **trước khi gửi một lần chạy dài lên Colab, duyệt thử toàn
bộ tập train bằng encoder tí hon ở máy.** Mất khoảng một phút, bắt được đúng lớp lỗi phụ
thuộc dữ liệu mà test mẫu nhỏ không thấy. Đã làm vậy sau khi sửa lỗi này.

## 6. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — lỗi cài đặt, phát hiện trước khi có bất kỳ số liệu nào, không ảnh hưởng
      kết quả. Giữ trong sổ để rút kinh nghiệm; bài học ở mục 5 dùng cho mọi step còn lại.
