# GAP-042 — Chương 4 viết "phần lớn khoảng cách đến từ cách đọc ra", trong khi hai phần gần bằng nhau

**Ngày phát hiện:** 17/10/2026 · **Phát hiện bởi:** Claude Code, khi viết lại Chương 4 bỏ các số đọc lại từ bảng (CD1.12o)
**Loại:** tài liệu (lời văn báo cáo nói quá số liệu)
**Mức độ:** nhẹ (hướng kết luận đúng, mức độ nói quá; báo cáo chưa nộp)
**Trạng thái:** ✅ Đã sửa trong bản nháp và file Word ngày 17/10/2026

---

## 1. Sai ở đâu

Mục 4.4 bản chính (viết ở CD1.12l), đoạn sau Bảng thí nghiệm đối chứng:

> Như vậy phần lớn khoảng cách giữa ASGCN và PhoBERT đến từ cách đọc ra chứ không từ cây phụ thuộc, và không thành phần
> đồ thị nào cho lợi ích đo được.

Số của chính bảng đó: đổi cách đọc ra −0,63 điểm macro-F1, thêm GCN trên cây phụ thuộc −0,58 điểm, tắt độ chính xác hỗn hợp
+0,32 điểm; tổng khoảng cách ASGCN trừ PhoBERT −0,88 điểm. Hai phần âm gần bằng nhau về độ lớn. Chỗ khác nhau thật là ở phép
kiểm định: phần đọc ra có ý nghĩa ở cả bootstrap và phép hoán vị seed (p 0,007 và 0,018), phần cây phụ thuộc chỉ có ý nghĩa
ở bootstrap (p 0,010) và không qua phép hoán vị (p 0,310). GAP-040 đã ghi đúng là "khoảng một nửa".

## 2. Phát hiện thế nào

Viết lại câu này mà không dùng con số, Claude phải nói rõ "phần lớn" dựa trên đâu, và đặt hai hiệu số cạnh nhau.

## 3. Nguyên nhân gốc

Câu viết theo kết luận của phép hoán vị (chỉ phần đọc ra vượt được dao động giữa các seed) nhưng diễn đạt thành tỉ lệ độ
lớn ("phần lớn"). Công cụ đối chiếu chỉ kiểm con số đi kèm (−0,63), không kiểm chữ "phần lớn".

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| Mục 4.4 bản chính | Đã sửa: "chỉ phần do đổi cách đọc ra là vượt được dao động giữa các lần huấn luyện lại" |
| Mục 4.7 bản chính | Viết lại cùng ý: "phần giảm đo được chắc chắn đến từ việc đổi cách đọc ra" |
| Phần tóm tắt | Không: chỉ nói phần đồ thị không đem lại lợi ích đo được |
| Bản lưu (bản đầy đủ) | Không: bản lưu không có thí nghiệm đối chứng |

## 5. Đã sửa thế nào

Sửa hai câu ở mục 4.4 và 4.7; `scripts/doi_chieu_chuong4.py` kiểm hai câu mới bằng neu() với điều kiện: chỉ bước đổi cách
đọc ra có ý nghĩa ở cả hai phép kiểm định, và bước cây phụ thuộc không qua phép hoán vị.

## 6. Bài học — phòng lần sau bằng cách nào

Từ chỉ mức độ ("phần lớn", "chủ yếu", "gần hết") là một khẳng định định lượng: phải tính tỉ lệ thật trước khi viết, hoặc
thay bằng điều kiểm định thật sự cho thấy.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] Không — đã sửa câu trong báo cáo trước khi nộp
