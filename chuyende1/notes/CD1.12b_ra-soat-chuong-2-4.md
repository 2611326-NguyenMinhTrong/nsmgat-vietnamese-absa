# CD1.12b — Rà soát Chương 2 đến 4 với bản gốc, dữ liệu và cấu hình

Ngày 13/10/2026. Làm sớm hơn lịch (tuần 14) theo yêu cầu của học viên: "check kỹ lại để tối ưu
report từ chương 2 đến chương 4, đảm bảo tài liệu phải có giá trị và phải chính xác".

## 1. ĐÃ LÀM GÌ

1. Tải bản gốc của 56 công trình và trích chữ, rồi tìm từng con số của Chương 3 trong văn bản đó.
2. Đọc ngữ cảnh quanh từng con số trong bản gốc: tên bảng, tên cột, câu chú thích.
3. Tính lại mọi con số của Chương 4 từ dữ liệu, 18 file kết quả, 18 file dự đoán.
4. So mô tả phương pháp ở Chương 2 và 4 với cấu hình, mã nguồn và nhật ký huấn luyện.
5. So bản dữ liệu đang dùng với bản do tác giả UIT-ViSFD công bố.
6. Đo hai từ điển cảm xúc tiếng Việt có sẵn trên dữ liệu của đề tài.
7. Kiểm tác giả, tên bài, nơi công bố của danh mục tài liệu qua trang đầu bản gốc, Crossref, arXiv.
8. Sửa bản nháp, ma trận khảo sát, danh mục tài liệu; vẽ hình; ghép lại vào file Word.

## 2. KẾT QUẢ RÀ SOÁT

| Hạng mục | Kết quả |
|---|---|
| Con số Chương 3 dẫn từ công trình khác | 129 con số, **cả 129 có trong bản gốc** |
| Con số Chương 4 | 68 chỗ, 66 khớp ngay, 2 chỗ lệch 0,01 do làm tròn (đã sửa) |
| Kết quả thực nghiệm (Bảng 4.5 đến 4.9) | **Không sai chỗ nào** |
| Bản dữ liệu đang dùng | **Trùng từng dòng** với ba file tác giả công bố trên GitHub (11.122 dòng, đúng thứ tự) |
| Tỉ lệ mẫu bị cắt ở 128 subword | Đo lại bằng đúng hàm của chương trình huấn luyện: khớp |
| Tám tài liệu viết theo trí nhớ | Cả tám đúng tác giả, tên bài, nơi công bố |
| Các con số tổng hợp của mục 3.9 | 48, 25, 13, 7, 11, 14: đếm lại từ ma trận đều khớp |

Cái sai nằm ở chỗ khác: **phần chữ đi kèm con số, và vài nhận định không có phép đo đứng sau**.
Tổng cộng sửa 53 chỗ trong ba chương. Phân loại đầy đủ ở
`chuyende1/gaps/GAP-031_ra-soat-chuong-2-4-so-dung-nhung-loi-gan-kem-sai.md`.

## 3. TỪNG CHỖ ĐÃ ĐỔI, ĐỂ BẠN ĐỌC LẠI

Đây là việc B8 trong sổ nhắc. Bốn chỗ đầu là nặng nhất.

### 3.1 Bốn nhận định sai sự thật

| Mục | Bản cũ | Bản mới | Căn cứ |
|---|---|---|---|
| 4.3 | "SenticNet không có cho tiếng Việt" | Có bản tiếng Việt, viết không dấu, chuyên đề chưa thực nghiệm | Trang tải về của SenticNet, mục VIETNAMESE RESOURCES, xem ngày 13/10 |
| 4.3 | "chưa tìm được một từ điển cảm xúc tiếng Việt công khai có độ phủ đủ lớn" | Hai tài nguyên có sẵn, kèm độ phủ đo được: 8,7 % và 52,4 % | `scripts/do_phu_tu_dien.py` |
| 3.2 | Phương pháp của Hatzivassiloglou và McKeown "không cần dữ liệu gán nhãn" | Bỏ vế này | Bài dùng 1.336 tính từ gán nhãn tay để huấn luyện và đánh giá |
| 3.8 | Tập son môi "cũng gồm một khía cạnh chung" | Bảy khía cạnh, một nhãn OTHERS cho bình luận rác | Mục 3.1 của bài |

### 3.2 Chương 3: số đúng, lời gắn kèm sai

| Mục | Đổi gì |
|---|---|
| 3.1 | Bỏ chỗ để trống. Viết thẳng: 28 trên 30 truy vấn là tra đích danh, đây là khảo sát có chọn lọc. Thêm câu: mọi con số đã được đối chiếu lại với bản gốc |
| 3.2 NRC-Canada | Thay 6,88 điểm (của tác vụ khác, miền khác) bằng 8,78 điểm của đúng tác vụ nhóm khía cạnh trên nhà hàng |
| 3.2 Vo và Zhang | Bỏ "được cài lại"; ghi rõ F1 là macro-F1 |
| 3.3 Moore và Barnes | Bốn tập gồm hai cho phủ định, hai cho suy đoán; mức tăng 3,8 điểm là khi dùng GloVe |
| 3.5 Socher | 81,8 % là tỉ lệ mô hình tăng mức tích cực, không phải tỉ lệ đảo đúng cực tính |
| 3.5 ASGCN | Đồ thị vô hướng tốt hơn trên bốn trong năm tập, không phải mọi tập; ghi chú Bảng 3.2 nói rõ dòng ASGCN là biến thể nào |
| 3.5 R-GAT | "câu khó hiểu" thành "nhóm đòi hỏi hiểu sâu nội dung câu" |
| 3.7 Garcez và Lamb | Bỏ mô tả hai làn sóng đầu |
| 3.7 SenticNet 7 | Thay "trung bình khoảng 82,4 %" (số tự tính) bằng khoảng 77,04 đến 90,08 % và việc cao nhất ở cả 10 tập |
| 3.7 Kocon | Nói rõ mô hình nào 87 %, mô hình nào 83 % |
| 3.8 VLSP 2016 | Bỏ "hai hệ thống SVM", chỉ nói có hệ thống dùng |
| 3.8 | Hai chỗ `[CẦN TÌM]` thành câu văn: nói thẳng công trình nào chưa đọc trực tiếp và vì sao không tính vào 48 |
| 3.8 | Bỏ con số 34 không đếm lại được |
| 3.9 | **Thêm Bảng 3.4**: 48 công trình, 8 cột, sinh từ ma trận |

### 3.3 Chương 2

| Mục | Đổi gì |
|---|---|
| 2.2 | BERT huấn luyện trước bằng hai tác vụ; nói rõ RoBERTa đổi những gì |
| 2.2 | **Thêm Hình 2.1**: trọng số tự chú ý thật của PhoBERT trên một đoạn bình luận, kèm ba câu đọc hình |
| 2.3 | ASGCN có hai biến thể, chuyên đề dùng biến thể vô hướng |
| 2.4 | Thay chỗ `[CẦN KIỂM]` bằng số đo của hai từ điển có sẵn |
| 2.5 | "Câu sau lấy từ" thành "Đoạn sau trích từ một bình luận" |
| 2.6 | Mô tả đúng cách tính p đang dùng trong mã |
| 2.6 | Thay chỗ `[TODO]` về ngưỡng kappa: 0,70, kèm hai mốc so sánh lấy từ bài đã đọc |

### 3.4 Chương 4

| Mục | Đổi gì |
|---|---|
| 4.1.1 | Nói rõ dữ liệu tải từ đâu và đã đối chiếu với bản của tác giả; nêu chỗ lệch 200 giữa bảng của bài giới thiệu và dữ liệu công bố |
| 4.1.1 | **Thêm Hình 4.1** |
| 4.1.2 | Viết phần đã làm xong (lọc ứng viên, cách chú thích). Chỗ để trống chỉ còn bảng số mẫu, kappa, tỉ lệ lệch nhãn |
| 4.2 | "Ba mô hình" thành bốn; nêu khác biệt về độ chính xác hỗn hợp; bỏ `[CẦN KIỂM]` ở tỉ lệ cắt; thêm câu về cách tính p |
| 4.2 | Phần cứng: chỉ ghi điều có bằng chứng, phần còn lại chờ bạn (B2) |
| 4.3 | "dưới 5 lần" thành "trong dưới 5 mẫu"; 9.136 ô gồm 9.134 subword và hai ký hiệu; hai số về mẫu số âm là của tập huấn luyện |
| 4.4 | 5,54 thành 5,53; 1,51 thành 1,52; thêm câu giải thích hiệu số tính từ số chưa làm tròn |
| 4.5 | Cột thiết bị của Bảng 4.9 chỉ ghi Tesla T4 ở hai dòng có nhật ký |
| 4.7 | Thêm khác biệt về độ chính xác hỗn hợp vào danh sách giới hạn |

Chương 1 đổi sáu chỗ cho khớp: câu ví dụ, cụm "toàn bộ siêu tham số", quy mô tập chẩn đoán (khoảng
800 mẫu, bốn nhóm), ba ô của Bảng 1.1.

## 4. NHỮNG ĐIỀU ĐỢT NÀY KHÔNG BẢO ĐẢM

1. **Công cụ không bắt được lỗi ngữ cảnh.** `doi_chieu_ban_goc.py` trả về "thấy" cho cả chín chỗ ở
   mục 3.2. Chúng được tìm ra nhờ đọc. Tôi đã đọc ngữ cảnh của mọi con số ở Chương 3, nhưng một
   lượt đọc không phải là bằng chứng không còn sót.
2. **Các câu không có con số** (mô tả kiến trúc, nhận định định tính) chỉ được kiểm ở những chỗ
   nêu trên. Ví dụ "kumaGCN học thêm một đồ thị tiềm ẩn" được tin theo ghi chú của ma trận.
3. **Chưa mở file Word bằng Word.** Tôi chỉ đọc lại bằng thư viện: 2 hình, 15 bảng, 60 tài liệu,
   không còn khoá trích dẫn chưa đánh số.
4. Chương 1 chỉ sửa sáu chỗ liên đới, chưa rà theo cách này. Chương 5, 6 chưa viết.

## 5. HAI PHÁT HIỆN LÀM THAY ĐỔI CÁCH ĐỌC ĐỀ TÀI

**SenticNet có bản tiếng Việt.** 36.520 khái niệm, hầu hết viết không dấu. Tra không dấu phủ 52,4 %
số lượt từ của tập huấn luyện, nhưng nhiều lượt là trùng mặt chữ: `máy` thành `may` (điểm âm
0,951), `trâu` thành `trau` (âm 0,863), `nhưng` thành `nhung` (âm 0,902). VietSentiWordNet bản
công khai thì sạch hơn nhưng nhỏ: 1.192 mục từ, phủ 8,7 %, 94,4 % số mẫu có ít nhất một từ tra
được.

Hệ quả: bậc 5 của thang mô hình đang dùng điểm cảm xúc suy từ chính nhãn huấn luyện, nên chưa
trả lời được câu hỏi "tri thức bên ngoài có ích không". Câu hỏi đó nay trả lời được bằng một thí
nghiệm thêm. Đây là quyết định C6 trong sổ nhắc, nên bàn với cô.

**PhoBERT và ba mô hình đồ thị khác nhau ở độ chính xác hỗn hợp.** Cấu hình ghi rõ, báo cáo cũ thì
viết "chung toàn bộ siêu tham số". Chênh lệch giữa ASGCN và PhoBERT (âm 1,21 điểm macro-F1) vì vậy
có thêm một cách giải thích chưa loại trừ. Muốn loại trừ thì chạy lại PhoBERT không bật thiết lập
này, ba lần, khoảng 3 giờ GPU. Chưa đưa vào sổ nhắc như một việc bắt buộc; nêu ở đây để bạn cân.

## 6. KIỂM CHỨNG

```
436 passed   (cả bộ)
```

- `doi_chieu_chuong4.py --do-cat`: 68 chỗ, khớp cả 68.
- `doi_chieu_ban_goc.py kiem Chuong3_KhaoSat.md`: 129 con số, thấy 120, thấy ở công trình khác
  cùng đoạn 9, cần xem tay 0.
- `survey_tools.py validate`: hợp lệ, 50 dòng dữ liệu.
- `nhap_chuong_vao_docx.py --ghi-de`: ghép xong, có bản sao lưu.

Công cụ mới: `scripts/doi_chieu_chuong4.py`, `scripts/doi_chieu_ban_goc.py`,
`scripts/do_phu_tu_dien.py`, `scripts/make_figures.py`; lệnh `table-gon` của `survey_tools.py`;
cú pháp chèn hình của `nhap_chuong_vao_docx.py`. Lệnh ở `SO_TAY_LENH.md` mục 11g và 11h.

File sinh ra, bạn quyết định giữ hay xoá: `data/cache/nguon_goc/` (56 file chữ trích từ bản gốc,
không lên GitHub); hai bản `.docx.bak` mới trong `chuyende1/report/`.

## 7. VIỆC CỦA BẠN

Đầy đủ ở `pLan/chuyende1/VIEC_CAN_LAM.md`. Xếp theo mức gấp:

1. **B8.** Đọc lại các câu đã đổi (mục 3 của phiếu này), khoảng 1 giờ.
2. **B3.** Mở file Word, bấm Ctrl+A rồi F9, xem Hình 2.1, Hình 4.1, Bảng 3.4, Bảng 4.6.
3. **B2.** Xác nhận phần cứng ở mục 4.2.
4. **C6.** Hỏi cô về việc chạy thêm Sentic-GCN với tri thức bên ngoài.
5. Các việc cũ còn nguyên: A7 (sao lưu), A14 (đọc 10 ca cùng sai), A12 (gán lại từ 27/10).
