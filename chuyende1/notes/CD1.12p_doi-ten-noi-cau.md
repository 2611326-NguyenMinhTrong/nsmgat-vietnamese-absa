# PHIẾU BÀN GIAO — [CD1.12p] Đổi tên "ASGCN nối gốc" thành "ASGCN nối câu"; chặn ghép đè phần có phương trình Word

Ngày 17/10/2026. Học viên:

1. Muốn tên bảng viết dưới bảng. Claude báo quy định trình bày của trường (Phần I mục 3) ghi tên bảng đặt phía trên, còn bản
   mẫu đặt phía dưới; học viên chọn giữ phía trên. Không sửa gì.
2. Báo đã sửa một số chỗ trong Word.
3. Thấy "nối gốc" khó hiểu, bảo sửa lại; chọn tên "ASGCN nối câu" trong ba phương án.

## 1. ĐÃ LÀM GÌ

1. Đưa 5 chỗ học viên sửa trong Word (lưu 15:56) vào bản nháp:
   - Chương 2: p_o, p_e thành chỉ số dưới (bản nháp ghi "po", "pe");
   - Chương 4: D_ij, T_ij thành chỉ số dưới (bản nháp ghi "Dij", "Tij");
   - Phụ lục: bỏ "tại địa chỉ" và câu giải thích địa chỉ, rút câu dẫn Bảng A.1.
   Học viên cũng chuyển công thức (4.1) và hai công thức nữa ở Chương 2 sang phương trình Word: file có 9 phương trình.
2. Đổi tên biến thể trong bản nháp Chương 4 (19 chỗ) và Phụ lục C trực tuyến (7 chỗ). Viết lại các cụm đi kèm cho đúng nghĩa:
   - "nối thêm các cây con rời nhau" thành "gộp cây cú pháp của các câu trong cùng bình luận vào một đồ thị";
   - "mẫu có từ hai gốc trở lên" thành "mẫu có từ hai câu trở lên": trong mã, số gốc là số cây cú pháp, cũng là số câu
     VnCoreNLP tách ra;
   - "cây nối gốc" thành "đồ thị nối câu".
3. Tên hiển thị trong mã (`compare_baselines.TEN_HIEN_THI`, `make_figures.TEN_NGAN`, `eval_llm`) đổi theo; vẽ lại Hình 4.2 và
   Hình 5.1 đến 5.4; đổi tên trong ba bảng xuất ở `chuyende1/tables/`. Bản lưu (bản đầy đủ) giữ tên cũ: công cụ đối chiếu
   dùng `TEN_BAN_LUU` khi `--ban day_du`.
4. Phụ lục C trực tuyến commit ở `6e507d9`; địa chỉ trong bản nháp và file Word ghim vào commit này.
5. File Word sửa thẳng bằng COM, không ghép (Chương 4 đã có phương trình Word): thay chữ cả file theo 7 cặp, thay ảnh Hình 4.2
   bằng ảnh mới cùng độ rộng. Chạy thử trên bản sao trước. Sao lưu `..._rutgon.20261017-171115.docx.bak`; lưu lúc 17:11:37.
6. `nhap_chuong_vao_docx.py` thêm `dinh_dang_tay`: phần sắp bị thay có phương trình Word hay chữ chỉ số trên, dưới thì dừng
   với mã 3, kể cả khi có `--ghi-de`. Thêm 1 test.

## 2. KẾT QUẢ

- File Word 58 trang. Bản học viên lưu lúc 15:56 đã là 58 trang (Chương 3 ngắn đi một trang); đổi tên không làm đổi số trang.
- Không còn chữ "nối gốc" trong file Word; 9 phương trình và 5 đoạn có chỉ số dưới còn nguyên; ảnh Hình 4.2 trong file đúng
  là ảnh mới (so mã băm).

## 3. KIỂM CHỨNG

- `kiem_sua_tay_word.py`: trước khi đổi tên, sau khi đưa 5 chỗ sửa vào bản nháp: chữ khớp (mã 2). Sau khi sửa Word: chữ khớp
  (mã 2).
- `doi_chieu_chuong4.py`: bản chính 234 trên 234, địa chỉ ghim đúng; bản lưu 174 trên 174 (vẫn tên cũ).
- Thử lớp chặn trên bản sao file thật: `--chi 4 phu_luc --ghi-de` và ghép cả file đều dừng mã 3, in Chương 2 (8 phương trình,
  18 chỗ chỉ số) và Chương 4 (1 phương trình, 3 chỗ chỉ số).
- Toàn bộ test: 546 qua, 1 bỏ qua.

## 4. ĐIỂM CẦN BIẾT

- Hình 5.1 đến 5.4 vẽ lại cũng lấy số mới nhất (5 seed) chứ không chỉ đổi tên; Chương 5 chưa dùng các hình này.
- `doi_chung_do_thi.py` và `results/doi_chung_do_thi.json` vẫn ghi "nối gốc" trong phần mô tả nhóm (nội bộ, không vào báo
  cáo); không chạy lại.
- Từ nay chỉ còn ghép được `--chi phu_luc` và các chương không có phương trình; Chương 2 và 4 sửa bằng COM.

## 5. DỪNG LẠI VÀ HỎI

1. Mở Word đọc lại các chỗ có "nối câu" ở mục 4.3, 4.4 và Hình 4.2.
2. Push các commit mới (`6e507d9` và commit phiếu này) để địa chỉ Phụ lục trong báo cáo mở được?
