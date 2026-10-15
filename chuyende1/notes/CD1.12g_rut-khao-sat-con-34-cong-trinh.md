# PHIẾU BÀN GIAO — [CD1.12g] Rút phần khảo sát của bản chính từ 48 xuống 34 công trình

Ngày 16/10/2026. Học viên hỏi: trong 48 công trình khảo sát có công trình nào không liên quan hoặc không có ích
không, nếu có thì loại bớt vì không muốn ghi quá nhiều vào báo cáo.

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `chuyende1/survey/khong_trinh_bay.csv` | Tạo | 14 công trình đã đọc nhưng không trình bày trong báo cáo, mỗi dòng kèm lý do |
| `scripts/survey_tools.py` | Sửa | `table-gon` bỏ các công trình trong file trên (cờ `--khong-trinh-bay`), từ chối khoá không phải công trình đã đọc, in số công trình theo nhóm |
| `tests/test_survey_tools.py` | Sửa | Thêm 3 test |
| `chuyende1/survey/survey_protocol.md` | Sửa | Dòng N₅: 34 công trình, trỏ về file trên |
| `chuyende1/report/nhap_rut_gon/Chuong3_KhaoSat.md` | Sửa, không lên GitHub | Mục 3.1 thêm một câu nói đã bỏ 14 công trình và vì sao; sửa Bảng 3.1 và mọi con số đếm; bỏ các câu chỉ liệt kê tên |
| `chuyende1/report/nhap_rut_gon/Chuong1_TongQuan.md`, `TrangDau.md` | Sửa, không lên GitHub | 48 thành 34; phần tóm tắt: 13 công trình tiếng Việt thành 12 |
| `chuyende1/report/nhap_rut_gon/PhuLuc.md` | Sửa, không lên GitHub | Bảng A.1 sinh lại còn 34 dòng; Bảng A.2 bỏ 11 dòng |
| `chuyende1/report/nhap_rut_gon/sao_luu/20261016-khao-sat/` | Tạo, không lên GitHub | Bản trước khi sửa của bốn file trên |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx` | Ghép lại, Word cập nhật trường và lưu | Sao lưu `..._rutgon.20261016-024722.docx.bak` |

## 2. TIÊU CHÍ BỎ

Một công trình bị bỏ khỏi báo cáo khi thoả cả hai điều:

1. Trong bản chính nó chỉ được nêu tên trong một câu liệt kê và có một dòng ở phụ lục: không cấp con số, không làm
   căn cứ cho lập luận hay khoảng trống nào, không được trích ở Chương 1, 2, 4.
2. Nó không thuộc các chủ đề trọng tâm: tiếng Việt có tác vụ cảm xúc, phủ định hay chuyển ý, mô hình đồ thị mức
   khía cạnh, và các mô hình hay thành phần chuyên đề thực nghiệm (từ điển cảm xúc, ATAE-LSTM, PhoBERT, ASGCN,
   Sentic-GCN, mô hình ngôn ngữ lớn) hay định nghĩa của hướng nơ-ron và ký hiệu.

Đây là đúng bước N₅ của giao thức khảo sát ("chỉ cần nhắc tên, không cần đào sâu"), và plan cũng tách hai mức: ma
trận ≥ 45 công trình, Chương 3 khoảng 25 bài phân tích sâu. Ma trận vẫn giữ đủ 48 công trình, nên tiêu chí của
plan cho ma trận (≥ 45 dòng, mỗi nhóm ≥ 4) vẫn đạt.

| Công trình bị bỏ | Nhóm | Lý do ngắn |
|---|---|---|
| Jiang và cộng sự 2011, Vo và Zhang 2015 | Cổ điển | Twitter, chỉ nêu tên |
| TD-LSTM, MemNet, IAN, RAM | Tuần tự | Chỉ nêu tên làm ví dụ; bậc 2 theo ATAE-LSTM |
| XLM-R, BARTpho | Tiền huấn luyện | Không có tác vụ cảm xúc tiếng Việt, chỉ có một dòng ở phụ lục |
| Dong và cộng sự 2014 | Đồ thị | Chỉ nêu tên làm tiền thân; vai trò đó đã có Socher và cộng sự |
| Zhang và cộng sự 2021, Varia và cộng sự 2023, InstructABSA | Sinh | Chỉ nêu tên; hướng sinh đã có Thin và Nguyen |
| Hamilton và cộng sự 2024 | Nơ-ron và ký hiệu | Tổng quan không thực nghiệm; định nghĩa hướng đã có Garcez và Lamb |
| SemEval 2015 | Tài nguyên | Chỉ nêu tên trong câu liệt kê tập dữ liệu |

## 3. KẾT QUẢ

| | Trước | Sau |
|---|---|---|
| Công trình được trình bày | 48 | 34 |
| Theo nhóm (cổ điển, tuần tự, tiền huấn luyện, đồ thị, sinh, nơ-ron và ký hiệu, tài nguyên) | 5, 7, 8, 9, 5, 5, 9 | 3, 3, 6, 8, 2, 4, 8 |
| Từ năm 2020; tiếng Việt | 25; 13 | 19; 12 |
| Dùng đồ thị; phủ định, chuyển ý; có giải thích | 11; 7; 14 | 9; 7; 11 |
| Mô hình đồ thị mức khía cạnh | 8 | 7 |
| Tài liệu tham khảo | 61 | 47 |
| Cả file (Word đếm) | 70 trang | 67 trang |
| Chương 3 | 10 trang | 10 trang |

Chương 3 không ngắn đi một trang nào: mười bốn công trình đó chỉ chiếm vài câu liệt kê trong thân chương; phần lớn
chỗ của chúng là dòng ở Bảng A.1, A.2 và mục ở danh sách tài liệu tham khảo. Bốn khoảng trống ở mục 3.10 không
đổi: không khoảng trống nào dựa vào các công trình bị bỏ.

## 4. QUYẾT ĐỊNH THIẾT KẾ VÀ PHƯƠNG ÁN ĐÃ LOẠI

- Không xoá dòng khỏi ma trận: ma trận là hồ sơ của khảo sát (đã đọc 48 công trình), còn việc trình bày gì là
  quyết định của báo cáo. Đưa một công trình trở lại chỉ cần xoá một dòng trong `khong_trinh_bay.csv`.
- Mục 3.1 nói thẳng đã bỏ 14 công trình và theo tiêu chí nào, thay vì lặng lẽ đổi 48 thành 34: mục đó đã nêu 21
  công trình xuất phát cộng 27 công trình mở rộng, tức 48.
- Các công trình đứng ranh giới được giữ:
  - Hatzivassiloglou và McKeown: gốc của hướng từ điển cảm xúc, mà bậc 1 và trọng số cạnh của Sentic-GCN dùng.
  - Garcez và Lamb: tài liệu định nghĩa hướng nơ-ron và ký hiệu, hướng của cả luận văn.
  - ViSoBERT, Nguyen và Nguyen (tách từ): tiếng Việt có tác vụ cảm xúc, trả lời câu hỏi thứ hai của khảo sát.
  - UIT-ViSD4SA: tiếng Việt, có mặt trong Bảng 3.3.
  - Kocon và cộng sự: là căn cứ của khoảng trống thứ hai.
  - CDT, kumaGCN, DualGCN, SSEGCN: là các dòng của Bảng 3.2, so sánh các mô hình đồ thị, hướng chính của đề tài.
- "hầu hết dưới dạng trực quan hoá trọng số attention" đổi thành "phần lớn": ba trong các công trình bị bỏ (MemNet,
  IAN, RAM) thuộc dạng giải thích đó, nên tỉ lệ còn lại không còn là gần hết. Ma trận không ghi dạng giải thích của
  từng công trình, nên không đếm chính xác được hơn.
- Bản đầy đủ (bản lưu) không sửa, vẫn 48 công trình.

## 5. ĐIỂM NỐI VỚI STEP SAU

Nếu học viên muốn rút tiếp: các công trình ranh giới ở mục 4. Mỗi lần đổi danh sách thì chạy lại `table-gon`, chép
Bảng A.1, sửa các con số ở mục 3.1 đến 3.10, Chương 1 và phần tóm tắt, rồi ghép lại.

## 6. KIỂM CHỨNG

```
survey_tools.py table-gon --khong-trinh-bay <file không có>   sinh lại Bảng A.1 cũ, giống từng ký tự (48 dòng); in 25, 13, 11, 7, 14
                                                             đúng các con số cũ của Chương 3
survey_tools.py table-gon                                    34 dòng; 19 từ 2020, 12 tiếng Việt, 9 đồ thị, 7 phủ định, 11 giải thích
đối chiếu một lần bằng mã                                    23 con số và cụm chữ đếm ở Chương 3 (cả 7 hàng Bảng 3.1) khớp số
                                                             đếm từ ma trận, 0 lệch
grep các khoá bị bỏ trong mọi file nháp của bản chính         không còn chỗ nào trích
doi_chieu_chuong4.py                                         224 chỗ, khớp 224; phần tóm tắt không có số lạ
doi_chieu_ban_goc.py kiem, Chương 3                          81 con số, thấy 75, thấy ở công trình khác cùng đoạn 6, cần xem tay 0
doi_chieu_ban_rut_gon.py                                     số lạ 34, 19 và 7 hàng Bảng 3.1: nội dung mới chỉ có ở bản chính (đã đối chiếu ở trên)
pytest tests/ -q                                             517 passed, 1 skipped
Word                                                          67 trang; Chương 3 trang 11 đến 20; tài liệu tham khảo 47 mục
```

## 7. DỪNG LẠI VÀ HỎI

1. Xem danh sách 14 công trình ở mục 2 (hoặc file `chuyende1/survey/khong_trinh_bay.csv`): có công trình nào muốn giữ lại không?
2. Có muốn bỏ thêm các công trình ranh giới ở mục 4 không? Bỏ hết sáu công trình đầu thì còn 28 công trình.
3. Có push commit này không?
