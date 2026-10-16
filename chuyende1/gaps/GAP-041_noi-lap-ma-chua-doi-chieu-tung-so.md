# GAP-041 — Nói "lặp, cắt không mất nội dung" mà chưa đối chiếu từng con số

**Ngày phát hiện:** 17/10/2026 · **Phát hiện bởi:** Claude Code, khi bắt tay cắt theo đề xuất của chính mình
**Loại:** tài liệu (phiếu rà soát)
**Mức độ:** nhẹ (chưa cắt gì sai; phát hiện trước khi xoá)
**Trạng thái:** ✅ Đã đính chính trong trả lời cho học viên; học viên chọn hướng xử lý phụ lục (17/10/2026, phiếu CD1.12n)

---

## 1. Sai ở đâu

Phiếu `chuyende1/notes/CD1.12h_ra-soat-ban-nop-truoc-gpt4o.md` (mục "Dư thừa") ghi:

- đoạn "Độ nhất quán của nhãn" ở mục 4.1.2 và Phụ lục B "gần như nguyên văn";
- sáu hàng của Bảng A.2 "lặp số liệu đã có trong Chương 3 hoặc Bảng 3.2", "cắt được mà không mất nội dung".

Đối chiếu từng con số ngày 17/10/2026:

- Phụ lục B có ba chi tiết mục 4.1.2 không có: cách rút 15 mẫu mỗi nhóm và 14, 15, 15, 16 mẫu; ít nhất 28 trên 60 mẫu
  gán lại trong vòng 3 ngày; nhóm cả hai giữ nguyên nhãn ở 9 trên 15 mẫu.
- Mỗi hàng trong sáu hàng Bảng A.2 có 1–2 con số chỉ có ở phụ lục: +3,8 điểm (Moore và Barnes), ViT5 so với PhoBERT về
  macro-F1 (Thin và cộng sự), 71,4 % và 81,8 % (Socher và cộng sự), 84,11 % của BERT (Sentic GCN-BERT), 32 % và 6 % lời
  khuyên (R-GAT), cỡ ngữ liệu 3.829.253 từ (Tran và Phan). Phần đúng của nhận định: cả sáu công trình đều được bàn ở
  Chương 2 hoặc 3, nên tên Bảng A.2 sai với chúng.

## 2. Phát hiện thế nào

Học viên bảo cắt hai chỗ đó. Trước khi xoá, Claude đặt hai đoạn cạnh nhau và tìm từng con số của sáu hàng trong các chương.

## 3. Nguyên nhân gốc

Nhận định "lặp" dựa trên việc thấy cùng tên công trình và vài con số trùng (86,92; 9.778; 46 %), rồi suy ra cả hàng trùng.
Không đối chiếu từng con số trước khi viết "không mất nội dung". Cùng mẫu với quy tắc trong bộ nhớ "kiểm ngữ cảnh con số":
một câu khẳng định về toàn bộ phải có lần kiểm toàn bộ.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| Phiếu CD1.12h, mục "Dư thừa" | Không sửa phiếu cũ (là bản ghi lúc đó); GAP này đính chính |
| Phiếu CD1.12m (phân tích độ dài) nhắc lại nhận định | Đã đính chính trong trả lời cho học viên |
| Báo cáo | Chưa xoá gì sai; đoạn Phụ lục B rút gọn giữ đủ ba chi tiết riêng |

## 5. Đã sửa thế nào

Báo cho học viên bảng đối chiếu từng hàng; rút gọn đoạn Phụ lục B nhưng giữ ba chi tiết riêng; để học viên chọn cách xử lý
Bảng A.2.

Học viên chọn (17/10/2026): giữ Bảng A.1 trong báo cáo, bỏ Bảng A.2, chuyển Phụ lục B và C lên GitHub
(`chuyende1/phu_luc/PhuLuc_B_C.md`). Bản trên GitHub dùng nguyên văn đầy đủ của đoạn độ nhất quán, nên ba chi tiết riêng
không mất; bản rút gọn của đoạn đó không còn dùng. Các con số chỉ có ở sáu hàng Bảng A.2 không còn trong báo cáo; chúng vẫn
nằm trong bản sao lưu của bản nháp và trong bản gốc của từng bài báo.

## 6. Bài học — phòng lần sau bằng cách nào

Trước khi viết "lặp" hay "cắt không mất nội dung" cho một đoạn hoặc một bảng, liệt kê mọi con số và mọi mệnh đề của nó và
tìm từng cái ở chỗ được coi là bản gốc; ghi số cái tìm thấy trên tổng số.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] Không — sai sót trong phiếu nội bộ, phát hiện trước khi sửa báo cáo
