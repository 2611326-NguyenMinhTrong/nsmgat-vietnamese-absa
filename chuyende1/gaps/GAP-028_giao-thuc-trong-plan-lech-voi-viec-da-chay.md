# GAP-028 — Giao thức thực nghiệm ghi trong plan lệch với việc đã chạy ở hai điểm

**Ngày phát hiện:** 06/10/2026 · **Phát hiện bởi:** Claude Code (khi viết mục 4.2 của bản nháp Chương 4)
**Loại:** phương pháp · **Mức độ:** trung bình (không sai số liệu, nhưng báo cáo sẽ mô tả sai nếu chép từ plan) · **Trạng thái:** ✅ Đã chốt phương án A ngày 06/10/2026

---

## 1. Sai ở đâu

`pLan/chuyende1/PLAN_CHUYENDE1.md` mục 6.1 chốt hai điều mà 18 lần chạy đã có đều không làm theo:

| Yếu tố | Plan ghi | Việc đã chạy |
|---|---|---|
| Độ dài tối đa | 256 sub-token | `max_seq_len: 128` ở `configs/base.yaml`, mọi mô hình kế thừa |
| Ngân sách tinh chỉnh | Mỗi mô hình thử đúng 3 learning rate {1e-5, 2e-5, 3e-5} trên seed 42, chọn theo dev | Mỗi mô hình chạy đúng **một** cấu hình, không dò gì |

Dàn ý `OUTLINE_BAOCAO_CD1.md` mục 4.2 yêu cầu ghi "ngân sách tinh chỉnh bằng nhau cho mọi mô hình".

## 2. Phát hiện thế nào

Viết mục 4.2 từ file config và log thay vì từ plan. Hai chỗ không khớp lộ ra khi đối chiếu.

## 3. Nguyên nhân gốc

Plan viết trước khi có config. Khi viết `base.yaml` và từng config con, giá trị được chọn tại
chỗ và không ai quay lại sửa plan hay ghi vào Sổ quyết định. Sổ quyết định không có dòng nào
về 128 hay về việc bỏ dò learning rate.

## 4. Ảnh hưởng lan tới đâu

- Số liệu: **không ảnh hưởng**. Mọi mô hình cùng 128 và cùng không dò, nên so sánh vẫn công bằng.
- Tỉ lệ bị cắt ở 128, đo ngày 06/10 bằng đoạn mã tạm (cặp câu và khía cạnh, tokenizer
  `vinai/phobert-base-v2`): train 393 / 23.872 = 1,65 %, dev 35 / 3.316 = 1,06 %,
  test 110 / 6.722 = 1,64 %. Chưa đối chiếu với đúng `ACSADataset`.
- Báo cáo: mục 4.2 của bản nháp đã viết theo việc đã chạy, kèm câu nói rõ các con số chưa phải
  kết quả tốt nhất của từng mô hình.
- Bảo vệ: câu hỏi "em có tinh chỉnh siêu tham số không" phải trả lời là không.

## 5. Phương án

- **A.** Giữ nguyên, sửa plan cho khớp, ghi vào Sổ quyết định. Tốn 0 giờ GPU. Điểm yếu: không
  biết các hiệu số nhỏ (dưới 1,3 điểm) có đổi khi đổi learning rate không.
- **B.** Dò 3 learning rate trên seed 42 cho bốn mô hình dùng PhoBERT: thêm 8 lần chạy, ước
  khoảng 8 đến 9 giờ T4. Nếu learning rate tốt nhất khác 2e-5 thì phải chạy lại cả 3 seed.

**Chốt 06/10/2026: phương án A.** Học viên giao Claude chọn phương án tốt nhất. Lý do chọn A: so sánh vẫn công bằng vì mọi mô hình cùng một cách đối xử; B tốn 8 đến 9 giờ T4 và có thể kéo theo chạy lại cả 12 lần chạy dùng PhoBERT, trong khi đường găng của chuyên đề là tập chẩn đoán và phân tích lỗi, không phải điểm số. Hệ quả phải mang theo: mục 4.2 và 1.6 của báo cáo nói rõ không dò siêu tham số, mục 6.2 ghi đây là hạn chế, và mọi hiệu số dưới 1,3 điểm không được diễn giải mạnh. Đã sửa `PLAN_CHUYENDE1.md` mục 6.1 cho khớp.

## 6. Bài học

Giá trị nào đã chốt trong plan mà config chọn khác đi thì ghi một dòng vào Sổ quyết định ngay
lúc viết config. Khi viết chương thực nghiệm, lấy số từ config và log, không lấy từ plan.

## 7. Có cần đưa vào báo cáo không

- [x] **Có** — mục 4.2 (đã viết) và mục 6.2 (hạn chế: mỗi mô hình một cấu hình).
- [ ] Không
