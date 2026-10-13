# CD1.12d — Bản rút gọn của bốn chương đầu, trong một file Word mới

Ngày 13/10/2026. Học viên yêu cầu cắt báo cáo về khoảng 30 trang theo phương án đã nêu ở phiếu
CD1.10b mục 8, làm trong một file mới và giữ nguyên file hiện tại.

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `chuyende1/report/nhap_rut_gon/` | Tạo, không lên GitHub | Bốn chương rút gọn, `PhuLuc.md`, bản chép `tai_lieu.json` |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx` | Tạo, không lên GitHub | File Word của bản rút gọn |
| `scripts/doi_chieu_ban_rut_gon.py` + test | Tạo | Kiểm bản rút gọn không chứa điều gì bản đầy đủ không có |
| `scripts/nhap_chuong_vao_docx.py` + test | Sửa | Ghép thêm `PhuLuc.md` nếu có; cờ `--sua-dinh-dang` |
| `scripts/ute_docx.py` + test | Sửa | Đặt khổ A4; xoá thuộc tính font chủ đề của style tiêu đề (GAP-034) |
| `.gitignore` | Sửa | Thêm `chuyende1/report/nhap_rut_gon/` |

File `chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx` và thư mục `chuyende1/report/nhap/` không bị đụng
tới; mã băm của file Word trước và sau trùng nhau.

## 2. CẮT NHỮNG GÌ

- Chương 1: gộp mục 1.5 vào 1.4 (còn 8 mục); rút 1.2, 1.3, 1.6, 1.8.
- Chương 2: bỏ Hình 2.1, công thức GAT, công thức precision và recall, đoạn về ViSoBERT; số liệu về hai
  từ điển có sẵn chuyển sang mục 4.3; mô tả bootstrap rút còn một đoạn. Công thức đánh số lại từ (2.1) tới (2.8).
- Chương 3: mỗi nhóm phương pháp chỉ bàn một hoặc hai công trình liên quan trực tiếp tới đề tài; số liệu
  của các công trình còn lại vào Bảng A.2; Bảng 3.4 thành Bảng A.1.
- Chương 4: quy trình chú thích đầy đủ vào Phụ lục B; bảy bảng vào Phụ lục C (cũ là 4.2, 4.3, 4.7, 4.12,
  4.14, 4.15, 4.16); chín bảng còn lại đánh số lại từ 4.1 tới 4.9; lời văn các mục rút lại.
- Hai chỗ sửa nội dung, không phải cắt: mục 1.5 ghi "799 mẫu" thay cho "khoảng 800 mẫu"; bỏ dòng ghi
  chú nội bộ ở mục kế hoạch thực hiện.

Thứ bị bỏ hẳn khỏi bản rút gọn, chỉ còn ở bản đầy đủ: chênh lệch 200 giữa số đếm và bảng thống kê của
bài giới thiệu UIT-ViSFD; phiên bản PyTorch và việc nhật ký hai phiên Colab không được lưu; kích thước
bảng nhúng và siêu tham số riêng của BiLSTM; tỉ lệ mẫu bị cắt ở tập huấn luyện và phát triển.

## 3. ĐỌC KẾT QUẢ THẾ NÀO

`doi_chieu_ban_rut_gon.py` in bốn dòng đếm. Ba dòng đầu phải bằng 0: con số không có trong bản đầy đủ,
hàng bảng không có nguyên văn trong bản đầy đủ, khoá trích dẫn lạ. Dòng thứ tư đếm các câu có số đã
được viết lại; thêm `--in-cau` để in chúng ra đọc.

## 4. KẾT QUẢ

| | Bản đầy đủ | Bản rút gọn |
|---|---|---|
| Chương 1 | 7 trang | 5 trang |
| Chương 2 | 9 trang | 6 trang |
| Chương 3 | 18 trang | 10 trang |
| Chương 4 | 24 trang | 17 trang |
| Bốn chương | 58 trang | 38 trang |
| Số chữ phần lời | khoảng 17.900 | khoảng 12.300 |
| Bảng trong thân bài | 21 | 13 |
| Tài liệu được trích | 60 | 60 |

Số trang đo bằng Word ở khổ A4. Bản đầy đủ đo sau khi đổi sang A4 trên một bản sao tạm.

**Kết quả chưa tới mức đã ước lượng.** Phiếu CD1.10b ước bốn chương còn khoảng 32 trang; thực tế là 38.
Ước lượng số chữ mỗi trang của tôi quá lạc quan. Trừ bảng và hình (khoảng 6 trang), lời văn của bốn
chương còn khoảng 32 trang.

## 5. GIỚI HẠN

- Công cụ kiểm được rằng không con số nào mới và không hàng bảng nào bị sửa. Nó không kiểm được một con
  số có còn gắn đúng mô hình, đúng tập, đúng độ đo hay không. 60 câu có số đã viết lại được đọc đối
  chiếu bằng mắt một lượt khi viết; học viên cần đọc lại.
- Bảng A.2 là bảng mới, dựng từ các câu của Chương 3 bản đầy đủ. Số của nó có trong bản đầy đủ; cách
  xếp vào cột là của lần rút gọn này.
- Các trang đầu, Chương 5, Chương 6 của file mới vẫn là khung như file hiện tại. Mục lục chưa cập nhật.
- Hai chỗ `[TODO ...]` của mục 4.3 và 4.5 còn nguyên, chờ số đo.
- Từ đây có hai bản song song. Khi mục 4.3 và 4.5 có số, phải cập nhật cả hai, hoặc chọn một bản làm chính.

## 6. KIỂM CHỨNG

```
487 passed, 1 skipped   (cả bộ; trước đó 474)
doi_chieu_ban_rut_gon.py: 224 hàng bảng, 0 hàng lạ; 0 con số lạ; 60 khoá, 0 khoá lạ, 0 khoá bị bỏ;
                          191 câu có số, 131 giữ nguyên văn, 60 đã viết lại
doi_chieu_ban_goc.py kiem --nhap chuyende1/report/nhap_rut_gon:
    Chương 2: 7 con số, thấy 7.  Chương 3: 82 con số, thấy 75, thấy ở công trình khác cùng đoạn 7, cần xem tay 0
Word, file mới: khổ 21,0 x 29,7 cm; font tiêu đề cấp 1, 2, 3 là Times New Roman; 65 trang
```

## 7. VIỆC CỦA BẠN

1. Mở `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx`, bấm Ctrl+A rồi F9, đọc bốn chương và
   ba phụ lục. Thấy chỗ nào cắt quá tay thì báo mục nào cần lấy lại.
2. Quyết: dừng ở 38 trang, hay cắt tiếp về khoảng 32. Cắt tiếp nghĩa là bỏ nội dung thật; ba chỗ có
   thể bỏ, mỗi chỗ khoảng một đến hai trang: phần bình luận từng bậc ở mục 4.4 (giữ bảng và kết luận),
   ba đoạn "đọc theo từng dấu hiệu", "so mô hình trong từng nhóm", "ảnh hưởng của nhãn gốc" ở mục 4.6
   (chuyển vào Phụ lục C), và Bảng 3.3 cùng nửa mục 3.8.
3. Sau khi chọn, quyết bản nào là bản chính để các lần sửa sau chỉ làm ở một nơi.
