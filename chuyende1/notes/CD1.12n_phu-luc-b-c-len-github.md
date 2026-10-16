# PHIẾU BÀN GIAO — [CD1.12n] Phụ lục B và C không in kèm, chuyển lên GitHub; bỏ Bảng A.2

Ngày 17/10/2026. Học viên bảo bỏ phần lặp trong Phụ lục (đoạn độ nhất quán ở Phụ lục B, sáu hàng Bảng A.2). Đối chiếu từng
số cho thấy hai chỗ đó không lặp hoàn toàn (GAP-041). Học viên đề xuất chuyển cả phụ lục lên GitHub; Claude nêu các hệ quả và
đề xuất giữ Bảng A.1 (bằng chứng của Chương 3). Học viên chọn: "làm theo đề xuất của bạn để vẫn có đầy đủ bằng chứng cho
khảo sát".

## 1. ĐÃ LÀM GÌ

1. Tạo `chuyende1/phu_luc/PhuLuc_B_C.md` (có push): Phụ lục B nguyên văn đầy đủ (lấy từ bản sao lưu trước khi rút gọn đoạn
   độ nhất quán) và Phụ lục C (Bảng C.1 đến C.6, đoạn dưới Bảng C.5). Giữ nguyên chữ cái và số bảng để các chỗ dẫn "Bảng C.4"
   trong Chương 4 vẫn đúng. Thêm đầu file (tên đề tài, học viên, GVHD, ghi chú số mục là số trong báo cáo) và một tài liệu
   tham khảo (Cohen 1960, trích dẫn đổi thành [1]). Commit `a4e8889`.
2. Bản nháp `nhap_rut_gon/PhuLuc.md`: chỉ còn Phụ lục A (Bảng A.1, 34 công trình); bỏ Bảng A.2 và đoạn dẫn của nó; thêm đoạn
   đầu phần Phụ lục ghi Phụ lục B, C không in kèm và địa chỉ
   `https://github.com/2611326-NguyenMinhTrong/nsmgat-vietnamese-absa/blob/a4e8889/chuyende1/phu_luc/PhuLuc_B_C.md`
   (dòng canh giữa riêng), kèm một câu nói địa chỉ trỏ vào phiên bản cố định.
3. Bản nháp Chương 4, mục 4.1.2: câu "Quy trình đầy đủ ở Phụ lục B; ..." thành "Quy trình đầy đủ ở Phụ lục B. Phụ lục B và
   Phụ lục C không in kèm báo cáo mà được lưu cùng mã nguồn của đề tài, địa chỉ ghi ở đầu phần Phụ lục. Phần dưới đây ...".
   Sáu chỗ dẫn Bảng C.1 đến C.6 giữ nguyên.
4. `scripts/doi_chieu_chuong4.py`: bản chính đọc thêm file phụ lục trực tuyến; thêm `kiem_ghim_phu_luc`: địa chỉ trong
   `PhuLuc.md` phải ghim một commit, file ở commit đó phải giống hệt file trên đĩa (lệch thì báo lỗi, mã thoát 1); commit chưa
   push thì chỉ in lưu ý. Thêm 2 test.
5. File Word: ghép riêng Chương 4 và Phụ lục (`--chi 4 phu_luc --ghi-de`), cập nhật mục lục và danh sách bảng. Sao lưu
   `..._rutgon.20261017-030831.docx.bak`. Lưu lần cuối 03:08:45.
6. Sổ sách: `chuyende1/MODULE.md` thêm dòng thư mục `phu_luc/`; GAP-041 ghi hướng học viên chọn; ở máy: `SO_TAY_LENH.md` §11h,
   `VIEC_CAN_LAM.md` (lần 19, thêm câu hỏi vào E6), bản sao lưu nháp `nhap_rut_gon/sao_luu/20261017-phu-luc-truc-tuyen/`.

## 2. KẾT QUẢ

| | Trước | Sau |
|---|---|---|
| Tổng số trang file Word | 69 | 63 |
| Phần Phụ lục in kèm | 10 trang | 4 trang (đoạn dẫn địa chỉ và Bảng A.1) |
| Số bảng trong file Word | 22 | 15 (14 tên bảng trong danh sách) |
| Tài liệu tham khảo | 47 | 47 (hai công trình chỉ được trích ở phụ lục nằm trong Bảng A.1 nên vẫn còn) |

Thân bài (Chương 1 đến 6) không đổi độ dài.

## 3. KIỂM CHỨNG

- `doi_chieu_chuong4.py`: bản chính 244 trên 244 (đọc Chương 4, `PhuLuc.md`, `PhuLuc_B_C.md`, phần tóm tắt), địa chỉ ghim đúng,
  lưu ý "commit a4e8889 chưa có trên GitHub"; bản lưu 174 trên 174.
- `kiem_sua_tay_word.py` trước khi ghép, so với bản nháp trước hôm nay: chữ khớp (mã 2, chỉ vì 6 phương trình ở Chương 2), file
  Word không bị sửa từ lần lưu 02:35. Sau khi ghép: chữ khớp bản nháp mới, 6 phương trình còn nguyên.
- Chạy thử trên bản sao trước: chỉ câu ở 4.1.2 và phần Phụ lục đổi; các chương khác giữ nguyên.
- `nhap_chuong_vao_docx.py --chi-xem`: 47 tài liệu được trích, thứ tự số trích dẫn không đổi.
- Toàn bộ test: 545 qua, 1 bỏ qua.

## 4. ĐIỂM CẦN BIẾT

- Địa chỉ trong báo cáo chỉ mở được sau khi push commit `a4e8889`.
- Sửa `PhuLuc_B_C.md` về sau (ví dụ khi có số GPT-4o): commit, đổi mã commit trong `PhuLuc.md`, ghép lại phần Phụ lục vào Word,
  push. Công cụ đối chiếu báo lỗi nếu quên đổi mã.
- Đoạn độ nhất quán rút gọn (100 chữ) không còn dùng: Phụ lục B trên GitHub dùng nguyên văn đầy đủ, lặp một phần mục 4.1.2,
  vì file trực tuyến cần đọc được độc lập và không tính trang.
- Các con số chỉ có ở Bảng A.2 (ví dụ +3,8 điểm của Moore và Barnes, 71,4 % và 81,8 % của Socher và cộng sự) không còn trong
  báo cáo.
- Repo công khai vẫn có `chuyende1/survey/survey_matrix.csv` (48 công trình) và `khong_trinh_bay.csv`; báo cáo chỉ dẫn tới
  file phụ lục, không dẫn tới thư mục khảo sát.
- Quy định "khoảng 30 trang" có tính phụ lục hay không vẫn chưa rõ (E6). Nếu phụ lục không tính, việc chuyển này không giúp
  gì cho giới hạn trang.

## 5. DỪNG LẠI VÀ HỎI

1. Push hai commit mới (`a4e8889` và commit phiếu này) để địa chỉ trong báo cáo mở được?
2. Mở file Word xem đầu phần Phụ lục (trang in 49) và câu ở mục 4.1.2.
3. Phần thân vẫn 43 trang so với 31 của bản mẫu; muốn rút tiếp thì chọn mức cắt cho Chương 4 (phiếu CD1.12m).
