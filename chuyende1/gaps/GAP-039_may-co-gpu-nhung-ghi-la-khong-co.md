# GAP-039 — Tài liệu ghi "máy không có GPU" trong khi máy có GPU mà PyTorch không dùng được

**Ngày phát hiện:** 16/10/2026 · **Phát hiện bởi:** Claude Code, khi xét đo chi phí suy luận ngay ở máy thay cho Colab
**Loại:** tài liệu
**Mức độ:** nhẹ (kết luận chạy trên Colab vẫn đúng; một câu sai đã nằm trong báo cáo tiến độ gửi giảng viên hướng dẫn)
**Trạng thái:** 🟡 Đã đính chính ở phiếu CD1.10b và sổ tay lệnh; báo cáo tiến độ gửi giảng viên để học viên quyết

---

## 1. Sai ở đâu

Nhiều tài liệu ghi máy của học viên "không có GPU". Lệnh `nvidia-smi` ngày 16/10/2026 cho thấy máy có một card
NVIDIA GeForce GTX 1650, 4.096 MiB bộ nhớ, driver 451.67 (CUDA 11.0). Điều đúng là PyTorch trong `.venv`
(phiên bản `2.13.0+cpu`) là bản chỉ chạy CPU, nên `torch.cuda.is_available()` trả về False; mọi phép đo trên máy
từ trước tới nay đều chạy trên CPU.

Các chỗ ghi sai:

| File | Dòng | Ghi gì |
|---|---|---|
| `chuyende1/notes/CD1.10b_cong-cu-do-chi-phi-va-moc-llm.md` | 54, 68 | "máy không có GPU" |
| `SO_TAY_LENH.md` | 188, 725 | "Máy này không có GPU", "Ở máy không có GPU" |
| `chuyende1/notes/CD1.6a_chay-3-seed.md` | 213 | "máy học viên không có GPU" |
| `chuyende1/gaps/GAP-021_...md` | 44, 70 | "không có GPU" |
| `chuyende1/user-require/BaoCaoTienDo-GVHD.md` | 88 | "máy cá nhân của em không có GPU" (báo cáo gửi giảng viên hướng dẫn) |

## 2. Phát hiện thế nào

Học viên yêu cầu làm tiếp để xong Chương 4. Trước khi giao lại việc đo chi phí suy luận trên Colab, Claude
chạy `nvidia-smi` để xem có đo được ngay ở máy không.

## 3. Nguyên nhân gốc

Ngày 21/09 phép đo "31,8 giây một bước, 52,8 giờ một hạt giống" chạy bằng PyTorch bản CPU, và kết luận được
viết thành "máy không có GPU" mà không ai hỏi phần cứng. Các tài liệu sau chép lại câu đó.

## 4. Ảnh hưởng lan tới đâu

- Không con số nào của báo cáo đổi: các phép đo trên máy đều ghi rõ là CPU, và bốn mô hình dùng PhoBERT huấn
  luyện trên Colab (Tesla T4), như Bảng 4.6 ghi.
- Kết luận chuyển sang Colab vẫn đúng: muốn dùng card này phải cập nhật driver và cài lại PyTorch bản CUDA, và
  4 GB bộ nhớ hẹp cho việc huấn luyện PhoBERT-base.
- Đo chi phí suy luận ở mục 4.5 vẫn làm trên Colab: cùng loại GPU đã huấn luyện bốn mô hình dùng PhoBERT. Đo
  trên card GTX 1650 cũng là một lựa chọn hợp lệ nếu cả sáu mô hình đo trên đó, nhưng cần cập nhật driver và
  cài PyTorch bản CUDA vào một môi trường riêng; Claude không làm việc đó khi chưa được yêu cầu.
- Câu trong báo cáo tiến độ gửi giảng viên hướng dẫn sai về chữ, đúng về hệ quả.

## 5. Đã sửa thế nào

- Phiếu CD1.10b và `SO_TAY_LENH.md`: thêm dòng đính chính trỏ về GAP-039, giữ nguyên câu cũ để biết đã viết gì.
- `CD1.6a_chay-3-seed.md`, GAP-021: không sửa; đó là ghi chép lịch sử, và hệ quả (test GPU không chạy được ở
  máy) vẫn đúng.
- `BaoCaoTienDo-GVHD.md`: không sửa. Nếu bản đó còn được gửi lại, học viên có thể viết: "máy cá nhân của em chỉ
  có GPU GTX 1650 4 GB, chưa cài để PyTorch dùng được, nên em chuyển sang Google Colab".

## 6. Bài học

Một nhận định về phần cứng phải đi kèm lệnh đã chạy để ra nó (`nvidia-smi`, `torch.cuda.is_available()`), vì
"không có GPU" và "PyTorch không thấy GPU" là hai điều khác nhau và dẫn tới hai cách xử lý khác nhau.
