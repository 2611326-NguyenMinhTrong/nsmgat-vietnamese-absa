# GAP-044 — Chương 5 đọc tỉ lệ mà không so với mức nền, và suy từ tập rút cân bằng nhãn ra toàn tập

**Ngày phát hiện:** 23/10/2026 · **Phát hiện bởi:** Claude Code, khi rà Chương 5 theo yêu cầu của học viên
**Loại:** tài liệu (lời văn báo cáo nói quá hoặc ngược với số liệu)
**Mức độ:** trung bình (con số đúng, kết luận rút ra sai hoặc rộng hơn bằng chứng; báo cáo chưa nộp)
**Trạng thái:** ✅ Đã sửa trong bản nháp và file Word ngày 23/10/2026 (phiếu CD1.11c)

---

## 1. Sai ở đâu

Chương 5 (viết ở CD1.11b, 18/10/2026) có 50 chỗ kiểm khớp, nhưng năm câu rút kết luận sai từ con số đúng:

| Chỗ | Câu cũ | Vì sao sai |
|---|---|---|
| 5.1, trung tính và PRICE | "Lớp này không khó chỉ vì nó hiếm", dẫn PRICE (57,6 % trung tính) có macro-F1 cao thứ ba | Số liệu nói ngược lại: PhoBERT tìm lại 87,6 % mẫu trung tính ở PRICE, 58,0 % ở chín khía cạnh còn lại, tức trung tính khó chính ở nơi nó hiếm |
| 5.1 và hạn chế 2, lỗi rơi vào nhãn kia | 60,3 đến 66,8 % lỗi ở bình luận hai nhãn rơi vào nhãn còn lại, "mô hình lấy ý kiến về khía cạnh khác" | Ba lớp nên một lỗi chỉ có hai chỗ để rơi; mức nền theo ma trận nhầm lẫn ngoài nhóm là 46,6 đến 48,5 %. Hiệu ứng có thật (14 đến 18 điểm) nhưng câu cũ coi cả tỉ lệ là bằng chứng |
| 5.4 cũ, sau Bảng 5.1 | "phần lớn lỗi là mẫu có nhãn gốc trung tính", rồi suy về luật lật cực nói chung | Đúng trên tập chẩn đoán (68 đến 79 %) vì tập này rút cân bằng nhãn; trên toàn tập kiểm tra chỉ 44,6 % số lỗi của PhoBERT. Kết luận về lật cực vẫn đứng vì lỗi ngược cực toàn tập chỉ 17,5 % |
| Hạn chế 4 | "hơn một nửa số lỗi ở ba nhóm có hiện tượng nằm ở mẫu không đồng ý", dùng làm bằng chứng nhãn kém tin cậy "đúng ở chỗ khó" | Nhóm thường cũng vậy (53 %); tỉ lệ không đồng ý ở nhóm phủ định (11,8 %) còn thấp hơn nhóm thường (12,5 %) |
| 5.1, lỗi chung | "Bốn mô hình dùng PhoBERT sai gần như ở cùng những mẫu" | Phần chung là 59 đến 66 % số lỗi cứng của từng mô hình, không phải "gần như" |

Kèm mười chỗ nhẹ hơn (thiếu trích dẫn, kết luận về cây cú pháp rộng hơn phép đo, coi trung tính là "không có ý kiến" dù bộ
dữ liệu không định nghĩa, bốn ca không nói cách chọn, thứ tự mục dùng bằng chứng trước khi trình bày), ghi ở phiếu CD1.11c.

## 2. Phát hiện thế nào

Đọc lại từng câu kết luận và hỏi hai câu: tỉ lệ này so với gì, và đo trên quần thể nào. Rồi tính lại từ dự đoán của 30 lần
chạy bằng một script tạm.

## 3. Nguyên nhân gốc

`doi_chieu_chuong5.py` kiểm đúng hai thứ: con số khớp nguồn, và câu định tính qua được một ngưỡng (`neu()`, ví dụ "hơn
một nửa" thì tỉ lệ > 0,5). Nó không kiểm ngưỡng đó có ý nghĩa không. "Hơn một nửa lỗi rơi vào nhãn kia" qua ngưỡng 0,5 trong
khi mức nền tự nhiên đã gần 0,5; "phần lớn lỗi có nhãn gốc trung tính" qua ngưỡng trên tập chẩn đoán trong khi tập này rút
cân bằng nhãn. Cùng họ với GAP-013 (con số đúng, mất ngữ cảnh) và GAP-042 (chữ chỉ mức độ là khẳng định định lượng), thêm
một dạng mới: tỉ lệ không có mốc so.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| Chương 5 bản chính (bản nháp và Word) | Đã sửa 15 chỗ, đổi thứ tự mục (5.2 ca điển hình, 5.3 thăm dò, 5.4 hạn chế) |
| `scripts/doi_chieu_chuong5.py` | Thêm chỗ kiểm cho mức nền, tìm lại trung tính theo khía cạnh, yếu tố đi cùng độ dài, phần lỗi trên toàn tập; 72 chỗ |
| Phiếu CD1.9, CD1.11, CD1.11b | Không sửa: ghi chép lịch sử. Câu "Bốn mô hình sai gần như cùng chỗ" ở CD1.9 có cùng lỗi |
| Tóm tắt, Chương 1, Chương 4 | Không: không dùng các câu này |

## 5. Đã sửa thế nào

Viết lại các câu theo số liệu (phiếu CD1.11c mục 3), mỗi số mới có chỗ kiểm tính từ dự đoán; ghép riêng Chương 5 vào Word
(`--chi 5 --ghi-de`) sau khi xác nhận từng ký tự và định dạng của Chương 5 trong Word chưa bị sửa tay.

## 6. Bài học — phòng lần sau bằng cách nào

Mỗi tỉ lệ dùng làm bằng chứng cho một cơ chế phải đi kèm mốc so: mức nền khi không có cơ chế đó, hoặc nhóm đối chứng. Mỗi tỉ
lệ đo trên tập chẩn đoán thì phải hỏi tập này rút thế nào trước khi suy ra tập kiểm tra. Khi viết `neu()`, điều kiện phải
là "khác mức nền" chứ không chỉ "qua ngưỡng".

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] Không — đã sửa câu trong báo cáo trước khi nộp
