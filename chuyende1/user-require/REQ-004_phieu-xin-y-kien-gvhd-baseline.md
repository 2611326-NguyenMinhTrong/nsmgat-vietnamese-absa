# REQ-004 — Phiếu xin ý kiến GVHD về danh sách baseline

**Ngày yêu cầu:** 27/08/2026 · **Trạng thái:** ✅ Xong — chờ học viên gửi Cô

---

## 1. Yêu cầu nguyên văn

> "giờ hãy viết cho tôi một file nội dung nhờ GVHD góp ý vấn đề 3 mục 11 trong plan chuyên đề 1
> 'Bốn mô hình baseline (PhoBERT, Sentic-GCN, ViSoBERT, LLM) có được cô chấp thuận không?
> Cô có muốn thêm/bớt mô hình nào?', nêu rõ từng lý do tại sao chọn các baseline đó, định dạng
> file có thể làm word, nếu word tốn quá nhiều tài nguyên để làm thì chỉ cần làm file markdown
> cũng được, đặt trong thư mục user-require"

## 2. Hiểu thành gì

Một văn bản gửi GVHD, không phải ghi chú nội bộ. Ba ràng buộc suy ra từ đó:

- **Phải đọc nhanh được.** GVHD bận; văn bản dài quá sẽ bị đọc lướt. Chốt ~4 trang.
- **Phải trả lời nhanh được.** Nếu bắt Cô viết email tự do thì khả năng cao là chậm hoặc trả
  lời chung chung. Vì vậy có phần **phiếu ý kiến với ô đánh dấu** ở cuối.
- **Phải nêu lý do, không chỉ nêu kết luận.** Yêu cầu nói rõ "nêu rõ từng lý do".

Về định dạng: python-docx 1.2.0 đã có sẵn trong `.venv` nên **làm Word không tốn tài nguyên**
như học viên lo ngại. Làm cả hai bản.

## 3. Vì sao học viên muốn thế

Đây là câu hỏi số 3 mục 11 của `PLAN_CHUYENDE1.md`, đang chặn CD1.6 (ViSoBERT). Danh sách
baseline quyết định toàn bộ Chương 4 và phần lập luận hạn chế ở Chương 5 — chốt sai thì Tuần 8
phải chạy lại, không còn thời gian.

## 4. Đã làm gì để đáp ứng

| File | Tạo | Nội dung |
|---|---|---|
| `chuyende1/user-require/XinYKien-GVHD_Baseline.md` | ✓ | Bản nguồn, sửa được, diff được trong git |
| `chuyende1/user-require/XinYKien-GVHD_Baseline.docx` | ✓ | Bản gửi Cô — đúng định dạng UTE |
| `scripts/md_to_docx_ute.py` | ✓ | Bộ chuyển Markdown → Word theo quy định UTE (**Vùng 1, dùng chung**) |

**Nội dung phiếu — 8 mục:**

1. Bối cảnh và mục đích
2. Nguyên tắc chọn baseline — *mỗi baseline là một giả thuyết cạnh tranh cần loại trừ*
3. Lý do từng mô hình (vai trò · vì sao chọn · nếu bỏ thì mất gì)
4. Đối chiếu với 6 nhóm phương pháp trong khảo sát — nhóm 6 để trống có chủ ý
5. Các mô hình đã cân nhắc nhưng chưa chọn, kèm mức sẵn sàng bổ sung
6. Hai vấn đề kỹ thuật đang phân vân — GAP-002 và GAP-003
7. Chi phí và tính khả thi (ước tính giờ GPU, chi phí API)
8. **Phiếu ý kiến có ô đánh dấu** — 5 câu hỏi

**Quyết định về nội dung:** chủ động nêu GAP-002 (từ điển cảm xúc) và GAP-003 (seed của LLM)
vào mục 6, dù học viên không yêu cầu. Lý do: hai rủi ro này ảnh hưởng trực tiếp tới việc chọn
baseline (GAP-002 có thể dẫn tới đổi Sentic-GCN sang ASGCN). Giấu đi rồi để Cô phát hiện sau
sẽ mất tin cậy nhiều hơn là nêu trước.

**Về bộ chuyển đặt ở `scripts/`:** đây là Vùng 1 (dùng chung) chứ không phải `chuyende1/`, vì
CD1.1 sẽ dùng lại nó để dựng `reference.docx` và khung cuốn chuyên đề, và CĐ2 cũng sẽ cần.
Cú pháp Markdown hỗ trợ được giới hạn có chủ ý ở mức đủ cho tài liệu học vụ.

## 5. Chi phí

- **Một lần:** ~1,5 giờ (soạn nội dung ~1 h, viết bộ chuyển ~0,5 h)
- **Lặp lại:** ~1 phút để sinh lại `.docx` sau mỗi lần sửa `.md`
- **Cả kỳ:** ~1,5 giờ — và **thu hồi được** ở CD1.1, vì bộ chuyển dùng lại luôn

## 6. Có làm lệch kế hoạch gốc không

- [x] **Không** — đây là việc đã có sẵn trong plan (câu hỏi 3 mục 11), chỉ là được làm thành
      văn bản hẳn hoi thay vì hỏi miệng.

## 7. Việc phát sinh về sau

- **Học viên gửi phiếu cho Cô** — chưa làm, cần điền ngày trước khi gửi.
- Khi có ý kiến của Cô: cập nhật `progress_cd1.md` (bảng câu hỏi, câu 3), ghi vào Sổ quyết
  định, và nếu Cô chọn phương án cho GAP-002/GAP-003 thì cập nhật hai file gap tương ứng.
- Nếu Cô yêu cầu thêm/bớt mô hình: sửa mục 2 của `PLAN_CHUYENDE1.md`, sửa lịch Tuần 3–7, và
  ghi một REQ mới.

**Lệnh sinh lại bản Word sau khi sửa nội dung:**

```
.venv/Scripts/python.exe scripts/md_to_docx_ute.py \
    chuyende1/user-require/XinYKien-GVHD_Baseline.md \
    chuyende1/user-require/XinYKien-GVHD_Baseline.docx
```
