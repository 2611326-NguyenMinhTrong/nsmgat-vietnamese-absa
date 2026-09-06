# GAP-008 — `train_time_sec` bị nhiễm chi phí tokenize mà mô hình không dùng

**Ngày phát hiện:** 06/09/2026 · **Phát hiện bởi:** Claude Code (khi chạy CD1.4a)
**Loại:** số liệu · **Mức độ:** nhẹ (chưa ảnh hưởng kết luận, nhưng **sẽ** ở CD1.10)
**Trạng thái:** 🔴 Mở — xử lý ở CD1.10

---

## 1. Phát hiện gì

Baseline `lexicon` có **9 tham số** nhưng `train_time_sec = 197,8`. Vô lý.

Đo ra nguyên nhân: `ACSADataset.__getitem__` gọi tokenizer PhoBERT **mỗi lần truy cập, mỗi
epoch** — không có bộ nhớ đệm.

```
Tokenize 2.000 item : 0,97 s
=> một epoch train  : ~12 s   (23.872 Example)
=> 11 epoch         : ~127 s
   (đo được train_time_sec = 197,8 s, phần còn lại là đánh giá dev mỗi epoch)
```

Tức **khoảng 2/3 thời gian "huấn luyện"** của `lexicon` là tokenize PhoBERT — thứ
`LexiconModel` **không hề dùng** (nó chỉ đọc `uid` rồi tra từ điển).

## 2. Vì sao sẽ thành vấn đề ở CD1.10

CD1.10 phải dựng **bảng chi phí tính toán** (mục 4.5 của báo cáo): số tham số / thời gian
huấn luyện / thời gian suy luận / VRAM. Nếu lấy thẳng `train_time_sec`:

| Mô hình | `train_time_sec` | Diễn giải sai | Diễn giải đúng |
|---|---|---|---|
| `lexicon` | ~198 s | "Mô hình từ điển tốn 3 phút huấn luyện" | Thực chất ~70 s, còn lại là tokenize không dùng đến |
| `phobert` | *(chưa chạy)* | | Tokenize là chi phí **thật** vì nó dùng `input_ids` |

Với `phobert`/`asgcn`/`senticgcn`, tokenize là chi phí **chính đáng**. Với `lexicon` thì
không. So sánh trực tiếp sẽ **thổi phồng chi phí của baseline rẻ nhất** — đúng chiều làm nó
trông kém hấp dẫn hơn thực tế.

## 3. Nguyên nhân gốc

`ACSADataset` được thiết kế ở S0.4 cho các mô hình **dựa trên PLM**, nơi tokenize là bắt buộc.
Khi CĐ1 thêm baseline **không dùng PLM** (`lexicon`, và sắp tới `bilstm`), giả định đó không
còn đúng, nhưng đường ống dữ liệu vẫn bắt mọi mô hình trả cùng một khoản phí.

Một biến thể của mẫu hỏng quen thuộc: **hạ tầng dùng chung mang theo một giả định ngầm**
(ở đây: "mọi mô hình đều cần input_ids") mà giả định đó không được viết ra.

## 4. Đã thử gì

Ban đầu tôi chẩn đoán sai — tưởng nút thắt là việc tính lại đặc trưng từ điển mỗi batch, nên
thêm bộ nhớ đệm vào `LexiconModel`. **Không ăn thua**: 197,8 s so với 189,6 s trước khi cache.
Đo lại mới ra nguyên nhân thật.

Giữ cache vì nó đúng về mặt khái niệm và vô hại, nhưng đã sửa chú thích trong code cho khớp
sự thật thay vì để nguyên lời giải thích sai.

## 5. Ba phương án cho CD1.10 — chưa chọn

| | Phương án | Được | Mất |
|---|---|---|---|
| **A** | Báo cáo `train_time_sec` như đang có, **kèm chú thích** phần tokenize | Không đụng hạ tầng dùng chung | Con số vẫn gây hiểu nhầm nếu đọc lướt bảng |
| **B** | Thêm bộ nhớ đệm tokenize vào `ACSADataset` | Mọi mô hình nhanh lên; con số sạch | Sửa hạ tầng **dùng chung**, cần chạy lại mọi thí nghiệm đã có để số liệu nhất quán |
| **C** | Đo và báo cáo **riêng** phần tokenize như một cột phụ | Trung thực và tách bạch nhất | Thêm việc đo, bảng rộng thêm một cột |

Nghiêng về **A hoặc C** — B đụng vào hạ tầng dùng chung và bắt chạy lại thí nghiệm, không
xứng với lợi ích ở quy mô này.

⚠️ **Nếu chọn B thì phải làm TRƯỚC khi chạy các baseline khác**, không được làm giữa chừng —
nếu không, `train_time_sec` của các mô hình sẽ đo bằng hai thước khác nhau.

## 6. Bài học

**Một con số vô lý phải được truy đến cùng, đừng vá theo linh cảm.** Tôi đã thêm cache dựa
trên phỏng đoán mà không đo trước; đo xong mới thấy đoán sai. Mất 15 phút vô ích, và suýt để
lại một chú thích sai trong code khẳng định cache đã sửa được vấn đề.

Quy trình đúng: **đo trước, sửa sau** — kể cả khi nguyên nhân "có vẻ hiển nhiên".

## 7. Có cần đưa vào báo cáo không

- [x] **Có** — mục 4.5 (chi phí tính toán) phải nói rõ `train_time_sec` được đo thế nào và
      có bao gồm tiền xử lý hay không. Nếu không, bảng chi phí không diễn giải được.
