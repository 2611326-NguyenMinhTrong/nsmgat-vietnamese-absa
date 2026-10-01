# GAP-019 — Đáp án trắc nghiệm lặp theo chu kỳ, đoán được mà không cần đọc bài

**Ngày phát hiện:** 01/10/2026 · **Phát hiện bởi:** Claude Code (lúc chấm bài)
**Loại:** phương pháp (công cụ đo) · **Mức độ:** **nghiêm trọng** (phép đo mất hiệu lực) · **Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

Đề trắc nghiệm 02 (bài ASGCN) có dãy đáp án:

```
A C B D   A C B D   A C B D   A C B
```

Chu kỳ 4 lặp lại trọn vẹn. Ai nhận ra quy luật sau tám câu đầu thì điền đúng bảy câu
còn lại mà không cần đọc bài báo.

Học viên làm bài được **15/15**, phiếu trả lời trùng khít dãy trên. Không có cách nào
phân biệt "đọc kỹ rồi trả lời đúng" với "nhận ra quy luật" từ dữ liệu này — và đó chính
là vấn đề: **bài kiểm tra mất khả năng phân biệt**, bất kể học viên đã thật sự đọc hay chưa.

## 2. Vì sao nghiêm trọng

Bộ trắc nghiệm sinh ra để biến "đã đọc kỹ" (REQ-005) từ lời tự khai thành thứ đo được
(REQ-009). Một đề đoán được phá đúng công dụng đó, mà lại phá một cách im lặng: điểm cao
trông như bằng chứng tốt.

Nặng hơn nữa, bảy câu trọng yếu của đề này là những chỗ quyết định cách cài `asgcn` ở
CD1.6a. Nếu học viên chưa thật sự nắm mà đề vẫn báo đạt, sai sót sẽ đi thẳng vào code.

## 3. Nguyên nhân gốc

**Hiểu nguyên tắc "đáp án phân bố đều A–D" theo nghĩa hẹp nhất rồi thi hành bằng cách
máy móc nhất.** Gán chữ cái theo vòng A, C, B, D cho phân bố đẹp nhất có thể, mà quên
rằng *đều* và *không đoán được* là hai tính chất khác nhau — phân bố đều hoàn hảo lại
là thứ dễ đoán nhất.

Test `test_dap_an_khong_don_vao_mot_chu_cai` có sẵn vẫn xanh, vì nó chỉ bắt trường hợp
dồn vào một chữ. Nó không hề đo tính đoán được. **Test xanh được dùng như bằng chứng
cho một điều rộng hơn thứ nó thật sự kiểm** — cùng cơ chế với GAP-014.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Trạng thái |
|---|---|
| `de/02_ASGCN.md` | ✅ đã xáo lại thứ tự phương án (seed cố định 20261001) |
| `dap-an/02_ASGCN.yaml` | ✅ cập nhật đáp án theo thứ tự mới; bỏ chỗ trích dẫn chữ cái trong lời giải thích để không hỏng khi xáo lần sau |
| `bai-lam/02_ASGCN.md` | ✅ xoá trắng — bộ chữ cái cũ không còn khớp đề mới |
| `ket-qua/02_ASGCN_2026-10-01_1949.md` | ✅ giữ nguyên điểm, thêm ghi chú nói rõ điểm này không đủ làm bằng chứng |
| Đề 01 (UIT-ViSFD) | ✅ không bị — dãy đáp án là C A B D C B A D B C D B A A D, không có chu kỳ |
| Kết luận "đã đọc kỹ ASGCN" | 🔴 **chưa được công nhận** — chờ học viên quyết cách xác minh lại |

## 5. Đã sửa thế nào

Thêm test `test_dap_an_khong_lap_theo_chu_ky` vào `tests/test_cham_trac_nghiem.py`: quét
mọi chu kỳ từ 1 tới một nửa số câu, chu kỳ nào lặp trọn vẹn thì báo đỏ. Chặn cả chu kỳ 2,
3, 5 chứ không riêng chu kỳ 4 vừa gặp.

Test này chạy trên mọi đề, kể cả các đề sau này.

## 6. Bài học

**Một ràng buộc chống gian lận phải được phát biểu theo thứ nó muốn chặn, không theo
thứ dễ kiểm.** "Phân bố đều" là thứ dễ kiểm; thứ thật sự muốn chặn là "đoán được mà
không cần đọc". Hai cái đó không bao hàm nhau, và lần này chúng còn mâu thuẫn nhau.

Áp dụng rộng hơn cho cả luận văn: khi viết tiêu chí nghiệm thu cho một phép đo, hỏi
thêm một câu — *có cách nào đạt tiêu chí này mà không đạt điều mình thật sự muốn không?*
Đây cũng chính là câu phải hỏi ở mục 4.2 của báo cáo khi bàn ngân sách tinh chỉnh bằng
nhau giữa các mô hình.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — sai sót ở công cụ học tập nội bộ, không chạm tới số liệu thực nghiệm
      hay kết luận nghiên cứu. Giữ trong sổ này để rút kinh nghiệm.
