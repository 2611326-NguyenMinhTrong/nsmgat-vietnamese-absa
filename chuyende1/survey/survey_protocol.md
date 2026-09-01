# GIAO THỨC KHẢO SÁT SOTA — `[CD1.2]`

> **Trạng thái:** giao thức đã chốt (27/08/2026). Mục 5 và 6 điền dần khi tìm.
> Đặc tả: `pLan/chuyende1/PLAN_CHUYENDE1.md` mục 5 → CD1.2.
>
> ⚠️ Giao thức này viết **trước** khi tìm bài. Khảo sát có giao thức viết trước là thứ
> phân biệt khảo sát khoa học với danh sách bài đọc ngẫu nhiên — và hội đồng sẽ hỏi
> "em tìm bằng cách nào".

## 1. Câu hỏi khảo sát

| Mã | Câu hỏi | Trả lời ở mục nào của báo cáo |
|---|---|---|
| CH1 | Các họ phương pháp nào đang là SOTA cho ABSA/ACSA, ưu–nhược từng họ? | 3.2 – 3.7 |
| CH2 | Riêng tiếng Việt đã có gì? Tập dữ liệu nào, kết quả đến đâu? | 3.8 |
| CH3 | Phủ định và chuyển ý được xử lý ra sao trong các công trình đó? | 3.9 (cột `xu_ly_phu_dinh_chuyen_y`) |
| CH4 | Khoảng trống nào còn đủ lớn để làm luận văn? | 3.10 |

CH3 là câu hỏi **riêng của đề tài này** — nó không có trong khảo sát ABSA thông thường.
Chính nó biến ma trận khảo sát thành bằng chứng cho Chương 5, chứ không chỉ là phần "nền".

## 2. Nguồn tìm kiếm

| Nguồn | Vai trò |
|---|---|
| ACL Anthology | Chính, cho NLP quốc tế. Ưu tiên vì có toàn văn miễn phí và metadata chuẩn |
| IEEE Xplore, Scopus | Tạp chí kỹ thuật |
| arXiv | Bài mới chưa qua phản biện — **đánh dấu riêng** ở cột `ghi_chu`, dùng thận trọng |
| Google Scholar | Truy vết trích dẫn xuôi/ngược từ các bài hạt giống |
| VLSP, RIVF, KSE, NAFOSTED | Hội nghị trong nước — nguồn chính cho CH2 |

**Chiến lược:** bắt đầu từ ~8 bài hạt giống đã biết tên (xem `survey_matrix.csv`), rồi
truy vết trích dẫn hai chiều. Cách này phủ tốt hơn là chỉ gõ từ khoá, vì thuật ngữ trong
lĩnh vực không thống nhất (ABSA / ATSC / ACSA / targeted sentiment).

## 3. Từ khoá

**Tiếng Anh**

```
"aspect-based sentiment analysis"
"aspect category sentiment analysis"
"aspect sentiment triplet extraction"
"ABSA graph neural network"
"syntax-aware aspect sentiment"
"dependency tree sentiment classification"
"affective knowledge sentiment graph"
"Vietnamese sentiment analysis"
"Vietnamese pre-trained language model"
"neuro-symbolic sentiment analysis"
"negation scope sentiment"
"contrastive discourse marker sentiment"
```

**Tiếng Việt**

```
"phân tích cảm xúc theo khía cạnh"
"phân tích quan điểm tiếng Việt"
"phân tích cảm xúc mức khía cạnh"
"xử lý phủ định tiếng Việt"
```

**Kết hợp:** mỗi từ khoá nhóm phương pháp × mỗi từ khoá ngôn ngữ, để không bỏ sót các
công trình áp dụng phương pháp quốc tế cho tiếng Việt.

## 4. Tiêu chí nhận / loại

**Nhận** khi thoả **cả ba**:

1. Có thực nghiệm định lượng, nêu rõ tập dữ liệu và độ đo;
2. Công bố ở hội nghị/tạp chí có phản biện — **hoặc** là mô hình nền tảng tiếng Việt được
   dùng rộng rãi (PhoBERT, ViSoBERT…) kể cả khi công bố ở arXiv;
3. Thuộc phạm vi: ABSA/ACSA, hoặc phân tích cảm xúc tiếng Việt, hoặc phương pháp
   neuro-symbolic cho phân loại văn bản.

**Loại** khi thuộc **bất kỳ** trường hợp nào:

1. Báo cáo kỹ thuật/blog không qua phản biện và không phải mô hình nền tảng;
2. Trùng lặp — giữ bản mới nhất, ghi bản cũ vào `ghi_chu`;
3. Không nêu rõ tập dữ liệu hoặc độ đo → không đưa vào bảng so sánh được;
4. Chỉ phân loại cảm xúc mức tài liệu/câu, không có khái niệm khía cạnh — **trừ khi** bài
   đó bàn riêng về phủ định hoặc chuyển ý (liên quan CH3).

Ngoại lệ ở mục 4 là có chủ ý: một bài về phạm vi phủ định trong phân loại cảm xúc mức câu
vẫn có giá trị cho Chương 5, dù không phải ABSA.

## 5. Quy trình sàng lọc — ghi số thật khi làm

| Bước | Số bài | Ngày | Cách lấy số |
|---|---|---|---|
| N₁ — thu thập thô | | | Tổng cột "Số kết quả" ở mục 6 |
| N₂ — sau khi loại trùng | | | |
| N₃ — sau sàng tiêu đề + tóm tắt | | | |
| N₄ — sau đọc toàn văn (vào ma trận) | | | `survey_tools.py stats` |
| N₅ — phân tích sâu trong Chương 3 | | | Số dòng có `trang_thai = da_doc_toan_van` |

Năm con số này dựng thành sơ đồ luồng ở mục 3.1 của báo cáo. **Chỉ tiêu:** N₁ ≥ 70,
N₄ ≥ 45, N₅ ≈ 25.

## 6. Nhật ký tìm kiếm

Ghi **ngay khi tìm**, không ghi lại từ trí nhớ. Cột "Truy vấn nguyên văn" phải chép đúng
chuỗi đã gõ, để người khác lặp lại được.

| Ngày | Nguồn | Truy vấn nguyên văn | Số kết quả | Số giữ lại |
|---|---|---|---|---|
| | | | | |

## 7. Quy trình kiểm chứng — chống bịa trích dẫn

Quy tắc số 7 của repo cấm bịa trích dẫn. Ở đây quy tắc đó được **cưỡng chế bằng công cụ**,
không dựa vào trí nhớ.

Mỗi dòng trong `survey_matrix.csv` có cột `trang_thai` với đúng ba giá trị:

| Giá trị | Nghĩa | Được dùng ở đâu |
|---|---|---|
| `chua_kiem` | Mới có tên bài, chưa mở nguồn | Không được trích dẫn trong báo cáo |
| `da_kiem_url` | Đã mở trang gốc, xác nhận tác giả / năm / nơi công bố | Được đưa vào bảng 3.9 |
| `da_doc_toan_van` | Đã đọc hết bài, hiểu phương pháp và kết quả | Được phân tích sâu ở mục 3.2 – 3.8 |

Trường nào chưa xác minh được thì ghi `[CẦN TÌM: ...]`, **không đoán, không để trống**.

`scripts/survey_tools.py table` **từ chối sinh bảng 3.9** nếu còn dòng `chua_kiem` được
chọn đưa vào bảng. Đây là chốt chặn kỹ thuật: không thể vô tình đưa một trích dẫn chưa
kiểm chứng vào cuốn báo cáo.

**Lệnh dùng hằng ngày khi khảo sát:**

```bash
python scripts/survey_tools.py validate   # cấu trúc file có hợp lệ không
python scripts/survey_tools.py stats      # tiến độ: phủ 6 nhóm tới đâu, kiểm chứng bao nhiêu
python scripts/survey_tools.py table      # sinh bảng 3.9 (chỉ từ dòng đã kiểm chứng)
```

## 8. Bài báo quan trọng — gắn cờ bắt buộc đọc kỹ

Ngoài kiểm chứng để đưa vào Bảng 3.9, một số ít công trình (5–10 bài) quan trọng hơn hẳn
phần còn lại — loại mà nếu bảo vệ bị hỏi sâu mà không trả lời được thì mất điểm ngay. Những
bài đó được theo dõi riêng ở
[`chuyende1/survey/doc_bat_buoc.md`](doc_bat_buoc.md).

Quy tắc gắn cờ và tiêu chí "quan trọng": xem `README.md` mục "Quy định riêng của học viên"
phần D. Tóm tắt: mỗi khi phát hiện một bài như vậy, phải (1) thêm vào `doc_bat_buoc.md`,
(2) thêm dòng vào ma trận này nếu chưa có, (3) **nói rõ ngay trong câu trả lời** và yêu cầu
học viên đọc kỹ — không âm thầm thêm vào rồi đi tiếp.
