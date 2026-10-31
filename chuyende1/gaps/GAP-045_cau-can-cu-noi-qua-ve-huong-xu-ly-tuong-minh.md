# GAP-045 — Báo cáo gọi số đo trên tập chẩn đoán là "căn cứ" cho hướng xử lý tường minh, và chưa nói rõ tiêu chí, lý do

**Ngày phát hiện:** 31/10/2026 · **Phát hiện bởi:** giảng viên hướng dẫn, qua sáu câu hỏi gửi học viên
**Loại:** tài liệu, phương pháp (lời văn rộng hơn bằng chứng; thiếu nội dung bắt buộc phải có khi bảo vệ)
**Mức độ:** nghiêm trọng nếu lọt vào bản nộp (đúng câu hội đồng sẽ hỏi; báo cáo chưa nộp)
**Trạng thái:** ✅ Đã sửa trong bản nháp và file Word ngày 31/10/2026 (phiếu CD1.12r)

---

## 1. Sai ở đâu

| Chỗ | Câu hoặc chỗ thiếu | Vì sao sai |
|---|---|---|
| Tóm tắt | "Đây là căn cứ để chuyên đề sau tập trung xử lý tường minh phủ định và chuyển ý." | Số đo cho biết hai hiện tượng khó hơn, không cho biết xử lý tường minh sẽ giúp. Mục 5.3 còn cho thấy luật lật cực gần như vô tác dụng |
| Mục 4.7 | "Đây là căn cứ thực nghiệm cho hướng xử lý tường minh ..." | Như trên, lại đứng ngay sau câu nói mô hình đồ thị không thu hẹp được khoảng cách |
| Mục 5.5 cũ | Giữ khung mô hình nhưng không nói vì sao vẫn chọn đồ thị khi Chương 4 cho kết quả âm | Người đọc thấy mâu thuẫn, chính là câu hỏi thứ nhất của giảng viên |
| Mục 4.1.2 | Không có tiêu chí xếp nhóm, chỉ dẫn sang Phụ lục B và hướng dẫn chú thích (không in kèm) | Không đánh giá được kết quả mục 4.6 nếu không biết nhóm được định nghĩa thế nào |
| Mục 4.1.1, 6.2 | Không nói vì sao chỉ dùng UIT-ViSFD | Mục 6.2 ghi là hạn chế nhưng không có lý do; mục 6.3 để "nếu còn điều kiện" |
| Chương 4, 5 | Các giải thích vì sao đồ thị không giúp nằm rải rác ở mục 4.3, 4.4, 5.3 | Chưa có chỗ nào trả lời trực tiếp, cũng chưa kiểm cách giải thích nào đứng được |
| Mục 5.2 | Bốn ca minh hoạ nhưng không nói lỗi nào phổ biến nhất của PhoBERT | Bảng 5.1 cũ có số nhưng gộp theo mục đích thăm dò, không theo loại lỗi |

## 2. Phát hiện thế nào

Giảng viên hướng dẫn đọc bản báo cáo và đặt sáu câu hỏi. Kiểm lại thì phiếu CD1.12q mục 5 đã ghi "Tóm tắt và đoạn cuối mục 4.7 chưa
khớp mục 5.5" và câu hỏi đó chưa được chốt, nên hai câu này còn nguyên khi báo cáo đến tay giảng viên.

## 3. Nguyên nhân gốc

Công cụ đối chiếu kiểm con số và điều kiện của câu (`neu`), không kiểm một câu kết luận có đi xa hơn bằng chứng về mặt lập luận
hay không. "Đây là căn cứ" không chứa con số nào nên không có chỗ kiểm. Cùng họ với GAP-044: số đúng, kết luận rộng hơn số. Mẫu
mới: đặt câu chuyển ý từ kết quả sang hướng đề tài theo mong muốn của đề tài, không hỏi "số này loại trừ được khả năng ngược lại
chưa". Phiếu CD1.12q đã thấy chỗ lệch nhưng để thành câu hỏi, thay vì sửa ngay phần chữ không tốn công.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| Tóm tắt, mục 1.5, 4.1.1, 4.1.2, 4.7, Chương 5, Chương 6 | Đã sửa (phiếu CD1.12r) |
| Mục 1.1 "là nơi các mô hình dễ sai" | Không: đúng với tỉ lệ sai đo được |
| Phụ lục B, C trực tuyến | Không: số liệu không đổi, không cần đổi mã commit ghim |
| Phiếu CD1.11, CD1.12q | Không sửa: ghi chép lịch sử |

## 5. Đã sửa thế nào

Xem phiếu CD1.12r. Hai câu "căn cứ" được thay bằng câu nói đúng mức: có dư địa, chưa chứng minh. Thêm phép đo ở
`scripts/phan_tich_bo_sung.py` để câu trả lời có số chạy lại được, và thêm chỗ kiểm cho mọi số, mọi nhận định mới.

## 6. Bài học — phòng lần sau bằng cách nào

Với mỗi câu dẫn từ kết quả sang hướng nghiên cứu, viết kèm câu đối lập: "nếu hướng này không có tác dụng thì số đo có khác đi không?".
Không khác thì số đo đó không phải căn cứ, chỉ là động cơ. Khi một phiếu ghi "chỗ này chưa khớp", sửa luôn nếu chỉ là chữ.

## 7. Có cần đưa vào báo cáo không

- [x] Có — nội dung đã đưa vào mục 5.6.1, 5.6.2 và 6.1 dưới dạng câu nói rõ hướng đề xuất là giả thuyết
- [ ] Không
