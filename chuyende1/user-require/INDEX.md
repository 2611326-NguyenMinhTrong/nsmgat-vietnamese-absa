# SỔ YÊU CẦU BỔ SUNG CỦA HỌC VIÊN — Chuyên đề 1

> Nơi lưu mọi yêu cầu học viên đưa ra **trong quá trình thực hiện**, ngoài phạm vi đã chốt
> trong `pLan/chuyende1/PLAN_CHUYENDE1.md`. Mỗi yêu cầu một file `REQ-00x_<tên-ngắn>.md`
> theo mẫu [`_TEMPLATE_require.md`](_TEMPLATE_require.md).

**Vì sao cần sổ này:**

1. **Giữ nguyên văn yêu cầu.** Diễn đạt lại theo trí nhớ sau 3 tháng sẽ lệch. Lời gốc là
   nguồn sự thật khi tranh cãi "ý em lúc đó là gì".
2. **Thấy được plan đã trôi bao xa.** Từng yêu cầu lẻ trông nhỏ; cộng lại có thể đội thêm
   vài tuần mà không ai để ý. Cột "chi phí" trong bảng dưới là để nhìn thấy điều đó.
3. **Phân biệt "học viên yêu cầu" với "Claude tự quyết".** Khi GVHD hỏi *"sao lại làm thêm
   cái này?"*, câu trả lời phải truy được về một yêu cầu cụ thể, có ngày tháng.

**Quan hệ với "Sổ quyết định"** trong `pLan/chuyende1/progress_cd1.md`: sổ này ghi
**yêu cầu** (đầu vào — học viên muốn gì); sổ kia ghi **quyết định** (đầu ra — cuối cùng chọn
làm thế nào). Một yêu cầu có thể sinh ra nhiều quyết định.

---

## Bảng theo dõi

| ID | Ngày | Yêu cầu | Chi phí ước tính | Ảnh hưởng lịch | Trạng thái |
|---|---|---|---|---|---|
| [REQ-001](REQ-001_tach-module-chuyende1.md) | 27/08/2026 | Tách Chuyên đề 1 thành module riêng, phần nào dùng chung thì dùng chung | ~2 h | Không | ✅ Xong |
| [REQ-002](REQ-002_phieu-ban-giao-sau-moi-step.md) | 27/08/2026 | Sau mỗi step phải giải thích rõ đã làm gì / để làm gì, rồi hỏi trước khi đi tiếp | +15–30 phút mỗi step (~+6 h cả kỳ) | Không — nằm trong thời gian làm việc | ✅ Xong (đang áp dụng) |
| [REQ-003](REQ-003_so-gaps-va-user-require.md) | 27/08/2026 | Tạo `chuyende1/gaps/` lưu sai sót và `chuyende1/user-require/` lưu yêu cầu bổ sung | ~1 h + ~10 phút mỗi lần ghi | Không | ✅ Xong |
| [REQ-004](REQ-004_phieu-xin-y-kien-gvhd-baseline.md) | 27/08/2026 | Soạn phiếu xin ý kiến GVHD về danh sách 4 baseline, nêu rõ lý do từng mô hình, định dạng Word | ~1,5 h | Không | ✅ Xong — **chờ học viên gửi Cô** |

**Trạng thái:** 🔴 Mới nhận · 🟡 Đang làm · ✅ Xong · ⚪ Đã hoãn / không làm (ghi rõ lý do)

---

## Tổng chi phí phát sinh

| Hạng mục | Giờ |
|---|---|
| Việc một lần (dựng khung, tạo thư mục, soạn phiếu GVHD, bộ chuyển Word) | ~4,5 h |
| Việc lặp lại (phiếu bàn giao, ghi sổ) | ~+6–8 h trải đều 15 tuần |
| **Tổng** | **~12 h** |

*Trong đó ~1,5 h của REQ-004 thu hồi được ở CD1.1 (bộ chuyển `md_to_docx_ute.py` dùng lại để
dựng `reference.docx`).*

> Rà lại bảng này ở **Tuần 8** (mốc báo cáo GVHD #1). Nếu tổng chi phí phát sinh vượt ~20 giờ,
> cần xem lại: hoặc cắt bớt phạm vi ở đâu đó, hoặc chấp nhận trượt lịch và báo GVHD sớm —
> không để đến Tuần 14 mới phát hiện.
