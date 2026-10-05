# PHÂN TÍCH KHOẢNG TRỐNG NGHIÊN CỨU — `[CD1.2]`

> **Trạng thái:** điền ngày 05/10/2026, cập nhật cùng ngày sau khi đọc thêm ba công trình tiếng
> Việt. Ma trận có 49 dòng đã đọc toàn văn.
> Đây là cầu nối từ Chương 3 sang Chương 5–6 của cuốn chuyên đề, và là luận cứ
> cho việc chọn hướng Chuyên đề 2. Bản văn xuôi để đưa vào báo cáo nằm ở mục 3.10 của
> `chuyende1/report/nhap/Chuong3_KhaoSat.md`.

## Quy tắc viết

Mỗi khoảng trống phải trỏ về **≥ 2 dòng cụ thể** trong `survey_matrix.csv` (ghi `ref_key`).
Khoảng trống không có bằng chứng từ ma trận là ý kiến cá nhân, không phải kết quả khảo sát.

## Phạm vi của mọi nhận định dưới đây

Bốn khoảng trống đều là phát biểu về **48 công trình đã đọc toàn văn**, không phải về toàn bộ
lĩnh vực. Câu "chưa có ai làm X" trong file này luôn phải đọc là "trong 48 công trình đã khảo
sát không có công trình nào làm X". Những chỗ làm phạm vi này yếu đi được ghi ở cuối file.

Cách đếm dùng chung: ma trận có 49 dòng đã kiểm chứng nhưng chỉ **48 công trình**, vì
`ATAE-LSTM` và `BiLSTM-attention` là cùng một bài báo giữ hai vai trò. Hai dòng `Lexicon-based`
và `BiLSTM-attention` mang `ngon_ngu = vi` vì đại diện cho baseline của đề tài, còn bài báo
gốc là tiếng Anh, nên không tính vào số công trình tiếng Việt. Số công trình tiếng Việt đã đọc
là **13**.

---

## Khoảng trống 1 — Mô hình đồ thị mức khía cạnh không xử lý tường minh phủ định và chuyển ý

- **Phát biểu:** cả tám mô hình đồ thị cho bài toán mức khía cạnh trong ma trận đều không có
  cơ chế kiến trúc riêng cho phủ định hay chuyển ý, trong khi tác hại của hai hiện tượng này
  đã được đo định lượng.
- **Bằng chứng từ ma trận:**
  - Tám dòng nhóm G4 có `xu_ly_phu_dinh_chuyen_y = khong`: `DongAdaRNN2014`, `ASGCN`, `CDT`,
    `kumaGCN`, `RGAT`, `DualGCN`, `SSEGCN`, `Sentic-GCN`.
  - Dòng G4 duy nhất có `co` là `SocherRNTN2013`, nhưng đó là mô hình mức câu trên cây thành
    phần, không phải mức khía cạnh. Chính nó đo được chỉ 41 % đúng với cấu trúc "X but Y".
  - Tác hại đã đo: `MooreNegationTSA`, mọi mô hình tụt trung bình 24 điểm F1 trên câu có phủ
    định và 25 điểm trên câu có suy đoán.
  - Dấu vết trong chính các bài đồ thị: `RGAT` đếm phủ định kép là 6 % trong 100 mẫu đoán sai;
    `SSEGCN` viết rằng các phương pháp khác có xu hướng bỏ qua phần phủ định; `ASGCN` và
    `SSEGCN` chỉ có ví dụ định tính.
- **Vì sao chưa ai lấp:** các tập chuẩn của SemEval không tách riêng câu có phủ định, nên
  thiếu sót này không hiện ra trên bảng kết quả. Tập thử thách đầu tiên trong ma trận chỉ có
  từ năm 2021 (`MooreNegationTSA`), sau khi phần lớn mô hình đồ thị đã công bố.
- **Liên quan tới đề tài:** đây là chỗ đứng của đồ thị logic trong NS-MGAT, nơi phủ định và
  tương phản là cạnh có nhãn chứ không phải thứ mô hình phải tự suy ra.

## Khoảng trống 2 — Tri thức ký hiệu chưa vào tới mức khía cạnh, và nơi đã vào thì không kèm độ tin cậy

- **Phát biểu:** các công trình kết hợp nơ-ron và ký hiệu trong ma trận đều làm việc ở mức
  câu, mức văn bản hoặc mức từ. Công trình duy nhất đưa tri thức vào đồ thị mức khía cạnh thì
  dùng nó làm trọng số cạnh cố định.
- **Bằng chứng từ ma trận:**
  - Nhóm G6, cả năm dòng: `HuLogicRules2016` mức câu, chỉ có luật "A but B", không xử lý phủ
    định; `KoconNeuroSymbolic` mức văn bản, tiếng Ba Lan; `SenticNet` là tài nguyên mức từ và
    khái niệm; `NeuroSymbolic3rdWave` và `HamiltonNeSyNLP` không có thực nghiệm riêng.
  - `Sentic-GCN`: tri thức cảm xúc chỉ đổi trọng số của cạnh cú pháp đã có, theo công thức
    `A = D × (S + T + 1)`. Không thêm cạnh, điểm cảm xúc dùng nguyên trạng.
  - Phản biện phải trả lời: `KiritchenkoNegators` đo được tác động của từ phủ định chênh nhau
    tới 0,41 ngay trong cùng nhóm, và kết luận học thống kê hứa hẹn hơn luật viết tay cố định.
  - Hướng được ủng hộ: `HamiltonNeSyNLP` kết luận các hệ thống biên dịch logic trực tiếp vào
    mạng nơ-ron đạt nhiều tiêu chí nhất. `ThinGenerativeACSA2023`, công trình tiếng Việt mới
    nhất trên chính UIT-ViSFD, tự nêu việc đưa tri thức vào mô hình là hướng tiếp theo.
- **Vì sao chưa ai lấp:** luật ở mức câu chỉ cần biết câu có liên từ nào. Luật ở mức khía cạnh
  còn phải biết liên từ đó tác động lên khía cạnh nào, tức cần gắn luật vào cấu trúc câu.
- **Liên quan tới đề tài:** bản duyệt của GVHD nêu điểm mới là luật vừa thêm cạnh vừa cung cấp
  độ tin cậy. Khoảng trống này là bằng chứng từ tài liệu cho đúng hai vế đó. Phản biện của
  `KiritchenkoNegators` chính là lý do độ tin cậy phải học được từ dữ liệu.

## Khoảng trống 3 — Tiếng Việt chưa có mạng nơ-ron đồ thị hay mô hình neuro-symbolic cho mức khía cạnh

- **Phát biểu:** trong 13 công trình tiếng Việt đã đọc, không công trình nào dùng mạng nơ-ron
  đồ thị hay kết hợp tri thức ký hiệu với mô hình nơ-ron cho bài toán mức khía cạnh.
- **Bằng chứng từ ma trận:**
  - Mười ba dòng tiếng Việt đều có `co_dung_do_thi = khong`: `PhoBERT`, `ViSoBERT`, `BARTpho`,
    `WordSegVNSentiment`, `PhoBERTPhoneReviewsCTU`, `ThinVNSentimentOverview`,
    `ViABSALipstick`, `ThinGenerativeACSA2023`, `UIT-ViSFD`, `UIT-ViSD4SA`, `VLSP-2018`,
    `VietSentiWordNet`, `TranValenceShiftersVN`.
  - `ThinGenerativeACSA2023` (2023) tổng quan nghiên cứu theo khía cạnh cho tiếng Việt và chỉ
    kể các hướng: SVM với đặc trưng thủ công, mạng tích chập, mạng tuần tự, BERT đa nhiệm,
    attention cửa sổ nhỏ, mô hình sinh.
  - `VLSP-2018`: cả ba hệ thống dự thi năm 2018 là SVM hoặc perceptron nhiều lớp với n-gram.
  - `SemEval2016` mở rộng sang 8 ngôn ngữ, không có tiếng Việt.
- **Phải nói rõ để không phát biểu quá tay**, theo Bảng 1 của `ThinVNSentimentOverview`, là
  nguồn phụ và chưa đọc trực tiếp bốn bài này:
  - Đã có hệ thống tiếng Việt dùng **luật phụ thuộc cú pháp** cùng từ điển cảm xúc cho từng
    khía cạnh (Tran và Phan 2018). Đó là hệ thuần luật, không có phần nơ-ron.
  - Đã có **Tree-LSTM trên cây phụ thuộc** cho tiếng Việt (Nguyen, Nguyen và Nguyen 2018),
    nhưng ở mức câu, trên phản hồi của sinh viên.
  - Đã có hệ thống mức tài liệu **có xử lý phủ định** (Nguyen-Nhat và Duong 2019).
  - Vì vậy khoảng trống đúng là **giao của ba điều kiện**: mạng nơ-ron đồ thị, mức khía cạnh,
    tiếng Việt. Bỏ một điều kiện là đã có người làm.
- **Vì sao chưa ai lấp:** mô hình đồ thị cần bộ phân tích cú pháp phụ thuộc đủ tốt cho văn
  bản mạng xã hội. Đề tài đã đo được 52,2 % Example của tập train UIT-ViSFD có cây phụ thuộc
  bị chia cắt (GAP-007), tức rào cản này có thật.
- **Liên quan tới đề tài:** ba baseline đồ thị ở Chương 4 (`asgcn`, `asgcn_linked`,
  `senticgcn`) là phép đo trực tiếp cho khoảng trống này.

## Khoảng trống 4 — Chưa có tập đánh giá riêng cho phủ định và chuyển ý ở tiếng Việt

- **Phát biểu:** tiếng Anh đã có tập thử thách cho phủ định và được dùng lại để đánh giá mô
  hình mới. Tiếng Việt chưa có tập nào như vậy trong ma trận.
- **Bằng chứng từ ma trận:**
  - Tiếng Anh: `MooreNegationTSA` xây bốn tập thử thách, đồng thuận Cohen's kappa 0,66 đến
    0,70; `ChatGPTSentiment` dùng lại chúng; `CouncillNegationScope` có kho nhận xét gán nhãn
    phạm vi phủ định.
  - Tiếng Việt: `UIT-ViSFD`, `UIT-ViSD4SA` và `VLSP-2018` không có nhãn nào về hai hiện tượng
    này. `TranValenceShiftersVN` chỉ có thống kê tần suất. `VLSP-2018` cho biết hai hệ thống
    dự thi năm 2016 dùng danh sách từ phủ định làm đặc trưng, nhưng không có đánh giá riêng.
- **Vì sao chưa ai lấp:** phải gán nhãn tay, và cần người gán thứ hai để đo độ đồng thuận.
  `VLSP-2018` gán nhãn bằng ba người mà cũng không báo cáo hệ số đồng thuận.
- **Liên quan tới đề tài:** tập chẩn đoán 300 câu của Chuyên đề 1 lấp đúng khoảng trống này.
  Mức kappa 0,66 đến 0,70 của `MooreNegationTSA` là mốc tham chiếu cho ngưỡng 0,70 đã đặt.

---

## Kết quả đã công bố trên UIT-ViSFD, và vì sao không so được với Chương 4

Ghi ở đây vì hội đồng gần như chắc chắn hỏi. Nguồn: Bảng 6 của `ThinGenerativeACSA2023`.

| Mô hình | Macro-F1 trên UIT-ViSFD | Nguồn của con số |
|---|---|---|
| BiLSTM-CNN | 63,06 | Bài giới thiệu tập dữ liệu, `UIT-ViSFD` |
| PhoBERT đa nhiệm | 74,44 | Thin và Nguyen tự cài |
| PhoBERT kết hợp tiền xử lý | 78,76 | Le và cộng sự 2022, **số trích lại**, bản gốc chưa đọc được |
| viT5 bản lớn | 81,10 | `ThinGenerativeACSA2023` |

**Bốn con số trên đo một bài toán khác với Chương 4.** Ở đó mô hình phải tự phát hiện nhóm khía
cạnh, và một dự đoán chỉ đúng khi đúng cả khía cạnh lẫn cực tính. Đề tài cho sẵn khía cạnh và
chỉ phân loại ba lớp. Macro-F1 0,8664 của `phobert` vì thế **không được đặt cạnh** 74,44 hay
81,10 như thể cùng một thang. Bài toán của đề tài dễ hơn ở khâu khía cạnh.

Hệ quả: Chương 4 không có con số đã công bố nào để đối chiếu trực tiếp. Muốn có thì phải chạy
thêm một cấu hình phát hiện khía cạnh, việc này ngoài phạm vi đã chốt của Chuyên đề 1.

---

## Những chỗ làm phạm vi khảo sát yếu đi

| Chỗ yếu | Ảnh hưởng tới khoảng trống nào | Việc cần làm |
|---|---|---|
| Tám công trình cảm xúc theo khía cạnh cho tiếng Việt mà `ThinGenerativeACSA2023` trích nhưng ma trận chưa có. Danh sách ở GAP-026 mục 5b | Khoảng trống 3 | Đọc ít nhất hai bộ dữ liệu lớn mức câu (ACM TALLIP 2021) và phương pháp biến đổi (JCC 2018, cùng số với bài VLSP) |
| Bốn công trình tiếng Việt cũ hơn biết qua Bảng 1 của `ThinVNSentimentOverview`: Tran và Phan 2018, Nguyen và cộng sự 2018, Nguyen-Nhat và Duong 2019, Ha và cộng sự 2011 | Khoảng trống 3, phần "phải nói rõ" | Đọc trực tiếp Tran và Phan 2018, vì đó là bài gần hướng luật của đề tài nhất |
| Hai bài trên IEEE Xplore chưa truy cập được: Le và cộng sự 2022 (dòng `PhoBERT-ViSFD-2022`), và "Multi-task Solution for Aspect Category Sentiment Analysis on Vietnamese Datasets" | Bảng kết quả đã công bố ở trên | Nhờ GVHD hoặc thư viện trường. Không gấp: số chính của bài thứ nhất đã có qua trích lại |
| 28 trong 30 truy vấn của nhật ký tìm kiếm là tra theo tên bài đã biết, chỉ 2 là từ khoá mở | Cả bốn. Không có căn cứ để nói đã quét hết một vùng tài liệu | Xem GAP-026 |

---

## Đối chiếu với hạn chế đo được *(điền ở Tuần 12, sau CD1.9 + CD1.11)*

Bảng này là chỗ hai nguồn bằng chứng gặp nhau: khoảng trống **từ tài liệu** và hạn chế
**từ thí nghiệm của chính mình**. Hạn chế nào trùng với khoảng trống nào thì hướng đó
đáng theo nhất.

| Khoảng trống (từ tài liệu) | Hạn chế đo được (CD1.9) | Trần cải tiến (CD1.11) | Đáng theo ở CĐ2? |
|---|---|---|---|
| 1. Đồ thị mức khía cạnh không xử lý phủ định và chuyển ý | | | |
| 2. Tri thức ký hiệu chưa vào mức khía cạnh, không kèm độ tin cậy | | | |
| 3. Tiếng Việt chưa có mạng nơ-ron đồ thị hay neuro-symbolic cho mức khía cạnh | | | |
| 4. Chưa có tập đánh giá phủ định và chuyển ý cho tiếng Việt | | | |
