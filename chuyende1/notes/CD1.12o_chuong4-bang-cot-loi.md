# PHIẾU BÀN GIAO — [CD1.12o] Chương 4 chỉ giữ bảng cốt lõi, lời văn không đọc lại số của bảng

Ngày 17/10/2026. Học viên yêu cầu: "rút bớt các chỗ đọc lại số liệu từ bảng đã có trên word, chỉ đọc lại số liệu khi thật sự
cần, nếu không thì chỉ cần nói bao quát phân tích về số liệu đó là được. Trong Chương 4, chỉ giữ lại các bảng cốt lõi tầm 4-6
bảng, các bảng khác không phải cốt lõi thì tóm tắt bằng 1–2 đoạn văn thay vì kẻ nguyên bảng, nhưng chất lượng thực nghiệm vẫn
phải rõ ràng".

## 1. ĐÃ LÀM GÌ

1. Chọn 5 bảng cốt lõi, là những bảng mà kết luận của chương dựa vào:
   - 4.1 kết quả trên tập kiểm tra;
   - 4.2 kiểm định bootstrap;
   - 4.3 thí nghiệm đối chứng;
   - 4.4 chi phí;
   - 4.5 accuracy trên bốn nhóm của tập chẩn đoán.
2. Năm bảng còn lại của Chương 4:
   - quy mô dữ liệu, hành vi trên lớp trung tính, thành phần tập chẩn đoán, hiệu số so với nhóm thường: tóm tắt bằng lời
     trong chương, nguyên bảng chuyển sang Phụ lục C trực tuyến;
   - thang mô hình: thay bằng danh sách năm bậc ở mục 4.3 (số tham số đã có ở Bảng 4.4).
3. Phụ lục C trực tuyến đánh số lại C.1 đến C.10 theo thứ tự được nhắc trong chương; thêm câu dẫn; sửa hai chỗ Phụ lục B dẫn
   tới số bảng cũ của báo cáo. Commit `a534885`; địa chỉ trong `PhuLuc.md` và file Word ghim vào commit này.
4. Lời văn Chương 4 viết lại theo xu hướng và kết luận, bỏ các số đã có trong bảng của chương. Giữ: số không có trong bảng nào
   (hiệu số trên nhóm con, giá trị p của phép hoán vị, khoảng hiệu số trên tập chẩn đoán), số then chốt của kết luận (15,0 đến
   17,6 điểm ở nhóm cả hai), và số mô tả phương pháp. Không đổi các mục 4.1.2, 4.2 và phần mô tả mô hình ở 4.3, trừ chỗ dẫn bảng.
5. Sửa câu "phần lớn khoảng cách giữa ASGCN và PhoBERT đến từ cách đọc ra" ở mục 4.4 và câu tương ứng ở 4.7 (GAP-042).
6. `scripts/doi_chieu_chuong4.py`: số bảng mới; câu chỉ còn ở bản lưu thì bỏ qua ở bản chính; mỗi câu xu hướng mới có chỗ kiểm
   `neu()` với điều kiện từ số liệu (ví dụ "giảm nhẹ ở cả hai độ đo, với hiệu số có ý nghĩa theo bootstrap" chỉ đúng khi cả hai
   hiệu số âm, nhỏ hơn 1 điểm và p dưới 0,05). Bỏ hàm `cau_tung_seed` và `import math` không còn dùng. Sửa 6 test theo số bảng mới.
7. File Word: ghép riêng Chương 4 và Phụ lục, cập nhật mục lục và danh sách bảng. Sao lưu `..._rutgon.20261017-134510.docx.bak`;
   lưu lần cuối 13:45:25. Bản nháp sao lưu ở `nhap_rut_gon/sao_luu/20261017-rut-chuong-4/`.

## 2. KẾT QUẢ

| | Trước | Sau |
|---|---|---|
| Số bảng trong Chương 4 | 10 | 5 |
| Số thập phân trong lời văn Chương 4 | 131 | 66 |
| Trong đó trùng hệt một số của bảng trong chương | 73 | 9 (đều trùng ngẫu nhiên, ví dụ 0,01 là hệ số suy giảm trọng số) |
| Chữ trong bảng của Chương 4 | 1.474 | 839 |
| Chương 4 | 21 trang | 19 trang |
| Cả file Word | 63 trang | 60 trang |

Số trang theo mục của Chương 4 hiện nay: 4.1 khoảng 3, 4.2 khoảng 2, 4.3 khoảng 3, 4.4 khoảng 4, 4.5 khoảng 2, 4.6 khoảng 3,
4.7 khoảng 2. Phần phương pháp (4.1 đến 4.3) chiếm khoảng 8 trang và chưa được rút trong bước này.

## 3. KIỂM CHỨNG

- `doi_chieu_chuong4.py`: bản chính 234 trên 234 (bỏ qua 40 câu chỉ có ở bản lưu), địa chỉ ghim đúng (lưu ý chưa push);
  bản lưu 174 trên 174.
- Rà từng con số trong lời văn mới so với danh sách chỗ kiểm: mọi số chưa có chỗ kiểm là số mục, số bảng, siêu tham số, cấu
  hình máy, số dẫn từ bài khác, hoặc các số đã ghi từ trước là chưa có chỗ kiểm; không số mới nào lọt.
- `kiem_sua_tay_word.py` trước khi ghép (so với bản nháp trước bước này): chữ khớp, không có chỗ sửa tay, file Word không bị sửa
  từ lần lưu 03:08:45. Sau khi ghép: chữ khớp bản nháp mới, 6 phương trình còn nguyên.
- Chạy thử trên bản sao trước: mọi chỗ đổi nằm trong Chương 4 và dòng địa chỉ ở Phụ lục.
- Toàn bộ test: 545 qua, 1 bỏ qua.

## 4. ĐIỂM CẦN BIẾT

- Mục tiêu chính của bước này là bớt đọc lại số và bớt bảng, nên Chương 4 chỉ ngắn đi 2 trang. Phần dài còn lại là phương
  pháp: mục 4.1.2 (quy trình và độ nhất quán của tập chẩn đoán), 4.2 (giao thức, phần cứng, phép thử đổi nền tảng) và phần mô
  tả từng mô hình ở 4.3.
- Địa chỉ trong báo cáo trỏ tới commit `a534885`, chỉ mở được sau khi push.
- Chương 1 đến 3 gần như không đọc lại số từ bảng (Chương 3 có 6 trên 30 số thập phân trùng với bảng, phần lớn là các mốc cần
  cho lập luận ở mục 3.8); chưa sửa.

## 5. DỪNG LẠI VÀ HỎI

1. Mở file Word đọc lại Chương 4 (trang in 21 đến 39), nhất là danh sách năm bậc ở 4.3 và các đoạn tóm tắt ở 4.4, 4.6.
2. Có muốn rút tiếp phần phương pháp (4.1.2, 4.2, 4.3) không, và rút tới mức nào?
3. Push các commit đang ở máy (91a4d2b, a4e8889, d1f240b, a534885 và commit phiếu này)?
