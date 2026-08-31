# GAP-002 — Sentic-GCN cần từ điển cảm xúc tiếng Việt, nhưng bước dựng từ điển thuộc CĐ2

**Ngày phát hiện:** 27/08/2026 · **Phát hiện bởi:** Claude Code (khi đọc đặc tả S1.2)
**Loại:** phương pháp · **Mức độ:** **nghiêm trọng** (ảnh hưởng kết luận) · **Trạng thái:** 🔴 Mở

---

## 1. Sai ở đâu

Sentic-GCN (Liang et al., 2022) dùng **SenticNet** để tăng cường trọng số cạnh của đồ thị
phụ thuộc bằng điểm cảm xúc của từng token. SenticNet là tài nguyên **tiếng Anh** — không có
bản tiếng Việt tương đương chất lượng.

Đặc tả S1.2 đã lường trước và cho hai lựa chọn:

> "…và từ điển cảm xúc tiếng Việt (**VietSentiWordNet** hoặc **từ điển tự dựng ở S2.1**)."

Nhưng **S2.1 (xây từ điển + đặc tả luật) thuộc Chuyên đề 2**. Vậy CD1.5 chỉ còn một đường:
VietSentiWordNet — một tài nguyên mà chất lượng và độ phủ trên miền bình luận điện thoại
(teencode, viết tắt, sai chính tả) **chưa được kiểm chứng**.

## 2. Rủi ro cụ thể

Nếu từ điển phủ kém, Sentic-GCN sẽ cho kết quả thấp. Khi đó có **hai cách giải thích** mà
ta không phân biệt được:

1. Phương pháp đồ thị + tri thức cảm xúc thật sự không hợp với bài toán này *(kết luận khoa học)*
2. Từ điển tiếng Việt quá thưa nên phần "tri thức cảm xúc" gần như bị vô hiệu hoá
   *(lỗi triển khai)*

Kết luận (1) mà thật ra là (2) thì **sai một cách nguy hiểm**: nó làm đóng góp của CĐ2 trông
to hơn thực tế, và phản biện có kinh nghiệm sẽ hỏi đúng chỗ này. Liên quan tới rủi ro **R3**
trong plan ("Sentic-GCN thua PhoBERT quá nhiều — gần như luôn là lỗi cài đặt").

## 3. Nguyên nhân gốc

**Cắt module theo mốc học vụ, nhưng phụ thuộc kỹ thuật không cắt theo mốc đó.** Khi tách CĐ1
khỏi CĐ2, tôi lấy ranh giới ở "baseline thuộc CĐ1, symbolic thuộc CĐ2" — nhưng một baseline
của CĐ1 lại cần một tài nguyên mà kế hoạch xếp vào CĐ2.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Ghi chú |
|---|---|
| CD1.5 (Sentic-GCN) | Chưa chạy |
| Bảng kết quả chính, Chương 4 | Nếu số của Sentic-GCN không đáng tin thì cả bảng bị nghi ngờ |
| Chương 5, hạn chế "cú pháp chưa đủ" | Luận cứ này dựa vào Sentic-GCN |
| Hiệu số `NS-MGAT − Sentic-GCN` ở CĐ2 | Đây là phép đo đóng góp — sai mốc là sai cả đóng góp |

## 5. Phương án xử lý — chưa chốt, cần học viên quyết

| Phương án | Nội dung | Đánh đổi |
|---|---|---|
| **A** *(khuyến nghị)* | Thêm **bước kiểm tra chất lượng từ điển** vào đầu CD1.5: đo độ phủ của VietSentiWordNet trên tập train (bao nhiêu % token cảm xúc được gán điểm), và báo cáo con số này trong Chương 4 | Tốn ~0,5 ngày; đổi lại loại được cách giải thích (2) |
| **B** | Kéo một phần S2.1 lên CĐ1 — tự dựng từ điển cảm xúc tối giản | Vi phạm ranh giới module; lấn việc của CĐ2 |
| **C** | Đổi baseline sang **ASGCN** (GCN thuần cú pháp, không cần từ điển cảm xúc) | Mất mất "tri thức cảm xúc" khỏi phép so, hiệu số CĐ2 kém sạch hơn |
| **D** | Chạy **cả Sentic-GCN và ASGCN** | Thêm ~1 ngày GPU; nhưng tách bạch được đóng góp của cú pháp và của tri thức cảm xúc |

## 6. Bài học *(điền sau khi chốt phương án)*

Khi cắt module theo mốc học vụ, phải rà **phụ thuộc tài nguyên** (từ điển, checkpoint, dữ liệu
ngoài) chứ không chỉ phụ thuộc code.

## 7. Có cần đưa vào báo cáo không

- [x] **Có** — dù xử lý theo phương án nào, độ phủ của từ điển cảm xúc phải được nêu trong
      mục 4.3 (mô tả mô hình) và nhắc lại ở mục 6.2 (hạn chế).
