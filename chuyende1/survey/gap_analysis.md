# PHÂN TÍCH KHOẢNG TRỐNG NGHIÊN CỨU — `[CD1.2]`

> **Trạng thái:** đã điền ngày 05/10/2026, sau khi ma trận có 46 dòng đã đọc toàn văn.
> Đây là cầu nối từ Chương 3 sang Chương 5–6 của cuốn chuyên đề, và là luận cứ
> cho việc chọn hướng Chuyên đề 2. Bản văn xuôi để đưa vào báo cáo nằm ở mục 3.10 của
> `chuyende1/report/nhap/Chuong3_KhaoSat.md`.

## Quy tắc viết

Mỗi khoảng trống phải trỏ về **≥ 2 dòng cụ thể** trong `survey_matrix.csv` (ghi `ref_key`).
Khoảng trống không có bằng chứng từ ma trận là ý kiến cá nhân, không phải kết quả khảo sát.

## Phạm vi của mọi nhận định dưới đây

Bốn khoảng trống đều là phát biểu về **45 công trình đã đọc toàn văn**, không phải về toàn bộ
lĩnh vực. Câu "chưa có ai làm X" trong file này luôn phải đọc là "trong 45 công trình đã khảo
sát không có công trình nào làm X". Ba chỗ làm phạm vi này yếu đi được ghi ở cuối file.

Cách đếm dùng chung: ma trận có 46 dòng đã kiểm chứng nhưng chỉ **45 công trình**, vì
`ATAE-LSTM` và `BiLSTM-attention` là cùng một bài báo giữ hai vai trò. Hai dòng `Lexicon-based`
và `BiLSTM-attention` mang `ngon_ngu = vi` vì đại diện cho baseline của đề tài, còn bài báo
gốc là tiếng Anh, nên không tính vào số công trình tiếng Việt.

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
    mạng nơ-ron đạt nhiều tiêu chí nhất.
- **Vì sao chưa ai lấp:** luật ở mức câu chỉ cần biết câu có liên từ nào. Luật ở mức khía cạnh
  còn phải biết liên từ đó tác động lên khía cạnh nào, tức cần gắn luật vào cấu trúc câu.
- **Liên quan tới đề tài:** bản duyệt của GVHD nêu điểm mới là luật vừa thêm cạnh vừa cung cấp
  độ tin cậy. Khoảng trống này là bằng chứng từ tài liệu cho đúng hai vế đó. Phản biện của
  `KiritchenkoNegators` chính là lý do độ tin cậy phải học được từ dữ liệu.

## Khoảng trống 3 — Tiếng Việt chưa có mô hình đồ thị hay neuro-symbolic cho mức khía cạnh, và phủ định mới dừng ở mô tả

- **Phát biểu:** mười công trình tiếng Việt trong ma trận không dùng đồ thị cú pháp và không
  kết hợp tri thức ký hiệu với mô hình nơ-ron. Công trình duy nhất về từ đổi cực tính chưa cài
  đặt mô hình nào.
- **Bằng chứng từ ma trận:**
  - Mười dòng tiếng Việt đều có `co_dung_do_thi = khong`: `PhoBERT`, `ViSoBERT`, `BARTpho`,
    `WordSegVNSentiment`, `PhoBERTPhoneReviewsCTU`, `ViABSALipstick`, `UIT-ViSFD`,
    `UIT-ViSD4SA`, `VietSentiWordNet`, `TranValenceShiftersVN`.
  - `TranValenceShiftersVN` là dòng tiếng Việt duy nhất có `xu_ly_phu_dinh_chuyen_y = co`,
    nhưng bài chỉ thống kê tần suất và tự viết rằng các luật đề xuất sẽ được cài đặt sau.
  - `SemEval2016` mở rộng sang 8 ngôn ngữ, không có tiếng Việt.
  - Trên chính `UIT-ViSFD`, kết quả đã công bố duy nhất trong ma trận cho bài toán ba lớp theo
    khía cạnh là macro-F1 63,06 % của bài giới thiệu tập dữ liệu. `PhoBERTPhoneReviewsCTU` có
    dùng các bình luận đó nhưng bỏ nhãn khía cạnh và gán nhãn hai lớp, không so được.
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
  - Tiếng Việt: `UIT-ViSFD` và `UIT-ViSD4SA` có `xu_ly_phu_dinh_chuyen_y = khong`;
    `TranValenceShiftersVN` chỉ có thống kê tần suất trên ngữ liệu chưa gán nhãn cảm xúc theo
    hiện tượng.
- **Vì sao chưa ai lấp:** phải gán nhãn tay, và cần người gán thứ hai để đo độ đồng thuận.
- **Liên quan tới đề tài:** tập chẩn đoán 300 câu của Chuyên đề 1 lấp đúng khoảng trống này.
  Mức kappa 0,66 đến 0,70 của `MooreNegationTSA` là mốc tham chiếu cho ngưỡng 0,70 đã đặt.

---

## Ba chỗ làm phạm vi khảo sát yếu đi

| Chỗ yếu | Ảnh hưởng tới khoảng trống nào | Việc cần làm |
|---|---|---|
| Ba công trình tiếng Việt đã biết tên nhưng chưa đọc được toàn văn: "A New Approach for Vietnamese Aspect-Based Sentiment Analysis" và "Multi-task Solution for Aspect Category Sentiment Analysis on Vietnamese Datasets" trên IEEE Xplore, "Vietnamese Sentiment Analysis: An Overview and Comparative Study of Fine-tuning Pretrained Language Models" trên ACM | Khoảng trống 3, vế "kết quả đã công bố duy nhất trên UIT-ViSFD" | Học viên lấy toàn văn qua thư viện trường, rồi thêm dòng vào ma trận |
| `VLSP-2018` còn `chua_kiem` | Khoảng trống 3 và 4, phần mô tả dữ liệu tiếng Việt | Tìm bản PDF khác của bài trên Journal of Computer Science and Cybernetics |
| 26 trong 28 truy vấn của nhật ký tìm kiếm là tra theo tên bài đã biết, chỉ 2 là từ khoá mở | Cả bốn. Không có căn cứ để nói đã quét hết một vùng tài liệu | Xem GAP-026. Hoặc chạy thêm một lượt tìm từ khoá mở có ghi nhật ký, hoặc gọi đúng tên phương pháp là khảo sát có chủ đích |

---

## Đối chiếu với hạn chế đo được *(điền ở Tuần 12, sau CD1.9 + CD1.11)*

Bảng này là chỗ hai nguồn bằng chứng gặp nhau: khoảng trống **từ tài liệu** và hạn chế
**từ thí nghiệm của chính mình**. Hạn chế nào trùng với khoảng trống nào thì hướng đó
đáng theo nhất.

| Khoảng trống (từ tài liệu) | Hạn chế đo được (CD1.9) | Trần cải tiến (CD1.11) | Đáng theo ở CĐ2? |
|---|---|---|---|
| 1. Đồ thị mức khía cạnh không xử lý phủ định và chuyển ý | | | |
| 2. Tri thức ký hiệu chưa vào mức khía cạnh, không kèm độ tin cậy | | | |
| 3. Tiếng Việt chưa có mô hình đồ thị hay neuro-symbolic | | | |
| 4. Chưa có tập đánh giá phủ định và chuyển ý cho tiếng Việt | | | |
