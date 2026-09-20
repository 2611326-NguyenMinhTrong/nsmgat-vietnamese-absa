# GAP-016 — 18 cột của ma trận khảo sát không có định nghĩa ở đâu cả

**Ngày phát hiện:** 20/09/2026 · **Phát hiện bởi:** học viên (hỏi *"bieu_dien_dau_vao nghĩa là gì"*)
**Loại:** tài liệu (kéo theo số liệu)
**Mức độ:** nghiêm trọng nếu để lâu — ảnh hưởng trực tiếp Bảng 3.9 của cuốn báo cáo
**Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

`survey_matrix.csv` có 18 cột. `survey_protocol.md` có 8 mục, **không mục nào định nghĩa
cột nào**. Chỉ hai cột được ghi rõ giá trị hợp lệ, và cả hai là vì `survey_tools.py` cần
chúng để chạy: `trang_thai` và `ho_phuong_phap`.

16 cột còn lại: người điền tự hiểu.

## 2. Phát hiện thế nào

Học viên hỏi một câu rất đơn giản — `bieu_dien_dau_vao` nghĩa là gì. Đi tìm định nghĩa
chính thức để trả lời cho chắc thì không có. Hai dòng duy nhất đã điền cột đó cho thấy hậu
quả có thật:

```
Lexicon-based       → "tu dien cam xuc"
BiLSTM-attention    → "embedding + BiLSTM"
```

Dòng thứ hai **trộn hai trục vào một ô**: `embedding` là biểu diễn đầu vào, `BiLSTM` là kiến
trúc — thứ thuộc cột `ho_phuong_phap`. Hai dòng, hai kiểu viết, một lỗi trục.

Ngay ngày hôm đó học viên tự điền dòng `UIT-ViSFD` và sinh thêm hai lỗi cùng họ, độc lập với
tôi: **tiêu đề bài báo bị gõ vào ô `nam`**, và ô `co_ma_nguon` (đáng lẽ `co`/`khong`) nhận
một đường dẫn GitHub. Không có gì chặn lại cả — đó là bằng chứng mạnh nhất rằng lỗ hổng này
không phải giả định.

## 3. Nguyên nhân gốc

**Lược đồ dữ liệu được dựng bằng code trước, mô tả cho người dùng thì không ai viết.** Cột
nào công cụ *cần* thì được định nghĩa (vì không định nghĩa thì code không chạy); cột nào chỉ
*người* đọc thì bỏ trống — vì thiếu nó không làm gì đỏ cả.

Đây là mẫu "chỉ kiểm thứ máy kiểm được" — cùng họ với GAP-014 (test xanh không có nghĩa là
điều bạn tin đã được chứng minh).

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| 3 dòng đã điền (`Lexicon-based`, `BiLSTM-attention`, `UIT-ViSFD`) | Có — đã chuẩn hoá |
| 19 dòng còn trống | Không — nhờ phát hiện sớm, chúng sẽ được điền theo từ vựng ngay từ đầu |
| Bảng 3.9 trong báo cáo | Chưa in ra bảng nào nên chưa lan tới. Nếu để tới lúc 45 dòng đã điền mới phát hiện thì phải rà tay toàn bộ |

Không có số liệu thí nghiệm nào bị ảnh hưởng.

## 5. Đã sửa thế nào

Ba lớp, cố ý trùng nhau:

1. **`survey_protocol.md` mục 9 "Từ điển cột"** — 18 cột, mỗi cột một câu nghĩa + tập giá trị
   hợp lệ, cộng bảng mã riêng cho `bieu_dien_dau_vao`.
2. **Hai dòng `#MO_TA` / `#VI_DU` ngay trong `survey_matrix.csv`** — mô tả và một dòng điền
   mẫu nằm ngay cạnh chỗ đang gõ, không phải mở tài liệu khác ra tra. Mọi dòng có `ref_key`
   bắt đầu bằng `#` đều bị công cụ bỏ qua.
3. **`survey_tools.py validate` cưỡng chế** — 7 cột có tập giá trị đóng, `bieu_dien_dau_vao`
   phải bắt đầu bằng một mã, và một kiểm tra mâu thuẫn nội tại (`co_dung_do_thi=khong` thì
   `loai_do_thi` phải trống). +5 test.

Lớp 3 là lớp duy nhất không thể quên được — hai lớp kia chỉ có tác dụng nếu người ta đọc.

## 6. Bài học — phòng lần sau bằng cách nào

**Cột nào người phải điền tay thì cột đó phải có: một câu định nghĩa, một tập giá trị hợp lệ,
một ví dụ đúng — và nếu tập giá trị đóng thì phải có code chặn.** Viết lược đồ xong mà chưa
viết ba thứ đó thì lược đồ chưa xong.

Dấu hiệu nhận biết sớm: **ô đầu tiên được điền vào một cột mới**. Nếu lúc đó chưa có định
nghĩa, người điền đang tự đặt ra quy ước — và người tiếp theo sẽ đặt quy ước khác.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — sai sót nội bộ về quy trình, đã sửa trước khi sinh ra bất kỳ bảng nào trong
      cuốn báo cáo. Nhưng *quy trình đã sửa* thì có: mục 9 của `survey_protocol.md` là thứ
      nên mô tả trong phần phương pháp khảo sát (mục 3.1).
