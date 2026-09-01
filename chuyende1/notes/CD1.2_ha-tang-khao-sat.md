# PHIẾU BÀN GIAO — [CD1.2] Hạ tầng khảo sát SOTA

**Ngày:** 27/08/2026 · **Step:** CD1.2 (phần code) · **Ánh xạ plan gốc:** `[MỚI]` · **Thời gian:** ~1,5 giờ

> ⚠️ **Step này chỉ xong một nửa, và đó là điều đúng.** Phần còn lại — tìm và đọc ≥45 công
> trình — là việc tay của học viên, không giao AI được. Xem mục 7.

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `chuyende1/survey/survey_protocol.md` | Điền | Từ khoá EN/VI, tiêu chí nhận/loại, chỉ tiêu N₁–N₅, **mục 7 mới: quy trình kiểm chứng ba mức** |
| `chuyende1/survey/survey_matrix.csv` | Sửa | Thêm 2 cột `trang_thai`, `nguon_url`; gieo 20 dòng hạt giống |
| `scripts/survey_tools.py` | Tạo | 3 lệnh `validate` / `stats` / `table` |
| `tests/test_survey_tools.py` | Tạo | 17 test, trọng tâm ở chốt chặn chống bịa trích dẫn |
| `chuyende1/MODULE.md` | Sửa | Ghi nhận 2 file mới ở Vùng 1 |

```bash
python scripts/survey_tools.py validate   # Hợp lệ. 20 dòng, 18 cột.
python scripts/survey_tools.py stats      # phủ nhóm + tiến độ kiểm chứng
python scripts/survey_tools.py table      # exit 1 — chưa dòng nào kiểm chứng
```

## 2. ĐỂ LÀM GÌ

- **Trước:** giao thức khảo sát còn 4 chỗ `[TODO]`, ma trận rỗng chỉ có dòng tiêu đề. Không
  có cách nào biết "khảo sát đã đủ chưa" ngoài đếm tay.
- **Sau:** chỉ tiêu thành số đo được (`stats`), và **quy tắc số 7 của repo được cưỡng chế
  bằng code** thay vì bằng thiện chí.
- **Nếu bỏ:** đến Tuần 13 viết Chương 3, rất dễ đưa vào bảng một trích dẫn nhớ mang máng mà
  chưa từng mở nguồn. Hội đồng hỏi đúng bài đó là hỏng cả chương.

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1. Ý chính: biến một quy tắc đạo đức thành một ràng buộc kỹ thuật

Quy tắc số 7 nói *"không bịa trích dẫn"*. Vấn đề: quy tắc dựa vào trí nhớ và thiện chí, mà
cả hai đều hỏng vào tuần 13 lúc 11 giờ đêm trước hạn nộp.

Cách xử lý: thêm cột `trang_thai` với đúng ba giá trị, rồi bắt công cụ tôn trọng nó.

| `trang_thai` | Nghĩa | Được dùng ở đâu |
|---|---|---|
| `chua_kiem` | Mới có tên bài | **Không** được trích dẫn |
| `da_kiem_url` | Đã mở trang gốc, xác nhận tác giả/năm/nơi công bố | Vào được Bảng 3.9 |
| `da_doc_toan_van` | Đã đọc hết, hiểu phương pháp và kết quả | Phân tích sâu ở 3.2–3.8 |

`table` **chỉ đọc dòng đã kiểm chứng**, và nếu không có dòng nào thì thoát mã 1 kèm hướng dẫn.
Nghĩa là: không thể vô ý đưa trích dẫn chưa kiểm chứng vào cuốn báo cáo — muốn đưa vào thì
phải tự tay đổi `trang_thai`, và lúc đó là hành động có ý thức chứ không phải sơ suất.

### 3.2. Đi qua một ví dụ cụ thể

Ma trận hiện có dòng:

```
Sentic-GCN,chua_kiem,[CẦN TÌM],[CẦN TÌM],G4_do_thi,...
```

Chạy `table` → thoát mã 1, không ghi file. Giờ giả sử bạn mở bài gốc, xác nhận năm và nơi
công bố, điền vào, đổi `trang_thai` thành `da_kiem_url` và điền `nguon_url`. Chạy lại:

```
OK -> chuyende1/tables/bang_3_9_khao_sat.md  (1 công trình, bỏ qua 19 dòng chưa kiểm chứng)
```

Nếu bạn đổi `trang_thai` nhưng **quên** điền năm — tức trường vẫn là `[CẦN TÌM]` — thì
`validate` bắt được:

```
Dòng 12 (Sentic-GCN): đã đánh 'da_kiem_url' nhưng còn [CẦN TÌM] ở: nam
```

Đây là **kiểm tra mâu thuẫn nội tại**: không so với nguồn ngoài (không làm được), mà so
tuyên bố của chính bạn với dữ liệu bạn điền. Rẻ, và bắt được đúng kiểu lỗi hay xảy ra khi làm vội.

### 3.3. Vì sao gieo sẵn 20 dòng thay vì để file rỗng

20 tên đó **lấy từ chính plan trong repo** (`PLAN_CHUYENDE1.md` mục CD1.2 và `PLAN_NSMGAT.md`),
không phải từ trí nhớ của tôi. Mọi trường khác đều là `[CẦN TÌM]`.

Nói cách khác: đây là **danh sách việc cần làm**, không phải dữ liệu khảo sát. File rỗng thì
bạn phải tự nhớ ra nên tìm gì; file này cho bạn 20 điểm khởi đầu và một chiến lược
(truy vết trích dẫn hai chiều từ bài hạt giống).

### 3.4. Con số `stats` in ra dùng ngay ở đâu

`N₄` và `N₅` không phải để trang trí — chúng là hai ô trong **sơ đồ luồng sàng lọc** ở mục
3.1 của cuốn báo cáo. Có sơ đồ đó là dấu hiệu khảo sát có phương pháp; hội đồng nhìn vào đó
để biết bạn tìm bằng cách nào chứ không phải đọc ngẫu nhiên.

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Ai làm phần đọc bài | **Học viên** | Để AI tìm và điền ma trận | Vi phạm quy tắc số 7; và hội đồng sẽ hỏi chi tiết từng bài — không đọc thì không trả lời được |
| Chống bịa trích dẫn | Cột `trang_thai` + công cụ tôn trọng nó | Ghi một dòng nhắc trong tài liệu | Dòng nhắc không chặn được gì lúc 11 giờ đêm trước hạn nộp |
| Khi chưa có dòng kiểm chứng | `table` thoát mã 1 | Sinh bảng rỗng | Bảng rỗng dễ bị hiểu là "khảo sát xong mà không có gì" |
| Cửa thoát `--allow-unverified` | **Không có** | Có, để tiện | Có cửa thoát thì chốt chặn thành vô nghĩa |
| Gieo ma trận | 20 dòng, tên lấy từ plan repo | Để rỗng · hoặc tôi tự điền từ trí nhớ | Rỗng thì vô ích; điền từ trí nhớ là bịa |
| Nhóm `TAI_NGUYEN` | Tách riêng, không tính vào chỉ tiêu 6 nhóm | Xếp dataset vào G3 | UIT-ViSFD là tập dữ liệu, không phải phương pháp — trộn vào sẽ làm chỉ tiêu phủ nhóm sai |

**Đổi lược đồ CSV:** thêm `trang_thai` và `nguon_url` so với header dựng ở REQ-003. File
lúc đó chưa có dữ liệu và CD1.2 là step sở hữu nó, nên không phải sai sót — nhưng đã ghi ở
đây để sau này không ai thắc mắc vì sao lược đồ đổi.

## 5. ĐIỂM NỐI VỚI STEP SAU

- Step kế tiếp theo lịch: **CD1.3 — Đồ thị cú pháp (S3.1)**, chạy song song cùng Tuần 2,
  **không phụ thuộc** step này.
- CD1.2 còn nửa sau ở **Tuần 5** (khảo sát đợt 2 + `gap_analysis.md`).
- Nơi các đầu ra chảy tới:
  - `survey_matrix.csv` → `bang_3_9_khao_sat.md` → mục 3.9 của báo cáo
  - `stats` N₄/N₅ → sơ đồ luồng ở mục 3.1
  - `gap_analysis.md` → mục 3.10, rồi đối chiếu với hạn chế đo được ở CD1.9

## 6. KIỂM CHỨNG

```
.venv/Scripts/python.exe -m pytest tests/ -q
.........................................................                [100%]
57 passed in 52.22s
```

Trước CD1.2 là 40 test, giờ 57. Ba nhóm test đáng chú ý:

- `test_bang_chi_lay_dong_da_kiem_chung` — dòng `chua_kiem` không lọt vào bảng
- `test_table_tu_choi_khi_chua_co_dong_nao_kiem_chung` — và **không ghi file**
- `test_bat_mau_thuan_da_kiem_chung_nhung_con_can_tim` — bắt tuyên bố mâu thuẫn dữ liệu

Chạy thật trên ma trận hiện tại: `validate` hợp lệ 20 dòng/18 cột; `stats` cho thấy G1, G5,
G6 chưa đủ 4 công trình; `table` thoát mã 1 đúng như thiết kế.

**Chưa có số liệu khảo sát nào** — đúng như mong đợi, vì chưa ai mở nguồn bài nào.

## 7. DỪNG LẠI VÀ HỎI

**Việc của bạn, không giao được cho tôi:**

Tìm và kiểm chứng ≥45 công trình. Quy trình ở `survey_protocol.md` mục 7. Ba nhóm đang
thiếu nhất: **G1** (0/4), **G5** (1/4), **G6** (1/4) — riêng G6 là nhóm mà Chuyên đề 2 sẽ
đứng vào, nên phải nắm kỹ nhất.

**Câu hỏi mở:**

1. **Bạn có muốn tôi dùng web search để tìm giúp không?** Tôi có công cụ đó. Nếu dùng, tôi
   sẽ chỉ điền những trường đọc được từ trang gốc và để `trang_thai = da_kiem_url`; phần
   `da_doc_toan_van` vẫn phải là bạn. Đánh đổi: nhanh hơn nhiều, nhưng bạn mất phần lớn
   giá trị học thuật của việc tự khảo sát — và hội đồng sẽ hỏi chi tiết từng bài.
   **Tôi nghiêng về việc bạn tự làm**, tôi chỉ hỗ trợ khi bạn bí một bài cụ thể.
2. Chỉ tiêu ≥45 có hợp lý với thời gian bạn có không? Ước tính ~15–20 giờ đọc.

**Những chỗ bạn có thể muốn hỏi thêm:**

- Vì sao không để AI điền ma trận cho nhanh?
- Ba mức `trang_thai` có quá rườm rà không, hai mức được không?
- Sơ đồ luồng sàng lọc ở mục 3.1 trông như thế nào, và vì sao hội đồng quan tâm?

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
