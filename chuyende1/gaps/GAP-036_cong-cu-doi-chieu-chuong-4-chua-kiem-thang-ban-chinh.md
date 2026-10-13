# GAP-036 — Công cụ đối chiếu Chương 4 chưa kiểm thẳng được bản chính của báo cáo

**Ngày phát hiện:** 13/10/2026 · **Phát hiện bởi:** Claude Code, ngay sau khi học viên chọn bản rút gọn làm bản chính
**Loại:** công cụ kiểm · tài liệu
**Mức độ:** nhẹ lúc này (chưa con số nào lệch), thành trung bình khi mục 4.3 và 4.5 có số
**Trạng thái:** 🔴 Mở: chờ học viên đồng ý cho chỉnh công cụ

---

## 1. Sai ở đâu

Từ ngày 13/10/2026 bản chính của báo cáo là bản rút gọn (`chuyende1/report/nhap_rut_gon/`).
`scripts/doi_chieu_chuong4.py` tính lại 153 chỗ từ dữ liệu và file kết quả rồi tìm nguyên văn từng chỗ
trong một file, mặc định là Chương 4 của bản đầy đủ. Chạy trên bản chính:

| Đầu vào | Khớp | Lệch |
|---|---|---|
| Chương 4 của bản đầy đủ | 153 | 0 |
| Chương 4 của bản chính | 97 | 56 |
| Chương 4 và Phụ lục của bản chính, nối tạm thành một file | 146 | 7 |

56 chỗ lệch ở dòng thứ hai gồm 38 hàng của sáu bảng đã chuyển sang Phụ lục C, 9 câu của mục 4.1.2 đã
chuyển sang Phụ lục B, và 9 câu ở mục 4.4, 4.6, 4.7. Công cụ không đọc `PhuLuc.md`.

7 chỗ lệch ở dòng thứ ba đã được đọc tay ngày 13/10:

- 2 chỗ là câu đã viết lại, con số giữ nguyên: Sentic-GCN cao hơn ASGCN 1,07 điểm và thấp hơn PhoBERT
  0,14 điểm; ba hiệu số macro-F1 ở nhóm phủ định là 8,4, 7,5 và 6,5 điểm.
- 5 chỗ là câu đã bỏ khỏi bản chính, con số của chúng còn trong các hàng bảng giữ nguyên văn.

Không con số nào lệch. Thứ thiếu là một lần kiểm tự động chạy thẳng trên bản chính.

## 2. Phát hiện thế nào

Sau khi học viên chọn bản chính, Claude chạy từng công cụ đối chiếu trên thư mục của bản đó thay vì
suy ra từ kết quả của bản đầy đủ.

## 3. Nguyên nhân gốc

Công cụ được viết khi chỉ có một bản báo cáo: nó nhận một file, và các cụm chữ nó tìm là nguyên văn của
bản đầy đủ. Bản rút gọn chia Chương 4 ra hai file và viết lại một số câu.

## 4. Ảnh hưởng lan tới đâu

- Hôm nay số liệu của bản chính được bảo đảm theo đường vòng: `doi_chieu_ban_rut_gon.py` cho thấy không
  con số và không hàng bảng nào của bản chính nằm ngoài bản đầy đủ, còn bản đầy đủ khớp 153 trên 153.
- Đường vòng đó không biết một con số có còn nằm trong đúng câu hay không. Phần này đang dựa vào một
  lượt đọc tay 60 câu có số đã viết lại.
- Khi mục 4.3 và 4.5 có số đo, các số đó chỉ được viết vào bản chính. Nếu công cụ chưa được chỉnh thì
  chúng không có lần kiểm tự động nào.

## 5. Sẽ sửa thế nào

Chưa sửa. Việc cần làm khi học viên đồng ý, trước khi đưa số của mục 4.3 và 4.5 vào:

- Cho công cụ đọc cả Chương 4 và `PhuLuc.md` của bản chính.
- Sửa 7 cụm chữ theo lời văn của bản chính; 5 cụm của các câu đã bỏ thì kiểm ở hàng bảng tương ứng.
- Thêm các chỗ kiểm cho bảng chi phí suy luận và bảng mốc tham chiếu bằng mô hình ngôn ngữ lớn.
- Đích: 0 chỗ lệch khi chạy thẳng trên bản chính.

## 6. Bài học

Đổi bản chính thì phải đổi luôn đích của mọi công cụ kiểm, và chạy lại từng công cụ trên bản mới. Một
kết quả "khớp" chỉ nói về đúng cái file đã được đưa vào.
