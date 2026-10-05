# CD1.8b — Hướng dẫn chú thích tập chẩn đoán, và công cụ chú thích qua Excel

**Ngày:** 06/10/2026 · **Trạng thái:** ✅ xong, còn một chỗ học viên phải điền trước khi gán · **Step kế:** CD1.8c (việc tay của học viên)

---

## 1. ĐÃ LÀM GÌ

| File | Việc | Lên GitHub? |
|---|---|---|
| `docs/annotation_guideline.md` | Viết mới, thay bản giữ chỗ. Phiên bản 1, mười mục | Không (`docs/` không bao giờ push) |
| `scripts/chu_thich_chan_doan.py` | Tạo. Ba lệnh `excel`, `tu-excel`, `tien-do` | Có |
| `tests/test_chu_thich_chan_doan.py` | Tạo. 7 test | Có |
| `data/diagnostic/candidates_chu_thich.xlsx` | Sinh ra, 800 dòng, chưa dòng nào được gán | Không |
| `.gitignore` | Chặn `candidates*.csv`, `*.xlsx`, `*.bak` trong `data/diagnostic/` | Có |
| `SO_TAY_LENH.md` mục 11d, `chuyende1/MODULE.md` | Thêm mục cho công cụ mới | Sổ tay không lên |
| `pLan/chuyende1/PLAN_CHUYENDE1.md` mục 6.1, `progress_cd1.md` | Sửa theo GAP-028, thêm bốn dòng Sổ quyết định | Không |

Bốn quyết định học viên giao Claude chọn ngày 06/10, ghi ở Sổ quyết định:

1. GAP-028 phương án A: giữ một cấu hình cho mỗi mô hình.
2. `candidates.csv` và file `.xlsx` không lên GitHub.
3. Giữ nguyên 800 ứng viên, không đặt trần cho PRICE.
4. Commit ở máy, **chưa push**.

## 2. ĐỂ LÀM GÌ

- **Vấn đề:** 800 dòng ứng viên mới được chia nhóm bằng từ khoá. Từ khoá có mặt trong câu không
  có nghĩa nó tác động lên khía cạnh của dòng. Nhãn thật phải do người gán, và hai người gán
  phải ra cùng kết quả thì tập mới dùng được làm bằng chứng.
- **Sau step này:** có quy tắc viết ra, đủ cụ thể để một bạn cùng lớp đọc là gán được, và có
  đường thao tác không làm hỏng file.
- **Nếu bỏ:** gán theo cảm tính, kappa thấp, phải gán lại. Đó là 20 đến 25 giờ.

## 3. CƠ CHẾ — phần để học

### 3.1. Hiện tượng gán cho cặp câu và khía cạnh

Cùng một câu, khía cạnh khác nhau nhận hiện tượng khác nhau. Câu `visfd-test-00264`:

> Máy xài mượt chụp ảnh đẹp nhưng chụp ban đêm thì không được rỏ lắm. Điểm yếu của máy là pin nhanh hết quá.

| Khía cạnh | Hiện tượng | Vì sao |
|---|---|---|
| PERFORMANCE | `contrast` | "Máy xài mượt" là vế A của "nhưng", vế B tiêu cực. Từ "không" thuộc về camera |
| BATTERY | `regular` | Ý về pin ở câu thứ hai, ngoài cả phủ định lẫn chuyển ý |

Cả hai dòng đều nằm trong nhóm ứng viên "cả hai" vì câu có cả "không" lẫn "nhưng". Không dòng
nào thật sự là `both`. Đây là lý do nhóm ứng viên không được dùng làm nhãn, và cũng là lý do
file `.xlsx` giấu cột `nhom_ung_vien`.

### 3.2. Hai phép thử thay cho cảm giác

- **Phủ định, phép thử bỏ từ:** che từ phủ định đi; cảm xúc về khía cạnh này đổi hoặc câu vô
  nghĩa thì tính.
- **Chuyển ý, phép xác định vế:** ranh giới câu là dấu chấm, chấm hỏi, chấm than, ".." hoặc
  xuống dòng, dấu phẩy không tính. Ý về khía cạnh phải nằm trong vế A hoặc vế B, và hai vế
  khác cực. Từ nối đứng đầu câu thì vế A là câu liền trước.

Hai phép thử này tồn tại để hai người khác nhau ra cùng một đáp án. Quy tắc "dấu phẩy không
phải ranh giới" làm vế A rộng, có thể bắt cả khía cạnh không liên quan trực tiếp tới ý trái
ngược, như PERFORMANCE ở trên. Tôi chấp nhận điều đó để đổi lấy một quy tắc không cần phán đoán.

### 3.3. Mười quy tắc ca khó

K1 phủ định không dính khía cạnh · K2 khía cạnh chỉ làm khung ("trong tầm giá") · K3 "không"
không mang nghĩa phủ định (câu hỏi, cụm cố định) · K4 phủ định kép · K5 "chưa biết" · K6 hai
vế cùng cực · K7 ý nằm ngoài cấu trúc · K8 GENERAL · K9 "không … lắm" · K10 còn phân vân.

K2 là câu trả lời cho mối lo ở CD1.8a về 110 dòng trung tính thuộc PRICE: phần lớn sẽ ra
`regular`, đúng với bản chất, thay vì bị ép vào nhóm phủ định.

### 3.4. Công cụ Excel

```
candidates.csv --excel--> candidates_chu_thich.xlsx --(gán tay)--> tu-excel --> candidates.csv
```

- Thứ tự dòng trong `.xlsx`: xáo câu trong từng nhóm ứng viên, xếp xen kẽ bốn nhóm, mọi khía
  cạnh của một câu liền nhau. Dừng ở dòng nào thì phần đã gán cũng trải đều.
- Chỉ ba cột chú thích mở khoá; hai cột có ô chọn giá trị.
- `tu-excel` kiểm bốn thứ trước khi ghi: tập `uid` trùng CSV, ba cột dữ liệu không bị sửa, giá
  trị hợp lệ, không có dòng điền dở. Sai một thứ là dừng, không ghi gì.
- CSV giữ nguyên thứ tự và mười cột cũ, nên bước chốt tập đọc lại không cần biết tới Excel.

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao |
|---|---|---|---|
| Số giá trị `phenomenon` | Năm: negation, contrast, both, regular, bo | Ba như `metrics.json` | Gán chi tiết thì gộp lại được, gán gộp thì không tách ra được |
| Ngưỡng kappa | 0,70 | 0,6 của plan gốc | Plan Chuyên đề 1 mới hơn và chặt hơn |
| Kappa tính trên cột nào | `phenomenon` | Cả hai cột | Đây là thứ tập này tạo ra; nhãn cảm xúc chỉ là kiểm lại |
| Chuyển ý hai vế cùng cực | `regular` | `contrast` | Từ nối không làm việc chuyển ý thì mô hình không cần hiểu nó |
| "chưa biết" | `negation` | `regular` | Muốn ra nhãn trung tính, mô hình phải hiểu từ phủ định đó |
| Ranh giới vế | Dấu câu mạnh, không tính dấu phẩy | Mệnh đề theo nghĩa | Bình luận viết không chuẩn, tách mệnh đề theo nghĩa là nơi hai người lệch nhau |
| Công cụ gán | `.xlsx` trung gian | Mở CSV bằng Excel; viết giao diện riêng | CSV dính cột trên máy tiếng Việt; giao diện riêng tốn công mà không hơn Excel |
| Giấu `nhom_ung_vien` khi gán | Giấu | Hiện | Nhìn thấy sẽ lái cách gán |
| Sửa nhãn gốc | Không, chỉ ghi vào `nhan_kiem_tra` | Sửa thẳng | Nhãn gốc là dữ liệu của người khác; bất đồng là một con số đáng báo cáo |

## 5. ĐIỂM NỐI VỚI STEP SAU

- **CD1.8c là việc tay của học viên**, khoảng 20 đến 25 giờ, chia hai đợt.
- CD1.8d cần thêm một công cụ: rút 60 dòng cho người thứ hai, tính kappa, chốt
  `diagnostic_300.jsonl`. Chưa viết, đúng lượt của nó.
- CD1.8d phải quyết: `both` vào đâu trong ba nhóm của `metrics.json`.
- Người chú thích thứ hai vẫn chưa có. Câu hỏi gửi GVHD chưa gửi.
- Hướng dẫn đi vào Phụ lục B của báo cáo.

## 6. KIỂM CHỨNG

```
401 passed
```

- Tăng 7 so với 394.
- **Cả 32 chỗ trích ví dụ trong hướng dẫn đã đối chiếu bằng mã với `candidates.csv`:** đúng dòng,
  đúng khía cạnh, đúng nhãn gốc, đoạn câu trích có trong câu thật. 0 lỗi.
- Đã sinh file `.xlsx` thật 800 dòng và chạy `tien-do`: 0 / 800.
- Test có một dòng mà câu bắt đầu bằng "=1+1" để chắc Excel không biến câu thành công thức.
- **Chưa kiểm:** chưa mở file `.xlsx` bằng Excel thật để thử ô chọn và khoá cột; test chỉ kiểm
  bằng thư viện. Hướng dẫn chưa qua tay người thứ hai, nên chưa biết kappa.
- **Nhãn của mười hai dòng mẫu là do Claude gán theo quy tắc.** Bạn cần duyệt.

## 7. VIỆC CỦA BẠN, THEO THỨ TỰ

1. **Chép định nghĩa ba lớp cảm xúc của UIT-ViSFD** vào `docs/annotation_guideline.md`, mục 5,
   thay cho đoạn `[CẦN KIỂM: ...]`. Nguồn: mục mô tả quy trình gán nhãn của bài báo gốc. Dạng:
   ba gạch đầu dòng, mỗi lớp một câu. Việc này chặn CD1.8c.
2. **Đọc hướng dẫn, tự gán mười hai dòng mẫu ở mục 7** mà không nhìn bảng, rồi so. Chỗ nào bạn
   không đồng ý với nhãn của tôi thì báo, sửa quy tắc trước khi gán thật.
3. **Mở `data/diagnostic/candidates_chu_thich.xlsx`** và thử gán năm dòng, lưu, đóng, chạy:
   `.\.venv\Scripts\python.exe scripts\chu_thich_chan_doan.py tu-excel`. Nếu ô chọn hay khoá
   cột không hoạt động thì báo ngay.
4. **Sao lưu** thư mục `data/diagnostic/` ra ngoài máy sau mỗi buổi gán. File này không nằm
   trên GitHub.
5. Gán tới khi `tien-do` báo đủ.

Bạn có câu hỏi phụ nào về phần này không? Step kế là CD1.8c, phần gán tay của bạn; trong lúc
đó tôi có thể làm song song CD1.7 (mốc tham chiếu bằng mô hình ngôn ngữ lớn) nếu bạn muốn.
