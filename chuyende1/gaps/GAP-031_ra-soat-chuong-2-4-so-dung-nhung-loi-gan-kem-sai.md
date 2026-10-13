# GAP-031 — Rà soát Chương 2 đến 4: con số đúng nhưng lời gắn kèm sai, và một nhận định không đo

**Ngày phát hiện:** 13/10/2026 · **Phát hiện bởi:** Claude Code, khi đối chiếu từng nhận định với bản gốc theo yêu cầu của học viên
**Loại:** tài liệu · số liệu · phương pháp
**Mức độ:** nghiêm trọng nếu lọt vào bản nộp (ảnh hưởng độ tin cậy của khảo sát và của lý do chọn từ điển)
**Trạng thái:** ✅ Đã sửa trong bản nháp, ma trận và file Word. Hai việc còn mở ghi ở mục 6

---

## 1. Sai ở đâu

Ba chương được đối chiếu lại với ba loại nguồn: văn bản của 56 bản gốc (tải về và trích chữ), dữ
liệu cùng file kết quả của chính đề tài, và cấu hình cùng nhật ký huấn luyện.

Không có con số thực nghiệm nào sai. 129 con số mà Chương 3 dẫn từ công trình khác đều có trong
bản gốc. 68 con số của Chương 4 khớp với dữ liệu, trừ hai chỗ lệch 0,01 do làm tròn.

Cái sai nằm ở phần chữ đi kèm con số, và ở vài nhận định không có phép đo đứng sau.

### 1.1 Nhận định sai sự thật (nặng nhất)

| Chỗ | Bản cũ viết | Sự thật |
|---|---|---|
| Mục 4.3, Sentic-GCN | "SenticNet không có cho tiếng Việt" | Trang tải về của SenticNet có mục tài nguyên tiếng Việt, file `senticnet_vi.zip`, 36.520 khái niệm |
| Mục 4.3, mô hình từ điển | "chưa tìm được một từ điển cảm xúc tiếng Việt công khai có độ phủ đủ lớn" | Chưa từng đo độ phủ của từ điển nào. Câu mô tả một việc không diễn ra |
| Mục 3.2, Hatzivassiloglou và McKeown | "không cần dữ liệu gán nhãn" | Mô hình dự đoán liên kết được huấn luyện trên 1.336 tính từ gán nhãn tay |
| Mục 3.8, tập son môi | "cũng gồm một khía cạnh chung" | Bảy khía cạnh và một nhãn OTHERS cho bình luận rác; không có khía cạnh chung |

### 1.2 Số đúng, gắn sai ngữ cảnh

| Chỗ | Vấn đề |
|---|---|
| Mục 3.2, NRC-Canada | 6,88 điểm là của tác vụ cực tính theo cụm khía cạnh trên laptop, đặt ngay sau câu nói về tác vụ nhóm khía cạnh trên nhà hàng |
| Mục 3.5, Socher | 81,8 % được gọi là tỉ lệ đảo đúng cực tính; bài đo bằng việc mức tích cực tăng lên |
| Mục 3.5, ASGCN | "đồ thị vô hướng tốt hơn có hướng" không đúng trên chính tập nhà hàng 2014 dùng ở Bảng 3.2 |
| Mục 3.7, SenticNet 7 | 82,4 % là trung bình tự tính, bảng của bài không có và không ghi tên độ đo |
| Mục 3.3, Moore và Barnes | Thiếu điều kiện "khi dùng GloVe" của mức tăng 3,8 điểm; tập nhà hàng gộp ba năm SemEval chứ không riêng 2014 |
| Mục 3.2, Vo và Zhang | "được cài lại": bài không nói vậy |
| Mục 3.7, Garcez và Lamb | Mô tả hai làn sóng đầu không tìm thấy trong văn bản đã đọc |
| Mục 3.8, VLSP 2016 | "hai hệ thống SVM": cụ thể hơn mức bảng của bài cho phép khẳng định |
| Mục 3.8 | "34 công trình" trong bảng tổng quan của Thin và cộng sự: không đếm lại được từ văn bản trích |

### 1.3 Mô tả phương pháp của chính đề tài chưa chính xác

| Chỗ | Bản cũ | Đúng |
|---|---|---|
| Mục 4.2 | "Ba mô hình dùng PhoBERT có chung toàn bộ siêu tham số" | Bốn mô hình; PhoBERT bật độ chính xác hỗn hợp, ba mô hình đồ thị thì không |
| Mục 2.6 | Mô tả kiểm định bootstrap theo cách của bài gốc | Mã dùng dạng đếm số tập có hiệu số trái dấu, p hai phía |
| Mục 2.2 | BERT huấn luyện trước bằng tác vụ đoán từ bị che | Hai tác vụ, thêm đoán câu kế tiếp |
| Mục 4.3 | "Từ xuất hiện dưới 5 lần bị loại" | Từ có mặt trong dưới 5 mẫu |
| Mục 4.3 | "9.136 subword" | 9.134 subword và hai ký hiệu đặc biệt |
| Mục 4.3 | 0,079 % và 3,70 % "trên UIT-ViSFD" | Hai số này đo trên tập huấn luyện |
| Mục 4.2, Bảng 4.9 | GPU Tesla T4 cho cả bốn mô hình | Chỉ có nhật ký của ASGCN và biến thể nối gốc |
| Mục 4.4 | 5,54 và 1,51 | 5,53 và 1,52 khi tính từ số chưa làm tròn |

### 1.4 Danh mục tài liệu và ma trận

- `VietSentiWordNet`: ghi "KIPS Fall Conference"; hội nghị diễn ra tháng 4/2014.
- `HamiltonNeSyNLP`: bản tạp chí mang tên có chữ "Promises", in ở Semantic Web tập 15 số 4 năm 2024.
- `BERT-SPC`: bản in ở ICANN 2019 mang một tên khác với bản arXiv đã đọc.
- `InstructABSA`: thuộc tập Short Papers của NAACL 2024.
- Ma trận ghi `Lexicon-based` là tiếng Việt; bài báo làm trên ngữ liệu tiếng Anh.

### 1.5 Thiếu, không phải sai

- Báo cáo không nói dữ liệu lấy từ đâu. Mã tải từ một bản sao trên Hugging Face.
- Bảng thống kê của bài giới thiệu UIT-ViSFD ghi 33.710 khía cạnh, dữ liệu công bố có 33.910 cặp.

## 2. Phát hiện thế nào

Công cụ chỉ bắt được một phần. `doi_chieu_ban_goc.py` tìm con số trong văn bản bản gốc và trả về
"thấy" cho mọi con số ở mục 1.2. Các lỗi ở đó lộ ra khi đọc đoạn văn quanh con số: tên bảng, tên
cột, câu chú thích bảng.

Lỗi về SenticNet lộ ra ở bước soát lần cuối, khi một câu khẳng định "không có" bị đem đi kiểm trên
trang chính thức thay vì được coi là hiển nhiên.

## 3. Nguyên nhân gốc

1. **Viết chương từ ô tóm tắt của ma trận, rồi diễn giải thêm.** Ma trận ghi "bỏ đặc trưng từ điển
   đóng góp 6,88 điểm trên Laptop". Khi thành câu văn, phần "tác vụ nào" rơi mất. Mỗi lần diễn
   giải là một lần có thể lệch, và không có bước nào đem câu văn quay lại so với bản gốc.
2. **Kiểm số mà không kiểm lời.** Mọi đợt kiểm trước đây đều hỏi "con số này có trong bài không".
   Không đợt nào hỏi "con số này là của mô hình nào, tập nào, độ đo nào, điều kiện nào".
3. **Khẳng định phủ định không được kiểm.** "Không có", "chưa tìm được", "không cần" là những câu
   chỉ đúng khi đã tìm. Hai câu như vậy được viết ra mà không có lần tìm nào đứng sau.
4. **Hiệu số tính từ số đã làm tròn** khi viết lời văn, trong khi bảng kiểm định tính từ số gốc.

## 4. Ảnh hưởng lan tới đâu

- Lý do chọn từ điển tự suy ra cho Sentic-GCN phải viết lại: không còn là "không có tài nguyên",
  mà là "có hai tài nguyên, đã đo, chưa thực nghiệm". Đây là một giới hạn của bậc 5 và là một
  thí nghiệm bổ sung khả thi.
- GAP-002 ghi "SenticNet không có bản tiếng Việt tương đương chất lượng": nửa đầu sai, nửa sau
  thì phép đo hôm nay ủng hộ. Đã thêm ghi chú vào GAP-002.
- Bốn khoảng trống ở mục 3.10 không đổi. Các con số 7, 11, 13, 14, 25 và 48 đếm lại từ ma trận
  đều khớp.
- Không kết quả thực nghiệm nào đổi.

## 5. Đã sửa thế nào

- Ba bản nháp chương: 53 chỗ (Chương 2: 10, Chương 3: 20, Chương 4: 23, tính cả đợt sửa về
  SenticNet), cộng 6 chỗ ở Chương 1 cho khớp. File Word ghép lại, có sao lưu.
- Ma trận khảo sát: 11 dòng, mỗi dòng có ghi chú "DOI CHIEU LAI VOI BAN GOC 13/10/2026".
- Danh mục tài liệu: sửa 4 mục, gỡ đánh dấu 8 mục sau khi đối chiếu, thêm 4 nguồn web.
- Ba công cụ để lần sau kiểm lại được: `doi_chieu_chuong4.py`, `doi_chieu_ban_goc.py`,
  `do_phu_tu_dien.py`.
- Chi tiết từng chỗ ở `chuyende1/notes/CD1.12b_ra-soat-chuong-2-4.md`.

## 6. Còn mở

1. Các câu chưa được kiểm theo cách của đợt này: toàn bộ Chương 1 ngoài sáu chỗ đã sửa, và mọi
   chương viết sau. Trước khi nộp phải chạy lại hai công cụ đối chiếu và đọc lại ngữ cảnh.
2. Công cụ không bắt được lỗi ngữ cảnh. Phần đó vẫn phải có người đọc.

## 7. Bài học

Một con số trích dẫn có bốn thứ đi kèm: mô hình, tập dữ liệu, độ đo, điều kiện. Kiểm con số mà
không kiểm bốn thứ đó là mới kiểm một phần năm. Và câu nào có chữ "không có", "chưa có", "duy
nhất", "đầu tiên" thì phải có một lần tìm đứng sau, ghi được ngày và nơi tìm.
