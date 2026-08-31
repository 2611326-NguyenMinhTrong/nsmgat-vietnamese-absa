# PHIẾU BÀN GIAO — [CD1.1] Khởi động & khung báo cáo

**Ngày:** 27/08/2026 · **Step:** CD1.1 · **Ánh xạ plan gốc:** `[MỚI]` · **Thời gian:** ~2 giờ

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `scripts/ute_docx.py` | Tạo | Thư viện định dạng Word theo quy định UTE — lề, phông, style tiêu đề, đánh số trang theo section, trường mục lục, chú thích bảng/hình |
| `scripts/build_cd1_report.py` | Tạo | Dựng `reference.docx` + khung cuốn chuyên đề từ dàn ý trong `OUTLINE_BAOCAO_CD1.md` |
| `scripts/md_to_docx_ute.py` | Sửa | Bỏ phần định dạng trùng lặp, dùng lại `ute_docx.py` |
| `tests/test_ute_docx.py` | Tạo | 17 test kiểm định dạng |
| `requirements.txt` | Sửa | Thêm `python-docx>=1.1` |
| `chuyende1/report/reference.docx` | Sinh | Mẫu định dạng, trưng bày từng style kèm tên |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx` | Sinh | Khung rỗng: 3 section, 6 chương, 40 mục con, 55 chỗ `[TODO:]` |

```bash
.venv/Scripts/python.exe scripts/build_cd1_report.py
.venv/Scripts/python.exe -m pytest tests/ -q
```

## 2. ĐỂ LÀM GÌ

- **Trước:** chưa có file `.docx` nào. Định dạng UTE mới chỉ nằm dưới dạng checklist trong
  `OUTLINE_BAOCAO_CD1.md` — tức là phải nhớ và làm tay 12 thông số mỗi lần tạo tài liệu.
- **Sau:** định dạng thành **code chạy được và kiểm được**. Mở file ra là gõ nội dung, không
  phải chỉnh lề, chỉnh phông, chỉnh kiểu đánh số trang.
- **Nếu bỏ step này:** đến Tuần 13 mới dựng khung thì hai rủi ro: (a) gõ 30 trang xong mới
  phát hiện sai định dạng, phải chỉnh tay toàn bộ; (b) không biết mỗi mục viết bao nhiêu
  trang nên viết lệch ngân sách (thường là Chương 2 phình, Chương 5 thiếu).

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1. Vì sao số trang phải là "trường", không phải chữ

Yêu cầu của UTE: bìa không đánh số → các trang đầu đánh `i, ii, iii` → từ Chương 1 đánh
`1, 2, 3` **bắt đầu lại từ 1**. Không thể gõ tay vì thêm một đoạn văn là toàn bộ số trang sai.

Word giải quyết bằng **field** — một ô do Word tự tính. Trong XML, một field gồm ba nút:

```xml
<w:fldChar w:fldCharType="begin"/>     <!-- mở -->
<w:instrText>PAGE</w:instrText>        <!-- lệnh: in số trang hiện tại -->
<w:fldChar w:fldCharType="end"/>       <!-- đóng -->
```

`python-docx` không bọc sẵn thứ này, nên `ute_docx.add_field()` dựng tay. Cùng một cơ chế
dùng lại cho mục lục, chỉ khác chuỗi lệnh:

```
PAGE                       -> số trang
TOC \o "1-3" \h \z \u      -> mục lục, gom Heading 1..3, có siêu liên kết
```

### 3.2. Ba kiểu đánh số → ba section, không phải ba file

Trong Word, **section** là đơn vị mang thuộc tính trang (lề, khổ giấy, kiểu đánh số).
Cuốn báo cáo có ba section:

| Section | Nội dung | `w:pgNumType` |
|---|---|---|
| 1 | Bìa | *(không có)* → không in số |
| 2 | Lời cảm ơn → Danh sách hình | `fmt="lowerRoman" start="1"` → i, ii, iii |
| 3 | Chương 1 → Phụ lục | `fmt="decimal" start="1"` → 1, 2, 3 |

Đi qua một ví dụ cụ thể: giả sử phần đầu dài 6 trang. Trang vật lý thứ 8 nằm ở section 3,
là trang thứ 2 của section đó. Vì section 3 khai `start="1"` nên Word in **2**, không phải 8.
Đó chính là điều quy định UTE yêu cầu.

### 3.3. Cái bẫy đã sập một lần: footer kế thừa

Section mới trong Word **mặc định dùng chung footer với section trước**. Nếu chỉ đặt
`w:pgNumType` mà quên tách footer thì cả ba section vẫn dùng một footer, và kiểu đánh số
không đổi được. Dòng xử lý:

```python
section.footer.is_linked_to_previous = False   # ute_docx.py, set_page_numbering()
```

Có hẳn một test canh chỗ này: `test_footer_khong_ke_thua_section_truoc`.

### 3.4. Vì sao dùng style dựng sẵn `Heading 1` chứ không tạo style tên riêng

Mục lục tự động của Word gom theo **style**, không theo cỡ chữ. Nếu tạo tiêu đề bằng cách
bôi đậm chữ thường thì trường `TOC` không thấy gì và mục lục rỗng. Vì vậy `apply_styles()`
sửa lại chính `Heading 1/2/3` dựng sẵn — đổi phông sang Times New Roman, đổi **màu xanh mặc
định của Word sang đen**, đặt cỡ 16/14/13.

> Khi gõ bài: đặt con trỏ vào dòng tiêu đề rồi chọn style `Heading 2` trong Word,
> **đừng** bôi đậm rồi tăng cỡ chữ.

### 3.5. Mục lục hiện trống là bình thường

Trường `TOC` chỉ được Word tính khi người dùng yêu cầu. Mở file lần đầu, chỗ mục lục hiện
dòng nhắc. Bấm `Ctrl+A` rồi `F9`, chọn *Update entire table* là ra. Đã ghi câu nhắc này
ngay trong file.

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Cách tạo cuốn 30 trang | Sinh khung `.docx` một lần rồi **gõ trực tiếp trong Word** | Viết Markdown rồi chuyển sang Word mỗi lần | Cuốn 30 trang cần mục lục tự động, chú thích đánh số theo chương, tham chiếu chéo. Word làm sẵn; bộ chuyển Markdown sẽ phải viết lại toàn bộ và vẫn kém hơn |
| Vị trí thư viện định dạng | `scripts/ute_docx.py` (Vùng 1) | `chuyende1/` | CĐ2 và luận văn dùng lại y nguyên |
| Style tiêu đề | Sửa `Heading 1/2/3` dựng sẵn | Tạo style tên riêng `UTE Heading` | Mục lục tự động và thanh style của Word đều nhận diện sẵn style dựng sẵn |
| Ngân sách trang | Ghi thẳng vào khung dưới mỗi tiêu đề chương | Chỉ để trong plan | Lúc gõ bài không ai mở plan ra tra |
| Nội dung mỗi mục | Một dòng `[TODO: CD1.x — ...]` nêu rõ **gói việc nào** điền | Để trắng | Đến Tuần 13 sẽ không nhớ mục 4.6 lấy số từ đâu |
| Kiểm định dạng | 17 test tự động | In ra đo thước (như plan viết) | Đo tay một lần thì được; sửa script 5 lần thì phải đo 5 lần |

## 5. ĐIỂM NỐI VỚI STEP SAU

- Step kế tiếp: **CD1.2 — Khảo sát SOTA đợt 1 (Tuần 2)**.
- CD1.2 dùng lại từ step này: mục **3.1 → 3.10** của khung đã có sẵn tiêu đề và `[TODO:]`
  ghi rõ nguồn dữ liệu (`survey_matrix.csv`, `gap_analysis.md`), nên viết Chương 3 chỉ là
  điền vào chỗ trống.
- Giao diện giữa hai step: `chuyende1/survey/survey_protocol.md` — CD1.2 điền mục 3, 4, 5;
  các con số N₁…N₄ trong mục 5 chảy thẳng vào mục 3.1 của cuốn báo cáo.
- CD1.3 (đồ thị cú pháp) chạy song song trong cùng Tuần 2, không phụ thuộc step này.

## 6. KIỂM CHỨNG

```
.venv/Scripts/python.exe -m pytest tests/ -q
.......................................                                  [100%]
39 passed in 10.40s
```

Trước CD1.1 là 22 test, giờ 39 — thêm 17 test định dạng. Kiểm được:

- Lề 3,5 / 2,0 / 3,0 / 3,5 cm trên **cả ba** section
- Times New Roman 13, giãn dòng 1,5
- Heading 1/2/3 đúng cỡ 16/14/13, **màu đen** (Word mặc định màu xanh)
- Bìa không số trang · trang đầu `lowerRoman` từ 1 · phần chính `decimal` từ 1
- Footer đã tách khỏi section trước
- Đủ 6 chương và 40 mục con, có trường `TOC`, có `TÀI LIỆU THAM KHẢO` và `PHỤ LỤC`
- Bìa ghi `8480101`, **không** còn `601401`
- Chú thích `Bảng 4.1` và `Hình 3.1` tồn tại đúng style `Caption`

**Sự cố gặp phải — và một hồi quy đã bắt được:**

Khi sinh lại phiếu GVHD thì gặp `PermissionError` do file đang mở trong Word. Nhưng chính lúc
kiểm tra lại, phát hiện việc refactor đã làm **mất số trang của mọi tài liệu chuyển từ
Markdown**: `md_to_docx_ute.py` chuyển sang dùng `ute_docx.new_document()`, mà hàm đó cố ý
tắt số trang cho section đầu (vì section đầu của cuốn báo cáo là trang bìa). Tài liệu sinh từ
Markdown không có bìa nên bị mất số trang một cách âm thầm.

Đã sửa: `convert()` bật lại đánh số trang, và thêm assert vào test để lần sau không tái diễn.
Đây là ví dụ điển hình của việc dùng lại code mà **giả định ngầm đi theo không được viết ra** —
giả định ở đây là "section đầu tiên là trang bìa".

File `chuyende1/user-require/XinYKien-GVHD_Baseline.docx` hiện trên đĩa vẫn đúng (sinh bằng
mã cũ, vốn có số trang). Không cần sinh lại; nếu muốn sinh lại thì đóng Word trước.

## 7. DỪNG LẠI VÀ HỎI

**Câu hỏi mở:**

1. Bạn có định gõ bài **trực tiếp trong Word** không? Tôi thiết kế theo hướng đó. Nếu bạn
   muốn viết Markdown trong repo rồi chuyển sang Word thì phải đầu tư thêm cho bộ chuyển
   (mục lục, đánh số bảng/hình theo chương) — nói sớm để tôi làm trước khi bạn viết nhiều.
2. Tên hướng nghiên cứu trên bìa hiện là bản nháp tôi đề xuất. Bạn chốt luôn, hay để hỏi
   GVHD cùng lượt với phiếu baseline?
3. `chuyende1/report/*.docx` có commit lên GitHub không? *(câu này treo từ phiếu CD1.0)*

**Những chỗ bạn có thể muốn hỏi thêm:**

- Vì sao chọn gõ Word thay vì Markdown, khi cả repo đang theo hướng tự động hoá?
- Trường `TOC` và `PAGE` hoạt động ra sao, vì sao mở file lần đầu mục lục lại trống?
- Có nên viết test cho `.docx` không, hay chỉ cần mở ra nhìn?

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
