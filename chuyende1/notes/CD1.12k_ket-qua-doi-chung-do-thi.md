# PHIẾU BÀN GIAO — [CD1.12k] Kết quả 17 lần chạy đối chứng trên Kaggle và kiểm định 5 seed

Ngày 16/10/2026. Học viên chạy xong `notebooks/kaggle_doi_chung_do_thi.ipynb` (một phiên, 9,06 giờ, hai Tesla T4, mã
ở commit `a9eab5c`), đặt `ket_qua.zip` vào `data/cache/kaggle_doi_chung/`, báo hai dòng kiểm của ô cuối: PhoBERT seed 42
Colab so với Kaggle khác 234 trên 6.722 dự đoán (3,48 %); số tham số của mô hình không GCN đúng bằng PhoBERT.

## 1. ĐÃ LÀM GÌ

1. Kiểm 17 lần chạy trước khi dùng: cả 17 ghi `xong`; mã cấu hình tính lại từ config trong repo khớp cả 17 (cách tính
   này cũng tính lại đúng mã của 12 lần chạy cũ trên Colab); số tham số đúng; thứ tự 6.722 uid và nhãn thật khớp
   `visfd_test.jsonl`; accuracy tính lại từ dự đoán khớp `metrics.json`; không file nào chứa tên tài khoản Kaggle.
2. Chép vào `results/<exp>/seed<N>/` (metrics, dự đoán) và `logs/<exp>/seed<N>.log`, chỉ tạo mới, có chặn ghi đè;
   `git diff` trên các file đã theo dõi trống. Các công cụ cũ chỉ đọc seed 42, 1337, 2024 nên không bảng, hình nào đổi.
3. Viết `scripts/doi_chung_do_thi.py` (7 test trong `tests/test_doi_chung_do_thi.py`), dùng lại hàm bootstrap của
   `compare_baselines.py`, thêm phép hoán vị trên điểm từng seed. Kết quả ở `results/doi_chung_do_thi.json`.
4. Kiểm thêm: PhoBERT seed 42 chạy trên Colab và trên Kaggle, chấm theo từng nhóm.

## 2. KẾT QUẢ TRÊN TOÀN TẬP KIỂM TRA

Macro-F1 (%) từng seed, theo thứ tự 42, 1337, 2024, 7, 123:

| Mô hình | Từng seed | Trung bình |
|---|---|---|
| PhoBERT (fp16) | 86,49 · 86,65 · 86,77 · 86,48 · 87,10 | 86,70 |
| PhoBERT fp32 | 87,18 · 86,80 · 87,09 | 87,02 |
| Gộp attention, không GCN | 86,36 · 86,13 · 86,40 · 86,41 · 86,68 | 86,40 |
| ASGCN | 86,69 · 85,14 · 84,47 · 86,87 · 85,93 | 85,82 |
| ASGCN nối gốc | 86,36 · 85,94 · 86,49 · 86,83 · 86,42 | 86,41 |
| Sentic-GCN | 86,28 · 86,40 · 86,82 · 86,96 · 87,05 | 86,70 |

Tách từng thành phần (hiệu số macro-F1, điểm phần trăm):

| Bước | Hiệu số | p bootstrap | p hoán vị seed |
|---|---|---|---|
| Tắt fp16 (PhoBERT fp32 trừ PhoBERT) | +0,32 | 0,117 | 0,107 |
| Đổi cách đọc ra (không GCN trừ PhoBERT fp32) | **−0,63** | 0,007 | 0,018 |
| Thêm GCN cây phụ thuộc (ASGCN trừ không GCN) | −0,58 | 0,010 | 0,310 |
| Thêm GCN cây nối gốc | +0,01 | 0,922 | 0,921 |
| Thêm GCN trọng số cảm xúc (Sentic-GCN) | +0,31 | 0,109 | 0,119 |
| ASGCN trừ PhoBERT, 5 seed (Bảng 4.4 ghi −1,21 với 3 seed) | −0,88 | < 0,001 | 0,111 |
| ASGCN nối gốc trừ PhoBERT, 5 seed (Bảng 4.4: −0,38) | −0,29 | 0,222 | 0,159 |
| Sentic-GCN trừ PhoBERT, 5 seed (Bảng 4.4: −0,14) | +0,00 | 0,990 | 1,000 |

Đọc:

- **GAP-040 được xác nhận bằng số.** Việc đổi cách đọc ra, từ token `<s>` sang gộp attention theo khía cạnh, làm giảm
  0,63 điểm. Đây là kết quả duy nhất có ý nghĩa ở cả hai phép kiểm định. Phần "đồ thị thua PhoBERT" ở báo cáo hiện tại
  phần lớn là phần này, không phải GCN.
- Thêm GCN lên trên cùng cách đọc ra: cây phụ thuộc thô làm giảm 0,58 điểm (có ý nghĩa ở bootstrap, không ở hoán vị seed
  vì ASGCN dao động mạnh giữa các seed); cây nối gốc không đổi gì; trọng số cảm xúc tăng 0,31 điểm, không có ý nghĩa.
- Với 5 seed, kết luận của Bảng 4.4 giữ nguyên chiều; khoảng thua của ASGCN thu từ 1,21 xuống 0,88 điểm.

## 3. ĐỐI CHIẾU VỚI TIÊU CHÍ "ĐỒ THỊ CÓ ÍCH" (phiếu CD1.12j mục 8)

Script đếm 4 chỗ ĐẠT theo đúng tiêu chí đã viết (hiệu số dương, p bootstrap < 0,05, mô hình đồ thị so với đối chứng
không đồ thị, ở bất kỳ nhóm nào), cả 4 đều là Sentic-GCN:

| # | So sánh | Nhóm | Hiệu số | p bootstrap | p hoán vị seed | So cùng nhóm với PhoBERT fp32 |
|---|---|---|---|---|---|---|
| 1 | Sentic-GCN trừ không GCN | Bình luận trái cảm xúc, macro-F1 | +0,63 | 0,006 | 0,063 | Sentic-GCN −0,17 (p 0,558) |
| 2 | như trên | như trên, accuracy | +0,45 | 0,014 | | |
| 3 | Sentic-GCN trừ PhoBERT fp16 | Chẩn đoán: có phủ định, macro-F1 | +2,71 | 0,035 | 0,079 | Sentic-GCN −0,73 (p 0,578) |
| 4 | Sentic-GCN trừ PhoBERT fp16 | Chẩn đoán: có chuyển ý, macro-F1 | +2,08 | 0,047 | 0,183 | Sentic-GCN +0,61 (p 0,591) |

Đánh giá của Claude: **về hình thức tiêu chí đạt, nhưng chưa phải bằng chứng đồ thị có ích**, vì bốn lý do:

1. Tiêu chí do Claude viết ngày 16/10 có hai lỗ: không hiệu chỉnh so nhiều lần, và cho phép so với PhoBERT fp16 (vốn còn
   lẫn biến fp16). Script chạy 110 phép so, trong đó 90 phép là mô hình đồ thị so với đối chứng; nếu đồ thị hoàn toàn
   không có tác dụng, chỉ do ngẫu nhiên vẫn kỳ vọng khoảng 2 chỗ "dương và p < 0,05" (90 × 0,025, các phép không độc lập
   nên đây chỉ là cỡ). Quan sát được 4 chỗ, trong đó 2 chỗ là cùng một phép so đo bằng hai độ đo. Hiệu chỉnh Holm cho 90
   phép (ngưỡng nhỏ nhất 0,05/90, khoảng 0,00056) thì không chỗ nào còn đạt.
2. Chỗ 3 và 4 biến mất khi so với PhoBERT cùng độ chính xác (fp32). Trên các nhóm chẩn đoán nhỏ (203 và 265 mẫu), cùng
   seed 42, cùng config, chỉ đổi Colab sang Kaggle mà PhoBERT đã lệch +1,22 điểm ở nhóm có phủ định và +3,41 điểm ở nhóm
   có chuyển ý. Hiệu số 2 đến 3 điểm ở các nhóm này nằm trong dao động của nền tảng.
3. Chỗ 1 và 2 là ứng viên thật nhất: cùng cách đọc ra, cùng fp32, 5 với 5 seed. Nhưng phép hoán vị seed cho p 0,063,
   tức chưa vượt được dao động do huấn luyện lại; và Sentic-GCN chỉ lấy lại phần mà cách đọc ra đã làm mất, không vượt
   PhoBERT fp32 (−0,17 điểm).
4. Điểm cảm xúc của Sentic-GCN lấy từ nhãn tập huấn luyện (mục 4.3), nên nếu có lợi thì một phần có thể là thông tin nhãn
   đi vòng vào trọng số cạnh, không hẳn là "đồ thị".

Kết luận đề xuất: trong thiết lập của chuyên đề, **chưa chứng minh được đồ thị có ích**; có một tín hiệu yếu, chưa vững,
là GCN có trọng số cảm xúc giúp ở bình luận trái cảm xúc so với cùng đầu gộp không GCN. Học viên quyết có dùng cách đọc
này hay giữ đúng chữ của tiêu chí (mục 7).

## 4. HAI PHÁT HIỆN PHỤ

- **Đổi nền tảng gần bằng đổi seed.** Cùng seed 42, cùng config, cùng mã cấu hình `1d4507b4e2e0`: Colab và Kaggle khác
  3,48 % dự đoán (ba seed PhoBERT khác nhau trung bình 4,49 %); macro-F1 86,49 so với 86,32. Gộp seed của hai nền tảng vào
  một trung bình là thêm dao động, nhưng chưa thấy lệch có hệ thống (hai seed PhoBERT trên Kaggle cho 86,48 và 87,10).
- **fp16 so với fp32 của PhoBERT:** trên toàn tập không khác có ý nghĩa (+0,32, p 0,117). Ở nhóm chẩn đoán có hiệu số lớn
  (+3,44 ở có phủ định, +4,68 ở cả hai, p bootstrap 0,002 và 0,007) nhưng ba lần chạy fp32 đều trên Kaggle, còn ba trong
  năm lần chạy fp16 trên Colab, nên chưa tách được fp16 khỏi nền tảng.

## 5. ẢNH HƯỞNG TỚI BÁO CÁO (chưa sửa gì)

Hai cách, học viên chọn:

- **(a) Giữ ba seed ở các bảng chính**, thêm một đoạn và một bảng nhỏ ở mục 4.4 về thí nghiệm đối chứng (bảng ở mục 2 của
  phiếu này), sửa lời văn theo GAP-040 ở mục 4.3, 4.4, 4.7, phần tóm tắt và Chương 1. Ít việc, các bảng khác không đổi.
- **(b) Chuyển cả Chương 4 sang 5 seed**: đổi Bảng 4.3, 4.4, 4.5, 4.8, 4.9, Phụ lục C, Hình 4.1, 4.2 và 239 chỗ công cụ đối
  chiếu đang kiểm; phải ghi rõ hai seed mới chạy trên nền tảng khác.

Claude đề xuất (a).

## 6. KIỂM CHỨNG

- `pytest tests/test_doi_chung_do_thi.py`: 7 test qua. Test đầu tiên bắt được một chỗ Claude tính sai (p nhỏ nhất của
  hoán vị 5 với 3 là 1/56, không phải 2/56), đã sửa cả docstring.
- Nhóm chẩn đoán gộp theo dấu hiệu khớp Bảng 4.7: có phủ định 203 = 119 + 84, có chuyển ý 265 = 181 + 84, cả hai 84.
- Nhóm trái cảm xúc: 3.592 mẫu, 986 bình luận, khớp `error_analysis.json` (`da_trai`).
- Macro-F1 ba seed cũ đọc qua script mới khớp Bảng 4.3 (PhoBERT 86,49, 86,65, 86,77).

## 7. DỪNG LẠI VÀ HỎI

1. Tiêu chí: coi là **chưa chứng minh được** (đề xuất của Claude, không thêm khảo sát vào báo cáo), hay giữ đúng chữ của
   tiêu chí đã viết (đạt, thêm các công trình hướng A và D của phiếu CD1.12j)?
2. Báo cáo: cách (a) hay (b) ở mục 5?
3. Push commit chứa 17 lần chạy, script và phiếu này?

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

**16/10/2026, học viên quyết câu 1:** coi là **chưa chứng minh được** đồ thị có ích, không thêm khảo sát (phiếu CD1.12j)
vào báo cáo. Câu 2 (cách a hay b) và câu 3 (push) chưa trả lời.

Cùng lúc học viên thấy phần TÓM TẮT của báo cáo "đưa số liệu vào hơi nhiều và hơi khó hiểu". Claude viết lại mục TÓM TẮT
trong `chuyende1/report/nhap_rut_gon/TrangDau.md` (bản cũ ở `nhap_rut_gon/sao_luu/20261016-tom-tat/`):

- Bỏ năm con số: 85,43 %, 86,50 %, p bằng 0,630, 71,31 % và kappa 0,733 (vẫn có ở thân bài). Giữ 34, 12, 11.122, 86,64 %,
  799 và khoảng 15,8 đến 19,6 điểm, đều có nguyên văn ở thân bài, không làm tròn số mới.
- Thêm ví dụ cho hai hiện tượng ("không tốt", "đẹp nhưng pin yếu"), viết ba câu hỏi thành câu hỏi thường.
- Bỏ câu "mỗi bậc thêm một thành phần" (sai theo GAP-040), thay bằng "từ đơn giản đến phức tạp".
- Kết quả về đồ thị viết thành một câu: "ASGCN và Sentic-GCN không tốt hơn PhoBERT".
- Công cụ đối chiếu sửa theo: bản chính 236 trên 236, bản lưu 174 trên 174.
- Chưa ghép vào file Word: lúc sửa, file `..._rutgon.docx` đang mở trong Word.
