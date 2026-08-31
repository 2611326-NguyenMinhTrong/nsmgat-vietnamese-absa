# GAP-001 — Ranh giới sở hữu `models/layers.py` đặt sai mức

**Ngày phát hiện:** 27/08/2026 · **Phát hiện bởi:** Claude Code (khi đọc lại đặc tả S1.2)
**Loại:** tài liệu · **Mức độ:** nhẹ · **Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

`chuyende1/MODULE.md` mục 2.3 ghi `src/nsmgat/models/layers.py` vào danh sách
"KHÔNG ĐƯỢC ĐỘNG VÀO — thuộc Chuyên đề 2".

Nhưng `pLan/PLAN_NSMGAT.md` mục S1.2 (= CD1.5, Sentic-GCN) yêu cầu rõ:

> FILE 2: `src/nsmgat/models/layers.py` — class `GCNLayer` tái sử dụng được
> (sẽ dùng lại ở NS-MGAT). Nhận `(x, adj) -> x'`. Có normalize đối xứng.
> Yêu cầu quan trọng: `GCNLayer` phải viết tổng quát để Stage 4 dùng lại
> cho 3 đồ thị mà không phải sửa.

Tức là CĐ1 **bắt buộc** phải tạo file đó ở CD1.5. Nếu tuân theo `MODULE.md` như đã viết,
CD1.5 sẽ bị chặn.

## 2. Phát hiện thế nào

Học viên hỏi *"tại sao chọn 4 baseline này?"*. Để trả lời cho chắc, tôi đọc lại đặc tả S1.2
trong plan gốc thay vì trả lời từ trí nhớ — và thấy dòng "FILE 2: layers.py".

Đáng chú ý: sai sót lộ ra **không phải do ai đi tìm nó**, mà do một câu hỏi buộc phải quay
lại đọc nguồn gốc.

## 3. Nguyên nhân gốc

**Đặt ranh giới sai mức: theo *file* thay vì theo *class*.**

Khi viết `MODULE.md`, tôi phân loại file theo cảm nhận "file này nghe có vẻ thuộc mô hình
NS-MGAT" mà không mở đặc tả của mọi step có nhắc tới nó. `layers.py` chứa hai class thuộc
hai giai đoạn khác nhau:

| Class | Thuộc | Sinh ra ở |
|---|---|---|
| `GCNLayer` | Chuyên đề 1 | CD1.5 (S1.2) |
| `EdgeAwareAttention` | Chuyên đề 2 | S4.1 |

Ranh giới module chỉ đúng khi bám theo **đơn vị mà đặc tả thao tác** — ở đây là class,
không phải file.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Phải sửa theo |
|---|---|
| `chuyende1/MODULE.md` mục 2.3 | ✅ đã sửa |
| CD1.5 (chưa bắt đầu) | Không — phát hiện trước khi code |

Chưa sinh ra số liệu nào nên không có kết quả nào phải chạy lại.

## 5. Đã sửa thế nào

`chuyende1/MODULE.md` mục 2.3: tách dòng `layers.py` thành ghi chú theo class — cấm
`EdgeAwareAttention`, cho phép `GCNLayer` ở CD1.5, và nói rõ *"ranh giới ở đây là theo class,
không theo file"*.

## 6. Bài học

**Trước khi viết ranh giới sở hữu cho một file, `grep` tên file đó trong `PLAN_NSMGAT.md` và
đọc mọi step có nhắc tới nó.** Một file bị nhiều step chạm vào thì ranh giới phải hạ xuống
mức class/hàm, không dừng ở mức file.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — sai sót nội bộ về tài liệu, phát hiện và sửa trước khi code, không ảnh hưởng
      kết quả hay kết luận nào.
