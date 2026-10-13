# CD1.6c — Sentic-GCN với từ điển có sẵn: dựng bảng điểm và kiểm trước khi huấn luyện

Ngày 13/10/2026. Học viên đồng ý chạy thêm Sentic-GCN với một từ điển cảm xúc có sẵn. Phiếu này ghi
phần chuẩn bị và lý do **chưa giao học viên chạy trên Colab**.

## 1. ĐÃ LÀM GÌ

- `scripts/build_lexicon_external.py` với ba lệnh: `senticnet` và `vswn` đổi hai từ điển có sẵn sang
  bảng điểm mà `senticgcn` đọc được; `kiem` đo độ phủ và mẫu số chuẩn hoá của một bảng điểm bằng
  chính lớp mô hình.
- Đã dựng hai bảng điểm, nằm ở `data/processed/` (chỉ trên máy, đã thêm vào `.gitignore`):
  `lexicon_senticnet_vi.json` có 3.327 mục, `lexicon_vswn.json` có 1.192 mục.
- Hai file nguồn được giữ ở `data/cache/tu_dien_ngoai/` (chỉ trên máy) để dựng lại được.
- Đã chạy `kiem` trên cả hai. **Cả hai đều làm lần huấn luyện dừng giữa chừng.**
- Trong lúc kiểm công cụ, phát hiện một con số sai ở mục 4.3 của báo cáo (GAP-033), đã sửa.

Chưa làm, vì chờ quyết định ở mục 7: file cấu hình của hai biến thể, dòng đăng ký trong notebook Colab.

## 2. VÌ SAO LÀM VẬY

- Bảng điểm SenticNet được dựng bằng cách đi qua từ vựng của dữ liệu, bỏ dấu, rồi tra. Bản tiếng Việt
  viết không dấu (`tot`, `dep`), còn mô hình tra đúng mặt chữ có dấu. Làm ở bước dựng bảng thì không
  phải sửa mã mô hình, và biến thể chỉ khác bậc 5 ở đúng một khoá `lexicon_path`.
- Bảng điểm không lên GitHub: SenticNet chỉ cho dùng phi thương mại, kho VietSentiWordNet không ghi
  giấy phép.
- Kiểm trước khi chạy: một lần chạy Sentic-GCN tốn 70 đến 79 phút GPU. `GCNLayer` có dây bẫy dừng
  huấn luyện khi mẫu số chuẩn hoá bằng 0. Bậc 5 chưa bao giờ chạm dây bẫy; bảng điểm mới thì chưa biết.

## 3. ĐỌC KẾT QUẢ THẾ NÀO

Công thức (7) của bài chia mỗi hàng của ma trận kề cho (E_i + 1), với E_i là tổng có dấu của trọng số
trên hàng. Ba mức cần phân biệt:

- mẫu số ≤ 0: cả hàng đổi dấu. Bài gốc không bàn, chuyên đề đã chọn giữ nguyên (quyết định 03/10).
- |mẫu số| < 0,001: hàng bị khuếch đại hơn 1000 lần.
- mẫu số bằng 0: phép chia không xác định; mã dừng với thông báo lỗi.

## 4. KẾT QUẢ

Tập huấn luyện, 23.872 mẫu, đếm theo mẫu:

| | Từ điển tự suy (bậc 5 đã chạy) | VietSentiWordNet | SenticNet tiếng Việt |
|---|---|---|---|
| Độ phủ số lượt từ | 83,31 % | 8,66 % | 52,39 % |
| Từ có mẫu số ≤ 0 | 735 (0,079 %) | 64 (0,007 %) | 39.570 (4,239 %) |
| Mẫu có ít nhất một từ như vậy | 596 (2,50 %) | 60 (0,25 %) | 14.626 (61,27 %) |
| Từ có \|mẫu số\| < 0,001 | 0 | 31 | 136 |
| Từ có mẫu số bằng 0 (kích dây bẫy) | 0 | 31, thuộc 31 mẫu | 110, thuộc 110 mẫu |
| Ô khác 0 mang trọng số âm | 1,68 % | 0,45 % | 12,25 % |

Tập phát triển và kiểm tra cho hình ảnh tương tự (SenticNet: 22 và 23 mẫu kích dây bẫy; VietSentiWordNet: 4 và 15).

Hai điều đọc ra:

1. Với công thức của bài, **cả hai từ điển có sẵn đều không huấn luyện được**: lần chạy sẽ dừng ở
   lô đầu tiên chứa một trong các mẫu trên.
2. Hai từ điển hỏng theo hai cách khác nhau. VietSentiWordNet chỉ hỏng ở 8 câu của tập huấn luyện,
   tại hai từ `cực` và `chậm` (cùng có điểm -0,75). Ngoài chỗ đó nó hiền hơn bậc 5.
   SenticNet tiếng Việt thì hỏng rộng: 61 % số mẫu có ít nhất một hàng đổi dấu. Từ kích dây bẫy
   nhiều nhất là `ngày` (33 câu), nhận điểm -0,898 của khái niệm không dấu `ngay`.

## 5. GIỚI HẠN

- Điểm của mục từ VietSentiWordNet là trung bình trên các tập đồng nghĩa, không phân biệt từ loại. Đây
  là lựa chọn của chuyên đề, bài gốc của từ điển không quy định.
- Bảng SenticNet chứa nhiễu trùng mặt chữ có hệ thống (`máy` nhận điểm của `may`, -0,951).
- Phép kiểm tính trên cả câu, không cắt ở 128 subword như lúc huấn luyện. Số mẫu kích dây bẫy lúc
  chạy thật có thể ít hơn một chút, không thể nhiều hơn.
- Chưa có lần huấn luyện nào với hai bảng điểm này. Mọi nhận định về kết quả là chưa có.

## 6. KIỂM CHỨNG

```
445 passed   (cả bộ; tests/test_build_lexicon_external.py có 5 test)
doi_chieu_chuong4.py --do-cat --do-mau-so: 157 chỗ, 157 khớp
```

- Phép đếm của `kiem` trên bảng điểm cũ khớp ba con số đã ghi ngày 03/10: số từ có mẫu số ≤ 0
  (735, 86, 251), mức nhỏ nhất (1,1e-3; 7,0e-3; 1,1e-3), và không từ nào dưới 0,001.
- Độ phủ in ra khớp số đã đo bằng `do_phu_tu_dien.py`: 52,39 % và 8,66 % trên tập huấn luyện.
- Có test dựng một câu hai từ mà mẫu số bằng đúng 0 và kiểm rằng `kiem` trả mã 1.
- sha256 của hai bảng điểm: `59786f51…5b101e` (SenticNet), `e5f63726…2e213` (VietSentiWordNet); bản
  đầy đủ ở hai file `.meta.json` cạnh bảng điểm.
- **Chưa kiểm:** chưa thử lần huấn luyện nào, kể cả vài bước trên CPU.

## 7. VIỆC CỦA BẠN

Một quyết định, chưa có việc chạy nào. Ba lựa chọn:

1. **Không chạy.** Báo cáo ghi phát hiện ở mục 4: công thức chuẩn hoá của bài chia cho 0 với cả hai
   từ điển có sẵn. Không tốn giờ GPU.
2. **Thêm một quy tắc cho đúng trường hợp mẫu số bằng 0** (hàng đó để nguyên, không chia), rồi chạy.
   Bậc 5 không đổi một chữ số nào vì không hàng nào của nó bằng 0. VietSentiWordNet khi đó chạy được
   và ổn hơn cả bậc 5. SenticNet tiếng Việt vẫn có 61 % số mẫu đổi dấu và 26 từ bị khuếch đại hơn
   1000 lần, có thể không hội tụ. Mỗi từ điển khoảng 4 giờ GPU.
3. **Đổi sang cách tính trọng số luôn dương** như mã nguồn của tác giả (điểm của một đầu cạnh cộng
   1). Đây là đổi phương pháp, trái với quyết định 03/10 "làm theo bài báo", và phải chạy thêm để so
   cho sạch.

Claude đề nghị: lựa chọn 2 cho VietSentiWordNet; với SenticNet tiếng Việt thì đưa số đo ở mục 4 vào
báo cáo thay vì chạy. Nên hỏi cô, vì đây là chỗ đề cương nêu đích danh SenticNet.
