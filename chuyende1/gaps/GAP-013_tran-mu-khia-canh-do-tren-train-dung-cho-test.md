# GAP-013 — Trần mù khía cạnh đo trên tập TRAIN nhưng dùng làm trần cho tập TEST

**Ngày phát hiện:** 08/09/2026 · **Phát hiện bởi:** Claude Code (đo lại khi viết tài liệu so sánh với số công bố)
**Loại:** số liệu
**Mức độ:** nhẹ (không đổi kết luận, nhưng là lỗi phương pháp hội đồng bắt được)
**Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

`chuyende1/notes/CD1.4a_lexicon.md` mục "Phát hiện 2":

| | Ghi trong ghi chú | Đo trên tập nào (thật) |
|---|---|---|
| Câu có > 1 khía cạnh | 86,6 % | **train** |
| Câu có khía cạnh trái nhãn | 47,0 % | **train** |
| **Trần accuracy cho mô hình mù khía cạnh** | **80,2 %** | **train** |

Ba con số này **không ghi rõ đo trên tập nào**. Ngay dòng dưới, chúng được đem so với
`lexicon` đạt **74,7 %** — mà 74,7 % là **accuracy trên tập TEST**.

Đo lại đầy đủ:

| Tập | > 1 khía cạnh | Trái nhãn | Trần mù khía cạnh |
|---|---|---|---|
| train | 86,6 % | 47,0 % | **0,8022** |
| dev | — | — | 0,8145 |
| **test** | 86,7 % | **45,1 %** | **0,8088** |
| cả ba | — | — | 0,8047 |

Trần đúng để so với kết quả test là **80,88 %**, không phải 80,2 %.

## 2. Phát hiện thế nào

Đang đo lại mọi con số để viết tài liệu *"số nào so được với số nào"* (REQ-008) — nguyên tắc
tự đặt ra là **không viết con số nào theo trí nhớ**. Đo trên test ra 0,8088, lệch với 80,2 %
đã ghi. Truy ngược mới thấy 80,2 % là số của train.

**Cách phát hiện này đáng nhớ:** nó không phải nhờ test tự động hay đọc lại code, mà nhờ
**đo lại từ đầu thay vì chép số cũ**. Nếu lúc viết tài liệu tôi chép 80,2 % từ ghi chú
CD1.4a sang thì sai sót này đã đi thẳng vào báo cáo.

## 3. Nguyên nhân gốc

**Giả định ngầm không được viết ra.**

Lúc đo ở CD1.4a, tôi đang phân tích *tính chất của bài toán* nên đo trên tập lớn nhất
(train) — tự nó không sai. Cái sai là **không ghi tập nào vào cạnh con số**, rồi ngay sau đó
đem so với một con số của tập khác. Một chỉ số không kèm tập dữ liệu là một chỉ số chưa
hoàn chỉnh.

Đây **không** phải mẫu "một giá trị lan ra nhiều nơi" như GAP-004/005/006/009/012. Đây là
mẫu mới: **con số đúng, ngữ cảnh của nó bị mất trên đường đi.**

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| `chuyende1/notes/CD1.4a_lexicon.md` mục "Phát hiện 2" | Có — đã sửa |
| Kết luận *"`lexicon` đã dùng gần hết dư địa mù khía cạnh"* | **Không đổi.** 74,7 % so với 80,88 % vẫn là "gần hết dư địa" |
| Kết luận *"`bilstm` đã phá trần"* | **Không đổi, còn chắc hơn.** 85,82 % vượt cả 80,88 % lẫn 80,2 % |
| `results/lexicon_stats.json` | Không chứa ba con số này |
| Chương 5 báo cáo | Phải dùng **80,88 %** khi so với kết quả test |

Không có số liệu nào phải chạy lại.

## 5. Đã sửa thế nào

Sửa `chuyende1/notes/CD1.4a_lexicon.md`: bảng ghi **cả hai cột train và test**, ghi rõ tập
nào, và nói rõ **con số dùng để so với kết quả test là 80,88 %**.

## 6. Bài học — phòng lần sau bằng cách nào

**Mọi chỉ số về dữ liệu phải ghi kèm tập đo ngay trong tên hoặc trong ô bảng
("trần mù khía cạnh — test"), không để trong câu văn xung quanh.** Câu văn bị cắt khi chép
sang tài liệu khác; nhãn nằm trong ô bảng thì đi theo con số.

Và: **khi viết tài liệu tổng hợp, đo lại thay vì chép số từ ghi chú cũ.** Lần này chính
việc đo lại đã bắt được lỗi.

## 7. Có cần đưa vào báo cáo không

- [ ] Có — đưa vào mục 6.2
- [x] Không — đã sửa trước khi con số vào báo cáo, và kết luận không đổi.
      Nhưng **con số dùng trong Chương 5 phải là 80,88 % (test)**, đã ghi rõ trong ghi chú.
