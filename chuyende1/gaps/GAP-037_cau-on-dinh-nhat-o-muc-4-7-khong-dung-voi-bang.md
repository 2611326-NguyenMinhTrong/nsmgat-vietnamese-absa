# GAP-037 — Câu "ổn định nhất giữa các hạt giống" ở mục 4.7 không đúng với bảng kết quả

**Ngày phát hiện:** 13/10/2026 · **Phát hiện bởi:** Claude Code, khi thêm chỗ kiểm cho các câu của mục 4.7
**Loại:** tài liệu · số liệu
**Mức độ:** nhẹ (một câu nhận xét; không con số nào sai)
**Trạng thái:** ✅ Đã sửa ở bản chính; bản đầy đủ (bản lưu) giữ nguyên câu cũ

---

## 1. Sai ở đâu

Mục 4.7, đoạn "Mô hình tốt nhất", ở cả hai bản: "Trên cả accuracy lẫn macro-F1, PhoBERT tinh chỉnh là mô hình
đứng đầu và cũng là mô hình ổn định nhất giữa các hạt giống."

Vế thứ hai không đúng với độ lệch chuẩn trong bảng kết quả chính (Bảng 4.3 của bản chính):

| Mô hình | Độ lệch chuẩn accuracy | Độ lệch chuẩn macro-F1 |
|---|---|---|
| Từ điển cảm xúc | 0,02 | 0,02 |
| PhoBERT tinh chỉnh | 0,11 | 0,14 |
| ASGCN nối gốc | 0,08 | 0,29 |

Mô hình từ điển ổn định hơn PhoBERT ở cả hai độ đo, và ASGCN nối gốc ổn định hơn PhoBERT về accuracy. Điều
đúng là: trong năm mô hình học, PhoBERT có độ lệch chuẩn của macro-F1 nhỏ nhất.

## 2. Phát hiện thế nào

Khi viết chỗ kiểm cho câu này (GAP-036), điều kiện "PhoBERT có độ lệch chuẩn nhỏ nhất" phải được viết thành
mã và tính trên số thật, và nó sai.

## 3. Nguyên nhân gốc

Câu được viết theo ấn tượng khi so PhoBERT với ba mô hình đồ thị, rồi phát biểu rộng ra cho mọi mô hình. Công
cụ đối chiếu lúc đó chỉ kiểm câu có con số, còn câu định tính không có số thì không ai kiểm.

## 4. Ảnh hưởng lan tới đâu

- Một câu ở mục 4.7 của cả hai bản. Không có ở các chương khác hay ở phần tóm tắt.
- Không con số nào sai.

## 5. Đã sửa thế nào

Bản chính, mục 4.7: "Trên cả accuracy lẫn macro-F1, PhoBERT tinh chỉnh là mô hình đứng đầu; trong năm mô hình
học, nó cũng có độ lệch chuẩn của macro-F1 nhỏ nhất giữa các hạt giống (0,14)." Câu này nay có chỗ kiểm
trong `doi_chieu_chuong4.py`: mô tả "4.7, mô hình đứng đầu", điều kiện tính trên `metrics.json`. Bản đầy đủ là
bản lưu nên không sửa.

## 6. Bài học

Câu nhận xét không có con số vẫn là một khẳng định về số liệu. Mỗi câu so sánh ("cao nhất", "duy nhất", "ổn
định nhất", "ở mọi mô hình") cần một điều kiện tính được, như các câu đã có hàm `neu` trong công cụ.
