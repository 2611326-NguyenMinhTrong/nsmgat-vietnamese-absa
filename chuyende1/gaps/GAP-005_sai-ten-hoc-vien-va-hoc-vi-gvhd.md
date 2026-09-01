# GAP-005 — Sai tên học viên và sai học vị GVHD trên mọi tài liệu

**Ngày phát hiện:** 27/08/2026 · **Phát hiện bởi:** học viên
**Loại:** tài liệu · **Mức độ:** **nghiêm trọng** (suýt gửi ra ngoài) · **Trạng thái:** 🟡 Đang xử lý

---

## 1. Sai ở đâu

| Trường | Đã ghi (sai) | Đúng |
|---|---|---|
| Tên học viên | Nguyễn Minh **Trọng** | Nguyễn Minh **Trộng** |
| Học vị GVHD | **ThS.** Phan Thị Huyền Trang | **TS.** Phan Thị Huyền Trang |

Lan ra 5 file, trong đó có **bìa cuốn chuyên đề** và **phiếu xin ý kiến sắp gửi cho chính Cô**:

- `README.md` dòng 3
- `pLan/PLAN_NSMGAT.md` dòng 3
- `pLan/chuyende1/PLAN_CHUYENDE1.md` dòng 3–4
- `chuyende1/user-require/XinYKien-GVHD_Baseline.md` dòng 5, 7, 215
- `scripts/build_cd1_report.py` hằng số `HOC_VIEN`, `GVHD` → chảy vào bìa `.docx`

## 2. Vì sao đây là sai sót nghiêm trọng, không phải lỗi chính tả

Ba hệ quả, xếp theo mức nặng dần:

1. Tên học viên sai trên bìa cuốn nộp cho hội đồng.
2. **Hạ học vị của GVHD** trong tài liệu gửi cho chính người đó. Đây không phải lỗi kỹ
   thuật mà là lỗi ứng xử — và người nhận sẽ là người đầu tiên nhìn thấy.
3. Sai sót nằm trong **hằng số của script sinh tài liệu**, nên mọi `.docx` sinh ra về sau
   đều mang lỗi, kể cả sau khi sửa file Markdown.

## 3. Nguyên nhân gốc

**Lấy dữ liệu định danh từ nguồn thứ cấp mà không xác nhận với người liên quan.**

Tên và học vị được chép từ `README.md` dòng 3 — file có sẵn trong repo từ trước. Nguồn đó
sai, và mọi tài liệu phái sinh kế thừa lỗi mà không có bước nào kiểm chứng.

Đây là **cùng một cơ chế hỏng với GAP-004** (lệch tên thí nghiệm giữa hai plan) và với
nguyên tắc `metrics.json` là nguồn duy nhất: *một giá trị sai ở nguồn sẽ lan âm thầm ra
mọi thứ dẫn xuất từ nó.* Khác biệt là ở đây giá trị nói về **một con người thật**, nên
không có cách nào tự kiểm chứng bằng code — bắt buộc phải hỏi.

Một điểm đáng lưu ý: quy tắc số 7 của repo là "không bịa số liệu, không bịa trích dẫn".
Quy tắc đó **không phủ tới thông tin định danh về người**. Đó là lỗ hổng của chính bộ quy tắc.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Trạng thái |
|---|---|
| 5 file nguồn `.md` / `.py` | ✅ đã sửa |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx` (bìa) | ✅ đã sinh lại |
| `chuyende1/report/reference.docx` | ✅ đã sinh lại |
| `chuyende1/user-require/XinYKien-GVHD_Baseline.docx` | 🔴 **CHƯA sinh lại** — file đang mở trong Word, bị khoá ghi |
| Commit `8e9fac0` | Đã chứa nội dung sai; sửa bằng commit tiếp theo, không viết lại lịch sử |

**Chưa có tài liệu nào được gửi ra ngoài.** Phát hiện kịp.

Tên file `ChuyenDe1_NguyenMinhTrong.docx` không đổi: bỏ dấu thì cả "Trọng" và "Trộng" đều
thành "Trong".

## 5. Đã sửa thế nào

1. Thay chuỗi trên 5 file nguồn (dùng chuỗi khớp chính xác — cẩn thận không đụng vào từ
   "QUAN TRỌNG" và "Trọng số" xuất hiện nhiều nơi trong `PLAN_NSMGAT.md`).
2. Sinh lại `reference.docx` và khung cuốn chuyên đề.
3. Thêm test `test_bia_khong_con_hoc_vi_sai` — chốt giá trị đúng trên bìa và **cấm chuỗi
   "ThS." xuất hiện trở lại**.

**Việc còn lại của học viên:** đóng file `XinYKien-GVHD_Baseline.docx` trong Word rồi chạy

```
.venv/Scripts/python.exe scripts/md_to_docx_ute.py \
    chuyende1/user-require/XinYKien-GVHD_Baseline.md \
    chuyende1/user-require/XinYKien-GVHD_Baseline.docx
```

⚠️ **Không gửi bản `.docx` hiện tại cho Cô** — nó vẫn ghi "ThS.".

## 6. Bài học

**Thông tin định danh về người thật (họ tên đầy đủ, học vị, chức danh, mã số) phải được
xác nhận trực tiếp với người đó hoặc với học viên trước khi đưa vào bất kỳ tài liệu nào
gửi ra ngoài — không chép lại từ file có sẵn trong repo.**

Đã bổ sung vào `README.md` mục "Quy định riêng của học viên" như một mở rộng của quy tắc
số 7: không bịa số liệu, không bịa trích dẫn, **và không suy đoán thông tin định danh**.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — sai sót nội bộ, phát hiện trước khi gửi ra ngoài, không ảnh hưởng kết quả
      nghiên cứu. Giữ trong sổ này để rút kinh nghiệm.
