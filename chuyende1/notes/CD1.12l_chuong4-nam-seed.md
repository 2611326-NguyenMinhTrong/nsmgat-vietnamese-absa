# PHIẾU BÀN GIAO — [CD1.12l] Chuyển Chương 4 bản chính sang 5 seed và thêm thí nghiệm đối chứng

Ngày 17/10/2026. Học viên chọn cách (b) ở phiếu CD1.12k (chuyển cả Chương 4 sang 5 seed), chạy thêm seed 7 và 123 cho
từ điển và BiLSTM trên Kaggle (CPU), xác nhận không tự chỉnh định dạng trong Chương 4 và Phụ lục, và bảo đưa thí nghiệm
đối chứng vào mục 4.4.

## 1. ĐÃ LÀM GÌ

1. Kiểm 4 lần chạy mới (từ điển, BiLSTM, seed 7 và 123): chạy CPU, số tham số, mã cấu hình, thứ tự mẫu đều đúng; đưa vào
   `results/` không ghi đè. Cả sáu mô hình đủ 5 seed.
2. Công cụ: `compare_baselines.SEEDS` thành (42, 1337, 2024, 7, 123), thêm `SEEDS_BA` cho bản lưu. Chụp kết quả 3 seed cũ ở
   `results/ba_seed/` (compare_baselines, error_analysis, diagnostic_eval). Sinh lại ba file đó, Hình 4.2, ba bảng trong
   `chuyende1/tables/`. `doi_chung_do_thi.py` thêm nhóm một gốc / nhiều gốc và cặp nối gốc trừ ASGCN.
3. `doi_chieu_chuong4.py`: bản chính dùng 5 seed; bản lưu (`--ban day_du`) dùng 3 seed và đọc `results/ba_seed/`. Thêm
   `so_lieu_doi_chung` kiểm Bảng 4.5 mới và mọi số đi kèm; các câu viết lại có chỗ kiểm dựng từ số liệu (ví dụ câu kể hiệu
   số theo từng seed sinh từ chính hiệu số). Thời gian huấn luyện ở Bảng 4.7 lấy ba seed đầu.
4. Bản nháp: mục 4.2 (5 seed, nguồn của từng seed, phép thử đổi nền tảng, phép hoán vị seed), 4.3 (mô tả ASGCN đúng theo
   GAP-040, Bảng 4.2 dòng bậc 4, hai mô hình đối chứng), 4.4 (mọi số, Bảng 4.5 đối chứng mới, đoạn "đồ thị bị chia cắt" viết
   lại theo phép tách nhóm), 4.5, 4.6, 4.7, Phụ lục C (Bảng C.2 thêm hai cột seed), phần tóm tắt, Chương 1, mục 2.6.
   Đánh số lại Bảng 4.5 đến 4.9 thành 4.6 đến 4.10.
5. File Word: `nhap_chuong_vao_docx.py` thêm cờ `--chi`; ghép riêng Chương 4 và Phụ lục (`--chi 4 phu_luc --ghi-de`), giữ
   nguyên Chương 2 có phương trình Word, trang đầu, tài liệu tham khảo. Bảy chỗ ngoài Chương 4 (phần tóm tắt 4, Chương 1 hai,
   mục 2.6 một) sửa thẳng trong Word bằng COM. Chạy thử trên bản sao trước mỗi bước. Sao lưu:
   `..._rutgon.20261017-015603.docx.bak` (trước khi ghép), `..._rutgon.20261017-015743.docx.bak` (trước câu Chương 1).

## 2. KẾT QUẢ CHÍNH VỚI 5 SEED

| Mô hình | Accuracy | Macro-F1 |
|---|---|---|
| Từ điển cảm xúc | 74,68 ± 0,02 | 52,39 ± 0,02 |
| BiLSTM | 86,38 ± 0,44 | 79,47 ± 0,75 |
| PhoBERT tinh chỉnh | 91,79 ± 0,19 | 86,70 ± 0,26 |
| ASGCN | 91,46 ± 0,33 | 85,82 ± 1,02 |
| ASGCN nối gốc | 91,70 ± 0,17 | 86,41 ± 0,32 |
| Sentic-GCN | 91,59 ± 0,31 | 86,70 ± 0,34 |

Kết luận đổi so với bản 3 seed: PhoBERT không còn đứng đầu cả hai độ đo (bằng Sentic-GCN về macro-F1); PhoBERT không còn
hơn Sentic-GCN có ý nghĩa về accuracy (p 0,158); Sentic-GCN đạt 75,2 % ở nhóm cả hai; về macro-F1 ở nhóm phủ định chỉ còn
BiLSTM thấp hơn có ý nghĩa; trên tập con đồng ý, BiLSTM ở nhóm cả hai không còn có ý nghĩa (p 0,066). Kết luận chính giữ
nguyên: không mô hình đồ thị nào hơn PhoBERT có ý nghĩa; nhóm cả hai khó nhất ở mọi mô hình (thấp hơn 15,0 đến 17,6 điểm).

## 3. KIỂM CHỨNG

- `doi_chieu_chuong4.py`: bản chính 244 trên 244 (thêm 23 chỗ kiểm cho phần mới); bản lưu 174 trên 174.
- `kiem_sua_tay_word.py`: mã 2 (chữ của file Word khớp bản nháp, có 6 phương trình Word nên không ghép cả file).
- Bản chạy thử ghép riêng: chỉ Chương 4 (76 đoạn) và Phụ lục (4 đoạn) đổi, 6 phương trình còn nguyên.
- File Word 69 trang, 22 bảng; danh sách bảng có Bảng 4.5; Hình 4.2 trong file đúng là ảnh mới (so mã băm).
- Toàn bộ test: 543 qua (thêm 2 test cho `--chi`; sửa test ghi cứng 3 seed và số bảng cũ).
- Công cụ đối chiếu bắt được 5 lỗi số do Claude viết sai lúc đầu (5,50 thay vì 5,49; 18 thay vì 17 điểm; ba hiệu số trên
  tập con; hai câu dưới Bảng C.5; "p bằng 0,001" thay vì "p nhỏ hơn 0,001"), đã sửa.

## 4. ĐIỂM CẦN BIẾT

- Hai seed sau chạy trên nền tảng khác ba seed đầu; chương ghi rõ ở mục 4.2 kèm phép thử đổi nền tảng (3,48 % so với 4,48 %).
- Từ nay ghép file Word chỉ được dùng `--chi` cho đúng phần đổi, và chỉ khi học viên không chỉnh định dạng ở phần đó.
- Bản lưu (bản đầy đủ) giữ 3 seed; muốn kiểm nó phải có `results/ba_seed/`.

## 5. DỪNG LẠI VÀ HỎI

1. Mở file Word đọc lại mục 4.4 (đoạn thí nghiệm đối chứng và Bảng 4.5) và mục 4.7.
2. Push các commit đang ở máy?
3. Ba việc còn treo: 34 đoạn kiểu "Nhãn. Nội dung"; trang bìa "ĐỀ CƯƠNG THẠC SĨ"; chạy GPT-4o (mục 4.4 còn một dòng TODO).

## 6. GHI CHÚ SAU KHI TRAO ĐỔI *(điền sau)*
