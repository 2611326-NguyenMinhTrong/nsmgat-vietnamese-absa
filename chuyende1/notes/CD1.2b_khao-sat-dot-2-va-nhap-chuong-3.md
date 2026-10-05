# PHIẾU BÀN GIAO — [CD1.2b] Khảo sát đợt 2 và nháp Chương 3

> Tiếp sau [CD1.2_ha-tang-khao-sat.md](CD1.2_ha-tang-khao-sat.md), phiếu về hạ tầng khảo sát.
> Step này dùng ma trận 46 dòng đã đọc toàn văn để viết ra hai thứ: phân tích khoảng trống và
> bản nháp Chương 3.

**Ngày:** 05/10/2026 · **Step:** CD1.2b · **Ánh xạ plan gốc:** `[MỚI]` · **Không dùng GPU**

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `chuyende1/report/nhap/Chuong3_KhaoSat.md` | Tạo | Bản nháp Chương 3, đủ mười mục 3.1 đến 3.10, 45 tài liệu được trích. **Không lên GitHub**, đã chặn bằng `.gitignore` theo quyết định của học viên, xem mục 8 |
| `chuyende1/survey/gap_analysis.md` | Sửa | Bốn khoảng trống, mỗi cái trỏ về các dòng cụ thể của ma trận |
| `chuyende1/tables/bang_3_9_khao_sat.md` | Sửa | Sinh lại bằng công cụ: từ 1 lên 46 công trình |
| `chuyende1/survey/survey_matrix.csv` | Sửa | Dòng `Sentic-GCN`: thêm số của BERT thuần trong Bảng 3 của bài vào `ghi_chu` |
| `chuyende1/survey/survey_protocol.md` | Sửa | Mục 5: N₄ và N₅ bằng 46; sửa đoạn giải thích từ hai nhánh thành ba phần |
| `chuyende1/gaps/GAP-025_*.md` | Tạo | Phễu sàng lọc lệch một bài so với ma trận |
| `chuyende1/gaps/GAP-026_*.md` | Tạo | Nhật ký tìm kiếm là tra tên bài, không phải phễu sàng lọc. **Còn mở** |

Không sửa dòng mã nào. Không thêm script nào vào kho.

Lệnh đã chạy:

```bash
python scripts/survey_tools.py validate
python scripts/survey_tools.py stats
python scripts/survey_tools.py table -o chuyende1/tables/bang_3_9_khao_sat.md
python scripts/md_to_docx_ute.py chuyende1/report/nhap/Chuong3_KhaoSat.md <thư mục tạm>/thu_chuong3.docx
```

---

## 2. ĐỂ LÀM GÌ

- **Vấn đề:** ma trận khảo sát đã đủ 45 công trình từ ngày 22/09 nhưng vẫn là một bảng dữ
  liệu. Chưa có chữ nào của Chương 3, và `gap_analysis.md` còn là khung rỗng.
- **Sau step này:** có bản nháp Chương 3 đọc được từ đầu tới cuối, và bốn khoảng trống có bằng
  chứng, nối sang Chương 5.
- **Nếu bỏ step này:** tới tuần 12 viết Chương 5 sẽ không có "khoảng trống từ tài liệu" để đối
  chiếu với "hạn chế đo được", và định hướng Chuyên đề 2 chỉ còn một chân.

---

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1 Một khoảng trống được rút ra từ ma trận như thế nào

Lấy khoảng trống thứ nhất làm ví dụ chạy xuyên suốt. Nó không phải một nhận định viết ra rồi
đi tìm trích dẫn. Nó là kết quả của ba phép lọc trên ma trận:

| Bước | Lọc gì | Còn lại |
|---|---|---|
| 1 | `ho_phuong_phap = G4_do_thi` | 9 dòng |
| 2 | Bỏ `SocherRNTN2013` vì là mô hình mức câu, không phải mức khía cạnh | 8 dòng |
| 3 | Trong 8 dòng đó, `xu_ly_phu_dinh_chuyen_y = co` | **0 dòng** |

Rồi ghép với một dòng nằm ở nhóm khác: `MooreNegationTSA` đo được mức tụt 24 điểm F1 trên câu
có phủ định. Hai vế đứng cạnh nhau mới thành khoảng trống: hiện tượng có hại đã đo được, và
tám mô hình không có gì để xử lý nó.

Điều đáng học là **cột `xu_ly_phu_dinh_chuyen_y` được thiết kế từ ngày 27/08 chính là để phép
lọc này làm được.** Giao thức gọi đó là câu hỏi CH3, câu hỏi riêng của đề tài. Một khảo sát
ABSA thông thường không có cột này và sẽ không rút ra được khoảng trống này.

Ba khoảng trống còn lại rút ra theo cùng cách, từ các cột `ngon_ngu`, `co_dung_do_thi`,
`co_tri_thuc_ngoai`. Chi tiết ở `chuyende1/survey/gap_analysis.md`.

### 3.2 Bảng đáng giá nhất của chương là Bảng 3.2

Bảng này đặt bảy mô hình đồ thị cạnh nhau trên cùng một tập, miền nhà hàng của SemEval 2014,
theo số của chính từng bài:

| Mô hình | Đầu vào | Accuracy | Macro-F1 |
|---|---|---|---|
| ASGCN | GloVe | 80,77 | 72,02 |
| Sentic GCN | GloVe | 84,03 | 75,38 |
| SSEGCN, tốt nhất nhóm GloVe | GloVe | 84,72 | 77,51 |
| **BERT-SPC, không có đồ thị** | BERT | **84,46** | **76,98** |
| Sentic GCN-BERT | BERT | 86,92 | 81,03 |

Dòng in đậm là điều đáng chú ý: **một BERT ghép cặp câu, không dùng cú pháp, đã ngang mô hình
đồ thị tốt nhất dùng GloVe.** Ba năm cải tiến đồ thị từ 2019 tới 2022 đưa accuracy từ 80,77
lên 84,72, và việc đổi bộ mã hoá làm được ngần ấy trong một bước.

Điều này soi lại kết quả của chính ta ở Chương 4. Trên tiếng Anh, theo các bài báo, đồ thị
cộng BERT vẫn hơn BERT thuần khoảng 2 đến 3 điểm accuracy. Trên UIT-ViSFD, ba mô hình đồ thị
của ta không hơn `phobert`. Hai điều khác nhau cần nói ra khi so: các bài báo làm với khía
cạnh là cụm từ **nằm trong câu**, còn ta làm với nhóm khía cạnh; và cây phụ thuộc của ta vỡ ở
52,2 % dữ liệu. Chỗ lệch này là nội dung cho Chương 5, không phải Chương 3.

### 3.3 Hai chỗ số liệu của giao thức không đứng được

Viết mục 3.1 đòi hỏi kể lại "đã tìm tài liệu bằng cách nào". Tôi không chép số từ giao thức mà
đếm lại từ ma trận và từ nhật ký, và hai chỗ lộ ra.

**GAP-025, nhẹ.** Giao thức ghi 45 dòng gồm "24 qua phễu tìm kiếm và 21 hạt giống". Đếm lại:
25 dòng ghi là tìm mới, nhật ký chỉ giữ 24. Bài `VoZhang2015` không có truy vấn nào. Số "21"
nhiều khả năng là 45 trừ 24 chứ không được đếm.

**GAP-026, nặng hơn nhiều.** Trong 28 truy vấn của nhật ký, 26 là tra theo tên bài đã biết để
tìm bản gốc, chỉ 2 là từ khoá mở. Con số "258 kết quả, giữ lại 24" vì thế không phải một cái
phễu: không có 234 bài nào bị loại qua sàng lọc cả. Dàn ý yêu cầu vẽ sơ đồ phễu ở mục 3.1 và
gọi đó là dấu hiệu của khảo sát có phương pháp. **Vẽ ra thì sai sự thật.**

Phân biệt cho rõ hai thứ:

- **Nội dung ma trận đáng tin.** Từng bài đã đọc toàn văn từ bản gốc, số đã đối chiếu chéo.
- **Độ phủ thì không có bằng chứng.** Không biết còn bao nhiêu công trình liên quan chưa xét.

Bản nháp vì vậy viết mục 3.1 theo đúng thực tế và để một đoạn `[CẦN KIỂM]`. Mọi câu "chưa có
công trình nào" ở mục 3.10 đều giới hạn trong 45 công trình đã khảo sát.

### 3.4 46 dòng nhưng 45 công trình

`ATAE-LSTM` và `BiLSTM-attention` là cùng một bài báo, cùng đường dẫn. Hai dòng tồn tại vì hai
vai trò: công trình được khảo sát, và nguồn của baseline `bilstm`. Bản nháp đếm theo công
trình nên mọi con số là trên 45. `survey_tools.py stats` đếm theo dòng nên ra 46. Khi dán Bảng
3.9 vào Word phải gộp hai dòng này làm một.

### 3.5 Trích dẫn được đánh số bằng máy, và danh mục được đối chiếu với ma trận

Bản nháp viết trước với mã tạm dạng tên khoá, rồi một đoạn script tạm thay bằng số theo thứ tự
xuất hiện. Trước khi ghi file, script kiểm ba điều cho cả 45 mục: khoá phải là dòng
`da_doc_toan_van`, tiêu đề trong danh mục phải trùng nguyên văn cột `tieu_de`, và năm phải
trùng cột `nam`. Không có tài liệu nào trong danh mục mà ma trận không có.

Script đó nằm ở thư mục tạm, không vào kho, vì đánh số lại cho cả cuốn là việc của bước ghép
các chương ở tuần 13.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Làm step nào trước | CD1.2b | CD1.8a lọc ứng viên tập chẩn đoán | Bảng tiến độ xếp CD1.2b trước, và việc đóng dòng `Sentic-GCN` vừa xong nối thẳng vào đây. CD1.8a làm ngay sau |
| Bản nháp để ở đâu | `chuyende1/report/nhap/`, dạng Markdown | Sửa thẳng vào file Word | File Word là thứ học viên sửa tay, và công cụ dựng khung sẽ chặn nếu thấy đã sửa. Markdown đổi sang Word được bằng `md_to_docx_ute.py` |
| Commit bản nháp | **Chưa**, chờ học viên quyết | Commit cùng các file khác | Kho đang công khai. File Word của cuốn báo cáo vốn không đưa lên. Văn bản chương có lên GitHub hay không là việc của học viên |
| Sơ đồ phễu ở mục 3.1 | **Không vẽ** | Vẽ theo số có sẵn trong giao thức | GAP-026: 26 trong 28 truy vấn là tra tên bài. Vẽ phễu là mô tả một quá trình chưa từng xảy ra |
| Nguồn của từng câu mô tả mô hình | Chỉ từ `ghi_chu` của ma trận và từ bài Sentic-GCN vừa đọc lại | Viết từ hiểu biết chung về các mô hình | Quy tắc số 7. Một câu mô tả sai về bài của người khác là thứ hội đồng bắt được ngay |
| Bốn công trình lệch tiêu chí nhận | Nêu thẳng trong mục 3.1 | Im lặng | Hai bài không có thực nghiệm, một bài chỉ có thống kê, một bài chưa qua phản biện. Tự nêu ra thì là phương pháp, bị hỏi mới nói thì là sơ hở |
| Số khoảng trống | 4 | 3, đúng mức tối thiểu của plan | Khoảng trống thứ tư về tập đánh giá là thứ Chuyên đề 1 tự lấp bằng tập chẩn đoán, bỏ đi thì mất mối nối sang CD1.8 |
| Danh mục tài liệu | Tác giả, tên bài, nơi công bố, năm | Đủ số trang theo mẫu UTE | Ma trận không ghi số trang. Bổ sung khi lập danh mục chung ở tuần 13 |
| Văn phong | Không gạch ngang nối ý, không backtick, không in đậm, không mã step | Viết như phiếu bàn giao | Đây là văn bản gửi GVHD và hội đồng. Đã kiểm bằng máy: cả bốn đều bằng 0 |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Step kế tiếp là: **CD1.8a, lọc ứng viên tập chẩn đoán** từ tập test bằng từ khoá phủ định
  và chuyển ý, khoảng 800 câu ứng viên. Theo lịch đây là việc của tuần 5, đang trễ một tuần.
- Nó dùng lại từ step này: bảy kiểu từ đổi cực tính trong bài `TranValenceShiftersVN` (từ phủ
  định, giảm nhẹ, tăng cường, liên từ tương phản, câu nhân quả, câu điều kiện, câu hỏi) là
  điểm xuất phát có trích dẫn cho danh sách từ khoá. Mức kappa 0,66 đến 0,70 của
  `MooreNegationTSA` là mốc tham chiếu cho ngưỡng 0,70 của CD1.8d.
- Bảng "Đối chiếu với hạn chế đo được" cuối `gap_analysis.md` đã có sẵn bốn dòng, chờ điền ở
  tuần 12.
- Mục 3.2 của phiếu này là luận điểm sẵn có cho phần bàn luận ở Chương 5.
- Điều kiện tiên quyết còn thiếu để Chương 3 thành bản nộp: quyết định về GAP-026, và toàn
  văn của bốn công trình tiếng Việt nêu ở mục 7.

---

## 6. KIỂM CHỨNG — bằng chứng chạy thật

```
357 passed in 61.47s (0:01:01)
```

Không đổi so với trước step này, vì không thêm mã và không thêm test.

Kiểm bản nháp bằng máy:

| Mục kiểm | Kết quả |
|---|---|
| Số tài liệu được trích | 45, bằng đúng số công trình đã đọc toàn văn |
| Tài liệu có trong danh mục nhưng không được trích | 0 |
| Công trình đã kiểm chứng nhưng không có trong danh mục | 0 |
| Tiêu đề và năm của 45 mục so với ma trận | Trùng cả 45 |
| Gạch ngang dài, backtick, in đậm, mã step trong phần thân | 0, 0, 0, 0 |
| Chuyển sang Word bằng `md_to_docx_ute.py` | Được: 109 đoạn, 3 bảng |
| Chỗ còn đánh dấu | 1 `[CẦN KIỂM]`, 4 `[CẦN TÌM]`, 1 `[CHÈN BẢNG]` |

Kiểm ma trận: `validate` báo hợp lệ, 47 dòng dữ liệu và 2 dòng chú thích. `stats`: 46 dòng
`da_doc_toan_van`, 1 dòng `chua_kiem`, cả sáu nhóm đạt chỉ tiêu tối thiểu 4.

Số của phễu, đếm lại từ nhật ký: 28 truy vấn, tổng 258 kết quả, tổng 24 giữ lại. 12 truy vấn
đầu 111 kết quả giữ 11, 16 truy vấn sau 147 kết quả giữ 13.

**Hai điều chưa đạt:**

- Phần thân dài 4.467 âm tiết không tính bảng, ước chừng 8 đến 9 trang, **vượt ngân sách 7
  trang** của dàn ý. Cần cắt khoảng một phần năm.
- Bảng 3.9 sinh ra có ô rất dài và còn mã nội bộ như `G4_do_thi`, `khong`. Phải rút gọn và
  Việt hoá khi đưa vào Word. Bản nháp đánh số bảng liên tục 3.1, 3.2, 3.3, nên bảng tổng hợp sẽ
  là Bảng 3.4 chứ không phải 3.9 như tên file.

---

## 7. DỪNG LẠI VÀ HỎI

**Câu hỏi cần bạn quyết:**

1. **GAP-026, quan trọng nhất.** Chọn A hay B?
   - A. Chạy thêm một lượt tìm từ khoá mở trên Google Scholar hoặc ACL Anthology, ghi nhật ký
     thật, khoảng 3 đến 5 giờ tay. Sau đó mục 3.1 có phễu thật.
   - B. Gọi đúng tên là khảo sát có chủ đích, bỏ sơ đồ phễu, thêm một câu vào mục hạn chế.
2. Báo cáo có nêu việc tìm và đọc tài liệu có công cụ trí tuệ nhân tạo hỗ trợ không? Việc này
   theo quy định của trường và ý GVHD, tôi không quyết thay.
3. Bản nháp `chuyende1/report/nhap/Chuong3_KhaoSat.md` có đưa lên GitHub không? Kho đang công
   khai. Hiện tôi để chưa commit.
4. GAP-025: bài `VoZhang2015` xử lý thế nào, gõ lại một truy vấn và ghi bổ sung, hay nói thẳng
   trong mục 3.1 là có một bài vào ngoài nhật ký?

**Việc chỉ bạn làm được**, vì cần tài khoản thư viện trường:

| Tải gì | Từ đâu | Đặt vào đâu |
|---|---|---|
| "A New Approach for Vietnamese Aspect-Based Sentiment Analysis" | IEEE Xplore | `chuyende1/docs/`, thư mục này không lên GitHub |
| "Multi-task Solution for Aspect Category Sentiment Analysis on Vietnamese Datasets" | IEEE Xplore | như trên |
| "Vietnamese Sentiment Analysis: An Overview and Comparative Study of Fine-tuning Pretrained Language Models" | ACM Digital Library | như trên |
| "VLSP Shared Task: Sentiment Analysis", JCC 34(4), 2018 | Trang tạp chí, hoặc xin tác giả | như trên |

Ba bài đầu có thể làm đổi câu "chưa tìm thấy kết quả đã công bố nào trên UIT-ViSFD ngoài bài
giới thiệu tập dữ liệu" ở mục 3.8. Có file rồi báo tôi, tôi đọc và thêm dòng vào ma trận.

**Còn treo từ step trước:** có kiểm quan sát về epoch 3 bằng thí nghiệm không, và có gom hai
dòng tiêm trong `train.py` thành một hàm không.

**Những chỗ có thể bạn muốn hỏi thêm:**

- Khảo sát có chủ đích khác khảo sát có hệ thống ở đâu, và hội đồng coi trọng cái nào hơn?
- Vì sao BERT thuần ngang mô hình đồ thị tốt nhất mà người ta vẫn làm đồ thị?
- Phản biện của Kiritchenko và Mohammad có làm hỏng hướng dùng luật của NS-MGAT không?
- Bản nháp dài quá ngân sách thì nên cắt mục nào?

**Kết:**
> Bạn có câu hỏi phụ nào về phần này không, hay tôi đi tiếp sang **CD1.8a, lọc ứng viên tập
> chẩn đoán**?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

Học viên trả lời và hỏi lại cùng ngày 05/10/2026. **Các con số ở mục 1 đến 7 là số tại thời
điểm viết phiếu.** Sau trao đổi, ma trận tăng từ 46 lên 49 dòng đã đọc toàn văn, tức từ 45 lên
48 công trình, và bản nháp trích 48 tài liệu.

### 8.1 Trả lời của học viên

| Câu hỏi ở mục 7 | Trả lời | Đã làm gì theo đó |
|---|---|---|
| 3. Bản nháp có lên GitHub không | **Không** | Thêm `chuyende1/report/nhap/` vào `.gitignore`, đã push các file còn lại |
| 2. Báo cáo có nêu công cụ trí tuệ nhân tạo hỗ trợ khảo sát không | **Không nêu** | Ghi vào GAP-026. Mục 3.1 vẫn mô tả đúng việc đã làm với tài liệu và không vẽ phễu |
| Bốn bài cần tải | Lấy được hai bài cuối, hai bài IEEE không truy cập được | Đọc toàn văn cả hai, xem mục 8.2 |
| 1. GAP-026, phương án A hay B | Chưa trả lời | Vẫn mở |
| 4. GAP-025, bài `VoZhang2015` | Chưa trả lời | Vẫn mở |

### 8.2 Học viên hỏi: bốn bài này để làm gì, có quan trọng không

Trả lời ngắn: **cả bốn đều để kiểm một câu ở mục 3.8** của bản nháp, câu nói rằng ngoài bài
giới thiệu tập dữ liệu thì chưa thấy kết quả đã công bố nào trên UIT-ViSFD. Câu đó quyết định
bạn trả lời hội đồng thế nào khi bị hỏi "so với bài khác trên cùng dữ liệu thì sao". Đọc xong
hai bài lấy được, cộng một bài mở tìm thêm, thì **câu đó sai và đã được sửa.**

| Bài | Để làm gì | Đọc xong thấy gì | Quan trọng cỡ nào |
|---|---|---|---|
| VLSP Shared Task, JCC 2018. **Đã có, đã đọc** | Mô tả bộ dữ liệu theo khía cạnh thứ hai của tiếng Việt, để mục 3.8 không còn ô trống | Nhà hàng 4.751 và khách sạn 5.600 đánh giá. Chỉ ba đội nộp, cả ba dùng SVM hoặc perceptron với n-gram, đội tốt nhất F1 0,61. Hai hệ thống năm 2016 đã dùng danh sách từ phủ định làm đặc trưng | **Vừa.** Lấp ô trống cuối của Bảng 3.3. Không đổi kết luận nào |
| Tổng quan của Thin, Hao, Nguyen, ACM 2023. **Đã có, đã đọc** | Tưởng là có kết quả trên UIT-ViSFD | **Không có UIT-ViSFD và không phải bài toán theo khía cạnh.** Nhưng cho hai thứ khác: bằng chứng rằng PhoBERT là lựa chọn tốt nhất trong mười mô hình tiền huấn luyện cho tiếng Việt, và một bảng 34 công trình cảm xúc tiếng Việt | **Cao, theo cách khác dự kiến.** Bảng 34 công trình là thước đo độc lập cho độ phủ của khảo sát: ma trận chỉ có 1 trong 34. Nó cũng chỉ ra bốn bài tiếng Việt cũ có dùng luật cú pháp, Tree-LSTM và xử lý phủ định, khiến hai câu "duy nhất" trong bản nháp phải viết lại |
| "A New Approach for Vietnamese ABSA", KSE 2022, IEEE. **Chưa có** | PhoBERT trên chính UIT-ViSFD, là con số gần với baseline `phobert` của bạn nhất | Chưa đọc được. Nhưng số chính của nó, macro-F1 78,76 %, đã có qua bài thứ năm bên dưới trích lại | **Hạ xuống thấp.** Có thì đọc phần tiền xử lý. Không có thì báo cáo vẫn viết được, miễn ghi là số trích lại |
| "Multi-task Solution for ACSA on Vietnamese Datasets", IEEE. **Chưa có** | Cùng dạng bài toán nhóm khía cạnh trên dữ liệu tiếng Việt | Chưa đọc được, cũng chưa biết bài có chạy trên UIT-ViSFD không | **Thấp tới vừa.** Không chặn việc gì |
| **Bài thứ năm, tìm thêm được:** Thin và Nguyen, VNU Journal of Science 2023, truy cập mở | Hiện ra khi tra tên hai bài IEEE | **Có kết quả trên chính UIT-ViSFD**, macro-F1 81,10 %, và gom mọi kết quả trước đó trên tập này vào một bảng | **Cao nhất trong cả năm.** Thay được vai trò của hai bài IEEE. Đã gắn cờ 🔴 trong `doc_bat_buoc.md` |

**Điều quan trọng nhất rút ra, phải nhớ khi viết Chương 4 và khi bảo vệ:**

Trên UIT-ViSFD đã có kết quả công bố: 63,06 rồi 74,44 rồi 78,76 rồi 81,10 macro-F1. Nhưng
những con số đó đo bài toán **tự phát hiện khía cạnh kèm cảm xúc**, một dự đoán chỉ đúng khi
đúng cả hai. Bạn làm bài toán **cho sẵn khía cạnh**. Macro-F1 0,8664 của `phobert` cao hơn
81,10 **không** có nghĩa là mô hình của bạn tốt hơn, và hai con số không được đặt cạnh nhau như
cùng một thang.

### 8.3 Thay đổi sau trao đổi

| File | Thay đổi |
|---|---|
| `chuyende1/survey/survey_matrix.csv` | `VLSP-2018` sang `da_doc_toan_van`; thêm `ThinVNSentimentOverview`, `ThinGenerativeACSA2023`; thêm `PhoBERT-ViSFD-2022` ở mức `chua_kiem`; sửa nơi công bố của `UIT-ViSFD` |
| `chuyende1/report/nhap/Chuong3_KhaoSat.md` | Mục 3.4, 3.6, 3.8 viết lại theo ba bài mới; mọi con số 45 thành 48; danh mục 48 tài liệu |
| `chuyende1/survey/gap_analysis.md` | Khoảng trống 3 phát biểu hẹp lại thành giao của ba điều kiện; thêm bảng kết quả đã công bố trên UIT-ViSFD |
| `chuyende1/survey/survey_protocol.md` | Ghi hai truy vấn ngày 05/10; N₄ và N₅ bằng 49 |
| `chuyende1/survey/doc_bat_buoc.md` | Gắn cờ 🔴 bài `ThinGenerativeACSA2023`; cập nhật mục `PhoBERT-ViSFD-2022` |
| `chuyende1/gaps/GAP-027_*.md` | Mới: ma trận ghi sai nơi công bố của bài UIT-ViSFD, KSE thay vì KSEM |
| `chuyende1/gaps/GAP-026_*.md` | Thêm mục 5b: phép thử độ phủ, 1 trên 34 và 3 trên 11 |
| `scripts/survey_tools.py` | Sửa một dòng ví dụ ghi KSE 2021 |

Bản nháp nay dài 5.102 âm tiết phần thân, vượt ngân sách 7 trang nhiều hơn trước. Việc cắt để
dành cho lúc ghép chương.
