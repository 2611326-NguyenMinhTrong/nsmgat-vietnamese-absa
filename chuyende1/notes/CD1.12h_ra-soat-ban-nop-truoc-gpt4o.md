# PHIẾU BÀN GIAO — [CD1.12h] Rà soát bản nộp trước khi chạy GPT-4o

Ngày 16/10/2026. Học viên yêu cầu: trước khi chạy GPT-4o, rà soát kỹ file nộp xem còn sai sót không, có dư thừa không, và các
bằng chứng để phát triển đề tài có thật sự khả thi và có giá trị không.

## 1. ĐÃ LÀM GÌ

Ba lớp rà soát trên bản chính (`chuyende1/report/nhap_rut_gon/` và file Word ghép từ đó):

1. Chạy lại mọi công cụ kiểm: `doi_chieu_chuong4.py` (kể cả `--do-cat`, `--do-mau-so`), `doi_chieu_ban_goc.py kiem`,
   `doi_chieu_ban_rut_gon.py`, cả bộ test.
2. Đọc toàn văn các trang đầu, sáu chương và ba phụ lục; quét bằng mã văn phong, tham chiếu chéo (bảng, hình, mục, công
   thức) và chữ viết tắt; tự đối chiếu những con số mà công cụ chưa kiểm.
3. Đọc lại phần bằng chứng ở Chương 3, 4 và Phụ lục C, tính thêm một phép đo mức tập trung lỗi trên toàn tập kiểm tra.

Đã sửa bốn lỗi (bản nháp, rồi ghép lại file Word, sao lưu `..._rutgon.20261016-034420.docx.bak`):

| Chỗ | Sai | Sửa thành |
|---|---|---|
| Chương 1, mục 1.2 | "Trong 13 công trình tiếng Việt đã đọc": sót khi rút khảo sát còn 34 công trình (CD1.12g) | 12 |
| Chương 1, mục 1.2 | "các công trình trong phạm vi khảo sát mới làm việc ở mức câu hoặc mức văn bản": trái với chính trích dẫn SenticNet (mức từ) và với mục 3.7 | "các công trình theo hướng này ... ở mức câu, mức văn bản hoặc mức từ (mục 3.7)" |
| Chương 1, mục 1.3 | "kết quả đo ... cho năm mô hình": phần tóm tắt và Chương 4 nói sáu mô hình | sáu |
| Chương 2, mục 2.4 | "được bàn ở mục 4.4": phần bàn đầy đủ nằm ở mục 4.3, mục 4.4 chỉ nhắc lại | "mục 4.3 và 4.4" |

## 2. KẾT QUẢ KIỂM

- Văn phong: không còn gạch ngang dài, chữ đậm, dấu nháy mã, mã bước plan hay tên công cụ AI trong bản chính. Còn đúng một
  dòng [TODO] (kết quả GPT-4o, cuối mục 4.4).
- Tham chiếu chéo: mọi "Bảng", "Hình", "mục", "công thức" đều trỏ tới chỗ có thật (21 bảng, 2 hình, 9 công thức).
- Con số: công cụ đối chiếu 239 trên 239. Những số công cụ chưa kiểm đã được đối chiếu tay:
  - Chương 1: 86,7 % và 45,1 % khớp tập kiểm tra (1.897 và 986 trong 2.187 bình luận); câu "pin 4500 nhưng nhanh hết quá"
    có trong dữ liệu; 80,77 đến 84,72 %, 84,46 % và khoảng 86,9 % khớp Bảng 3.2.
  - Mục 4.1.1: năm người gán nhãn, sáu vòng huấn luyện mỗi vòng 200 bình luận, ngưỡng trên 80 %: khớp bài gốc UIT-ViSFD.
  - Mục 4.1.2: 1.223 bình luận có từ phủ định (55,9 %), 500 chỉ dùng dạng viết tắt (40,9 %, bài ghi "khoảng 41 %"), "ko" 570
    lần và "k" 384 lần, không lần nào được gán phó từ: khớp khi đếm lại.
  - Mục 4.2 và 4.3: 110 mẫu bị cắt (1,64 %), 0,079 % và 2,50 %: khớp khi đo lại bằng `--do-cat` và `--do-mau-so`.
- `--do-cat` báo hai câu "không thấy" (tỉ lệ cắt ở tập huấn luyện 1,65 % và tập phát triển 1,06 %): hai câu này chỉ có ở
  bản đầy đủ, bản chính đã lược; không phải lỗi của bản chính.

## 3. CÒN LẠI CHƯA SỬA, CẦN HỌC VIÊN QUYẾT

Sai sót nhỏ:
- Bìa: tháng còn để trống; dòng học viên có hai dấu gạch dài ("NGUYỄN MINH TRỘNG — MSHV 2611326 — Khoá 2026A") (E3).
- CPU (3 lần) và GPU (7 lần) được dùng mà không có trong danh sách chữ viết tắt (bỏ ra ngày 13/10 để danh sách vừa một trang).
- Tên Bảng A.2 là "các công trình không được bàn chi tiết ở Chương 3", nhưng 6 trong 11 hàng là công trình Chương 3 có bàn:
  Moore và Barnes, Thin và cộng sự, Socher và cộng sự, Sentic GCN-BERT, R-GAT, Tran và Phan.

Dư thừa (cắt được mà không mất nội dung):
- Đoạn "Độ nhất quán của nhãn" có hai lần gần như nguyên văn: mục 4.1.2 và Phụ lục B. Giữ bản đầy đủ ở Phụ lục B, mục 4.1.2
  còn hai câu (kappa 0,733 và ba lưu ý tóm tắt): bớt khoảng nửa trang.
- Bảng A.2: sáu hàng nêu trên lặp số liệu đã có trong Chương 3 hoặc Bảng 3.2 (ví dụ 86,92 % của Sentic GCN-BERT, 9.778 lần
  "không" của Tran và Phan, 46 % và 6 % của R-GAT). Bỏ sáu hàng thì tên bảng cũng đúng trở lại.
- Mục 1.2 nhắc lại các con số của Bảng 3.2 và của Moore và Barnes; có thể chỉ giữ câu nhận định, bỏ con số (khoảng 3 dòng).

## 4. BẰNG CHỨNG CHO HƯỚNG ĐỀ TÀI: ĐÁNH GIÁ

### Điểm đứng vững

1. Lỗi tập trung ở các câu có hiện tượng. Phép đo mới trên toàn tập kiểm tra (6.722 mẫu, trung bình ba hạt giống, từ khoá
   lấy đúng danh sách của bước lọc tập chẩn đoán, xét theo cả bình luận):

   | Bình luận chứa | Số mẫu | Tỉ lệ sai của PhoBERT | Phần trong tổng số lỗi của PhoBERT |
   |---|---|---|---|
   | Không có từ khoá | 2.454 (36,5 %) | 5,4 % | 24,1 % |
   | Chỉ từ phủ định | 2.438 (36,3 %) | 8,3 % | 37,0 % |
   | Chỉ từ chuyển ý | 592 (8,8 %) | 10,9 % | 11,8 % |
   | Cả hai | 1.238 (18,4 %) | 12,0 % | 27,2 % |

   Mẫu có từ khoá chiếm 63,5 % tập nhưng chiếm 75,9 % số lỗi, tỉ lệ sai cao gấp 1,5 đến 2,2 lần. Sentic-GCN cho tỉ lệ gần như vậy.
2. Nhóm có cả phủ định lẫn chuyển ý khó một cách vững: thấp hơn nhóm thường 15,8 đến 19,6 điểm ở cả sáu mô hình, và vẫn
   thấp hơn có ý nghĩa ở cả năm mô hình học khi chỉ giữ mẫu người chú thích đồng ý với nhãn gốc (PhoBERT thấp hơn 12,6 điểm,
   p bằng 0,002).
3. Các cách đưa cấu trúc và tri thức hiện có (ASGCN, Sentic-GCN) không thu hẹp khoảng cách đó ở nhóm nào (Bảng C.6): chỗ
   trống mà đề tài nhắm tới chưa có ai lấp.
4. Có hai phát hiện kỹ thuật dùng ngay được cho mô hình đề xuất: 41 % bình luận có phủ định chỉ dùng dạng viết tắt mà bộ gán
   từ loại không nhận ra, nên luật phủ định phải dựa vào từ vựng chứ không dựa vào từ loại; và hơn một nửa đồ thị cú pháp bị
   chia cắt, nối gốc lấy lại khoảng 69 % phần ASGCN thua PhoBERT.
5. Khả thi về hạ tầng: toàn bộ đường đi từ dữ liệu, phân tích cú pháp, đồ thị, sáu mô hình, tập chẩn đoán tới kiểm định đã
   chạy và tái lập được; một lần huấn luyện mô hình dùng PhoBERT mất khoảng một giờ trên GPU T4 miễn phí; mô hình đồ thị chỉ
   chậm hơn PhoBERT khoảng 30 % khi suy luận.

### Điểm yếu và rủi ro

1. Phủ định đứng một mình chưa có bằng chứng. Nhóm phủ định không thấp hơn nhóm thường có ý nghĩa về accuracy ở mô hình học
   nào (p từ 0,199 đến 0,726); trên tập con đồng ý với nhãn gốc, PhoBERT chỉ thấp hơn 0,4 điểm. Tên đề tài đặt phủ định
   ngang chuyển ý, nhưng số liệu đỡ chuyển ý và tổ hợp hai hiện tượng mạnh hơn nhiều.
2. Nhãn gốc nhiễu đúng ở chỗ đề tài nhắm tới. Người chú thích không đồng ý với nhãn gốc ở 27,1 % nhóm chuyển ý và 34,5 % nhóm
   cả hai. Bỏ các mẫu đó thì khoảng cách của nhóm chuyển ý ở PhoBERT và ba mô hình đồ thị không còn ý nghĩa (p từ 0,050 đến
   0,146). Một mô hình tốt hơn trên các hiện tượng này có thể không thể hiện được trên nhãn chính thức của tập kiểm tra.
3. Chưa có bằng chứng rằng xử lý tường minh bằng luật sẽ thắng PhoBERT. Thêm cấu trúc lên PhoBERT theo cách đã biết chưa cho
   lợi ích đo được. Phép thăm dò trần cải tiến (mục 5.4, gói CD1.11 của plan) chính là để trả lời câu này, và chưa làm.
4. Mẫu nhỏ: nhóm cả hai có 84 mẫu (55 mẫu sau khi bỏ mẫu không đồng ý với nhãn gốc); nhãn hiện tượng do một người gán;
   kappa 0,733 là cận trên; các phép so chưa hiệu chỉnh cho so sánh nhiều lần.
5. Tri thức cảm xúc có sẵn cho tiếng Việt yếu: VietSentiWordNet phủ 8,7 % số lượt từ; SenticNet bản tiếng Việt phủ 52,4 % nhưng
   lẫn nhiều lượt tra trùng; cả hai đều làm công thức của Sentic-GCN chia cho 0 (C9). Thành phần "ký hiệu" của mô hình đề
   xuất phải tự xây nguồn tri thức.
6. Mức cải thiện tối đa trên toàn tập là có hạn. Nếu mọi mẫu có từ khoá chỉ sai với tỉ lệ của mẫu không có từ khoá (5,4 %),
   PhoBERT còn khoảng 361 lỗi thay vì 547, accuracy từ 91,86 % lên khoảng 94,6 %. Đây là trần lạc quan: có từ khoá chưa có
   nghĩa là có hiện tượng (ở tập chẩn đoán chỉ 46 % mẫu của kho phủ định thật sự thuộc nhóm phủ định hoặc cả hai), và các
   bình luận có từ khoá cũng thường dài và có nhiều khía cạnh trái nhãn. Mức cải thiện thật trên toàn tập nhiều khả năng
   nhỏ hơn một điểm; giá trị của đề tài nên được đo trên tập chẩn đoán và ở khả năng giải thích, không ở accuracy toàn tập.

### Kết luận

Hướng đề tài khả thi và có giá trị, với hai điều chỉnh về cách đặt vấn đề: trọng tâm có bằng chứng là chuyển ý và tổ hợp
phủ định với chuyển ý, còn phủ định đứng một mình chưa có; và giá trị cần được đo trên tập chẩn đoán đã làm sạch nhãn, vì
nhãn gốc nhiễu đúng ở các hiện tượng đó. Bằng chứng còn thiếu quan trọng nhất là phép thăm dò trần cải tiến bằng luật
(mục 5.4).

## 5. ĐIỂM NỐI VỚI STEP SAU

- Không có gì trong rà soát này chặn việc chạy GPT-4o.
- Đề nghị làm sớm phép thăm dò ở mục 5.4: dùng ngay dự đoán đã có, không cần huấn luyện. Ví dụ: với mẫu có chuyển ý, áp luật
  "cảm xúc theo vế sau từ chuyển ý" cho đúng khía cạnh ở vế sau, rồi đo trên tập chẩn đoán xem luật đúng bao nhiêu khi PhoBERT
  sai và sai bao nhiêu khi PhoBERT đúng.
- Người chú thích thứ hai cho tập chẩn đoán (A8, C4): làm rủi ro 2 và 4 nhỏ đi nhiều.

## 6. KIỂM CHỨNG

```
doi_chieu_chuong4.py                 239 chỗ, khớp 239 (trước và sau khi sửa)
doi_chieu_chuong4.py --do-cat --do-mau-so   thêm 4 chỗ; 2 "không thấy" là câu chỉ có ở bản đầy đủ
doi_chieu_ban_goc.py kiem            Chương 2: 7/7; Chương 3: 82, cần xem tay 0; Chương 1: 5 cần xem tay, đã đối chiếu tay (mục 2);
                                     Chương 4: 32 cần xem tay, đều là số của chuyên đề đứng cạnh trích dẫn, đã đối chiếu (mục 2)
quét văn phong, tham chiếu chéo        0 lỗi; 1 dòng [TODO]
Word                                  68 trang sau khi sửa
```

## 7. DỪNG LẠI VÀ HỎI

1. Có cắt hai chỗ dư thừa ở mục 3 (đoạn độ nhất quán ở mục 4.1.2, sáu hàng của Bảng A.2) không?
2. Có thêm CPU, GPU vào danh sách chữ viết tắt không (có thể làm danh sách sang trang thứ hai)?
3. Có làm phép thăm dò ở mục 5.4 trước khi viết Chương 5 không? Có hỏi cô về việc đặt trọng tâm vào chuyển ý không?
