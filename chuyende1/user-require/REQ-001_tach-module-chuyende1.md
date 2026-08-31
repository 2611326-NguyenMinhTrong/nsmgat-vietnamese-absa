# REQ-001 — Tách Chuyên đề 1 thành module riêng

**Ngày yêu cầu:** 27/08/2026 · **Trạng thái:** ✅ Xong

---

## 1. Yêu cầu nguyên văn

> "tách riêng phần chuyên đề 1 này ra thành một module nhỏ trong project đi, những phần nào
> có thể dùng chung thì dùng nhưng tôi không muốn sản phẩm luận văn lộn xộn giữa các chuyên
> đề + luận văn"

## 2. Hiểu thành gì

Hai vế, không mâu thuẫn nhau nếu tách đúng chiều:

- *"phần nào dùng chung thì dùng"* → code, dữ liệu, kết quả thí nghiệm **không** nhân bản
  theo môn học.
- *"không lộn xộn giữa các chuyên đề + luận văn"* → văn bản nộp của từng môn phải ở nơi
  riêng, không trộn.

Chiều tách đúng: **theo loại tài sản**, không theo môn học.

## 3. Vì sao học viên muốn thế

Ba sản phẩm học vụ (CĐ1 → CĐ2 → luận văn) dùng chung một nền kỹ thuật nhưng nộp ở ba thời
điểm khác nhau cho ba hội đồng khác nhau. Nếu để chung, đến khi làm CĐ2 sẽ không biết bảng
biểu nào thuộc bản đã nộp.

## 4. Đã làm gì để đáp ứng

| File | Tạo/Sửa | Nội dung |
|---|---|---|
| `chuyende1/MODULE.md` | Tạo | Hợp đồng ranh giới: 3 vùng repo, sở hữu/được ghi/cấm động, tài sản bàn giao cho CĐ2 |
| `chuyende1/{survey,report,tables,figures,slides,notes}/` | Tạo | Thư mục sở hữu riêng của module |
| `chuyende2/MODULE.md` | Tạo | Giữ chỗ + danh sách tài sản nhận bàn giao |
| `README.md` | Sửa | Mục "Cấu trúc thư mục" → mô hình 3 vùng; thêm mục B "Ranh giới module" |
| `pLan/chuyende1/*.md` | Sửa | Đổi đường dẫn `docs/survey/` → `chuyende1/survey/`, `reports/chuyende1/` → `chuyende1/report|tables|figures/` |
| `chuyende1/notes/CD1.0_tach-module.md` | Tạo | Phiếu bàn giao cho chính thay đổi này |

**Quyết định then chốt:** `results/` **giữ phẳng**, không tách theo module. Lý do: schema
`results/{exp}/seed{N}/metrics.json` đóng băng ở S0.4 và `make_tables.py` chỉ đọc đúng đường
dẫn đó — đổi thành `results/cd1/{exp}/` là phá hợp đồng. Quyền sở hữu khai báo trong
`MODULE.md`, không mã hoá vào đường dẫn.

## 5. Chi phí

- **Một lần:** ~2 giờ
- **Lặp lại:** không đáng kể (đọc `MODULE.md` trước khi tạo file mới)
- **Cả kỳ:** ~2 giờ

## 6. Có làm lệch kế hoạch gốc không

- [x] **Có, nhưng không đội lịch** — thuần tuý tổ chức lại thư mục, không thêm việc nghiên cứu.
      Đã ghi vào "Sổ quyết định" (`progress_cd1.md`, dòng 27/08/2026).

## 7. Việc phát sinh về sau

Có: mỗi lần tạo file mới phải xác định thuộc vùng nào.
Đã ghi vào `README.md` mục "Quy định riêng của học viên" phần **B — Ranh giới module**.

Một việc còn treo: khi bắt đầu Chuyên đề 2, phải dựng `chuyende2/` theo đúng khuôn này —
đã ghi sẵn trong `chuyende2/MODULE.md`.
