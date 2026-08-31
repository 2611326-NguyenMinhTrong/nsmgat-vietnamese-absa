# PHIẾU BÀN GIAO — [CD1.x] <tên step>

> Mẫu này là bắt buộc sau mỗi step. Copy file này thành `CD1.x_<ten-ngan>.md`, điền đủ 7 mục,
> rồi mới commit. Mục 7 là mục **không được bỏ**: phải dừng lại hỏi trước khi sang step sau.
>
> Vì sao có phiếu này: học viên muốn *hiểu* chứ không chỉ *có* code. Ngoài ra đến Tuần 13,
> khi viết Chương 4 của cuốn chuyên đề, các phiếu này chính là bản nháp có sẵn của mục
> "phương pháp" và "quyết định thiết kế".

**Ngày:** … · **Step:** CD1.x · **Ánh xạ plan gốc:** S… · **Thời gian thực tế:** … giờ

---

## 1. ĐÃ LÀM GÌ — danh sách thay đổi

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| | | |

Nếu có chạy thí nghiệm: ghi lệnh đã chạy nguyên văn.

```bash

```

---

## 2. ĐỂ LÀM GÌ — vấn đề mà phần này giải quyết

- **Vấn đề:** trước step này, cái gì chưa làm được?
- **Sau step này:** làm được gì mà trước đó không?
- **Nếu bỏ step này thì hỏng ở đâu:** step nào sau đó sẽ không chạy được, hoặc kết luận nào
  trong báo cáo sẽ mất chỗ dựa?

---

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

Giải thích cách phần vừa viết thực sự hoạt động, ở mức người khác đọc xong có thể tự cài lại.
Ưu tiên: một ví dụ cụ thể chạy xuyên suốt (một câu tiếng Việt thật, một tensor có số đo thật)
hơn là mô tả trừu tượng.

- Ý tưởng cốt lõi trong 2–3 câu:
- Đi qua một ví dụ cụ thể (đầu vào → từng bước → đầu ra):
- Chỗ dễ hiểu sai nhất:

---

## 4. QUYẾT ĐỊNH THIẾT KẾ — và phương án đã loại

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| | | | |

Ghi cả những chỗ chỉ là quy ước (đặt tên, thứ tự cột) — sau 2 tháng sẽ không nhớ vì sao.

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Step kế tiếp là: **CD1.y — …**
- Nó sẽ dùng lại từ step này: (hàm / file / định dạng dữ liệu nào)
- Giao diện giữa hai step: (chữ ký hàm, schema file trung gian)
- Điều kiện tiên quyết còn thiếu (nếu có):

---

## 6. KIỂM CHỨNG — bằng chứng chạy thật

```bash
pytest tests/ -q
```

- Kết quả test (dán output thật, không viết "đã pass"):
- Số liệu thu được (nếu có), và **đường dẫn file** để truy nguồn:
- Sự cố gặp phải và cách xử lý:

> Quy tắc số 7 của repo: không bịa số liệu. Chưa chạy được thì ghi `[TODO: cần chạy X]`.

---

## 7. DỪNG LẠI VÀ HỎI  ← không được bỏ mục này

**Câu hỏi mở của tôi gửi học viên** (chỗ tôi không chắc, cần bạn quyết):

1.

**Những chỗ tôi đoán học viên có thể muốn hỏi thêm** (gợi ý để bạn chọn, không bắt buộc):

- …?
- …?

**Kết:**
> Bạn có câu hỏi phụ nào về phần này không, hay tôi đi tiếp sang **CD1.y — …**?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI *(điền sau, nếu học viên có hỏi thêm)*

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
