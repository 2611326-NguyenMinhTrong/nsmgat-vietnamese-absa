# GAP-017 — Vòng Excel nuốt mất thay đổi trong `.csv`, không báo gì

**Ngày phát hiện:** 20/09/2026 · **Phát hiện bởi:** Claude Code (test đỏ với nội dung lạ trong file)
**Loại:** code (công cụ)
**Mức độ:** nghiêm trọng — mất dữ liệu âm thầm
**Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

`survey_tools.py excel` xuất `.csv` ra `.xlsx`. File `.xlsx` là một **bản chụp** tại thời điểm
xuất. `tu-excel` nhập ngược bằng cách **ghi đè toàn bộ** `.csv` từ bản chụp đó.

Không có gì kiểm tra xem `.csv` có thay đổi trong khoảng thời gian giữa hai lệnh hay không.
Ai sửa `.csv` trong khoảng đó — học viên bằng editor, Claude Code bằng script, hay một lần
`git checkout` — thì lần `tu-excel` kế tiếp xoá sạch, **không cảnh báo, không sao lưu**.

## 2. Phát hiện thế nào

Test `test_file_that_trong_repo_hop_le` đỏ, với nội dung không ai trong phiên vừa viết:
ô `co_ma_nguon` chứa một đường dẫn GitHub. Đọc `git diff` thì thấy bốn thứ vừa được commit
đã biến mất khỏi file làm việc:

- hai dòng chú thích `#MO_TA` / `#VI_DU`
- phần chi tiết trong ngoặc của 3 ô `bieu_dien_dau_vao`
- toàn bộ `ghi_chu` bổ sung của dòng `UIT-ViSFD` (tiêu đề bài báo, link mã nguồn, ghi chú
  nguồn của năm, ghi chú vì sao điền `khong`)
- tiền tố `https://` trong `nguon_url`

Dấu vết xác nhận cơ chế: `survey_matrix.xlsx` và `survey_matrix.csv` có cùng mốc sửa 16:58 —
học viên sửa trong Excel rồi chạy `tu-excel`, đúng lúc `.csv` đang chứa bản đã sửa của
Claude Code.

**Chỉ mất một lần duy nhất mà không ai nhận ra ngay** — đó là mức độ nguy hiểm thật của lỗi
này. Nếu hôm đó không có test đọc file thật, phần đã mất sẽ chỉ lộ ra sau nhiều tuần.

## 3. Nguyên nhân gốc

**Công cụ chống ghi đè đã tồn tại trong repo, nhưng không được áp cho chỗ này.**
`build_cd1_report.py` có đúng cơ chế đó từ REQ-006: lưu dấu vân tay nội dung vào
`.generated.json`, lần sau so vân tay rồi **từ chối ghi đè** nếu file đã bị sửa tay.

Khi viết cầu nối Excel (09/09), tôi coi nó là "một tiện ích nhỏ" nên không hỏi câu đã hỏi ở
REQ-006: *lệnh này ghi đè cái gì, và có gì bảo đảm thứ bị ghi đè là thứ đáng bỏ?*

Mẫu hỏng: **một lớp an toàn được dựng cho một file, rồi lệnh sau viết ra một đường ghi đè
khác mà không đi qua lớp đó.**

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| `survey_matrix.csv` — 4 nhóm nội dung | Có — đã khôi phục toàn bộ |
| `nam` của `UIT-ViSFD` | Có, nhưng vì lý do khác: ô này ghi `2018`, mâu thuẫn với trang arXiv (nộp 31/05/2021) → sửa thành `2021`, ghi nguồn vào `ghi_chu` |
| Số liệu thí nghiệm | Không liên quan |

## 5. Đã sửa thế nào

1. **Dấu vân tay trong chính file `.xlsx`** — trang tính ẩn `_nguon` giữ vân tay nội dung của
   `.csv` tại lúc xuất.
2. **`tu-excel` từ chối nhập ngược** khi `.csv` đã đổi so với vân tay đó, và in ra hai lựa
   chọn rõ ràng (`--ghi-de` để giữ bản Excel, hoặc chạy lại `excel` để giữ bản `.csv`) kèm
   lệnh `git diff` để xem trước khi chọn.
3. **Luôn sao lưu `.csv.bak`** trước khi ghi đè, kể cả khi vân tay khớp.
4. **3 test mới**: một vòng Excel không làm đổi dữ liệu (kể cả dòng chú thích); bị chặn thì
   `.csv` không bị đụng tới; `--ghi-de` thì lấy bản Excel và vẫn có bản sao lưu.

## 6. Bài học — phòng lần sau bằng cách nào

**Mọi lệnh ghi đè một file do người sửa tay đều phải trả lời được: "thứ tôi sắp xoá có mới
hơn thứ tôi sắp ghi không?"** Nếu không trả lời được thì phải có vân tay để trả lời, hoặc
tối thiểu là một bản sao lưu.

Dấu hiệu nhận biết sớm: **bất kỳ cặp lệnh xuất-ra / nhập-về nào.** Cặp lệnh đó luôn tạo ra
một bản chụp, và bản chụp nào cũng có thể cũ đi.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — sai sót công cụ nội bộ, đã sửa, không chạm tới số liệu hay kết luận. Nhưng
      cơ chế vân tay thì đáng nhắc một dòng trong mục nói về quy trình khảo sát.
