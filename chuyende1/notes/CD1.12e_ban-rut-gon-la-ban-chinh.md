# CD1.12e — Bản rút gọn thành bản chính; bỏ hai mục cuối của Chương 1

Ngày 13/10/2026. Học viên quyết: từ nay lấy bản rút gọn làm bản chính, và bỏ hai mục "Kế hoạch thực
hiện" và "Cấu trúc của chuyên đề".

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `chuyende1/report/nhap_rut_gon/Chuong1_TongQuan.md` | Sửa, không lên GitHub | Bỏ mục 1.7 và 1.8 cùng Bảng 1.1. Chương 1 còn sáu mục, từ 1.1 tới 1.6 |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx` | Ghép lại, không lên GitHub | Có bản sao lưu `..._rutgon.20261013-150946.docx.bak` |
| `scripts/nhap_chuong_vao_docx.py` | Sửa | Hai đường dẫn mặc định trỏ vào bản chính |
| `scripts/doi_chieu_ban_goc.py` | Sửa | Thư mục nháp mặc định là bản chính |
| `scripts/doi_chieu_chuong4.py`, `scripts/doi_chieu_ban_rut_gon.py` | Sửa lời ghi chú | Ghi rõ công cụ đang kiểm bản nào và giới hạn từ nay |
| `chuyende1/gaps/GAP-036_...md` | Tạo | Công cụ đối chiếu Chương 4 chưa kiểm thẳng được bản chính |
| `chuyende1/gaps/GAP-034_...md` | Sửa | Đóng: bản chính đã ở khổ A4, tiêu đề Times New Roman |

Bản đầy đủ (`chuyende1/report/nhap/` và `ChuyenDe1_NguyenMinhTrong.docx`) không bị đụng tới; mã băm của
file Word đó trước và sau trùng nhau. Nó là bản lưu, không được cập nhật nữa.

## 2. VÌ SAO LÀM THẾ

- Đổi đường dẫn mặc định: lệnh ghép gõ không kèm cờ phải rơi vào bản chính. Nếu để như cũ thì một lệnh
  gõ theo thói quen sẽ ghi vào file mà học viên muốn giữ nguyên.
- Không đổi mặc định của `doi_chieu_chuong4.py`: 153 chỗ kiểm của nó gắn với nguyên văn của bản đầy đủ.
  Trỏ nó vào bản chính lúc này chỉ cho ra 56 dòng báo lệch không phải lỗi số liệu.

## 3. ĐỌC KẾT QUẢ THẾ NÀO

- `nhap_chuong_vao_docx.py --ghi-de` nay in dòng "Đã ghi ...ChuyenDe1_NguyenMinhTrong_rutgon.docx".
- `doi_chieu_ban_goc.py kiem` đọc bốn chương của bản chính; thêm `PhuLuc.md` để kiểm phụ lục.
- `doi_chieu_chuong4.py` không kèm cờ vẫn in kết quả của bản đầy đủ. Đừng đọc nó như kết quả của bản chính.

## 4. KẾT QUẢ

| | Trước | Sau khi bỏ hai mục |
|---|---|---|
| Chương 1 | 5 trang, 8 mục | 4 trang, 6 mục |
| Chương 2 | 6 trang | 6 trang |
| Chương 3 | 10 trang | 10 trang |
| Chương 4 | 17 trang | 17 trang |
| Bốn chương | 38 trang | 37 trang |
| Cả file | 65 trang | 64 trang |
| Bảng trong thân bài | 13 | 12 |

Số trang do Word đếm trên một bản sao, khổ A4. Phần bị bỏ dài khoảng 380 chữ, kể cả Bảng 1.1.

## 5. GIỚI HẠN

- Quy định trình bày của trường, Phần III, viết rằng nội dung chuyên đề gồm "tổng quan các vấn đề liên
  quan đến đề tài, mục tiêu, phương pháp nghiên cứu, các kết quả đạt được, kế hoạch thực hiện để đạt
  được mục tiêu đặt ra". Phần I mục 2 cũng liệt kê "Kế hoạch thực hiện" trong Chương 1, kèm chữ "nên
  (nhưng không bắt buộc)". Sau lần bỏ này, bản chính không còn mục kế hoạch nào có nội dung: mục 6.3 về
  kế hoạch của chuyên đề tiếp theo mới có tiêu đề. Mục "Cấu trúc của chuyên đề" thì quy định không nhắc.
- Mục lục trong file Word chưa cập nhật, còn hiện hai mục đã bỏ cho tới khi bấm Ctrl+A rồi F9.
- `doi_chieu_chuong4.py` chưa kiểm thẳng được bản chính (GAP-036). Hôm nay số liệu của bản chính được
  bảo đảm theo đường vòng qua bản đầy đủ.
- Các trang đầu, Chương 5, Chương 6 vẫn là khung: còn 19 dòng `[TODO ...]`, gồm 9 ở các trang đầu, 2 ở
  Chương 4 (mục 4.3 và 4.5, chờ số đo), 5 ở Chương 5 và 3 ở Chương 6.

## 6. KIỂM CHỨNG

```
487 passed, 1 skipped   (cả bộ, sau khi đổi đường dẫn mặc định)
doi_chieu_ban_rut_gon.py: 214 hàng bảng, 0 hàng lạ; 0 con số lạ; 60 khoá, 0 khoá lạ, 0 khoá bị bỏ;
                          190 câu có số, 130 giữ nguyên văn, 60 đã viết lại
doi_chieu_ban_goc.py kiem (bản chính): Chương 2: 7 con số, thấy 7. Chương 3: 82 con số, thấy 75,
                          thấy ở công trình khác cùng đoạn 7, cần xem tay 0
doi_chieu_ban_goc.py kiem PhuLuc.md: 64 con số, thấy 48, cần xem tay 16; cả 16 là số của chính chuyên đề
                          về kappa, đứng cạnh trích dẫn bài của Cohen
doi_chieu_chuong4.py: bản đầy đủ 153 khớp, 0 lệch; Chương 4 của bản chính 97 khớp, 56 lệch;
                          Chương 4 nối Phụ lục của bản chính 146 khớp, 7 lệch (đã đọc tay, không con số nào lệch)
Word, file bản chính: khổ 21,0 x 29,7 cm; tiêu đề cấp 1, 2, 3 là Times New Roman; 64 trang;
                          Chương 1 từ trang 1, Chương 2 từ 5, Chương 3 từ 11, Chương 4 từ 21, Chương 5 từ 38
File Word: 22 bảng, 1 hình, 60 tài liệu tham khảo; trong thân bài không còn "Kế hoạch thực hiện",
                          "Cấu trúc của chuyên đề", "Bảng 1.1"
```

Trước khi ghép, file Word mà học viên đã mở và lưu lúc 15:03 được so với kết quả ghép lần trước: nội dung
đoạn văn và bảng trùng nhau, chỉ thừa một dòng trống ở cuối. Không có chỗ sửa tay nào bị ghi đè.

## 7. VIỆC CỦA BẠN

1. Mở `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx`, bấm Ctrl+A rồi F9 để mục lục bỏ hai mục
   cũ, rồi đọc Chương 1.
2. Quyết về mục kế hoạch (mục 5, gạch đầu dòng thứ nhất): giữ như hiện giờ và để kế hoạch ở mục 6.3 khi
   viết Chương 6, hoặc hỏi cô xem bản nộp tiến độ có cần mục kế hoạch không.
3. Cho biết có đồng ý để Claude chỉnh `doi_chieu_chuong4.py` cho nó kiểm thẳng bản chính không (GAP-036).
   Nên làm trước khi đưa số của mục 4.3 và 4.5 vào.
4. Từ nay sửa nội dung ở `chuyende1/report/nhap_rut_gon/`, không sửa ở `chuyende1/report/nhap/`.
