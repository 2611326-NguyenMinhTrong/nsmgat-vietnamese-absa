# PHIẾU BÀN GIAO — [CD1.12m] Vì sao báo cáo dài hơn bản mẫu (chỉ phân tích, chưa sửa)

Ngày 17/10/2026. Học viên hỏi: những nguyên nhân chính nào khiến `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx`
dài gấp đôi bản mẫu `chuyende1/docs/2591306-chuyende1spkt-thamkhao.pdf`. Chưa sửa gì.

## 1. CÁCH ĐO

- Bản mẫu (PDF): đếm trang và chữ từng trang bằng PyMuPDF; đo cỡ chữ, khoảng cách dòng, vùng chữ trên các trang toàn chữ.
- Bản của học viên: đọc một bản sao (file thật không bị mở để ghi). Số trang của từng tiêu đề lấy từ Word (COM, chỉ đọc);
  số chữ, số bảng, hàng bảng, hình đếm bằng python-docx theo từng mục cấp 1; số dòng và chữ trên trang lấy từ Word.

## 2. SỐ TRANG THEO PHẦN

| Phần | Bản mẫu | Bản học viên | Chênh |
|---|---|---|---|
| Bìa và các trang đầu | 13 | 11 | −2 |
| Chương 1 | 6 | 4 | −2 |
| Chương 2 | 6 | 6 | 0 |
| Chương 3 | 7 | 10 | +3 |
| Chương 4 | 4 | 21 | +17 |
| Chương 5 | 5 | 1 (khung) | −4 |
| Chương 6 | 3 | 1 (khung) | −2 |
| Tài liệu tham khảo | 2 | 5 | +3 |
| Phụ lục | 0 | 10 | +10 |
| Tổng | 46 | 69 | +23 |

Không kể các trang đầu: 58 trang so với 33 (gấp 1,76 lần). Chương 5, 6 mới là khung; nếu viết dài như bản mẫu (8 trang)
thì khoảng 64 so với 33, tức gần gấp đôi.

## 3. SỐ CHỮ

| Phần | Bản mẫu | Bản học viên (lời văn + chữ trong bảng) |
|---|---|---|
| Chương 1 | 2.125 | 1.565 |
| Chương 2 | 2.159 | 2.211 |
| Chương 3 | 2.587 | 3.040 + 377 |
| Chương 4 | 1.407 | 6.584 + 981 |
| Chương 5, 6 | 2.905 | 340 (khung) |
| Tài liệu tham khảo | 360 (23 mục) | 997 (47 mục) |
| Phụ lục | 0 | 1.162 + 1.371 |

## 4. DÀN TRANG

Giống bản mẫu: Times New Roman 13, giãn dòng 1,5, lề trái 3,5 cm, lề phải 2 cm. Khác: lề trên 3,0 cm, lề dưới 3,5 cm, cách
6 pt sau mỗi đoạn. Trang toàn chữ: bản học viên 26 đến 28 dòng, 400 đến 480 chữ; bản mẫu 29 đến 30 dòng, 435 đến 464 chữ.
Dàn trang chỉ đóng góp khoảng 5 %, cỡ 3 trang.

## 5. NGUYÊN NHÂN, XẾP THEO SỐ TRANG

1. Chương 4, +17 trang (khoảng ba phần tư chênh lệch).
   - Phạm vi thực nghiệm: 6 mô hình × 5 seed, 2 mô hình đối chứng, sắp thêm GPT-4o; bản mẫu 2 baseline, 1 seed, 1 tập dữ liệu.
   - Phần bản mẫu không có: tập chẩn đoán tự xây (mục 4.1.2 và 4.6, khoảng 5 trang), kiểm định bootstrap và hoán vị seed,
     thí nghiệm đối chứng, đo chi phí suy luận (mục 4.5, 2 trang).
   - 10 bảng (70 hàng) và 2 hình trong riêng Chương 4; cả bản mẫu có 3 bảng, 5 hình.
   - Lời văn nhắc lại số của bảng: 92 trên 131 số thập phân trong lời văn Chương 4 (70 %) đã có trong bảng.
   - Chi tiết tái lập và dè dặt: mục 4.2 (841 chữ) và 4.3 (1.283 chữ); 16 câu nêu giá trị p, 24 câu mang ý giới hạn hay dè
     dặt; ý "giới hạn" có ở 4.2, 4.6 và 4.7.
2. Phụ lục, +10 trang: bản mẫu không có phụ lục. A (bảng 34 công trình và A.2, 4 trang), B (quy trình chú thích, 2 trang,
   lặp đoạn độ nhất quán ở 4.1.2), C (6 bảng bổ sung, 4 trang).
3. Tài liệu tham khảo, +3 trang: 47 mục so với 23, mỗi mục trung bình 21 chữ so với 16.
4. Chương 3, +3 trang: khảo sát 34 công trình với 3 bảng (28 hàng). Bản mẫu gộp cơ sở lý thuyết và khảo sát vào một chương
   7 trang; bản học viên tách thành Chương 2 và 3, tổng 16 trang.
5. Dàn trang, khoảng 3 trang (mục 4).

Không phải nguyên nhân: các trang đầu (ngắn hơn bản mẫu 2 trang), Chương 1 (ngắn hơn 2 trang), Chương 2 (bằng nhau).

Chỗ dư thừa đã ghi từ trước (phiếu CD1.12h): đoạn độ nhất quán lặp ở 4.1.2 và Phụ lục B; sáu hàng Bảng A.2 lặp số liệu
Chương 3; mục 1.2 nhắc lại số của Bảng 3.2.

## 6. DỪNG LẠI VÀ HỎI

Học viên chỉ yêu cầu phân tích. Nếu muốn rút gọn: hỏi cô quy định "khoảng 30 trang" áp cho phần nào (việc E6), rồi chọn
mức cắt cho Chương 4, Phụ lục và Chương 3.
