# GAP-025 — Phễu sàng lọc ghi 24 bài tìm mới, ma trận có 25: một bài không có truy vấn nào trong nhật ký

**Ngày phát hiện:** 05/10/2026 · **Phát hiện bởi:** Claude Code (khi tính lại số cho mục 3.1 của báo cáo)
**Loại:** số liệu · **Mức độ:** nhẹ (lệch một đơn vị, nhưng nằm đúng ở sơ đồ hội đồng sẽ hỏi) · **Trạng thái:** 🟡 Đã sửa con số, còn một câu hỏi chưa trả lời được

---

## 1. Sai ở đâu

`chuyende1/survey/survey_protocol.md` mục 5 ghi rằng 45 dòng đã kiểm chứng ngày 22/09 gồm
"24 dòng đi qua phễu tìm kiếm có ghi log và 21 dòng hạt giống".

Đếm lại từ chính `survey_matrix.csv` ngày 05/10/2026:

| Cách đếm | Kết quả |
|---|---|
| Tổng cột "Số giữ lại" của 28 truy vấn trong nhật ký mục 6 | 24 |
| Số dòng mà `ghi_chu` ghi "Tim moi 22/09/2026" | **25** |
| Số dòng hạt giống | 22, trong đó 21 đã kiểm chứng tính tới 05/10 |

Dòng thừa ra là `VoZhang2015`. `ghi_chu` của nó ghi là tìm mới ngày 22/09, nhưng nhật ký tìm
kiếm không có truy vấn nào nhắc tới bài này, cũng không có dòng "giữ lại" nào ghi chú thêm nó.

Vậy mốc 45 của ngày 22/09 thực tế là 24 qua phễu, 1 không có nhật ký và **20** hạt giống đã
kiểm chứng, chứ không phải 24 và 21.

## 2. Phát hiện thế nào

Khi viết mục 3.1 của bản nháp Chương 3, không chép số từ giao thức mà đếm lại từ ma trận và
từ nhật ký. Hai cách đếm ra hai số khác nhau. Đây đúng là quy tắc rút từ GAP-013: viết tài
liệu tổng hợp thì đo lại từ đầu.

## 3. Nguyên nhân gốc

**Con số trong đoạn giải thích được suy ra bằng phép trừ, không được đếm.** Nhiều khả năng
"21 hạt giống" có được bằng cách lấy 45 trừ 24, thay vì đếm số dòng hạt giống đã kiểm chứng.
Phép trừ luôn cho tổng đúng nên không ai thấy sai.

Còn vì sao `VoZhang2015` không có trong nhật ký thì **không xác định được** từ những gì còn
ghi lại. Bảng tiến độ ghi đợt 2 tìm được 12 công trình bằng 12 truy vấn với 11 bài giữ lại,
tức sự lệch đã có ngay từ ngày 22/09. Có thể bài này lộ ra trong kết quả của một truy vấn khác
hoặc qua bảng so sánh của một bài đang đọc, nhưng đó là phỏng đoán.

Quy tắc của chính giao thức, mục 6, đã lường trước chuyện này: "ghi ngay lúc đang tìm, không
ghi lại từ trí nhớ". Một bài lọt khỏi nhật ký là đúng loại sai sót mà quy tắc đó nhắm tới.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| `survey_protocol.md` mục 5, đoạn giải thích N₄ | Có, đã sửa |
| Sơ đồ luồng sàng lọc ở mục 3.1 của báo cáo | Có. Bản nháp Chương 3 viết theo số đã đếm lại, ba nhánh |
| Nội dung dòng `VoZhang2015` trong ma trận | Không. Bài đã đọc toàn văn, số liệu đã đối chiếu Bảng 5 của bài |
| N₁ = 258, N₂ = N₃ = 24 | Không. Đếm lại khớp |

Không con số thực nghiệm nào bị ảnh hưởng.

## 5. Đã sửa thế nào

- `survey_protocol.md` mục 5: thay đoạn hai nhánh bằng bảng ba phần 24, 1 và 21, kèm cảnh báo
  về bản cũ.
- Bản nháp Chương 3 mục 3.1 nêu đúng ba phần, và đánh dấu bài lọt nhật ký bằng `[CẦN KIỂM]`.

**Chưa sửa được:** nguồn gốc của `VoZhang2015`. Hai cách xử lý, chờ học viên quyết:

1. Gõ lại một truy vấn tìm đúng bài này, ghi vào nhật ký mục 6 với ngày thật là ngày gõ lại,
   và ghi rõ là bổ sung sau.
2. Giữ nguyên, và trong mục 3.1 nói thẳng có một bài vào ma trận ngoài nhật ký tìm kiếm.

Không được viết "tìm bằng truy vết trích dẫn" khi chưa có bằng chứng, dù giao thức có cho phép
chiến lược đó.

## 6. Bài học — phòng lần sau bằng cách nào

**Mỗi số hạng của một phép cộng phải được đếm độc lập, rồi mới cộng để kiểm tổng.** Lấy tổng
trừ đi một số hạng để ra số hạng kia thì tổng luôn khớp và sai sót không bao giờ lộ.

## 7. Có cần đưa vào báo cáo không

- [x] **Có**, nếu học viên chọn cách 2 ở mục 5: một câu trong mục 3.1.
- [ ] Không, nếu chọn cách 1 và nhật ký được bổ sung.
