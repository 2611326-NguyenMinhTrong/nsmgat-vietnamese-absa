# CD1.12f — Công cụ đối chiếu kiểm thẳng bản chính; dọn các trang đầu của file nộp

Ngày 13/10/2026. Học viên yêu cầu hai việc: chỉnh công cụ đối chiếu Chương 4 để kiểm thẳng bản chính, và
dọn file nộp (tóm tắt, danh sách bảng và hình, chữ viết tắt, lời cam đoan, 19 dòng để trống).

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `scripts/doi_chieu_chuong4.py` | Sửa | Mặc định kiểm bản chính; hàng bảng phải ở đúng bảng; thêm chỗ kiểm cho câu so sánh và phần tóm tắt |
| `tests/test_doi_chieu_chuong4.py` | Tạo | 9 test cho phần tìm kiếm, không cần dữ liệu thật |
| `scripts/nhap_chuong_vao_docx.py` | Sửa | Ghép các trang trước Chương 1 từ `TrangDau.md`; danh sách bảng, hình tự động; thu gọn trang bìa |
| `tests/test_nhap_chuong_vao_docx.py` | Sửa | Thêm 7 test cho các trang đầu |
| `chuyende1/report/nhap_rut_gon/TrangDau.md` | Tạo, không lên GitHub | Lời cảm ơn (bản nháp), lời cam đoan, tóm tắt, chữ viết tắt |
| `chuyende1/report/nhap_rut_gon/Chuong5_*.md`, `Chuong6_*.md` | Tạo, không lên GitHub | Mỗi mục một câu nêu nội dung dự kiến |
| `chuyende1/report/nhap_rut_gon/Chuong4_ThucNghiem.md` | Sửa | Sửa một câu sai ở mục 4.7 (GAP-037) |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx` | Ghép lại, Word cập nhật trường và lưu | Có bản sao lưu `..._rutgon.20261013-165016.docx.bak` |
| `chuyende1/gaps/GAP-036`, `GAP-037`, `GAP-038`, `INDEX.md` | Sửa, tạo | Đóng GAP-036; ghi hai lỗi mới tìm thấy |

## 2. CÔNG CỤ ĐỐI CHIẾU NAY KIỂM GÌ

- Đọc Chương 4, Phụ lục và mục TÓM TẮT của bản chính. `--ban day_du` kiểm bản lưu.
- Mỗi hàng bảng phải nằm trong đúng bảng mang số đó, và tên bảng phải chứa một cụm từ khoá. Trước đây một hàng
  chỉ cần có ở đâu đó trong chương, nên hai bảng cùng dạng hàng bị đổi tên cho nhau vẫn qua được.
- Câu so sánh không có con số ("cao nhất", "duy nhất", "ở mọi mô hình") có điều kiện tính trên số thật.
  Điều kiện của câu "ổn định nhất giữa các hạt giống" ở mục 4.7 sai, nên câu đó đã được sửa (GAP-037).
- Phần tóm tắt: chín cụm có số được tính lại, và mọi con số của phần tóm tắt phải có trong các chương hoặc phụ lục.

## 3. CÁC TRANG ĐẦU

- Lời cam đoan theo mẫu Phụ lục 6 của quy định, "luận văn/đề án" đổi thành "chuyên đề".
- Tóm tắt: năm đoạn, 524 chữ, dài hơn một trang và nằm trên hai trang (quy định: không quá hai trang). Chỉ nêu những gì đã có số;
  đoạn cuối ghi rõ phần nào đang thực hiện. Chưa có bản tiếng Anh.
- Lời cảm ơn: ba câu do Claude viết làm bản nháp, chỉ nêu điều có thật (giảng viên hướng dẫn, chương trình học,
  tài nguyên đã dùng). Học viên sửa theo ý mình trong `TrangDau.md`.
- Chữ viết tắt: dựng lại từ những chữ thật sự có trong bản chính, 14 mục, ba cột (chữ viết tắt, tên đầy đủ,
  nghĩa tiếng Việt). Tên đầy đủ của ASGCN, ATAE-LSTM, R-GAT, GloVe, BERT và UIT-ViSFD được đối chiếu với văn bản
  của bài gốc đã tải. Bỏ CPU và GPU để bảng nằm gọn một trang.
- Danh sách bảng (21 mục) và danh sách hình (1 mục) do Word dựng từ trường TC gắn vào từng tên bảng, tên hình.
  Trường TC mang chữ ẩn thì Word không gom (đã thử), nên trường để không ẩn; nó không hiện gì trên trang.
- Bỏ mục danh sách công thức (quy định không đòi), bỏ mọi dòng [TODO] ở các trang đầu, mỗi mục một trang mới.
- Trang bìa trước đây tràn sang trang thứ hai (GAP-038); nay nằm một trang. Dòng có chữ của bìa không đổi, nên
  dòng "tháng ...... năm 2026" vẫn để trống.
- Chương 5 và 6: thay khung bằng file nháp giữ chỗ, mỗi mục một câu nêu nội dung dự kiến. Đầu mỗi chương ghi
  "Chương này đang được thực hiện".

## 4. KẾT QUẢ

| | Trước | Sau |
|---|---|---|
| Dòng [TODO] và "(Ngân sách ...)" trong file Word | 19 và 2 | 2 và 0 (mục 4.3 và 4.5, chờ số đo) |
| Trang bìa | 2 trang | 1 trang |
| Các trang đầu | không ngắt trang, danh sách để trống | i đến xi, mỗi mục một trang |
| Bốn chương | 37 trang | 37 trang |
| Cả file | 64 trang | 69 trang |

Số trang do Word đếm sau khi cập nhật mọi trường.

## 5. GIỚI HẠN

- Lời cảm ơn là bản nháp của Claude. Tóm tắt cần viết lại sau khi có Chương 5, 6 và số đo của mục 4.3, 4.5.
- Bìa: chưa điền tháng; dòng học viên còn hai dấu gạch dài ("NGUYỄN MINH TRỘNG — MSHV 2611326 — Khoá 2026A").
- Các bảng trong file đều giãn dòng 1,5 như thân bài. Chưa đo xem giãn dòng đơn trong bảng bớt được bao nhiêu trang.
- Danh sách tài liệu tham khảo chưa bổ sung số trang.
- Hai dòng [TODO] của mục 4.3 và 4.5 còn đó cho tới khi có số đo.
- Ngày 14/10, học viên đang sửa một bản riêng ở `Backup\ChuyenDe1_NguyenMinhTrong_final.docx`, lưu lúc 22:46. Bản
  đó dựng từ bản đầy đủ, khác bản chính ở nhiều chỗ (xem phần trả lời trong phiên làm việc và VIEC_CAN_LAM).
  Không có thay đổi nào của bản đó đi vào bản chính.

## 6. KIỂM CHỨNG

```
503 passed, 1 skipped   (cả bộ)
doi_chieu_chuong4.py: bản chính 215 chỗ, khớp 215, bỏ qua 5 câu chỉ có ở bản đầy đủ, 0 số lạ trong tóm tắt
                      bản đầy đủ 174 chỗ, khớp 174
doi_chieu_ban_rut_gon.py: 214 hàng bảng, 0 hàng lạ; 0 con số lạ; 60 khoá, 0 khoá lạ
doi_chieu_ban_goc.py kiem: Chương 2: 7 con số, thấy 7. Chương 3: 82 con số, thấy 75, thấy ở công trình khác
                      cùng đoạn 7, cần xem tay 0
Word, file bản chính: A4, tiêu đề Times New Roman; mục lục 57 dòng, danh sách bảng 21, danh sách hình 1;
                      bìa trang 1, LỜI CẢM ƠN trang i, Chương 1 trang 1, Chương 5 trang 38; 69 trang
```

## 7. VIỆC CỦA BẠN

1. Quyết file nào để nộp: `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx` (bản chính) hay
   `Backup\ChuyenDe1_NguyenMinhTrong_final.docx` (bản bạn đang sửa). Nếu là bản chính: nói những chỗ bạn muốn giữ
   từ bản kia (ví dụ lời văn phần tóm tắt, câu "Lời đầu tiên"), Claude đưa vào `TrangDau.md`.
2. Đọc lời cảm ơn và tóm tắt ở `chuyende1/report/nhap_rut_gon/TrangDau.md`; sửa thẳng trong file đó.
3. Cho Claude biết tháng ghi trên bìa, hoặc gõ thẳng trên bìa trong Word (lệnh ghép không đụng tới dòng đó).
